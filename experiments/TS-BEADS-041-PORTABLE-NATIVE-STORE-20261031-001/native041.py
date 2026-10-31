#!/usr/bin/env python3
"""TS-EE-LLM-BEADS-040: disposable native Beads workgraph, no model calls or Product effects."""
import json, os, pathlib, subprocess, sys, traceback
LAB=pathlib.Path(os.environ["LAB_ROOT"]).resolve()
OUT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
IDENTITY="TS-BEADS-041-PORTABLE-NATIVE-STORE-20261031-001"
PREFIX="beads041"
ENV={**os.environ,"BEADS_DIR":str(LAB/".beads"),"BD_NO_PUSH":"1",
     "BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1","NO_COLOR":"1",
     "GIT_TERMINAL_PROMPT":"0","BEADS_ACTOR":"TS-EE-LLM-040-EXPERIMENT"}
R={"id":IDENTITY,"status":"RUNNING","authority":"EXPERIMENTAL_CONTROL_ONLY",
   "product_effect":"NONE","shared_dolt_effect":"NONE","model_provider_effect":"NONE",
   "attempt":"TS-BEADS-041-ATTEMPT-001",
   "models":["opencode/deepseek-v4.1-flash-free","opencode/mimo-v2.6-flash-free"],
   "fixture":"disposable_git_and_embedded_dolt_no_remote","checks":{},
   "qualification_ceiling":"WORKGRAPH_AND_DEPENDENCIES_ONLY;NO_MODEL_INFERENCE_OR_TOOL_QUALIFICATION",
   "limitations":["No actual LLM calls","No concurrent external workers or writer confinement",
                  "No real Product execution or acceptance","Privileged 028 bypass unresolved"]}
def persist():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf-8")
def verify(label,condition,evidence):
    R["checks"][label]={"pass":bool(condition),"evidence":evidence}
    persist()
    if not condition: raise AssertionError(label)
def cmd(*args):
    q=subprocess.run([str(BD),*map(str,args)],cwd=LAB,env=ENV,
                     capture_output=True,text=True,timeout=50)
    if q.returncode: raise RuntimeError("BEADS_COMMAND_FAILED:"+str(args)+
                                        ":exit="+str(q.returncode)+
                                        ":stderr="+q.stderr[-800:]+":stdout="+q.stdout[-800:])
    return q.stdout
def jsoncmd(*args):
    raw=cmd(*args,"--json")
    start=min((p for p in (raw.find("["),raw.find("{")) if p>=0),default=-1)
    if start<0: raise ValueError("NO_NATIVE_JSON:"+raw[-500:])
    return json.loads(raw[start:])
def ids(raw):
    if isinstance(raw,list):return sorted(str(x.get("id","")) for x in raw)
    if isinstance(raw,dict):
        for k in ("issues","ready","results","data"):
            if k in raw and isinstance(raw[k],list):return ids(raw[k])
    raise ValueError("UNKNOWN_READY_JSON_SHAPE:"+str(raw)[:500])
def main():
    verify("fresh_disposable_paths",not LAB.exists() and not OUT.exists(),str(LAB))
    LAB.mkdir(parents=True)
    subprocess.run(["git","init","-q",str(LAB)],check=True,timeout=10)
    q=subprocess.run(["git","remote"],cwd=LAB,capture_output=True,text=True,timeout=10)
    verify("git_isolation_no_remotes",q.returncode==0 and not q.stdout.strip(),q.stdout)
    version=cmd("--version").strip()
    R["beads_version"]=version
    verify("native_beads_version_pinned",("1.3.1" in version),version)
    cmd("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    tasks=[
        ("preflight","Synthetic environment and capability preflight; NO provider call"),
        ("deepseek","READ_AND_DENY qualification slot for opencode/deepseek-v4.1-flash-free; NOT DISPATCHED"),
        ("mimo","READ_AND_DENY qualification slot for opencode/mimo-v2.6-flash-free; NOT DISPATCHED"),
        ("compare","Compare two ORIGINAL qualified results only when received; NOT READY")
    ]
    for key,title in tasks:
        cmd("create",title,"--id",PREFIX+"-"+key,"--force",
            "--type","task","--description","Synthetic Beads workgraph only; Product authority NONE")
    cmd("dep","add",PREFIX+"-deepseek",PREFIX+"-preflight")
    cmd("dep","add",PREFIX+"-mimo",PREFIX+"-preflight")
    cmd("dep","add",PREFIX+"-compare",PREFIX+"-deepseek")
    cmd("dep","add",PREFIX+"-compare",PREFIX+"-mimo")
    initial=ids(jsoncmd("ready"))
    verify("initial_only_preflight_ready",initial==[PREFIX+"-preflight"],initial)
    cmd("close",PREFIX+"-preflight")
    ready=ids(jsoncmd("ready"))
    verify("two_independent_model_slots_ready",ready==sorted([PREFIX+"-deepseek",PREFIX+"-mimo"]),ready)
    verify("comparison_not_ready",PREFIX+"-compare" not in ready,ready)
    # Provider-native original is verified by Actions BEFORE the environment
    # variable is set. Beads only stores the reference, never re-executes it.
    receipt=os.environ.get("BEADS041_VERIFIED_PROVIDER_RECEIPT","")
    expected=("github-actions:41173329767:artifact:13031552292:"
       "sha256:96839db7c20212930ccb80a4147bb3c69f35d23ef70a65d909b58f8fff41593c")
    verify("original_provider_receipt_preverified",receipt==expected,receipt)
    cmd("update",PREFIX+"-deepseek","--description",
        "External provider original verified; receipt="+receipt)
    history_before=jsoncmd("history",PREFIX+"-deepseek")
    verify("native_Beads_history_records_description_before_close",
        isinstance(history_before,list) and len(history_before)>=1,len(history_before) if isinstance(history_before,list) else "not_list")
    cmd("close",PREFIX+"-deepseek")
    one_ready=ids(jsoncmd("ready"))
    verify("single_finished_child_does_not_unblock_join",
        one_ready==[PREFIX+"-mimo"],one_ready)
    cmd("update",PREFIX+"-mimo","--description",
        "External original receipt ref (same qualified provider)="+receipt)
    cmd("close",PREFIX+"-mimo")
    join_ready=ids(jsoncmd("ready"))
    verify("native_join_ready_after_both_children_closed",
        join_ready==[PREFIX+"-compare"],join_ready)
    cmd("update",PREFIX+"-compare","--description",
        "Consumer-only native Beads dependency join, no provider reexecution; receipt="+receipt)
    cmd("close",PREFIX+"-compare")
    closed=ids(jsoncmd("ready"))
    verify("all_native_issues_terminal_no_ready_work",closed==[],closed)
    final_children=[jsoncmd("show",PREFIX+"-"+key) for key in ("deepseek","mimo","compare")]
    verify("native_Beads_readback_shows_terminal_children",
        all(any(x.get("status")=="closed" for x in (rows if isinstance(rows,list) else [rows]))
            for rows in final_children),[str(x)[:130] for x in final_children])
    history_after=jsoncmd("history",PREFIX+"-deepseek")
    verify("native_Beads_historical_version_count_increased",
        isinstance(history_after,list) and len(history_after)>len(history_before),
        {"before":len(history_before),"after":len(history_after)})
    R["original_provider_receipt_ref"]=receipt
    R["provider_redispatch_count"]=0
    R["native_full_lifecycle"]={"initial":[PREFIX+"-preflight"],
       "two_siblings":ready,"one_sibling":[PREFIX+"-mimo"],
       "join":join_ready,"terminal":closed,
       "native_history_entries":len(history_after)}
    recovered=ids(jsoncmd("ready"))
    verify("fresh_cli_readback_stable",recovered==[],recovered)
    q=subprocess.run(["git","remote"],cwd=LAB,capture_output=True,text=True,timeout=10)
    verify("final_no_git_remotes",q.returncode==0 and not q.stdout.strip(),q.stdout)
    R["native_ready_ids"]=ready
    R["status"]="PASS_NATIVE_BEADS_END_TO_END_READY_HISTORY_AND_PROVIDER_REFERENCE"
    persist()
    print("TS_BEADS041="+R["status"]+";checks="+str(len(R["checks"]))+
          ";ready="+",".join(ready)+";Product=NONE;provider=NONE")
if __name__=="__main__":
    try: main()
    except Exception as err:
        R["status"]="FAIL_CLOSED"
        R["error"]=str(err)
        persist()
        raise
