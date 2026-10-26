#!/usr/bin/env python3
"""026 nonProduct native Beads auth, same-UID bypass, route coverage, rotation and restart.
No public tokens, credentials, Product writes or shared Dolt changes.
"""
from __future__ import annotations
import json,os,pathlib,secrets,subprocess,sys,time,urllib.request,urllib.error,shutil
import pymysql
from hashlib import sha256
from collections import Counter
if len(sys.argv)>1 and sys.argv[1]=="same_uid":
    # Independently started client running with *same effective UID* as bd serve.
    # It gets NO SQL root credential, only a token filename: same UID can read it.
    token_file,port,source,target=sys.argv[2:]
    token=pathlib.Path(token_file).read_text().strip()
    body=json.dumps({"actor":"TS026-SAME-UID-ADVERSARY","provenance":"test://ts026/same-uid",
       "items":[{"kind":"dep_add","dep_add":{"source":{"id":source},"target":{"id":target},"type":"related"}}]}).encode()
    req=urllib.request.Request(f"http://127.0.0.1:{port}/v0/beads/issues:batchApply",
       data=body,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=7) as r:
            print(json.dumps({"status":r.status,"success":200<=r.status<300}))
    except urllib.error.HTTPError as e:
        print(json.dumps({"status":e.code,"success":False}))
    sys.exit(0)

BIN=pathlib.Path(os.environ["BD_BIN"]).resolve()
DOLT=pathlib.Path(os.environ["DOLT_BIN"]).resolve()
ROOT=pathlib.Path(os.environ["LAB_ROOT"]).resolve()
OUTPUT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
if ROOT.exists():raise RuntimeError("DISPOSABLE_PATH_ALREADY_EXISTS")
ROOT.mkdir(mode=0o700,parents=True)
RUN_ID=int(os.environ.get("GITHUB_RUN_ID","2600"))
SQL_PORT=27000+RUN_ID%13000
HTTP_PORT=41000+RUN_ID%12000
doc={"id":"TS-BEADS-026-NATIVE-AUTH-SAME-UID-AND-RECOVERY-20261026-001",
 "state":"RUNNING","Product_effect":"NONE","shared_Dolt_effect":"NONE",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","checks":[],"findings":[],"routes":[],
 "scope":"native Beads v1.3.1 token auth + same-UID separate process + restart + token loss"}
def check(name,value):
    if not value:raise AssertionError(name)
    doc["checks"].append(name)
def run(args,*,cwd=None,env=None,timeout=45,allow_failure=False):
    p=subprocess.run([str(x) for x in args],cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
    if p.returncode and not allow_failure:
        raise RuntimeError("COMMAND_FAILED:"+str(args[:3])+":"+p.stderr[-700:])
    return p
def sql(user,password):
    return pymysql.connect(host="127.0.0.1",port=SQL_PORT,user=user,password=password,
    connect_timeout=3,read_timeout=4,write_timeout=4,autocommit=True)
server=None;dolt=None;streams=[]
def stop_server():
    global server
    if server:
        if server.poll() is None:
            server.terminate()
            try:server.wait(timeout=8)
            except subprocess.TimeoutExpired:server.kill();server.wait(timeout=5)
        server=None
def http(method,path,body=None,token=None,port=HTTP_PORT):
    headers={"Content-Type":"application/json"}
    if token:headers["Authorization"]="Bearer "+token
    args={"method":method,"headers":headers}
    if body is not None:args["data"]=json.dumps(body).encode()
    request=urllib.request.Request(f"http://127.0.0.1:{port}{path}",**args)
    try:
        with urllib.request.urlopen(request,timeout=6) as response:
            raw=response.read(1200).decode(errors="replace")
            return response.status,raw
    except urllib.error.HTTPError as e:
        return e.code,e.read(800).decode(errors="replace")
def start_server(env,tokenpath):
    global server
    output=open(ROOT/f"beads-serve-{int(time.time()*1000)}.log","w");streams.append(output)
    server=subprocess.Popen([str(BIN),"serve","--addr",f"127.0.0.1:{HTTP_PORT}",
       "--auth-token-file",str(tokenpath)],cwd=gitroot,env=env,
       stdout=output,stderr=subprocess.STDOUT)
    for _ in range(100):
        if server.poll() is not None:raise RuntimeError("AUTH_NATIVE_SERVER_EXITED")
        try:
            code,_=http("GET","/healthz")
            if code==200:return
        except Exception:time.sleep(.15)
    raise RuntimeError("BEADS_AUTH_SERVICE_NOT_READY")
def detail(id,token):
    status,raw=http("GET","/v0/beads/issues/"+id+"?brief_deps=true",token=token)
    if status!=200:raise RuntimeError("AUTH_DETAIL_BAD_STATUS:"+str(status)+":"+raw[:120])
    v=json.loads(raw)
    def walk(x,d=0):
        if d>7:return None
        if isinstance(x,dict):
            if x.get("id")==id and "revision" in x:return x
            for val in x.values():
                r=walk(val,d+1)
                if r:return r
        if isinstance(x,list):
            for val in x:
                r=walk(val,d+1)
                if r:return r
        return None
    return walk(v)
def dep_ids(x):return sorted(d["id"] for d in x.get("dependencies",[]))
def write_tokens(file,values):
    temp=file.with_name(file.name+".next")
    with open(temp,"x",encoding="utf-8") as fd:
        fd.write("\n".join(values)+"\n")
    temp.chmod(0o600);temp.replace(file)
try:
    check("native_exact_binary_paths",BIN.is_file() and DOLT.is_file())
    gitroot=ROOT/"git";gitroot.mkdir(mode=0o700)
    run(["git","init","-q"],cwd=gitroot)
    check("native_git_has_no_remote",run(["git","remote"],cwd=gitroot).stdout.strip()=="")
    sqlroot=ROOT/"sql-private";sqlroot.mkdir(mode=0o700)
    log=open(ROOT/"dolt-native.log","w");streams.append(log)
    dolt=subprocess.Popen([str(DOLT),"sql-server","--host","127.0.0.1","--port",str(SQL_PORT)],
       cwd=sqlroot,stdout=log,stderr=subprocess.STDOUT)
    for _ in range(100):
        if dolt.poll() is not None:raise RuntimeError("DOLT_SQL_SERVER_EXITED")
        try:
            c=sql("root","");break
        except Exception:time.sleep(.15)
    else:raise RuntimeError("DOLT_BOOTSTRAP_FAILED")
    root_secret=secrets.token_urlsafe(26)
    with c.cursor() as cur:
        cur.execute("SELECT user,host FROM mysql.user WHERE user='root'")
        for user,host in cur.fetchall():
            host_sql=host.replace("'","''")
            cur.execute(f"ALTER USER 'root'@'{host_sql}' IDENTIFIED BY %s",(root_secret,))
    c.close()
    try:sql("root","").close();valid=False
    except Exception:valid=True
    check("native_sql_root_password_required",valid)
    env={**os.environ,"BEADS_DIR":str(gitroot/".beads"),"BEADS_DOLT_SERVER_MODE":"1",
       "BEADS_DOLT_SERVER_HOST":"127.0.0.1","BEADS_DOLT_SERVER_PORT":str(SQL_PORT),
       "BEADS_DOLT_SERVER_USER":"root","BEADS_DOLT_PASSWORD":root_secret,
       "BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false","BEADS_ACTOR":"TS-BEADS-026"}
    run([BIN,"init","--server","--quiet","--stealth"],cwd=gitroot,env=env,timeout=55)
    for id in ["ts026-root","ts026-from-cli","ts026-from-http","ts026-from-guard"]:
        result=run([BIN,"create","TS026 "+id,"--type","task","--id",id,"--force",
          "--metadata",'{"ts026":"BASE"}',"--json"],cwd=gitroot,env=env,timeout=40)
        value=result.stdout.strip();i=min([i for i in (value.find("{"),value.find("[")) if i>=0])
        decoded=json.loads(value[i:]);decoded=decoded[0] if isinstance(decoded,list) else decoded
        check("native_created_"+id,decoded.get("id")==id)
    tokenpath=ROOT/"bearer-tokens.private"
    first=secrets.token_urlsafe(32);second=secrets.token_urlsafe(32)
    write_tokens(tokenpath,[first])
    check("native_token_file_is_private_mode",tokenpath.stat().st_mode&0o777==0o600)
    # Another UID must not access secret even though current same-UID can.
    not_reader=run(["sudo","-n","-u","nobody","--","test","-r",str(tokenpath)],allow_failure=True)
    check("different_UID_cannot_read_token_file",not_reader.returncode!=0)
    check("same_UID_can_read_server_token_secret",tokenpath.read_text().strip()==first)
    start_server(env,tokenpath)
    check("healthz_public_only",http("GET","/healthz")[0]==200)
    protected=[
      ("GET","/v0/beads/context",None),
      ("GET","/v0/beads/issues/ts026-root",None),
      ("POST","/v0/beads/issues:batchApply",{"actor":"TS026-NEGATIVE","items":[]}),
      ("POST","/v0/beads/dependencies:add",{"actor":"TS026-NEGATIVE","edges":[]}),
      ("POST","/v0/beads/issues:claimNext",{"actor":"TS026-NEGATIVE"}),
      ("POST","/v0/beads/issues/ts026-root:casMetadata",{}),
    ]
    for method,path,body in protected:
        denied=http(method,path,body)
        denied_wrong=http(method,path,body,"incorrect-026-token")
        doc["routes"].append({"method":method,"path":path,"no_token":denied[0],"invalid_token":denied_wrong[0]})
        check("native_route_requires_token_"+str(len(doc["routes"])),denied[0]==401 and denied_wrong[0]==401)
    check("valid_bearer_can_read_native_issue",detail("ts026-root",first)["id"]=="ts026-root")
    # DIFFERENT process but same Unix UID as privileged writer, no password passed.
    before=detail("ts026-root",first)
    attacker=run([sys.executable,__file__,"same_uid",tokenpath,HTTP_PORT,"ts026-root","ts026-from-http"],
      cwd=gitroot,env={k:v for k,v in env.items() if k!="BEADS_DOLT_PASSWORD"},timeout=18)
    outcome=json.loads(attacker.stdout)
    after=detail("ts026-root",first)
    check("separate_same_UID_process_can_use_shared_token",outcome["success"] and outcome["status"]==200)
    check("same_UID_native_write_bypasses_causal_root_revision",after["revision"]==before["revision"]
       and "ts026-from-http" in dep_ids(after))
    doc["findings"].append({"name":"SAME_UID_SECRET_CANNOT_ISOLATE_PRIVILEGED_HTTP_WRITER",
      "status":"REPRODUCED","before_revision":before["revision"],"after_revision":after["revision"],
      "attacker_process":"separate process, same effective OS UID; no SQL root password"})
    # Native CLI direct DB access bypasses HTTP protection for privileged identity.
    run([BIN,"dep","add","ts026-root","ts026-from-cli","--type","related"],
      cwd=gitroot,env=env,timeout=40)
    aftercli=detail("ts026-root",first)
    check("privileged_direct_CLI_is_another_write_surface","ts026-from-cli" in dep_ids(aftercli))
    check("direct_CLI_dep_change_does_not_advance_root_revision",aftercli["revision"]==after["revision"])
    # Token rotation uses existing native file watcher; no service restart.
    write_tokens(tokenpath,[first,second])
    time.sleep(1.3)
    check("native_rotation_accepts_second_token",http("GET","/v0/beads/context",token=second)[0]==200)
    write_tokens(tokenpath,[second])
    time.sleep(1.3)
    check("native_revocation_refuses_first_token",http("GET","/v0/beads/context",token=first)[0]==401)
    check("native_rotated_token_still_works",http("GET","/v0/beads/context",token=second)[0]==200)
    # An unreadable / missing file while running keeps last-good credentials
    # per native source, DOES NOT fail closed on existing server.
    tokenpath.rename(ROOT/"token-file-withheld")
    time.sleep(1.4)
    retained=http("GET","/v0/beads/context",token=second)[0]
    doc["findings"].append({"name":"TOKEN_FILE_LOSS_RUNNING_SERVER_LAST_GOOD",
      "native_response":retained,"interpretation":"reload error retains cached last-good credential set; loss is not immediate fail-closed"})
    check("unreadable_file_does_not_immediately_revoke_cached_token",retained==200)
    stop_server()
    # Start with missing token file: should fail startup, rather than serve open.
    nofilelog=open(ROOT/"missing-token-server.log","w");streams.append(nofilelog)
    absent=subprocess.Popen([str(BIN),"serve","--addr",f"127.0.0.1:{HTTP_PORT}","--auth-token-file",str(tokenpath)],
      cwd=gitroot,env=env,stdout=nofilelog,stderr=subprocess.STDOUT)
    try:
        absent.wait(timeout=5)
        failed=absent.returncode!=0
    except subprocess.TimeoutExpired:
        absent.terminate();absent.wait(timeout=5);failed=False
    check("missing_auth_file_prevents_authenticated_server_start",failed)
    (ROOT/"token-file-withheld").replace(tokenpath)
    start_server(env,tokenpath)
    check("server_restart_recovers_auth_using_persisted_second_token",
        http("GET","/v0/beads/context",token=second)[0]==200)
    check("server_restart_rejects_revoked_token",
        http("GET","/v0/beads/context",token=first)[0]==401)
    check("server_restart_still_protects_write_routes",http("POST",
        "/v0/beads/issues:batchApply",{"actor":"TS026","items":[]})[0]==401)
    # Native correct writer with precondition, no user-supplied global journal
    root=detail("ts026-root",second)
    body={"actor":"TS026-COMPETENT-SYNTHETIC","provenance":"test://026/guard",
      "items":[{"kind":"update","update":{"target":{"id":"ts026-root"},
         "expected_version":root["revision"],"patch":{"metadata":{"set":{"ts026_mark":"SCOPED"}}}}},
        {"kind":"dep_add","dep_add":{"source":{"id":"ts026-root"},
         "target":{"id":"ts026-from-guard"},"type":"related"}}]}
    result=http("POST","/v0/beads/issues:batchApply",body,second)
    check("valid_native_bearer_can_execute_atomic_causal_guard",result[0]==200)
    final=detail("ts026-root",second)
    check("guarded_writer_root_revision_advanced_and_edge_exists",
       final["revision"]!=root["revision"] and "ts026-from-guard" in dep_ids(final))
    stale={"actor":"TS026-COMPETENT-SYNTHETIC","provenance":"test://026/stale",
      "items":[{"kind":"update","update":{"target":{"id":"ts026-root"},
        "expected_version":root["revision"],"patch":{"metadata":{"set":{"ts026_mark":"STALE"}}}}}]}
    check("native_legacy_token_refuses_stale_mutation",
       http("POST","/v0/beads/issues:batchApply",stale,second)[0]!=200)
    doc["recovery"]={"native_token_rotation":"PASS","server_restart_secret_survived":"PASS",
       "auth_file_loss_while_running":"CACHED_LAST_GOOD_NOT_IMMEDIATE_REVOKE",
       "missing_file_on_start":"FAIL_CLOSED",
       "auth_per_endpoint":"ALL_SURFACED_TESTED_AUTHENTICATED",
       "same_UID_privileged_token":"NOT_PROTECTED",
       "same_UID_privileged_CLI":"NOT_PROTECTED"}
    doc["status"]="PASS_AUTH_BOUNDARY_WITH_SAME_UID_AND_TOKEN_LOSS_GAPS"
    print("TS_BEADS026=PASS;checks="+str(len(doc["checks"]))+
      ";same_UID_bypass=CONFIRMED;rotation=PASS;recovery=QUALIFIED_WITH_GAP;Product=NONE")
except Exception as e:
    doc["status"]="FAIL_EXACT_NATIVE_ATTEMPT_RECONCILE";doc["error"]=str(e)[:900]
    print("TS_BEADS026_ERROR="+str(e)[:600],file=sys.stderr)
    raise
finally:
    stop_server()
    if dolt and dolt.poll() is None:
        dolt.terminate()
        try:dolt.wait(timeout=8)
        except subprocess.TimeoutExpired:dolt.kill();dolt.wait(timeout=5)
    for o in streams:o.close()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("TS_BEADS026_RECEIPT="+str(OUTPUT)+";status="+doc["status"])
