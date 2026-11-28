"""TS EE 004 IR005 F01/F02 bounded negative regression tests (NONPRODUCT)."""
import copy
import errno
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def load(relative, name):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

producer=load("adapters/q5b_to_common_v01.py","ir005_producer")
validator=load("receipt_validator_v01.py","ir005_validator")
FIXTURE=ROOT/"fixtures"/"qa_report_v01_observe_only.example.json"

class ReferenceBypassGuard(unittest.TestCase):
    def setUp(self):
        self.report=json.loads(FIXTURE.read_text("utf8"))

    def test_reference_drift_without_map_is_rejected(self):
        self.report["original"]["reference"]="ARBITRARY_USER_SELF_REPORTED_REF"
        self.report.pop("scenario_evidence")
        r=validator.evaluate(self.report)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_scenario_evidence_incomplete",r["errors"])

    def test_reference_drift_with_real_mapping_is_still_diagnostic(self):
        self.report["original"]["reference"]="OTHER_NON_NATIVE_REFERENCE"
        r=validator.evaluate(self.report)
        self.assertEqual(r["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")
        self.assertFalse(r["provider_native_verified"])

    def test_reference_drift_with_forged_map_fails(self):
        self.report["original"]["reference"]="FAKE_NOT_A_SOURCE_JOIN"
        self.report["scenario_evidence"]["console_http"]["viewports"][0]["observed"]["http_500"]="NOT_RUN"
        r=validator.evaluate(self.report)
        self.assertEqual(r["status"],"INVALID_REPORT")
        self.assertIn("q5b_evidence_missing_pass_console_http",r["errors"])

    def test_generic_nonchrome_or_not_run_does_not_inherit_q5b_checks(self):
        self.report["stages"]["browser"]="NOT_RUN"
        self.report["functional_browser_status"]="NOT_RUN"
        self.report["network_assurance_status"]="NOT_RUN"
        self.report["terminal_result"]="NOT_RUN"
        self.report["reported_verdict"]="NOT_RUN"
        self.report["scenarios"]={k:"NOT_RUN" for k in self.report["scenarios"]}
        self.report["viewports"]=[{"width":w,"status":"NOT_RUN"} for w in validator.WIDTHS]
        self.report.pop("scenario_evidence")
        r=validator.evaluate(self.report)
        self.assertEqual(r["status"],"VALID_TEST_VECTOR_SHAPE_ONLY")

class QuarantinedPartialOutput(unittest.TestCase):
    def test_complete_output_marker_removed_and_descriptor_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"new"
            fd=None
            with producer.create_only_output(root) as f:
                fd=f
                self.assertTrue((root/"INCOMPLETE_Q5B").exists())
                producer.write_create_only(f,"shot.bin",b"bytes")
            self.assertFalse((root/"INCOMPLETE_Q5B").exists())
            self.assertEqual((root/"shot.bin").read_bytes(),b"bytes")
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_midwrite_oserror_quarantines_and_closes_fd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"partial"
            fd=None
            original=producer.write_create_only
            def injected(directory_fd,name,data):
                if name=="shot.bin":
                    raise OSError(errno.ENOSPC,"injected output failure")
                return original(directory_fd,name,data)
            with patch.object(producer,"write_create_only",side_effect=injected):
                with self.assertRaises(OSError):
                    with producer.create_only_output(root) as f:
                        fd=f
                        producer.write_create_only(f,"shot.bin",b"unwritten")
            self.assertTrue((root/"INCOMPLETE_Q5B").exists())
            self.assertFalse((root/"COMMON_RECEIPT_V01.json").exists())
            with self.assertRaises(OSError):
                os.fstat(fd)
            with self.assertRaises(FileExistsError):
                with producer.create_only_output(root):
                    pass

    def test_collision_failure_is_quarantined_and_retains_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"partial"
            with self.assertRaises(FileExistsError):
                with producer.create_only_output(root) as fd:
                    producer.write_create_only(fd,"shot.bin",b"original")
                    producer.write_create_only(fd,"shot.bin",b"overwrite")
            self.assertEqual((root/"shot.bin").read_bytes(),b"original")
            self.assertTrue((root/"INCOMPLETE_Q5B").exists())

    def test_validator_rejects_partial_even_with_valid_test_vector_artifacts(self):
        report=json.loads(FIXTURE.read_text("utf8"))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"partial"
            root.mkdir()
            (root/"INCOMPLETE_Q5B").write_text("partial",encoding="ascii")
            result=validator.evaluate(report,artifact_root=root)
            self.assertEqual(result["status"],"INVALID_REPORT")
            self.assertIn("incomplete_producer_output",result["errors"])
            self.assertFalse(result["artifact_bytes_verified_locally"])

if __name__=="__main__":
    unittest.main()
