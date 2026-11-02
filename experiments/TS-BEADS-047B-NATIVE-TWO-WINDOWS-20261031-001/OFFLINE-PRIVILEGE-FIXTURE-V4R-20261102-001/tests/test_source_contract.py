"""TS-BEADS 047B V4R deterministic source-only checks; NO SQL or host effects."""
import hashlib
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SEC=ROOT/'candidate'/'Security-047B-V4R.psm1'
RUN=ROOT/'candidate'/'Invoke-047B-V4R-Fixture.ps1'
LCH=ROOT/'candidate'/'Start-047B-V4R.ps1'

def blob(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode('ascii')+b'\0'+b).hexdigest()

class Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sec=SEC.read_bytes().decode('utf-8')
        cls.run=RUN.read_bytes().decode('utf-8')
        cls.lch=LCH.read_bytes().decode('utf-8')
        for file in (SEC,RUN,LCH):
            b=file.read_bytes()
            assert b'\r\n' not in b and not b.startswith(b'\xef\xbb\xbf')

    def test_source_identity(self):
        self.assertEqual(blob(SEC.read_bytes()),'2451f61a401be1fe2b920b1752d554d8a6ab27e9')
        self.assertEqual(blob(RUN.read_bytes()),'5e3f5b56d5ac474081dff82eb022120587ebc7a8')
        self.assertIn('2451f61a401be1fe2b920b1752d554d8a6ab27e9',self.lch)
        self.assertIn('2451f61a401be1fe2b920b1752d554d8a6ab27e9',self.run)
        self.assertIn('5e3f5b56d5ac474081dff82eb022120587ebc7a8',self.lch)

    def test_unprovisioned_gate(self):
        self.assertIn("$script:V4RTrustedKeySha256=('0' * 64)",self.sec)
        self.assertIn("'NO_COMPETENT_ISSUER_PIN'",self.sec)
        self.assertIn('RSASignaturePadding]::Pss',self.sec)
        self.assertIn('SIGNED_SUBJECT_BLOB_MISMATCH',self.sec)
        self.assertIn('OFFHOST_CAS_OBSERVATION_ABSENT',self.sec)
        self.assertIn('ORIGINAL_PROVIDER_RECEIPTS_UNJOINED',self.sec)

    def test_acl_sources(self):
        self.assertIn('CreateDirectoryW',self.sec)
        self.assertIn('CreateFileW(path,0x40000000,0,ref a,1,0x80000000',self.sec)
        self.assertIn('D:P(A;OICI;FA;;;',self.sec)
        self.assertIn('New-V4RAtomicPrivateFile $paths.Receipt',self.run)
        self.assertIn('Assert-V4RPrivateAcl $Privilege $true',self.run)
        self.assertIn('Assert-V4RPrivateAcl $priv $true',self.run)
        self.assertNotIn('FileMode]::CreateNew',self.run)

    def test_effect_taxonomy(self):
        self.assertIn('StageInFlight',self.run)
        self.assertIn("'UNKNOWN_EFFECT'",self.run)
        self.assertIn("'FAILED_OR_PARTIAL_SQL_EFFECT'",self.run)
        self.assertIn("'PARTIAL_NO_SQL'",self.run)
        self.assertIn('lastExitCode=$script:LastExitCode',self.run)
        self.assertIn('confirmedStages=$script:ConfirmedStages',self.run)
        self.assertIn('CHILD_AMBIGUOUS',self.run)

    def test_sql_evidence_limit(self):
        self.assertIn('FROM mysql.user',self.run)
        self.assertIn('FROM mysql.db',self.run)
        self.assertIn('-NoEnumerate',self.run)
        self.assertIn('READBACK_ROWS_NOT_ARRAY',self.run)
        self.assertIn('ReadCap(Stream stream,int cap)',self.run)
        self.assertIn('Task.WhenAny(all,Task.Delay(deadlineMs))',self.run)
        self.assertNotIn('sql-server',self.run)
        self.assertNotIn('.Kill()',self.run)
        self.assertNotIn('ArgumentList.Add($password)',self.run)

if __name__=='__main__':
    unittest.main(verbosity=2)
