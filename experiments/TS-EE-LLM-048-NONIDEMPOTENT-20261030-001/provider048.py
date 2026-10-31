#!/usr/bin/env python3
"""Deliberately non-idempotent synthetic HTTP effect provider; no status endpoint."""
import argparse,hashlib,http.server,json,os,pathlib,socket,sqlite3,urllib.parse

def open_db(path):
 c=sqlite3.connect(path,timeout=8,isolation_level=None)
 c.execute("PRAGMA busy_timeout=8000")
 c.execute("PRAGMA journal_mode=WAL")
 c.execute("PRAGMA synchronous=FULL")
 c.execute("CREATE TABLE IF NOT EXISTS effects (event_id INTEGER PRIMARY KEY AUTOINCREMENT,attempt TEXT NOT NULL,subject TEXT NOT NULL,owner TEXT NOT NULL,receipt TEXT NOT NULL)")
 return c
def valid(a):
 return isinstance(a,dict) and all(isinstance(a.get(k),str) and a[k] for k in ("attempt","subject","owner"))
def serve(db,ready):
 class Handler(http.server.BaseHTTPRequestHandler):
  protocol_version="HTTP/1.1"
  def log_message(self,*args):pass
  def reply(self,status,data):
   raw=json.dumps(data,sort_keys=True).encode()
   self.send_response(status);self.send_header("Content-Type","application/json")
   self.send_header("Content-Length",str(len(raw)));self.end_headers()
   self.wfile.write(raw);self.wfile.flush()
  def do_GET(self):
   self.reply(405,{"phase":"NO_AUTHORITATIVE_STATUS"})
  def do_POST(self):
   url=urllib.parse.urlsplit(self.path)
   if url.path!="/effect":return self.reply(404,{"phase":"BAD_ROUTE"})
   try:
    n=int(self.headers.get("Content-Length","0"))
    if not 1<=n<=8192:return self.reply(400,{"phase":"BAD_LENGTH"})
    a=json.loads(self.rfile.read(n))
   except (ValueError,TypeError):return self.reply(400,{"phase":"BAD_BODY"})
   if not valid(a):return self.reply(400,{"phase":"BAD_IDENTITY"})
   fault=urllib.parse.parse_qs(url.query).get("fault",["none"])[0]
   if fault not in ("none","drop_after_commit","drop_before_commit","crash_after_commit"):return self.reply(400,{"phase":"BAD_FAULT"})
   if fault=="drop_before_commit":
    try:self.connection.shutdown(socket.SHUT_RDWR)
    except OSError:pass
    self.connection.close();self.close_connection=True;return
   c=open_db(db);c.execute("BEGIN IMMEDIATE")
   c.execute("INSERT INTO effects(attempt,subject,owner,receipt) VALUES(?,?,?,?)",(a["attempt"],a["subject"],a["owner"],"PENDING"))
   event_id=c.execute("SELECT last_insert_rowid()").fetchone()[0]
   receipt=hashlib.sha256(("048|"+str(event_id)+"|"+a["attempt"]+"|"+a["subject"]+"|"+a["owner"]).encode()).hexdigest()
   c.execute("UPDATE effects SET receipt=? WHERE event_id=?",(receipt,event_id))
   c.execute("COMMIT");c.close()
   if fault=="crash_after_commit":os._exit(73)
   if fault=="drop_after_commit":
    try:self.connection.shutdown(socket.SHUT_RDWR)
    except OSError:pass
    self.connection.close();self.close_connection=True;return
   self.reply(201,{"phase":"APPLIED","receipt":receipt,"event_id":event_id})
 open_db(db).close()
 server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
 server.daemon_threads=True
 ready.write_text(json.dumps({"host":"127.0.0.1","port":server.server_port})+"\n")
 print(json.dumps({"phase":"LISTENING","port":server.server_port}),flush=True)
 server.serve_forever(poll_interval=.1)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--db",required=True);p.add_argument("--ready",required=True)
 a=p.parse_args();serve(pathlib.Path(a.db),pathlib.Path(a.ready))
