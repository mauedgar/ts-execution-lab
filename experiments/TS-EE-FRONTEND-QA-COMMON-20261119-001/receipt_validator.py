#!/usr/bin/env python3
"""Frontend QA v0 report checker. Output is never a provider or Product attestation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

WIDTHS=(320,375,768,1440)
SCENARIOS=("viewport","routing","history","deep_link_refresh","sku_negative",
           "keyboard_focus","a11y_basic","console_http")
STAGES=("identity","dependencies","integration","build","browser")
STATES=("PASS","FAIL","BLOCKED","NOT_RUN","SKIPPED")
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")
NAME=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ATTEMPT=re.compile(r"^[A-Z0-9][A-Z0-9_-]{8,127}$")

def evaluate(report,artifact_root=None,expected_commit=None,expected_tree=None,expected_run_id=None):
    errors=[]
    def need(ok,code):
        if not ok: errors.append(code)
    if not isinstance(report,dict):
        return {"status":"INVALID_REPORT","errors":["report_not_object"]}
    need(report.get("schema")=="ts-ee/frontend-browser-qa/v0","wrong_schema")
    need(report.get("product_effect")=="NONE","product_effect_not_none")
    need(bool(ATTEMPT.fullmatch(str(report.get("attempt","")))),"bad_attempt")
    need(report.get("reported_verdict") in ("PASS","FAIL","PARTIAL","NOT_RUN"),"bad_verdict")
    s=report.get("source")
    if not isinstance(s,dict):s={}
    need(s.get("subject_kind") in ("SYNTHETIC","PRODUCT_PREVIEW"),"bad_subject_kind")
    need(isinstance(s.get("repository"),str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",s.get("repository","")) is not None,"bad_repository")
    need(bool(HEX40.fullmatch(str(s.get("commit","")))),"bad_commit")
    need(bool(HEX40.fullmatch(str(s.get("tree","")))),"bad_tree")
    if expected_commit is not None:need(s.get("commit")==expected_commit,"expected_commit_mismatch")
    if expected_tree is not None:need(s.get("tree")==expected_tree,"expected_tree_mismatch")
    runner=report.get("runner")
    if not isinstance(runner,dict):runner={}
    need(runner.get("engine") in ("PLAYWRIGHT_PYTHON","CHROMEDRIVER_NODE"),"bad_engine")
    need(isinstance(runner.get("version"),str) and bool(runner.get("version")),"missing_version")
    need(isinstance(runner.get("os"),str) and bool(runner.get("os")),"missing_os")
    need(isinstance(runner.get("native_run_id"),str) and bool(runner.get("native_run_id")),"missing_native_run_id")
    need(runner.get("head_sha")==s.get("commit"),"native_head_mismatch")
    if expected_run_id is not None:need(runner.get("native_run_id")==str(expected_run_id),"expected_run_id_mismatch")
    num=runner.get("attempt_number")
    need(type(num) is int and num>=1,"bad_run_attempt")
    stages=report.get("stages")
    if not isinstance(stages,dict):stages={}
    for name in STAGES:need(stages.get(name) in STATES,"bad_stage_"+name)
    if runner.get("engine")=="PLAYWRIGHT_PYTHON" and stages.get("browser")=="PASS":
        need(isinstance(runner.get("browser_version"),str) and
             bool(runner.get("browser_version")),"missing_browser_version")
        need(bool(HEX64.fullmatch(str(runner.get("browser_binary_sha256","")))),
             "missing_browser_binary_sha256")
        need(type(runner.get("browser_binary_bytes")) is int and
             runner.get("browser_binary_bytes")>0,
             "missing_browser_binary_bytes")
    scenarios=report.get("scenarios")
    if not isinstance(scenarios,dict):scenarios={}
    for name in SCENARIOS:need(scenarios.get(name) in STATES,"bad_scenario_"+name)
    if stages.get("identity")!="PASS" and any(stages.get(x)=="PASS" for x in STAGES[1:]):
        errors.append("identity_lifecycle_contradiction")
    if stages.get("dependencies")!="PASS" and any(stages.get(x)=="PASS" for x in STAGES[2:]):
        errors.append("dependencies_lifecycle_contradiction")
    if stages.get("integration") in ("FAIL","BLOCKED") and stages.get("build")=="PASS":
        errors.append("failed_integration_followed_by_build_pass")
    if stages.get("build") in ("FAIL","BLOCKED") and stages.get("browser")=="PASS":
        errors.append("failed_build_followed_by_browser_pass")
    if stages.get("integration") in ("FAIL","BLOCKED") and stages.get("browser")=="PASS":
        errors.append("failed_integration_followed_by_browser_pass")
    if s.get("subject_kind")=="PRODUCT_PREVIEW" and stages.get("browser")=="PASS":
        need(stages.get("integration")=="PASS" and stages.get("build")=="PASS","product_prerequisite_not_pass")
    if s.get("subject_kind")=="SYNTHETIC" and stages.get("browser")=="PASS":
        need(stages.get("integration")=="SKIPPED" and stages.get("build")=="SKIPPED",
             "synthetic_stage_policy_not_explicit")
    widths=report.get("viewports")
    if not isinstance(widths,list):widths=[]
    seen={}
    for row in widths:
        if not isinstance(row,dict):
            errors.append("invalid_viewport_row");continue
        w=row.get("width")
        if type(w) is not int or w not in WIDTHS:
            errors.append("bad_viewport_width");continue
        need(row.get("status") in STATES,"bad_viewport_status")
        if w in seen:errors.append("duplicate_viewport_"+str(w))
        seen[w]=row.get("status")
    need(set(seen)==set(WIDTHS),"missing_viewports")
    network=report.get("network")
    if not isinstance(network,dict):network={}
    need(network.get("enforcement") in ("PREVENTIVE_BROWSER_ABORT","OBSERVE_ONLY"),"bad_network_mode")
    need(network.get("service_workers") in ("BLOCKED","NOT_VERIFIED"),"bad_service_workers")
    need(network.get("measurement_scope")=="BROWSER_CONTEXT_OBSERVED_REQUESTS_ONLY",
         "network_scope_not_bounded")
    need(network.get("os_egress_attested") is False,"unjustified_os_egress_attestation")
    counts={}
    for k in ("outbound_attempted","outbound_blocked","outbound_escaped"):
        v=network.get(k)
        need(type(v) is int and v>=0,"bad_network_"+k)
        counts[k]=v if type(v) is int and v>=0 else 0
    need(counts["outbound_blocked"]+counts["outbound_escaped"]==counts["outbound_attempted"],
         "inconsistent_network_counts")
    artifacts=report.get("artifacts")
    if not isinstance(artifacts,list):artifacts=[]
    names=set();shots=set();has_trace=False
    supplied=Path(artifact_root) if artifact_root is not None else None
    if supplied is not None and (supplied.is_symlink() or
            any(parent.is_symlink() for parent in supplied.parents) or not supplied.is_dir()):
        errors.append("unsafe_artifact_root")
        root=None
    else:
        root=supplied.resolve() if supplied is not None else None
    for a in artifacts:
        if not isinstance(a,dict):errors.append("artifact_not_object");continue
        name=a.get("name")
        if not isinstance(name,str) or not NAME.fullmatch(name):
            errors.append("unsafe_artifact_name");continue
        if name in names:errors.append("duplicate_artifact_name")
        names.add(name)
        need(bool(HEX64.fullmatch(str(a.get("sha256","")))),"bad_artifact_hash")
        size=a.get("bytes")
        need(type(size) is int and size>0,"bad_artifact_bytes")
        kind=a.get("kind")
        need(kind in ("SCREENSHOT","TRACE","LOG"),"bad_artifact_kind")
        if kind=="SCREENSHOT":
            w=a.get("width")
            need(type(w) is int and w in WIDTHS,"bad_screenshot_width")
            if type(w) is int and w in WIDTHS:shots.add(w)
        if kind in ("TRACE","LOG"):has_trace=True
        if root is not None:
            p=root/name
            if not p.is_file() or p.is_symlink():errors.append("missing_or_unsafe_artifact_"+name)
            elif p.stat().st_size!=size:errors.append("artifact_size_mismatch_"+name)
            elif hashlib.sha256(p.read_bytes()).hexdigest()!=a.get("sha256"):
                errors.append("artifact_hash_mismatch_"+name)
    original=report.get("original")
    if not isinstance(original,dict):original={}
    # Custody is reported by producer and NEVER independently authenticated by this validator.
    need(original.get("custody") in ("TEST_VECTOR","LOCAL_UNVERIFIED","PROVIDER_NATIVE_READBACK",
                                   "LIBRARY_VERIFIED","GIT_BYTES_VERIFIED"),"bad_original_custody")
    need(bool(HEX64.fullmatch(str(original.get("sha256","")))),"bad_original_hash")
    need(type(original.get("bytes")) is int and original.get("bytes")>0,"bad_original_bytes")
    need(isinstance(original.get("reference"),str) and bool(original.get("reference")),"bad_original_ref")
    need(isinstance(report.get("limitations"),list) and
         all(isinstance(x,str) for x in report.get("limitations",[])),"bad_limitations")
    browser=stages.get("browser")
    if browser=="PASS":
        need(all(scenarios.get(k)=="PASS" for k in SCENARIOS),"browser_pass_missing_scenarios")
        need(all(seen.get(w)=="PASS" for w in WIDTHS),"browser_pass_missing_viewports")
        need(all(w in shots for w in WIDTHS),"browser_pass_missing_screenshots")
        need(has_trace,"browser_pass_missing_trace_or_log")
        need(network.get("enforcement")=="PREVENTIVE_BROWSER_ABORT","browser_pass_without_preventive_egress")
        need(network.get("service_workers")=="BLOCKED","browser_pass_without_serviceworker_block")
        need(counts["outbound_escaped"]==0,"browser_pass_with_outbound_escape")
    elif browser in ("NOT_RUN","SKIPPED","BLOCKED"):
        need(not any(scenarios.get(k)=="PASS" for k in SCENARIOS),"unrun_browser_with_pass_scenarios")
        need(not any(seen.get(w)=="PASS" for w in WIDTHS),"unrun_browser_with_pass_viewports")
    if browser=="PASS":
        need(report.get("reported_verdict")=="PASS","browser_pass_verdict_mismatch")
    elif browser=="FAIL":
        need(report.get("reported_verdict")=="FAIL","browser_fail_verdict_mismatch")
        need(any(scenarios.get(k)=="FAIL" for k in SCENARIOS) or
             any(seen.get(w)=="FAIL" for w in WIDTHS),
             "browser_fail_without_negative_evidence")
    elif browser in ("BLOCKED","NOT_RUN","SKIPPED"):
        need(report.get("reported_verdict") in ("NOT_RUN","PARTIAL"),
             "unrun_browser_verdict_mismatch")
    if report.get("reported_verdict")=="PASS":
        need(browser=="PASS","reported_pass_but_browser_not_pass")
    if report.get("reported_verdict")=="NOT_RUN":
        need(browser in ("NOT_RUN","SKIPPED","BLOCKED"),"reported_notrun_browser_executed")
    if errors:return {"status":"INVALID_REPORT","errors":sorted(set(errors)),"artifact_bytes_verified_locally":False}
    status="VALID_TEST_VECTOR_SHAPE_ONLY" if original["custody"]=="TEST_VECTOR" else "VALID_SHAPE_UNATTESTED"
    return {"status":status,"artifact_bytes_verified_locally":root is not None,
            "provider_native_verified":False,"Product_accepted":False,
            "scenario_count":len(SCENARIOS),"widths":list(WIDTHS)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("report",type=Path)
    p.add_argument("--artifact-root",type=Path)
    p.add_argument("--expected-commit")
    p.add_argument("--expected-tree")
    p.add_argument("--expected-run-id")
    a=p.parse_args()
    try:
        data=json.loads(a.report.read_text(encoding="utf8"))
        result=evaluate(data,a.artifact_root,a.expected_commit,a.expected_tree,a.expected_run_id)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError) as err:
        result={"status":"INVALID_REPORT","errors":[type(err).__name__]}
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"].startswith("VALID_") else 1
if __name__=="__main__":sys.exit(main())
