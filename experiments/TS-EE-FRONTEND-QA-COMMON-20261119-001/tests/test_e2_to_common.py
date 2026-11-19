import importlib.util
import hashlib
import copy
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
SPEC=importlib.util.spec_from_file_location("bridge",ROOT/"adapters"/"e2_to_common.py")
module=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(module)

def make(root):
    rows=[]
    for w in (320,375,768,1440):
        rows.append(dict(width=w,overflow_px=0,label=True,detail=True,back=True,forward=True,
                         deep_refresh=True,first_tab="Catalog",keyboard_activated=True,
                         keyboard_negative_rejected=True,external_navigation_rejected=True,
                         hidden_rejected=True,
                         console_errors=0,http_errors=0,blocked_external=1))
    injected=[dict(r,overflow_px=15 if r["width"]==320 else 0,
                   label=False,hidden_rejected=False,console_errors=1,http_errors=1)
              for r in rows]
    artifacts=[]
    for name in ("good","bad"):
        for w in (320,375,768,1440):
            for ext in ("png","zip"):
                p=root/(name+"-"+str(w)+"."+ext)
                data=(name+str(w)+ext).encode()
                p.write_bytes(data)
                artifacts.append(dict(file=p.name,sha256=hashlib.sha256(data).hexdigest(),
                                      bytes=len(data)))
    return dict(schema="ts-ee-e2-browser-qa/v1",pass_=True,
                source_sha256="a"*64,widths=[320,375,768,1440],service_workers="BLOCKED",
                runtime={"playwright":"1.57.0","chromium":"136.0.test",
                         "chromium_executable_sha256":"a"*64,
                         "chromium_executable_bytes":12400000},
                variants={"good":{"pass":True,"detected":[],"rows":rows,"blocked_external_requests":4},
                          "bad":{"pass":True,"detected":["CONSOLE","HIDDEN_SKU","HTTP","LABEL","OVERFLOW"],
                                 "rows":injected,"blocked_external_requests":4}},
                artifacts=artifacts)
def bridge(r,root):
    r["pass"]=r.pop("pass_")
    return module.convert(r,repository="mauedgar/ts-execution-lab",commit="a"*40,
                          tree="b"*40,run_id="SYNTHETIC_ONLY",attempt="TS-EE-FEQA-CONVERTER-A001",
                          script_hash="a"*64,original_sha="f"*64,original_bytes=200,
                          evidence_root=root)

class BridgeTests(unittest.TestCase):
    def test_source_receipt_to_common_format(self):
        with tempfile.TemporaryDirectory() as d:
            common=bridge(make(Path(d)),Path(d))
            self.assertEqual(common["schema"],"ts-ee/frontend-browser-qa/v0")
            self.assertEqual(len(common["scenarios"]),8)
            self.assertEqual(len(common["artifacts"]),16)
            self.assertEqual(common["original"]["custody"],"LOCAL_UNVERIFIED")
    def test_missing_screenshot_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));(Path(d)/"good-320.png").unlink()
            with self.assertRaisesRegex(ValueError,"UNSAFE_EVIDENCE_OPEN"):bridge(r,Path(d))
    def test_bad_control_must_match_known_injection(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["bad"]["detected"]=[]
            with self.assertRaisesRegex(ValueError,"CONTROL_bad"):bridge(r,Path(d))
    def test_script_sha_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["source_sha256"]="b"*64
            with self.assertRaisesRegex(ValueError,"SCRIPT_HASH"):bridge(r,Path(d))
    def test_missing_keyboard_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]["first_tab"]="other"
            with self.assertRaisesRegex(ValueError,"SCENARIOS_keyboard_focus"):bridge(r,Path(d))
    def test_enter_activation_missing_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]["keyboard_activated"]=False
            with self.assertRaisesRegex(ValueError,"SCENARIOS_keyboard_focus"):bridge(r,Path(d))
    def test_disabled_enter_negative_control_missing_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["bad"]["rows"][0]["keyboard_negative_rejected"]=False
            with self.assertRaisesRegex(ValueError,"SCENARIOS_keyboard_focus"):bridge(r,Path(d))
    def test_egress_route_success_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]["external_navigation_rejected"]=False
            with self.assertRaisesRegex(ValueError,"OBSERVED_EGRESS_ROUTE_RESULT"):bridge(r,Path(d))
    def test_malformed_root_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_ROOT"):
                module.convert([],repository="owner/repo",commit="a"*40,tree="b"*40,
                               run_id="X",attempt="A",script_hash="a"*64,original_sha="f"*64,
                               original_bytes=1,evidence_root=Path(d))
    def test_malformed_nested_row_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]=None
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_ROWS_good"):bridge(r,Path(d))
    def test_egress_total_tampering_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["blocked_external_requests"]=99
            with self.assertRaisesRegex(ValueError,"EGRESS_TOTAL_MISMATCH_good"):bridge(r,Path(d))
    def test_malformed_runtime_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["runtime"]=None
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_RUNTIME_OR_WIDTHS"):bridge(r,Path(d))
    def test_malformed_width_inventory_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["widths"]=None
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_RUNTIME_OR_WIDTHS"):bridge(r,Path(d))
    def test_wrong_type_outbound_counter_rejected_directly(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]["blocked_external"]="1"
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_COUNTER_good_blocked_external"):
                bridge(r,Path(d))
    def test_mixed_viewport_types_rejected_without_typeerror(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["widths"]=[320,375,None,1440]
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_VIEWPORT_TYPE"):
                bridge(r,Path(d))
    def test_missing_chromium_binary_identity_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["runtime"].pop("chromium_executable_sha256")
            with self.assertRaisesRegex(ValueError,"CHROMIUM_BINARY_IDENTITY"):
                bridge(r,Path(d))
    def test_symlinked_artifact_rejected_by_fd_open(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);r=make(root);p=root/"good-320.png";replacement=root/"real-file"
            p.rename(replacement);p.symlink_to(replacement)
            with self.assertRaisesRegex(ValueError,"UNSAFE_EVIDENCE_OPEN"):
                bridge(r,root)
    def test_bad_binary_bytes_type_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["artifacts"][0]["bytes"]="7"
            with self.assertRaisesRegex(ValueError,"ARTIFACT_LENGTH"):
                bridge(r,Path(d))
    def test_malformed_bool_flag_rejected_directly(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["variants"]["good"]["rows"][0]["keyboard_activated"]=None
            with self.assertRaisesRegex(ValueError,"MALFORMED_E2_FLAG_good_keyboard_activated"):
                bridge(r,Path(d))
    def test_local_artifact_sha_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["artifacts"][0]["sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"CORRUPTED_E2_ARTIFACT"):bridge(r,Path(d))
if __name__=="__main__":unittest.main()
