"""Deterministic standalone POSIX/WSL v5 source-only receipt tests, no provider calls."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ts_ee_orca_jsonl_receipt_v5 import (  # noqa E402
    Rejected, analyze, parse_event, run, publish, open_root,
)

ATTEMPT = "TS-EE-ORCA-R005-A001"
SID = "ses_test_1234567890"
MODEL = "opencode/deepseek-v4.1-flash-free"


def event(kind, part=None, sid=SID):
    data = {"type": kind, "sessionID": sid,
            "part": part or {"type": {"step_start": "step-start", "step_finish": "step-finish",
                                     "text": "text", "tool_use": "tool"}[kind]}}
    return (json.dumps(data, separators=(",", ":"), sort_keys=True) + "\n").encode()


START = event("step_start")
TEXT = event("text", {"type": "text", "text": "F01 quantity > 0"})
END = event("step_finish", {"type": "step-finish", "cost": 0})
GOOD = START + TEXT + END


@unittest.skipUnless(os.name == "posix", "v5 intentionally POSIX only")
class R005Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "results").mkdir(mode=0o700)
        (self.root / "receipts").mkdir(mode=0o700)
        self.source = self.root / "results/ORIGINAL.jsonl"
        self.final = self.root / "receipts/RECEIPT.json"
        self.raw = GOOD
        self.digest = hashlib.sha256(GOOD).hexdigest()
        self.source.write_bytes(GOOD)

    def execute(self, data=None, digest=None, root=None, original="results/ORIGINAL.jsonl",
                receipt="receipts/RECEIPT.json", attempt=ATTEMPT, session=SID,
                model=MODEL, exit_code=0):
        if data is not None:
            self.source.write_bytes(data)
            if digest is None:
                digest = hashlib.sha256(data).hexdigest()
        return run(root or self.root, original, digest or self.digest,
                   receipt, attempt, session, model, exit_code)

    def denied(self, **kwargs):
        with self.assertRaises((Rejected, OSError, OverflowError)):
            self.execute(**kwargs)

    def test_01_publish_once(self):
        out = self.execute()
        self.assertEqual(out["status"], "RECEIPT_PUBLISHED_AT_OBSERVATION")
        b = self.final.read_bytes()
        self.assertEqual(hashlib.sha256(b).hexdigest(), out["receipt_sha256"])
        self.assertEqual(out["receipt_bytes"], len(b))
        self.assertEqual(stat.S_IMODE(self.final.stat().st_mode), 0o600)
        self.assertEqual(out["receipt_inode"], self.final.stat().st_ino)
        self.assertEqual(list((self.root / "receipts").glob(".stage-*")), [])
        parsed = json.loads(b)
        self.assertEqual(parsed["semantic_review_verdict"], "NOT_ASSESSED")
        self.assertFalse(parsed["independent_billing_verified"])

    def test_02_double_call_never_overwrites(self):
        self.execute()
        before = self.final.read_bytes()
        with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
            self.execute()
        self.assertEqual(self.final.read_bytes(), before)

    def test_03_multiple_steps(self):
        content = GOOD + START + TEXT + END
        self.execute(data=content)
        self.assertEqual(json.loads(self.final.read_bytes())["step_finish_count"], 2)

    def test_04_readonly_tool(self):
        data = START + event("tool_use", {"type": "tool", "tool": "read", "state": {"status": "completed"}}) + TEXT + END
        self.execute(data=data)
        self.assertEqual(json.loads(self.final.read_bytes())["read_only_tool_events"], 1)

    def test_05_unsafe_tool_observed(self):
        data = START + event("tool_use", {"type": "tool", "tool": "edit", "state": {"status": "completed"}}) + TEXT + END
        self.execute(data=data)
        self.assertEqual(json.loads(self.final.read_bytes())["other_tool_events"], 1)

    def test_06_tool_error_observed(self):
        data = START + event("tool_use", {"type": "tool", "tool": "read", "state": {"status": "error"}}) + TEXT + END
        self.execute(data=data)
        self.assertEqual(json.loads(self.final.read_bytes())["reported_tool_errors"], 1)

    def test_07_missing_finish(self):
        self.denied(data=START + TEXT)

    def test_08_double_finish(self):
        self.denied(data=GOOD + END)

    def test_09_double_start(self):
        self.denied(data=START + START + TEXT + END)

    def test_10_text_outside_step(self):
        self.denied(data=TEXT + GOOD)

    def test_11_tool_outside_step(self):
        self.denied(data=event("tool_use", {"type": "tool", "tool": "read", "state": {"status": "error"}}) + GOOD)

    def test_12_wrong_part_type(self):
        self.denied(data=event("step_start", {"type": "wrong"}) + TEXT + END)

    def test_13_wrong_session(self):
        self.denied(data=START + event("text", {"type": "text", "text": "x"}, sid="ses_other_1234") + END)

    def test_14_error_unknown_event(self):
        self.denied(data=START + b'{"type":"error","sessionID":"'+SID.encode()+b'","part":{}}\n' + TEXT + END)

    def test_15_bad_terminal_state(self):
        data = START + event("tool_use", {"type": "tool", "tool": "read", "state": {"status": "running"}}) + TEXT + END
        self.denied(data=data)

    def test_16_no_text(self):
        self.denied(data=START + END)

    def test_17_invalid_utf8(self):
        self.denied(data=START + b'\xff\n' + TEXT + END)

    def test_18_duplicate_json_key(self):
        self.denied(data=START + b'{"type":"text","type":"text","sessionID":"'+SID.encode()+b'","part":{"type":"text","text":"x"}}\n' + END)

    def test_19_bad_nan(self):
        self.denied(data=START + TEXT + b'{"type":"step_finish","sessionID":"'+SID.encode()+b'","part":{"type":"step-finish","cost":NaN}}\n')

    def test_20_deeply_nested(self):
        huge = b'{"type":"text","sessionID":"'+SID.encode()+b'","part":{"type":"text","text":"x","deep":'+b'['*2500+b'0'+b']'*2500+b'}}\n'
        self.denied(data=START + huge + END)

    def test_21_no_lf(self):
        self.denied(data=GOOD[:-1])

    def test_22_crlf(self):
        self.denied(data=GOOD.replace(b'\n', b'\r\n'))

    def test_23_bad_hash(self):
        self.denied(digest="0"*64)

    def test_24_bad_model_claim(self):
        self.denied(model="openai/gpt-6")

    def test_25_nonzero_exit_claim(self):
        self.denied(exit_code=1)

    def test_26_path_traversal(self):
        self.denied(original="results/../ORIGINAL.jsonl")

    def test_27_source_symlink(self):
        self.source.unlink()
        self.source.symlink_to(self.root / "outside.txt")
        self.denied()

    def test_28_receipt_parent_symlink(self):
        (self.root / "receipts").rmdir()
        (self.root / "receipts").symlink_to(self.root / "results")
        self.denied()

    def test_29_root_ancestor_symlink(self):
        link = self.root / "linkroot"
        link.symlink_to(self.root, target_is_directory=True)
        self.denied(root=link)

    def test_30_untrusted_receipts_mode(self):
        (self.root / "receipts").chmod(0o750)
        with self.assertRaisesRegex(Rejected, "NOT_EXCLUSIVE"):
            self.execute()
        self.assertFalse(self.final.exists())

    def test_31_wrong_receipt_owner_simulated(self):
        from ts_ee_orca_jsonl_receipt_v5 import private_dir
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.geteuid", return_value=os.geteuid() + 10):
            self.denied()

    def test_32_existing_symlink_final(self):
        self.final.symlink_to(self.source)
        with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
            self.execute()
        self.assertTrue(self.final.is_symlink())

    def test_33_prelink_fsync_failure_removes_stage(self):
        real = os.fsync
        def fail_file(fd):
            if stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("synthetic prelink fsync failure")
            return real(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.fsync", side_effect=fail_file):
            self.denied()
        self.assertFalse(self.final.exists())
        self.assertEqual(list((self.root / "receipts").glob(".stage-*")), [])

    def test_34_cleanup_failure_prelink_is_unknown(self):
        real_fsync, real_unlink = os.fsync, os.unlink
        def badfsync(fd):
            if stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("prelink fsync failure")
            return real_fsync(fd)
        def badunlink(path, *args, **kwargs):
            if str(path).startswith(".stage-"):
                raise OSError("cleanup denied")
            return real_unlink(path, *args, **kwargs)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.fsync", side_effect=badfsync), \
             mock.patch("ts_ee_orca_jsonl_receipt_v5.os.unlink", side_effect=badunlink):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_STAGE_CLEANUP"):
                self.execute()
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_35_link_created_then_raises_is_unknown(self):
        real = os.link
        def uncertain(*args, **kwargs):
            real(*args, **kwargs)
            raise OSError("interrupted after link")
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.link", side_effect=uncertain):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertTrue(self.final.exists())
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_36_link_fails_without_effect_still_unknown(self):
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.link", side_effect=OSError("no effect")):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertFalse(self.final.exists())
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_37_final_regular_file_replaced_before_readback_detected(self):
        real = os.fsync
        fired = False
        def swap_on_dir_fsync(fd):
            nonlocal fired
            if not fired and stat.S_ISDIR(os.fstat(fd).st_mode):
                fired = True
                self.final.unlink()
                self.final.write_bytes(b'competing writer payload')
            return real(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.fsync", side_effect=swap_on_dir_fsync):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertEqual(self.final.read_bytes(), b'competing writer payload')
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_38_cleanup_failure_postlink_is_unknown(self):
        real = os.unlink
        def badunlink(path, *args, **kwargs):
            if str(path).startswith(".stage-"):
                raise OSError("cleanup denied")
            return real(path, *args, **kwargs)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.unlink", side_effect=badunlink):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertTrue(self.final.exists())
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_39_fsync_failure_after_stage_cleanup_is_unknown(self):
        real = os.fsync
        counter = 0
        def bad_second_dir_fsync(fd):
            nonlocal counter
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                counter += 1
                if counter == 2:
                    raise OSError("directory durability unknown")
            return real(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.fsync", side_effect=bad_second_dir_fsync):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertTrue(self.final.exists())

    def test_40_stage_is_not_exposed_in_final_on_prelink_failure(self):
        def badwrite(*args, **kwargs):
            raise OSError("simulated early failure")
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.link", side_effect=badwrite):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
                self.execute()
        self.assertFalse(self.final.exists())

    def test_41_forged_provider_cost_is_only_claim(self):
        self.execute()
        b = json.loads(self.final.read_bytes())
        self.assertFalse(b["independent_billing_verified"])
        self.assertFalse(b["native_terminal_verified"])
        self.assertEqual(b["claimed_model"], MODEL)

    def test_42_no_private_prompt_in_receipt(self):
        secret = "INTERNAL_PROMPT_SENTINEL_123"
        self.execute(data=START + event("text", {"type": "text", "text": secret}) + END)
        self.assertNotIn(secret.encode(), self.final.read_bytes())

    def test_43_unicode_unescaped_input_is_counted(self):
        self.execute(data=START + event("text", {"type": "text", "text": "ñá"}) + END)
        self.assertEqual(json.loads(self.final.read_bytes())["step_finish_count"], 1)

    def test_44_root_file_not_dir(self):
        self.denied(root=self.source)

    def test_45_orphaned_stage_manual_collision_not_removed(self):
        (self.root / "receipts/.stage-aaaaaaaaaaaaaaaa").write_bytes(b'old')
        self.execute()
        self.assertTrue((self.root / "receipts/.stage-aaaaaaaaaaaaaaaa").exists())

    def test_46_invalid_id(self):
        self.denied(attempt="bad")

    def test_47_oversize_cost(self):
        self.denied(data=START + TEXT + event("step_finish", {"type": "step-finish", "cost": 10**400}))

    def test_48_preexisting_final_content_not_modified(self):
        self.final.write_bytes(b"ORIGINAL PREEXISTING")
        with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH"):
            self.execute()
        self.assertEqual(self.final.read_bytes(), b"ORIGINAL PREEXISTING")


    def test_49_untrusted_writable_ancestor_rejected(self):
        untrusted = self.root / "mutable_parent"
        untrusted.mkdir(mode=0o700)
        untrusted.chmod(0o777)
        child = untrusted / "case"
        child.mkdir(mode=0o700)
        (child / "results").mkdir(mode=0o700)
        (child / "receipts").mkdir(mode=0o700)
        (child / "results/ORIGINAL.jsonl").write_bytes(GOOD)
        with self.assertRaisesRegex(Rejected, "UNTRUSTED_MUTABLE_ANCESTOR"):
            self.execute(root=child)
        self.assertFalse((child / "receipts/RECEIPT.json").exists())

    def test_50_trusted_sticky_ancestor_admits_owned_child(self):
        sticky = self.root / "sticky_parent"
        sticky.mkdir(mode=0o700)
        sticky.chmod(0o1777)
        child = sticky / "owned_case"
        child.mkdir(mode=0o700)
        (child / "results").mkdir(mode=0o700)
        (child / "receipts").mkdir(mode=0o700)
        (child / "results/ORIGINAL.jsonl").write_bytes(GOOD)
        result = self.execute(root=child)
        self.assertEqual(result["status"], "RECEIPT_PUBLISHED_AT_OBSERVATION")

    def test_51_receipts_folder_close_after_link_is_unknown(self):
        original_close = os.close
        directory = (self.root / "receipts").stat()
        fired = {"count": 0}
        def fault(fd):
            st = os.fstat(fd)
            if (not fired["count"] and stat.S_ISDIR(st.st_mode)
                    and st.st_dev == directory.st_dev
                    and st.st_ino == directory.st_ino and self.final.exists()):
                fired["count"] += 1
                original_close(fd)
                raise OSError("injected close error after final")
            return original_close(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.close", side_effect=fault):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH_POSTCONDITION"):
                self.execute()
        self.assertEqual(fired["count"], 1)
        self.assertTrue(self.final.exists())

    def test_52_root_fd_close_after_link_is_unknown(self):
        original_close = os.close
        directory = self.root.stat()
        fired = {"count": 0}
        def fault(fd):
            st = os.fstat(fd)
            if (not fired["count"] and stat.S_ISDIR(st.st_mode)
                    and st.st_dev == directory.st_dev
                    and st.st_ino == directory.st_ino and self.final.exists()):
                fired["count"] += 1
                original_close(fd)
                raise OSError("injected root close after final")
            return original_close(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.close", side_effect=fault):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH_POSTCONDITION"):
                self.execute()
        self.assertEqual(fired["count"], 1)
        self.assertTrue(self.final.exists())

    def test_53_prior_unknown_survives_root_close_error(self):
        original_close = os.close
        original_link = os.link
        directory = self.root.stat()
        def uncertain_link(*args, **kwargs):
            original_link(*args, **kwargs)
            raise OSError("link returned error after creating final")
        def faulty_close(fd):
            st = os.fstat(fd)
            if (stat.S_ISDIR(st.st_mode) and st.st_dev == directory.st_dev
                    and st.st_ino == directory.st_ino and self.final.exists()):
                original_close(fd)
                raise OSError("root close also raised")
            return original_close(fd)
        with mock.patch("ts_ee_orca_jsonl_receipt_v5.os.link",
                        side_effect=uncertain_link), mock.patch(
                        "ts_ee_orca_jsonl_receipt_v5.os.close",
                        side_effect=faulty_close):
            with self.assertRaisesRegex(Rejected, "UNKNOWN_PUBLISH_POSTCONDITION"):
                self.execute()
        self.assertTrue(self.final.exists())
        self.assertEqual(len(list((self.root / "receipts").glob(".stage-*"))), 1)

    def test_54_symlinked_higher_ancestor_rejected(self):
        parent = self.root / "work"
        parent.mkdir(mode=0o700)
        child = parent / "case"
        child.mkdir(mode=0o700)
        (child / "results").mkdir(mode=0o700)
        (child / "receipts").mkdir(mode=0o700)
        (child / "results/ORIGINAL.jsonl").write_bytes(GOOD)
        link = self.root / "redirect"
        link.symlink_to(parent, target_is_directory=True)
        self.denied(root=link / "case")
        self.assertFalse((child / "receipts/RECEIPT.json").exists())

    def test_55_test_import_uses_sibling_tools_path(self):
        expected = (Path(__file__).resolve().parents[1] / "tools").resolve()
        self.assertEqual(Path(sys.path[0]).resolve(), expected)


if __name__ == "__main__":
    unittest.main()
