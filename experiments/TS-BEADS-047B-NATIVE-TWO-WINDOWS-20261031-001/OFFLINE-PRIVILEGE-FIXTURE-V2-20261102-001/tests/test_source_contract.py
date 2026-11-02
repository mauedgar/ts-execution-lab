# Static-only Python 3 source contract tests. No network, SQL, host access or PowerShell.
from pathlib import Path
import hashlib
import re
import unittest

BASE = Path(__file__).resolve().parents[1] / "candidate"
MODULE = BASE / "Security-047B-V2.psm1"
RUNNER = BASE / "Invoke-047B-V2-Fixture.ps1"
LAUNCHER = BASE / "Start-047B-V2.ps1"

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

class V2SourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = MODULE.read_bytes()
        cls.runner = RUNNER.read_bytes()
        cls.launcher = LAUNCHER.read_bytes()
        cls.m = cls.module.decode("utf-8")
        cls.r = cls.runner.decode("utf-8")
        cls.l = cls.launcher.decode("utf-8")

    def test_pinned_security_module(self):
        digest = hashlib.sha256(self.module).hexdigest().upper()
        self.assertEqual(digest, "101D9737C198DA7FD6070F9F8C961BF900499EA05857314E4F97701777239F77")
        self.assertIn(digest, self.r)
        self.assertIn(digest, self.l)

    def test_pinned_runner_blob(self):
        self.assertEqual(git_blob(self.runner), "8f9b66ada9b52e2d793a3aef3d8fea96c1d90291")
        self.assertIn(git_blob(self.runner), self.l)

    def test_unprovisioned_trust_anchor_fails_closed(self):
        self.assertIn("$script:V2TrustedKeySha256=('0' * 64)", self.m)
        self.assertIn("'NO_COMPETENT_ISSUER_PIN'", self.m)
        self.assertIn("'ISSUER_TRUST_ANCHOR_UNPROVISIONED'", self.m)
        self.assertIn("RSASignaturePadding]::Pss", self.m)
        self.assertIn("Assert-V2Authority $AuthorityDirectory $PSCommandPath $LauncherPath", self.r)

    def test_fixed_attempt_and_no_caller_hash(self):
        self.assertIn("TS-BEADS-047B-DOLT-FIXTURE-V2-20261102-001", self.m)
        self.assertNotIn("ApprovedGrantSha256", self.r + self.l)
        self.assertNotIn("ExecutionAttempt", self.r + self.l)
        self.assertIn("FileMode]::CreateNew", self.r)

    def test_no_sql_server_or_automatic_kill(self):
        self.assertNotRegex(self.r + self.m + self.l, r"(?i)\bsql-server\b")
        self.assertNotRegex(self.r + self.m + self.l, r"\.Kill\s*\(")
        self.assertIn("'UNKNOWN_EFFECT'", self.r)
        self.assertIn("'PARTIAL_NO_SQL'", self.r)

    def test_bounded_io_and_no_password_in_argv(self):
        self.assertIn("ReadCap(Stream stream,int cap)", self.r)
        self.assertIn("Task.WhenAny(all,Task.Delay(deadlineMs))", self.r)
        self.assertIn("RedirectStandardInput=$true", self.r)
        self.assertIn("16384,15000", self.r)
        self.assertNotIn("ArgumentList.Add($password)", self.r)
        self.assertIn("Array]::Clear($secretBytes", self.r)

    def test_both_privilege_tables_and_no_network_service(self):
        self.assertIn("FROM mysql.user", self.r)
        self.assertIn("FROM mysql.db", self.r)
        self.assertIn("Assert-V2NoNetworkExposure", self.r)
        self.assertIn("CreateDirectoryW", self.m)
        self.assertIn("D:P(A;;FA;;;", self.m)

if __name__ == "__main__":
    unittest.main(verbosity=2)
