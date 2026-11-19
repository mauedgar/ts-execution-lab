"""Deterministic stdlib tests; zero Orca, WSL, subprocess or host contact."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from uuid import uuid4

import orca_status_probe as g

HOST = "notebook-host-0001"
TERM = "term_aabbccdd99887766"
RUN = "123e4567-e89b-12d3-a456-426614174000"
SHA = "a" * 40
ATTEMPT = "TS-RS002-P0-ORCA-P00-SOURCE-20261119-001-A001"


def jsonbytes(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def status(rid=RUN):
    return {"id": "local-status", "ok": True, "result": {"app": {"running": True}, "runtime": {
        "state": "ready", "reachable": True, "runtimeId": rid}}, "_meta": {"runtimeId": rid}}


def listing(rid=RUN):
    return {"id": "local", "ok": True, "result": {"hostScope": {"hostIds": [HOST],
        "omittedHostIds": []}, "terminals": [{"handle": TERM, "executionHostId": HOST,
        "connected": True, "orphaned": False}]}, "_meta": {"runtimeId": rid}}


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.path = Path(self.d.name) / "Orca.exe"
        self.path.write_bytes(b"synthetic-orca-executable-identity-test-only")
        self.f = g.Frozen(ATTEMPT, SHA, hashlib.sha256(self.path.read_bytes()).hexdigest(),
            str(self.path), TERM, HOST)
        self.docs = [status(), listing(), status()]
        self.called = []

    def runner(self, argv, **kwargs):
        self.called.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, jsonbytes(self.docs[len(self.called) - 1]), b"")

    def classify(self):
        return g.inspect_readonly(self.f, self.runner)

    def assert_blocked(self, match=None):
        with self.assertRaises(g.BlockedPrecondition) as err:
            self.classify()
        if match:
            self.assertIn(match, str(err.exception))

    def test_nominal_fixture_explicitly_not_physical(self):
        r = self.classify()
        self.assertEqual(r["classification"], g.SOURCE_ONLY)
        self.assertEqual(r["linux_pid"], "NOT_ATTESTED")
        self.assertEqual(r["physical_p0_dispatch"], "NOT_DISPATCHED")
        self.assertEqual(len(self.called), 3)
        for cmd, kw in self.called:
            self.assertFalse(kw["shell"])
            self.assertTrue(kw["capture_output"])
            self.assertEqual(kw["timeout"], 8)
            self.assertNotIn("send", cmd)
            self.assertNotIn("create", cmd)
            self.assertNotIn("wsl.exe", cmd)

    def test_physical_admission_always_fails(self):
        with self.assertRaisesRegex(g.BlockedPrecondition, "NOT_QUALIFIED"):
            g.physical_admission()

    def test_no_actual_entrypoint_dispatch(self):
        self.assertFalse(hasattr(g, "run_p0"))

    def test_cli_cmd_wrapper_rejected(self):
        self.f = replace(self.f, exe_path=str(self.path.with_suffix(".cmd")))
        self.assert_blocked("WINDOWS_ORCA_EXECUTABLE_REQUIRED")
        self.assertFalse(self.called)

    def test_relative_executable_rejected(self):
        self.f = replace(self.f, exe_path="Orca.exe")
        self.assert_blocked("CLI_PATH_NOT_ABSOLUTE")

    def test_stale_executable_sha_rejected_before_probe(self):
        self.f = replace(self.f, expected_exe_sha256="b" * 64)
        self.assert_blocked("CLI_HASH_MISMATCH")
        self.assertFalse(self.called)

    def test_executable_symlink_rejected(self):
        link = self.path.with_name("Linked-Orca.exe")
        link.symlink_to(self.path)
        self.f = replace(self.f, exe_path=str(link))
        self.assert_blocked("CLI_MISSING_OR_SYMLINK")

    def test_wrong_frozen_attempt_rejected(self):
        self.f = replace(self.f, attempt="unknown")
        self.assert_blocked("ATTEMPT_NOT_FROZEN")

    def test_wrong_terminal_handle_rejected(self):
        self.f = replace(self.f, expected_terminal="not-terminal")
        self.assert_blocked("TERMINAL_HANDLE_INVALID")

    def test_status_not_ready_rejected(self):
        self.docs[0]["result"]["runtime"]["state"] = "starting"
        self.assert_blocked("ORCA_RUNTIME_NOT_READY")

    def test_status_not_reachable_rejected(self):
        self.docs[0]["result"]["runtime"]["reachable"] = False
        self.assert_blocked("ORCA_RUNTIME_NOT_READY")

    def test_status_app_not_running_rejected(self):
        self.docs[0]["result"]["app"]["running"] = False
        self.assert_blocked("ORCA_APP_NOT_RUNNING")

    def test_missing_runtime_id_rejected(self):
        self.docs[0]["result"]["runtime"]["runtimeId"] = None
        self.assert_blocked("ORCA_RUNTIME_ID_MISSING")

    def test_restarted_runtime_rejected(self):
        other = str(uuid4())
        self.docs[2] = status(other)
        self.assert_blocked("ORCA_RUNTIME_RESTARTED_DURING_OBSERVATION")

    def test_provider_meta_runtime_mismatch_rejected(self):
        self.docs[1]["_meta"]["runtimeId"] = str(uuid4())
        self.assert_blocked("LIST_RUNTIME_DRIFT")

    def test_host_scope_missing_rejected(self):
        del self.docs[1]["result"]["hostScope"]
        self.assert_blocked("HOST_SCOPE_UNVERIFIABLE")

    def test_host_scope_omitted_not_explicit_rejected(self):
        del self.docs[1]["result"]["hostScope"]["omittedHostIds"]
        self.assert_blocked("HOST_SCOPE_OMITTED_NOT_EXPLICIT")

    def test_target_host_omitted_rejected(self):
        self.docs[1]["result"]["hostScope"]["omittedHostIds"] = [HOST]
        self.assert_blocked("TARGET_HOST_NOT_NATIVE_COVERED")

    def test_target_host_not_in_covered_rejected(self):
        self.docs[1]["result"]["hostScope"]["hostIds"] = ["another-host-0002"]
        self.assert_blocked("TARGET_HOST_NOT_NATIVE_COVERED")

    def test_terminal_missing_rejected(self):
        self.docs[1]["result"]["terminals"] = []
        self.assert_blocked("TARGET_TERMINAL_MISSING")

    def test_terminal_duplicate_rejected(self):
        self.docs[1]["result"]["terminals"] *= 2
        self.assert_blocked("TARGET_TERMINAL_MISSING")

    def test_terminal_host_wrong_rejected(self):
        self.docs[1]["result"]["terminals"][0]["executionHostId"] = "another-host-0002"
        self.assert_blocked("TERMINAL_HOST_MISMATCH")

    def test_terminal_orphaned_rejected(self):
        self.docs[1]["result"]["terminals"][0]["orphaned"] = True
        self.assert_blocked("TERMINAL_ORPHANED")

    def test_terminal_not_connected_rejected(self):
        self.docs[1]["result"]["terminals"][0]["connected"] = False
        self.assert_blocked("TERMINAL_ORPHANED")

    def test_no_stdout_even_if_exit_zero_rejected(self):
        def silent(argv, **kw):
            self.called.append((argv, kw))
            return subprocess.CompletedProcess(argv, 0, b"", b"single-instance lock")
        with self.assertRaisesRegex(g.BlockedPrecondition, "CLI_STDOUT_EMPTY"):
            g.inspect_readonly(self.f, silent)

    def test_non_json_exit_zero_rejected(self):
        def text(argv, **kw):
            return subprocess.CompletedProcess(argv, 0, b"not-json", b"")
        with self.assertRaisesRegex(g.BlockedPrecondition, "CLI_NONJSON"):
            g.inspect_readonly(self.f, text)

    def test_cli_failure_rejected(self):
        def fail(argv, **kw):
            return subprocess.CompletedProcess(argv, 1, b"", b"error")
        with self.assertRaisesRegex(g.BlockedPrecondition, "NATIVE_CLI_EXIT_NONZERO"):
            g.inspect_readonly(self.f, fail)

    def test_cli_timeout_rejected_no_retry(self):
        def timeout(argv, **kw):
            raise subprocess.TimeoutExpired(argv, 8)
        with self.assertRaisesRegex(g.BlockedPrecondition, "NO_RETRY"):
            g.inspect_readonly(self.f, timeout)

    def test_err_oversize_rejected(self):
        def noisy(argv, **kw):
            return subprocess.CompletedProcess(argv, 0, jsonbytes(status()), b"x" * (g.MAX_STDERR + 1))
        self.assert_blocked_with_runner(noisy, "CLI_STDERR_OVERSIZE")

    def assert_blocked_with_runner(self, runner, text):
        with self.assertRaisesRegex(g.BlockedPrecondition, text):
            g.inspect_readonly(self.f, runner)

    def test_stdout_oversize_rejected(self):
        def noisy(argv, **kw):
            return subprocess.CompletedProcess(argv, 0, b"x" * (g.MAX_STDOUT + 1), b"")
        self.assert_blocked_with_runner(noisy, "CLI_STDOUT_EMPTY_OR_TOO_LARGE")

    def test_extra_cli_command_is_not_ran(self):
        self.classify()
        self.assertEqual([x[0][1:] for x in self.called],
            [["status", "--json"], ["terminal", "list", "--json"], ["status", "--json"]])


if __name__ == "__main__":
    unittest.main()
