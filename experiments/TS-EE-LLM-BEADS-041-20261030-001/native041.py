#!/usr/bin/env python3
"""Beads 041: isolated native evidence-attestation join and dependency unblocking.

Host JSONL originals are referenced by SHA, not copied/revalidated on CI.
No provider dispatch, no Product effects, no privileged-bypass proof.
"""
from __future__ import annotations
import json,os,pathlib,re,subprocess,traceback

ROOT=pathlib.Path(os.environ["LAB_ROOT"]).resolve()
OUT=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
BD=pathlib.Path(os.environ["BD_BIN"]).resolve()
INPUT=pathlib.Path(os.environ["ATTESTATIONS_PATH"]).resolve()
PREFIX="llm041"
E={**os.environ,"BEADS_DIR":str(ROOT/".beads"),"BD_NO_PUSH":"1",
   "BD_DOLT_AUTO_PUSH":"false","BD_NON_INTERACTIVE":"1","NO_COLOR":"1",
   "GIT_TERMINAL_PROMPT":"0","BEADS_ACTOR":"TS-EE-LLM-041-EXPERIMENT"}
R={"id":"TS-EE-LLM-BEADS-041-20261030-001","attempt":"TS-EE-LLM-BEADS-041-ATTEMPT-001",
   "status":"RUNNING","authority":"EXPERIMENTAL_CONTROL_ONLY",
   "product_effect":"NONE","shared_dolt_effect":"NONE","provider_effect":"NONE",
   "original_log_bytes_available_on_runner":False,
   "evidence_level":"HOST_ATTESTATION_WITH_ORIGINAL_SHA_ONLY",
   "not_qualified":["native rehash of host-only JSONLs","model review or implementation",
                    "actual parallel model execution","privileged writer exclusivity",
                    "Product acceptance, TaskCycle or Beads adoption"],
   "checks":{}}
def save():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(R,sort_keys=True,indent=2)+"\n",encoding="utf8")
def check(name,ok,evidence=None):
    R["checks"][name]={"result":"PASS" if ok else "FAIL","evidence":evidence}
    save()
    if not ok:raise AssertionError(name)
def run(*args):
    q=subprocess.run([str(BD),*map(str,args)],cwd=ROOT,env=E,
                     capture_output=True,text=True,timeout=55)
    if q.returncode:raise RuntimeError("BD_FAILED:"+repr(args)+":"+q.stderr[-500:]+":"+q.stdout[-300:])
    return q.stdout
def js(*args):
    t=run(*args,"--json");p=min((i for i in (t.find("["),t.find("{")) if i>=0),default=-1)
    if p<0:raise RuntimeError("BD_NO_JSON:"+t[-300:])
    return json.loads(t[p:])
def ids(raw):
    if isinstance(raw,list):return sorted(str(x.get("id","")) for x in raw)
    if isinstance(raw,dict):
        for k in ("issues","ready","results","data"):
            if isinstance(raw.get(k),list):return ids(raw[k])
    raise RuntimeError("BD_READY_SHAPE_UNKNOWN")
def ready():return ids(js("ready"))
def remote_free():
    q=subprocess.run(["git","remote"],cwd=ROOT,capture_output=True,text=True,timeout=10)
    return q.returncode==0 and not q.stdout.strip()
def qualified_manifest(m):
    if m.get("experiment_id")!="TS-EE-LLM-BEADS-041-20261030-001":return False
    if m.get("evidence_class")!="HOST_OBSERVED_ATTESTATIONS_NOT_RAW_JSONL":return False
    if m.get("source_fixture_commit")!="8e50200880f3b266673a2563d62cda6175eb545d":return False
    a=m.get("models",[])
    if len(a)!=2 or {x.get("slot") for x in a}!={"deepseek","mimo"}:return False
    for x in a:
        if not re.fullmatch(r"[A-F0-9]{64}",x.get("sha256","")):return False
        if x.get("native_exit")!=0 or x.get("tool_calls")!=2 or x.get("worktree_clean") is not True:return False
        if x.get("allowed_read")!="README.md" or x.get("denied_read")!="RESTRICTED.txt":return False
        if x.get("marker")!="LANTERN-040-CEDAR":return False
        if not x.get("attempt_id") or not x.get("session_id") or not x.get("original_jsonl_path"):return False
        if not x.get("model_id","").startswith("opencode/") or x.get("bytes",0)<100:return False
    return True
def main():
    check("fresh_disposable_workspace",not ROOT.exists() and not OUT.exists(),str(ROOT))
    m=json.loads(INPUT.read_text(encoding="utf8"))
    check("evidence_manifest_shape_and_original_sha_refs",qualified_manifest(m),
          [x.get("sha256") for x in m.get("models",[])])
    check("advisories_preserved_exactly",
          {x["slot"]:x["final_step_finish"] for x in m["models"]}=={"deepseek":True,"mimo":False}
          and {x["slot"]:x["requested_order_followed"] for x in m["models"]}=={"deepseek":True,"mimo":False},
          "MiMo missing final step_finish and inverse order preserved")
    ROOT.mkdir(parents=True)
    subprocess.run(["git","init","-q",str(ROOT)],check=True,timeout=10)
    check("new_git_has_no_remote",remote_free(),True)
    vers=run("--version").strip()
    check("native_beads_v1_3_1",("1.3.1" in vers),vers)
    run("init","--quiet","--stealth","--skip-agents","--skip-hooks","--non-interactive")
    for n,desc in (("preflight","Verify two host-observed attestations, not raw event bytes"),
                   ("deepseek","Consume one DeepSeek host-qualified read/deny attestation"),
                   ("mimo","Consume one MiMo host-qualified read/deny attestation"),
                   ("compare","Compare native Beads dependency-joined evidence")):
        run("create",desc,"--id",PREFIX+"-"+n,"--force","--type","task",
            "--description","EXPERIMENTAL_ONLY;Product=NONE")
    for src,dep in (("deepseek","preflight"),("mimo","preflight"),
                    ("compare","deepseek"),("compare","mimo")):
        run("dep","add",PREFIX+"-"+src,PREFIX+"-"+dep)
    check("only_preflight_ready_initially",ready()==[PREFIX+"-preflight"],ready())
    run("close",PREFIX+"-preflight")
    check("both_model_slots_ready_after_preflight",
          ready()==sorted([PREFIX+"-deepseek",PREFIX+"-mimo"]),ready())
    check("comparison_initially_blocked",PREFIX+"-compare" not in ready(),ready())
    byslot={x["slot"]:x for x in m["models"]}
    for slot in ("deepseek","mimo"):
        e=byslot[slot]
        description=("ATTESTED_HOST_RESULT_ONLY|model="+e["model_id"]+
                     "|attempt="+e["attempt_id"]+"|session="+e["session_id"]+
                     "|sha256="+e["sha256"]+"|original_bytes_on_runner=false")
        run("update",PREFIX+"-"+slot,"--description",description)
        show=run("show",PREFIX+"-"+slot,"--json")
        check(slot+"_beads_native_evidence_ref_persisted",
              e["sha256"] in show and e["attempt_id"] in show, e["sha256"])
        run("close",PREFIX+"-"+slot)
        current=ready()
        expected=[PREFIX+"-mimo"] if slot=="deepseek" else [PREFIX+"-compare"]
        check(slot+"_dependency_join_ready_exact",current==expected,current)
        check(slot+"_fresh_cli_readback",ready()==expected,ready())
    verdict={
      "selection":"NO_UNIVERSAL_WINNER_ONE_RUN_PER_MODEL",
      "read_deny":"BOTH_BOUNDED_PASS_AS_HOST_ATTESTED",
      "deepseek":"FINAL_STEP_FINISH_PRESENT_AND_REQUESTED_ORDER_FOLLOWED",
      "mimo":"FINAL_STEP_FINISH_MISSING_AND_ORDER_REVERSED",
      "original_bytes_verified_in_this_experiment":False,
      "inference_cost_comparison":"NOT_QUALIFIED",
      "next_model_gate":"ISOLATED_IMPLEMENTATION_FIXTURES_ONLY_AFTER_NEW_EXPLICIT_SCOPE"}
    check("comparison_deterministic_and_not_misrepresented",
          verdict["original_bytes_verified_in_this_experiment"] is False
          and byslot["deepseek"]["final_step_finish"] is True
          and byslot["mimo"]["final_step_finish"] is False,verdict["selection"])
    run("update",PREFIX+"-compare","--description",
        "DETERMINISTIC_COMPARISON|BOTH_READ_DENY_BOUNDED_PASS|NO_UNIVERSAL_WINNER|RAW_HOST_ONLY")
    check("comparison_advisory_persisted",
          "NO_UNIVERSAL_WINNER" in run("show",PREFIX+"-compare","--json"),True)
    run("close",PREFIX+"-compare")
    check("all_synthetic_tasks_finished",ready()==[],ready())
    check("final_fresh_cli_readback",ready()==[],ready())
    check("final_no_git_remote",remote_free(),True)
    R["comparison"]=verdict
    R["models"]={k:{"attempt_id":v["attempt_id"],"session_id":v["session_id"],
                     "original_sha256":v["sha256"],"original_host_path":v["original_jsonl_path"]}
                 for k,v in byslot.items()}
    R["status"]="PASS_BOUNDED_NATIVE_BEADS_ATTESTATION_JOIN_WITH_RAW_PROVENANCE_LIMIT"
    save()
    print("TS_EE_LLM_BEADS041="+R["status"]+";checks="+str(len(R["checks"]))+
          ";native_compare_closed=1;original_raw_bytes_on_runner=0;Product=NONE")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        R["status"]="FAIL_CLOSED";R["error"]=str(exc);save();raise
