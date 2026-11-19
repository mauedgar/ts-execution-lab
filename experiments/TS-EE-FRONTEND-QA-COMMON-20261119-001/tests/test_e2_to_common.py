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
                         deep_refresh=True,first_tab="Catalog",hidden_rejected=True,
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
                runtime={"playwright":"1.57.0"},
                variants={"good":{"pass":True,"detected":[],"rows":rows},
                          "bad":{"pass":True,"detected":["CONSOLE","HIDDEN_SKU","HTTP","LABEL","OVERFLOW"],
                                 "rows":injected}},
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
            with self.assertRaisesRegex(ValueError,"MISSING_E2_ARTIFACT"):bridge(r,Path(d))
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
    def test_local_artifact_sha_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r=make(Path(d));r["artifacts"][0]["sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"CORRUPTED_E2_ARTIFACT"):bridge(r,Path(d))
if __name__=="__main__":unittest.main()
