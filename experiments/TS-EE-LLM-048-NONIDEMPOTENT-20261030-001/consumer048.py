#!/usr/bin/env python3
"""Fail-closed consumer: durable reservation before network, never repeats an attempt."""
import argparse,json,sqlite3,urllib.request,urllib.error,urllib.parse

def db(path):
 c=sqlite3.connect(path,timeout=8,isolation_level=None)
 c.execute("PRAGMA busy_timeout=8000")
 c.execute("PRAGMA journal_mode=WAL")
 c.execute("PRAGMA synchronous=FULL")
 c.execute("CREATE TABLE IF NOT EXISTS attempts (attempt TEXT PRIMARY KEY,subject TEXT NOT NULL,owner TEXT NOT NULL,state TEXT NOT NULL,receipt TEXT)")
 c.execute("CREATE TABLE IF NOT EXISTS history (seq INTEGER PRIMARY KEY AUTOINCREMENT,attempt TEXT NOT NULL,state TEXT NOT NULL,receipt TEXT)")
 return c
def emit(phase,**kwargs):
 print(json.dumps({"phase":phase,**kwargs},sort_keys=True,separators=(",",":")),flush=True)
def identity(a):
 return all(isinstance(a[k],str) and a[k] for k in ("attempt","subject","owner"))
def update(c,attempt,state,receipt=None):
 c.execute("BEGIN IMMEDIATE")
 c.execute("UPDATE attempts SET state=?,receipt=? WHERE attempt=?",(state,receipt,attempt))
 c.execute("INSERT INTO history(attempt,state,receipt) VALUES(?,?,?)",(attempt,state,receipt))
 c.execute("COMMIT")
def current(c,a):
 row=c.execute("SELECT subject,owner,state,receipt FROM attempts WHERE attempt=?",(a["attempt"],)).fetchone()
 if row is None:return None
 if row[:2]!=(a["subject"],a["owner"]):return ("BLOCK_IDENTITY",None)
 if row[2]=="CONFIRMED":return ("NO_RETRY_CONFIRMED",row[3])
 return ("BLOCK_REPEAT_UNKNOWN",None)
def reserve(c,a):
 c.execute("BEGIN IMMEDIATE")
 row=c.execute("SELECT subject,owner,state,receipt FROM attempts WHERE attempt=?",(a["attempt"],)).fetchone()
 if row:
  c.execute("COMMIT")
  if row[:2]!=(a["subject"],a["owner"]):return ("BLOCK_IDENTITY",None)
  if row[2]=="CONFIRMED":return ("NO_RETRY_CONFIRMED",row[3])
  return ("BLOCK_REPEAT_UNKNOWN",None)
 c.execute("INSERT INTO attempts VALUES(?,?,?,'SEND_STARTED',NULL)",(a["attempt"],a["subject"],a["owner"]))
 c.execute("INSERT INTO history(attempt,state,receipt) VALUES(?,'SEND_STARTED',NULL)",(a["attempt"],))
 c.execute("COMMIT")
 return None
def main():
 p=argparse.ArgumentParser()
 p.add_argument("command",choices=["dispatch","reconcile","inspect","prepare"])
 p.add_argument("--journal",required=True);p.add_argument("--url",default="http://127.0.0.1:1")
 for s in ("attempt","subject","owner"):p.add_argument("--"+s,default="")
 p.add_argument("--fault",choices=["none","drop_after_commit","drop_before_commit","crash_after_commit"],default="none")
 p.add_argument("--discard-ack",action="store_true")
 a0=p.parse_args();a={k:getattr(a0,k) for k in ("attempt","subject","owner")}
 c=db(a0.journal)
 if a0.command=="inspect":
  emit("INSPECT",attempts=c.execute("SELECT * FROM attempts ORDER BY attempt").fetchall(),
       history=c.execute("SELECT * FROM history ORDER BY seq").fetchall(),
       integrity=c.execute("PRAGMA integrity_check").fetchone()[0]);return
 if not identity(a):emit("BAD_IDENTITY");raise SystemExit(79)
 if a0.command=="reconcile":
  result=current(c,a)
  if result is None:emit("NO_LOCAL_INTENT");raise SystemExit(78)
  emit(result[0],receipt=result[1])
  if result[0] in ("BLOCK_IDENTITY","BLOCK_REPEAT_UNKNOWN"):raise SystemExit(77)
  return
 reserved=reserve(c,a)
 if reserved is not None:
  emit(reserved[0],receipt=reserved[1])
  if reserved[0] in ("BLOCK_IDENTITY","BLOCK_REPEAT_UNKNOWN"):raise SystemExit(77)
  return
 if a0.command=="prepare":emit("RESERVED_BUT_NOT_SENT");return
 url=a0.url.rstrip("/")+"/effect?"+urllib.parse.urlencode({"fault":a0.fault})
 req=urllib.request.Request(url,data=json.dumps(a).encode(),headers={"Content-Type":"application/json"},method="POST")
 try:
  with urllib.request.urlopen(req,timeout=4) as res:
   response=json.loads(res.read())
 except (OSError,ValueError,urllib.error.URLError) as e:
  update(c,a["attempt"],"UNKNOWN")
  emit("ACK_UNKNOWN",transport_error=type(e).__name__)
  raise SystemExit(75)
 if a0.discard_ack:
  update(c,a["attempt"],"UNKNOWN")
  emit("ACK_DISCARDED")
  raise SystemExit(76)
 if response.get("phase")!="APPLIED" or not isinstance(response.get("receipt"),str):
  update(c,a["attempt"],"UNKNOWN")
  emit("INVALID_ACK_UNKNOWN")
  raise SystemExit(75)
 update(c,a["attempt"],"CONFIRMED",response["receipt"])
 emit("ACK_CONFIRMED",receipt=response["receipt"])
if __name__=="__main__":main()
