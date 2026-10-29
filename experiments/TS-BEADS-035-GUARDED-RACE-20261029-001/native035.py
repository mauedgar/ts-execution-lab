#!/usr/bin/env python3
"""035: two independent guarded writers in a disposable native Beads race.

No Product, shared Dolt or external provider effect.
Never exercises privileged alternate writer bypass already found in 028.
"""
from __future__ import annotations
import json,os,pathlib,secrets,subprocess,sys,time,urllib.request,urllib.error
from urllib.parse import quote

BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
LAB=pathlib.Path(os.environ["LAB_ROOT"]).resolve()
BASE=pathlib.Path(os.environ["TS035_BASE"]).resolve()
OUT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
PORT=31000+(int(os.environ.get("GITHUB_RUN_ID","35"))%22000)
HOST="http://127.0.0.1:"+str(PORT)
N=4
ROOT="ts035-root"
TOKEN=secrets.token_urlsafe(32)
E=dict(os.environ)
E.update({"BEADS_DIR":str(LAB/".beads"),"BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false",
          "BD_DOLT_AUTO_COMMIT":"on","BEADS_ACTOR":"TS-BEADS-035-NONPRODUCT",
          "BD_NON_INTERACTIVE":"1","NO_COLOR":"1","GIT_TERMINAL_PROMPT":"0"})
R={"id":"TS-BEADS-035-GUARDED-RACE-20261029-001","status":"RUNNING",
   "authority":"EXPERIMENTAL_CONTROL_ONLY","Product_effect":"NONE",
   "shared_Dolt_effect":"NONE","new_provider_effect":"NONE",
   "runtime":{"beads":"v1.3.1","dolt":"v2.2.0","store":"disposable_embedded",
              "rounds":N,"writer_processes_per_round":2},
   "checks":{},"rounds":[],"not_qualified":[
     "Universal causal writer exclusivity including privileged native bd/Dolt shell",
     "Native authorization of caller's Product authority or no-duplicate effects",
     "Multi-replica or remote Dolt concurrency, real provider ACK loss",
     "Global Product revision/event-count/hash-chain equivalence",
     "Product acceptance, integration, migration or Kernel retirement"]}
def save():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def check(k,v,evidence=None):
    R["checks"][k]={"result":"PASS" if v else "FAIL","evidence":evidence}
    save()
    if not v:raise AssertionError(k)

def command(*argv):
    q=subprocess.run([str(BD),*argv],cwd=LAB,env=E,capture_output=True,
                     text=True,timeout=55)
    if q.returncode:raise RuntimeError("NATIVE_CMD:"+str(argv)+":"+q.stderr[-700:]+":"+q.stdout[-300:])
    return q.stdout.strip()
def json_stdout(out):
    starts=[p for p in (out.find("{"),out.find("[")) if p>=0]
    if not starts:raise ValueError("MISSING_NATIVE_JSON:"+out[-300:])
    return json.loads(out[min(starts):])
def native(*argv):return json_stdout(command(*argv,"--json"))
def one(v):return v[0] if isinstance(v,list) and len(v)==1 else v

def request(path,method="GET",payload=None,token=None):
    raw=None if payload is None else json.dumps(payload,separators=(",",":")).encode()
    headers={"Content-Type":"application/json"}
    if token:headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(HOST+path,method=method,data=raw,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=35) as f:
            return f.status,f.read(7000).decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code,e.read(1200).decode(errors="replace")
def find(v,issue,depth=0):
    if depth>8:return None
    if isinstance(v,dict):
        if v.get("id")==issue and "revision" in v:return v
        for child in v.values():
            val=find(child,issue,depth+1)
            if val:return val
    if isinstance(v,list):
        for child in v:
            val=find(child,issue,depth+1)
            if val:return val
    return None
def detail(id):
    code,raw=request("/v0/beads/issues/"+quote(id)+"?brief_deps=true",token=TOKEN)
    if code!=200:raise RuntimeError("DETAIL_NOT_200:"+str(code)+":"+raw[-500:])
    v=find(json.loads(raw),id)
    if not v:raise RuntimeError("ISSUE_DETAIL_ABSENT:"+id+":"+raw[-500:])
    return v
def dependencies(row):
    return sorted(x["id"] for x in row.get("dependencies",[]))
def meta(row):
    m=row.get("metadata",{})
    return json.loads(m) if isinstance(m,str) else (m or {})
def git_remote():
    q=subprocess.run(["git","remote"],cwd=LAB,capture_output=True,text=True,timeout=10)
    return q.returncode==0 and not q.stdout.strip()
def batch(revision,roundno,side):
    target="ts035-r"+str(roundno)+side.lower()
    tag="round"+str(roundno)+"-"+side
    return {"actor":"TS035-WRITER-"+side,
      "provenance":"experiment://TS035/"+tag,
      "items":[{"kind":"update","update":{
          "target":{"id":ROOT},"expected_version":revision,
          "patch":{"metadata":{"set":{"ts035_epoch":tag}}}}},
        {"kind":"dep_add","dep_add":{"source":{"id":ROOT},
                                   "target":{"id":target},"type":"related"}}]}

def worker(roundno,side,revision):
    """Standalone OS process; only native bearer HTTP, never bd direct."""
    gate=BASE/("go-"+str(roundno))
    ready=BASE/("ready-"+str(roundno)+"-"+side)
    result=BASE/("worker-"+str(roundno)+"-"+side+".json")
    auth=os.environ["TS035_BEARER"]
    ready.write_text("READY\n")
    deadline=time.monotonic()+20
    while not gate.exists():
        if time.monotonic()>deadline:raise RuntimeError("BARRIER_TIMEOUT")
        time.sleep(.009)
    started=time.time_ns()
    code,body=request("/v0/beads/issues:batchApply","POST",batch(revision,roundno,side),auth)
    result.write_text(json.dumps({"side":side,"status":code,"start_ns":started,
                                  "finish_ns":time.time_ns(),"body":body[-750:]},
                                 sort_keys=True)+"\n")
    print("TS035_WORKER_"+side+"="+str(code))

def main():
    assert not LAB.exists() and not BASE.exists(),"NONEMPTY_ATTEMPT_WORKSPACE"
    BASE.mkdir(parents=True)
    LAB.mkdir(parents=True)
    subprocess.run(["git","init","-q",str(LAB)],check=True,timeout=10)
    check("isolated_git_no_remote",git_remote())
    command("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    check("beads_initialized_successfully",True)
    command("create","TS035 causal graph root","--id",ROOT,"--force","--type","task",
            "--description","NONPRODUCT_GUARDED_CONCURRENT_RACE")
    for roundno in range(1,N+1):
        for s in ("a","b"):
            command("create","TS035 graph child "+str(roundno)+s,
                    "--id","ts035-r"+str(roundno)+s,"--force","--type","task")
    tokenfile=BASE/"beads-auth.token"
    tokenfile.write_text(TOKEN+"\n")
    tokenfile.chmod(0o600)
    log=open(BASE/"beads-http.log","w")
    server=subprocess.Popen([str(BD),"serve","--addr","127.0.0.1:"+str(PORT),
                             "--auth-token-file",str(tokenfile)],
                            cwd=LAB,env=E,stdout=log,stderr=subprocess.STDOUT)
    try:
        for i in range(90):
            if server.poll() is not None:raise RuntimeError("NATIVE_HTTP_EARLY_EXIT")
            try:
                if request("/healthz")[0]==200:break
            except Exception:pass
            time.sleep(.20)
        else:raise RuntimeError("NATIVE_SERVER_NOT_READY")
        check("authenticated_service_started",True)
        unauth,_=request("/v0/beads/issues/"+ROOT)
        check("selected_http_route_rejects_unauthenticated_reader",unauth==401,unauth)
        observed=detail(ROOT)
        check("root_native_revision_available",bool(observed.get("revision")),observed.get("revision"))
        all_edges=[]
        for roundno in range(1,N+1):
            before=detail(ROOT)
            revision=before["revision"]
            expected_edges=dependencies(before)
            children={}
            processes=[]
            for side in ("A","B"):
                proc=subprocess.Popen([sys.executable,__file__,"worker",str(roundno),side,revision],
                                      cwd=LAB,env={**E,"TS035_BEARER":TOKEN},
                                      stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                processes.append((side,proc))
            try:
                for i in range(200):
                    if all((BASE/("ready-"+str(roundno)+"-"+s)).exists() for s in ("A","B")):break
                    if any(p.poll() is not None for _,p in processes):raise RuntimeError("EARLY_WORKER_EXIT")
                    time.sleep(.02)
                else:raise RuntimeError("WORKER_READINESS_TIMEOUT")
                (BASE/("go-"+str(roundno))).write_text("GO\n")
                for side,proc in processes:
                    stdout,stderr=proc.communicate(timeout=45)
                    if proc.returncode:raise RuntimeError("WORKER_"+side+"_CRASH:"+stderr[-500:])
                    children[side]=json.loads((BASE/("worker-"+str(roundno)+"-"+side+".json")).read_text())
            finally:
                for side,proc in processes:
                    if proc.poll() is None:
                        proc.terminate()
                        proc.wait(timeout=5)
            accepted=[s for s,x in children.items() if x["status"]==200]
            rejected=[s for s,x in children.items() if x["status"]!=200]
            check("round"+str(roundno)+"_one_winner_one_rejection",
                  len(accepted)==1 and len(rejected)==1,
                  {"codes":{s:x["status"] for s,x in children.items()},"revision":revision})
            after=detail(ROOT)
            winner=accepted[0]; loser=rejected[0]
            winner_id="ts035-r"+str(roundno)+winner.lower()
            loser_id="ts035-r"+str(roundno)+loser.lower()
            d=dependencies(after)
            check("round"+str(roundno)+"_winner_edge_only",
                  d==sorted(expected_edges+[winner_id]) and loser_id not in d,
                  {"observed":d,"winner":winner_id,"loser":loser_id})
            check("round"+str(roundno)+"_root_revision_changed",
                  after["revision"]!=revision,
                  {"before":revision,"after":after["revision"]})
            check("round"+str(roundno)+"_root_metadata_records_winner",
                  meta(after).get("ts035_epoch")=="round"+str(roundno)+"-"+winner,
                  meta(after))
            check("round"+str(roundno)+"_rejected_request_failure_status",
                  children[loser]["status"]>=400,
                  {"loser":loser,"status":children[loser]["status"],
                   "response":children[loser]["body"][-350:]})
            R["rounds"].append({"round":roundno,"revision":revision,
                 "winner":winner,"loser":loser,"writer_status":{s:x["status"] for s,x in children.items()},
                 "writer_start_ns":{s:x["start_ns"] for s,x in children.items()},
                 "root_after_revision":after["revision"],"winner_edge":winner_id,
                 "rejected_edge_absent":True})
            all_edges.append(winner_id)
            save()
        final=detail(ROOT)
        check("final_live_graph_exact_winning_edges",
              dependencies(final)==sorted(all_edges),dependencies(final))
    finally:
        if server.poll() is None:
            server.terminate()
            try:server.wait(timeout=12)
            except subprocess.TimeoutExpired:
                server.kill();server.wait(timeout=5)
        log.close()
    persisted=one(native("show",ROOT))
    check("fresh_cli_process_recovers_same_graph",
          dependencies(persisted)==sorted(all_edges),
          {"observed":dependencies(persisted),"expected":sorted(all_edges)})
    check("final_git_no_remote",git_remote())
    R["status"]="PASS_NATIVE_CONCURRENT_GUARDED_CAUSAL_WRITER_WITH_PRIVILEGED_BOUNDARY_OPEN"
    save()
    print("TS_BEADS035="+R["status"]+";rounds="+str(N)+";checks="+str(len(R["checks"]))+
          ";Product=NONE;shared_Dolt=NONE;new_provider=NONE")
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="worker":
        worker(int(sys.argv[2]),sys.argv[3],sys.argv[4])
    else:
        try:main()
        except Exception as e:
            R["status"]="FAIL_CLOSED_NATIVE_GUARDED_CONCURRENCY"
            R["error"]=str(e)
            save()
            raise
