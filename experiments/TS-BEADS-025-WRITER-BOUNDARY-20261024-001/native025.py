#!/usr/bin/env python3
"""025: native Dolt SQL authentication + OS filesystem restriction + co-resident HTTP bypass/admission.
The graph is synthetic; Product and shared refs are checked by external workflow.
One disposable runner, no Docker and no global mutable issue ledger.
"""
import json, os, pathlib, secrets, shutil, socket, subprocess, sys, time, urllib.request
from hashlib import sha256

if len(sys.argv)>1 and sys.argv[1]=="attacker":
    mode=sys.argv[2]
    if mode=="http":
        port=int(os.environ["TS025_HTTP_PORT"])
        target=os.environ["TS025_DEP_TARGET"]
        root=os.environ["TS025_DEP_SOURCE"]
        item={"kind":"dep_add","dep_add":{"source":{"id":root},"target":{"id":target},"type":"related"}}
        payload=json.dumps({"actor":"TS025-UNTRUSTED-LOCAL","provenance":"test://ts025/untrusted","items":[item]}).encode()
        try:
            req=urllib.request.Request(f"http://127.0.0.1:{port}/v0/beads/issues:batchApply",
                data=payload,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=4) as res:
                print(json.dumps({"connected":True,"status":res.status,"response":res.read(400).decode(errors="replace")}))
        except Exception as e:
            print(json.dumps({"connected":False,"error":type(e).__name__,"message":str(e)[:120]}))
    elif mode=="sql":
        import pymysql
        p=int(os.environ["TS025_SQL_PORT"])
        database=os.environ["TS025_DATABASE"]
        password=os.environ["TS025_READER_PASSWORD"]
        c=pymysql.connect(host="127.0.0.1",port=p,user="ts025_readonly",
            password=password,database=database,connect_timeout=4,read_timeout=4)
        with c.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM issues")
            count=cur.fetchone()[0]
            try:
                cur.execute("UPDATE issues SET title=title WHERE 1=0")
                update="UNEXPECTED_WRITE_ALLOWED"
            except Exception as e:
                update="DENIED:"+type(e).__name__
        c.close()
        print(json.dumps({"read_count":count,"write_attempt":update}))
    else:raise ValueError("attacker mode not recognized")
    sys.exit(0)

import pymysql

BINARY=pathlib.Path(os.environ["BD_BIN"]).resolve()
DOLT=pathlib.Path(os.environ["DOLT_BIN"]).resolve()
ROOT=pathlib.Path(os.environ["LAB_ROOT"]).resolve()
OUT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
if ROOT.exists():raise RuntimeError("DISPOSABLE_ROOT_EXISTS_NO_REPLAY")
ROOT.mkdir(parents=True,mode=0o700)
ROOT.chmod(0o700)
for p in [BINARY,DOLT]:
    if not p.exists():raise RuntimeError("BINARY_MISSING_"+str(p))
RUN_ID=int(os.environ.get("GITHUB_RUN_ID","25"))
# Untrusted UID must read only public *code* and the PyMySQL package. Do not
# grant access to Actions workspace, private Dolt store, result or SQL passwords.
ATTACKER_STAGE=pathlib.Path("/tmp")/f"tsbeads025-untrusted-{RUN_ID}"
if ATTACKER_STAGE.exists():raise RuntimeError("ATTACKER_STAGE_EXISTS_NO_REPLAY")
ATTACKER_STAGE.mkdir(mode=0o755)
shutil.copy2(pathlib.Path(__file__).resolve(),ATTACKER_STAGE/"attacker025.py")
(ATTACKER_STAGE/"attacker025.py").chmod(0o644)
shutil.copytree(pathlib.Path(pymysql.__file__).resolve().parent, ATTACKER_STAGE/"pymysql")
for package_file in (ATTACKER_STAGE/"pymysql").rglob("*"):
    if package_file.is_dir():package_file.chmod(0o755)
    else:package_file.chmod(0o644)
SQL_PORT=27000+RUN_ID%13000
HTTP_PORT=41000+RUN_ID%12000
SYS_PY=sys.executable
readonly_pass=secrets.token_urlsafe(24)
root_pass=secrets.token_urlsafe(24)
receipt={"id":"TS-BEADS-025-EFFECTIVE-CAUSAL-WRITER-BOUNDARY-20261024-001",
 "status":"RUNNING","Product_effect":"NONE","shared_Dolt_effect":"NONE",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","checks":[],"findings":[],
 "native":"BEADS_1.3.1_DOLT_2.2.0_UBUNTU","attempt_provider":"GITHUB_ACTIONS",
 "boundary":{"credential_mode":"DOLT_SQL_AUTH_AND_UNIX_UID_NETWORK_POLICY",
             "separate_global_ledger":False,"writer_API_requires_isolation":True}}
def check(name,val):
    if not val:raise AssertionError(name)
    receipt["checks"].append({"name":name,"status":"PASS"})
def run(argv,*,cwd=None,env=None,timeout=45,allow_fail=False):
    p=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
    if p.returncode and not allow_fail:
        raise RuntimeError(f"command:{argv[0]}:{argv[1:3]}:exit={p.returncode} stderr={p.stderr[-700:]}")
    return p
def api(path,body=None):
    kw={"timeout":8}
    if body is not None:
        kw.update({"data":json.dumps(body).encode()})
    req=urllib.request.Request(f"http://127.0.0.1:{HTTP_PORT}"+path,
        headers={"Content-Type":"application/json"},method="POST" if body is not None else "GET",**({"data":kw["data"]} if "data" in kw else {}))
    with urllib.request.urlopen(req,timeout=8) as res:
        return json.loads(res.read())
def locate(data,issue,depth=0):
    if not isinstance(data,(dict,list)) or depth>8:return None
    if isinstance(data,dict):
        if data.get("id")==issue and "status" in data:return data
        for v in data.values():
            o=locate(v,issue,depth+1)
            if o:return o
    else:
        for v in data:
            o=locate(v,issue,depth+1)
            if o:return o
    return None
def issue(id):
    row=locate(api("/v0/beads/issues/"+id+"?brief_deps=true"),id)
    if not row or not isinstance(row.get("revision"),str):
        raise RuntimeError("NATIVE_ISSUE_NOT_FOUND_"+id)
    return row
def deps(id):return sorted(x["id"] for x in issue(id).get("dependencies",[]))
def batch(items,label):
    return api("/v0/beads/issues:batchApply",
         {"actor":"TS-BEADS-025-CONTROLLED","provenance":"test://025/"+label,"items":items})
def update(root,token,tag):
    return {"kind":"update","update":{"target":{"id":root},"expected_version":token,
     "patch":{"metadata":{"set":{"ts025_graph_version_marker":tag}}}}}
def edge(root,dep):
    return {"kind":"dep_add","dep_add":{"source":{"id":root},"target":{"id":dep},"type":"related"}}
def attacker(mode,*,target=None):
    env={**os.environ,"TS025_HTTP_PORT":str(HTTP_PORT),"TS025_SQL_PORT":str(SQL_PORT),
        "TS025_DEP_SOURCE":"ts025-root","TS025_DEP_TARGET":target or "ts025-unauthorized",
        "TS025_DATABASE":db_name,"TS025_READER_PASSWORD":readonly_pass}
    env["PYTHONPATH"]=str(ATTACKER_STAGE)
    restricted=["PYTHONPATH","TS025_HTTP_PORT","TS025_SQL_PORT","TS025_DEP_SOURCE","TS025_DEP_TARGET","TS025_DATABASE","TS025_READER_PASSWORD"]
    wrapper=["sudo","-n","-u","nobody","--","/usr/bin/env",*[f"{k}={env.get(k,'')}" for k in restricted],
             SYS_PY,str(ATTACKER_STAGE/"attacker025.py"),"attacker",mode]
    x=run(wrapper,env=env,timeout=20,allow_fail=True)
    if x.returncode:raise RuntimeError("ATTACKER_RUNNER_"+mode+": "+x.stderr[-500:])
    return json.loads(x.stdout.strip())
def sql_conn(user,password,database=None):
    return pymysql.connect(host="127.0.0.1",port=SQL_PORT,user=user,password=password,
        database=database,connect_timeout=4,read_timeout=6,write_timeout=6,autocommit=True)
sqlserver=None
beads_http=None
firewall_args=None
db_name=None
try:
    check("native_binaries_exist",BINARY.is_file() and DOLT.is_file())
    gitroot=ROOT/"repository";gitroot.mkdir()
    run(["git","init","-q"],cwd=gitroot)
    check("synthetic_git_no_remotes",run(["git","remote"],cwd=gitroot).stdout.strip()=="")
    sqlroot=ROOT/"dolt_private";sqlroot.mkdir(mode=0o700);sqlroot.chmod(0o700)
    stream=open(ROOT/"dolt-server.log","w")
    sqlserver=subprocess.Popen([str(DOLT),"sql-server","--host","127.0.0.1","--port",str(SQL_PORT)],
        cwd=sqlroot,stdout=stream,stderr=subprocess.STDOUT)
    for i in range(100):
        if sqlserver.poll() is not None:raise RuntimeError("DOLT_SQL_SERVER_DIED")
        try:
            rootconn=sql_conn("root","")
            break
        except Exception:
            time.sleep(.15)
    else:raise RuntimeError("DOLT_SQL_UNREACHABLE")
    with rootconn.cursor() as cur:
        cur.execute("SELECT user,host FROM mysql.user WHERE user='root'")
        roots=cur.fetchall()
        for u,h in roots:
            if u!="root":continue
            safehost=h.replace("'","''")
            cur.execute(f"ALTER USER 'root'@'{safehost}' IDENTIFIED BY %s",(root_pass,))
    rootconn.close()
    try:
        noauth=sql_conn("root","")
        noauth.close();denied=False
    except Exception:
        denied=True
    check("SQL_root_without_password_rejected",denied)
    env={**os.environ,"BEADS_DIR":str(gitroot/".beads"),
       "BEADS_DOLT_SERVER_MODE":"1","BEADS_DOLT_SERVER_HOST":"127.0.0.1",
       "BEADS_DOLT_SERVER_PORT":str(SQL_PORT),"BEADS_DOLT_SERVER_USER":"root",
       "BEADS_DOLT_PASSWORD":root_pass,"BD_NO_PUSH":"1","BD_DOLT_AUTO_PUSH":"false",
       "GIT_TERMINAL_PROMPT":"0","BEADS_ACTOR":"TS-BEADS-025-TEST"}
    init=run([BINARY,"init","--server","--quiet","--stealth"],cwd=gitroot,env=env,timeout=60)
    rootconn=sql_conn("root",root_pass)
    with rootconn.cursor() as cur:
        cur.execute("SHOW DATABASES")
        dbs=[r[0] for r in cur.fetchall()]
        candidates=[d for d in dbs if d not in ("information_schema","performance_schema","mysql","sys")]
        if len(candidates)!=1:raise RuntimeError("NONUNIQUE_SYNTHETIC_BEADS_DATABASE:"+str(candidates))
        db_name=candidates[0]
        cur.execute("CREATE USER 'ts025_readonly'@'%%' IDENTIFIED BY %s",(readonly_pass,))
        cur.execute(f"GRANT SELECT ON `{db_name}`.* TO 'ts025_readonly'@'%'")
    rootconn.close()
    check("read_only_authenticated_sql_user_created",True)
    # Root and readonly credentials are never written to the public Git repo or receipt.
    for id in ("ts025-root","ts025-initial","ts025-unauthorized","ts025-controlled","ts025-blocked"):
        a=run([BINARY,"create","TS025 "+id,"--type","task","--id",id,"--force",
                "--description","EXPERIMENT_ONLY","--metadata",'{"ts025_graph_version_marker":"BASE"}','--json'],
                cwd=gitroot,env=env,timeout=55)
        raw=a.stdout.strip();offset=raw.find("{")
        alt=raw.find("[")
        if alt>=0 and (offset<0 or alt<offset):offset=alt
        if offset<0:raise RuntimeError("NATIVE_CREATE_JSON_MISSING")
        obj=json.loads(raw[offset:])
        if isinstance(obj,list):obj=obj[0]
        check("native_issue_created_"+id,obj.get("id")==id)
    b=run([BINARY,"dep","add","ts025-root","ts025-initial","--type","related"],cwd=gitroot,env=env,timeout=50)
    check("native_baseline_edge_created",True)
    # Native Beads HTTP service is a privileged writer; DB readonly user cannot authenticate as root.
    http_stream=open(ROOT/"beads-http.log","w")
    beads_http=subprocess.Popen([str(BINARY),"serve","--addr",f"127.0.0.1:{HTTP_PORT}"],
        cwd=gitroot,env=env,stdout=http_stream,stderr=subprocess.STDOUT)
    for i in range(110):
        if beads_http.poll() is not None:raise RuntimeError("BEADS_HTTP_DIED")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{HTTP_PORT}/healthz",timeout=.8) as r:
                if r.status==200:break
        except Exception:time.sleep(.18)
    else:raise RuntimeError("BEADS_HTTP_UNREACHABLE")
    check("privileged_native_beads_service_ready",True)
    nativeBefore=issue("ts025-root")
    sql=attacker("sql")
    check("untrusted_UID_read_only_SQL_query_succeeds",sql["read_count"]>=5)
    check("untrusted_UID_SQL_write_denied",sql["write_attempt"].startswith("DENIED:"))
    receipt["boundary"]["SQL_reader_read_count"]=sql["read_count"]
    private=gitroot/".beads"/"metadata.json"
    forbidden=run(["sudo","-n","-u","nobody","--","test","-r",private],allow_fail=True)
    check("untrusted_UID_cannot_read_private_Beads_metadata",forbidden.returncode!=0)
    # The exact bypass: HTTP native batch lacks OS/process caller authentication by default.
    injected=attacker("http",target="ts025-unauthorized")
    after=issue("ts025-root")
    check("unprotected_privileged_HTTP_can_be_called_by_untrusted_UID",
          injected["connected"] and injected["status"]==200)
    check("untrusted_HTTP_dep_add_modified_same_native_graph",
          "ts025-unauthorized" in deps("ts025-root"))
    check("untrusted_HTTP_dep_add_did_not_advance_root_revision",
          nativeBefore["revision"]==after["revision"])
    receipt["findings"].append({
     "name":"SQL_ACL_AND_FILE_ACL_ALONE_INSUFFICIENT",
     "observation":"Untrusted OS UID with no write SQL privileges and no private store access wrote a native dependency through exposed local Beads HTTP API without advancing root revision",
     "original_root_revision":nativeBefore["revision"],"after_uncontrolled_edge":after["revision"]})
    # Install a bounded OS-owner network firewall rule on the ephemeral Actions runner.
    attacker_uid=run(["id","-u","nobody"]).stdout.strip()
    firewall_args=["-p","tcp","-d","127.0.0.1","--dport",str(HTTP_PORT),
       "-m","owner","--uid-owner",attacker_uid,"-j","REJECT"]
    policy=run(["sudo","-n","iptables","-I","OUTPUT","1",*firewall_args],allow_fail=True)
    if policy.returncode:
        receipt["status"]="BLOCKED_NETWORK_OWNER_POLICY_UNAVAILABLE"
        receipt["findings"].append({"name":"NETWORK_POLICY_UNAVAILABLE",
            "error":policy.stderr[-500:],
            "classification":"Material adoption blocker: unsafe HTTP bypass still exposed to co-resident process"})
    else:
        check("ephemeral_process_UID_HTTP_network_boundary_installed",True)
        blocked=attacker("http",target="ts025-blocked")
        check("untrusted_UID_cannot_reach_write_API_after_owner_policy",not blocked["connected"])
        check("rejected_untrusted_writer_did_not_change_graph","ts025-blocked" not in deps("ts025-root"))
        allowed=issue("ts025-root")
        result=batch([update("ts025-root",allowed["revision"],"CONTROLLED_EDGE"),
                  edge("ts025-root","ts025-controlled")],"controlled-writer")
        check("privileged_controlled_edge_update_native_atomic",len(result.get("items",[]))==2)
        current=issue("ts025-root")
        check("privileged_root_revision_advanced_after_controlled_edge",
              current["revision"]!=allowed["revision"])
        check("privileged_controlled_edge_exists","ts025-controlled" in deps("ts025-root"))
        try:
            batch([update("ts025-root",allowed["revision"],"STALE_WRITE")],"stale-writer")
            rejected=False
        except Exception:
            rejected=True
        check("native_stale_competing_writer_rejected",rejected)
        # Even as readonly SQL, the untrusted process should continue to use queries.
        sql2=attacker("sql")
        check("reader_retains_native_SQL_read_after_HTTP_policy",sql2["read_count"]>=5)
        check("reader_cannot_update_SQL_after_HTTP_policy",sql2["write_attempt"].startswith("DENIED:"))
        receipt["boundary"].update({"root_secret_exposure":"NONE_TO_UNTRUSTED",
         "HTTP_untrusted_UID":"DENIED_BY_EPHEMERAL_OS_POLICY",
         "direct_private_store":"DENIED_BY_DIRECTORY_PERMISSIONS",
         "authenticated_sql_write":"DENIED_BY_GRANTS",
         "authorized_writer":"EXACT_ROOT_BATCH_VERSIONED",
         "bypass_under_same_UID":"NOT_PREVENTED_BY_OWNER_POLICY"})
        receipt["status"]="PASS_EFFECTIVE_UID_BOUNDARY_WITH_MATERIAL_SAME_UID_LIMITATIONS"
        receipt["findings"].append({"name":"CONDITIONAL_EFFECTIVE_BOUNDARY",
         "scope":"Untrusted separate Unix UID with readonly SQL credentials vs privileged writer on ephemeral Linux runner",
         "exclusions":["same-UID code execution","root/sudo escalation","other network ingress",
            "separately exposed Beads writable endpoints","direct filesystem access under privileged identity",
            "real multi-host deployment and Product lifecycle"]})
    print(f"TS_BEADS025={receipt['status']};checks={len(receipt['checks'])};Product=NONE")
except Exception as e:
    receipt["status"]="FAIL_ORIGINAL_BOUNDARY_ATTEMPT"
    receipt["error"]=str(e)[:1000]
    print("TS_BEADS025_ERROR="+str(e)[:600],file=sys.stderr)
    raise
finally:
    if firewall_args:
        run(["sudo","-n","iptables","-D","OUTPUT",*firewall_args],timeout=10,allow_fail=True)
    if beads_http and beads_http.poll() is None:
        beads_http.terminate()
        try:beads_http.wait(timeout=7)
        except subprocess.TimeoutExpired:beads_http.kill()
    if sqlserver and sqlserver.poll() is None:
        sqlserver.terminate()
        try:sqlserver.wait(timeout=7)
        except subprocess.TimeoutExpired:sqlserver.kill()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    shutil.rmtree(ATTACKER_STAGE,ignore_errors=True)
    print(f"TS_BEADS025_RECEIPT={OUT};status={receipt['status']}")
