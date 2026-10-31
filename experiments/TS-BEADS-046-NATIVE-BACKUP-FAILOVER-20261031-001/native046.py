#!/usr/bin/env python3
"""046 - independently recover NONTERMINAL native Beads from remote GitHub artifact.
Two distinct GitHub-hosted runners; NOT a shared remote SQL-primary qualification.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tarfile

ROLE=os.environ["TS046_ROLE"]
ROOT=pathlib.Path(os.environ["TS046_ROOT"]).resolve()
ART=pathlib.Path(os.environ["TS046_ART"]).resolve()
PROJ=ROOT/"project"
BD=os.environ["BD_BIN"]
PFX="b046"
PROVIDER="github-actions:41177022889:artifact:13032823741:sha256:07b70ea4902d4bfec9efdda08e939b3d753287a2d2b74c6a7e4fe93f38ee33f4"
OP="TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001"
ATT="TS-BEADS-046-"+("A" if ROLE=="producer" else "B")+"-ATTEMPT-001"
ENV={**os.environ,"BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1",
     "GIT_TERMINAL_PROMPT":"0","NO_COLOR":"1","BEADS_DIR":str(PROJ/".beads"),
     "BEADS_ACTOR":"TS046-"+ROLE.upper()}
R={"operation":OP,"execution_attempt":ATT,"role":ROLE,
   "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
   "kernel_used":False,"provider_reference":PROVIDER,"provider_redispatch_count":0,
   "state_backend":"NATIVE_BEADS_DOLT","remote_persistence":"GITHUB_ACTIONS_NATIVE_BACKUP_ARTIFACT",
   "live_remote_sql_primary":False,"status":"RUNNING","checks":{},
   "limitations":["No live shared remote Dolt SQL endpoint; artifact transfer only.",
   "Producer host cleanly terminates, not forcibly crashed.",
   "Original provider 045 receipt is a read-only witness, NOT a beta child effect.",
   "No real provider UNKNOWN/exactly-once guarantee or Product authority."]}
def check(name,yes,extra=None):
    R["checks"][name]={"pass":bool(yes),"evidence":extra}
    if not yes:raise RuntimeError("CHECK_FAILED:"+name+":"+str(extra)[:220])
def command(args,cwd=PROJ,allow=False,timeout=80):
    p=subprocess.run(list(map(str,args)),cwd=cwd,env=ENV,
                      capture_output=True,text=True,timeout=timeout)
    if not allow and p.returncode:
        raise RuntimeError("COMMAND_FAILED:"+str(args[:3])+":"+str(p.returncode)+":"+p.stderr[-300:])
    return p
def bd(*args):
    return command([BD,*args],timeout=90).stdout
def native(*args):
    txt=bd(*args,"--json")
    locations=[n for n in (txt.find("["),txt.find("{")) if n>=0]
    check("native_json_present_"+str(args[0]),bool(locations))
    return json.loads(txt[min(locations):])
def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for key in ("issues","ready","results","data"):
            if isinstance(x.get(key),list):return x[key]
    return [x]
def show(n):
    a=rows(native("show",PFX+"-"+n))
    if len(a)!=1:raise RuntimeError("ISSUE_MISSING:"+n)
    return a[0]
def ready():
    return sorted(x["id"] for x in rows(native("ready")))
def init():
    check("fresh_host_workspace",not ROOT.exists())
    PROJ.mkdir(parents=True)
    command(["git","init","-q"],cwd=PROJ)
    check("no_git_remote",command(["git","remote"]).stdout.strip()=="")
    check("no_kernel_folder",not (PROJ/"state-kernel").exists())
    bd("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    check("native_store_created",(PROJ/".beads").exists())
def producer():
    init()
    check("native_bd_version","1.3.1" in command([BD,"--version"]).stdout)
    for n in ("preflight","alpha","beta","join","parent"):
        bd("create","TS046 "+n,"--id",PFX+"-"+n,"--force","--type","task",
           "--description","Synthetic lab task Product NONE")
    for child,dep in (("alpha","preflight"),("beta","preflight"),
                      ("join","alpha"),("join","beta"),("parent","join")):
        bd("dep","add",PFX+"-"+child,PFX+"-"+dep)
    check("only_preflight_ready",ready()==[PFX+"-preflight"])
    bd("close",PFX+"-preflight")
    check("both_children_ready",ready()==[PFX+"-alpha",PFX+"-beta"])
    bd("update",PFX+"-alpha","--description","EXTERNAL_READ_ONLY_WITNESS:"+PROVIDER)
    bd("close",PFX+"-alpha")
    bd("update",PFX+"-beta","--status","in_progress",
       "--description","SYNTHETIC_HOST_LOSS_PENDING;NO_EXTERNAL_PROVIDER_DISPATCH")
    check("alpha_closed",show("alpha")["status"]=="closed")
    check("beta_in_progress",show("beta")["status"]=="in_progress")
    check("join_blocked",show("join")["status"]!="closed" and PFX+"-join" not in ready())
    check("parent_blocked",show("parent")["status"]!="closed" and PFX+"-parent" not in ready())
    backup=ROOT/"dolt-native-backup"
    bd("backup","init",str(backup))
    bd("backup","sync")
    check("native_backup_populated",backup.exists() and any(backup.iterdir()))
    ART.mkdir(parents=True,exist_ok=True)
    output=ART/"BACKUP046.tar.gz"
    with tarfile.open(output,"w:gz") as tar:
        tar.add(backup,arcname="dolt-native-backup")
    hashval=hashlib.sha256(output.read_bytes()).hexdigest()
    (ART/"BACKUP_SHA256.txt").write_text(hashval+"  BACKUP046.tar.gz\n",encoding="utf8")
    R["backup_sha256"]=hashval
    R["source_run_id"]=os.environ["GITHUB_RUN_ID"]
    R["native_issue_count"]=5
    check("provider_original_045_verified_by_workflow",os.environ.get("TS046_PROVIDER_VERIFIED")=="yes")
    R["status"]="PASS_NATIVE_BACKUP_PUBLISHED_FROM_NONTERMINAL_HOST_A"
    (ART/"RESULT046_A.json").write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("TS_BEADS046_A="+R["status"]+";backup_sha256="+hashval+";Product=NONE")
def consumer():
    producer_art=pathlib.Path(os.environ["TS046_PRODUCER_ART"]).resolve()
    receipt=json.loads((producer_art/"RESULT046_A.json").read_text(encoding="utf8"))
    check("original_A_identity",receipt.get("execution_attempt")=="TS-BEADS-046-A-ATTEMPT-001")
    check("original_A_status",receipt.get("status")=="PASS_NATIVE_BACKUP_PUBLISHED_FROM_NONTERMINAL_HOST_A")
    check("same_original_run",receipt.get("source_run_id")==os.environ["GITHUB_RUN_ID"])
    source=producer_art/"BACKUP046.tar.gz"
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    expected=(producer_art/"BACKUP_SHA256.txt").read_text().split()[0]
    check("external_provider_backup_integrity",digest==expected==receipt["backup_sha256"],digest)
    check("provider_original_045_verified_by_workflow",os.environ.get("TS046_PROVIDER_VERIFIED")=="yes")
    check("fresh_host_does_not_inherit_producer_workspace",not ROOT.exists())
    PROJ.mkdir(parents=True)
    command(["git","init","-q"],cwd=PROJ)
    check("no_host_A_store_copy",not (PROJ/".beads").exists())
    check("no_git_remote",command(["git","remote"]).stdout.strip()=="")
    bd("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    with tarfile.open(source,"r:gz") as tar:
        names=tar.getnames()
        check("backup_tar_entries_scoped",all(x=="dolt-native-backup" or x.startswith("dolt-native-backup/") for x in names))
        tar.extractall(path=ROOT,filter="data")
    bd("backup","restore","--force",str(ROOT/"dolt-native-backup"))
    check("recovered_alpha_closed",show("alpha")["status"]=="closed")
    check("recovered_beta_in_progress",show("beta")["status"]=="in_progress")
    check("original_external_ref_present",PROVIDER in str(show("alpha")["description"]))
    check("native_join_still_blocked",PFX+"-join" not in ready())
    check("native_parent_still_blocked",PFX+"-parent" not in ready())
    bd("update",PFX+"-beta","--description","HOST_B_COLD_RESTORED_SYNTHETIC;ORIGINAL_NO_PROVIDER_DISPATCH")
    bd("close",PFX+"-beta")
    check("join_native_ready",ready()==[PFX+"-join"],ready())
    bd("close",PFX+"-join")
    check("parent_native_ready",ready()==[PFX+"-parent"],ready())
    bd("close",PFX+"-parent")
    check("ready_empty_after_recovery",ready()==[],ready())
    for n in ("preflight","alpha","beta","join","parent"):
        check("issue_"+n+"_terminal",show(n)["status"]=="closed")
    for n in ("alpha","beta"):
        check("history_"+n+"_retained",len(rows(native("history",PFX+"-"+n)))>=2)
    check("no_kernel_used",not (ROOT/"state-kernel").exists())
    R["recovered_from_original_A_backup_sha256"]=digest
    R["source_run_id"]=os.environ["GITHUB_RUN_ID"]
    R["native_issue_count"]=5
    R["independent_host_runners"]=2
    R["status"]="PASS_REMOTE_NATIVE_BACKUP_NONTERMINAL_HOST_FAILOVER_WITH_LIMITATIONS"
    ART.mkdir(parents=True,exist_ok=True)
    (ART/"RESULT046_B.json").write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("TS_BEADS046_B="+R["status"]+";independent_hosts=2;sql_live=false;Product=NONE")
if __name__=="__main__":
    try:
        if ROLE=="producer":producer()
        elif ROLE=="consumer":consumer()
        else:raise RuntimeError("INVALID_ROLE")
    except BaseException as e:
        R["status"]="FAIL_CLOSED_ORIGINAL"
        R["error_class"]=type(e).__name__
        R["error"]=str(e)[:400]
        ART.mkdir(parents=True,exist_ok=True)
        (ART/("RESULT046_A.json" if ROLE=="producer" else "RESULT046_B.json")).write_text(
            json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf8")
        raise
