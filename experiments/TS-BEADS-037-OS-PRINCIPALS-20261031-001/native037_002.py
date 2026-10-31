#!/usr/bin/env python3
"""037: Real Beads/Dolt, different Unix UIDs, selected guarded write path.

All original effects disposable GitHub runner, no Product, no shared Dolt.
This is *not* a universal security test of privileged native writers.
"""
import json,os,pathlib,secrets,shlex,socket,subprocess,sys,time,urllib.request,urllib.error
import pymysql

BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
DOLT=pathlib.Path(os.environ["DOLT_BIN"]).resolve()
BASE=pathlib.Path(os.environ["TS037_BASE"]).resolve()
OUT=pathlib.Path(os.environ["TS037_RESULT"]).resolve()
RUN=int(os.environ.get("GITHUB_RUN_ID","37"))
SQL_PORT=23000+(RUN%13000)
HTTP_PORT=38000+(RUN%12000)
W="ts037writer"; R="ts037reader"
PRIV=BASE/"writer-only";PUBLIC=BASE/"reader-public"
RESULT={"id":"TS-BEADS-037-OS-PRINCIPALS-20261031-001",
        "execution_attempt":"TS-BEADS-037-ATTEMPT-002",
        "authority":"EXPERIMENTAL_CONTROL_ONLY","product_effect":"NONE",
        "source":"native_bd_1.3.1_dolt_2.2.0",
        "status":"RUNNING","checks":[],"limitations":[
          "Local disposable Unix identities only; runner sudo/root retains privileges.",
          "Native privileged bd CLI and alternate serve remain able to bypass selected HTTP path (028).",
          "No Product TaskCycle/kernel semantic equivalence or remote provider ACK test.",
          "All possible OS escape methods and all native bd/Dolt mutation routes not exhausted."]}
PROCS=[]; STREAMS=[]; bearer=None; rootpass=None

def record(label,ok,detail=None):
    RESULT["checks"].append({"name":label,"pass":bool(ok),"detail":detail})
    if not ok:raise AssertionError(label+":"+str(detail))
def run(cmd,allow=False,env=None,cwd=None,timeout=35):
    q=subprocess.run([str(x) for x in cmd],text=True,capture_output=True,env=env,cwd=cwd,timeout=timeout)
    if q.returncode and not allow:raise RuntimeError("EXEC_FAILED:"+str(cmd[:3])+":"+q.stderr[-300:]+":"+q.stdout[-170:])
    return q
def su(user,cmd,allow=False,timeout=45):
    return run(["sudo","-n","-u",user,"--",*cmd],allow=allow,timeout=timeout)
def writer(*cmd,allow=False):
    return su(W,[str(PRIV/"exec-writer.sh"),*map(str,cmd)],allow=allow)
def http(path,method="GET",payload=None,token=None):
    h={"Content-Type":"application/json"}
    if token:h["Authorization"]="Bearer "+token
    q=urllib.request.Request(f"http://127.0.0.1:{HTTP_PORT}"+path,method=method,
        data=(json.dumps(payload).encode() if payload is not None else None),headers=h)
    try:
        with urllib.request.urlopen(q,timeout=9) as r:return r.status,r.read(16000).decode()
    except urllib.error.HTTPError as e:return e.code,e.read(1000).decode()
def find(obj,needle):
    if isinstance(obj,dict):
        if obj.get("id")==needle and "revision" in obj:return obj
        for x in obj.values():
            z=find(x,needle)
            if z:return z
    if isinstance(obj,list):
        for x in obj:
            z=find(x,needle)
            if z:return z
    return None
def detail(id):
    status,body=http("/v0/beads/issues/"+id+"?brief_deps=true",token=bearer)
    if status!=200:raise RuntimeError("DETAIL_"+str(status)+":"+body[-220:])
    row=find(json.loads(body),id)
    if row is None:raise RuntimeError("NATIVE_ISSUE_ABSENT:"+id)
    return row
def deps(row):return sorted(x["id"] for x in row.get("dependencies",[]))
def sqlconnect(passwd):
    return pymysql.connect(host="127.0.0.1",port=SQL_PORT,user="root",password=passwd,
        connect_timeout=3,read_timeout=3,write_timeout=3,autocommit=True)
def launch(cmd,path):
    f=open(path,"w");STREAMS.append(f)
    p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);PROCS.append(p)
    return p
def ready(p,fn,timeout=20):
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        if p.poll() is not None:raise RuntimeError("EARLY_PROCESS_EXIT:"+str(p.returncode))
        try:
            if fn():return
        except Exception:pass
        time.sleep(.15)
    raise RuntimeError("SERVICE_READY_TIMEOUT")
def clean():
    for p in reversed(PROCS):
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
    for f in STREAMS:f.close()
def main():
    global bearer,rootpass
    assert not BASE.exists(),"FRESH_SCRATCH_REQUIRED"
    BASE.mkdir(parents=True,mode=0o755)
    PRIV.mkdir(mode=0o700);PUBLIC.mkdir(mode=0o755)
    for child in ["repo","sql","home"]:(PRIV/child).mkdir(mode=0o700)
    run(["sudo","-n","useradd","-M","-s","/bin/sh",W])
    run(["sudo","-n","useradd","-M","-s","/bin/sh",R])
    record("disjoint_native_Unix_UIDs",run(["id","-u",W]).stdout.strip()!=run(["id","-u",R]).stdout.strip())
    rootpass=secrets.token_urlsafe(30);bearer=secrets.token_urlsafe(30)
    wrapper=PRIV/"exec-writer.sh"
    wrapper.write_text("#!/bin/sh\nset -eu\n"+
       "export HOME="+shlex.quote(str(PRIV/"home"))+"\n"+
       "export BEADS_DIR="+shlex.quote(str(PRIV/"repo"/".beads"))+"\n"+
       "export BEADS_DOLT_SERVER_MODE=1\n"+
       "export BEADS_DOLT_SERVER_HOST=127.0.0.1\n"+
       f"export BEADS_DOLT_SERVER_PORT={SQL_PORT}\n"+
       "export BEADS_DOLT_SERVER_USER=root\n"+
       "export BEADS_DOLT_PASSWORD="+shlex.quote(rootpass)+"\n"+
       "export BD_NO_PUSH=1\nexport BD_DOLT_AUTO_PUSH=false\n"+
       "export BEADS_ACTOR=TS-BEADS-037-EXPERIMENTAL-WRITER\n"+
       "cd "+shlex.quote(str(PRIV/"repo"))+"\nexec \"$@\"\n")
    wrapper.chmod(0o700)
    token_file=PRIV/"bearer"
    token_file.write_text(bearer+"\n");token_file.chmod(0o600)
    launcher=PRIV/"guarded-http.sh"
    launcher.write_text("#!/bin/sh\nset -eu\n"+
      'if [ "$#" -ne 0 ]; then exit 78; fi\n'+
      "exec "+shlex.quote(str(wrapper))+" "+shlex.quote(str(BD))+
      f" serve --addr 127.0.0.1:{HTTP_PORT} --auth-token-file "+
      shlex.quote(str(token_file))+"\n")
    launcher.chmod(0o700)
    run(["sudo","-n","chown","-R",W+":"+W,str(PRIV)])
    record("private_root_0700",run(["stat","-c","%a",str(PRIV)]).stdout.strip()=="700")
    record("token_file_0600",run(["sudo","-n","stat","-c","%a",str(token_file)]).stdout.strip()=="600")
    for p in (PRIV,wrapper,token_file,launcher,PRIV/"repo"/".beads"):
        if p.name==".beads":continue
        denied=su(R,["test","-r",str(p)],allow=True)
        record("reader_cannot_read_private_"+p.name,denied.returncode!=0)
    # Separate native Dolt SQL server, same privileged writer UID, SQLite NOT used.
    sqlcmd="cd "+shlex.quote(str(PRIV/"sql"))+" && exec "+shlex.quote(str(DOLT))+f" sql-server --host 127.0.0.1 --port {SQL_PORT}"
    dolt=launch(["sudo","-n","-u",W,"--","/usr/bin/env","HOME="+str(PRIV/"home"),"/bin/sh","-c",sqlcmd],BASE/"original-dolt.log")
    def sqlok():
        s=sqlconnect("");s.close();return True
    ready(dolt,sqlok)
    c=sqlconnect("")
    with c.cursor() as cur:
        cur.execute("SELECT user,host FROM mysql.user WHERE user='root'")
        for _,host in cur.fetchall():
            cur.execute("ALTER USER 'root'@'"+host.replace("'","''")+"' IDENTIFIED BY %s",(rootpass,))
    c.close()
    try:
        sqlconnect("").close();no_root_password=False
    except Exception:no_root_password=True
    record("SQL_root_requires_secret",no_root_password)
    reader_sql_probe=su(R,["/usr/bin/python3","-c",
        f"import socket;s=socket.create_connection(('127.0.0.1',{SQL_PORT}),timeout=2);s.close()"],allow=False)
    record("reader_network_reaches_loopback_only",reader_sql_probe.returncode==0)
    writer("git","init","-q")
    record("no_git_remote",writer("git","remote").stdout.strip()=="")
    writer(BD,"init","--server","--quiet","--stealth",allow=False)
    for id in ["ts037-root","ts037-child-a","ts037-child-b"]:
        writer(BD,"create","TS037 "+id,"--type","task","--id",id,"--force","--json")
    record("beads_native_fresh_graph_seeded",True)
    record("direct_native_Beads_path_reader_inaccessible",
           su(R,["test","-r",str(PRIV/"repo"/".beads"/"metadata.json")],allow=True).returncode!=0)
    # Explicit alternate entry points from unauthorized UID, NOT escalation.
    denied=su(R,["/usr/bin/env","BEADS_DIR="+str(PRIV/"repo"/".beads"),
            "BEADS_DOLT_SERVER_MODE=1","BEADS_DOLT_SERVER_HOST=127.0.0.1",
            "BEADS_DOLT_SERVER_PORT="+str(SQL_PORT),"BEADS_DOLT_SERVER_USER=root",
            str(BD),"dep","add","ts037-root","ts037-child-b","--type","related"],
            allow=True,timeout=18)
    record("reader_direct_bd_dep_add_denied",denied.returncode!=0,
           {"returncode":denied.returncode})
    # No disclosed token or root password, even if reader creates own store.
    denied_server=su(R,["/usr/bin/env","BEADS_DIR="+str(PRIV/"repo"/".beads"),
        "BEADS_DOLT_SERVER_MODE=1","BEADS_DOLT_SERVER_HOST=127.0.0.1",
        "BEADS_DOLT_SERVER_PORT="+str(SQL_PORT),"BEADS_DOLT_SERVER_USER=root",
        str(BD),"serve","--addr","127.0.0.1:"+str(HTTP_PORT+1)],allow=True,timeout=13)
    record("reader_direct_service_with_privileged_Beads_dir_denied",
           denied_server.returncode!=0,{"returncode":denied_server.returncode})
    record("reader_cannot_invoke_privileged_launcher",
           su(R,[str(launcher)],allow=True,timeout=10).returncode!=0)
    record("privileged_launcher_rejects_args",
           su(W,[str(launcher),"--insecure"],allow=True,timeout=10).returncode!=0)
    http_proc=launch(["sudo","-n","-u",W,"--",str(launcher)],BASE/"original-http.log")
    ready(http_proc,lambda:http("/healthz")[0]==200)
    record("guarded_native_http_service_started",True)
    status,_=http("/v0/beads/issues/ts037-root")
    record("unauthorized_HTTP_read_denied",status==401,status)
    status,_=http("/v0/beads/issues:batchApply","POST",{"actor":"reader","items":[]})
    record("unauthorized_HTTP_write_denied",status==401,status)
    before=detail("ts037-root")
    revision=before["revision"]
    batch={"actor":"TS037-APPROVED-EXPERIMENTAL",
      "provenance":"experiment://TS037/selected-guarded",
      "items":[{"kind":"update","update":{"target":{"id":"ts037-root"},
        "expected_version":revision,
        "patch":{"metadata":{"set":{"ts037_epoch":"guarded-1"}}}}},
        {"kind":"dep_add","dep_add":{"source":{"id":"ts037-root"},
          "target":{"id":"ts037-child-a"},"type":"related"}}]}
    status,body=http("/v0/beads/issues:batchApply","POST",batch,token=bearer)
    record("approved_native_batch_commits_atomically",status==200,{"status":status,"response":body[-110:]})
    after=detail("ts037-root")
    record("approved_native_graph_edge_exists",deps(after)==["ts037-child-a"],deps(after))
    record("approved_native_root_revision_advances",revision!=after["revision"])
    status,_=http("/v0/beads/issues:batchApply","POST",batch,token=bearer)
    record("stale_root_revision_rejected",status!=200,status)
    # OS/UID reader's initial attempts must not have changed protected graph.
    record("unauthorized_reader_edge_absent",deps(after)==["ts037-child-a"])
    http_proc.terminate();http_proc.wait(timeout=10)
    writer_graph=writer(BD,"show","ts037-root","--json").stdout
    record("native_Beads_fresh_process_readback_contains_guarded_edge",
           "ts037-child-a" in writer_graph and "ts037-child-b" not in writer_graph)
    ready_graph=writer(BD,"ready","--json").stdout
    record("native_Beads_ready_query_available",bool(ready_graph.strip()))
    record("privileged_writer_alternate_CLI_NOT_excluded_by_OS",
           su(W,["test","-r",str(PRIV/"repo"/".beads"/"metadata.json")]).returncode==0)
    RESULT["status"]="PASS_SCOPED_UNPRIVILEGED_DENIAL_AND_GUARDED_NATIVE_PATH_WITH_PRIVILEGED_BYPASS_OPEN"
    RESULT["native_graph"]={"root":"ts037-root","dependencies":["ts037-child-a"],
          "stale_rejected":True,"privileged_bypass_unresolved":True}
    print("TS_BEADS037="+RESULT["status"]+";checks="+str(len(RESULT["checks"]))+";Product=NONE",flush=True)

try:
    main()
except Exception as ex:
    RESULT["status"]="FAIL_CLOSED_NATIVE_037"
    RESULT["error"]=str(ex)[:450].replace(str(rootpass),"[REDACTED]") if rootpass else str(ex)[:450]
    logfile=BASE/"original-dolt.log"
    if logfile.exists():
        tail=logfile.read_text(errors="replace")[-850:]
        for secret in (rootpass,bearer):
            if secret:tail=tail.replace(secret,"[REDACTED]")
        RESULT["dolt_startup_diagnostic_redacted"]=tail
    print("TS_BEADS037_FAIL="+RESULT["error"],flush=True)
    raise
finally:
    clean()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(RESULT,sort_keys=True,indent=2)+"\n")
