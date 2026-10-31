#!/usr/bin/env python3
"""Prospective tests: non-idempotent provider versus fail-closed consumer, no Product effects."""
import http.client,json,os,pathlib,socket,sqlite3,subprocess,sys,time,unittest,urllib.error,urllib.request
ROOT=pathlib.Path(os.environ["LAB048_ROOT"]).resolve()
PROVIDER=pathlib.Path(os.environ["LAB048_PROVIDER"]).resolve()
CONSUMER=pathlib.Path(os.environ["LAB048_CONSUMER"]).resolve()
RESULT=pathlib.Path(os.environ["LAB048_RESULT"]).resolve()
class BoundaryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):ROOT.mkdir(parents=True,exist_ok=False)
 def setUp(self):
  self.root=ROOT/self._testMethodName;self.root.mkdir()
  self.provider_db=self.root/"provider.sqlite3"
  self.consumer_db=self.root/"consumer.sqlite3"
  self.ready=self.root/"provider-ready.json"
  self.server=None;self.server_log=None
  self.a={"attempt":self._testMethodName,"subject":"synthetic@048","owner":"TS_EE_048"}
  self.start()
 def start(self):
  if self.ready.exists():self.ready.unlink()
  self.server_log=open(self.root/"provider-original.log","a",encoding="utf8")
  self.server=subprocess.Popen([sys.executable,str(PROVIDER),"--db",str(self.provider_db),"--ready",str(self.ready)],
             stdout=self.server_log,stderr=subprocess.STDOUT,text=True)
  deadline=time.monotonic()+6
  while not self.ready.exists():
   if self.server.poll() is not None:raise AssertionError("PROVIDER_EARLY_EXIT")
   if time.monotonic()>=deadline:raise AssertionError("PROVIDER_READY_TIMEOUT")
   time.sleep(.015)
  self.url="http://127.0.0.1:"+str(json.loads(self.ready.read_text())["port"])
 def stop(self):
  if self.server is None:return
  if self.server.poll() is None:
   self.server.terminate()
   try:self.server.wait(timeout=3)
   except subprocess.TimeoutExpired:self.server.kill();self.server.wait(timeout=3)
  self.server_log.close();self.server=None
 def tearDown(self):
  self.stop()
  for f in self.root.glob("*.sqlite3"):
   c=sqlite3.connect(f)
   self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok",str(f))
   c.execute("PRAGMA wal_checkpoint(TRUNCATE)");c.close()
 def args(self,command,extra=(),journal=None,owner=None,url=None):
  return [sys.executable,str(CONSUMER),command,"--journal",str(journal or self.consumer_db),
          "--url",url or self.url,"--attempt",self.a["attempt"],
          "--subject",self.a["subject"],"--owner",owner or self.a["owner"],*extra]
 def client(self,command,extra=(),expect=0,owner=None,url=None):
  p=subprocess.run(self.args(command,extra,owner=owner,url=url),capture_output=True,text=True,timeout=12)
  with (self.root/"consumer-original.log").open("a",encoding="utf8") as f:
   f.write(json.dumps({"cmd":command,"exit":p.returncode,"stdout":p.stdout,"stderr":p.stderr},sort_keys=True)+"\n")
  self.assertEqual(p.returncode,expect,(p.stdout,p.stderr))
  return json.loads(p.stdout.strip().splitlines()[-1])
 def effects(self):
  c=sqlite3.connect(self.provider_db)
  rows=c.execute("SELECT event_id,attempt,subject,owner,receipt FROM effects ORDER BY event_id").fetchall()
  c.close();return rows
 def states(self):
  c=sqlite3.connect(self.consumer_db)
  rows=c.execute("SELECT state FROM history ORDER BY seq").fetchall();c.close()
  return [x[0] for x in rows]
 def test_01_commit_then_tcp_ack_lost_blocks_duplicate(self):
  self.assertEqual(self.client("dispatch",["--fault","drop_after_commit"],expect=75)["phase"],"ACK_UNKNOWN")
  self.assertEqual(self.client("reconcile",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(self.client("dispatch",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(len(self.effects()),1)
  self.assertEqual(self.states(),["SEND_STARTED","UNKNOWN"])
  with self.assertRaises(urllib.error.HTTPError) as ex:urllib.request.urlopen(self.url+"/effect",timeout=2)
  self.assertEqual(ex.exception.code,405)
 def test_02_tcp_ack_lost_before_commit_blocks_even_with_zero_effect(self):
  self.assertEqual(self.client("dispatch",["--fault","drop_before_commit"],expect=75)["phase"],"ACK_UNKNOWN")
  self.assertEqual(len(self.effects()),0)
  self.assertEqual(self.client("dispatch",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(self.client("reconcile",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(len(self.effects()),0)
 def test_03_provider_crash_after_commit_cannot_be_retried(self):
  self.assertEqual(self.client("dispatch",["--fault","crash_after_commit"],expect=75)["phase"],"ACK_UNKNOWN")
  self.assertEqual(self.server.wait(timeout=3),73)
  self.stop();self.start()
  self.assertEqual(self.client("reconcile",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(self.client("dispatch",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(len(self.effects()),1)
 def test_04_ack_durable_and_same_attempt_never_reapplied(self):
  a=self.client("dispatch");self.assertEqual(a["phase"],"ACK_CONFIRMED")
  self.assertEqual(self.client("dispatch")["phase"],"NO_RETRY_CONFIRMED")
  self.assertEqual(self.client("reconcile")["receipt"],a["receipt"])
  self.assertEqual(len(self.effects()),1)
 def test_05_received_ack_discarded_locally_preserves_unknown(self):
  self.assertEqual(self.client("dispatch",["--discard-ack"],expect=76)["phase"],"ACK_DISCARDED")
  self.assertEqual(self.client("reconcile",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(len(self.effects()),1)
 def test_06_owner_collision_blocked_before_new_network_send(self):
  self.assertEqual(self.client("dispatch")["phase"],"ACK_CONFIRMED")
  self.assertEqual(self.client("dispatch",owner="DIFFERENT_OWNER",expect=77)["phase"],"BLOCK_IDENTITY")
  self.assertEqual(len(self.effects()),1)
 def test_07_process_exits_after_intent_before_http_false_positive_unknown(self):
  self.assertEqual(self.client("prepare")["phase"],"RESERVED_BUT_NOT_SENT")
  self.assertEqual(self.client("dispatch",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(self.client("reconcile",expect=77)["phase"],"BLOCK_REPEAT_UNKNOWN")
  self.assertEqual(len(self.effects()),0)
  self.assertEqual(self.states(),["SEND_STARTED"])
 def test_08_concurrent_consumers_same_journal_only_one_submission(self):
  args=self.args("dispatch")
  p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  q=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  outcomes=[]
  for x in (p,q):
   out,err=x.communicate(timeout=12)
   self.assertIn(x.returncode,(0,77),(out,err))
   item=json.loads(out.strip().splitlines()[-1]);outcomes.append(item["phase"])
   with (self.root/"concurrent-original.log").open("a",encoding="utf8") as f:f.write(json.dumps({"exit":x.returncode,"stdout":out,"stderr":err})+"\n")
  self.assertIn("ACK_CONFIRMED",outcomes)
  self.assertTrue(all(x in ("ACK_CONFIRMED","BLOCK_REPEAT_UNKNOWN","NO_RETRY_CONFIRMED") for x in outcomes),outcomes)
  self.assertEqual(len(self.effects()),1)
 def test_09_bypassing_consumer_demonstrates_real_provider_duplication(self):
  raw=json.dumps(self.a).encode()
  receipts=[]
  for i in range(2):
   req=urllib.request.Request(self.url+"/effect",data=raw,method="POST",headers={"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=4) as response:
    self.assertEqual(response.status,201)
    receipts.append(json.load(response)["receipt"])
  self.assertNotEqual(receipts[0],receipts[1])
  self.assertEqual(len(self.effects()),2)
  self.assertFalse(self.consumer_db.exists())
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryTests)
 r=unittest.TextTestRunner(verbosity=2).run(suite)
 summary={"experiment":"TS-EE-LLM-048-NONIDEMPOTENT-20261030-001",
          "execution_attempt":"TS-EE-LLM-048-ATTEMPT-001",
          "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
          "provider":"LOCAL_NONIDEMPOTENT_HTTP_SQLITE_MOCK",
          "tests_run":r.testsRun,"failures":len(r.failures),"errors":len(r.errors),
          "success":r.wasSuccessful(),
          "scenarios":sorted(x.name for x in ROOT.iterdir())}
 RESULT.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf8")
 print("TS_EE_LLM048="+("PASS_BOUNDED_FAIL_CLOSED_UNKNOWN" if r.wasSuccessful() else "FAIL_CLOSED")+
       ";tests="+str(r.testsRun)+";failed="+str(len(r.failures)+len(r.errors))+";Product=NONE",flush=True)
 sys.exit(0 if r.wasSuccessful() else 1)
