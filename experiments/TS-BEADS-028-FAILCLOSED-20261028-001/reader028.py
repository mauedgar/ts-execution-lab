#!/usr/bin/env python3
"""027 test client. Run strictly as separate nonprivileged Unix UID."""
import json,os,pathlib,sys,urllib.request,urllib.error
import pymysql
action=sys.argv[1]
port=int(os.environ["TS028_HTTP_PORT"])
sqlport=int(os.environ["TS028_SQL_PORT"])
read_secret=pathlib.Path(os.environ["TS028_READER_SECRET"]).read_text().strip()
database=os.environ["TS028_DB"]
if action=="probe":
 c=pymysql.connect(host="127.0.0.1",port=sqlport,user="ts028_reader",password=read_secret,database=database,connect_timeout=5,autocommit=True)
 with c.cursor() as cur:
  cur.execute("SELECT COUNT(*) FROM issues")
  count=int(cur.fetchone()[0])
  try:
   cur.execute("UPDATE issues SET title=title WHERE 1=0")
   update="UNEXPECTED_SQL_WRITE_ALLOWED"
  except Exception:
   update="SQL_WRITE_REFUSED"
 c.close()
 def call(method,path,data=None):
  request=urllib.request.Request("http://127.0.0.1:"+str(port)+path,method=method,
    headers={"Content-Type":"application/json"},data=json.dumps(data).encode() if data is not None else None)
  try:
   with urllib.request.urlopen(request,timeout=6) as response:return response.status
  except urllib.error.HTTPError as e:return e.code
 endpoints=[
  ("GET","/v0/beads/issues/ts028-root",None),
  ("GET","/v0/beads/context",None),
  ("POST","/v0/beads/issues:batchApply",{"actor":"TS028-READER","items":[]}),
  ("POST","/v0/beads/dependencies:add",{"actor":"TS028-READER","edges":[]}),
  ("POST","/v0/beads/issues:claimNext",{"actor":"TS028-READER"})]
 statuses=[{"method":m,"path":p,"status":call(m,p,d)} for m,p,d in endpoints]
 print(json.dumps({"sql_issue_count":count,"sql_write":update,"endpoints":statuses}))
elif action=="inventory":
 routefile=pathlib.Path(os.environ["TS028_ROUTES_FILE"])
 manifest=json.loads(routefile.read_text())
 assert len(manifest["routes"])==41 and sum(r["write"] for r in manifest["routes"])==20
 answers=[]
 for row in manifest["routes"]:
  path=row["path"].replace("{id}","ts028-root").replace("{key}","ts028-config")
  req=urllib.request.Request("http://127.0.0.1:"+str(port)+path,
     method=row["method"],headers={"Content-Type":"application/json"},
     data=(b"{}" if row["method"] in ("POST","PUT","PATCH") else None))
  try:
   with urllib.request.urlopen(req,timeout=5) as res:status=res.status
  except urllib.error.HTTPError as exc:status=exc.code
  answers.append({"operation":row["operation"],"method":row["method"],"path":row["path"],
    "write":row["write"],"status":status})
 print(json.dumps({"route_count":len(answers),"write_count":sum(x["write"] for x in answers),
  "all_protected_401":all(x["status"]==401 for x in answers if x["path"]!="/healthz"),
  "healthz_status":next(x["status"] for x in answers if x["path"]=="/healthz"),
  "responses":answers}))
elif action=="misconfig":
 body={"actor":"TS028-READER-NEGATIVE","provenance":"test://027/insecure-restart",
   "items":[{"kind":"dep_add","dep_add":{"source":{"id":"ts028-root"},"target":{"id":"ts028-insecure"},"type":"related"}}]}
 req=urllib.request.Request("http://127.0.0.1:"+str(port)+"/v0/beads/issues:batchApply",
    method="POST",headers={"Content-Type":"application/json"},data=json.dumps(body).encode())
 try:
  with urllib.request.urlopen(req,timeout=6) as response:status=response.status
 except urllib.error.HTTPError as e:status=e.code
 print(json.dumps({"status":status}))
else:raise RuntimeError("unsupported reader probe mode")
