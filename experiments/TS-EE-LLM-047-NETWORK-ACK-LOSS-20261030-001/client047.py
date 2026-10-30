#!/usr/bin/env python3
"""Separate synthetic HTTP consumer with durable intent/journal, no automatic retry."""
import argparse, json, sqlite3, urllib.request, urllib.error, urllib.parse

def open_db(path):
    c=sqlite3.connect(path, timeout=10, isolation_level=None)
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=FULL")
    c.execute("CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY AUTOINCREMENT,attempt TEXT NOT NULL,subject TEXT NOT NULL,owner TEXT NOT NULL,state TEXT NOT NULL,receipt TEXT)")
    return c
def write(c,a,state,receipt=None):
    c.execute("BEGIN IMMEDIATE")
    c.execute("INSERT INTO journal(attempt,subject,owner,state,receipt) VALUES(?,?,?,?,?)",
        (a["attempt"],a["subject"],a["owner"],state,receipt))
    c.execute("COMMIT")
def validate(a):
    if not all(isinstance(a.get(k),str) and a[k] for k in ("attempt","subject","owner")):raise ValueError("BAD_IDENTITY")
def emit(phase,**more):
    print(json.dumps({"phase":phase,**more},sort_keys=True,separators=(",",":")),flush=True)
def http(url,a,fault=None,method="GET"):
    full=url.rstrip("/")+"/effect"
    if method=="GET":
        full+="?"+urllib.parse.urlencode(a)
        req=urllib.request.Request(full,method="GET")
    else:
        full+="?"+urllib.parse.urlencode({"fault":fault or "none"})
        req=urllib.request.Request(full,data=json.dumps(a).encode(),headers={"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=5) as response:
            return response.status,json.loads(response.read())
    except urllib.error.HTTPError as e:
        return e.code,json.loads(e.read())
def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["dispatch","reconcile","inspect"])
    p.add_argument("--journal",required=True);p.add_argument("--url",default="http://127.0.0.1:1")
    p.add_argument("--attempt",default="");p.add_argument("--subject",default="");p.add_argument("--owner",default="")
    p.add_argument("--fault",default="none",choices=["none","drop_ack","crash_after_commit","crash_before_commit"])
    p.add_argument("--discard-ack",action="store_true")
    x=p.parse_args();a={"attempt":x.attempt,"subject":x.subject,"owner":x.owner}
    c=open_db(x.journal)
    if x.command=="inspect":
        rows=c.execute("SELECT seq,attempt,subject,owner,state,receipt FROM journal ORDER BY seq").fetchall()
        emit("JOURNAL",rows=rows,integrity=c.execute("PRAGMA integrity_check").fetchone()[0]);return
    validate(a)
    if x.command=="dispatch":
        # Adversarial duplicate is explicitly a test request, not automated retry.
        write(c,a,"INTENT")
        try:status,result=http(x.url,a,x.fault,"POST")
        except (OSError,ConnectionError,TimeoutError,ValueError) as e:
            write(c,a,"ACK_UNKNOWN")
            emit("ACK_UNKNOWN",error=type(e).__name__)
            raise SystemExit(75)
        if x.discard_ack:
            # Simulated lost ACK after real HTTP response, but before journal consumes it.
            write(c,a,"ACK_DISCARDED")
            emit("ACK_DISCARDED")
            raise SystemExit(76)
        phase=result.get("phase","BAD_RESPONSE")
        write(c,a,phase,result.get("receipt"))
        emit(phase,receipt=result.get("receipt"),http_status=status)
        if status==409:raise SystemExit(77)
        if status>=400:raise SystemExit(78)
    else:
        rows=c.execute("SELECT subject,owner,state,receipt FROM journal WHERE attempt=? ORDER BY seq",(a["attempt"],)).fetchall()
        if not rows or any(row[:2]!=(a["subject"],a["owner"]) for row in rows):
            emit("BLOCK_IDENTITY_OR_MISSING_INTENT")
            raise SystemExit(78)
        try:status,result=http(x.url,a,method="GET")
        except (OSError,ConnectionError,TimeoutError,ValueError) as e:
            write(c,a,"RECONCILE_UNKNOWN")
            emit("RECONCILE_UNKNOWN",error=type(e).__name__)
            raise SystemExit(75)
        if status==200 and result.get("phase")=="PROVIDER_CONFIRMED":
            state,receipt="NO_RETRY_CONFIRMED",result["receipt"]
        elif status==404 and result.get("phase")=="AUTHORITATIVE_ABSENT":
            state,receipt="ABSENT_REQUIRES_AUTHORITY",None
        else:
            state,receipt="BLOCK_IDENTITY_OR_BAD_RESPONSE",None
        write(c,a,state,receipt)
        emit(state,receipt=receipt,http_status=status)
        if state=="BLOCK_IDENTITY_OR_BAD_RESPONSE":raise SystemExit(77)
if __name__=="__main__":main()
