"""Offline synthetic v3 checker tests: POSIX only, no provider or Product calls."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ts_ee_orca_jsonl_receipt_v3 import Rejected, run

SID = "ses_synthetic_qualified_001"
ATTEMPT = "TS-EE-ORCA-V3-SYNTHETIC-A001"
MODEL = "opencode/deepseek-v4.1-flash-free"


def evt(kind, part, session=SID):
    return (json.dumps({"type": kind, "sessionID": session, "part": part},
                       separators=(",", ":"), sort_keys=True) + "\n").encode()


def start():
    return evt("step_start", {"type": "step-start"})


def text(v="F01 zero allowed"):
    return evt("text", {"type": "text", "text": v})


def finish(cost=0):
    return evt("step_finish", {"type": "step-finish", "cost": cost})


def tool(name="read", status="completed"):
    return evt("tool_use", {"type": "tool", "tool": name,
                            "state": {"status": status}})


@unittest.skipUnless(os.name == "posix", "POSIX-only validator")
class V3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "results").mkdir()
        (self.root / "receipts").mkdir()
        self.source = self.root / "results" / "ORIGINAL.jsonl"
        self.dest = self.root / "receipts" / "R.json"
        self.good = start() + text() + tool() + finish()

    def invoke(self, data=None, digest=None, original="results/ORIGINAL.jsonl",
               receipt="receipts/R.json", model=MODEL, exit_claim=0,
               attempt=ATTEMPT, session=SID):
        raw = self.good if data is None else data
        self.source.write_bytes(raw)
        return run(self.root, original, digest or hashlib.sha256(raw).hexdigest(),
                   receipt, attempt, session, model, exit_claim)

    def rejects(self, **opts):
        with self.assertRaises((Rejected, OSError)):
            self.invoke(**opts)
        self.assertFalse(self.dest.exists())

    def test_01_clean_atomic_receipt(self):
        o = self.invoke()
        self.assertEqual(o["event_count"], 4)
        self.assertEqual(o["semantic_verdict"], "NOT_ASSESSED")
        p = json.loads(self.dest.read_text())
        self.assertEqual(p["step_start_count"], 1)
        self.assertEqual(p["step_finish_count"], 1)
        self.assertFalse(p["provider_billing_verified_independently"])
        self.assertEqual(p["original_sha256"], hashlib.sha256(self.good).hexdigest())
        self.assertEqual(list((self.root / "receipts").glob(".stage-*")), [])
        self.assertEqual(self.dest.stat().st_mode & 0o777, 0o600)

    def test_02_multiple_balanced_steps(self):
        result = self.invoke(data=start() + text() + finish() + start() + text() + finish())
        self.assertEqual(result["event_count"], 6)
        self.assertEqual(json.loads(self.dest.read_text())["step_finish_count"], 2)

    def test_03_finish_without_start(self):
        self.rejects(data=text() + finish())

    def test_04_double_finish(self):
        self.rejects(data=start() + text() + finish() + finish())

    def test_05_duplicate_start(self):
        self.rejects(data=start() + start() + text() + finish())

    def test_06_text_before_start(self):
        self.rejects(data=text() + start() + finish())

    def test_07_finish_missing(self):
        self.rejects(data=start() + text())

    def test_08_error_event_rejected(self):
        self.rejects(data=start() + evt("error", {"message": "failure"}) + text() + finish())

    def test_09_unknown_event_rejected(self):
        self.rejects(data=start() + evt("unknown", {"type": "unknown"}) + text() + finish())

    def test_10_part_type_mismatch(self):
        self.rejects(data=start() + evt("text", {"type": "tool", "text": "xx"}) + finish())

    def test_11_tool_missing_status(self):
        self.rejects(data=start() + text() + tool("read", "running") + finish())

    def test_12_unexpected_tool_only_observational(self):
        self.invoke(data=start() + text() + tool("edit") + finish())
        p = json.loads(self.dest.read_text())
        self.assertEqual(p["other_tool_events"], 1)
        self.assertFalse(p["runtime_permission_enforcement_verified"])

    def test_13_wrong_hash(self):
        self.rejects(digest="0" * 64)

    def test_14_malformed_json(self):
        self.rejects(data=b'{"type":\n')

    def test_15_duplicate_keys(self):
        self.rejects(data=start() + b'{"type":"text","type":"text","sessionID":"'
                     + SID.encode() + b'","part":{"type":"text","text":"a"}}\n' + finish())

    def test_16_nan_metadata(self):
        self.rejects(data=start() + b'{"type":"text","sessionID":"'
                     + SID.encode() + b'","part":{"type":"text","text":"a","bad":NaN}}\n' + finish())

    def test_17_mixed_session(self):
        self.rejects(data=start() + evt("text", {"type": "text", "text": "x"},
                                       "ses_malicious_other") + finish())

    def test_18_missing_final_lf(self):
        self.rejects(data=self.good[:-1])

    def test_19_crlf_rejected(self):
        self.rejects(data=self.good.replace(b"\n", b"\r\n"))

    def test_20_cost_nonfinite(self):
        self.rejects(data=start() + text() + finish(float("nan")))

    def test_21_cost_too_large(self):
        self.rejects(data=start() + text() + finish(10**20))

    def test_22_exit_nonzero(self):
        self.rejects(exit_claim=1)

    def test_23_model_not_free(self):
        self.rejects(model="openai/gpt-6")

    def test_24_existing_receipt_collision(self):
        self.dest.write_text("existing")
        with self.assertRaises((Rejected, OSError)):
            self.invoke()
        self.assertEqual(self.dest.read_text(), "existing")

    def test_25_traversal(self):
        self.rejects(original="results/../other.jsonl")

    def test_26_source_symlink_rejected(self):
        outside = self.root / "outside"
        outside.write_bytes(self.good)
        self.source.symlink_to(outside)
        with self.assertRaises((Rejected, OSError)):
            self.invoke()

    def test_27_receipts_parent_symlink_rejected(self):
        outside = self.root / "out"
        outside.mkdir()
        (self.root / "receipts" / "R.json").parent.rmdir()
        (self.root / "receipts").symlink_to(outside, target_is_directory=True)
        self.rejects()
        self.assertFalse((outside / "R.json").exists())

    def test_28_link_failure_no_final(self):
        with patch("ts_ee_orca_jsonl_receipt_v3.os.link", side_effect=OSError("injected link failure")):
            self.rejects()
        self.assertEqual(list((self.root / "receipts").glob(".stage-*")), [])

    def test_29_failure_after_link_reports_unknown_preserves_final(self):
        real = os.fsync
        calls = 0
        def injected(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected fsync after link")
            return real(fd)
        with patch("ts_ee_orca_jsonl_receipt_v3.os.fsync", side_effect=injected):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH_POSTCONDITION"):
                self.invoke()
        self.assertTrue(self.dest.exists())
        self.assertGreater(self.dest.stat().st_size, 0)
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_30_receipt_final_symlink_rejected(self):
        outside = self.root / "outside"
        outside.write_text("KEEP")
        self.dest.symlink_to(outside)
        with self.assertRaises((Rejected, OSError)):
            self.invoke()
        self.assertEqual(outside.read_text(), "KEEP")

    def test_31_fake_finish_cost_boolean(self):
        self.rejects(data=start() + text() + finish(True))

    def test_32_partial_write_not_in_final(self):
        with patch("ts_ee_orca_jsonl_receipt_v3.os.link", side_effect=OSError("disk full")):
            self.rejects()
        self.assertFalse(self.dest.exists())

    def test_33_bad_receipt_parent(self):
        self.rejects(receipt="receipts/missing/R.json")

    def test_34_inline_bad_utf8(self):
        self.rejects(data=start() + b"\xff\n" + finish())


if __name__ == "__main__":
    unittest.main()
