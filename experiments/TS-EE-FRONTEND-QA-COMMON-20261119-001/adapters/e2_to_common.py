#!/usr/bin/env python3
"""Bridge an actual E2 synthetic source receipt to FEQA v0; never attest provider identity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys

WIDTHS=(320,375,768,1440)
EXPECTED_BAD=["CONSOLE","HIDDEN_SKU","HTTP","LABEL","OVERFLOW"]
IMAGE=re.compile(r"^(good|bad)-(320|375|768|1440)\.(png|zip)$")
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")

def digest(b):return hashlib.sha256(b).hexdigest()

def convert(raw, *, repository, commit, tree, run_id, attempt, script_hash,
            original_sha, original_bytes, evidence_root):
    if raw.get("schema")!="ts-ee-e2-browser-qa/v1" or raw.get("pass") is not True:
        raise ValueError("BLOCKED_UNQUALIFIED_E2_REPORT")
    if raw.get("source_sha256")!=script_hash:
        raise ValueError("BLOCKED_E2_SCRIPT_HASH")
    if raw.get("service_workers")!="BLOCKED":
        raise ValueError("BLOCKED_SERVICE_WORKER_POLICY")
    if sorted(raw.get("widths",[]))!=list(WIDTHS):
        raise ValueError("BLOCKED_VIEWPORT_INVENTORY")
    variants=raw.get("variants",{})
    good=variants.get("good",{})
    bad=variants.get("bad",{})
    for tag,case,expected in (("good",good,[]),("bad",bad,EXPECTED_BAD)):
        if case.get("pass") is not True or case.get("detected")!=expected:
            raise ValueError("BLOCKED_E2_CONTROL_"+tag)
        if sorted(x.get("width") for x in case.get("rows",[]))!=list(WIDTHS):
            raise ValueError("BLOCKED_E2_ROWS_"+tag)
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
        "keyboard_focus":all_both(lambda r:r.get("first_tab")=="Catalog"),
        "a11y_basic":all_rows(lambda r:r.get("label") is True) and
          all(r.get("label") is False for r in injected),
        "console_http":all_rows(lambda r:r.get("console_errors")==0 and r.get("http_errors")==0) and
          all(r.get("console_errors",0)>0 and r.get("http_errors",0)>0 for r in injected)
    }
    if not all(scenario_checks.values()):
        raise ValueError("BLOCKED_E2_SCENARIOS_"+",".join(k for k,v in scenario_checks.items() if not v))
    attempted=sum(r["blocked_external"] for r in positive+injected)
    if any(type(r.get("blocked_external")) is not int or r["blocked_external"]<1
           for r in positive+injected):
        raise ValueError("BLOCKED_OUTBOUND_ABORT_PROOF")
    evidence_root=Path(evidence_root)
    artifacts=[]
    for entry in raw.get("artifacts",[]):
        filename=entry.get("file","")
        match=IMAGE.fullmatch(filename)
        if not match:raise ValueError("BLOCKED_E2_ARTIFACT_NAME")
        p=evidence_root/filename
        if p.is_symlink() or not p.is_file():raise ValueError("BLOCKED_MISSING_E2_ARTIFACT")
        actual=p.read_bytes()
        if len(actual)!=entry.get("bytes") or digest(actual)!=entry.get("sha256"):
            raise ValueError("BLOCKED_CORRUPTED_E2_ARTIFACT")
        kind="SCREENSHOT" if match[3]=="png" else "TRACE"
        item={"name":filename,"kind":kind,"sha256":digest(actual),"bytes":len(actual)}
        if kind=="SCREENSHOT":item["width"]=int(match[2])
        artifacts.append(item)
    if len(artifacts)!=16 or len({x["name"] for x in artifacts})!=16:
        raise ValueError("BLOCKED_ARTIFACT_COMPLETENESS")
    if not HEX40.fullmatch(commit) or not HEX40.fullmatch(tree):
        raise ValueError("BLOCKED_FROZEN_GIT_IDENTITY")
    if not repository or not run_id or not attempt or not HEX64.fullmatch(original_sha):
        raise ValueError("BLOCKED_NATIVE_INPUT")
    return {
        "schema":"ts-ee/frontend-browser-qa/v0","product_effect":"NONE",
        "reported_verdict":"PASS","attempt":attempt,
        "source":{"repository":repository,"commit":commit,"tree":tree,"subject_kind":"SYNTHETIC"},
        "runner":{"engine":"PLAYWRIGHT_PYTHON",
                  "version":raw.get("runtime",{}).get("playwright",""),
                  "os":platform.platform(),"native_run_id":run_id,
                  "head_sha":commit,"attempt_number":int(os.environ.get("GITHUB_RUN_ATTEMPT","1"))},
        "stages":{"identity":"PASS","dependencies":"PASS","integration":"SKIPPED",
                  "build":"SKIPPED","browser":"PASS"},
        "scenarios":{name:"PASS" for name in scenario_checks},
        "viewports":[{"width":w,"status":"PASS"} for w in WIDTHS],
        "network":{"enforcement":"PREVENTIVE_BROWSER_ABORT","service_workers":"BLOCKED",
                   "outbound_attempted":attempted,"outbound_blocked":attempted,
                   "outbound_escaped":0},
        "artifacts":artifacts,
        "original":{"custody":"LOCAL_UNVERIFIED","sha256":original_sha,
                    "bytes":original_bytes,
                    "reference":"RESULT.json on original isolated job; provider/native readback required"},
        "limitations":[
            "BROWSER_CONTEXT_ROUTE_ABORT_ONLY_NOT_OS_EGRESS_PROOF",
            "NONPRODUCT_SYNTHETIC_NOT_AWARE_SOURCE_E2E",
            "ARTIFACT_BYTES_LOCAL_VERIFIED_PROVIDER_ZIP_READBACK_SEPARATE",
            "KEYBOARD_ROUTING_REFRESH_POSITIVE_ONLY_NEGATIVE_SENSITIVITY_UNMEASURED",
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
    result=convert(json.loads(data),repository=a.repository,commit=a.commit,tree=a.tree,
                   run_id=a.run_id,attempt=a.attempt,script_hash=digest(a.source_script.read_bytes()),
                   original_sha=digest(data),original_bytes=len(data),
                   evidence_root=a.e2.parent)
    with a.output.open("x",encoding="utf8") as f:
        f.write(json.dumps(result,sort_keys=True,indent=2)+"\n")
        f.flush();os.fsync(f.fileno())
    print("TS_EE_FEQA_COMMON_PRODUCED="+json.dumps({
        "source_receipt_sha256":digest(data),"scenarios":len(result["scenarios"]),
        "artifacts":len(result["artifacts"]),"report_path":str(a.output),
        "provider_attested":False},sort_keys=True))
if __name__=="__main__":main()
