"""A01 NONPRODUCT fixture: PostgreSQL authority and effect serialization.
One ephemeral Actions host only. No real Developer grants or Product connections.
"""
import json
import os
import select
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

ROLES = {"postgres": "a01-disposable-admin",
         "rs011_authority": "a01-disposable-authority",
         "rs011_writer": "a01-disposable-writer",
         "rs011_observer": "a01-disposable-observer"}
SUBJECT = dict(repo="synthetic", branch="fixture", tree="tree1", taskcycle="tc1",
               operation="op1", attempt="att1", subject="effect1")
WRITER, AUTH, OBS = "rs011_writer", "rs011_authority", "rs011_observer"
PSQL = "/usr/bin/psql"
BEGIN = "BEGIN ISOLATION LEVEL READ COMMITTED;"
results = {}

def check(ok, name):
    if not ok:
        raise RuntimeError(name)

def fixture():
    check(os.environ.get("GITHUB_ACTIONS") == "true", "NOT_ACTIONS")
    check(os.environ.get("TS_RS011_A01_DISPOSABLE") == "yes", "NOT_DISPOSABLE")
    check(sys.version_info[:3] == (3, 15, 2), "PYTHON_VERSION")

def args(role, app, port=5432):
    check(role in ROLES, "ROLE")
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PGPASSWORD": ROLES[role],
           "PGAPPNAME": app, "PGHOSTADDR": "127.0.0.1", "PGSSLMODE": "disable",
           "PGGSSENCMODE": "disable", "PGCONNECT_TIMEOUT": "3",
           "PGOPTIONS": "-c statement_timeout=12000 -c lock_timeout=8000 -c idle_in_transaction_session_timeout=18000"}
    return [PSQL, "-X", "-qAt", "-w", "-v", "ON_ERROR_STOP=1",
            "-h", "127.0.0.1", "-p", str(port), "-U", role, "-d", "postgres"], env

def invoke(sql, role, app="a01_direct", port=5432, error=None):
    cmd, env = args(role, app, port)
    p = subprocess.run(cmd, input="\\set VERBOSITY verbose\n"+sql+"\n",
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env, timeout=20)
    check(len(p.stdout)+len(p.stderr) < 65536, "OUTPUT_LIMIT")
    if error:
        check(p.returncode != 0 and error in p.stderr, "EXPECTED_ERROR_"+error)
    else:
        check(p.returncode == 0, "PSQL_ERROR_"+app+"_"+p.stderr[-800:])
    return p.stdout.strip(), p.returncode

def query(sql, role=OBS):
    return invoke(sql, role)[0]

def literal(s):
    return "'" + s.replace("'", "''") + "'"

def apply(scope, subject=None, version=1, payload=None, mid=None):
    s = SUBJECT if subject is None else subject
    p = {"value": "new"} if payload is None else payload
    return ("SELECT rs011_a01.apply_effect("
            + literal(scope) + "," + str(version) + ","
            + literal(json.dumps(s)) + "::jsonb,"
            + literal(mid or "mutation-"+scope) + ","
            + literal(json.dumps(p)) + "::jsonb);")

def revoke(scope):
    return "SELECT rs011_a01.revoke_grant("+literal(scope)+",1);"

def state(scope):
    s = literal(scope)
    return query("SELECT g.version||'|'||g.active||'|'||h.revision||'|'||"
                 "(SELECT count(*) FROM rs011_a01.events WHERE scope="+s+")||'|'||"
                 "(SELECT count(*) FROM rs011_a01.receipts WHERE scope="+s+")"
                 " FROM rs011_a01.grants g JOIN rs011_a01.head h USING(scope)"
                 " WHERE g.scope="+s+";")

class Session:
    """A dedicated psql child; explicit send/observe/commit barrier, no sleep-held lock."""
    def __init__(self, role, app):
        cmd, env = args(role, app)
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, env=env, bufsize=0)
        self.buffer = b""
        self.serial = 0
    def send(self, sql):
        self.serial += 1
        marker = "A01_END_"+str(self.serial)
        self.p.stdin.write((sql+"\n\\echo "+marker+"\n").encode())
        self.p.stdin.flush()
        return marker
    def read(self, marker, seconds=10):
        end = time.monotonic()+seconds
        target = (marker+"\n").encode()
        while target not in self.buffer:
            left = end-time.monotonic()
            check(left > 0, "SESSION_DEADLINE")
            ready, _, _ = select.select([self.p.stdout], [], [], left)
            check(bool(ready), "SESSION_TIMEOUT")
            data = os.read(self.p.stdout.fileno(), 4096)
            check(bool(data), "SESSION_CLOSED_"+self.buffer.decode(errors="replace")[-500:])
            self.buffer += data
            check(len(self.buffer) < 65536, "SESSION_OUTPUT_LIMIT")
        data, self.buffer = self.buffer.split(target, 1)
        return data.decode().strip()
    def call(self, sql):
        return self.read(self.send(sql))
    def close(self):
        if self.p.poll() is None:
            self.p.kill()
        self.p.wait(timeout=3)
        self.p.stdin.close()
        self.p.stdout.close()

def blocking(waiter, blocker):
    end=time.monotonic()+5
    sql=("SELECT count(*) FROM pg_stat_activity WHERE pid="+str(waiter)
         +" AND wait_event_type='Lock' AND "+str(blocker)+"=ANY(pg_blocking_pids(pid));")
    while time.monotonic()<end:
        if query(sql, "postgres") == "1":
            return True
        time.sleep(.06)
    return False

def ordered(scope, first_role, first_sql, second_role, second_sql, first_answer, second_answer):
    first = second = None
    try:
        first=Session(first_role,"a01_"+scope+"_first")
        second=Session(second_role,"a01_"+scope+"_second")
        pid1=int(first.call("SELECT pg_backend_pid();"))
        pid2=int(second.call("SELECT pg_backend_pid();"))
        check(pid1 != pid2, "IDENTICAL_BACKEND")
        check(first.call(BEGIN+"\n"+first_sql)==first_answer, "FIRST_RESULT")
        check(second.call(BEGIN)=="", "SECOND_BEGIN")
        pending=second.send(second_sql)
        check(blocking(pid2,pid1), "NO_EXACT_BLOCKER_EDGE")
        # First explicit commit only AFTER server observes second waiting on first.
        check(first.call("COMMIT;")=="", "FIRST_COMMIT")
        check(second.read(pending)==second_answer, "SECOND_RESULT")
        check(second.call("COMMIT;")=="", "SECOND_COMMIT")
        return {"first_pid":pid1,"second_pid":pid2,"exact_blocker_edge":True,
                "first_result":first_answer,"second_result":second_answer,
                "final":state(scope)}
    finally:
        for s in (second,first):
            if s is not None:
                s.close()

def timeout_case():
    hold=None
    try:
        hold=Session(AUTH,"a01_timeout_holder")
        check(hold.call(BEGIN+"\n"+revoke("timeout"))=="REVOKED","HOLD")
        invoke(BEGIN+"\nSET LOCAL lock_timeout='300ms';\n"+apply("timeout"),
               WRITER,"a01_timeout_writer",error="55P03")
        check(hold.call("ROLLBACK;")=="","HOLDER_ROLLBACK")
        check(state("timeout")=="1|true|0|0|0","TIMEOUT_EFFECT")
        return {"sqlstate":"55P03","effect":"NONE","final":state("timeout")}
    finally:
        if hold is not None:
            hold.close()

def recv_exact(sock,n):
    data=bytearray()
    while len(data)<n:
        part=sock.recv(n-len(data))
        if not part:
            raise EOFError("SOCKET_CLOSED")
        data.extend(part)
    return bytes(data)

def ack_case():
    """One local wire fault: omit actual backend CommandComplete(COMMIT) from client."""
    dropped=threading.Event()
    faults=[]
    listener=socket.socket()
    listener.bind(("127.0.0.1",0))
    listener.listen(1)
    listener.settimeout(8)
    port=listener.getsockname()[1]
    def relay():
        try:
            with listener:
                client,_=listener.accept()
                with client, socket.create_connection(("127.0.0.1",5432),timeout=5) as server:
                    client.settimeout(12)
                    server.settimeout(12)
                    def upstream():
                        try:
                            while True:
                                x=client.recv(4096)
                                if not x:
                                    return
                                server.sendall(x)
                        except OSError:
                            return
                    t=threading.Thread(target=upstream,daemon=True)
                    t.start()
                    while True:
                        h=recv_exact(server,5)
                        size=struct.unpack("!I",h[1:])[0]
                        check(4<=size<=65536,"PROTOCOL_FRAME_LIMIT")
                        payload=recv_exact(server,size-4)
                        if h[:1]==b"C" and payload==b"COMMIT\x00":
                            dropped.set()
                            # The real server completed COMMIT. Neither its
                            # CommandComplete nor subsequent ReadyForQuery is forwarded.
                            client.shutdown(socket.SHUT_RDWR)
                            return
                        client.sendall(h+payload)
        except Exception as exc:
            faults.append(type(exc).__name__)
    t=threading.Thread(target=relay,daemon=True)
    t.start()
    cmd,env=args(WRITER,"a01_lost_ack",port)
    p=subprocess.run(cmd,input=BEGIN+"\n"+apply("ack")+"\nCOMMIT;\n",
                     text=True,capture_output=True,env=env,timeout=20)
    t.join(timeout=3)
    check(not t.is_alive() and not faults and dropped.is_set(),"ACK_FAULT_NOT_OBSERVED")
    check(p.returncode!=0,"CLIENT_DID_NOT_LOSE_ACK")
    # Classify client effect UNKNOWN first, then reconcile SAME original
    # mutation through a distinct READ ONLY connection, no replay.
    receipt=query("SELECT mutation_id||'|'||grant_version||'|'||revision||'|'||"
                  "((payload='{\"value\":\"new\"}'::jsonb) AND subject="
                  +literal(json.dumps(SUBJECT))+"::jsonb)::text"
                  " FROM rs011_a01.receipts WHERE scope='ack';")
    check(receipt=="mutation-ack|1|1|true" and state("ack")=="1|true|1|1|1","ACK_RECONCILE")
    return {"wire_fault":"POSTGRES_COMMAND_COMPLETE_COMMIT_DROPPED",
            "client_exit":p.returncode,"initial_effect":"UNKNOWN",
            "reconciled_effect":"CONFIRMED","receipt":receipt,"replay":False}

def main():
    fixture()
    version=query("SHOW server_version_num;", "postgres")
    check(version=="160015","PG16_15_REQUIRED")
    invoke(Path(__file__).with_name("schema.sql").read_text(), "postgres", "a01_setup")
    # N01: both valid serial orders, including exact backend blocker.
    r=ordered("revoke_first",AUTH,revoke("revoke_first"),WRITER,apply("revoke_first"),
              "REVOKED","DENIED")
    e=ordered("effect_first",WRITER,apply("effect_first"),AUTH,revoke("effect_first"),
              "APPLIED","REVOKED")
    check(r["final"]=="2|false|0|0|0" and e["final"]=="2|false|1|1|1","N01")
    results["N01"]={"revoke_first":r,"effect_first":e}
    # N02: stale cached version and subject after committed revocation.
    check(query(revoke("stale"),AUTH)=="REVOKED","N02_REVOKE")
    check(query(apply("stale"),WRITER)=="DENIED" and state("stale")=="2|false|0|0|0","N02")
    results["N02"]="DENIED_STALE_CACHE"
    # N03: each identity component, version, expiry, and role privileges.
    for key in SUBJECT:
        changed=dict(SUBJECT); changed[key]="wrong"
        check(query(apply("wrong",subject=changed),WRITER)=="DENIED","N03_"+key)
    check(query(apply("wrong",version=2),WRITER)=="DENIED","N03_VERSION")
    check(query(apply("expired"),WRITER)=="DENIED","N03_EXPIRED")
    invoke("UPDATE rs011_a01.grants SET active=true WHERE scope='wrong';",WRITER,error="42501")
    invoke(revoke("wrong"),WRITER,error="42501")
    invoke(apply("wrong"),AUTH,error="42501")
    invoke(apply("wrong"),OBS,error="42501")
    check(state("wrong")=="1|true|0|0|0" and state("expired")=="1|true|0|0|0","N03_EFFECT")
    results["N03"]="DENIED_IDENTITY_VERSION_EXPIRY_ROLE"
    # N04: a different payload with the SAME original mutation ID cannot write.
    check(query(apply("duplicate"),WRITER)=="APPLIED","N04_ORIGINAL")
    check(query(apply("duplicate",payload={"value":"changed"}),WRITER)=="CONFLICT","N04_CONFLICT")
    check(state("duplicate")=="1|true|1|1|1","N04_COUNTS")
    check(query("SELECT payload::text FROM rs011_a01.receipts WHERE scope='duplicate';")
          == '{"value": "new"}',"N04_PAYLOAD")
    results["N04"]="CONFLICT_UNCHANGED_RECEIPT"
    results["N05"]=timeout_case()
    results["N06"]={"one_host_exact_blocker_edges":True,"two_physical_hosts":"NOT_TESTED"}
    results["N07"]=ack_case()
    # N08: transactional revocation rollback, then commit and new connections.
    check(query(BEGIN+"\n"+revoke("rollback")+"\nROLLBACK;",AUTH)=="REVOKED","N08_ROLLBACK")
    check(state("rollback")=="1|true|0|0|0","N08_ROLLBACK_STATE")
    check(query(revoke("rollback"),AUTH)=="REVOKED","N08_COMMIT")
    check(query(apply("rollback"),WRITER)=="DENIED" and state("rollback")=="2|false|0|0|0","N08_RECONNECT")
    results["N08"]={"rollback_and_new_connection":"PASS","server_restart_or_failover":"NOT_TESTED"}
    print(json.dumps({"status":"A01_OPTION_A_DISPOSABLE_PG16_PASS_LIMITED",
                      "server_version":version,"host_count":1,"cases":results,
                      "product_effect":"NONE","neon":"NOT_CONTACTED",
                      "authority_transfer":"NONE"},sort_keys=True))

if __name__=="__main__":
    main()
