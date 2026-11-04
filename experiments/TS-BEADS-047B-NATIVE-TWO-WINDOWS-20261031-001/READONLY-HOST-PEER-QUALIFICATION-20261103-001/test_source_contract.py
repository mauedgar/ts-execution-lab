"""TS047B read-only native host/peer source contract: Windows CI disposable fixtures.

No native notebook commands, no Tailscale CLI, SQL, DPAPI, product, or credentials.
The pure production Evaluate-Status function is exercised from an isolated
temporary PS fixture. Only a wrong-host denial runs the production script.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent
RUNNER=ROOT/"Invoke-047B-ReadOnlyHostPeerQualification.ps1"
TEXT=RUNNER.read_text(encoding="utf-8")
PWSH=shutil.which("pwsh")
WINDOWS=os.name=="nt" and bool(PWSH)

def status_fixture(doc):
    start=TEXT.index("function Get-StringDigest {")
    end=TEXT.index("function Run-TailscaleStatus {", start)
    funcs=TEXT[start:end]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        script=root/"ci-status-fixture.ps1"
        docpath=root/"ci-status-input.json"
        script.write_text(
            "[CmdletBinding()]\nparam([string]$JsonFile)\n"
            "$ErrorActionPreference='Stop'\n" + funcs +
            "\ntry {\n"
            "  $raw=[IO.File]::ReadAllText($JsonFile)\n"
            "  $res=Evaluate-Status -Text $raw -SelfName 'DESKTOP-DJLBEQH' "
            "-PeerName 'DESKTOP-3LJ0E54'\n"
            "  if($res.self_node_key_sha256.Length -ne 64 -or "
            "$res.peer_node_key_sha256.Length -ne 64){ throw 'BAD_HASH' }\n"
            "  'CI_STATUS_VALIDATED'; exit 0\n"
            "} catch { 'CI_STATUS_BLOCKED'; exit 42 }\n",
            encoding="utf-8"
        )
        docpath.write_text(json.dumps(doc), encoding="utf-8")
        return subprocess.run(
            [PWSH,"-NoLogo","-NoProfile","-NonInteractive",
             "-File",str(script),"-JsonFile",str(docpath)],
            capture_output=True,text=True,timeout=20,check=False,errors="replace"
        )

def valid_status():
    return {
        "BackendState":"Running",
        "Self":{"Online":True,"HostName":"DESKTOP-DJLBEQH",
                "PublicKey":"nodekey:fake-notebook-key"},
        "Peer":{"p1":{"HostName":"DESKTOP-3LJ0E54","Online":True,
                      "PublicKey":"nodekey:fake-desktop-key"}}
    }

class SourceFence(unittest.TestCase):
    def test_fixed_two_roles_hostnames_and_tailscale_digest(self):
        for token in (
            "[ValidateSet('Notebook','Desktop')]",
            "DESKTOP-DJLBEQH","DESKTOP-3LJ0E54",
            "9AB35EB10B9076EC7262696EA98428C91CC6E5F4EFE3FAEFD786EFED0BB6C68D",
            "C:\\Program Files\\Tailscale\\tailscale.exe",
        ):
            with self.subTest(token=token):
                self.assertIn(token,TEXT)

    def test_no_sql_or_mutating_interfaces(self):
        for regex in (
            r"\bdolt\b",r"\bbd init\b",r"\bCREATE\s+USER\b",
            r"\bALTER\s+USER\b",r"\bSet-Acl\b",r"\bRemove-Item\b",
            r"\bNew-Item\b",r"\bWriteAllBytes\b",r"\bProtectedData\b",
            r"\bserve\s+--",r"\bfunnel\s+--",r"\bInvoke-RestMethod\b"
        ):
            with self.subTest(regex=regex):
                self.assertIsNone(re.search(regex,TEXT,re.I))
        self.assertIn("NO_SQL_OR_CONFIGURATION_EFFECT",TEXT)

    def test_no_raw_identity_address_or_tailscale_dump(self):
        self.assertNotIn("Write-Output $statusText",TEXT)
        self.assertNotIn("'SID='+$win.User.Value",TEXT)
        self.assertIn("TAILSCALE_PEER_ADVERTISED_ONLINE=TRUE",TEXT)
        self.assertIn("TAILSCALE_DATA_ROUTE_AND_SERVE_FUNNEL_UNVERIFIED",TEXT)
        self.assertIn("ACL_EFFECTIVE_ON_FUTURE_SQL_ROOT_UNVERIFIED",TEXT)

    def test_status_cli_single_fixed_bounded_call(self):
        self.assertIn("$psi.ArgumentList.Add('status')",TEXT)
        self.assertIn("$psi.ArgumentList.Add('--json')",TEXT)
        self.assertIn("$child.WaitForExit(12000)",TEXT)
        self.assertIn("$child.Kill($true)",TEXT)
        self.assertNotIn("Start-Process",TEXT)

    def test_fail_closed_initial_host_gate(self):
        self.assertLess(TEXT.index("[Environment]::MachineName -cne $expectedHost"),
                        TEXT.index("Run-TailscaleStatus -Exe $tailscaleExe"))
        self.assertIn("BLOCKED_READONLY_HOST_PEER_QUALIFICATION",TEXT)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_wrong_host_rejects_without_cli(self):
        with tempfile.TemporaryDirectory() as d:
            env=os.environ.copy()
            env["LOCALAPPDATA"]=d
            result=subprocess.run(
                [PWSH,"-NoLogo","-NoProfile","-NonInteractive",
                 "-File",str(RUNNER),"-Role","Notebook"],
                env=env,text=True,capture_output=True,timeout=20,check=False)
            self.assertEqual(result.returncode,22,result.stdout+result.stderr)
            self.assertIn("BLOCKED_READONLY_HOST_PEER_QUALIFICATION",result.stdout)
            self.assertFalse((Path(d)/"TS-BEADS-047B").exists())

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_peer_online_status(self):
        r=status_fixture(valid_status())
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertIn("CI_STATUS_VALIDATED",r.stdout)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_peer_offline_blocks(self):
        value=valid_status()
        value["Peer"]["p1"]["Online"]=False
        r=status_fixture(value)
        self.assertEqual(r.returncode,42,r.stdout+r.stderr)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_duplicate_hostname_blocks(self):
        value=valid_status()
        value["Peer"]["p2"]={"HostName":"DESKTOP-3LJ0E54","Online":True,
                            "PublicKey":"nodekey:another-key"}
        r=status_fixture(value)
        self.assertEqual(r.returncode,42,r.stdout+r.stderr)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_missing_self_key_blocks(self):
        value=valid_status()
        value["Self"].pop("PublicKey")
        r=status_fixture(value)
        self.assertEqual(r.returncode,42,r.stdout+r.stderr)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_invalid_state_blocks(self):
        value=valid_status()
        value["BackendState"]="Stopped"
        r=status_fixture(value)
        self.assertEqual(r.returncode,42,r.stdout+r.stderr)

    @unittest.skipUnless(WINDOWS,"Windows PowerShell7 CI")
    def test_mocked_wrong_peer_name_blocks(self):
        value=valid_status()
        value["Peer"]["p1"]["HostName"]="OTHER-HOST"
        r=status_fixture(value)
        self.assertEqual(r.returncode,42,r.stdout+r.stderr)

if __name__=="__main__":
    unittest.main()
