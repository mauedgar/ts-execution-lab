"""IR006-F01: producer identity is caller-bound, not a mutable JSON selector.
NONPRODUCT shape/local-only test vectors; no provider/native execution.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ee004_ir006",ROOT/"receipt_validator_v01.py")
validator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
FIXTURE=ROOT/"fixtures"/"qa_report_v01_observe_only.example.json"

class TrustedConsumerIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads(FIXTURE.read_text("utf8"))
        cls.pins=(cls.original["source"]["commit"],cls.original["source"]["tree"],
                  cls.original["runner"]["native_run_id"],
                  "CHROMEDRIVER_NODE","SYNTHETIC","Q5B_SYNTHETIC_LOCAL_V01")

    def as_real(self):
        x=copy.deepcopy(self.original)
        x["original"]["custody"]="LOCAL_UNVERIFIED"
        x["original"]["reference"]="UNTRUSTED_PRODUCER_METADATA_ONLY"
        return x

    def check(self,report,*pins):
        return validator.evaluate(report,None,*pins)

    def test_real_without_external_identity_fails_closed(self):
        r=self.check(self.as_real())
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("missing_or_invalid_expected_engine",r["errors"])
        self.assertIn("missing_or_invalid_expected_subject_kind",r["errors"])
        self.assertIn("missing_or_invalid_expected_evidence_profile",r["errors"])

    def test_real_explicitly_pinned_shape_is_not_provider_attestation(self):
        r=self.check(self.as_real(),*self.pins)
        self.assertEqual(r["status"],"VALID_SHAPE_UNATTESTED")
        self.assertFalse(r["provider_native_verified"])
        self.assertFalse(r["artifact_bytes_verified_locally"])

    def test_engine_spoof_playwright_and_missing_q5b_map_fails(self):
        x=self.as_real()
        x["runner"]["engine"]="PLAYWRIGHT_PYTHON"
        x.pop("scenario_evidence")
        r=self.check(x,*self.pins)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("external_engine_mismatch",r["errors"])
        self.assertIn("q5b_scenario_evidence_incomplete",r["errors"])

    def test_subject_spoof_product_preview_and_missing_q5b_map_fails(self):
        x=self.as_real()
        x["source"]["subject_kind"]="PRODUCT_PREVIEW"
        x["stages"]["integration"]="PASS"
        x["stages"]["build"]="PASS"
        x.pop("scenario_evidence")
        r=self.check(x,*self.pins)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("external_subject_kind_mismatch",r["errors"])
        self.assertIn("q5b_scenario_evidence_incomplete",r["errors"])

    def test_change_both_engine_and_subject_does_not_escape(self):
        x=self.as_real()
        x["runner"]["engine"]="PLAYWRIGHT_PYTHON"
        x["source"]["subject_kind"]="PRODUCT_PREVIEW"
        x["stages"]["integration"]="PASS"
        x["stages"]["build"]="PASS"
        x.pop("scenario_evidence")
        r=self.check(x,*self.pins)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_scenario_evidence_incomplete",r["errors"])

    def test_q5b_profile_requires_expected_head_tree_and_run(self):
        x=self.as_real()
        for index in (0,1,2):
            with self.subTest(missing=index):
                pins=list(self.pins)
                pins[index]=None
                r=self.check(x,*pins)
                self.assertEqual(r["status"],"INVALID_REPORT")
                self.assertIn("q5b_provider_identity_not_pinned",r["errors"])

    def test_incorrect_external_profile_for_expected_q5b_fails(self):
        x=self.as_real()
        pins=list(self.pins)
        pins[4]="PRODUCT_PREVIEW"
        r=self.check(x,*pins)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_external_profile_configuration_mismatch",r["errors"])

    def test_legitimate_generic_playwright_does_not_inherit_q5b_mapping(self):
        x=self.as_real()
        x["runner"]["engine"]="PLAYWRIGHT_PYTHON"
        x.pop("scenario_evidence")
        pins=(x["source"]["commit"],x["source"]["tree"],
              x["runner"]["native_run_id"],
              "PLAYWRIGHT_PYTHON","SYNTHETIC","GENERIC_BROWSER_V01")
        r=self.check(x,*pins)
        self.assertEqual(r["status"],"VALID_SHAPE_UNATTESTED")
        self.assertFalse(r["provider_native_verified"])
        self.assertFalse(r["Product_accepted"])

    def test_strict_cli_without_identity_is_denied_even_with_report(self):
        x=self.as_real()
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"report.json"
            path.write_text(json.dumps(x),encoding="utf8")
            run=subprocess.run([sys.executable,str(ROOT/"receipt_validator_v01.py"),str(path)],
                               capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            self.assertIn("missing_or_invalid_expected_engine",json.loads(run.stdout)["errors"])

    def test_diagnostic_vector_still_never_consumer_attested(self):
        r=self.check(copy.deepcopy(self.original))
        self.assertEqual(r["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(r["provider_native_verified"])

if __name__=="__main__": unittest.main()
