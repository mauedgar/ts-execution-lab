import importlib.util
import copy
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
SPEC=importlib.util.spec_from_file_location("validator",ROOT/"receipt_validator.py")
module=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(module)
BASE=json.loads((ROOT/"fixtures"/"qa_report_v0.example.json").read_text())

class ContractTests(unittest.TestCase):
    def check(self,change,want,reason=None):
        r=copy.deepcopy(BASE);change(r)
        out=module.evaluate(r)
        self.assertEqual(out["status"],want,out)
        if reason:self.assertIn(reason,out.get("errors",[]))
    def test_vector_stays_non_attesting(self):
        self.assertEqual(module.evaluate(BASE)["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(module.evaluate(BASE)["provider_native_verified"])
    def test_browser_pass_with_reported_fail_rejected(self):
        self.check(lambda r:r.update(reported_verdict="FAIL"),"INVALID_REPORT",
                   "browser_pass_verdict_mismatch")
    def test_browser_fail_without_failure_evidence_rejected(self):
        self.check(lambda r:(r["stages"].update(browser="FAIL"),r.update(reported_verdict="FAIL")),
                   "INVALID_REPORT","browser_fail_without_negative_evidence")
    def test_browser_fail_with_negative_evidence_consistent(self):
        r=copy.deepcopy(BASE)
        r["stages"]["browser"]="FAIL";r["reported_verdict"]="FAIL"
        r["scenarios"]["keyboard_focus"]="FAIL"
        self.assertEqual(module.evaluate(r)["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
    def test_unrun_browser_fail_verdict_rejected(self):
        self.check(lambda r:(r["stages"].update(browser="NOT_RUN"),r.update(reported_verdict="FAIL")),
                   "INVALID_REPORT","unrun_browser_verdict_mismatch")
    def test_network_unbounded_scope_rejected(self):
        self.check(lambda r:r["network"].update(measurement_scope="GLOBAL_OS_EGRESS"),
                   "INVALID_REPORT","network_scope_not_bounded")
    def test_unsupported_os_egress_attestation_rejected(self):
        self.check(lambda r:r["network"].update(os_egress_attested=True),
                   "INVALID_REPORT","unjustified_os_egress_attestation")
    def test_no_browser_binary_digest_rejected(self):
        self.check(lambda r:r["runner"].pop("browser_binary_sha256"),
                   "INVALID_REPORT","missing_browser_binary_sha256")
    def test_invalid_browser_binary_size_rejected(self):
        self.check(lambda r:r["runner"].update(browser_binary_bytes=0),
                   "INVALID_REPORT","missing_browser_binary_bytes")
    def test_shape_only_report_is_rejected_by_strict_consumer_mode(self):
        out=module.evaluate(copy.deepcopy(BASE))
        self.assertEqual(out["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        strict=module.enforce_consumer_requirements(out,require_local_bytes=True)
        self.assertEqual(strict["status"],"INVALID_REPORT")
        self.assertIn("required_local_binary_readback_missing",strict["errors"])
    def test_normal_shape_mode_preserves_historical_contract(self):
        out=module.evaluate(copy.deepcopy(BASE))
        self.assertEqual(module.enforce_consumer_requirements(out,False),out)
    def test_cli_consumer_mode_rejects_realistic_local_test_vector(self):
        import hashlib
        import subprocess
        import sys
        report=copy.deepcopy(BASE)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for item in report["artifacts"]:
                blob=("LOCAL-TEST-VECTOR-"+item["name"]).encode()
                (root/item["name"]).write_bytes(blob)
                item["sha256"]=hashlib.sha256(blob).hexdigest()
                item["bytes"]=len(blob)
            document=root/"report.json"
            document.write_text(json.dumps(report),encoding="utf8")
            proof=module.evaluate(report,artifact_root=root)
            self.assertEqual(proof["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
            self.assertTrue(proof["artifact_bytes_verified_locally"])
            process=subprocess.run([sys.executable,str(ROOT/"receipt_validator.py"),
                       str(document),"--artifact-root",str(root),"--require-local-bytes"],
                       capture_output=True,text=True,check=False)
            self.assertEqual(process.returncode,1,process.stdout+process.stderr)
            result=json.loads(process.stdout)
            self.assertEqual(result["status"],"INVALID_REPORT")
            self.assertIn("test_vector_not_consumer_evidence",result["errors"])
    def test_cli_consumer_bytes_mode_still_requires_native_provider_join(self):
        import hashlib
        import subprocess
        import sys
        report=copy.deepcopy(BASE)
        report["original"]["custody"]="LOCAL_UNVERIFIED"
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for item in report["artifacts"]:
                blob=("LOCAL-SOURCE-RECEIPT-"+item["name"]).encode()
                (root/item["name"]).write_bytes(blob)
                item["sha256"]=hashlib.sha256(blob).hexdigest()
                item["bytes"]=len(blob)
            document=root/"report.json"
            document.write_text(json.dumps(report),encoding="utf8")
            process=subprocess.run([sys.executable,str(ROOT/"receipt_validator.py"),
                       str(document),"--artifact-root",str(root),"--require-local-bytes"],
                       capture_output=True,text=True,check=False)
            self.assertEqual(process.returncode,0,process.stdout+process.stderr)
            result=json.loads(process.stdout)
            self.assertEqual(result["status"],"VALID_SHAPE_UNATTESTED")
            self.assertFalse(result["provider_native_verified"])
            self.assertFalse(result["Product_accepted"])
    def test_fake_provider_custody_not_attested(self):
        r=copy.deepcopy(BASE);r["original"]["custody"]="PROVIDER_NATIVE_READBACK"
        out=module.evaluate(r)
        self.assertEqual(out["status"],"VALID_SHAPE_UNATTESTED")
        self.assertFalse(out["provider_native_verified"])
    def test_unverified_original_custody(self):
        r=copy.deepcopy(BASE);r["original"]["custody"]="LOCAL_UNVERIFIED"
        self.assertEqual(module.evaluate(r)["status"],"VALID_SHAPE_UNATTESTED")
    def test_wrong_product_effect(self):
        self.check(lambda r:r.update(product_effect="CONFIRMED"),"INVALID_REPORT","product_effect_not_none")
    def test_wrong_native_head(self):
        self.check(lambda r:r["runner"].update(head_sha="c"*40),"INVALID_REPORT","native_head_mismatch")
    def test_bad_stages_browser_without_integration(self):
        self.check(lambda r:r["source"].update(subject_kind="PRODUCT_PREVIEW"),"INVALID_REPORT","product_prerequisite_not_pass")
    def test_browser_pass_with_failed_integration(self):
        self.check(lambda r:r["stages"].update(integration="FAIL"),"INVALID_REPORT","failed_integration_followed_by_browser_pass")
    def test_browser_pass_with_failed_build(self):
        self.check(lambda r:r["stages"].update(build="FAIL"),"INVALID_REPORT","failed_build_followed_by_browser_pass")
    def test_browser_pass_without_scenario(self):
        self.check(lambda r:r["scenarios"].update(keyboard_focus="NOT_RUN"),"INVALID_REPORT","browser_pass_missing_scenarios")
    def test_browser_pass_without_all_widths(self):
        self.check(lambda r:r["viewports"][0].update(status="FAIL"),"INVALID_REPORT","browser_pass_missing_viewports")
    def test_missing_viewport(self):
        self.check(lambda r:r["viewports"].pop(),"INVALID_REPORT","missing_viewports")
    def test_duplicate_viewport(self):
        self.check(lambda r:r["viewports"].append(dict(r["viewports"][0])),"INVALID_REPORT","duplicate_viewport_320")
    def test_malformed_width_is_error_not_exception(self):
        self.check(lambda r:r["viewports"].append({"width":[],"status":"PASS"}),"INVALID_REPORT","bad_viewport_width")
    def test_only_observed_external_network(self):
        self.check(lambda r:r["network"].update(enforcement="OBSERVE_ONLY"),"INVALID_REPORT","browser_pass_without_preventive_egress")
    def test_serviceworker_not_blocked(self):
        self.check(lambda r:r["network"].update(service_workers="NOT_VERIFIED"),"INVALID_REPORT","browser_pass_without_serviceworker_block")
    def test_outbound_network_leak(self):
        self.check(lambda r:r["network"].update(outbound_blocked=0,outbound_escaped=1),"INVALID_REPORT","browser_pass_with_outbound_escape")
    def test_inconsistent_egress_counts(self):
        self.check(lambda r:r["network"].update(outbound_attempted=5),"INVALID_REPORT","inconsistent_network_counts")
    def test_artifact_path_traversal(self):
        self.check(lambda r:r["artifacts"][0].update(name="../escape.png"),"INVALID_REPORT","unsafe_artifact_name")
    def test_artifact_duplicate_name(self):
        self.check(lambda r:r["artifacts"].append(dict(r["artifacts"][0])),"INVALID_REPORT","duplicate_artifact_name")
    def test_artifact_invalid_width(self):
        self.check(lambda r:r["artifacts"][0].update(width="320"),"INVALID_REPORT","bad_screenshot_width")
    def test_missing_trace(self):
        self.check(lambda r:r["artifacts"].pop(),"INVALID_REPORT","browser_pass_missing_trace_or_log")
    def test_artifact_bytes_checked(self):
        import hashlib
        r=copy.deepcopy(BASE)
        with tempfile.TemporaryDirectory() as t:
            for a in r["artifacts"]:
                data=("TEST-"+a["name"]).encode()
                (Path(t)/a["name"]).write_bytes(data)
                a["sha256"]=hashlib.sha256(data).hexdigest()
                a["bytes"]=len(data)
            self.assertTrue(module.evaluate(r,artifact_root=t)["artifact_bytes_verified_locally"])
            (Path(t)/r["artifacts"][0]["name"]).write_text("CORRUPTED")
            out=module.evaluate(r,artifact_root=t)
            self.assertEqual(out["status"],"INVALID_REPORT")
            self.assertIn("artifact_size_mismatch_"+r["artifacts"][0]["name"],out["errors"])
    def test_missing_binary_artifact(self):
        with tempfile.TemporaryDirectory() as t:
            out=module.evaluate(BASE,artifact_root=t)
            self.assertEqual(out["status"],"INVALID_REPORT")
    def test_product_notrun_correctly_incomplete(self):
        r=copy.deepcopy(BASE)
        r["source"]["subject_kind"]="PRODUCT_PREVIEW"
        r["stages"]["integration"]="NOT_RUN";r["stages"]["build"]="NOT_RUN";r["stages"]["browser"]="NOT_RUN"
        r["reported_verdict"]="NOT_RUN"
        for s in r["scenarios"]:r["scenarios"][s]="NOT_RUN"
        for row in r["viewports"]:row["status"]="NOT_RUN"
        self.assertEqual(module.evaluate(r)["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")

if __name__=="__main__":unittest.main()
