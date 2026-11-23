"""NONPRODUCT TS EE 004 negative source tests for Q5B F02/F03, Linux-specific."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v01=load(ROOT/"receipt_validator_v01.py","ee004_v01")
producer=load(ROOT/"adapters"/"q5b_to_common_v01.py","ee004_producer")
FIXTURE=ROOT/"fixtures"/"qa_report_v01_observe_only.example.json"

class Q5BScenarioEvidence(unittest.TestCase):
    def setUp(self):
        self.report=json.loads(FIXTURE.read_text(encoding="utf8"))
        self.report["original"]["reference"]="LOCAL_NONPRODUCT_Q5B_ACTUAL_JSON_AND_TOOLCHAIN_BYTES"
        if "SYNTHETIC_LOCAL_FIXTURE_ONLY" not in self.report["limitations"]:
            self.report["limitations"].append("SYNTHETIC_LOCAL_FIXTURE_ONLY")
        self.report["scenario_evidence"]={
            name:{
                "scope":"SYNTHETIC_LOCAL_FIXTURE_ONLY",
                "checks":list(checks),
                "viewports":[{"width":width,"observed":{check:"PASS" for check in checks}}
                             for width in v01.WIDTHS]
            } for name,checks in producer.SCENARIO_CHECKS.items()
        }
        self.assertEqual(set(producer.SCENARIO_CHECKS),set(v01.Q5B_SCENARIO_CHECKS))
        self.assertEqual(producer.SCENARIO_CHECKS,v01.Q5B_SCENARIO_CHECKS)

    def test_fixture_map_has_a_narrow_valid_diagnostic_shape(self):
        r=v01.evaluate(self.report)
        self.assertEqual(r["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(r["Product_accepted"])
        self.assertFalse(r["provider_native_verified"])

    def test_absent_map_is_rejected_for_actual_q5b_reference(self):
        del self.report["scenario_evidence"]
        r=v01.evaluate(self.report)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_scenario_evidence_incomplete",r["errors"])

    def test_missing_console_http_and_a11y_specific_checks_are_rejected(self):
        cases=[
            ("console_http","http_500"),
            ("console_http","seeded_js_error"),
            ("a11y_basic","semantic_heading"),
            ("a11y_basic","keyboard_tab"),
            ("history","history_back"),
        ]
        for scenario,check in cases:
            with self.subTest(scenario=scenario,check=check):
                data=copy.deepcopy(self.report)
                data["scenario_evidence"][scenario]["viewports"][0]["observed"][check]="NOT_RUN"
                r=v01.evaluate(data)
                self.assertEqual(r["status"],"INVALID_REPORT")
                self.assertIn("q5b_evidence_missing_pass_"+scenario,r["errors"])

    def test_no_general_browser_or_wcag_claim(self):
        data=copy.deepcopy(self.report)
        data["scenario_evidence"]["console_http"]["scope"]="GENERAL_CONSOLE_TELEMETRY"
        r=v01.evaluate(data)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_evidence_scope_console_http",r["errors"])
        data=copy.deepcopy(self.report)
        data["limitations"].remove("SYNTHETIC_LOCAL_FIXTURE_ONLY")
        r=v01.evaluate(data)
        self.assertIn("q5b_fixture_scope_limit_missing",r["errors"])

    def test_wrong_viewport_identity_rejected(self):
        self.report["scenario_evidence"]["routing"]["viewports"][1]["width"]=320
        r=v01.evaluate(self.report)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_evidence_width_order_routing",r["errors"])

class DescriptorSecurity(unittest.TestCase):
    def test_intermediate_symlink_rejected_by_both_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            real=root/"real"
            real.mkdir()
            (real/"payload").write_bytes(b"actual")
            (root/"alias").symlink_to(real,target_is_directory=True)
            with self.assertRaises((OSError,ValueError)):
                producer.read_file(root/"alias"/"payload")
            with self.assertRaises((OSError,ValueError)):
                v01.secure_directory_fd(root/"alias")

    def test_symlink_leaf_and_special_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"real").write_bytes(b"file")
            (root/"alias").symlink_to(root/"real")
            with self.assertRaises((OSError,ValueError)):
                producer.read_file(root/"alias")
            fd=v01.secure_directory_fd(root)
            try:
                with self.assertRaises((OSError,ValueError)):
                    v01.secure_read_artifact(fd,"alias")
                with self.assertRaises((OSError,ValueError)):
                    v01.secure_read_artifact(fd,".")
            finally:
                os.close(fd)

    def test_create_only_output_dir_and_file_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            fd=producer.create_output_directory(root/"new")
            try:
                producer.write_create_only(fd,"result.json",b"first")
                with self.assertRaises(FileExistsError):
                    producer.write_create_only(fd,"result.json",b"overwritten")
                (root/"new"/"link").symlink_to(root/"new"/"result.json")
                with self.assertRaises(FileExistsError):
                    producer.write_create_only(fd,"link",b"overwritten")
                self.assertEqual((root/"new"/"result.json").read_bytes(),b"first")
            finally:
                os.close(fd)
            with self.assertRaises(FileExistsError):
                producer.create_output_directory(root/"new")

    def test_local_bytes_validator_rejects_symlink_parent(self):
        report=json.loads(FIXTURE.read_text(encoding="utf8"))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            actual=root/"actual"
            actual.mkdir()
            for artifact in report["artifacts"]:
                raw=("F02F03_TEST_"+artifact["name"]).encode("ascii")
                (actual/artifact["name"]).write_bytes(raw)
                artifact["bytes"]=len(raw)
                artifact["sha256"]=hashlib.sha256(raw).hexdigest()
            report["original"]["custody"]="LOCAL_UNVERIFIED"
            report["original"]["reference"]="EE004_TEST_FIXTURE_NOT_Q5B"
            good=v01.evaluate(report,actual)
            self.assertEqual(good["status"],"VALID_SHAPE_UNATTESTED")
            link=root/"alias"
            link.symlink_to(actual,target_is_directory=True)
            bad=v01.evaluate(report,link)
            self.assertEqual(bad["status"],"INVALID_REPORT")
            self.assertIn("unsafe_artifact_root",bad["errors"])
            (actual/report["artifacts"][0]["name"]).write_bytes(b"tampered")
            bad=v01.evaluate(report,actual)
            self.assertEqual(bad["status"],"INVALID_REPORT")

if __name__=="__main__":
    unittest.main()
