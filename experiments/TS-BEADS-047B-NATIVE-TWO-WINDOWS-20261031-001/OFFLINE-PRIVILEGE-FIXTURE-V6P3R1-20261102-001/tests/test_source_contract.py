"""Deterministic SOURCE checks: no native host effects and no SQL."""
from pathlib import Path
import hashlib
import json
import re
import unittest

BASE=Path(__file__).resolve().parents[1]/'candidate'
SEC=BASE/'Security-047B-V6.psm1'
RUN=BASE/'Invoke-047B-V6-Fixture.ps1'
LCH=BASE/'Start-047B-V6.ps1'

def gitblob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

class SourceSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sec=SEC.read_text(encoding='utf-8')
        cls.runner_source=RUN.read_text(encoding='utf-8')
        cls.launch=LCH.read_text(encoding='utf-8')

    def test_git_blobs(self):
        pins={SEC:'70f5bee86358cf48ac6cded50c619ce46fed8f42',
              RUN:'e32375735698032d2bb465ce7072600aa0348d91',
              LCH:'46252e92823041b69a4870433f3b6aff1154d4ae'}
        for file,pin in pins.items():
            raw=file.read_bytes()
            self.assertEqual(gitblob(raw),pin)
            self.assertNotIn(b'\r\n',raw)
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
        self.assertIn(pins[SEC],self.runner_source)
        self.assertIn(pins[SEC],self.launch)
        self.assertIn(pins[RUN],self.launch)

    def test_unprovisioned_grant_fails_closed(self):
        self.assertIn("$script:V6TrustedKeySha256=('0' * 64)",self.sec)
        self.assertIn('NO_COMPETENT_ISSUER_PIN',self.sec)
        self.assertIn('SIGNED_SUBJECT_BLOB_MISMATCH',self.sec)
        self.assertIn('SIGNED_COMMIT_NOT_CHECKED_OUT',self.sec)
        self.assertIn('OFFHOST_CAS_OBSERVATION_ABSENT',self.sec)
        self.assertIn('ORIGINAL_PROVIDER_RECEIPTS_UNJOINED',self.sec)

    def test_correct_acl_arity(self):
        calls=re.findall(r'(?m)^\s*Assert-V6PrivateAcl\s+([^#\r\n]+)',self.runner_source)
        self.assertGreaterEqual(len(calls),3)
        for args in calls:
            self.assertLessEqual(len(args.strip().split()),2,args)
        self.assertIn('Assert-V6PrivateAcl $Privilege $true',self.runner_source)
        self.assertNotIn('Assert-V6PrivateAcl $Privilege $true $true',self.runner_source)
        self.assertIn('Assert-V6PrivateAcl $priv $true',self.runner_source)
        self.assertIn('CreateFileW(path,0x40000000,0,ref a,1,0x80000000',self.sec)

    def test_bootstrap_import_order(self):
        body=self.runner_source.rsplit('\ntry {',1)[-1]
        imp=body.index('Import-Module -Name $script:V6Module')
        before=body[:imp]
        self.assertNotRegex(before,r'(?m)^\s*Assert-V6\s*\(')
        self.assertIn("if($blob -cne $script:V6ModuleBlob){throw",before)

    def test_confirmed_exit_not_ambiguous(self):
        self.assertIn('if(-not $script:ChildExitConfirmed)',self.runner_source)
        self.assertIn("Record 'CHILD_EXIT'",self.runner_source)
        self.assertIn("Record 'CHILD_AMBIGUOUS'",self.runner_source)
        self.assertIn("'UNKNOWN_EFFECT'",self.runner_source)
        self.assertIn('lastExitCode=$script:ChildExitCode',self.runner_source)

    def test_no_protected_automatic_variable_assignments(self):
        # PowerShell automatic variable identifiers are case insensitive.
        protected=r'(?i)\$(?:script:|global:|local:)?(?:pid|home|lastexitcode)\s*=(?!=)'
        for source in (self.sec,self.runner_source,self.launch):
            self.assertIsNone(re.search(protected,source))
        self.assertIn('$script:ChildProcessId',self.runner_source)
        self.assertIn('$script:ChildExitCode',self.runner_source)
        self.assertIn('$userProfilePath',self.sec)

    def test_no_sql_without_external_key(self):
        self.assertIn('Assert-V6Authority $AuthorityDirectory $PSCommandPath $LauncherPath',self.runner_source)
        self.assertIn("FROM mysql.user",self.runner_source)
        self.assertIn("FROM mysql.db",self.runner_source)
        self.assertIn('-NoEnumerate',self.runner_source)
        self.assertIn('Task.WhenAny(all,Task.Delay(deadlineMs))',self.runner_source)
        self.assertNotIn('.Kill()',self.runner_source)
        self.assertNotIn('ArgumentList.Add($password)',self.runner_source)


    def test_child_ambiguous_evidence_fails_closed(self):
        for required in (
            "$script:ChildEffectAmbiguous=$true",
            "lastExitKnown=$exitObserved",
            "observedExitCode=$observedCode",
            "possibleAlive=$possiblyAlive",
            "errorClass=$errorClass",
            "reconciled=$false",
            "PRESERVE_ORIGINAL_PID_AND_RECEIPT_NO_RETRY",
            "if(-not $script:ChildExitConfirmed)",
            "$p.Dispose()",
        ):
            self.assertIn(required, self.runner_source, required)
        self.assertNotIn(".Kill()", self.runner_source)
        self.assertNotIn("Stop-Process", self.runner_source)
        self.assertIn("TS-BEADS-047B-DOLT-FIXTURE-V6P3-20261102-001", self.runner_source)

    def test_native_ast_adversarial_fixtures_frozen(self):
        ast_path=BASE.parent/'tests'/'Test-V6P3-ParserAndAst.ps1'
        src=ast_path.read_text(encoding='utf-8')
        for marker in ("AssignmentStatementAst", "UnaryExpressionAst", "Set-Variable",
                       "Set-Item", "PSVariable", "NEGATIVE_ACCEPTED", "BENIGN_FIXTURE"):
            self.assertIn(marker,src)
        self.assertIn("PASS_V6P3_AST_SOURCE_ONLY", src)

    def test_manifest_integrity_source_only(self):
        manifest=json.loads((BASE.parent/'MANIFEST.json').read_text(encoding='utf-8'))
        self.assertTrue(manifest['sourceOnly'])
        self.assertTrue(manifest['notDispatchable'])
        self.assertFalse(manifest['grantPresent'])
        self.assertFalse(manifest['sqlExecuted'])
        self.assertFalse(manifest['originalProviderEffectsReconciled'])
        self.assertEqual(len(manifest['files']), 8)
        for item in manifest['files']:
            file=BASE.parent/item['path']
            raw=file.read_bytes()
            self.assertEqual(len(raw),item['bytes'],file)
            self.assertEqual(hashlib.sha256(raw).hexdigest().upper(),item['sha256Utf8Lf'],file)
            self.assertEqual(gitblob(raw),item['gitBlobSha1'],file)
            self.assertNotIn(b'\r',raw)
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))

if __name__=='__main__':
    unittest.main(verbosity=2)
