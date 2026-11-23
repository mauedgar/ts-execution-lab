#!/usr/bin/env python3
"""Frontend QA v0.1 separate experimental checker: functional vs network assurance.\nStable v0 remains unchanged. Provider and Product acceptance are always external.\n"""
import argparse
import hashlib
import json
import os
import stat
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
Q5B_SCENARIO_CHECKS={
    "viewport":("width","overflow","screenshot"),
    "routing":("deep_link",),
    "history":("history_back",),
    "deep_link_refresh":("deep_link_refresh",),
    "sku_negative":("sku_negative",),
    "keyboard_focus":("keyboard_tab","keyboard_enter"),
    "a11y_basic":("semantic_heading","button_label","keyboard_tab","keyboard_enter"),
    "console_http":("http_404","http_500","seeded_js_error")
}
MAX_ARTIFACT_BYTES=8*1024*1024

def secure_directory_fd(path):
    """Open every path component as a directory with no followed symlinks."""
    absolute=Path(os.path.abspath(os.fspath(path)))
    fd=os.open(os.path.sep,os.O_RDONLY|os.O_DIRECTORY)
    try:
        for component in absolute.parts[1:]:
            if component in ("", ".", ".."):
                raise ValueError("UNSAFE_DIRECTORY_COMPONENT")
            child=os.open(component,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd)
            fd=child
        return fd
    except BaseException:
        os.close(fd)
        raise

def secure_read_artifact(directory_fd,name):
    """One descriptor for type, size and content; no stat/read_bytes race."""
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory_fd)
    try:
        meta=os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or not 0<=meta.st_size<=MAX_ARTIFACT_BYTES:
            raise ValueError("UNSAFE_ARTIFACT_FILE")
        with os.fdopen(fd,"rb",closefd=False) as stream:
            raw=stream.read(MAX_ARTIFACT_BYTES+1)
        if len(raw)>MAX_ARTIFACT_BYTES:
            raise ValueError("OVERSIZE_ARTIFACT")
        return raw
    finally:
        os.close(fd)

def evaluate(report,artifact_root=None,expected_commit=None,expected_tree=None,expected_run_id=None):
    errors=[]
    def need(ok,code):
        if not ok: errors.append(code)
    if not isinstance(report,dict):
        return {"status":"INVALID_REPORT","errors":["report_not_object"]}
    need(report.get("schema")=="ts-ee/frontend-browser-qa/v0.1","wrong_schema")
    need(report.get("product_effect")=="NONE","product_effect_not_none")
    need(bool(ATTEMPT.fullmatch(str(report.get("attempt","")))),"bad_attempt")
    need(report.get("reported_verdict") in ("PASS","FAIL","PARTIAL","NOT_RUN"),"bad_verdict")
    need(report.get("functional_browser_status") in ("PASS","FAIL","NOT_RUN"),"bad_functional_status")
    need(report.get("network_assurance_status") in ("PREVENTIVE_BROWSER_ABORT","OBSERVE_ONLY_UNATTESTED","NOT_RUN"),"bad_network_assurance")
    need(report.get("terminal_result") in ("PASS_WITH_BROWSER_ABORT","PASS_FUNCTIONAL_ONLY","FAIL","NOT_RUN"),"bad_terminal_result")
    need(report.get("provider_native_verified") is False,"false_provider_attestation_required")
    need(report.get("Product_accepted") is False,"false_product_acceptance_required")
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
    if runner.get("engine")=="CHROMEDRIVER_NODE" and stages.get("browser")=="PASS":
        need(isinstance(runner.get("browser_version"),str) and bool(runner.get("browser_version")),"chromedriver_missing_browser_version")
        need(bool(HEX64.fullmatch(str(runner.get("browser_binary_sha256","")))),"chromedriver_missing_browser_binary_sha256")
        need(type(runner.get("browser_binary_bytes")) is int and runner.get("browser_binary_bytes")>0,"chromedriver_missing_browser_binary_bytes")
        need(isinstance(runner.get("driver_version"),str) and bool(runner.get("driver_version")),"chromedriver_missing_driver_version")
        need(bool(HEX64.fullmatch(str(runner.get("driver_binary_sha256","")))),"chromedriver_missing_driver_binary_sha256")
        need(type(runner.get("driver_binary_bytes")) is int and runner.get("driver_binary_bytes")>0,"chromedriver_missing_driver_binary_bytes")
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
    scope=network.get("measurement_scope")
    need(scope in ("BROWSER_CONTEXT_OBSERVED_REQUESTS_ONLY","LOCAL_FIXTURE_SERVER_ONLY"),
         "network_scope_not_bounded")
    fixture_only=scope=="LOCAL_FIXTURE_SERVER_ONLY"
    if fixture_only:
        need(network.get("enforcement")=="OBSERVE_ONLY","fixture_scope_cannot_claim_prevention")
        need(network.get("service_workers")=="NOT_VERIFIED","fixture_scope_cannot_claim_sw_block")
    need(network.get("os_egress_attested") is False,"unjustified_os_egress_attestation")
    counts={}
    for k in ("outbound_attempted","outbound_blocked","outbound_escaped"):
        v=network.get(k)
        if fixture_only:
            need(v is None,"unmeasured_network_count_must_be_null_"+k)
            counts[k]=0  # internal validation only, NOT measured traffic
        else:
            need(type(v) is int and v>=0,"bad_network_"+k)
            counts[k]=v if type(v) is int and v>=0 else 0
    if not fixture_only:
        need(counts["outbound_blocked"]+counts["outbound_escaped"]==counts["outbound_attempted"],
             "inconsistent_network_counts")
    artifacts=report.get("artifacts")
    if not isinstance(artifacts,list):artifacts=[]
    names=set();shots=set();has_trace=False
    root_fd=None
    if artifact_root is not None:
        try:
            root_fd=secure_directory_fd(artifact_root)
        except (OSError,ValueError,TypeError):
            errors.append("unsafe_artifact_root")
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
        if root_fd is not None:
            try:
                raw=secure_read_artifact(root_fd,name)
            except (OSError,ValueError):
                errors.append("missing_or_unsafe_artifact_"+name)
            else:
                if len(raw)!=size:errors.append("artifact_size_mismatch_"+name)
                elif hashlib.sha256(raw).hexdigest()!=a.get("sha256"):
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
    if (runner.get("engine")=="CHROMEDRIVER_NODE" and s.get("subject_kind")=="SYNTHETIC"
            and stages.get("browser")=="PASS" and
            original.get("reference")=="LOCAL_NONPRODUCT_Q5B_ACTUAL_JSON_AND_TOOLCHAIN_BYTES"):
        evidence=report.get("scenario_evidence")
        need(isinstance(evidence,dict) and set(evidence)==set(Q5B_SCENARIO_CHECKS),
             "q5b_scenario_evidence_incomplete")
        need("SYNTHETIC_LOCAL_FIXTURE_ONLY" in report.get("limitations",[]),
             "q5b_fixture_scope_limit_missing")
        if isinstance(evidence,dict):
            for scenario,required in Q5B_SCENARIO_CHECKS.items():
                item=evidence.get(scenario)
                if not isinstance(item,dict):
                    errors.append("q5b_evidence_missing_"+scenario)
                    continue
                need(item.get("scope")=="SYNTHETIC_LOCAL_FIXTURE_ONLY",
                     "q5b_evidence_scope_"+scenario)
                need(item.get("checks")==list(required),
                     "q5b_evidence_check_mapping_"+scenario)
                rows=item.get("viewports")
                if not isinstance(rows,list) or len(rows)!=len(WIDTHS) or any(
                    not isinstance(row,dict) for row in rows):
                    errors.append("q5b_evidence_viewports_"+scenario)
                    continue
                need([row.get("width") for row in rows]==list(WIDTHS),
                     "q5b_evidence_width_order_"+scenario)
                for row in rows:
                    observed=row.get("observed")
                    need(isinstance(observed,dict) and
                         set(observed)==set(required) and
                         all(observed.get(k)=="PASS" for k in required),
                         "q5b_evidence_missing_pass_"+scenario)
    browser=stages.get("browser")
    if browser=="PASS":
        need(all(scenarios.get(k)=="PASS" for k in SCENARIOS),"browser_pass_missing_scenarios")
        need(all(seen.get(w)=="PASS" for w in WIDTHS),"browser_pass_missing_viewports")
        need(all(w in shots for w in WIDTHS),"browser_pass_missing_screenshots")
        need(has_trace,"browser_pass_missing_trace_or_log")
        need(report.get("functional_browser_status")=="PASS","browser_pass_functional_mismatch")
        if network.get("enforcement")=="PREVENTIVE_BROWSER_ABORT":
            need(report.get("network_assurance_status")=="PREVENTIVE_BROWSER_ABORT","preventive_assurance_mismatch")
            need(report.get("terminal_result")=="PASS_WITH_BROWSER_ABORT","preventive_terminal_mismatch")
            need(network.get("service_workers")=="BLOCKED","browser_pass_without_serviceworker_block")
            need(counts["outbound_escaped"]==0,"browser_pass_with_outbound_escape")
        elif network.get("enforcement")=="OBSERVE_ONLY":
            need(report.get("network_assurance_status")=="OBSERVE_ONLY_UNATTESTED","observe_only_assurance_mismatch")
            need(report.get("terminal_result")=="PASS_FUNCTIONAL_ONLY","observe_only_terminal_mismatch")
            need(network.get("service_workers")=="NOT_VERIFIED","observe_only_serviceworkers_overclaim")
            need(counts["outbound_blocked"]==0,"observe_only_cannot_claim_blocked")
        else:
            errors.append("browser_pass_unknown_network_enforcement")
    elif browser in ("NOT_RUN","SKIPPED","BLOCKED"):
        need(not any(scenarios.get(k)=="PASS" for k in SCENARIOS),"unrun_browser_with_pass_scenarios")
        need(not any(seen.get(w)=="PASS" for w in WIDTHS),"unrun_browser_with_pass_viewports")
    if browser=="PASS":
        wanted="PASS" if network.get("enforcement")=="PREVENTIVE_BROWSER_ABORT" else "PARTIAL"
        need(report.get("reported_verdict")==wanted,"browser_pass_verdict_mismatch")
    elif browser=="FAIL":
        need(report.get("functional_browser_status")=="FAIL","browser_fail_functional_mismatch")
        need(report.get("terminal_result")=="FAIL","browser_fail_terminal_mismatch")
        need(report.get("reported_verdict")=="FAIL","browser_fail_verdict_mismatch")
        need(any(scenarios.get(k)=="FAIL" for k in SCENARIOS) or
             any(seen.get(w)=="FAIL" for w in WIDTHS),
             "browser_fail_without_negative_evidence")
    elif browser in ("BLOCKED","NOT_RUN","SKIPPED"):
        need(report.get("functional_browser_status")=="NOT_RUN","unrun_functional_mismatch")
        need(report.get("terminal_result")=="NOT_RUN","unrun_terminal_mismatch")
        need(report.get("network_assurance_status")=="NOT_RUN","unrun_assurance_mismatch")
        need(report.get("reported_verdict") in ("NOT_RUN","PARTIAL"),
             "unrun_browser_verdict_mismatch")
    if report.get("reported_verdict")=="PASS":
        need(browser=="PASS","reported_pass_but_browser_not_pass")
    if report.get("reported_verdict")=="NOT_RUN":
        need(browser in ("NOT_RUN","SKIPPED","BLOCKED"),"reported_notrun_browser_executed")
    if root_fd is not None:
        os.close(root_fd)
    if errors:return {"status":"INVALID_REPORT","errors":sorted(set(errors)),"artifact_bytes_verified_locally":False}
    status="VALID_TEST_VECTOR_SHAPE_ONLY" if original["custody"]=="TEST_VECTOR" else "VALID_SHAPE_UNATTESTED"
    return {"status":status,"artifact_bytes_verified_locally":root_fd is not None,
            "provider_native_verified":False,"Product_accepted":False,
            "scenario_count":len(SCENARIOS),"widths":list(WIDTHS),
            "functional_browser_status":report["functional_browser_status"],
            "network_assurance_status":report["network_assurance_status"],
            "terminal_result":report["terminal_result"],
            "network_policy_qualified": report["network_assurance_status"]=="PREVENTIVE_BROWSER_ABORT",
            "network_metrics_measured":not fixture_only,
            "acceptance_authority":"EXTERNAL_PRODUCT_CONTROL_ONLY"}

def enforce_consumer_requirements(result, require_local_bytes=False):
    """A valid shape is never a Product/native-provider attestation.

    Strict consumer mode forbids TEST_VECTOR even with all matching local bytes.
    A diagnostic run is separate, explicitly selected by --diagnostic-only.
    """
    if not require_local_bytes:
        return result
    status=result.get("status","")
    if status=="VALID_TEST_VECTOR_SHAPE_ONLY":
        return {"status":"INVALID_REPORT",
                "errors":["synthetic_test_vector_forbidden_for_consumer"],
                "provider_native_verified":False,"Product_accepted":False,
                "artifact_bytes_verified_locally":result.get("artifact_bytes_verified_locally") is True}
    if status=="VALID_SHAPE_UNATTESTED" and result.get("artifact_bytes_verified_locally") is not True:
        return {"status":"INVALID_REPORT",
                "errors":["required_local_binary_readback_missing"],
                "provider_native_verified":False,"Product_accepted":False,
                "artifact_bytes_verified_locally":False}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("report",type=Path)
    p.add_argument("--artifact-root",type=Path)
    p.add_argument("--expected-commit")
    p.add_argument("--expected-tree")
    p.add_argument("--expected-run-id")
    p.add_argument("--require-local-bytes",action="store_true",
                   help="deprecated explicit consumer guard; default is already strict")
    p.add_argument("--diagnostic-only",action="store_true",
                   help="allow schema-only TEST_VECTOR shape diagnostics; never use for consumer gates")
    a=p.parse_args()
    if a.diagnostic_only and a.require_local_bytes:
        result={"status":"INVALID_REPORT","errors":["diagnostic_strict_modes_conflict"],
                "Product_accepted":False,"provider_native_verified":False}
    else:
        try:
            data=json.loads(a.report.read_text(encoding="utf8"))
            result=evaluate(data,a.artifact_root,a.expected_commit,a.expected_tree,a.expected_run_id)
            if not a.diagnostic_only:
                result=enforce_consumer_requirements(result,require_local_bytes=True)
        except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError) as err:
            result={"status":"INVALID_REPORT","errors":[type(err).__name__],
                    "Product_accepted":False,"provider_native_verified":False}
    print(json.dumps(result,sort_keys=True))
    status=result.get("status","")
    if a.diagnostic_only:
        return 0 if status.startswith("VALID_") else 1
    return 0 if status=="VALID_SHAPE_UNATTESTED" and result.get("artifact_bytes_verified_locally") is True else 1
if __name__=="__main__":sys.exit(main())
