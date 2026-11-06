"""Descriptor-only bounded CLI input admission tests; no database credentials."""
import contextlib
import io
import os
import pathlib
import tempfile
import unittest

from ts_detstate.__main__ import _read_bounded_regular_file, main
from ts_detstate.core import Rejected, canonical


class CLIInputTests(unittest.TestCase):
    def test_plain_file_bounded_read_and_no_sql_plan(self):
        with tempfile.TemporaryDirectory(prefix="detfirst-") as root:
            path = pathlib.Path(root, "input.json")
            command = {
                "kind": "SyntheticState", "authority_ref": "AUTH-SYNTHETIC-R3",
                "operation_id": "R3-DET-OP-20261106-001",
                "attempt_id": "R3-DET-ATTEMPT-20261106-001",
                "mutation_id": "R3-DET-MUTATION-20261106-001",
                "state_id": "R3-DET-AGGREGATE-20261106-001",
                "expected_revision": 0, "state": {"synthetic": True, "value": 7},
            }
            path.write_text(canonical(command), encoding="utf-8")
            self.assertEqual(_read_bounded_regular_file(path), canonical(command))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(["plan", "--command-file", str(path)]), 0)
            self.assertIn('"disposition":"PLANNED_ONLY"', out.getvalue())
            self.assertIn('"effect":"NONE"', out.getvalue())

    def test_oversized_file_is_rejected_without_reading_to_eof(self):
        with tempfile.TemporaryDirectory() as root:
            path = pathlib.Path(root, "oversized.json")
            path.write_bytes(b"x" * 16385)
            with self.assertRaisesRegex(Rejected, "INPUT_LIMIT"):
                _read_bounded_regular_file(path)

    def test_untrusted_symlink_not_followed(self):
        if not hasattr(os, "O_NOFOLLOW"):
            self.skipTest("Linux/macOS O_NOFOLLOW required; qualified WSL runtime is Linux")
        with tempfile.TemporaryDirectory() as root:
            parent = pathlib.Path(root)
            target = parent / "target.json"
            target.write_text('{"synthetic":true}')
            link = parent / "input.json"
            link.symlink_to(target)
            with self.assertRaises(OSError):
                _read_bounded_regular_file(link)

    def test_fifo_rejected_as_nonregular_without_wait(self):
        if not hasattr(os, "mkfifo") or not hasattr(os, "O_NONBLOCK"):
            self.skipTest("POSIX nonblocking regular-file guard required")
        with tempfile.TemporaryDirectory() as root:
            fifo = pathlib.Path(root, "not-a-file")
            os.mkfifo(fifo)
            with self.assertRaisesRegex(Rejected, "INPUT_NOT_REGULAR"):
                _read_bounded_regular_file(fifo)

    def test_invalid_utf8_returns_safe_error(self):
        with tempfile.TemporaryDirectory() as root:
            path = pathlib.Path(root, "invalid.json")
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(Rejected, "INPUT_UTF8_INVALID"):
                _read_bounded_regular_file(path)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(main(["plan", "--command-file", str(path)]), 2)
            self.assertNotIn(str(path), stderr.getvalue())
            self.assertIn("INPUT_UTF8_INVALID", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
