"""Deterministic SOURCE checks: no native host effects and no SQL."""
from pathlib import Path
import hashlib
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
        cls.run=RUN.read_text(encoding='utf-8')
        cls.launch=LCH.read_text(encoding='utf-8')

    def test_git_blobs(self):
        pins={SEC:'70f5bee86358cf48ac6cded50c619ce46fed8f42',
              RUN:'21b48eb337dfe20a84b36408fe9c9ed98546febb',
              LCH:'af06633d104a8c860773fda4b96bc3f9200c1f7b'}
        for file,pin in pins.items():
            raw=file.read_bytes()
            self.assertEqual(gitblob(raw),pin)
            self.assertNotIn(b'\r\n',raw)
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
        self.assertIn(pins[SEC],self.run)
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
        calls=re.findall(r'(?m)^\s*Assert-V6PrivateAcl\s+([^#\r\n]+)',self.run)
        self.assertGreaterEqual(len(calls),3)
        for args in calls:
            self.assertLessEqual(len(args.strip().split()),2,args)
        self.assertIn('Assert-V6PrivateAcl $Privilege $true',self.run)
        self.assertNotIn('Assert-V6PrivateAcl $Privilege $true $true',self.run)
        self.assertIn('Assert-V6PrivateAcl $priv $true',self.run)
        self.assertIn('CreateFileW(path,0x40000000,0,ref a,1,0x80000000',self.sec)

    def test_bootstrap_import_order(self):
        body=self.run.rsplit('\ntry {',1)[-1]
        imp=body.index('Import-Module -Name $script:V6Module')
        before=body[:imp]
        self.assertNotRegex(before,r'(?m)^\s*Assert-V6\s*\(')
        self.assertIn("if($blob -cne $script:V6ModuleBlob){throw",before)

    def test_confirmed_exit_not_ambiguous(self):
        self.assertIn('if(-not $script:ChildExitConfirmed)',self.run)
        self.assertIn("Record 'CHILD_EXIT'",self.run)
        self.assertIn("Record 'CHILD_AMBIGUOUS'",self.run)
        self.assertIn("'UNKNOWN_EFFECT'",self.run)
        self.assertIn('lastExitCode=$script:ChildExitCode',self.run)

    def test_no_protected_automatic_variable_assignments(self):
        # PowerShell automatic variable identifiers are case insensitive.
        protected=r'(?i)\$(?:script:|global:|local:)?(?:pid|home|lastexitcode)\s*=(?!=)'
        for source in (self.sec,self.run,self.launch):
            self.assertIsNone(re.search(protected,source))
        self.assertIn('$script:ChildProcessId',self.run)
        self.assertIn('$script:ChildExitCode',self.run)
        self.assertIn('$userProfilePath',self.sec)

    def test_no_sql_without_external_key(self):
        self.assertIn('Assert-V6Authority $AuthorityDirectory $PSCommandPath $LauncherPath',self.run)
        self.assertIn("FROM mysql.user",self.run)
        self.assertIn("FROM mysql.db",self.run)
        self.assertIn('-NoEnumerate',self.run)
        self.assertIn('Task.WhenAny(all,Task.Delay(deadlineMs))',self.run)
        self.assertNotIn('.Kill()',self.run)
        self.assertNotIn('ArgumentList.Add($password)',self.run)

if __name__=='__main__':
    unittest.main(verbosity=2)
