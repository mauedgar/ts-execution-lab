"""TS-BEADS 047B IR002 advisory repair: non-effectful source + Windows negative fixtures.

Hosted Windows fixtures use disposable temporary directories only; never SQL,
DPAPI, Tailscale, native notebook or Product resources.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "Invoke-047B-NotebookOfflineBootstrap.ps1"
TEXT = RUNNER.read_text(encoding="utf-8")
PWSH = shutil.which("pwsh")
IS_WINDOWS = os.name == "nt" and bool(PWSH)

def invoke(*args, env=None):
    return subprocess.run(
        [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
         str(RUNNER), *[str(x) for x in args]],
        capture_output=True, text=True, timeout=20, check=False,
        errors="replace", env=env,
    )


def isolated_path_guard_fixture(probe_path):
    """CI-only: isolate the production guard function in a disposable PS1.

    The operator runner never receives ProbePath. This fixture is materialized
    only on ephemeral hosted Windows CI to exercise reparse/path negatives.
    """
    start = TEXT.index("function Assert-NoReparseAncestor {")
    end = TEXT.index("function Assert-ExactBinary {", start)
    function_source = TEXT[start:end]
    with tempfile.TemporaryDirectory() as scratch:
        fixture = Path(scratch) / "fixture-only-path-guard.ps1"
        fixture.write_text(
            "[CmdletBinding()]\n"
            "param([string]$ProbePath)\n"
            "Set-StrictMode -Version Latest\n"
            "$ErrorActionPreference = 'Stop'\n" + function_source +
            "\ntry { Assert-NoReparseAncestor $ProbePath; "
            "'CI_FIXTURE_PATH_OK_NOT_HOST_QUALIFIED'; exit 0 } "
            "catch { 'CI_FIXTURE_PATH_BLOCKED'; exit 42 }\n",
            encoding="utf-8",
        )
        return subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
             str(fixture), "-ProbePath", str(probe_path)],
            capture_output=True, text=True, timeout=20, check=False,
            errors="replace",
        )

class SourceOnly(unittest.TestCase):
    def test_execute_denied_before_readonly_functions(self):
        self.assertIn("if ($Mode -ceq 'Execute')", TEXT)
        self.assertLess(TEXT.index("if ($Mode -ceq 'Execute')"),
                        TEXT.index("function Assert-NoReparseAncestor"))
        self.assertIn("BLOCKED_UNADMITTED_EFFECT_NO_TRUSTED_ORIGINAL_RECEIPT", TEXT)

    def test_probepath_fixture_not_exposed_by_production_runner(self):
        self.assertIn("[ValidateSet('Inspect','Execute')]", TEXT)
        self.assertNotIn("ProbePath", TEXT)
        self.assertNotIn("PATH_PROBE_OK_NOT_HOST_QUALIFIED", TEXT)

    def test_no_third_party_cli_calls(self):
        for forbidden in ("& $dolt", "& $bd", "& $ts", "& $Tailscale", "Get-Command tailscale",
                          "dolt version", "bd version", "serve status --json",
                          "funnel status --json", "Invoke-Expression", "Start-Process"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, TEXT)

    def test_no_native_effect_apis(self):
        for pattern in (
            r"\bCreateDirectory\s*\(", r"\bWriteAllBytes\s*\(", r"\bWriteAllText\s*\(",
            r"\bSet-Acl\b", r"\bALTER\s+USER\b", r"\bCREATE\s+USER\b",
            r"\bGRANT\s+SELECT\b", r"\bProtectedData\]::Protect",
            r"\bWaitForExit\s*\(", r"\bRemove-Item\b", r"\bStop-Process\b",
            r"\bInvoke-WebRequest\b", r"\bInvoke-RestMethod\b"
        ):
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, TEXT, re.IGNORECASE))

    def test_binary_pin_not_version_claim(self):
        for value in (
            "DESKTOP-DJLBEQH",
            "DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91",
            "280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2",
            "Assert-ExactBinary $dolt", "Assert-ExactBinary $bd",
            "BINARY_HASH_ONLY_VERSION_UNVERIFIED"
        ):
            self.assertIn(value, TEXT)

    def test_partial_status_never_promotes_host_security(self):
        for value in ("READONLY_OS_OBSERVATION_PARTIAL",
                      "TAILSCALE_AND_PEER_STATE_UNVERIFIED",
                      "ALTERNATE_SQL_LISTENERS_UNVERIFIED",
                      "SID_PIN_AND_ACL_UNVERIFIED",
                      "REPARSE_SNAPSHOT_NOT_ATOMIC",
                      "PROVIDER_ORIGINAL_ATTEMPT_UNVERIFIED",
                      "SQL_DPAPI_BACKUP_RESTORE_UNVERIFIED"):
            self.assertIn(value, TEXT)
        self.assertNotIn("NOTEBOOK_READONLY_PREFLIGHT_PASS", TEXT)

    def test_reparse_and_containment_checks(self):
        for value in ("FileAttributes]::ReparsePoint", "Assert-NoReparseAncestor $base",
                      "IsPathFullyQualified", "BLOCKED_ROOT_CONTAINMENT",
                      "BLOCKED_EXISTING_ATTEMPT_OR_DATA",
                      "BLOCKED_POSSIBLE_SQL_LISTENER"):
            self.assertIn(value, TEXT)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_execute_unconditionally_denied(self):
        result = invoke("-Mode", "Execute")
        self.assertEqual(result.returncode, 41, result.stderr)
        self.assertIn("BLOCKED_UNADMITTED_EFFECT", result.stdout)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_forged_host_and_grant_cannot_enable_execute(self):
        with tempfile.TemporaryDirectory() as d:
            env = os.environ.copy()
            env["COMPUTERNAME"] = "DESKTOP-DJLBEQH"
            env["LOCALAPPDATA"] = d
            r = invoke("-Mode", "Execute", env=env)
            self.assertEqual(r.returncode, 41)
            self.assertFalse((Path(d) / "TS-BEADS-047B").exists())

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_regular_absolute_directory_path_probe(self):
        with tempfile.TemporaryDirectory() as d:
            r = isolated_path_guard_fixture(d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("CI_FIXTURE_PATH_OK_NOT_HOST_QUALIFIED", r.stdout)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_nonexistent_path_probe_denied(self):
        with tempfile.TemporaryDirectory() as d:
            missing = Path(d) / "does-not-exist"
            r = isolated_path_guard_fixture(missing)
            self.assertEqual(r.returncode, 42)
            self.assertIn("CI_FIXTURE_PATH_BLOCKED", r.stdout)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_relative_path_probe_denied(self):
        r = isolated_path_guard_fixture("relative-path")
        self.assertEqual(r.returncode, 42)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_junction_reparse_probe_denied(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "target"
            link = root / "junction"
            target.mkdir()
            mklink = subprocess.run(["cmd", "/D", "/C", "mklink", "/J",
                                     str(link), str(target)],
                                    capture_output=True, text=True, timeout=15, check=False)
            if mklink.returncode != 0:
                self.skipTest("NTFS junction capability unavailable on CI fixture")
            r = isolated_path_guard_fixture(link)
            self.assertEqual(r.returncode, 42, r.stdout + r.stderr)

    @unittest.skipUnless(IS_WINDOWS, "Windows pwsh only")
    def test_wrong_host_inspect_denied(self):
        with tempfile.TemporaryDirectory() as d:
            env = os.environ.copy()
            env["LOCALAPPDATA"] = d
            r = invoke("-Mode", "Inspect", env=env)
            self.assertEqual(r.returncode, 11, r.stdout + r.stderr)
            self.assertIn("BLOCKED_READONLY_OS_OBSERVATION", r.stdout)
            self.assertFalse((Path(d) / "TS-BEADS-047B").exists())

if __name__ == "__main__":
    unittest.main()
