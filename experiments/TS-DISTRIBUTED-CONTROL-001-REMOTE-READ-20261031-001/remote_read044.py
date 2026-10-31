#!/usr/bin/env python3
"""Read-only native Beads/Dolt GitHub remote qualification on an independent runner.

No Product, original task writes, kernel, push or external provider dispatch.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

EXP="TS-DISTRIBUTED-CONTROL-001-REMOTE-READ-20261031-001"
ATTEMPT="TS-DC044-REMOTE-READ-"+os.environ["TS044_SLOT"].upper()+"-ATTEMPT-001"
REMOTE="https://github.com/mauedgar/ts-execution-lab.git"
REMOTE_REF="refs/dolt/data"
PIN="1f72d68797114170a97fee27641858f2e55a4571"
ISSUES=("producer-1qa","producer-9a71a001","producer-9a71b002")
ROOT=pathlib.Path(os.environ["TS044_ROOT"]).resolve()
BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
ENV={**os.environ, "BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false",
     "BD_NON_INTERACTIVE":"1","GIT_TERMINAL_PROMPT":"0","NO_COLOR":"1"}
RESULT=pathlib.Path(os.environ["TS044_RESULT"]).resolve()

def run(args,cwd=None,timeout=80):
    x=subprocess.run(list(map(str,args)),cwd=cwd,env=ENV,encoding="utf8",
      capture_output=True,text=True,timeout=timeout)
    if x.returncode:raise RuntimeError("COMMAND_FAILED:"+str(args[:3])+":"+x.stderr[-400:])
    return x.stdout

def must(cond,label):
    if not cond: raise AssertionError(label)

def ref():
    v=run(["git","ls-remote",REMOTE,REMOTE_REF])
    p=v.strip().split("\t")
    must(len(p)==2 and p[1]==REMOTE_REF,"REMOTE_REF_NOT_FOUND")
    return p[0]

def native(*args):
    txt=run([BD,*args,"--json"],cwd=ROOT/"clone")
    off=[i for i in (txt.find("["),txt.find("{")) if i>=0]
    must(bool(off),"NATIVE_JSON_MISSING")
    return json.loads(txt[min(off):])

def rows(x):
    if isinstance(x,list): return x
    for k in ("issues","data","results","ready"):
        if isinstance(x.get(k),list):return x[k]
    return [x]

def main():
    slot=os.environ["TS044_SLOT"]
    must(slot in ("alpha","beta"),"WRONG_SLOT")
    must(not ROOT.exists() and not RESULT.exists(),"NOT_FRESH_ROOT")
    must(ref()==PIN,"DRIFT_BEFORE_READ")
    must("1.3.1" in run([BD,"--version"]),"NATIVE_VERSION")
    ROOT.mkdir(parents=True)
    run(["git","clone","--quiet","--no-tags","--single-branch","--branch",
         "experiment/beads-github-native-remote-20261013-009",REMOTE,ROOT/"clone"],timeout=110)
    must(not (ROOT/"clone"/".beads").exists(),"STORE_PREEXISTS")
    must(not (ROOT/"clone"/"state-kernel").exists(),"KERNEL_PREEXISTS")
    run([BD,"bootstrap"],cwd=ROOT/"clone",timeout=100)
    must((ROOT/"clone"/".beads").is_dir(),"BOOTSTRAP_NO_NATIVE_STORE")
    allissues=rows(native("list","--all"))
    extracted=sorted((str(x.get("id","")),str(x.get("status",""))) for x in allissues)
    must([i for i,_ in extracted]==list(ISSUES),"NOT_EXPECTED_ISSUES")
    first=rows(native("show",ISSUES[0]))
    must(len(first)==1 and first[0].get("id")==ISSUES[0],"FIRST_MISSING")
    must("SOURCE_REF=test://TS-BEADS-NATIVE-GITHUB-REMOTE-20261013-009/ORIGIN-A@FROZEN" in
         str(first[0].get("description","")),"SOURCE_ORIGIN_LOST")
    must(ref()==PIN,"DRIFT_AFTER_READ")
    payload={"experiment":EXP,"attempt":ATTEMPT,"slot":slot,"product_effect":"NONE",
      "remote_ref":REMOTE_REF,"remote_sha":PIN,"native_beads":"1.3.1",
      "recovered_issue_id_status":extracted,"source_origin_verified":True,
      "native_db_restored_from_fresh_git_clone":True,"kernel_used":False,
      "original_provider_dispatch_count":0,"native_push_count":0,
      "read_only_token":True,"host":"ubuntu-24.04_GitHub_Actions_fresh_runner",
      "status":"PASS_NATIVE_REMOTE_GITHUB_CROSS_HOST_READ_ONLY"}
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("TS_DC044="+payload["status"]+";slot="+slot+
      ";original_ref="+PIN+";count="+str(len(extracted))+";Product=NONE",flush=True)
    print("TS_DC044_RESULT_SHA256="+hashlib.sha256(RESULT.read_bytes()).hexdigest(),flush=True)

if __name__=="__main__":
    main()
