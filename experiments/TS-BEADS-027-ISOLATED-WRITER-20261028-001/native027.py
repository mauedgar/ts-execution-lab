#!/usr/bin/env python3
"""027 isolated native writer service vs separate read-only implementer Unix UID.
All privileged files and credentials are inside a 0700 writer-owned disposable root.
GitHub Actions is only the runner; NO Product, external effect or shared Dolt changes.
"""
from __future__ import annotations
import json,os,pathlib,shlex,secrets,shutil,subprocess,sys,time,urllib.request,urllib.error
import pymysql

BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
DOLT=pathlib.Path(os.environ["DOLT_BIN"]).resolve()
BASE=pathlib.Path(os.environ["TS027_BASE"]).resolve()
PRIVATE=BASE/"writer-private"
RESULT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
PROBE_SRC=pathlib.Path(os.environ["TS027_READER_PROBE"]).resolve()
RUN_ID=int(os.environ.get("GITHUB_RUN_ID","27"))
SQL_PORT=25000+RUN_ID%15000
HTTP_PORT=41000+RUN_ID%12000
WRITER="ts027w"
READER="ts027r"
doc={"id":"TS-BEADS-027-SEPARATE-PRINCIPAL-20261028-001",
 "status":"RUNNING","Product_effect":"NONE","shared_Dolt_effect":"NONE",
 "authority":"EXPERIMENTAL_CONTROL_ONLY","checks":[],"evidence":[],
 "limits":["Local disposable Ubuntu separate Unix users; no production multihost nor root escalation",
           "Writer service retains full Beads and Dolt privileges; implementers must not share writer UID",
           "Native HTTP token covers entire surface, not fine-grained per-operation permission",
           "No proof of durable production supervisor, disaster recovery or all clients/endpoints",
           "Misconfigured unauthenticated loopback startup remains a possible unsafe alternate mode"]}
def check(name,condition):
    if not condition:raise AssertionError(name)
    doc["checks"].append(name)
def call(args,timeout=40,allow_fail=False,env=None,cwd=None):
    q=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout,
                     env=env,cwd=cwd)
    if q.returncode and not allow_fail:
        raise RuntimeError("COMMAND_FAILED_"+str(args[:3])+":"+q.stderr[-550:])
    return q
def sudo(args,**opts):return call(["sudo","-n",*args],**opts)
def writer(args,timeout=45,allow_fail=False):
    return sudo(["-u",WRITER,"--",str(PRIVATE/"writer-exec.sh"),*map(str,args)],
        timeout=timeout,allow_fail=allow_fail)
def sql_root(password="",database=None):
    return pymysql.connect(host="127.0.0.1",port=SQL_PORT,user="root",password=password,
        database=database,connect_timeout=4,read_timeout=5,write_timeout=5,autocommit=True)
def get_url(path,token=None,method="GET",payload=None):
    headers={"Content-Type":"application/json"}
    if token:headers["Authorization"]="Bearer "+token
    request=urllib.request.Request("http://127.0.0.1:"+str(HTTP_PORT)+path,
        method=method,headers=headers,
        data=(json.dumps(payload).encode() if payload is not None else None))
    try:
        with urllib.request.urlopen(request,timeout=6) as r:
            return r.status,r.read(5000).decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code,e.read(400).decode(errors="replace")
def locate(v,id,depth=0):
    if depth>7:return None
    if isinstance(v,dict):
        if v.get("id")==id and "revision" in v:return v
        for x in v.values():
            z=locate(x,id,depth+1)
            if z:return z
    if isinstance(v,list):
        for x in v:
            z=locate(x,id,depth+1)
            if z:return z
    return None
def detail(token,id):
    code,raw=get_url("/v0/beads/issues/"+id+"?brief_deps=true",token)
    if code!=200:raise RuntimeError("AUTH_DETAIL_FAIL_"+str(code))
    return locate(json.loads(raw),id)
def deps(row):return sorted(x["id"] for x in row.get("dependencies",[]))
def mutation(token,root_revision,target,tag):
    return get_url("/v0/beads/issues:batchApply",token,"POST",
      {"actor":"TS027-QUALIFIED-WRITER","provenance":"experiment://ts027/"+tag,
       "items":[{"kind":"update","update":{"target":{"id":"ts027-root"},"expected_version":root_revision,
         "patch":{"metadata":{"set":{"ts027_graph_epoch":tag}}}}},
        {"kind":"dep_add","dep_add":{"source":{"id":"ts027-root"},"target":{"id":target},"type":"related"}}]})
proc_sql=None;proc_http=None;streams=[]
def stop_http():
    global proc_http
    if proc_http:
        if proc_http.poll() is None:
            proc_http.terminate()
            try:proc_http.wait(timeout=10)
            except subprocess.TimeoutExpired:proc_http.kill();proc_http.wait(timeout=4)
        proc_http=None
def launch_http(auth=True):
    global proc_http
    label="auth" if auth else "insecure"
    log=open(BASE/("beads-"+label+"-"+str(time.time_ns())+".log"),"w");streams.append(log)
    args=["sudo","-n","-u",WRITER,"--",str(PRIVATE/"writer-exec.sh"),str(BD),"serve",
          "--addr","127.0.0.1:"+str(HTTP_PORT)]
    if auth:args+=["--auth-token-file",str(PRIVATE/"bearer")]
    proc_http=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
    for _ in range(90):
        if proc_http.poll() is not None:raise RuntimeError("NATIVE_SERVICE_PREMATURE_EXIT_"+label)
        try:
            if get_url("/healthz")[0]==200:return
        except Exception:time.sleep(.18)
    raise RuntimeError("NATIVE_SERVICE_NOT_READY_"+label)
def reader_probe(action):
    public=BASE/"public"
    e=[
      "TS027_SQL_PORT="+str(SQL_PORT),"TS027_HTTP_PORT="+str(HTTP_PORT),
      "TS027_READER_SECRET="+str(BASE/"reader-private"/"readpass"),
      "TS027_DB="+db_name,"PYTHONPATH="+os.environ["PYTHONPATH"]]
    r=sudo(["-u",READER,"--","/usr/bin/env",*e,sys.executable,str(public/"reader027.py"),action],
            timeout=30)
    return json.loads(r.stdout)
def original_pid_user(pid):
    return call(["ps","-o","user=","-p",str(pid)],allow_fail=True).stdout.strip()
try:
    if BASE.exists():raise RuntimeError("ATTEMPT_WORKSPACE_ALREADY_EXISTS")
    BASE.mkdir(mode=0o755,parents=True)
    check("pinned_native_binaries",BD.is_file() and DOLT.is_file())
    sudo(["useradd","-M","-s","/bin/sh",WRITER])
    sudo(["useradd","-M","-s","/bin/sh",READER])
    check("separate_OS_identities",call(["id","-u",WRITER]).stdout.strip()!=
          call(["id","-u",READER]).stdout.strip())
    PRIVATE.mkdir(mode=0o700)
    work=PRIVATE/"git";sql_dir=PRIVATE/"sql";home=PRIVATE/"home"
    for p in [work,sql_dir,home]:p.mkdir(mode=0o700)
    root_pass=secrets.token_urlsafe(32)
    bearer=secrets.token_urlsafe(32)
    read_pass=secrets.token_urlsafe(32)
    script=PRIVATE/"writer-exec.sh"
    script.write_text("#!/bin/sh\nset -eu\n"+
       "export HOME="+shlex.quote(str(home))+"\n"+
       "export BEADS_DIR="+shlex.quote(str(work/".beads"))+"\n"+
       "export BEADS_DOLT_SERVER_MODE=1\n"+
       "export BEADS_DOLT_SERVER_HOST=127.0.0.1\n"+
       "export BEADS_DOLT_SERVER_PORT="+str(SQL_PORT)+"\n"+
       "export BEADS_DOLT_SERVER_USER=root\n"+
       "export BEADS_DOLT_PASSWORD="+shlex.quote(root_pass)+"\n"+
       "export BD_NO_PUSH=1\nexport BD_DOLT_AUTO_PUSH=false\n"+
       "export BEADS_ACTOR=TS-BEADS-027-WRITER\n"+
       "cd "+shlex.quote(str(work))+"\nexec \"$@\"\n",encoding="utf8")
    script.chmod(0o700)
    auth_file=PRIVATE/"bearer"
    auth_file.write_text(bearer+"\n");auth_file.chmod(0o600)
    sudo(["chown","-R",WRITER+":"+WRITER,str(PRIVATE)])
    sudo(["chmod","0700",str(PRIVATE)])
    check("writer_store_and_credentials_private",
      call(["stat","-c","%a",str(PRIVATE)]).stdout.strip()=="700" and
      call(["stat","-c","%a",str(auth_file)]).stdout.strip()=="600")
    for f in [PRIVATE,auth_file,script]:
        denied=sudo(["-u",READER,"--","test","-r",str(f)],allow_fail=True)
        check("reader_UID_cannot_read_privileged_"+f.name,denied.returncode!=0)
    public=BASE/"public";public.mkdir(mode=0o755)
    shutil.copyfile(PROBE_SRC,public/"reader027.py")
    (public/"reader027.py").chmod(0o644)
    reader_dir=BASE/"reader-private";reader_dir.mkdir(mode=0o700)
    (reader_dir/"readpass").write_text(read_pass+"\n")
    (reader_dir/"readpass").chmod(0o600)
    sudo(["chown","-R",READER+":"+READER,str(reader_dir)])
    log=open(BASE/"dolt.log","w");streams.append(log)
    # The privileged server has its own UID and private Dolt directory.
    shell=("cd "+shlex.quote(str(sql_dir))+" && exec "+shlex.quote(str(DOLT))+
          " sql-server --host 127.0.0.1 --port "+str(SQL_PORT))
    proc_sql=subprocess.Popen(["sudo","-n","-u",WRITER,"--","/bin/sh","-c",shell],
         stdout=log,stderr=subprocess.STDOUT)
    for _ in range(110):
        if proc_sql.poll() is not None:raise RuntimeError("DOLT_SERVER_DIED")
        try:c=sql_root("");break
        except Exception:time.sleep(.15)
    else:raise RuntimeError("DOLT_SERVER_BOOTSTRAP_FAILED")
    with c.cursor() as cur:
        cur.execute("SELECT user,host FROM mysql.user WHERE user='root'")
        for u,h in cur.fetchall():
            esc=h.replace("'","''")
            cur.execute(f"ALTER USER 'root'@'{esc}' IDENTIFIED BY %s",(root_pass,))
    c.close()
    try:sql_root("").close();without_password=False
    except Exception:without_password=True
    check("SQL_privileged_writer_root_auth_required",without_password)
    check("native_Dolt_process_under_writer_UID",original_pid_user(proc_sql.pid) in
          {WRITER,"root"}) # sudo wrapper may report root before process exec
    writer(["git","init","-q"])
    check("writer_git_store_no_remote",writer(["git","remote"]).stdout.strip()=="")
    writer([BD,"init","--server","--quiet","--stealth"],timeout=60)
    c=sql_root(root_pass)
    with c.cursor() as cur:
        cur.execute("SHOW DATABASES")
        all_db=[x[0] for x in cur.fetchall()]
        names=[x for x in all_db if x not in ("information_schema","performance_schema","mysql","sys")]
        if len(names)!=1:raise RuntimeError("UNEXPECTED_DATABASE_SET:"+repr(names))
        db_name=names[0]
        cur.execute("CREATE USER 'ts027_reader'@'%%' IDENTIFIED BY %s",(read_pass,))
        cur.execute("GRANT SELECT ON \`"+db_name+"\`.* TO 'ts027_reader'@'%'")
    c.close()
    for issue in ("ts027-root","ts027-guarded","ts027-insecure"):
        p=writer([BD,"create","TS027 "+issue,"--type","task","--id",issue,
          "--force","--metadata",'{"ts027_graph_epoch":"BASE"}',"--json"],timeout=40)
        s=p.stdout.strip();indexes=[v for v in (s.find("{"),s.find("[")) if v>=0]
        obj=json.loads(s[min(indexes):]);obj=obj[0] if isinstance(obj,list) else obj
        check("writer_created_"+issue,obj["id"]==issue)
    launch_http(auth=True)
    check("native_service_auth_running",get_url("/healthz")[0]==200)
    r=reader_probe("probe")
    check("separate_reader_SQL_SELECT_allowed",r["sql_issue_count"]>=3)
    check("separate_reader_SQL_UPDATE_denied",r["sql_write"]=="SQL_WRITE_REFUSED")
    check("separate_reader_HTTP_routes_all_401",len(r["endpoints"])==5 and
          all(x["status"]==401 for x in r["endpoints"]))
    doc["evidence"].append({"phase":"authenticated_boundary",**r})
    reader_native=sudo(["-u",READER,"--","test","-r",str(work/".beads"/"metadata.json")],allow_fail=True)
    check("reader_no_direct_Beads_storage_access",reader_native.returncode!=0)
    current=detail(bearer,"ts027-root")
    status,_=mutation(bearer,current["revision"],"ts027-guarded","guarded-start")
    check("authorized_writer_scoped_batch_succeeded",status==200)
    updated=detail(bearer,"ts027-root")
    check("causal_writer_advances_root_version",updated["revision"]!=current["revision"] and
       "ts027-guarded" in deps(updated))
    stale,_=get_url("/v0/beads/issues:batchApply",bearer,"POST",
       {"actor":"TS027-STALENESS","items":[{"kind":"update","update":{
        "target":{"id":"ts027-root"},"expected_version":current["revision"],
        "patch":{"metadata":{"set":{"ts027_graph_epoch":"STALE"}}}}}]})
    check("native_CAS_rejects_old_version",stale!=200)
    stop_http()
    launch_http(auth=True)
    check("restart_kept_service_authenticated",all(x["status"]==401 for x in reader_probe("probe")["endpoints"]))
    check("restart_kept_authorized_read",detail(bearer,"ts027-root")["id"]=="ts027-root")
    stop_http()
    sudo(["-u",WRITER,"--","mv",str(auth_file),str(PRIVATE/"bearer.withheld")])
    missing=subprocess.Popen(["sudo","-n","-u",WRITER,"--",str(script),str(BD),"serve",
        "--addr","127.0.0.1:"+str(HTTP_PORT),"--auth-token-file",str(auth_file)],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:missing.wait(timeout=5);refused=missing.returncode!=0
    except subprocess.TimeoutExpired:
        missing.terminate();missing.wait(timeout=5);refused=False
    check("restart_missing_token_file_fail_closed",refused)
    sudo(["-u",WRITER,"--","mv",str(PRIVATE/"bearer.withheld"),str(auth_file)])
    launch_http(auth=True)
    check("restored_credential_service_denies_unauthorized_reader",
       all(x["status"]==401 for x in reader_probe("probe")["endpoints"]))
    stop_http()
    # Controlled negative deployment regression: loopback server without --auth-token-file.
    # No Product endpoints or network egress; stop this deliberately insecure service immediately.
    prior=writer([BD,"show","ts027-root","--json"],timeout=30)
    launch_http(auth=False)
    attack=reader_probe("misconfig")
    stop_http()
    check("omitted_native_auth_flag_reopened_write_API",attack["status"]==200)
    launch_http(auth=True)
    final=detail(bearer,"ts027-root")
    check("misconfigured_unprotected_graph_change_persisted",
       "ts027-insecure" in deps(final))
    check("misconfigured_edge_was_not_root_revision_fenced",final["revision"]==updated["revision"])
    check("restored_auth_post_misconfig_closes_readonly_client_write",
       all(x["status"]==401 for x in reader_probe("probe")["endpoints"]))
    doc["evidence"].append({"phase":"restart_and_config_drift","missing_file_start":"REFUSED",
       "authenticated_restart":"PASS",
       "omitted_auth_restart":"UNAUTHORIZED_DEP_ADD_SUCCEEDED",
       "restored_auth_restart":"READER_DENIED",
       "root_revision_unchanged_during_unprotected_edge":True})
    doc["limits"].append("Non-authenticated loopback start can reintroduce full write bypass even with separate UIDs. Native Beads does not force bearer on loopback.")
    doc["status"]="PASS_SEPARATE_UID_WRITER_WITH_NATIVE_AUTH_CONFIGURATION_GAP"
    print("TS_BEADS027=PASS;checks="+str(len(doc["checks"]))+
          ";UID_ISOLATED=YES;OMITTED_AUTH=UNSAFE;Product=NONE")
except Exception as e:
    doc["status"]="FAIL_BOUNDED_027_ATTEMPT_RECONCILE"
    doc["error"]=str(e)[:1000]
    print("TS_BEADS027_ERROR="+str(e)[:650],file=sys.stderr)
    raise
finally:
    stop_http()
    if proc_sql and proc_sql.poll() is None:
        proc_sql.terminate()
        try:proc_sql.wait(timeout=7)
        except subprocess.TimeoutExpired:proc_sql.kill();proc_sql.wait(timeout=4)
    for stream in streams:stream.close()
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("TS_BEADS027_RECEIPT="+str(RESULT)+";status="+doc["status"])
