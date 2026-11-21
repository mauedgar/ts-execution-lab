import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v01_q5b",ROOT/"receipt_validator_v01.py")
v01=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v01)

class LocalFixtureOnlyCounts(unittest.TestCase):
    def setUp(self):
        self.report=json.loads((ROOT/"fixtures"/"qa_report_v01_observe_only.example.json").read_text("utf8"))
        self.report["network"]["measurement_scope"]="LOCAL_FIXTURE_SERVER_ONLY"
        self.report["network"]["outbound_attempted"]=None
        self.report["network"]["outbound_blocked"]=None
        self.report["network"]["outbound_escaped"]=None

    def test_unmeasured_is_explicit_and_not_preventive(self):
        r=v01.evaluate(self.report)
        self.assertEqual(r["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(r["network_policy_qualified"])
        self.assertFalse(r["network_metrics_measured"])
        self.assertEqual(r["terminal_result"],"PASS_FUNCTIONAL_ONLY")
        self.assertFalse(r["Product_accepted"])

    def test_missing_real_network_measurement_cannot_claim_prevention(self):
        cases=[
          (lambda d:d["network"].update(enforcement="PREVENTIVE_BROWSER_ABORT"),"fixture_scope_cannot_claim_prevention"),
          (lambda d:d["network"].update(service_workers="BLOCKED"),"fixture_scope_cannot_claim_sw_block"),
          (lambda d:d["network"].update(outbound_attempted=0),"unmeasured_network_count_must_be_null_outbound_attempted"),
          (lambda d:d["network"].update(outbound_blocked=0),"unmeasured_network_count_must_be_null_outbound_blocked"),
          (lambda d:d["network"].update(outbound_escaped=0),"unmeasured_network_count_must_be_null_outbound_escaped"),
          (lambda d:d.update(network_assurance_status="PREVENTIVE_BROWSER_ABORT"),"observe_only_assurance_mismatch"),
          (lambda d:d.update(reported_verdict="PASS"),"browser_pass_verdict_mismatch")
        ]
        for fn,code in cases:
            with self.subTest(code=code):
                report=copy.deepcopy(self.report)
                fn(report)
                r=v01.evaluate(report)
                self.assertEqual(r["status"],"INVALID_REPORT")
                self.assertIn(code,r["errors"])

if __name__=="__main__":unittest.main()
