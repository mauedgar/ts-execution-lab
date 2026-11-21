import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
V0=ROOT/"receipt_validator.py"
V01=ROOT/"receipt_validator_v01.py"
FIXTURE=ROOT/"fixtures"/"qa_report_v01_observe_only.example.json"

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class VersionedNetworkAxes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v0=module(V0,"ee_v0")
        cls.v01=module(V01,"ee_v01")
        cls.base=json.loads(FIXTURE.read_text(encoding="utf8"))

    def check(self,value):
        return self.v01.evaluate(value)

    def test_observe_only_has_functional_pass_but_no_security_acceptance(self):
        result=self.check(copy.deepcopy(self.base))
        self.assertEqual(result["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertEqual(result["functional_browser_status"],"PASS")
        self.assertEqual(result["network_assurance_status"],"OBSERVE_ONLY_UNATTESTED")
        self.assertEqual(result["terminal_result"],"PASS_FUNCTIONAL_ONLY")
        self.assertFalse(result["network_policy_qualified"])
        self.assertFalse(result["provider_native_verified"])
        self.assertFalse(result["Product_accepted"])

    def test_stable_v0_rejects_versioned_observe_only(self):
        result=self.v0.evaluate(copy.deepcopy(self.base))
        self.assertEqual(result["status"],"INVALID_REPORT")
        self.assertIn("wrong_schema",result["errors"])
        self.assertIn("browser_pass_without_preventive_egress",result["errors"])

    def test_prospective_seven_negative_policy_vectors(self):
        cases=[
          (lambda x:x.update(Product_accepted=True),"false_product_acceptance_required"),
          (lambda x:x.update(provider_native_verified=True),"false_provider_attestation_required"),
          (lambda x:x.update(reported_verdict="PASS"),"browser_pass_verdict_mismatch"),
          (lambda x:x.update(network_assurance_status="PREVENTIVE_BROWSER_ABORT"),"observe_only_assurance_mismatch"),
          (lambda x:x.update(terminal_result="PASS_WITH_BROWSER_ABORT"),"observe_only_terminal_mismatch"),
          (lambda x:x["network"].update(service_workers="BLOCKED"),"observe_only_serviceworkers_overclaim"),
          (lambda x:x["network"].update(outbound_attempted=1,outbound_blocked=1),"observe_only_cannot_claim_blocked"),
          (lambda x:x["runner"].pop("driver_binary_sha256"),"chromedriver_missing_driver_binary_sha256"),
          (lambda x:x["runner"].pop("browser_binary_sha256"),"chromedriver_missing_browser_binary_sha256"),
          (lambda x:x["artifacts"].pop(),"browser_pass_missing_trace_or_log")
        ]
        for mutate,code in cases:
            with self.subTest(code=code):
                data=copy.deepcopy(self.base)
                mutate(data)
                result=self.check(data)
                self.assertEqual(result["status"],"INVALID_REPORT")
                self.assertIn(code,result["errors"])

    def test_preventive_browser_policy_stays_distinct(self):
        data=copy.deepcopy(self.base)
        data["network"]["enforcement"]="PREVENTIVE_BROWSER_ABORT"
        data["network"]["service_workers"]="BLOCKED"
        data["network"]["outbound_attempted"]=1
        data["network"]["outbound_blocked"]=1
        data["network_assurance_status"]="PREVENTIVE_BROWSER_ABORT"
        data["terminal_result"]="PASS_WITH_BROWSER_ABORT"
        data["reported_verdict"]="PASS"
        result=self.check(data)
        self.assertEqual(result["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertTrue(result["network_policy_qualified"])
        self.assertFalse(result["Product_accepted"])

    def test_real_local_bytes_shape_still_not_provider_attestation(self):
        data=copy.deepcopy(self.base)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for a in data["artifacts"]:
                payload=("LOCAL_NONPRODUCT_TEST_BYTES_"+a["name"]).encode()
                (root/a["name"]).write_bytes(payload)
                a["bytes"]=len(payload)
                a["sha256"]=hashlib.sha256(payload).hexdigest()
            data["original"]["custody"]="LOCAL_UNVERIFIED"
            data["original"]["reference"]="LOCAL_NONPRODUCT_TEST_ONLY_NO_PROVIDER_ATTESTATION"
            result=self.v01.evaluate(data,root,data["source"]["commit"],data["source"]["tree"],data["runner"]["native_run_id"])
            self.assertEqual(result["status"],"VALID_SHAPE_UNATTESTED")
            self.assertTrue(result["artifact_bytes_verified_locally"])
            self.assertFalse(result["provider_native_verified"])
            self.assertFalse(result["Product_accepted"])
            one=data["artifacts"][0]["name"]
            (root/one).write_bytes(b"CHANGED")
            corrupt=self.v01.evaluate(data,root)
            self.assertEqual(corrupt["status"],"INVALID_REPORT")

    def test_diagnostic_only_is_not_default_consumer(self):
        strict=subprocess.run([sys.executable,str(V01),str(FIXTURE)],capture_output=True,text=True)
        self.assertNotEqual(strict.returncode,0)
        self.assertEqual(json.loads(strict.stdout)["status"],"INVALID_REPORT")
        diagnostic=subprocess.run([sys.executable,str(V01),str(FIXTURE),"--diagnostic-only"],capture_output=True,text=True)
        self.assertEqual(diagnostic.returncode,0)
        self.assertEqual(json.loads(diagnostic.stdout)["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")

if __name__=="__main__":
    unittest.main()
