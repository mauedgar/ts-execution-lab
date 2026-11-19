import importlib.util
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "receipt_validator.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
BASE = json.loads((ROOT / "fixtures" / "qa_report_v0.example.json").read_text())

class ContractTests(unittest.TestCase):
    def check(self, mutate, expected, reason=None):
        data = copy.deepcopy(BASE)
        mutate(data)
        result = module.evaluate(data)
        self.assertEqual(result["status"], expected, result)
        if reason:
            self.assertIn(reason, result.get("errors", []) + result.get("reasons", []))

    def test_valid_shape_not_native_success(self):
        result = module.evaluate(copy.deepcopy(BASE))
        self.assertEqual(result["status"], "SHAPE_PASS_TEST_VECTOR")

    def test_cannot_claim_other_product_effect(self):
        self.check(lambda x:x.update(product_effect="CONFIRMED"), "INVALID_REPORT", "product_effect_not_none")

    def test_native_commit_binding(self):
        self.check(lambda x:x["runner"].update(head_sha="c"*40), "INVALID_REPORT", "native_head_mismatch")

    def test_missing_viewport(self):
        self.check(lambda x:x["viewports"].pop(), "INVALID_REPORT", "missing_viewport")

    def test_duplicate_viewport(self):
        self.check(lambda x:x["viewports"].append(copy.deepcopy(x["viewports"][0])), "INVALID_REPORT", "duplicate_viewport_320")

    def test_browser_claim_without_build_product(self):
        self.check(lambda x:x["source"].update(subject_kind="PRODUCT_PREVIEW"),
                   "INVALID_REPORT", "product_browser_without_build")

    def test_browser_claim_without_identity(self):
        self.check(lambda x:x["stages"].update(identity="NOT_RUN"),
                   "INVALID_REPORT", "browser_without_identity_and_dependencies")

    def test_outbound_only_observed(self):
        self.check(lambda x:x["network"].update(enforcement="OBSERVE_ONLY"),
                   "INCOMPLETE_OR_BLOCKED", "egress_only_observed")

    def test_network_leak(self):
        self.check(lambda x:x["network"].update(outbound_blocked=0,outbound_escaped=1),
                   "INVALID_REPORT", "browser_pass_with_network_leak")

    def test_service_worker_not_blocked(self):
        self.check(lambda x:x["network"].update(service_workers="NOT_VERIFIED"),
                   "INCOMPLETE_OR_BLOCKED", "service_worker_interception_unverified")

    def test_scenario_not_run(self):
        self.check(lambda x:x["scenarios"].update(keyboard_focus="NOT_RUN"),
                   "INCOMPLETE_OR_BLOCKED", "scenario_not_fully_executed")

    def test_missing_screenshot(self):
        self.check(lambda x:x["artifacts"].pop(0), "INVALID_REPORT", "missing_viewport_screenshot")

    def test_artifact_path_traversal(self):
        self.check(lambda x:x["artifacts"][0].update(name="../../escape.png"),
                   "INVALID_REPORT", "unsafe_artifact_name")

    def test_missing_trace(self):
        self.check(lambda x:x["artifacts"].pop(), "INVALID_REPORT", "no_trace_or_log")

    def test_non_native_custody_does_not_claim_full(self):
        self.check(lambda x:x["original"].update(custody="FAKE_VERIFIED"),
                   "INVALID_REPORT", "bad_custody")

    def test_invalid_json_shape(self):
        self.assertEqual(module.evaluate([])["status"], "INVALID_REPORT")

if __name__ == "__main__":
    unittest.main()
