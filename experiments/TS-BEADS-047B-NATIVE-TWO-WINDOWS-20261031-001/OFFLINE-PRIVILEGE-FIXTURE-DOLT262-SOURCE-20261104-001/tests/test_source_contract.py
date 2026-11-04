"""Source-only negatives for the distinct, non-dispatchable Dolt 2.6.2 candidate.

No subprocesses, network, SQL, credentials, Windows registry or host effects.
"""
import hashlib
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1] / "candidate"
MODULE = ROOT / "Security-047B-D262.psm1"
RUNNER = ROOT / "Invoke-047B-D262-Fixture.ps1"
LAUNCHER = ROOT / "Start-047B-D262.ps1"
OLD_DOLT = "BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967"
NEW_DOLT = "DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91"
ATTEMPT = "TS-BEADS-047B-DOLT262-OFFLINE-FIXTURE-20261104-001"


def git_blob(path: pathlib.Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class Dolt262SourceOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = MODULE.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")

    def test_all_three_sources_are_lf_utf8(self):
        for p in (MODULE, RUNNER, LAUNCHER):
            with self.subTest(file=p.name):
                raw = p.read_bytes()
                self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
                self.assertNotIn(b"\r", raw)
                self.assertTrue(raw.endswith(b"\n"))
                raw.decode("utf-8")

    def test_new_attempt_is_distinct(self):
        self.assertIn(ATTEMPT, self.module)
        self.assertIn(ATTEMPT, self.runner)
        self.assertNotIn("TS-BEADS-047B-DOLT-FIXTURE-V6-20261102-001", self.module + self.runner)
        self.assertIn("TS047B-Offline-D262", self.module)
        self.assertNotIn("TS047B-Offline-V6", self.module)

    def test_exact_installed_dolt_binding(self):
        self.assertIn(NEW_DOLT, self.module)
        self.assertIn(NEW_DOLT, self.runner)
        self.assertNotIn(OLD_DOLT, self.module + self.runner + self.launcher)

    def test_no_effect_admission_without_external_key(self):
        self.assertIn("$script:V6TrustedKeySha256=('0' * 64)", self.module)
        self.assertIn("ISSUER_TRUST_ANCHOR_UNPROVISIONED", self.module)
        self.assertIn("NO_COMPETENT_ISSUER_PIN", self.module)
        self.assertIn("Assert-V6Authority $AuthorityDirectory $PSCommandPath $LauncherPath", self.runner)
        self.assertIn("Invoke-AuthorizedFixture", self.runner)
        self.assertIn("if($Preflight)", self.runner)
        self.assertIn("if($Preflight)", self.launcher)

    def test_module_pin_verified_by_runner(self):
        blob = git_blob(MODULE)
        self.assertIn("$script:V6ModuleBlob='" + blob + "'", self.runner)
        self.assertIn(blob, self.launcher)
        self.assertIn("SECURITY_MODULE_BLOB_MISMATCH", self.runner)

    def test_runner_pin_verified_by_launcher(self):
        blob = git_blob(RUNNER)
        self.assertIn(blob, self.launcher)
        self.assertIn("RUNNER_BLOB_MISMATCH", self.launcher)

    def test_no_server_or_tailscale_configuration_effect(self):
        combined = self.module + self.runner + self.launcher
        self.assertNotIn("sql-server", combined)
        self.assertNotIn("serve set", combined)
        self.assertNotIn("funnel on", combined)
        self.assertIn("Assert-V6NoNetworkExposure", self.runner)
        self.assertIn("Get-NetTCPConnection -State Listen", self.module)


if __name__ == "__main__":
    unittest.main()
