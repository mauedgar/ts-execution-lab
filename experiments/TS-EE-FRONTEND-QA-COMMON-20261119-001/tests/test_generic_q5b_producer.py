"""Source-only synthetic bytes; no browser or prior native artifact replay."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import generic_q5b_producer as p
from adapters import q5b_to_common_v01 as q

class Projection(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.raw=self.root/"raw";self.raw.mkdir()
        self.common=self.root/"common";self.out=self.root/"generic"
        self.c={"schema":"ts-ee/generic-browser-consumer-contract/v1","profile":"GENERIC_BROWSER_V01",
                "source":{"repository":"mauedgar/ts-execution-lab","commit":"a"*40,"tree":"b"*40,
                          "subject_kind":"SYNTHETIC"},
                "attempt":"TS-EE-GENERIC-PROJECTION-TEST-A001","run_id":"99999999","run_attempt":1,
                "engine":"CHROMEDRIVER_NODE","log_name":p.LOG,
                "checks":{s:{str(w):list(checks) for w in q.WIDTHS}
                          for s,checks in q.SCENARIO_CHECKS.items()}}
        t={"schema":"ts-ee/q5b/toolchain-local/v0","runner_os":"ubuntu-24.04",
           "provider_native_verified":False,"product_accepted":False,
           "chrome":{"version":"synthetic chrome","sha256":"c"*64,"bytes":123},
           "driver":{"version":"synthetic driver","sha256":"d"*64,"bytes":456}}
        (self.raw/"TOOLCHAIN.json").write_bytes(p.encode(t))
        for w in q.WIDTHS:
            path=self.raw/str(w);path.mkdir()
            name="q5b-"+str(w)+".png"
            png=bytes.fromhex("89504e470d0a1a0a")+("TEST ONLY "+str(w)).encode()*30
            (path/name).write_bytes(png)
            r={"schema":"ts-ee/chromedriver-browser-q5b/v0","subject":"NONPRODUCT_SYNTHETIC",
               "engine":"CHROMEDRIVER_NODE","overall":"PASS_BOUNDED_Q5B_BROWSER","error_class":"NONE",
               "requested_viewport_width":w,"observed_viewport_width":w,
               "network_mode":"OBSERVE_ONLY","os_egress_attested":False,
               "provider_native_verified":False,"product_accepted":False,
               "remote_session_state":"DELETED_CONFIRMED","session_delete":"ACK",
               "driver_termination":"DIRECT_PROCESS_EXIT_OBSERVED","descendant_termination":"NOT_ATTESTED",
               "server_close":"CLOSED","profile_cleanup":"PASS",
               "stage":{k:"PASS" for k in ("identity","server","driver","session","browser","cleanup")},
               "checks":{k:"PASS" for k in q.CHECKS},
               "local_http_events":{k:1 for k in ("home","product","deniedSku","notFound","serverError","scriptError")},
               "screenshot":{"filename":name,"width":w,"bytes":len(png),"sha256":p.g.digest(png)},
               "session_create_ms":12}
            (path/"Q5B_REPORT.json").write_bytes(p.encode(r))
        args=["q5b","--evidence-root",str(self.raw),"--output-root",str(self.common),
              "--repository",self.c["source"]["repository"],"--commit","a"*40,"--tree","b"*40,
              "--run-id",self.c["run_id"],"--run-attempt","1","--attempt",self.c["attempt"]]
        with patch.object(sys,"argv",args),contextlib.redirect_stdout(io.StringIO()):
            q.main()
    def project(self,pin=None):
        raw=p.encode(self.c)
        return p.project(self.raw,self.common,self.out,raw,pin or p.g.digest(raw))
    def rejected(self,reason):
        with self.assertRaisesRegex(ValueError,reason):self.project()
        self.assertFalse(self.out.exists())
    def mutate(self,path,change):
        obj=json.loads(path.read_bytes());change(obj);path.write_bytes(p.encode(obj))
    def test_project_and_consume(self):
        r=self.project();raw=p.encode(self.c)
        v=p.g.verify(r,raw,p.g.digest(raw),self.out)
        self.assertEqual(v["status"],"VALID_GENERIC_MAPPING_UNATTESTED")
        self.assertEqual(v["terminal_result"],"PASS_FUNCTIONAL_ONLY")
        self.assertFalse(v["provider_native_verified"])
        self.assertFalse(v["Product_accepted"])
        self.assertEqual(set(x.name for x in self.out.iterdir()),
                         {p.LOG,p.RECEIPT,*("shot-"+str(w)+".png" for w in q.WIDTHS)})
        before={x.name:x.read_bytes() for x in self.out.iterdir()}
        with self.assertRaises(FileExistsError):self.project()
        self.assertEqual(before,{x.name:x.read_bytes() for x in self.out.iterdir()})
    def test_wrong_contract_hash(self):
        with self.assertRaisesRegex(ValueError,"CONTRACT_HASH_MISMATCH"):self.project("0"*64)
        self.assertFalse(self.out.exists())
    def test_wrong_run(self):
        self.c["run_id"]="99999998";self.rejected("Q5B_RUN_MISMATCH")
    def test_missing_width(self):
        self.c["checks"]["history"].pop("320");self.rejected("BOUNDED_CALLER_POLICY")
    def test_wrong_policy(self):
        self.c["source"]["subject_kind"]="PRODUCT_PREVIEW";self.rejected("BOUNDED_CALLER_POLICY")
    def test_raw_tamper(self):
        self.mutate(self.raw/"320"/"Q5B_REPORT.json",lambda r:r.update(session_create_ms=13))
        self.rejected("Q5B_ORIGINAL_BYTES_JOIN")
    def test_raw_fail(self):
        self.mutate(self.raw/"320"/"Q5B_REPORT.json",lambda r:r["checks"].update(keyboard_tab="FAIL"))
        self.rejected("Q5B_CHECK_NOT_PASS")
    def test_toolchain_tamper(self):
        self.mutate(self.raw/"TOOLCHAIN.json",lambda r:r["chrome"].update(version="changed"))
        self.rejected("Q5B_TOOLCHAIN_JOIN")
    def test_incomplete_common(self):
        (self.common/"INCOMPLETE_Q5B").write_text("synthetic");self.rejected("Q5B_COMMON_REJECT")
    def test_source_duplicate(self):
        path=self.raw/"320"/"Q5B_REPORT.json"
        raw=path.read_bytes();path.write_bytes(raw.replace(b'{',b'{"engine":"CHROMEDRIVER_NODE",',1))
        self.rejected("DUPLICATE_JSON_KEY")
if __name__=="__main__":
    unittest.main()
