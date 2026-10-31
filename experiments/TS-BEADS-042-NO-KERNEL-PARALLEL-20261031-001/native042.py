#!/usr/bin/env python3
"""Real native Beads dispatch -> two parallel subprocesses -> receipts -> parent close.
Experimental work substrate, NO State Kernel import, product write, or new task store.
"""
import hashlib,json,os,pathlib,subprocess,sys,time,traceback
BASE=pathlib.Path(os.environ.get("TS042_BASE","/tmp/ts042-invalid")).resolve()
LAB=BASE/"git"
RESULT=pathlib.Path(os.environ["TS042_RESULT"]).resolve()
BD=pathlib.Path(os.environ.get("BD_BIN","/nonexistent")).resolve()
PREFIX="b042"
ENV={**os.environ,"BEADS_DIR":str(LAB/".beads"),"BD_NO_PUSH":"1",
     "BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1","NO_COLOR":"1",
     "GIT_TERMINAL_PROMPT":"0","BEADS_ACTOR":"TS042-TRUSTED-EXPERIMENTAL-COORDINATOR"}
R={"experiment":"TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001",
   "execution_attempt":"TS-BEADS-042-ATTEMPT-001",
   "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
   "status":"RUNNING","checks":{},"worker_dispatch_count":0,
   "state_backend":"NATIVE_BEADS_DOLT_ONLY","kernel_used":False,
   "parallel_work_type":"TWO_REAL_INDEPENDENT_LOCAL_SUBPROCESSES_WITH_DISJOINT_FILES",
   "limitations":["Workers are synthetic Python subprocesses, not native LLM providers.",
     "Trusted coordinator retains native Beads/Dolt write access and enforces receipts.",
     "No universally exclusive privileged writer: Beads 028 bypass remains.",
     "No Product global revision/event-count/hash-chain equivalence or Developer grant.",
     "No provider-native no-retry; UNKNOWN must be preserved by external policy."]}
def save():
 RESULT.parent.mkdir(parents=True,exist_ok=True)
 RESULT.write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf8")
def check(label,condition,evidence=None):
 R["checks"][label]={"pass":bool(condition),"evidence":evidence}
 save()
 if not condition:raise AssertionError(label+":"+str(evidence)[:350])
def cli(*args):
 p=subprocess.run([str(BD),*map(str,args)],cwd=LAB,env=ENV,
       capture_output=True,text=True,timeout=45)
 if p.returncode:raise RuntimeError("BD_COMMAND:"+str(args)+":exit="+str(p.returncode)+
                             ";stderr="+p.stderr[-380:]+";stdout="+p.stdout[-160:])
 return p.stdout
def native(*args):
 s=cli(*args,"--json")
 starts=[i for i in (s.find("{"),s.find("[")) if i>=0]
 if not starts:raise RuntimeError("JSON_MISSING:"+s[-230:])
 return json.loads(s[min(starts):])
def rows(v):
 if isinstance(v,list):return v
 if isinstance(v,dict):
  for key in ("issues","ready","results","data"):
   if isinstance(v.get(key),list):return v[key]
 return [v]
def ready():return sorted(x["id"] for x in rows(native("ready")))
def show(issue):
 a=rows(native("show",issue))
 if len(a)!=1:raise RuntimeError("UNEXPECTED_SHOW:"+str(issue))
 return a[0]
def worker():
 slot=os.environ["TS042_SLOT"]
 out=pathlib.Path(os.environ["TS042_SLOT_ROOT"]).resolve()
 gate=pathlib.Path(os.environ["TS042_GATE"])
 attempt=os.environ["TS042_CHILD_ATTEMPT"]
 if slot not in ("alpha","beta") or out.exists():raise SystemExit("BAD_WORKER")
 out.mkdir(parents=True)
 (out/"ready").write_text("READY\n")
 until=time.monotonic()+15
 while not gate.exists():
  if time.monotonic()>until:raise SystemExit("NO_DISPATCH_BARRIER")
  time.sleep(.015)
 start=time.monotonic_ns()
 payload={"slot":slot,"attempt":attempt,"subject":"frozen_beads042@synthetic",
          "owner":"worker-"+slot,"output":"REAL_EXECUTION_"+slot}
 data=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
 (out/"effect.json").write_bytes(data)
 time.sleep(.48)
 stop=time.monotonic_ns()
 receipt={"slot":slot,"attempt":attempt,"owner":"worker-"+slot,
          "subject":payload["subject"],"start_ns":start,"end_ns":stop,
          "effect_file":"effect.json","effect_sha256":hashlib.sha256(data).hexdigest(),
          "result_state":"CONFIRMED"}
 (out/"receipt.json").write_text(json.dumps(receipt,sort_keys=True)+"\n")
 print("TS042_WORKER="+slot+";effect_sha256="+receipt["effect_sha256"],flush=True)
def manager():
 check("fresh_workspace",not BASE.exists() and not RESULT.exists(),str(BASE))
 BASE.mkdir(parents=True)
 LAB.mkdir()
 subprocess.run(["git","init","-q",str(LAB)],check=True,timeout=10)
 rem=subprocess.run(["git","remote"],cwd=LAB,capture_output=True,text=True)
 check("no_git_remote",rem.returncode==0 and not rem.stdout.strip())
 version=cli("--version").strip()
 check("native_beads_pinned","1.3.1" in version,version)
 cli("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
 names=["preflight","alpha","beta","join","parent"]
 for n in names:cli("create","Beads042 real "+n,"--id",PREFIX+"-"+n,"--force",
                  "--type","task","--description","Experimental Beads-authoritative work state; Product NONE")
 for child,dep in [("alpha","preflight"),("beta","preflight"),("join","alpha"),
                   ("join","beta"),("parent","join")]:
  cli("dep","add",PREFIX+"-"+child,PREFIX+"-"+dep)
 check("initial_preflight_only",ready()==[PREFIX+"-preflight"],ready())
 cli("close",PREFIX+"-preflight")
 expected=sorted([PREFIX+"-alpha",PREFIX+"-beta"])
 check("two_parallel_tasks_ready",ready()==expected,ready())
 check("original_workgraph_has_no_external_kernel",
       not (LAB/"state-kernel").exists() and
       not any("state-kernel" in x for x in sys.modules))
 work=BASE/"owned-outputs"
 work.mkdir()
 procs=[]
 gate=BASE/"worker-go"
 for slot in ("alpha","beta"):
  args=[sys.executable,str(pathlib.Path(__file__).resolve()),"worker"]
  child_env={k:v for k,v in os.environ.items()
       if k not in ("BD_BIN","DOLT_BIN","BEADS_DIR","BEADS_ACTOR","BEADS_DOLT_SERVER_MODE")}
  child_env.update({"TS042_SLOT":slot,"TS042_SLOT_ROOT":str(work/slot),
                    "TS042_GATE":str(gate),
                    "TS042_CHILD_ATTEMPT":"TS-BEADS-042-"+slot.upper()+"-001"})
  p=subprocess.Popen(args,cwd=work,env=child_env,
       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  procs.append((slot,p))
  R["worker_dispatch_count"]+=1
 deadline=time.monotonic()+15
 while not all((work/slot/"ready").exists() for slot,_ in procs):
  if any(p.poll() is not None for _,p in procs):raise RuntimeError("WORKER_EXIT_BEFORE_START")
  if time.monotonic()>deadline:raise RuntimeError("WORKER_START_TIMEOUT")
  time.sleep(.025)
 gate.write_text("GO\n")
 receipts={}
 for slot,p in procs:
  stdout,stderr=p.communicate(timeout=15)
  check("worker_"+slot+"_terminal_success",p.returncode==0,
        {"out":stdout[-150:],"err":stderr[-240:]})
  out=work/slot
  x=json.loads((out/"receipt.json").read_text())
  raw=(out/"effect.json").read_bytes()
  check("worker_"+slot+"_owned_file_integrity",
        x["effect_sha256"]==hashlib.sha256(raw).hexdigest() and
        x["slot"]==slot and x["attempt"]=="TS-BEADS-042-"+slot.upper()+"-001" and
        x["owner"]=="worker-"+slot and x["result_state"]=="CONFIRMED")
  check("worker_"+slot+"_write_set_unique",
        sorted(p.name for p in out.iterdir())==["effect.json","ready","receipt.json"])
  receipts[slot]=x
 overlap=min(x["end_ns"] for x in receipts.values())-max(x["start_ns"] for x in receipts.values())
 check("two_real_workers_overlap_by_at_least_100ms",overlap>=100_000_000,overlap)
 check("worker_effects_disjoint",receipts["alpha"]["effect_sha256"]!=receipts["beta"]["effect_sha256"])
 R["actual_overlap_ns"]=overlap
 check("both_receipts_verified_before_any_child_close",len(receipts)==2)
 for slot in ("alpha","beta"):
  cli("update",PREFIX+"-"+slot,"--description",
      "TRUSTED_COORDINATOR_VERIFIED:"+slot+":"+receipts[slot]["effect_sha256"])
 cli("close",PREFIX+"-alpha")
 check("join_still_blocked_after_first_child",ready()==[PREFIX+"-beta"],ready())
 cli("close",PREFIX+"-beta")
 check("join_ready_after_both_confirmed",ready()==[PREFIX+"-join"],ready())
 joined=hashlib.sha256(("alpha:"+receipts["alpha"]["effect_sha256"]+
               "|beta:"+receipts["beta"]["effect_sha256"]).encode()).hexdigest()
 cli("update",PREFIX+"-join","--description","VERIFIED_CHILD_RECEIPTS_SHA256:"+joined)
 cli("close",PREFIX+"-join")
 check("parent_ready_after_join",ready()==[PREFIX+"-parent"],ready())
 cli("update",PREFIX+"-parent","--description",
    "FROZEN_EXPERIMENTAL_GRANT_ONLY;CHILD_RECEIPT_ROOT:"+joined)
 cli("close",PREFIX+"-parent")
 check("all_native_beads_issues_closed_ready_empty",ready()==[],ready())
 for n in names:
  found=show(PREFIX+"-"+n)
  check("native_closed_"+n,found.get("status")=="closed",found.get("status"))
 for slot in ("alpha","beta"):
  h=native("history",PREFIX+"-"+slot)
  check("native_history_for_"+slot,len(rows(h))>=2,len(rows(h)))
 R["native_store_directory"]=str(LAB/".beads")
 R["receipts"]=receipts
 R["receipt_root_sha256"]=joined
 R["status"]="PASS_REAL_PARALLEL_BEADS_FIRST_NO_STATE_KERNEL_WITH_TRUSTED_POLICY_BOUNDARY"
 save()
 print("TS_BEADS042="+R["status"]+";real_parallel=2;overlap_ns="+str(overlap)+
    ";parent=CLOSED;Product=NONE",flush=True)
if __name__=="__main__":
 if len(sys.argv)==2 and sys.argv[1]=="worker":
  worker()
 else:
  try:manager()
  except Exception as ex:
   R["status"]="FAIL_CLOSED_ORIGINAL"
   R["error"]=str(ex)[:450]
   save()
   traceback.print_exc()
   raise
