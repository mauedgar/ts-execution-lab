"""Source-only fixtures, not browser/native evidence."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import generic_browser_consumer as g

def raw(x): return (json.dumps(x,sort_keys=True)+"\n").encode()
def sha(x): return hashlib.sha256(x).hexdigest()

class GenericJoin(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.r=json.loads((ROOT/"fixtures/qa_report_v01_observe_only.example.json").read_text())
        self.r.pop("scenario_evidence",None)
        self.r["runner"]["native_run_id"]="999999999"
        self.r["attempt"]="TS-EE-GENERIC-TEST-ONLY-A001"
        self.c={"schema":"ts-ee/generic-browser-consumer-contract/v1","profile":"GENERIC_BROWSER_V01",
                "source":copy.deepcopy(self.r["source"]),"attempt":self.r["attempt"],"run_id":"999999999",
                "run_attempt":1,"engine":"CHROMEDRIVER_NODE","log_name":"generic.json",
                "checks":{s:{"375":["assert_"+s]} for s in g.common.SCENARIOS}}
        self.c["checks"]["viewport"]={str(w):["width","no_overflow"] for w in g.common.WIDTHS}
        self.e={"schema":"ts-ee/generic-browser-evidence/v1","contract_sha256":sha(raw(self.c)),
                **{k:copy.deepcopy(self.c[k]) for k in ("source","attempt","run_id","run_attempt","engine")},
                "observed":{s:{w:{k:"PASS" for k in checks} for w,checks in rows.items()}
                            for s,rows in self.c["checks"].items()}}
        self.r["artifacts"]=[]
        for w in g.common.WIDTHS:
            b=("synthetic test bytes "+str(w)).encode()
            name="shot-"+str(w)+".png"
            (self.root/name).write_bytes(b)
            self.r["artifacts"].append({"name":name,"kind":"SCREENSHOT","width":w,"bytes":len(b),"sha256":sha(b)})
        self.bind_log(raw(self.e))
    def bind_log(self,b):
        (self.root/"generic.json").write_bytes(b)
        self.r["artifacts"]=[a for a in self.r["artifacts"] if a["name"]!="generic.json"]
        self.r["artifacts"].append({"name":"generic.json","kind":"LOG","bytes":len(b),"sha256":sha(b)})
        self.r["original"]={"custody":"LOCAL_UNVERIFIED","reference":"generic.json","bytes":len(b),"sha256":sha(b)}
    def check(self):
        return g.verify(self.r,raw(self.c),sha(raw(self.c)),self.root)
    def reject(self,reason):
        with self.assertRaisesRegex(ValueError,reason): self.check()
    def test_positive_local_only(self):
        v=self.check()
        self.assertEqual(v["status"],"VALID_GENERIC_MAPPING_UNATTESTED")
        self.assertFalse(v["provider_native_verified"])
        self.assertFalse(v["Product_accepted"])
        self.assertEqual(v["terminal_result"],"PASS_FUNCTIONAL_ONLY")
    def test_contract_hash(self):
        with self.assertRaisesRegex(ValueError,"CONTRACT_HASH_MISMATCH"):
            g.verify(self.r,raw(self.c),"0"*64,self.root)
    def test_wrong_repository(self):
        self.r["source"]["repository"]="other/repo"
        self.reject("SUBJECT_MISMATCH")
    def test_wrong_attempt(self):
        self.r["attempt"]="TS-EE-WRONG-ATTEMPT"
        self.reject("SUBJECT_MISMATCH")
    def test_wrong_run_attempt(self):
        self.r["runner"]["attempt_number"]=True
        self.reject("RUN_MISMATCH")
    def test_wrong_profile(self):
        self.c["profile"]="Q5B_SYNTHETIC_LOCAL_V01"
        self.reject("CONTRACT_PROFILE")
    def test_missing_scenario(self):
        self.e["observed"].pop("history")
        self.bind_log(raw(self.e))
        self.reject("LOG_SCENARIOS")
    def test_wrong_width(self):
        self.e["observed"]["keyboard_focus"]={"320":{"assert_keyboard_focus":"PASS"}}
        self.bind_log(raw(self.e))
        self.reject("LOG_WIDTHS_keyboard_focus")
    def test_missing_check(self):
        self.e["observed"]["viewport"]["320"].pop("width")
        self.bind_log(raw(self.e))
        self.reject("LOG_CHECKS_viewport_320")
    def test_actual_fail(self):
        self.e["observed"]["routing"]["375"]["assert_routing"]="FAIL"
        self.bind_log(raw(self.e))
        self.reject("LOG_NONPASS_routing_375")
    def test_fake_original(self):
        self.r["original"]["custody"]="TEST_VECTOR"
        self.reject("ORIGINAL_CUSTODY_OR_REFERENCE")
    def test_original_hash_mismatch(self):
        self.r["original"]["sha256"]="0"*64
        self.reject("ORIGINAL_LOG_BYTES")
    def test_duplicate_json_key(self):
        b=raw(self.e).replace(b'{"attempt":',b'{"schema":"fake","attempt":',1)
        self.bind_log(b)
        self.reject("DUPLICATE_JSON_KEY")
    def test_incomplete_producer(self):
        (self.root/"INCOMPLETE_Q5B").write_text("incomplete")
        self.reject("COMMON_STRICT_REJECT")
    def test_missing_screenshot(self):
        (self.root/"shot-320.png").unlink()
        self.reject("COMMON_STRICT_REJECT")
    def test_report_self_claim_not_enough(self):
        self.r["artifacts"]=[a for a in self.r["artifacts"] if a["kind"]!="LOG"]
        self.reject("ORIGINAL_LOG_REQUIRED")

if __name__=="__main__": unittest.main()
