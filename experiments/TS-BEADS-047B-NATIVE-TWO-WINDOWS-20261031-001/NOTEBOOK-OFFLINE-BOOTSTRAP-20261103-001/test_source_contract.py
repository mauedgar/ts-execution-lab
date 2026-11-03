"""Source-only 047B checks. No SQL, DPAPI, Windows writes or Secrets."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / "Invoke-047B-NotebookOfflineBootstrap.ps1").read_text(encoding="utf-8")

class RunnerContract(unittest.TestCase):
    def test_safe_default(self):
        self.assertRegex(SOURCE, r"\[ValidateSet\('Inspect','Execute'\)\]\[string\]\$Mode\s*=\s*'Inspect'")
        self.assertIn("if ($Mode -ceq 'Inspect')", SOURCE)
        self.assertIn("'NO_SQL_OR_TAILSCALE_EFFECT'", SOURCE)
    def test_fixed_host_and_binary_identities(self):
        for text in (
            "DESKTOP-DJLBEQH",
            "DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91",
            "280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2",
            "dolt version 2[.]6[.]2",
            "bd version 1[.]3[.]2",
            "Assert-ExactFile $PSCommandPath",
        ):
            self.assertIn(text, SOURCE)
    def test_explicit_external_grant_precondition(self):
        for text in ("ExpectedGrantSha256", "ExpectedSourceSha256",
                     "TS047B_NOTEBOOK_SQL_GRANT_V1", "OFFLINE_SYNTHETIC_SQL_BOOTSTRAP_ONLY",
                     "originalTransportReceipt", "BLOCKED_INCOMPLETE_GRANT"):
            self.assertIn(text, SOURCE)
    def test_no_service_exposure(self):
        for token in ("'serve'", "'funnel'", "BLOCKED_SQL_LISTENER",
                      "NO_SERVER_STARTED", "SQL_SERVER_STARTED=FALSE"):
            self.assertIn(token, SOURCE)
        for prohibited in ("'sql-server'", "tailscale serve tcp", "tailscale funnel",
                           "0.0.0.0", "New-NetFirewallRule", "netsh interface portproxy",
                           "Start-Process", "Invoke-Expression", "Invoke-WebRequest"):
            self.assertNotIn(prohibited, SOURCE)
    def test_secret_boundary(self):
        for text in ("ProtectedData]::Protect", "DataProtectionScope]::CurrentUser",
                     "DirectorySecurity", "SetAccessRuleProtection($true,$false)",
                     "GetBytes(32)", "RedirectStandardInput", "Write($Sql)",
                     "ReadToEndAsync()", "IdentityReference"):
            self.assertIn(text, SOURCE)
        self.assertNotRegex(SOURCE, r"(?i)(--password\b|PASSWORD\s*=\s*['\"][^'\"]{3,}['\"])")
    def test_sql_is_scoped_and_does_not_auto_start_server(self):
        for text in ("CREATE DATABASE ts047b_beads;", "CREATE USER 'ts047b_writer'",
                     "GRANT ALL PRIVILEGES ON ts047b_beads.*", "GRANT SELECT ON ts047b_beads.*",
                     "ALTER USER 'root'@'localhost'", "privileges.db"):
            self.assertIn(text, SOURCE)
    def test_fail_closed_no_retry(self):
        for text in ("UNKNOWN_NATIVE_TIMEOUT_NO_KILL", "UNKNOWN_OR_PARTIAL_NATIVE_SQL_FAILURE",
                     "BLOCKED_EXISTING_ATTEMPT_OR_DATA", "UNKNOWN_OR_PARTIAL_OFFLINE_SQL_EFFECT_DO_NOT_RETRY_OR_CLEAN",
                     "BLOCKED_PRECONDITION_OR_PARTIAL_LOCAL_PREPARATION_DO_NOT_RETRY"):
            self.assertIn(text, SOURCE)
        self.assertNotIn("Remove-Item", SOURCE)
        self.assertNotIn("Stop-Process", SOURCE)

if __name__ == "__main__":
    unittest.main()
