"""Synthetic-only PostgreSQL transaction mechanics; NOT a Tecnotron domain reducer."""
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import psycopg
from psycopg.types.json import Jsonb

URL = os.environ["DBOS_SYSTEM_DATABASE_URL"]
TABLE_PREFIX = "ts_remote_v4_"
TC = "TC-SYNTHETIC-001"
OP = "OP-SYNTHETIC-001"
ATT = "ATT-SYNTHETIC-001"

class StaleRevision(Exception):
    pass

class UnknownEffectFence(Exception):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def event_hash(previous, event):
    return hashlib.sha256((previous + "\n" + canonical(event)).encode()).hexdigest()

def connection():
    return psycopg.connect(URL)

def init_tables():
    with connection() as db:
        db.execute("CREATE TABLE IF NOT EXISTS ts_remote_v4_meta (id int PRIMARY KEY, rev int NOT NULL, head text NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS ts_remote_v4_objects (kind text NOT NULL, id text NOT NULL, doc jsonb NOT NULL, PRIMARY KEY(kind,id))")
        db.execute("CREATE TABLE IF NOT EXISTS ts_remote_v4_events (seq int PRIMARY KEY, previous text NOT NULL, digest text NOT NULL, event jsonb NOT NULL)")
        db.execute("INSERT INTO ts_remote_v4_meta VALUES (1,0,%s) ON CONFLICT (id) DO NOTHING", ("0"*64,))

def current_revision():
    with connection() as db:
        return db.execute("SELECT rev FROM ts_remote_v4_meta WHERE id=1").fetchone()[0]

def mutate(kind, identity, document, expected):
    # Product validates domain transitions/authority independently.
    # This fixture tests only transaction atomicity and UNKNOWN admission fencing.
    with connection() as db:
        rev, previous = db.execute("SELECT rev,head FROM ts_remote_v4_meta WHERE id=1 FOR UPDATE").fetchone()
        if rev != expected:
            raise StaleRevision(f"expected={expected};actual={rev}")
        if kind == "ExecutionAttempt":
            existing = db.execute("SELECT 1 FROM ts_remote_v4_objects WHERE kind=%s AND id=%s", (kind, identity)).fetchone()
            if existing is None:
                rows = db.execute("SELECT doc FROM ts_remote_v4_objects WHERE kind='ExecutionAttempt'").fetchall()
                if any(row[0].get("operation_id") == document.get("operation_id") and row[0].get("reconciliation_required") is True for row in rows):
                    raise UnknownEffectFence("original outcome UNKNOWN")
        event = {"seq":rev+1,"kind":kind,"id":identity,"post":document}
        digest = event_hash(previous,event)
        db.execute("INSERT INTO ts_remote_v4_objects(kind,id,doc) VALUES (%s,%s,%s) ON CONFLICT(kind,id) DO UPDATE SET doc=excluded.doc",
                   (kind,identity,Jsonb(document)))
        db.execute("INSERT INTO ts_remote_v4_events(seq,previous,digest,event) VALUES (%s,%s,%s,%s)",
                   (rev+1,previous,digest,Jsonb(event)))
        db.execute("UPDATE ts_remote_v4_meta SET rev=%s,head=%s WHERE id=1", (rev+1,digest))
    return rev+1

def verify():
    with connection() as db:
        rev, head = db.execute("SELECT rev,head FROM ts_remote_v4_meta WHERE id=1").fetchone()
        rows = db.execute("SELECT seq,previous,digest,event FROM ts_remote_v4_events ORDER BY seq").fetchall()
        stored = {(r[0],r[1]):r[2] for r in db.execute("SELECT kind,id,doc FROM ts_remote_v4_objects").fetchall()}
    assert len(rows)==rev, (len(rows),rev)
    prior="0"*64
    replay={}
    for expected_seq,(seq,previous,digest,event) in enumerate(rows,1):
        assert seq==expected_seq and previous==prior and digest==event_hash(prior,event)
        replay[(event["kind"],event["id"])]=event["post"]
        prior=digest
    assert head==prior and replay==stored
    return rev,stored

def boot():
    init_tables()
    assert current_revision()==0
    initial=[
        ("Milestone","M-SYNTHETIC-001",{"state":"PLANNED"}),
        ("TaskCycle",TC,{"state":"READY","obligations":[{"id":"CHECK","status":"PENDING"}]}),
        ("Operation",OP,{"state":"DEFINED","taskcycle_id":TC}),
        ("ExecutionAttempt",ATT,{"state":"PREPARED","operation_id":OP,"reconciliation_required":False}),
    ]
    for i,(kind,identity,doc) in enumerate(initial):
        assert mutate(kind,identity,doc,i)==i+1
    assert verify()[0]==4
    print("PASS|POSTGRES_V4|boot|aggregates=4|revision=4|audit=valid")

def race():
    assert verify()[0]==4
    sync=Barrier(2,timeout=20)
    def writer(kind,identity,doc):
        sync.wait()
        try:
            return "COMMITTED" if mutate(kind,identity,doc,4)==5 else "BAD"
        except StaleRevision:
            return "STALE_REVISION"
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(writer,"Milestone","M-SYNTHETIC-001",{"state":"ACTIVE"})
        b=pool.submit(writer,"TaskCycle",TC,{"state":"ACTIVE","obligations":[{"id":"CHECK","status":"PENDING"}]})
        results=sorted([a.result(timeout=30),b.result(timeout=30)])
    assert results==["COMMITTED","STALE_REVISION"],results
    assert verify()[0]==5
    print("PASS|POSTGRES_V4|race|commits=1|stale=1|revision=5|audit=valid")

def unknown():
    rev,objects=verify()
    assert rev==5
    mutate("ExecutionAttempt",ATT,{"state":"UNKNOWN","operation_id":OP,"reconciliation_required":True},rev)
    try:
        mutate("ExecutionAttempt","ATT-SYNTHETIC-RETRY-002",
               {"state":"PREPARED","operation_id":OP,"reconciliation_required":False},6)
        raise AssertionError("UNKNOWN fence did not reject")
    except UnknownEffectFence:
        pass
    assert verify()[0]==6
    with connection() as db:
        try:
            db.execute("UPDATE ts_remote_v4_meta SET rev=999 WHERE id=1")
            raise RuntimeError("simulated failure before commit")
        except RuntimeError:
            db.rollback()
    assert verify()[0]==6
    print("PASS|POSTGRES_V4|unknown|retry=blocked|rollback=atomic|revision=6")

def restore():
    rev,objects=verify()
    assert rev==6
    with connection() as db:
        events=[x[0] for x in db.execute("SELECT event FROM ts_remote_v4_events ORDER BY seq")]
        db.execute("CREATE TABLE IF NOT EXISTS ts_remote_v4_restored (kind text NOT NULL, id text NOT NULL, doc jsonb NOT NULL, PRIMARY KEY(kind,id))")
        db.execute("DELETE FROM ts_remote_v4_restored")
        for e in events:
            db.execute("INSERT INTO ts_remote_v4_restored VALUES (%s,%s,%s) ON CONFLICT(kind,id) DO UPDATE SET doc=excluded.doc",
                       (e["kind"],e["id"],Jsonb(e["post"])))
        clone={(r[0],r[1]):r[2] for r in db.execute("SELECT kind,id,doc FROM ts_remote_v4_restored")}
        assert clone==objects
    print("PASS|POSTGRES_V4|restore|replayed_events=6|objects=4")

if __name__=="__main__":
    {"boot":boot,"race":race,"unknown":unknown,"restore":restore}[sys.argv[1]]()
