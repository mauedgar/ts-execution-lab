#!/usr/bin/env python3
"""127.0.0.1 HTTP synthetic provider; durable SQLite, explicit ACK faults."""
import argparse, hashlib, http.server, json, os, pathlib, socket, sqlite3, urllib.parse

def open_db(path):
    c=sqlite3.connect(path,timeout=10,isolation_level=None)
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=FULL")
    c.execute("CREATE TABLE IF NOT EXISTS effects (attempt TEXT PRIMARY KEY,subject TEXT NOT NULL,owner TEXT NOT NULL,receipt TEXT NOT NULL,units INTEGER NOT NULL CHECK(units=1))")
    return c

def valid(x):
    return isinstance(x,dict) and all(isinstance(x.get(k),str) and x[k] for k in ("attempt","subject","owner"))

def serve(db_path,ready_path):
    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version="HTTP/1.1"
        def log_message(self,*args): pass
        def reply(self,status,data):
            payload=json.dumps(data,sort_keys=True,separators=(",",":")).encode()
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            self.wfile.flush()
        def do_POST(self):
            u=urllib.parse.urlsplit(self.path)
            if u.path!="/effect": return self.reply(404,{"phase":"BAD_ROUTE"})
            try:
                n=int(self.headers.get("Content-Length","0"))
                if not 1<=n<=8192: return self.reply(400,{"phase":"BAD_LENGTH"})
                a=json.loads(self.rfile.read(n))
            except (ValueError,KeyError): return self.reply(400,{"phase":"BAD_PAYLOAD"})
            if not valid(a): return self.reply(400,{"phase":"BAD_IDENTITY"})
            fault=urllib.parse.parse_qs(u.query).get("fault",["none"])[0]
            if fault not in ("none","drop_ack","crash_after_commit","crash_before_commit"):
                return self.reply(400,{"phase":"BAD_FAULT"})
            c=open_db(db_path)
            try:
                c.execute("BEGIN IMMEDIATE")
                prev=c.execute("SELECT subject,owner,receipt FROM effects WHERE attempt=?",(a["attempt"],)).fetchone()
                if prev:
                    if prev[:2]!=(a["subject"],a["owner"]):
                        c.execute("ROLLBACK");return self.reply(409,{"phase":"BLOCK_IDENTITY"})
                    c.execute("COMMIT");return self.reply(200,{"phase":"ALREADY_CONFIRMED","receipt":prev[2]})
                receipt=hashlib.sha256(("047|"+a["attempt"]+"|"+a["subject"]+"|"+a["owner"]).encode()).hexdigest()
                c.execute("INSERT INTO effects VALUES(?,?,?,?,1)",(a["attempt"],a["subject"],a["owner"],receipt))
                if fault=="crash_before_commit":os._exit(74)
                c.execute("COMMIT")
                if fault=="crash_after_commit":os._exit(73)
                if fault=="drop_ack":
                    # Real transport-layer loss: commit succeeded; no HTTP response reaches client.
                    try:self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:pass
                    self.connection.close()
                    self.close_connection=True
                    return
                return self.reply(201,{"phase":"APPLIED_ACK","receipt":receipt})
            finally:
                c.close()
        def do_GET(self):
            u=urllib.parse.urlsplit(self.path)
            if u.path!="/effect":return self.reply(404,{"phase":"BAD_ROUTE"})
            args=urllib.parse.parse_qs(u.query)
            a={k:args.get(k,[""])[0] for k in ("attempt","subject","owner")}
            if not valid(a):return self.reply(400,{"phase":"BAD_IDENTITY"})
            c=open_db(db_path)
            try:
                found=c.execute("SELECT subject,owner,receipt,units FROM effects WHERE attempt=?",(a["attempt"],)).fetchone()
            finally:c.close()
            if found is None:return self.reply(404,{"phase":"AUTHORITATIVE_ABSENT"})
            if found[:2]!=(a["subject"],a["owner"]):
                return self.reply(409,{"phase":"BLOCK_IDENTITY"})
            return self.reply(200,{"phase":"PROVIDER_CONFIRMED","receipt":found[2],"units":found[3]})
    open_db(db_path).close()
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    server.daemon_threads=True
    ready_path.write_text(json.dumps({"host":"127.0.0.1","port":server.server_port})+"\n")
    print(json.dumps({"phase":"PROVIDER_LISTENING","port":server.server_port}),flush=True)
    server.serve_forever(poll_interval=.1)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--db",required=True);p.add_argument("--ready",required=True)
    a=p.parse_args();serve(pathlib.Path(a.db),pathlib.Path(a.ready))
