#!/usr/bin/env python3
"""Independent fresh GitHub runner native Beads/Dolt store readback, NO writes or provider calls."""
import hashlib,json,os,pathlib,subprocess,sys
LAB=pathlib.Path(os.environ["LAB041_CONSUMER_ROOT"]).resolve()
BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
OUT=pathlib.Path(os.environ["RESULT041_JOIN"]).resolve()
E={**os.environ,"BEADS_DIR":str(LAB/".beads"),"BD_NO_PUSH":"1",
   "BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1","NO_COLOR":"1","GIT_TERMINAL_PROMPT":"0"}
def call(*cmd):
 p=subprocess.run([str(BD),*cmd,"--json"],cwd=LAB,env=E,capture_output=True,text=True,timeout=60)
 if p.returncode:raise RuntimeError("NATIVE_BD_ERROR:"+str(cmd)+":"+p.stderr[-380:])
 t=p.stdout
 i=min((x for x in (t.find("["),t.find("{")) if x>=0),default=-1)
 if i<0:raise RuntimeError("NATIVE_JSON_MISSING:"+str(cmd)+":"+t[-250:])
 return json.loads(t[i:])
def aslist(v):
 if isinstance(v,list):return v
 if isinstance(v,dict):
  for k in ("issues","data","ready","results"):
   if isinstance(v.get(k),list):return v[k]
 return [v]
def check(x,expr):
 if not expr:raise RuntimeError("FAIL_"+x)
 return x
def main():
 checks=[]
 expected="github-actions:41173329767:artifact:13031552292:sha256:96839db7c20212930ccb80a4147bb3c69f35d23ef70a65d909b58f8fff41593c"
 checks.append(check("fresh_extracted_Beads_directory",(LAB/".beads").is_dir()))
 checks.append(check("fresh_native_git_no_remote",
    subprocess.run(["git","remote"],cwd=LAB,capture_output=True,text=True).stdout.strip()==""))
 r=call("ready")
 checks.append(check("terminal_no_ready_issues",aslist(r)==[]))
 for key in ("deepseek","mimo","compare"):
  ident="beads041-"+key
  found=aslist(call("show",ident))
  checks.append(check("terminal_issue_"+key,len(found)==1 and found[0].get("id")==ident and found[0].get("status")=="closed"))
  desc=found[0].get("description","")
  checks.append(check("native_provider_reference_"+key,expected in str(desc)))
 hist=call("history","beads041-deepseek")
 checks.append(check("native_Dolt_history_preserved",len(aslist(hist))>=2))
 raw={"experiment":"TS-BEADS-041-PORTABLE-NATIVE-STORE-20261031-001",
      "execution_attempt":"TS-BEADS-041-JOIN-001",
      "status":"PASS_NATIVE_BEADS_STORE_PORTABLE_FRESH_RUNNER",
      "product_effect":"NONE","authority":"EXPERIMENTAL_CONTROL_ONLY",
      "checks":checks,"source_beads_store_sha256":os.environ["BEADS041_ARCHIVE_SHA256"],
      "same_provider_original_reference":expected,
      "provider_redispatch_count":0,"native_history_entries":len(aslist(hist))}
 OUT.write_text(json.dumps(raw,sort_keys=True,indent=2)+"\n",encoding="utf8")
 print("TS_BEADS041_JOIN=PASS_NATIVE_FRESH_RUNNER_READBACK;checks="+str(len(checks))+";Product=NONE",flush=True)
 print("TS_BEADS041_JOIN_RESULT_SHA256="+hashlib.sha256(OUT.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
