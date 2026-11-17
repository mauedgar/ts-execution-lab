"""Synthetic tests only: NEVER contact Docker, PostgreSQL or remote hosts."""
from __future__ import annotations
import importlib.util
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

module_path = Path(__file__).parent / "p1_catalog.py"
spec = importlib.util.spec_from_file_location("p1_catalog", module_path)
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)


class StructuredP1Tests(TestCase):
    def test_frozen_sql_read_only_and_fixed(self):
        self.assertEqual(tuple(p1.SQL), ("A", "B", "C"))
        self.assertEqual(p1.SQL_SOURCE_BLOB, "250a4e647b4f4cc780a7db3766244422d0b32bc3")
        for query in p1.SQL.values():
            self.assertTrue(query.startswith("BEGIN TRANSACTION "))
            self.assertTrue(query.endswith("COMMIT;"))
            self.assertIn(" READ ONLY;", query)
            self.assertNotIn("INSERT INTO", query)
            self.assertNotIn("CREATE ", query)
        self.assertEqual(p1.USER, "ts_rs002_admin")
        self.assertEqual(p1.CID, "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88")

    def test_all_phase_outputs_and_fail_closed(self):
        for phase, expected in p1.EXPECTED.items():
            with self.subTest(phase=phase):
                p1.check_result(phase, "\n".join(expected) + "\n")
                p1.check_result(phase, "BEGIN\n" + "\n".join(expected) + "\nCOMMIT\n")
                with self.assertRaisesRegex(RuntimeError, "READONLY_CATALOG_MISMATCH"):
                    p1.check_result(phase, "\n".join(expected[:-1]) + "\n")
                if len(expected) > 1:
                    with self.assertRaisesRegex(RuntimeError, "READONLY_CATALOG_MISMATCH"):
                        p1.check_result(phase, "\n".join(reversed(expected)) + "\n")
        with self.assertRaisesRegex(RuntimeError, "UNSAFE_SQL_STDOUT"):
            p1.normalize("injected\x00payload")
        with self.assertRaisesRegex(RuntimeError, "UNSAFE_SQL_STDOUT"):
            p1.normalize("A" * 6001)

    def test_structured_argv_one_native_call_no_shell_no_retry(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(p1, "RESULTS", Path(td) / "attempt"), \
             patch.object(p1, "read_only_preflight") as preflight, \
             patch.object(p1.subprocess, "run") as execute:
            execute.return_value = SimpleNamespace(returncode=0, stdout=p1.EXPECTED["A"][0] + "\n", stderr="")
            p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)
            args = execute.call_args.args[0]
            self.assertEqual(args[:6], ["/usr/bin/docker", "exec", "--user", "postgres", p1.CID, "psql"])
            self.assertEqual(args[-2:], ["-c", p1.SQL["A"]])
            self.assertIs(execute.call_args.kwargs["shell"], False)
            self.assertEqual(json.loads((p1.RESULTS / "A" / "terminal.json").read_text())["status"], "PASS")
            with self.assertRaises(FileExistsError):
                p1.run_phase("A")
            self.assertEqual(execute.call_count, 1, "no duplicate SQL invocation")

    def test_phase_failure_receipted_and_not_replayed(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(p1, "RESULTS", Path(td) / "attempt"), \
             patch.object(p1, "read_only_preflight"), \
             patch.object(p1.subprocess, "run") as execute:
            execute.return_value = SimpleNamespace(returncode=1, stdout="", stderr="password should never be printed")
            with self.assertRaises(SystemExit):
                p1.run_phase("A")
            receipt = json.loads((p1.RESULTS / "A" / "terminal.json").read_text())
            self.assertEqual(receipt["status"], "UNKNOWN_OR_FAILED")
            self.assertTrue(receipt["no_retry"])
            self.assertNotIn("password", json.dumps(receipt))
            with self.assertRaises(FileExistsError):
                p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)


if __name__ == "__main__":
    main()
