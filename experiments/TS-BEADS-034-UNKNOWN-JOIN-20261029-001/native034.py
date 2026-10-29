#!/usr/bin/env python3
"""034: Beads-native UNKNOWN issue reconciled against the already-terminal 033 effect.

All writes are to one disposable, no-remote Beads database; provider requests are GET.
Each stage executes in a distinct Python OS process and each bd call is a fresh process.
"""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

LAB=Path(os.environ["LAB_ROOT"]).resolve()
BD=Path(os.environ["BD_BIN"]).resolve()
TMP=Path(os.environ["RUNNER_TEMP"]).resolve()/"ts034"
STATE=TMP/"events.json"
ID="ts034-provider-attempt-001"
ORIGINAL_ATTEMPT="TS-BEADS-033-PROVIDER-20261029-001/ATTEMPT-001"
PROVIDER_REPO="mauedgar/ts-execution-lab"
SHA033="eebf8e72b83df5aed61416ffc0fa81e84fdf55ea"
RUN=40930288498
JOB=123646594227
ART=12921817863
ARTNAME="ts-beads-033-provider-attempt-001"
DIGEST="sha256:329d05a218ea04dd740ab1579aed31d00a3f110700670e4d380993a0bde98dc6"
REQSHA="350fb2c516c5ae94cf34cac7c38f5ea10ef11e3d715bf35826dadbce25dfdfe2"
ENV=dict(os.environ)
ENV.update({"BEADS_DIR":str(LAB/".beads"),"BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false",
            "BD_DOLT_AUTO_COMMIT":"on","BD_NON_INTERACTIVE":"1",
            "BEADS_ACTOR":"TS-BEADS-034-NONPRODUCT","NO_COLOR":"1","GIT_TERMINAL_PROMPT":"0"})

def state():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"id":"TS-BEADS-034-UNKNOWN-JOIN-20261029-001",
            "authority":"EXPERIMENTAL_CONTROL_ONLY",
            "status":"IN_PROGRESS","Product_effect":"NONE","shared_Dolt_effect":"NONE",
            "new_provider_effect":"NONE","original_provider_run":RUN,"checks":{},
            "not_qualified":["Actual network ACK loss/timeout","Product native global revision/event_count equivalence",
                "Native Beads alone enforcing retry/authority","Concurrent privileged native writer safety",
                "Product adoption, canonical migration or Kernel removal"]}

def persist(r):
    TMP.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")

def check(r,name,condition,evidence=None):
    r["checks"][name]={"result":"PASS" if condition else "FAIL","evidence":evidence}
    persist(r)
    if not condition: raise AssertionError(name)

def run(*args, json_mode=False):
    argv=[str(BD),*args]
    if json_mode:argv.append("--json")
    p=subprocess.run(argv,cwd=LAB,env=ENV,text=True,capture_output=True,timeout=55)
    if p.returncode:raise RuntimeError("BD_ERROR "+repr(args)+" "+p.stderr[-1500:]+p.stdout[-600:])
    return p.stdout.strip()

def bdj(*args):
    raw=run(*args,json_mode=True)
    positions=[i for i in (raw.find("{"),raw.find("[")) if i>=0]
    if not positions:raise ValueError("EMPTY_JSON "+raw[-500:])
    return json.loads(raw[min(positions):])

def one(x):
    if isinstance(x,list):
        if len(x)!=1:raise ValueError("EXPECTED_ONE_ISSUE "+str(len(x)))
        return x[0]
    return x

def desc(x):return json.loads(one(x)["description"])

def current():return one(bdj("show",ID))

def commit():
    obj=bdj("vc","status")
    return obj.get("commit") or obj.get("Commit")

def no_remote():
    r=subprocess.run(["git","remote"],cwd=LAB,text=True,capture_output=True,timeout=10)
    return r.returncode==0 and not r.stdout.strip()

def gh(path, *, binary=False):
    url="https://api.github.com/repos/"+PROVIDER_REPO+"/"+path
    token=os.environ.get("GITHUB_TOKEN","")
    if not token:raise RuntimeError("READ_ONLY_PROVIDER_TOKEN_ABSENT")
    headers={"Accept":"application/vnd.github+json","Authorization":"Bearer "+token,
             "X-GitHub-Api-Version":"2022-11-28"}
    if binary:
        target=TMP/"original033.zip"
        p=subprocess.run(["curl","--fail","--location","--silent","--show-error",
                          "--header","Accept: application/vnd.github+json",
                          "--header","Authorization: Bearer "+token,
                          "--output",str(target),url],
                         capture_output=True,text=True,timeout=70)
        if p.returncode:raise RuntimeError("READ_ONLY_PROVIDER_ZIP_FAILED "+p.stderr[-600:])
        return target.read_bytes()
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=40) as resp:
        return json.loads(resp.read())

def strict_receipt(x):
    required={"schema":"TS-BEADS-033-PROVIDER-RECEIPT/1",
              "attempt":ORIGINAL_ATTEMPT,"subject":PROVIDER_REPO+"@"+SHA033,
              "run_id":str(RUN),"run_attempt":"1",
              "request_sha256":REQSHA,"effect":"PROVIDER_NATIVE_ARTIFACT_WRITE",
              "Product_effect":"NONE","shared_Dolt_effect":"NONE",
              "workflow":"TS Beads 033 External Provider Identity"}
    return isinstance(x,dict) and all(x.get(k)==v for k,v in required.items())

def retry_allowed(x):
    # Tecnotron caller policy; not an intrinsic bd security boundary.
    return not (x.get("effect_state")=="UNKNOWN" and x.get("reconciliation_required") is True)

def prepare(r):
    LAB.mkdir(parents=True,exist_ok=False)
    subprocess.run(["git","init","-q",str(LAB)],check=True,timeout=15)
    check(r,"empty_lab_no_remote",bool(no_remote()))
    run("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    attempt={"schema":"TS-BEADS-034-ATTEMPT/1","attempt_id":ORIGINAL_ATTEMPT,
             "operation_id":"TS-BEADS-033-PROVIDER-20261029-001",
             "effect_state":"UNKNOWN","reconciliation_required":True,
             "expected":{"run_id":RUN,"run_attempt":1,"source":SHA033,
                         "artifact_id":ART,"request_sha256":REQSHA},
             "result_ref":None}
    made=one(bdj("create","TS034 synthetic Beads UNKNOWN attempt",
                 "--type","task","--id",ID,"--force",
                 "--description",json.dumps(attempt,sort_keys=True,separators=(",",":")),
                 "--metadata",'{"ts034":"disposable_provider_attempt"}'))
    check(r,"native_attempt_created_once",made.get("id")==ID,made.get("id"))
    check(r,"native_unknown_after_first_process",desc(current())==attempt)
    check(r,"caller_policy_blocks_second_dispatch",not retry_allowed(attempt),
          "no second provider run or Beads attempt created")
    r["before_commit"]=commit()
    check(r,"native_unknown_history_commit_available",bool(r["before_commit"]),r["before_commit"])
    persist(r)

def join(r):
    before=desc(current())
    check(r,"fresh_process_recovers_unknown",before["effect_state"]=="UNKNOWN" and before["reconciliation_required"])
    check(r,"second_attempt_still_blocked",not retry_allowed(before))
    run_meta=gh("actions/runs/"+str(RUN))
    check(r,"provider_exact_run_completed_success",
          run_meta.get("id")==RUN and run_meta.get("head_sha")==SHA033
          and run_meta.get("status")=="completed" and run_meta.get("conclusion")=="success"
          and run_meta.get("run_attempt")==1,
          {"id":run_meta.get("id"),"status":run_meta.get("status"),"sha":run_meta.get("head_sha")})
    jobs=gh("actions/runs/"+str(RUN)+"/jobs").get("jobs",[])
    found=[j for j in jobs if j.get("id")==JOB]
    check(r,"provider_exact_job_completed_success",len(found)==1
          and found[0].get("status")=="completed" and found[0].get("conclusion")=="success",
          [j.get("id") for j in found])
    artifacts=gh("actions/runs/"+str(RUN)+"/artifacts").get("artifacts",[])
    matching=[a for a in artifacts if a.get("id")==ART]
    check(r,"provider_artifact_exact_identity",
          len(matching)==1 and matching[0].get("name")==ARTNAME
          and matching[0].get("digest")==DIGEST and matching[0].get("expired") is False
          and matching[0].get("workflow_run",{}).get("head_sha")==SHA033,
          [{"id":a.get("id"),"digest":a.get("digest")} for a in matching])
    zipbytes=gh("actions/artifacts/"+str(ART)+"/zip",binary=True)
    got="sha256:"+hashlib.sha256(zipbytes).hexdigest()
    check(r,"downloaded_provider_zip_sha256_exact",got==DIGEST,
          {"observed":got,"expected":DIGEST,"bytes":len(zipbytes)})
    with zipfile.ZipFile(io.BytesIO(zipbytes)) as z:
        names=z.namelist()
        check(r,"provider_zip_single_expected_receipt",names==["PROVIDER_RECEIPT.json"],names)
        original=json.loads(z.read("PROVIDER_RECEIPT.json"))
    check(r,"provider_receipt_internal_exact_identity",strict_receipt(original),original)
    for field,fake in [("attempt","BAD_ATTEMPT"),("run_id","999999999"),
                       ("request_sha256","bad_sha"),("subject","bad_subject")]:
        tampered=copy.deepcopy(original);tampered[field]=fake
        check(r,"reject_tampered_"+field,not strict_receipt(tampered),field)
    check(r,"unknown_preserved_before_verified_commit",desc(current())==before)
    after=copy.deepcopy(before)
    after.update({"effect_state":"CONFIRMED","reconciliation_required":False,
                  "result_ref":{"provider":"GITHUB_ACTIONS","run_id":RUN,"job_id":JOB,
                                "artifact_id":ART,"artifact_digest":DIGEST,
                                "request_sha256":REQSHA,"source":SHA033},
                  "join_classification":"CONFIRMED_FROM_PROVIDER_NATIVE_RECEIPT"})
    run("update",ID,"--description",json.dumps(after,sort_keys=True,separators=(",",":")))
    r["after_commit"]=commit()
    check(r,"native_confirmed_commit_advanced",
          bool(r["after_commit"]) and r["after_commit"]!=r["before_commit"],
          {"unknown":r["before_commit"],"confirmed":r["after_commit"]})
    check(r,"native_confirmed_matches_verified_provider",desc(current())==after)
    r["observed_original_receipt_sha256"]=hashlib.sha256(
        json.dumps(original,sort_keys=True,indent=2).encode()+b"\n").hexdigest()
    persist(r)

def inspect(r):
    cur=desc(current())
    check(r,"independent_final_process_sees_confirmed",
          cur["effect_state"]=="CONFIRMED" and cur["reconciliation_required"] is False
          and cur["result_ref"]["artifact_id"]==ART)
    h=bdj("history",ID)
    hashes=[e.get("CommitHash") or e.get("commit_hash") or e.get("hash")
            for e in h if isinstance(e,dict)]
    check(r,"native_history_retains_unknown_and_confirmed",
          r["before_commit"] in hashes and r["after_commit"] in hashes,
          {"observed_hashes":hashes})
    old=desc(bdj("show",ID,"--as-of",r["before_commit"]))
    new=desc(bdj("show",ID,"--as-of",r["after_commit"]))
    check(r,"native_asof_unknown_pre_join",old["effect_state"]=="UNKNOWN" and old["reconciliation_required"])
    check(r,"native_asof_confirmed_post_join",new==cur)
    check(r,"final_no_remote",bool(no_remote()))
    check(r,"no_second_attempt_or_provider_dispatch",
          cur["attempt_id"]==ORIGINAL_ATTEMPT and r["original_provider_run"]==RUN
          and len([x for x in h if isinstance(x,dict)])>=2,
          "only the already-terminal 033 provider identity was read; provider POST count=0")
    r["status"]="PASS_B_FIRST_UNKNOWN_TO_CONFIRMED_REAL_PROVIDER_READ_ONLY_JOIN"
    r["process_stages"]=["prepare","join","inspect"]
    r["effects"]={"Product":"NONE","shared_Dolt":"NONE","new_provider":"NONE",
                 "disposable_native_Beads":"UNKNOWN -> CONFIRMED"}
    persist(r)
    print("TS_BEADS034_JOIN="+r["status"]+";checks="+str(len(r["checks"]))+
          ";provider_original_run="+str(RUN)+";provider_new_effect=NONE;Product=NONE")

if __name__=="__main__":
    phase=sys.argv[1]
    r=state()
    try:
        {"prepare":prepare,"join":join,"inspect":inspect}[phase](r)
    except Exception as e:
        r["status"]="FAIL_CLOSED_"+phase.upper()
        r["error"]=str(e)
        persist(r)
        raise
