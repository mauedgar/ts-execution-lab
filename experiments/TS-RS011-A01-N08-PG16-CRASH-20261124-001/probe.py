"""NONPRODUCT N08: actual PostgreSQL crash recovery on one disposable CI host.
Uses the exact PR85 experimental schema, not an adopted authority implementation.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import select
import subprocess
import sys
import time

IMAGE = "postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e"
SCHEMA_BLOB = "1a5027709214092a4cabb21c63a53ca4f262c09c"
AUTH = "rs011_authority"
WRITER = "rs011_writer"
OBS = "rs011_observer"
PASSWORDS = {
    "postgres": "a01-disposable-admin",
    AUTH: "a01-disposable-authority",
    WRITER: "a01-disposable-writer",
    OBS: "a01-disposable-observer",
}
SUBJECT = '{"repo":"synthetic","branch":"fixture","tree":"tree1","taskcycle":"tc1","operation":"op1","attempt":"att1","subject":"effect1"}'
PAYLOAD = '{"value":"crash-fixture"}'
BEGIN = "BEGIN ISOLATION LEVEL READ COMMITTED;"

def check(ok, code):
    if not ok:
        raise RuntimeError(code)

def run(cmd, *, data=None, env=None, timeout=15, expected=True):
    p = subprocess.run(cmd, input=data, text=True, capture_output=True,
                       timeout=timeout, env=env)
    check(len(p.stdout)+len(p.stderr)<262144, "OUTPUT_LIMIT")
    if expected:
        check(p.returncode == 0, "COMMAND_FAILED_"+cmd[0]+"_"+p.stderr[-300:])
    return p

def pg_args(role, app):
    env = {"PATH":"/usr/bin:/bin","LC_ALL":"C","PGPASSWORD":PASSWORDS[role],
           "PGAPPNAME":app,"PGHOSTADDR":"127.0.0.1","PGSSLMODE":"disable",
           "PGGSSENCMODE":"disable","PGCONNECT_TIMEOUT":"2",
           "PGOPTIONS":"-c statement_timeout=8000 -c lock_timeout=4000 -c idle_in_transaction_session_timeout=60000"}
    return ["/usr/bin/psql","-X","-qAt","-w","-v","ON_ERROR_STOP=1",
            "-h","127.0.0.1","-p","5432","-U",role,"-d","postgres"], env

def pg(sql, role=OBS, app="rs011_n08_observer"):
    cmd,env=pg_args(role,app)
    return run(cmd,data=sql+"\n",env=env,timeout=12).stdout.strip()

def revoke(scope):
    check(scope in {"stale","effect_first","rollback"},"BAD_SCOPE")
    return "SELECT rs011_a01.revoke_grant('"+scope+"',1);"

def apply(scope):
    check(scope in {"stale","effect_first"},"BAD_SCOPE")
    return ("SELECT rs011_a01.apply_effect('"+scope+"',1,'"+SUBJECT
            +"'::jsonb,'n08-"+scope+"','"+PAYLOAD+"'::jsonb);")

def inspect(cid):
    raw=run(["docker","inspect",cid]).stdout
    doc=json.loads(raw)
    check(len(doc)==1,"CONTAINER_COUNT")
    d=doc[0]
    check(d["Id"]==cid and d["Config"]["Image"]==IMAGE,"SERVICE_IDENTITY")
    check(d["HostConfig"]["PortBindings"]=={
        "5432/tcp":[{"HostIp":"127.0.0.1","HostPort":"5432"}]
    },"PORT_BINDING")
    mounts=[m for m in d["Mounts"] if m["Destination"]=="/var/lib/postgresql/data"]
    check(len(mounts)==1 and mounts[0]["Type"]=="volume" and mounts[0]["RW"],"PGDATA_VOLUME")
    name=mounts[0].get("Name","")
    check(bool(re.fullmatch("[0-9a-f]{64}",name)),"PGDATA_NOT_ANONYMOUS")
    check(d["HostConfig"]["RestartPolicy"]["Name"] in {"","no"},"RESTART_POLICY")
    return {"id":d["Id"],"volume":name,"started_at":d["State"]["StartedAt"],
            "running":d["State"]["Running"],"exit_code":d["State"]["ExitCode"]}

def facts():
    return pg("SELECT system_identifier::text FROM pg_control_system();"
              "SELECT current_setting('server_version_num');"
              "SELECT current_setting('fsync')||'|'||current_setting('synchronous_commit')||'|'||current_setting('full_page_writes');"
              "SELECT pg_postmaster_start_time()::text;", "postgres", "rs011_n08_identity").splitlines()

def snapshot():
    # Observer has SELECT only. Exact state, events and receipts, including payload and subject.
    out=pg("""SELECT jsonb_build_object(
       'grants',(SELECT jsonb_agg(to_jsonb(g) ORDER BY scope) FROM rs011_a01.grants g),
       'head',(SELECT jsonb_agg(to_jsonb(h) ORDER BY scope) FROM rs011_a01.head h),
       'events',(SELECT jsonb_agg(to_jsonb(e) ORDER BY scope) FROM rs011_a01.events e),
       'receipts',(SELECT jsonb_agg(to_jsonb(r) ORDER BY scope) FROM rs011_a01.receipts r))::text;""")
    return json.loads(out)

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def grant(snap,scope):
    return next(g for g in snap["grants"] if g["scope"]==scope)

def head(snap,scope):
    return next(h for h in snap["head"] if h["scope"]==scope)

def open_uncommitted():
    cmd,env=pg_args(AUTH,"rs011_n08_inflight")
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                       env=env,bufsize=0)
    try:
        p.stdin.write(("SELECT pg_backend_pid();\n"+BEGIN+"\n"+revoke("rollback")+
                       "\n\\echo N08_UNCOMMITTED_REVOKE\n").encode())
        p.stdin.flush()
        deadline=time.monotonic()+8
        buf=b""
        while b"N08_UNCOMMITTED_REVOKE\n" not in buf:
            left=deadline-time.monotonic()
            check(left>0,"INFLIGHT_DEADLINE")
            ready,_,_=select.select([p.stdout],[],[],left)
            check(bool(ready),"INFLIGHT_TIMEOUT")
            part=os.read(p.stdout.fileno(),4096)
            check(bool(part),"INFLIGHT_CLOSED")
            buf+=part
            check(len(buf)<8192,"INFLIGHT_OUTPUT")
        lines=buf.decode().strip().splitlines()
        check(len(lines)==3 and lines[1:]==["REVOKED","N08_UNCOMMITTED_REVOKE"],"INFLIGHT_ORACLE")
        pid=int(lines[0])
        check(pg("SELECT count(*) FROM pg_stat_activity WHERE pid="+str(pid)+
                 " AND application_name='rs011_n08_inflight' AND state='idle in transaction'"
                 " AND backend_xid IS NOT NULL;","postgres")=="1","INFLIGHT_NOT_ACTIVE")
        return p,pid
    except BaseException:
        p.kill()
        p.wait(timeout=3)
        raise

def wait_recovery():
    deadline=time.monotonic()+35
    cmd,env=pg_args("postgres","rs011_n08_recovery")
    while time.monotonic()<deadline:
        p=run(cmd,data="SELECT 1;\n",env=env,timeout=4,expected=False)
        if p.returncode==0 and p.stdout.strip()=="1":
            return
        time.sleep(.25)
    raise RuntimeError("RECOVERY_TIMEOUT")

def main():
    check(os.environ.get("GITHUB_ACTIONS")=="true" and
          os.environ.get("TS_RS011_N08_DISPOSABLE")=="yes","NOT_DISPOSABLE")
    check(sys.version_info[:3]==(3,15,2),"PYTHON_VERSION")
    cid=os.environ["TS_RS011_N08_SERVICE_ID"]
    check(bool(re.fullmatch("[0-9a-f]{64}",cid)),"BAD_SERVICE_ID")
    schema=Path(sys.argv[1]).read_bytes()
    check(hashlib.sha1(b"blob "+str(len(schema)).encode()+b"\0"+schema).hexdigest()==SCHEMA_BLOB,
          "SCHEMA_BLOB")
    before_container=inspect(cid)
    check(before_container["running"],"SERVICE_NOT_RUNNING")
    before_identity=facts()
    check(len(before_identity)==4 and before_identity[1:3]==["160015","on|on|on"],"DURABILITY_SETTINGS")
    pg(schema.decode(),"postgres","rs011_n08_schema")
    check(pg(revoke("stale"),AUTH)=="REVOKED","STALE_REVOKE")
    check(pg(apply("effect_first"),WRITER)=="APPLIED","COMMITTED_EFFECT")
    check(pg(revoke("effect_first"),AUTH)=="REVOKED","EFFECT_REVOKE")
    before=snapshot()
    check(grant(before,"stale")["version"]==2 and not grant(before,"stale")["active"],"STALE_BEFORE")
    check(grant(before,"effect_first")["version"]==2 and not grant(before,"effect_first")["active"],"EFFECT_BEFORE")
    check(grant(before,"rollback")["version"]==1 and grant(before,"rollback")["active"],"ROLLBACK_BEFORE")
    check(head(before,"effect_first")["revision"]==1 and head(before,"stale")["revision"]==0,"HEAD_BEFORE")
    check(before["events"]==[{"scope":"effect_first","revision":1,"payload":json.loads(PAYLOAD)}],"EVENT_BEFORE")
    check(before["receipts"]==[{"scope":"effect_first","mutation_id":"n08-effect_first",
        "grant_version":1,"subject":json.loads(SUBJECT),"payload":json.loads(PAYLOAD),"revision":1}],"RECEIPT_BEFORE")
    pending=None
    try:
        pending,pid=open_uncommitted()
        check(snapshot()==before,"UNCOMMITTED_VISIBLE")
        # Exact CI service only. Abrupt SIGKILL, not a graceful shutdown.
        check(run(["docker","kill","--signal=KILL",cid]).stdout.strip()==cid,"KILL_RECEIPT")
        down=inspect(cid)
        check(not down["running"] and down["exit_code"]==137,"NOT_CRASH_EXIT")
        pending.stdin.close()
        rc=pending.wait(timeout=8)
        # psql may exit 0 on EOF while idle at stdin, even after server death.
        # No COMMIT was sent on this session; post-recovery equality is the oracle.
        check(pending.poll() is not None,"CLIENT_NOT_TERMINAL")
        print(json.dumps({"stage":"CRASH_CONFIRMED","exit":down["exit_code"],
                          "client_exit":rc,"commit_sent":False},sort_keys=True),flush=True)
        check(run(["docker","start",cid]).stdout.strip()==cid,"START_RECEIPT")
        wait_recovery()
        after_container=inspect(cid)
        check(after_container["running"] and after_container["volume"]==before_container["volume"]
              and after_container["started_at"]!=before_container["started_at"],"STORAGE_OR_RESTART_ID")
        after_identity=facts()
        check(after_identity[:3]==before_identity[:3] and after_identity[3]!=before_identity[3],
              "POSTMASTER_OR_CLUSTER_ID")
        after=snapshot()
        check(after==before,"DURABLE_STATE_MISMATCH")
        # Fresh first-time stale request only. No replay of a previously committed mutation.
        check(pg(apply("stale"),WRITER)=="DENIED","STALE_AFTER_CRASH")
        check(snapshot()==after,"DENIAL_CHANGED_STATE")
        print(json.dumps({"status":"N08_SINGLE_HOST_PG16_CRASH_RECOVERY_PASS_LIMITED",
          "container_id":cid,"same_anonymous_volume":True,"crash_exit":down["exit_code"],
          "uncommitted_client_pid":pid,"uncommitted_client_exit":rc,"uncommitted_client_commit_sent":False,
          "before_identity":before_identity,"after_identity":after_identity,
          "same_cluster":True,"before_state_sha256":digest(before),"after_state_sha256":digest(after),
          "committed_revocation":"PRESERVED","committed_effect_and_receipt":"PRESERVED",
          "uncommitted_revocation":"ROLLED_BACK","stale_grant_after_restart":"DENIED",
          "host_count":1,"cross_host_failover":"NOT_TESTED","neon":"NOT_CONTACTED",
          "product_effect":"NONE","replay":False},sort_keys=True))
    finally:
        if pending is not None:
            if pending.poll() is None:
                pending.kill()
                pending.wait(timeout=3)
            pending.stdout.close()
            if not pending.stdin.closed:
                pending.stdin.close()

if __name__=="__main__":
    main()
