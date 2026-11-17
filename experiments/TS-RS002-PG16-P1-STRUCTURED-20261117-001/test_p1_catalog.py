"""Synthetic only: no Docker, PostgreSQL, host connection or Product effect."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch
from subprocess import TimeoutExpired

source = Path(__file__).parent / "p1_catalog.py"
spec = importlib.util.spec_from_file_location("p1_catalog", source)
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)


def mock_child(returncode=0, output=""):
    class Child:
        pid = 99991
        def __init__(self):
            self.returncode = returncode
        def communicate(self, timeout):
            return output, ""
    return Child()


class StructuredP1Tests(TestCase):
    def test_frozen_sql_exact_shape(self):
        self.assertEqual(tuple(p1.SQL), ("A", "B", "C"))
        self.assertEqual(p1.SQL_SOURCE_BLOB, "250a4e647b4f4cc780a7db3766244422d0b32bc3")
        for q in p1.SQL.values():
            self.assertTrue(q.startswith("BEGIN TRANSACTION "))
            self.assertIn(" READ ONLY;", q)
            self.assertTrue(q.endswith("COMMIT;"))
            self.assertNotIn("INSERT INTO ", q)
            self.assertNotIn("DROP TABLE ", q)
        self.assertEqual(p1.CID, "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88")

    def test_native_output_strict(self):
        for phase, expected in p1.EXPECTED.items():
            with self.subTest(phase=phase):
                p1.check_result(phase, "BEGIN\n" + "\n".join(expected) + "\nCOMMIT\n")
                with self.assertRaisesRegex(RuntimeError, "READONLY_CATALOG_MISMATCH"):
                    p1.check_result(phase, "\n".join(expected[:-1]))
                if len(expected) > 1:
                    with self.assertRaisesRegex(RuntimeError, "READONLY_CATALOG_MISMATCH"):
                        p1.check_result(phase, "\n".join(reversed(expected)))
        with self.assertRaisesRegex(RuntimeError, "UNSAFE_SQL_STDOUT"):
            p1.normalize("x\x00")
        with self.assertRaisesRegex(RuntimeError, "UNSAFE_SQL_STDOUT"):
            p1.normalize("x" * 6001)

    def test_admission_self_hash_and_readonly_review(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            fake = p / "p1_catalog.py"
            fake.write_bytes(b"reviewed-source")
            m = {"runner_id": p1.RUNNER_ID, "source_git_commit": "a" * 40,
                 "source_git_blob": "b" * 40,
                 "runner_sha256": hashlib.sha256(fake.read_bytes()).hexdigest(),
                 "sql_source_git_blob": p1.SQL_SOURCE_BLOB, "container_id": p1.CID,
                 "review_verdict": "RECOMMEND", "review_original_blob": "c" * 40,
                 "allowed_phase": "A", "prior_provider_receipt_sha256": "GENESIS",
                 "protocol": "TS-RS002-P1-C001-STRUCTURED-v2"}
            admission_file = p / "admission.json"
            admission_file.write_text(json.dumps(m))
            os.chmod(admission_file, 0o600)
            with patch.object(p1, "__file__", str(fake)):
                self.assertEqual(p1.admission("A")[1], m["runner_sha256"])
                fake.write_bytes(b"tampered-script")
                with self.assertRaisesRegex(RuntimeError, "UNADMITTED_SOURCE_OR_ARTIFACT_HASH"):
                    p1.admission("A")
                fake.write_bytes(b"reviewed-source")
                m["review_verdict"] = "NO_RECOMMEND"
                admission_file.write_text(json.dumps(m))
                with self.assertRaisesRegex(RuntimeError, "UNADMITTED_SOURCE_OR_ARTIFACT_HASH"):
                    p1.admission("A")

    def test_one_structured_native_call_per_phase(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(p1, "RESULTS", Path(td) / "attempt"), \
             patch.object(p1, "read_only_preflight", return_value=("GENESIS", "admh", "runh")), \
             patch.object(p1.subprocess, "Popen", return_value=mock_child(output=p1.EXPECTED["A"][0] + "\n")) as execute:
            p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)
            args = execute.call_args.args[0]
            self.assertEqual(args[:6], [p1.DOCKER, "exec", "--user", "postgres", p1.CID, "psql"])
            self.assertEqual(args[-2:], ["-c", p1.SQL["A"]])
            self.assertIs(execute.call_args.kwargs["shell"], False)
            doc = json.loads((p1.RESULTS / "A" / "terminal.json").read_text())
            self.assertEqual(doc["status"], "PASS")
            self.assertEqual(doc["exit_code"], 0)
            self.assertEqual(doc["child_pid"], 99991)
            with self.assertRaises(FileExistsError):
                p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)

    def test_forged_local_receipt_never_admits_phase_b(self):
        # A coherent forged local JSON is never a source of B authority.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = root / "p1_catalog.py"
            fake.write_text("frozen")
            forged_dir = root / "attempt" / "A"
            forged_dir.mkdir(parents=True, mode=0o700)
            forged = {"runner_id": p1.RUNNER_ID, "phase": "A",
                      "status": "PASS", "stdout": list(p1.EXPECTED["A"])}
            (forged_dir / "intent.json").write_text(json.dumps(forged))
            (forged_dir / "terminal.json").write_text(json.dumps(forged))
            # Even internally coherent files cannot create the independently
            # qualified admission_B.json, which must be delivered by Control.
            with patch.object(p1, "__file__", str(fake)):
                with self.assertRaises(FileNotFoundError):
                    p1.admission("B")
            self.assertNotIn("read_prior", p1.__dict__)

    def test_symlink_and_partial_phase_never_execute(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            normal = root / "normal"
            normal.write_text("record")
            link = root / "link"
            link.symlink_to(normal)
            with self.assertRaisesRegex(RuntimeError, "UNTRUSTED_RECEIPT_FILE"):
                p1.safe_read(link)
            prior = root / "attempt" / "A"
            prior.mkdir(parents=True, mode=0o700)
            (prior / "intent.json").write_text('{"status":"PENDING_READONLY"}')
            with patch.object(p1, "RESULTS", root / "attempt"), \\
                 patch.object(p1, "read_only_preflight", return_value=("GENESIS", "admh", "runh")), \\
                 patch.object(p1.subprocess, "Popen") as invoke:
                with self.assertRaises(FileExistsError):
                    p1.run_phase("A")
                invoke.assert_not_called()

    def test_timeout_unknown_and_no_retry(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(p1, "RESULTS", Path(td) / "attempt"), \
             patch.object(p1, "read_only_preflight", return_value=("GENESIS", "admh", "runh")), \
             patch.object(p1.subprocess, "Popen") as execute:
            child = execute.return_value
            child.pid = 10021
            child.communicate.side_effect = TimeoutExpired(cmd="docker", timeout=30)
            with self.assertRaises(SystemExit):
                p1.run_phase("A")
            self.assertEqual(json.loads((p1.RESULTS / "A" / "terminal.json").read_text())["status"], "UNKNOWN")
            with self.assertRaises(FileExistsError):
                p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)

    def test_failed_spawn_not_dispatched_and_no_retry(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(p1, "RESULTS", Path(td) / "attempt"), \
             patch.object(p1, "read_only_preflight", return_value=("GENESIS", "admh", "runh")), \
             patch.object(p1.subprocess, "Popen", side_effect=FileNotFoundError("no docker")) as execute:
            with self.assertRaises(SystemExit):
                p1.run_phase("A")
            row = json.loads((p1.RESULTS / "A" / "terminal.json").read_text())
            self.assertEqual(row["status"], "NOT_DISPATCHED")
            self.assertEqual(row["child_pid"], None)
            self.assertNotIn("no docker", json.dumps(row))
            with self.assertRaises(FileExistsError):
                p1.run_phase("A")
            self.assertEqual(execute.call_count, 1)


if __name__ == "__main__":
    main()
