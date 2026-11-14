"""Source-only deterministic tests; no model, Orca, Actions or Product calls."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ts_ee_orca_jsonl_receipt_v2 import InvalidEvidence, inspect  # noqa: E402


SID = "ses_synthetic_123456"
ATTEMPT = "TS-EE-ORCA-BRIDGE-SYNTHETIC-A001"
MODEL = "opencode/deepseek-v4.1-flash-free"


def event(kind, **other):
    value = {"type": kind, "sessionID": SID, **other}
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "results").mkdir()
        (self.root / "receipts").mkdir()
        self.original = "results/ORIGINAL.jsonl"
        self.receipt = "receipts/RECEIPT.json"
        self.good = (
            event("step_start", part={"type": "step-start"})
            + event("text", part={"type": "text", "text": "F01: zero incorrectly allowed"})
            + event("step_finish", part={"type": "step-finish", "cost": 0})
        )

    def check(self, data=None, digest=None, attempt=ATTEMPT, session=SID,
              original=None, receipt=None, model=MODEL, exit_claim=0):
        data = self.good if data is None else data
        source = self.root / (original or self.original)
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(data)
        return inspect(
            self.root, original or self.original,
            digest or hashlib.sha256(data).hexdigest(),
            receipt or self.receipt, attempt, session, model, exit_claim,
        )

    def assert_rejected(self, **kwargs):
        with self.assertRaises(InvalidEvidence):
            self.check(**kwargs)

    def test_clean_completed_jsonl_is_structural_only(self):
        result = self.check()
        self.assertEqual(result["event_count"], 3)
        self.assertEqual(result["step_count"], 1)
        self.assertEqual(result["provider_reported_cost_total"], 0)
        self.assertEqual(result["semantic_review_verdict"], "NOT_ASSESSED")
        self.assertFalse(result["provider_billing_independently_verified"])

    def test_unsafe_tool_is_reported_never_normalized_to_pass(self):
        data = (
            event("step_start")
            + event("tool_use", part={"type": "tool", "tool": "edit",
                                       "state": {"status": "completed"}})
            + event("text", part={"text": "unexpected edit"})
            + event("step_finish", part={"cost": 0})
        )
        report = self.check(data=data)
        self.assertEqual(report["result"], "UNSAFE_TOOL_REPORTED")
        self.assertEqual(report["unexpected_tool_names"]["edit"], 1)

    def test_wrong_digest(self):
        self.assert_rejected(digest="0" * 64)

    def test_malformed_json_event(self):
        self.assert_rejected(data=b'{"type":\n')

    def test_duplicate_json_keys(self):
        first = b'{"type":"text","type":"text","sessionID":"'+SID.encode()+b'"}\n'
        self.assert_rejected(data=first + event("step_finish", part={"cost": 0}))

    def test_mixed_sessions(self):
        data = self.good.replace(SID.encode(), b"ses_not_original_1111", 1)
        self.assert_rejected(data=data)

    def test_missing_terminal_step(self):
        self.assert_rejected(data=self.good.split(b'{"sessionID"')[0] + event("text"))

    def test_nonfinite_cost(self):
        bad = event("step_start") + event("text") + event("step_finish", part={"cost": float("nan")})
        self.assert_rejected(data=bad)

    def test_massive_cost(self):
        bad = event("step_start") + event("text") + event("step_finish", part={"cost": 10**400})
        self.assert_rejected(data=bad)

    def test_missing_newline(self):
        self.assert_rejected(data=self.good[:-1])

    def test_unqualified_provider_exit(self):
        self.assert_rejected(exit_claim=1)

    def test_openai_model_fails_closed(self):
        self.assert_rejected(model="openai/gpt-6")

    def test_receipt_collision(self):
        (self.root / self.receipt).write_text("previous receipt", encoding="utf-8")
        self.assert_rejected()

    def test_path_traversal(self):
        self.assert_rejected(original="results/../outside.jsonl")

    def test_missing_precreated_receipt_directory(self):
        self.assert_rejected(receipt="receipts/missing/new.json")

    def test_another_event_type_is_preserved_as_metadata(self):
        data = event("step_start") + event("thinking") + event("text") + event(
            "step_finish", part={"cost": 0.0}
        )
        report = self.check(data=data)
        self.assertEqual(report["events_by_type"]["thinking"], 1)


if __name__ == "__main__":
    unittest.main()
