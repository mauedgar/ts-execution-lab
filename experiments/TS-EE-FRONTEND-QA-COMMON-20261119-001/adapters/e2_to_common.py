#!/usr/bin/env python3
"""Bridge an actual E2 synthetic source receipt to FEQA v0; never attest provider identity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import sys

WIDTHS=(320,375,768,1440)
EXPECTED_BAD=["CONSOLE","HIDDEN_SKU","HTTP","LABEL","OVERFLOW"]
IMAGE=re.compile(r"^(good|bad)-(320|375|768|1440)\.(png|zip)$")
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")
MAX_EVIDENCE_BYTES=16*1024*1024

def read_verified_file(rootfd, filename, declared_bytes):
    """Open a single regular evidence inode using its trusted directory FD.
    No symlink follow; descriptor protects against path replacement after open.
    Entire workspace ancestry must still be trusted and isolated by runner.
    """
    if type(declared_bytes) is not int or not 0<declared_bytes<=MAX_EVIDENCE_BYTES:
        raise ValueError("BLOCKED_E2_ARTIFACT_LENGTH")
    flags=os.O_RDONLY | getattr(os,"O_CLOEXEC",0)
    if not hasattr(os,"O_NOFOLLOW"):
        raise ValueError("BLOCKED_MISSING_NOFOLLOW_SUPPORT")
    flags |= os.O_NOFOLLOW
    try:
        fd=os.open(filename,flags,dir_fd=rootfd)
    except OSError as err:
        raise ValueError("BLOCKED_UNSAFE_EVIDENCE_OPEN") from err
    try:
        record=os.fstat(fd)
        if not stat.S_ISREG(record.st_mode) or record.st_size!=declared_bytes:
            raise ValueError("BLOCKED_E2_ARTIFACT_NOT_REGULAR_OR_LENGTH")
        with os.fdopen(fd,"rb",closefd=False) as handle:
            data=handle.read(MAX_EVIDENCE_BYTES+1)
        if len(data)!=declared_bytes:
            raise ValueError("BLOCKED_E2_ARTIFACT_MUTATED_DURING_READ")
        return data
    finally:
        os.close(fd)

def digest(b):return hashlib.sha256(b).hexdigest()

def convert(raw, *, repository, commit, tree, run_id, attempt, script_hash,
            original_sha, original_bytes, evidence_root):
    if not isinstance(raw,dict):
        raise ValueError("BLOCKED_MALFORMED_E2_ROOT")
    if raw.get("schema")!="ts-ee-e2-browser-qa/v1" or raw.get("pass") is not True:
        raise ValueError("BLOCKED_UNQUALIFIED_E2_REPORT")
    if raw.get("source_sha256")!=script_hash:
        raise ValueError("BLOCKED_E2_SCRIPT_HASH")
    if raw.get("service_workers")!="BLOCKED":
        raise ValueError("BLOCKED_SERVICE_WORKER_POLICY")
    if not isinstance(raw.get("widths"),list):
        raise ValueError("BLOCKED_MALFORMED_E2_RUNTIME_OR_WIDTHS")
    if len(raw["widths"])!=len(WIDTHS) or any(type(w) is not int for w in raw["widths"]):
        raise ValueError("BLOCKED_MALFORMED_E2_VIEWPORT_TYPE")
    if sorted(raw["widths"])!=list(WIDTHS):
        raise ValueError("BLOCKED_VIEWPORT_INVENTORY")
    runtime=raw.get("runtime")
    if not isinstance(runtime,dict):
        raise ValueError("BLOCKED_MALFORMED_E2_RUNTIME_OR_WIDTHS")
    if (not isinstance(runtime.get("chromium"),str) or not runtime.get("chromium") or
            not HEX64.fullmatch(str(runtime.get("chromium_executable_sha256",""))) or
            type(runtime.get("chromium_executable_bytes")) is not int or
            runtime["chromium_executable_bytes"]<=0):
        raise ValueError("BLOCKED_CHROMIUM_BINARY_IDENTITY")
    variants=raw.get("variants",{})
    if not isinstance(variants,dict):
        raise ValueError("BLOCKED_MALFORMED_E2_VARIANTS")
    good=variants.get("good",{})
    bad=variants.get("bad",{})
    for tag,case,expected in (("good",good,[]),("bad",bad,EXPECTED_BAD)):
        if not isinstance(case,dict) or not isinstance(case.get("rows"),list) or any(
                not isinstance(row,dict) for row in case["rows"]):
            raise ValueError("BLOCKED_MALFORMED_E2_ROWS_"+tag)
        if case.get("pass") is not True or case.get("detected")!=expected:
            raise ValueError("BLOCKED_E2_CONTROL_"+tag)
        rows=case["rows"]
        if len(rows)!=len(WIDTHS):
            raise ValueError("BLOCKED_E2_ROWS_"+tag)
        if any(type(row.get("width")) is not int for row in rows):
            raise ValueError("BLOCKED_MALFORMED_ROW_WIDTH_"+tag)
        if sorted(row["width"] for row in rows)!=list(WIDTHS):
            raise ValueError("BLOCKED_E2_ROWS_"+tag)
        for row in rows:
            for field in ("blocked_external","overflow_px","console_errors","http_errors"):
                value=row.get(field)
                if type(value) is not int or value<0:
                    raise ValueError("BLOCKED_MALFORMED_E2_COUNTER_"+tag+"_"+field)
            for field in ("label","detail","back","forward","deep_refresh",
                          "keyboard_activated","keyboard_negative_rejected",
                          "external_navigation_rejected","hidden_rejected"):
                if type(row.get(field)) is not bool:
                    raise ValueError("BLOCKED_MALFORMED_E2_FLAG_"+tag+"_"+field)
    positive=good["rows"]
    injected=bad["rows"]
    def all_rows(pred):
        return all(pred(r) for r in positive)
    def all_both(pred):
        return all(pred(r) for r in positive+injected)
    scenario_checks={
        "viewport":all_rows(lambda r:r.get("overflow_px")==0) and
          any(r.get("overflow_px",0)>0 for r in injected),
        "routing":all_both(lambda r:r.get("detail") is True),
        "history":all_both(lambda r:r.get("back") is True and r.get("forward") is True),
        "deep_link_refresh":all_both(lambda r:r.get("deep_refresh") is True),
        "sku_negative":all_rows(lambda r:r.get("hidden_rejected") is True) and
          all(r.get("hidden_rejected") is False for r in injected),
        "keyboard_focus":all_both(lambda r:r.get("first_tab")=="Catalog" and
                              r.get("keyboard_activated") is True and
                              r.get("keyboard_negative_rejected") is True),
        "a11y_basic":all_rows(lambda r:r.get("label") is True) and
          all(r.get("label") is False for r in injected),
        "console_http":all_rows(lambda r:r.get("console_errors")==0 and r.get("http_errors")==0) and
          all(r.get("console_errors",0)>0 and r.get("http_errors",0)>0 for r in injected)
    }
    if not all(scenario_checks.values()):
        raise ValueError("BLOCKED_E2_SCENARIOS_"+",".join(k for k,v in scenario_checks.items() if not v))
    if not all_both(lambda r:r.get("external_navigation_rejected") is True):
        raise ValueError("BLOCKED_OBSERVED_EGRESS_ROUTE_RESULT")
    for tag,case in (("good",good),("bad",bad)):
        per_row=sum(r.get("blocked_external",0) for r in case["rows"])
        if type(case.get("blocked_external_requests")) is not int or case["blocked_external_requests"]!=per_row:
            raise ValueError("BLOCKED_EGRESS_TOTAL_MISMATCH_"+tag)
    attempted=sum(r["blocked_external"] for r in positive+injected)
    if any(type(r.get("blocked_external")) is not int or r["blocked_external"]<1
           for r in positive+injected):
        raise ValueError("BLOCKED_OUTBOUND_ABORT_PROOF")
    evidence_root=Path(evidence_root)
    if not evidence_root.is_dir() or evidence_root.is_symlink() or any(
            parent.is_symlink() for parent in evidence_root.parents):
        raise ValueError("BLOCKED_UNSAFE_EVIDENCE_ROOT")
    artifacts=[]
    entries=raw.get("artifacts")
    if not isinstance(entries,list):
        raise ValueError("BLOCKED_MALFORMED_E2_ARTIFACTS")
    if not hasattr(os,"O_DIRECTORY") or not hasattr(os,"O_NOFOLLOW"):
        raise ValueError("BLOCKED_UNQUALIFIED_EVIDENCE_HOST")
    try:
        rootfd=os.open(str(evidence_root),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    except OSError as err:
        raise ValueError("BLOCKED_EVIDENCE_ROOT_OPEN") from err
    try:
        for entry in entries:
            if not isinstance(entry,dict):
                raise ValueError("BLOCKED_MALFORMED_E2_ARTIFACT")
            filename=entry.get("file","")
            if not isinstance(filename,str):
                raise ValueError("BLOCKED_E2_ARTIFACT_NAME")
            match=IMAGE.fullmatch(filename)
            if not match:raise ValueError("BLOCKED_E2_ARTIFACT_NAME")
            actual=read_verified_file(rootfd,filename,entry.get("bytes"))
            if digest(actual)!=entry.get("sha256"):
                raise ValueError("BLOCKED_CORRUPTED_E2_ARTIFACT")
            kind="SCREENSHOT" if match[3]=="png" else "TRACE"
            item={"name":filename,"kind":kind,"sha256":digest(actual),"bytes":len(actual)}
            if kind=="SCREENSHOT":item["width"]=int(match[2])
            artifacts.append(item)
    finally:
        os.close(rootfd)
    if len(artifacts)!=16 or len({x["name"] for x in artifacts})!=16:
        raise ValueError("BLOCKED_ARTIFACT_COMPLETENESS")
    if not HEX40.fullmatch(commit) or not HEX40.fullmatch(tree):
        raise ValueError("BLOCKED_FROZEN_GIT_IDENTITY")
    if not repository or not run_id or not attempt or not HEX64.fullmatch(original_sha) or \
            type(original_bytes) is not int or original_bytes<=0:
        raise ValueError("BLOCKED_NATIVE_INPUT")
    return {
        "schema":"ts-ee/frontend-browser-qa/v0","product_effect":"NONE",
        "reported_verdict":"PASS","attempt":attempt,
        "source":{"repository":repository,"commit":commit,"tree":tree,"subject_kind":"SYNTHETIC"},
        "runner":{"engine":"PLAYWRIGHT_PYTHON",
                  "version":runtime.get("playwright",""),
                  "browser_version":runtime["chromium"],
                  "browser_binary_sha256":runtime["chromium_executable_sha256"],
                  "browser_binary_bytes":runtime["chromium_executable_bytes"],
                  "os":platform.platform(),"native_run_id":run_id,
                  "head_sha":commit,"attempt_number":int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))},
        "stages":{"identity":"PASS","dependencies":"PASS","integration":"SKIPPED",
                  "build":"SKIPPED","browser":"PASS"},
        "scenarios":{name:"PASS" for name in scenario_checks},
        "viewports":[{"width":w,"status":"PASS"} for w in WIDTHS],
        "network":{"enforcement":"PREVENTIVE_BROWSER_ABORT","service_workers":"BLOCKED",
                   "outbound_attempted":attempted,"outbound_blocked":attempted,
                   "outbound_escaped":0,
                   "measurement_scope":"BROWSER_CONTEXT_OBSERVED_REQUESTS_ONLY",
                   "os_egress_attested":False},
        "artifacts":artifacts,
        "original":{"custody":"LOCAL_UNVERIFIED","sha256":original_sha,
                    "bytes":original_bytes,
                    "reference":"RESULT.json on original isolated job; provider/native readback required"},
        "limitations":[
            "BROWSER_CONTEXT_ROUTE_ABORT_ONLY_NOT_OS_EGRESS_PROOF",
            "NONPRODUCT_SYNTHETIC_NOT_AWARE_SOURCE_E2E",
            "ARTIFACT_BYTES_LOCAL_VERIFIED_PROVIDER_ZIP_READBACK_SEPARATE",
            "KEYBOARD_ROUTE_AND_EGRESS_FAULT_INJECTION_REQUIRES_DISTINCT_NATIVE_TEST",
            "CHROMIUM_BINARY_SHA256_LOCAL_JOB_ONLY_PROVIDER_READBACK_SEPARATE",
            "NATIVE_RUN_ID_AND_GIT_ID_FROM_CI_CONTEXT_REQUIRES_INDEPENDENT_CHECK"
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--e2",type=Path,required=True)
    p.add_argument("--source-script",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--repository",required=True)
    p.add_argument("--commit",required=True)
    p.add_argument("--tree",required=True)
    p.add_argument("--run-id",required=True)
    p.add_argument("--attempt",required=True)
    a=p.parse_args()
    if a.output.exists():raise SystemExit("BLOCKED_EXISTING_RECEIPT_OUTPUT")
    data=a.e2.read_bytes()
    try:
        result=convert(json.loads(data),repository=a.repository,commit=a.commit,tree=a.tree,
                   run_id=a.run_id,attempt=a.attempt,script_hash=digest(a.source_script.read_bytes()),
                   original_sha=digest(data),original_bytes=len(data),
                   evidence_root=a.e2.parent)
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError) as exc:
        raise SystemExit("BLOCKED_MALFORMED_OR_UNQUALIFIED_E2_RECEIPT:"+type(exc).__name__)
    with a.output.open("x",encoding="utf8") as f:
        f.write(json.dumps(result,sort_keys=True,indent=2)+"\n")
        f.flush();os.fsync(f.fileno())
    print("TS_EE_FEQA_COMMON_PRODUCED="+json.dumps({
        "source_receipt_sha256":digest(data),"scenarios":len(result["scenarios"]),
        "artifacts":len(result["artifacts"]),"report_path":str(a.output),
        "provider_attested":False},sort_keys=True))
if __name__=="__main__":main()
