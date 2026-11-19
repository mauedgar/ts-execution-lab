"""B006: check exact consumer CLI return codes, not only evaluate() objects."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
SCRIPT=ROOT/"receipt_validator.py"
FIXTURE=json.loads((ROOT/"fixtures"/"qa_report_v0.example.json").read_text())

def evidence(root):
    r=copy.deepcopy(FIXTURE)
    for item in r["artifacts"]:
        name=item["name"]
        data=("SYNTHETIC-ONLY-"+name).encode("utf8")
        (root/name).write_bytes(data)
        item["bytes"]=len(data)
        item["sha256"]=hashlib.sha256(data).hexdigest()
    return r

def cli(report,root=None,*args):
    with tempfile.TemporaryDirectory() as temp:
        file=Path(temp)/"receipt.json"
        file.write_text(json.dumps(report),encoding="utf8")
        command=[sys.executable,str(SCRIPT),str(file)]
        if root is not None:command+=["--artifact-root",str(root)]
        command+=list(args)
        proc=subprocess.run(command,text=True,capture_output=True,timeout=20,check=False)
        return proc.returncode,json.loads(proc.stdout)

class StrictConsumerCliTests(unittest.TestCase):
    def test_default_rejects_vector_with_matching_local_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            code,result=cli(evidence(Path(d)),Path(d))
            self.assertNotEqual(code,0)
            self.assertEqual(result["status"],"INVALID_REPORT")
            self.assertIn("synthetic_test_vector_forbidden_for_consumer",result["errors"])

    def test_explicit_strict_rejects_vector_with_matching_local_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            code,result=cli(evidence(Path(d)),Path(d),"--require-local-bytes")
            self.assertNotEqual(code,0)
            self.assertIn("synthetic_test_vector_forbidden_for_consumer",result["errors"])

    def test_default_rejects_vector_without_artifacts(self):
        code,result=cli(copy.deepcopy(FIXTURE))
        self.assertNotEqual(code,0)
        self.assertIn("synthetic_test_vector_forbidden_for_consumer",result["errors"])

    def test_diagnostic_mode_explicitly_allows_shape_only(self):
        code,result=cli(copy.deepcopy(FIXTURE),None,"--diagnostic-only")
        self.assertEqual(code,0)
        self.assertEqual(result["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(result["provider_native_verified"])
        self.assertFalse(result["Product_accepted"])

    def test_diagnostic_strict_conflict_is_rejected(self):
        code,result=cli(copy.deepcopy(FIXTURE),None,"--diagnostic-only","--require-local-bytes")
        self.assertNotEqual(code,0)
        self.assertIn("diagnostic_strict_modes_conflict",result["errors"])

    def test_nonvector_with_matching_bytes_passes_shape_only(self):
        with tempfile.TemporaryDirectory() as d:
            r=evidence(Path(d));r["original"]["custody"]="LOCAL_UNVERIFIED"
            code,result=cli(r,Path(d))
            self.assertEqual(code,0)
            self.assertEqual(result["status"],"VALID_SHAPE_UNATTESTED")
            self.assertTrue(result["artifact_bytes_verified_locally"])
            self.assertFalse(result["provider_native_verified"])
            self.assertFalse(result["Product_accepted"])

    def test_nonvector_without_bytes_fails_default(self):
        r=copy.deepcopy(FIXTURE);r["original"]["custody"]="LOCAL_UNVERIFIED"
        code,result=cli(r)
        self.assertNotEqual(code,0)
        self.assertIn("required_local_binary_readback_missing",result["errors"])

if __name__=="__main__":unittest.main()
