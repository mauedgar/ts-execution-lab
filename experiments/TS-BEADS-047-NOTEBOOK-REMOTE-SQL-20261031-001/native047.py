#!/usr/bin/env python3
"""TS-BEADS-047: native Beads live SQL from independent GitHub-hosted runners.
Uses only a pre-provisioned private notebook Dolt server; NO self-hosted shadow database,
no Product, no provider action dispatch, no automatic failover or retry.
"""
import hashlib
import json
import os
import pathlib
import platform
import socket
import subprocess
import tarfile
import sys
import pymysql

ROLE=os.environ["TS047_ROLE"]
OP="TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001"
PFX="b047"
DB="ts047beads"
HOST=os.environ["TS047_SQL_HOST"]
PORT=3307
USER="ts047_writer"
PWD=os.environ["TS047_SQL_PASSWORD"]
RO_PWD=os.environ["TS047_RO_PASSWORD"]
BD=os.environ["BD_BIN"]
ROOT=pathlib.Path(os.environ["TS047_ROOT"]).resolve()
PROJ=ROOT/"project"
ORIGINAL=pathlib.Path(os.environ["TS047_ORIGINAL"]).resolve()
META_SOURCE=os.environ.get("TS047_META_SOURCE","")
RUN=os.environ["GITHUB_RUN_ID"]
SHA=os.environ["GITHUB_SHA"]
MACHINE_FINGERPRINT=hashlib.sha256(socket.gethostname().encode()).hexdigest()
HOST_FINGERPRINT=hashlib.sha256((HOST+":"+str(PORT)).encode()).hexdigest()
ATT="TS-BEADS-047-"+ROLE.upper()+"-ATTEMPT-001"
ENV={**os.environ,"HOME":str(ROOT/"home"),
     "BEADS_DIR":str(PROJ/".beads"),
     "BEADS_DOLT_SERVER_MODE":"1","BEADS_DOLT_SERVER_HOST":HOST,
     "BEADS_DOLT_SERVER_PORT":str(PORT),"BEADS_DOLT_SERVER_USER":USER,
     "BEADS_DOLT_PASSWORD":PWD,
     "BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1",
     "GIT_TERMINAL_PROMPT":"0","BEADS_ACTOR":"TS047-"+ROLE.upper(),
     "NO_COLOR":"1"}
R={"operation":OP,"attempt":ATT,"role":ROLE,"status":"STARTED",
   "run_id":RUN,"run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),
   "subject_sha":SHA,"host_fingerprint":HOST_FINGERPRINT,
   "runner_machine_fingerprint":MACHINE_FINGERPRINT,
   "product_effect":"NONE","kernel_used":False,
   "original_provider_dispatch_count":0,"sql_server_mode":True,
   "server_data_owner":"NOTEBOOK_WINDOWS_PRIMARY","automatic_failover":False,
   "checks":{}}

def save(name=None):
    ORIGINAL.mkdir(parents=True,exist_ok=True)
    dest=ORIGINAL/(name or ("RESULT047_"+ROLE.upper()+".json"))
    dest.write_text(json.dumps(R,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def check(name,condition,detail=None):
    R["checks"][name]={"pass":bool(condition),"detail":detail}
    save()
    if not condition:
        raise RuntimeError("FAIL_CLOSED:"+name+(":"+str(detail)[:100] if detail else ""))

def run(args,cwd=PROJ,timeout=90,allow=False):
    cp=subprocess.run([str(x) for x in args],cwd=cwd,env=ENV,
       capture_output=True,text=True,timeout=timeout)
    if cp.returncode and not allow:
        err=cp.stderr[-240:]
        for secret in (PWD,RO_PWD,HOST):
            if secret:err=err.replace(secret,"[REDACTED]")
        raise RuntimeError("CLI_FAILED:"+str(args[0]).split("/")[-1]+
                           ":rc="+str(cp.returncode)+":"+err)
    return cp

def native(*args):
    txt=run([BD,*args,"--json"]).stdout
    indexes=[p for p in (txt.find("["),txt.find("{")) if p>=0]
    check("native_json_"+args[0],bool(indexes))
    return json.loads(txt[min(indexes):])

def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for k in ("issues","data","results","ready"):
            if isinstance(x.get(k),list):return x[k]
    if x is None:return []
    return [x]

def ready():return sorted(r["id"] for r in rows(native("ready")))
def show(name):
    r=rows(native("show",PFX+"-"+name))
    check("native_show_"+name,len(r)==1 and r[0].get("id")==PFX+"-"+name)
    return r[0]

def conn(user=USER,password=PWD,db=DB):
    return pymysql.connect(host=HOST,port=PORT,user=user,password=password,
       database=db,connect_timeout=8,read_timeout=8,write_timeout=8,autocommit=True)

def sql_preflight(allow_initialized):
    check("source_sha_present",len(SHA)==40 and all(c in "0123456789abcdef" for c in SHA.lower()))
    check("single_original_attempt",os.environ.get("GITHUB_RUN_ATTEMPT")=="1")
    check("expected_private_sql_host",bool(HOST) and HOST.lower() not in
          ("localhost","127.0.0.1","0.0.0.0"))
    check("expected_native_bd_1_3_1","1.3.1" in run([BD,"--version"],cwd=ROOT.parent).stdout)
    with conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT DOLT_VERSION()")
            vers=str(cur.fetchone()[0])
            check("dolt_primary_2_2_0",vers.startswith("2.2.0"),vers)
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s",(DB,))
            count=int(cur.fetchone()[0])
            check("dedicated_database_freshness",count==0 if not allow_initialized else count>0,
                  "tables="+str(count))
            cur.execute("SELECT CURRENT_USER()")
            identity=str(cur.fetchone()[0])
            check("not_root_sql_account",identity.split("@")[0]==USER,identity.split("@")[0])
    try:
        x=conn(password="THIS_WRONG_PASSWORD_MUST_FAIL_TS047");x.close()
        invalid_denied=False
    except pymysql.err.OperationalError:
        invalid_denied=True
    check("invalid_sql_password_denied",invalid_denied)
    check("no_credential_written_to_receipt",PWD not in json.dumps(R) and RO_PWD not in json.dumps(R))
    return

def prepare_fresh():
    check("fresh_new_runner_workdir",not ROOT.exists())
    PROJ.mkdir(parents=True)
    (ROOT/"home").mkdir()
    run(["git","init","-q"],cwd=PROJ)
    check("runner_has_no_git_remote",not run(["git","remote"]).stdout.strip())
    check("runner_has_no_kernel",not (PROJ/"state-kernel").exists())
    check("no_initial_beads_local",not (PROJ/".beads").exists())

def load_meta():
    path=pathlib.Path(META_SOURCE).resolve()
    check("meta_artifact_present",path.is_file())
    with tarfile.open(path,"r:gz") as tf:
        names=tf.getnames()
        allow={".beads/config.yaml",".beads/metadata.json"}
        check("only_portable_beads_metadata",set(names)==allow,sorted(names))
        check("meta_no_symlinks",all(m.isfile() and not m.issym() for m in tf.getmembers()))
        tf.extractall(PROJ,filter="data")
    check("beads_metadata_restored",all((PROJ/n).is_file() for n in
                                       (".beads/config.yaml",".beads/metadata.json")))
    check("no_shadow_database",not (PROJ/".beads"/"dolt").exists()
          and not (PROJ/".beads"/"embeddeddolt").exists())

def bootstrap():
    prepare_fresh()
    sql_preflight(False)
    run([BD,"init","--server","--database",DB,"--quiet","--stealth",
         "--skip-agents","--skip-hooks","--non-interactive"])
    check("server_mode_metadata",(PROJ/".beads"/"metadata.json").is_file())
    check("beads_native_store_remote_only",
          not (PROJ/".beads"/"embeddeddolt").exists()
          and not (PROJ/".beads"/"dolt").exists())
    check("fresh_native_issues_empty",rows(native("list","--all"))==[])
    for name in ("preflight","alpha","beta","join","parent"):
        run([BD,"create","TS047 "+name,"--id",PFX+"-"+name,
             "--force","--type","task","--description","TS047 isolated native SQL experiment Product NONE"])
    for child,dep in (("alpha","preflight"),("beta","preflight"),
                      ("join","alpha"),("join","beta"),("parent","join")):
        run([BD,"dep","add",PFX+"-"+child,PFX+"-"+dep])
    check("initial_preflight_only",ready()==[PFX+"-preflight"])
    run([BD,"close",PFX+"-preflight"])
    check("children_ready",ready()==[PFX+"-alpha",PFX+"-beta"])
    original=ORIGINAL/"META047.tar.gz"
    ORIGINAL.mkdir(parents=True,exist_ok=True)
    with tarfile.open(original,"w:gz") as tf:
        for name in (".beads/config.yaml",".beads/metadata.json"):
            path=PROJ/name
            check("required_metadata_"+name.replace("/","_"),path.is_file())
            tf.add(path,arcname=name,recursive=False)
    R["portable_metadata_sha256"]=hashlib.sha256(original.read_bytes()).hexdigest()
    R["status"]="PASS_REMOTE_SQL_INITIALIZED_ON_NOTEBOOK"
    save()
    print("TS047_BOOTSTRAP=PASS;no_kernel=1;native_server=NOTEBOOK;Product=NONE")

def worker():
    check("worker_role",ROLE in ("alpha","beta"))
    prepare_fresh()
    load_meta()
    sql_preflight(True)
    check("both_children_unclosed",show(ROLE)["status"] in ("open","in_progress"))
    run([BD,"update",PFX+"-"+ROLE,"--status","in_progress"])
    check("own_child_claimed",show(ROLE)["status"]=="in_progress")
    run([BD,"close",PFX+"-"+ROLE])
    check("own_child_closed",show(ROLE)["status"]=="closed")
    check("native_history",len(rows(native("history",PFX+"-"+ROLE)))>=2)
    check("no_local_data_created",not (PROJ/".beads"/"dolt").exists()
          and not (PROJ/".beads"/"embeddeddolt").exists())
    R["completed_child"]=PFX+"-"+ROLE
    R["status"]="PASS_INDEPENDENT_NATIVE_CLIENT_SHARED_SQL"
    save()
    print("TS047_WORKER_"+ROLE.upper()+"=PASS;server=NOTEBOOK;Product=NONE")

def join():
    prepare_fresh()
    load_meta()
    sql_preflight(True)
    originals=pathlib.Path(os.environ["TS047_WORKER_RECEIPTS"]).resolve()
    receives={}
    for role in ("alpha","beta"):
        f=originals/role/("RESULT047_"+role.upper()+".json")
        check("original_"+role+"_receipt_exists",f.is_file())
        z=json.loads(f.read_text(encoding="utf8"))
        check("original_"+role+"_identity",
              z["attempt"]=="TS-BEADS-047-"+role.upper()+"-ATTEMPT-001"
              and z["subject_sha"]==SHA and z["run_id"]==RUN
              and z["role"]==role and z["run_attempt"]=="1"
              and z["status"]=="PASS_INDEPENDENT_NATIVE_CLIENT_SHARED_SQL")
        check("original_"+role+"_endpoint",z["host_fingerprint"]==HOST_FINGERPRINT)
        receives[role]=z
    check("two_distinct_runner_hosts",
          receives["alpha"]["runner_machine_fingerprint"]!=
          receives["beta"]["runner_machine_fingerprint"])
    check("children_closed",all(show(x)["status"]=="closed" for x in ("alpha","beta")))
    check("only_join_ready",ready()==[PFX+"-join"])
    run([BD,"close",PFX+"-join"])
    check("only_parent_ready",ready()==[PFX+"-parent"])
    run([BD,"close",PFX+"-parent"])
    check("all_closed",all(show(x)["status"]=="closed"
          for x in ("preflight","alpha","beta","join","parent")))
    check("no_ready",ready()==[])
    with conn(user="ts047_reader",password=RO_PWD) as c:
        with c.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM issues")
            check("read_only_sql_sees_native_issues",int(cur.fetchone()[0])==5)
            try:
                cur.execute("UPDATE issues SET title=title WHERE 1=0")
                write_denied=False
            except pymysql.MySQLError:
                write_denied=True
            check("sql_reader_update_denied",write_denied)
    check("final_no_local_shadow",not (PROJ/".beads"/"dolt").exists()
          and not (PROJ/".beads"/"embeddeddolt").exists())
    R["independent_runner_machines"]=2
    R["original_worker_attempts"]=[receives[x]["attempt"] for x in ("alpha","beta")]
    R["status"]="PASS_TWO_INDEPENDENT_HOSTS_NOTEBOOK_LIVE_SQL_WITH_LIMITATIONS"
    R["limitations"]=["Only live shared SQL; off-host native backup/failover is a separate gate.",
         "No real provider in-flight UNKNOWN or notebook physical loss tested.",
         "Privileged host SQL administrator remains trusted; no Product changes."]
    save()
    print("TS047_JOIN="+R["status"]+";host_count=2;SQL_SHARED=YES;Product=NONE")

if __name__=="__main__":
    try:
        check("valid_role",ROLE in ("bootstrap","alpha","beta","join"))
        if ROLE=="bootstrap":bootstrap()
        elif ROLE in ("alpha","beta"):worker()
        else:join()
    except BaseException as e:
        R["status"]="FAIL_CLOSED_ORIGINAL"
        R["error_type"]=type(e).__name__
        msg=str(e)
        for secret in (PWD,RO_PWD,HOST):
            if secret:msg=msg.replace(secret,"[REDACTED]")
        R["error"]=msg[:320]
        save()
        raise
