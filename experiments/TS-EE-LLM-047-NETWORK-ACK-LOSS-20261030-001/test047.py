#!/usr/bin/env python3
"""Independent real-TCP-ACK-drop subprocess test, seven prospective cases."""
import json, os, pathlib, sqlite3, subprocess, sys, time, unittest

ROOT=pathlib.Path(os.environ["LAB047_ROOT"]).resolve()
PROVIDER=pathlib.Path(os.environ["LAB047_PROVIDER"]).resolve()
CLIENT=pathlib.Path(os.environ["LAB047_CLIENT"]).resolve()
RESULT=pathlib.Path(os.environ["LAB047_RESULT"]).resolve()

class Test047(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ROOT.mkdir(parents=True,exist_ok=False)
    def setUp(self):
        self.root=ROOT/self._testMethodName;self.root.mkdir()
        self.db=self.root/"provider.sqlite3"
        self.journal=self.root/"consumer.sqlite3"
        self.ident={"attempt":self._testMethodName,"subject":"frozen047@synthetic","owner":"TS_EE_047"}
        self.server=None;self.server_log=None;self.port=None
        self.start_provider()
    def tearDown(self):
        self.stop_provider()
        for p in (self.db,self.journal):
            if p.exists():
                c=sqlite3.connect(p)
                self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                c.close()
    def start_provider(self):
        ready=self.root/"provider-ready.json"
        if ready.exists():ready.unlink()
        self.server_log=open(self.root/"provider-original.log","a",encoding="utf8")
        self.server=subprocess.Popen([sys.executable,str(PROVIDER),"--db",str(self.db),"--ready",str(ready)],
                stdout=self.server_log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+5
        while not ready.exists():
            if self.server.poll() is not None:raise AssertionError("PROVIDER_EXITED_EARLY")
            if time.monotonic()>deadline:raise AssertionError("PROVIDER_START_TIMEOUT")
            time.sleep(.02)
        self.port=json.loads(ready.read_text())["port"]
        self.url="http://127.0.0.1:"+str(self.port)
    def stop_provider(self):
        if self.server is None:return
        if self.server.poll() is None:
            self.server.terminate()
            try:self.server.wait(timeout=3)
            except subprocess.TimeoutExpired:self.server.kill();self.server.wait(timeout=3)
        self.server_log.close()
        self.server=None
    def client(self,command,*,fault="none",discard=False,owner=None,journal=None,expect=0):
        args=[sys.executable,str(CLIENT),command,"--journal",str(journal or self.journal),
              "--url",self.url,"--attempt",self.ident["attempt"],
              "--subject",self.ident["subject"],"--owner",owner or self.ident["owner"]]
        if command=="dispatch":args+=["--fault",fault]
        if discard:args+=["--discard-ack"]
        proc=subprocess.run(args,capture_output=True,text=True,timeout=12)
        with (self.root/"client-original.log").open("a",encoding="utf8") as f:
            f.write(json.dumps({"command":command,"fault":fault,"exit":proc.returncode,
                                "stdout":proc.stdout,"stderr":proc.stderr},sort_keys=True)+"\n")
        self.assertEqual(proc.returncode,expect,(args,proc.stdout,proc.stderr))
        return json.loads(proc.stdout.strip().splitlines()[-1])
    def effects(self):
        c=sqlite3.connect(self.db);rows=c.execute("SELECT attempt,subject,owner,receipt,units FROM effects").fetchall()
        c.close();return rows
    def journal_states(self):
        c=sqlite3.connect(self.journal);rows=c.execute("SELECT state FROM journal ORDER BY seq").fetchall()
        c.close();return [x[0] for x in rows]
    def test_01_transport_ack_dropped_after_durable_commit(self):
        r=self.client("dispatch",fault="drop_ack",expect=75)
        self.assertEqual(r["phase"],"ACK_UNKNOWN")
        self.assertIsNone(self.server.poll())
        j=self.client("reconcile")
        self.assertEqual(j["phase"],"NO_RETRY_CONFIRMED")
        self.assertEqual(self.effects()[0][3],j["receipt"])
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.journal_states(),["INTENT","ACK_UNKNOWN","NO_RETRY_CONFIRMED"])
    def test_02_server_process_crash_after_commit_no_ack_and_restart(self):
        r=self.client("dispatch",fault="crash_after_commit",expect=75)
        self.assertEqual(r["phase"],"ACK_UNKNOWN")
        self.assertEqual(self.server.wait(timeout=3),73)
        self.stop_provider();self.start_provider()
        j=self.client("reconcile")
        self.assertEqual(j["phase"],"NO_RETRY_CONFIRMED")
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(j["receipt"],self.effects()[0][3])
    def test_03_precommit_crash_and_authoritative_absence_no_retry(self):
        self.assertEqual(self.client("dispatch",fault="crash_before_commit",expect=75)["phase"],"ACK_UNKNOWN")
        self.assertEqual(self.server.wait(timeout=3),74)
        self.assertEqual(self.client("reconcile",expect=75)["phase"],"RECONCILE_UNKNOWN")
        self.stop_provider();self.start_provider()
        self.assertEqual(self.client("reconcile")["phase"],"ABSENT_REQUIRES_AUTHORITY")
        self.assertEqual(self.effects(),[])
    def test_04_consumer_discards_real_http_ack_then_recovers(self):
        self.assertEqual(self.client("dispatch",discard=True,expect=76)["phase"],"ACK_DISCARDED")
        j=self.client("reconcile")
        self.assertEqual(j["phase"],"NO_RETRY_CONFIRMED")
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(j["receipt"],self.effects()[0][3])
    def test_05_same_attempt_changed_owner_blocked(self):
        self.assertEqual(self.client("dispatch")["phase"],"APPLIED_ACK")
        other=self.client("dispatch",owner="OTHER_OWNER",journal=self.root/"rogue.sqlite3",expect=77)
        self.assertEqual(other["phase"],"BLOCK_IDENTITY")
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.effects()[0][2],self.ident["owner"])
    def test_06_explicit_duplicate_request_returns_same_receipt(self):
        a=self.client("dispatch");b=self.client("dispatch")
        self.assertEqual((a["phase"],b["phase"]),("APPLIED_ACK","ALREADY_CONFIRMED"))
        self.assertEqual(a["receipt"],b["receipt"])
        self.assertEqual(len(self.effects()),1)
    def test_07_concurrent_network_clients_one_effect(self):
        def args(j):
            return [sys.executable,str(CLIENT),"dispatch","--journal",str(j),"--url",self.url,
                    "--attempt",self.ident["attempt"],"--subject",self.ident["subject"],"--owner",self.ident["owner"]]
        a=subprocess.Popen(args(self.journal),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        b=subprocess.Popen(args(self.root/"consumer2.sqlite3"),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        outs=[]
        for p in (a,b):
            stdout,stderr=p.communicate(timeout=12)
            self.assertEqual(p.returncode,0,(stdout,stderr))
            outs.append(json.loads(stdout))
            with (self.root/"client-original.log").open("a",encoding="utf8") as f:
                f.write(json.dumps({"concurrent":True,"output":stdout,"stderr":stderr})+"\n")
        self.assertEqual(sorted(x["phase"] for x in outs),["ALREADY_CONFIRMED","APPLIED_ACK"])
        self.assertEqual(outs[0]["receipt"],outs[1]["receipt"])
        self.assertEqual(len(self.effects()),1)
        self.assertEqual(self.client("reconcile")["phase"],"NO_RETRY_CONFIRMED")
if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Test047)
    outcome=unittest.TextTestRunner(verbosity=2).run(suite)
    data={"experiment":"TS-EE-LLM-047-NETWORK-ACK-LOSS-20261030-001",
          "execution_attempt":"TS-EE-LLM-047-ATTEMPT-001",
          "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
          "network":"HTTP_OVER_127_0_0_1_DISTINCT_SUBPROCESSES",
          "provider":"SYNTHETIC_SQLITE_NOT_EXTERNAL",
          "tests_run":outcome.testsRun,"failures":len(outcome.failures),"errors":len(outcome.errors),
          "success":outcome.wasSuccessful(),
          "scenario_directories":sorted(x.name for x in ROOT.iterdir())}
    RESULT.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("TS_EE_LLM047="+("PASS_BOUNDED_NETWORK_ACK_DROP_RECOVERY" if outcome.wasSuccessful() else "FAIL_CLOSED")+";tests="+str(outcome.testsRun)+";failed="+str(len(outcome.failures)+len(outcome.errors))+";Product=NONE",flush=True)
    sys.exit(0 if outcome.wasSuccessful() else 1)
