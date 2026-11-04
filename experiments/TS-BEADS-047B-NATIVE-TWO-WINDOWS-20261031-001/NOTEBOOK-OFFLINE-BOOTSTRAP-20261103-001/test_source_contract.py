"""IR001 source-only security regression. Never invokes Dolt SQL or host writes.

Behavioral tests execute only the unconditionally denied path and wrong-host Inspect
on disposable CI. They do not qualify native notebook ACL, DPAPI or SQL accounts.
"""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT / "Invoke-047B-NotebookOfflineBootstrap.ps1"
TEXT = RUNNER.read_text(encoding="utf-8")
PWSH = shutil.which("pwsh")

def denied(*args, localappdata=None, computername=None):
    env = os.environ.copy()
    if localappdata is not None:
        env["LOCALAPPDATA"] = str(localappdata)
    if computername is not None:
        env["COMPUTERNAME"] = computername
    return subprocess.run(
        [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(RUNNER), *args],
        capture_output=True, text=True, errors="replace", timeout=20, env=env, check=False,
    )

class SourceBoundary(unittest.TestCase):
    def test_inspect_is_default_and_execute_denied_first(self):
        self.assertRegex(TEXT, r"\[ValidateSet\('Inspect','Execute'\)\]\[string\]\$Mode = 'Inspect'")
        self.assertLess(TEXT.index("if ($Mode -ceq 'Execute')"), TEXT.index("function Assert-ExactBinary"))
        self.assertIn("BLOCKED_UNADMITTED_EFFECT_NO_TRUSTED_ORIGINAL_RECEIPT", TEXT)

    def test_no_effectful_sql_or_secret_apis(self):
        # Guard against reintroducing the original IR001 unsafe bootstrap.
        for forbidden in (
            r"\bCreateDirectory\s*\(", r"\bWriteAllBytes\s*\(", r"\bWriteAllText\s*\(",
            r"\bSet-Acl\b", r"\bStart-Process\b", r"\bInvoke-Expression\b",
            r"\bALTER\s+USER\b", r"\bCREATE\s+USER\b", r"\bGRANT\s+SELECT\b",
            r"\bProtectedData\]::Protect", r"\bRedirectStandardInput\s*=",
            r"\bWaitForExit\s*\(", r"\bRemove-Item\b", r"\bStop-Process\b",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertIsNone(re.search(forbidden, TEXT, re.IGNORECASE))

    def test_no_self_asserted_grant_admission(self):
        for forbidden in ("ExpectedGrantSha256", "GrantPath", "ConvertFrom-Json $grant",
                          "originalTransportReceipt", "decision -cne 'ADMITTED'"):
            self.assertNotIn(forbidden, TEXT)

    def test_inspect_checks_known_hashes_and_versions(self):
        for s in ("DESKTOP-DJLBEQH", "DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91",
                  "280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2",
                  "dolt version 2[.]6[.]2", "bd version 1[.]3[.]2"):
            self.assertIn(s, TEXT)

    def test_inspect_blocks_unknown_proxy_and_reparse(self):
        for s in ("ConvertFrom-Json", "BackendState", "Self.Online",
                  "Assert-NoReparseAncestor", "FileAttributes]::ReparsePoint",
                  "BLOCKED_POSSIBLE_SQL_LISTENER", "BLOCKED_EXISTING_ATTEMPT_OR_DATA"):
            self.assertIn(s, TEXT)

    def test_sid_and_peer_not_misrepresented(self):
        self.assertIn("WindowsIdentity]::GetCurrent()", TEXT)
        self.assertIn("SID_PIN_AND_PEER_IDENTITY_UNVERIFIED", TEXT)
        self.assertIn("SQL_ACCOUNT_ACL_DPAPI_AND_RESTORE_UNVERIFIED", TEXT)
        self.assertIn("ORIGINAL_PROVIDER_RECEIPT_UNVERIFIED", TEXT)

    @unittest.skipUnless(os.name == "nt" and PWSH, "Windows PowerShell 7 CI only")
    def test_execute_denied_without_identity_or_grant(self):
        result = denied("-Mode", "Execute")
        self.assertEqual(result.returncode, 41, result.stderr)
        self.assertIn("BLOCKED_UNADMITTED_EFFECT_NO_TRUSTED_ORIGINAL_RECEIPT", result.stdout)
        self.assertIn("NO_SQL_OR_TAILSCALE_EFFECT", result.stdout)

    @unittest.skipUnless(os.name == "nt" and PWSH, "Windows PowerShell 7 CI only")
    def test_forged_grant_file_cannot_be_consumed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            forged = root / "forged.json"
            forged.write_text('{"decision":"ADMITTED","attempt":"TS047B_NOTEBOOK_OFFLINE_BOOTSTRAP_20261103_001"}')
            result = denied("-Mode", "Execute", "-GrantPath", str(forged), localappdata=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "TS-BEADS-047B").exists())

    @unittest.skipUnless(os.name == "nt" and PWSH, "Windows PowerShell 7 CI only")
    def test_spoofed_computername_does_not_admit_execute(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = denied("-Mode", "Execute", localappdata=root, computername="DESKTOP-DJLBEQH")
            self.assertEqual(result.returncode, 41)
            self.assertFalse((root / "TS-BEADS-047B").exists())

    @unittest.skipUnless(os.name == "nt" and PWSH, "Windows PowerShell 7 CI only")
    def test_inspect_wrong_host_denied_without_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # GitHub-hosted runner identity is not the named physical notebook.
            result = denied("-Mode", "Inspect", localappdata=root)
            self.assertEqual(result.returncode, 11, result.stderr)
            self.assertIn("BLOCKED_READONLY_PREFLIGHT", result.stdout)
            self.assertFalse((root / "TS-BEADS-047B").exists())

if __name__ == "__main__":
    unittest.main()
