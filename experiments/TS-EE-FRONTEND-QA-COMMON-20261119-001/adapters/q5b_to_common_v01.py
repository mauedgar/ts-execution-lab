#!/usr/bin/env python3
"""NONPRODUCT ChromeDriver Q5B local producer. Output is not a provider or Product attestation."""
import argparse
import hashlib
import json
from pathlib import Path
import re

WIDTHS=(320,375,768,1440)
CHECKS=("width","overflow","semantic_heading","button_label","keyboard_tab","keyboard_enter",
        "deep_link","deep_link_refresh","history_back","sku_negative","http_404",
        "http_500","seeded_js_error","screenshot")
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")
ATTEMPT=re.compile(r"^[A-Z0-9][A-Z0-9_-]{8,127}$")
MARKERS=("FAKE_SECRET_SESSION_ID","FAKE_SECRET_TOKEN","FAKE_BASE64_PNG")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok,code):
    if not ok:
        raise ValueError(code)

def read_file(path):
    require(path.is_file() and not path.is_symlink(),"MISSING_OR_UNSAFE_SOURCE_FILE")
    return path.read_bytes()

def safe_json(raw):
    return json.loads(raw.decode("utf-8"))

def validated_png(raw):
    require(100<len(raw)<2*1024*1024 and raw.startswith(bytes.fromhex("89504e470d0a1a0a")),
            "INVALID_SCREENSHOT_PNG")

def local_source(root,w):
    base=root/str(w)
    raw=read_file(base/"Q5B_REPORT.json")
    require(not any(m.encode() in raw for m in MARKERS),"SENSITIVE_MARKER_IN_SOURCE_JSON")
    r=safe_json(raw)
    require(r.get("schema")=="ts-ee/chromedriver-browser-q5b/v0","WRONG_Q5B_SCHEMA")
    require(r.get("subject")=="NONPRODUCT_SYNTHETIC","WRONG_SUBJECT")
    require(r.get("overall")=="PASS_BOUNDED_Q5B_BROWSER" and r.get("error_class")=="NONE","Q5B_SOURCE_NOT_PASS")
    require(r.get("requested_viewport_width")==w and r.get("observed_viewport_width")==w,"Q5B_WIDTH_MISMATCH")
    require(r.get("network_mode")=="OBSERVE_ONLY" and r.get("os_egress_attested") is False,"NETWORK_OVERCLAIM")
    require(r.get("provider_native_verified") is False and r.get("product_accepted") is False,"PROVIDER_OR_PRODUCT_OVERCLAIM")
    require(r.get("remote_session_state")=="DELETED_CONFIRMED" and r.get("session_delete")=="ACK","SESSION_NOT_CLOSED")
    require(r.get("driver_termination")=="DIRECT_PROCESS_EXIT_OBSERVED" and
            r.get("descendant_termination")=="NOT_ATTESTED","PROCESS_CUSTODY_OVERCLAIM")
    require(r.get("server_close")=="CLOSED" and r.get("profile_cleanup")=="PASS","RESOURCE_CLEANUP_FAILED")
    require(all(r.get("stage",{}).get(k)=="PASS" for k in
            ("identity","server","driver","session","browser","cleanup")),"Q5B_STAGE_NOT_PASS")
    checks=r.get("checks",{})
    require(set(checks)==set(CHECKS),"Q5B_CHECK_SET_INCOMPLETE")
    require(all(checks[k]=="PASS" for k in CHECKS),"Q5B_CHECK_NOT_PASS")
    ev=r.get("local_http_events",{})
    require(type(ev.get("product")) is int and ev.get("product")>=1 and
            all(ev.get(k)==1 for k in ("deniedSku","notFound","serverError","scriptError")),
            "FIXTURE_FAULT_EVENT_NOT_OBSERVED")
    a=r.get("screenshot",{})
    name="q5b-"+str(w)+".png"
    require(a.get("filename")==name and a.get("width")==w,"SCREENSHOT_IDENTITY_MISMATCH")
    png=read_file(base/name)
    validated_png(png)
    require(a.get("bytes")==len(png) and a.get("sha256")==digest(png),"SCREENSHOT_BYTES_HASH_MISMATCH")
    require(type(r.get("session_create_ms")) is int and r.get("session_create_ms")>=0,
            "SESSION_DURATION_NOT_OBSERVED")
    return r,raw,png

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence-root",required=True,type=Path)
    p.add_argument("--output-root",required=True,type=Path)
    p.add_argument("--repository",required=True)
    p.add_argument("--commit",required=True)
    p.add_argument("--tree",required=True)
    p.add_argument("--run-id",required=True)
    p.add_argument("--run-attempt",type=int,required=True)
    p.add_argument("--attempt",required=True)
    a=p.parse_args()
    require(bool(HEX40.fullmatch(a.commit)) and bool(HEX40.fullmatch(a.tree)),"SOURCE_IDENTITY_INVALID")
    require(bool(ATTEMPT.fullmatch(a.attempt)),"ATTEMPT_IDENTITY_INVALID")
    require(a.repository=="mauedgar/ts-execution-lab" and
            a.run_id.isdecimal() and a.run_attempt>=1,"NATIVE_SOURCE_IDENTITY_INVALID")
    require(a.evidence_root.is_dir() and not a.evidence_root.is_symlink(),"UNSAFE_EVIDENCE_ROOT")
    require(not a.output_root.exists() and not a.output_root.is_symlink(),"CREATE_ONLY_OUTPUT_COLLISION")
    tool_raw=read_file(a.evidence_root/"TOOLCHAIN.json")
    t=safe_json(tool_raw)
    require(t.get("schema")=="ts-ee/q5b/toolchain-local/v0" and
            t.get("provider_native_verified") is False and t.get("product_accepted") is False,
            "TOOLCHAIN_PROVENANCE_OVERCLAIM")
    for name in ("chrome","driver"):
        item=t.get(name,{})
        require(isinstance(item.get("version"),str) and bool(item.get("version")) and
                bool(HEX64.fullmatch(str(item.get("sha256","")))) and
                type(item.get("bytes")) is int and item.get("bytes")>0,
                "INVALID_TOOLCHAIN_BYTES_"+name)
    require(t.get("runner_os")=="ubuntu-24.04","UNEXPECTED_OS")
    sources=[]
    for w in WIDTHS:
        sources.append((w,*local_source(a.evidence_root,w)))
    # Separate output directory creates only new files in one isolated CI workspace.
    a.output_root.mkdir(parents=True,exist_ok=False)
    artifacts=[]
    for w,r,raw,png in sources:
        name="shot-"+str(w)+".png"
        with (a.output_root/name).open("xb") as fp:
            fp.write(png)
        artifacts.append({"name":name,"kind":"SCREENSHOT","width":w,
                          "bytes":len(png),"sha256":digest(png)})
    log_data={"schema":"ts-ee/q5b/sanitized-fixture-events/v0",
              "subject":"NONPRODUCT_SYNTHETIC",
              "network_scope":"LOCAL_FIXTURE_SERVER_ONLY",
              "browser_context_network_metrics":"NOT_MEASURED",
              "events":[{"viewport":w,
                         "scenario_checks":len(CHECKS),
                         "checks":{k:r["checks"][k] for k in CHECKS},
                         "fixture_http_counts":{k:r["local_http_events"][k] for k in
                             ("home","product","deniedSku","notFound","serverError","scriptError")},
                         "session_create_ms":r["session_create_ms"],
                         "direct_driver_exit_observed":True,
                         "descendants_attested":False} for w,r,_,_ in sources]}
    log_bytes=(json.dumps(log_data,sort_keys=True,indent=2)+"\n").encode("utf-8")
    require(not any(m.encode() in log_bytes for m in MARKERS),"LOG_MARKER_LEAK")
    with (a.output_root/"sanitized-q5b-log.json").open("xb") as fp:
        fp.write(log_bytes)
    artifacts.append({"name":"sanitized-q5b-log.json","kind":"LOG",
                      "bytes":len(log_bytes),"sha256":digest(log_bytes)})
    original_bytes=b"\n--Q5B-BOUNDARY--\n".join([tool_raw]+[x[2] for x in sources])
    report={
      "schema":"ts-ee/frontend-browser-qa/v0.1",
      "product_effect":"NONE",
      "attempt":a.attempt,
      "source":{"repository":a.repository,"commit":a.commit,"tree":a.tree,"subject_kind":"SYNTHETIC"},
      "runner":{"engine":"CHROMEDRIVER_NODE","version":t["driver"]["version"],
          "os":t["runner_os"],"native_run_id":a.run_id,"head_sha":a.commit,
          "attempt_number":a.run_attempt,
          "browser_version":t["chrome"]["version"],
          "browser_binary_sha256":t["chrome"]["sha256"],
          "browser_binary_bytes":t["chrome"]["bytes"],
          "driver_version":t["driver"]["version"],
          "driver_binary_sha256":t["driver"]["sha256"],
          "driver_binary_bytes":t["driver"]["bytes"]},
      "stages":{"identity":"PASS","dependencies":"PASS","integration":"SKIPPED",
                "build":"SKIPPED","browser":"PASS"},
      "scenarios":{name:"PASS" for name in
           ("viewport","routing","history","deep_link_refresh","sku_negative",
            "keyboard_focus","a11y_basic","console_http")},
      "viewports":[{"width":w,"status":"PASS"} for w in WIDTHS],
      "network":{"enforcement":"OBSERVE_ONLY","service_workers":"NOT_VERIFIED",
                 "outbound_attempted":None,"outbound_blocked":None,"outbound_escaped":None,
                 "measurement_scope":"LOCAL_FIXTURE_SERVER_ONLY","os_egress_attested":False},
      "artifacts":artifacts,
      "original":{"custody":"LOCAL_UNVERIFIED","sha256":digest(original_bytes),
                  "bytes":len(original_bytes),"reference":"LOCAL_NONPRODUCT_Q5B_ACTUAL_JSON_AND_TOOLCHAIN_BYTES"},
      "limitations":["LOCAL_FIXTURE_SERVER_ONLY_NETWORK_COUNTS_NOT_MEASURED",
                     "CHROME_DIRECT_CHILD_EXIT_NOT_DESCENDANT_ATTESTATION",
                     "SYNTHETIC_ROUTE_ERROR_FIXTURES_NOT_GENERIC_CDP_NETWORK_OR_CONSOLE",
                     "NO_HOST_OS_EGRESS_DENIAL","NO_PRODUCT_QA_ACCEPTANCE_OR_WCAG",
                     "NATIVE_PROVIDER_JOIN_EXTERNAL_TO_SELF_REPORT"],
      "functional_browser_status":"PASS",
      "network_assurance_status":"OBSERVE_ONLY_UNATTESTED",
      "terminal_result":"PASS_FUNCTIONAL_ONLY",
      "reported_verdict":"PARTIAL",
      "provider_native_verified":False,
      "Product_accepted":False
    }
    dst=a.output_root/"COMMON_RECEIPT_V01.json"
    with dst.open("x",encoding="utf-8") as fp:
        json.dump(report,fp,sort_keys=True,indent=2)
        fp.write("\n")
    print(json.dumps({"producer":"PASS_BOUNDED_Q5B_LOCAL",
        "artifact_count":len(artifacts),"widths":list(WIDTHS),
        "functional_browser_status":"PASS","network_assurance":"OBSERVE_ONLY_UNATTESTED",
        "provider_native_verified":False,"Product_accepted":False},sort_keys=True))

if __name__=="__main__":
    main()
