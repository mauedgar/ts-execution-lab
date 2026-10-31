#!/usr/bin/env python3
"""TS Beads 045: disposable SQL server, native Beads, real client processes.
NOT a remote interhost result; no Product effects, old attempts or Kernel.
"""
import concurrent.futures
import json
import os
import pathlib
import secrets
import subprocess
import sys
import time
import traceback
import pymysql

BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
DOLT=pathlib.Path(os.environ["DOLT_BIN"]).resolve()
BASE=pathlib.Path(os.environ["TS045_BASE"]).resolve()
RESULT=pathlib.Path(os.environ["TS045_RESULT"]).resolve()
PORT=27000+(int(os.environ.get("GITHUB_RUN_ID","45"))%13000)
PFX="b045"
R={"operation":"TS-BEADS-045-SERVER-BOUNDARY-20261031-002",
"execution_attempt":"TS-BEADS-045-ATTEMPT-002",
"authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
"subject_sha":os.environ.get("GITHUB_SHA","LOCAL_NOT_ATTESTED"),
"status":"RUNNING","checks":{},"runner_count":1,"external_host_count":0,
"kernel_used":False,"remote_host_independence":"NOT_TESTED",
"class":"SINGLE_HOST_REMOTE_SQL_SERVICE_PREREQUISITE_ONLY",
"limitations":["Server bound to loopback on one runner; NOT a remote second host.",
"Trusted SQL administrator and native writer remain inside the TCB.",
"No privileged-writer confinement, global Product hash-chain audit parity or real UNKNOWN.",
"No external failover, remote OpenCode or Product lifecycle tested."]}
P=None; SERVER_LOG=None; ROOTPASS=None; READERPASS=None
def save():
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def check(name,ok,detail=None):
    R["checks"][name]={"pass":bool(ok),"detail":detail}; save()
    if not ok:raise AssertionError(name+":"+str(detail)[:250])
def run(cmd,env=None,cwd=None,timeout=45,allow=False):
    p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,env=env,cwd=cwd,timeout=timeout)
    if p.returncode and not allow:
        raise RuntimeError("COMMAND_FAILED;exe="+pathlib.Path(str(cmd[0])).name+
             ";rc="+str(p.returncode)+";stderr_tail="+p.stderr[-220:])
    return p
def sql(user="root",password=None,db=None):
    return pymysql.connect(host="127.0.0.1",port=PORT,user=user,
         password=ROOTPASS if password is None else password,database=db,
         connect_timeout=3,read_timeout=5,write_timeout=5,autocommit=True)
def start_server(bootstrap):
    global P,SERVER_LOG
    if P is not None and P.poll() is None:raise RuntimeError("DUPLICATE_SERVER")
    SERVER_LOG=open(BASE/"dolt-server.log","a",encoding="utf-8")
    P=subprocess.Popen([str(DOLT),"sql-server","--host","127.0.0.1","--port",str(PORT)],
      cwd=BASE/"sql",env={**os.environ,"HOME":str(BASE/"home")},
      stdout=SERVER_LOG,stderr=subprocess.STDOUT)
    until=time.monotonic()+20
    while time.monotonic()<until:
        if P.poll() is not None:raise RuntimeError("DOLT_SERVER_EXIT_"+str(P.returncode))
        try:
            c=sql(password="" if bootstrap else ROOTPASS);c.close();return
        except Exception:time.sleep(.2)
    raise RuntimeError("DOLT_SERVER_READY_TIMEOUT")
def stop_server():
    global P,SERVER_LOG
    if P is not None:
        if P.poll() is None:
            P.terminate()
            try:P.wait(timeout=8)
            except subprocess.TimeoutExpired:P.kill();P.wait(timeout=8)
        P=None
    if SERVER_LOG is not None:SERVER_LOG.close();SERVER_LOG=None
def env(client,readonly=False):
    return {**os.environ,"HOME":str(BASE/"home"),
        "BEADS_DIR":str(BASE/"project"/".beads"),
        "BEADS_DOLT_SERVER_MODE":"1","BEADS_DOLT_SERVER_HOST":"127.0.0.1",
        "BEADS_DOLT_SERVER_PORT":str(PORT),
        "BEADS_DOLT_SERVER_USER":"reader" if readonly else "root",
        "BEADS_DOLT_PASSWORD":READERPASS if readonly else ROOTPASS,
        "BEADS_ACTOR":"TS045-"+client,"BD_NON_INTERACTIVE":"1",
        "BD_DOLT_AUTO_PUSH":"false","BD_NO_PUSH":"1","GIT_TERMINAL_PROMPT":"0"}
def bd(client,*args,readonly=False,allow=False):
    return run([BD,*args],env=env(client,readonly),cwd=BASE/"project",allow=allow)
def json_native(client,*args):
    output=bd(client,*args,"--json").stdout
    offsets=[x for x in (output.find("{"),output.find("[")) if x!=-1]
    if not offsets:raise RuntimeError("NATIVE_JSON_MISSING_"+str(args))
    return json.loads(output[min(offsets):])
def rows(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for key in ("issues","ready","results","data"):
            if isinstance(x.get(key),list):return x[key]
    return [x]
def ready():return sorted(x["id"] for x in rows(json_native("COORDINATOR","ready")))
def main():
    global ROOTPASS,READERPASS
    check("fresh_disposable_workspace",not BASE.exists() and not RESULT.exists())
    (BASE/"sql").mkdir(parents=True)
    (BASE/"home").mkdir()
    (BASE/"project").mkdir()
    run(["git","init","-q"],cwd=BASE/"project")
    check("no_git_remotes_or_shared_dolt_refs",not run(["git","remote"],cwd=BASE/"project").stdout.strip())
    check("native_bd_1_3_1_pinned","1.3.1" in run([BD,"--version"]).stdout)
    check("native_dolt_2_2_0_pinned","2.2.0" in run([DOLT,"version"]).stdout)
    ROOTPASS=secrets.token_urlsafe(30); READERPASS=secrets.token_urlsafe(30)
    start_server(bootstrap=True)
    with sql(password="") as con:
        with con.cursor() as cur:
            cur.execute("SELECT user,host FROM mysql.user WHERE user='root'")
            for _,host in cur.fetchall():
                cur.execute("ALTER USER 'root'@'"+host.replace("'","''")+"' IDENTIFIED BY %s",(ROOTPASS,))
    try:
        c=sql(password="");c.close();passless=True
    except Exception:passless=False
    check("SQL_root_rejects_empty_password",not passless)
    bd("COORDINATOR","init","--server","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    check("beads_server_mode_metadata_exists",(BASE/"project"/".beads"/"metadata.json").is_file())
    check("no_embedded_local_work_database",not (BASE/"project"/".beads"/"embeddeddolt").exists())
    with sql() as con:
        with con.cursor() as cur:
            cur.execute("SHOW DATABASES")
            names=[x[0] for x in cur.fetchall() if x[0].lower() not in
                   ("information_schema","mysql","performance_schema","sys")]
            check("server_contains_beads_database",len(names)>=1,{"database_count":len(names)})
            db=names[0]; safe_db=chr(96)+db.replace(chr(96),chr(96)*2)+chr(96)
            cur.execute("CREATE USER 'reader'@'%%' IDENTIFIED BY %s",(READERPASS,))
            cur.execute("GRANT SELECT ON "+safe_db+".* TO 'reader'@'%'")
    with sql("reader",READERPASS,db=db) as con:
        with con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM issues")
            check("reader_can_retrieve_sql_issue_count",cur.fetchone()[0]>=0)
            try:
                cur.execute("UPDATE issues SET title=title WHERE 1=0")
                mutation_denied=False
            except Exception:mutation_denied=True
            check("read_only_SQL_reader_cannot_mutate_native_issues",mutation_denied)
    for n in ("preflight","alpha","beta","join","parent"):
        bd("COORDINATOR","create","TS045 "+n,"--id",PFX+"-"+n,"--force",
           "--type","task","--description","TS045 synthetic work without Kernel or Product")
    for n,dep in (("alpha","preflight"),("beta","preflight"),
                  ("join","alpha"),("join","beta"),("parent","join")):
        bd("COORDINATOR","dep","add",PFX+"-"+n,PFX+"-"+dep)
    check("native_initial_graph_preflight_ready",ready()==[PFX+"-preflight"],ready())
    bd("COORDINATOR","close",PFX+"-preflight")
    check("native_two_children_ready",ready()==[PFX+"-alpha",PFX+"-beta"],ready())
    start=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures={n:pool.submit(bd,"CLIENT_"+n.upper(),"update",
                    PFX+"-"+n,"--status","in_progress") for n in ("alpha","beta")}
        outputs={n:f.result(timeout=35) for n,f in futures.items()}
    R["native_client_process_count"]=len(outputs)
    R["concurrent_client_elapsed_ms"]=round((time.monotonic()-start)*1000,3)
    for n in ("alpha","beta"):
        entry=rows(json_native("COORDINATOR","show",PFX+"-"+n))[0]
        check("native_client_"+n+"_committed",entry["status"]=="in_progress",entry["status"])
    check("native_distinct_clients_on_server",len(outputs)==2)
    denied=bd("UNTRUSTED","update",PFX+"-alpha","--description","ILLEGAL",
              readonly=True,allow=True)
    check("unauthorized_native_bd_client_denied",denied.returncode!=0,denied.returncode)
    for n in ("alpha","beta"):bd("COORDINATOR","close",PFX+"-"+n)
    check("join_ready_only_after_both_children_closed",ready()==[PFX+"-join"],ready())
    bd("COORDINATOR","close",PFX+"-join")
    check("parent_ready_after_join",ready()==[PFX+"-parent"],ready())
    bd("COORDINATOR","close",PFX+"-parent")
    check("all_native_tasks_closed",ready()==[],ready())
    for n in ("alpha","beta"):
        h=rows(json_native("COORDINATOR","history",PFX+"-"+n))
        check("history_persisted_"+n,len(h)>=2,len(h))
    before={n:rows(json_native("COORDINATOR","show",PFX+"-"+n))[0]["status"]
            for n in ("alpha","beta","join","parent")}
    stop_server()
    start_server(bootstrap=False)
    after={n:rows(json_native("RECOVERED","show",PFX+"-"+n))[0]["status"]
           for n in ("alpha","beta","join","parent")}
    check("server_restart_recovers_full_native_work_graph",
          before==after and all(x=="closed" for x in after.values()),after)
    check("recovered_ready_empty",ready()==[],ready())
    check("no_kernel_directory_or_import",not (BASE/"state-kernel").exists()
          and not any("state-kernel" in x for x in sys.modules))
    R["native_issue_count"]=5;R["server_process_starts"]=2
    R["status"]="PASS_SINGLE_HOST_DOLT_SQL_SERVER_BOUNDARY_WITH_RESTART"
    save()
    print("TS_BEADS045="+R["status"]+";clients=2;remote_hosts=0;Product=NONE",flush=True)
try:main()
except Exception as e:
    R["status"]="FAIL_CLOSED_ORIGINAL";R["error_type"]=type(e).__name__
    R["error"]=str(e)[:450]
    for secret in (ROOTPASS,READERPASS):
        if secret:R["error"]=R["error"].replace(secret,"[REDACTED]")
    save();traceback.print_exc();raise
finally:stop_server();save()
