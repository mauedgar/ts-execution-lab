#!/usr/bin/env python3
"""Project fresh same-run Q5B source bytes into caller-bound generic evidence.
NONPRODUCT; no provider attestation, browser launch or historical artifact admission.
"""
import argparse
import copy
import json
from pathlib import Path
import sys
import generic_browser_consumer as g
from adapters import q5b_to_common_v01 as q

MAPPING={s:{str(w):list(checks) for w in q.WIDTHS}
         for s,checks in q.SCENARIO_CHECKS.items()}
LOG="generic-evidence.json"
RECEIPT="COMMON_RECEIPT_V01.json"

def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2)+"\n").encode("utf-8")

def contract(raw,pin):
    g.require(isinstance(pin,str) and g.common.HEX64.fullmatch(pin)
              and g.digest(raw)==pin,"CONTRACT_HASH_MISMATCH")
    c=g.expected_contract(g.strict_json(raw))
    g.require(c["engine"]=="CHROMEDRIVER_NODE" and
              c["source"]["repository"]=="mauedgar/ts-execution-lab" and
              c["source"]["subject_kind"]=="SYNTHETIC" and
              c["run_attempt"]==1 and c["log_name"]==LOG and c["checks"]==MAPPING,
              "BOUNDED_CALLER_POLICY")
    return c

def project(raw_root,common_root,output_root,contract_raw,pin):
    # These roots MUST be independently admitted stable, exclusive fresh-run roots
    # by the caller. Q5B raw reports lack native run IDs: local mapping alone cannot
    # prove freshness or provider origin. Caller must preserve the original ZIP/logs.
    c=contract(contract_raw,pin)
    report=g.strict_json(q.read_file(common_root/RECEIPT))
    g.require(report.get("source")==c["source"] and report.get("attempt")==c["attempt"],
              "Q5B_SUBJECT_MISMATCH")
    runner=report.get("runner",{})
    g.require(runner.get("native_run_id")==c["run_id"] and
              type(runner.get("attempt_number")) is int and
              runner["attempt_number"]==c["run_attempt"] and runner.get("engine")==c["engine"],
              "Q5B_RUN_MISMATCH")
    v=g.common.enforce_consumer_requirements(g.common.evaluate(
        report,common_root,c["source"]["commit"],c["source"]["tree"],c["run_id"],
        c["engine"],"SYNTHETIC","Q5B_SYNTHETIC_LOCAL_V01"),require_local_bytes=True)
    g.require(v.get("status")=="VALID_SHAPE_UNATTESTED" and
              v.get("artifact_bytes_verified_locally") is True,"Q5B_COMMON_REJECT")
    g.require(v.get("functional_browser_status")=="PASS" and
              v.get("network_assurance_status")=="OBSERVE_ONLY_UNATTESTED" and
              v.get("terminal_result")=="PASS_FUNCTIONAL_ONLY","Q5B_NETWORK_POLICY")
    tool_raw=q.read_file(raw_root/"TOOLCHAIN.json")
    tool=g.strict_json(tool_raw)
    g.require(tool.get("schema")=="ts-ee/q5b/toolchain-local/v0" and
              tool.get("runner_os")==runner.get("os")=="ubuntu-24.04" and
              tool.get("provider_native_verified") is False and tool.get("product_accepted") is False,
              "Q5B_TOOLCHAIN_POLICY")
    for original,mapped in (("chrome","browser"),("driver","driver")):
        entry=tool[original]
        for k,dest in (("version","version"),("sha256","binary_sha256"),("bytes","binary_bytes")):
            g.require(entry[k]==runner[mapped+"_"+dest] and type(entry[k]) is type(runner[mapped+"_"+dest]),
                      "Q5B_TOOLCHAIN_JOIN_"+original+"_"+k)
    sources={}
    for width in q.WIDTHS:
        r,raw,png=q.local_source(raw_root,width)
        g.require(g.strict_json(raw)==r and r.get("engine")==c["engine"],"Q5B_RAW_ENGINE_OR_JSON")
        name="shot-"+str(width)+".png"
        g.require(q.read_file(common_root/name)==png,"Q5B_SCREENSHOT_JOIN")
        sources[str(width)]=(r,raw,png)
    joined=b"\n--Q5B-BOUNDARY--\n".join([tool_raw]+[sources[str(w)][1] for w in q.WIDTHS])
    g.require(report["original"]=={"custody":"LOCAL_UNVERIFIED","sha256":g.digest(joined),
              "bytes":len(joined),"reference":"LOCAL_NONPRODUCT_Q5B_ACTUAL_JSON_AND_TOOLCHAIN_BYTES"},
              "Q5B_ORIGINAL_BYTES_JOIN")
    observed={s:{width:{check:sources[width][0]["checks"][check] for check in checks}
                 for width,checks in rows.items()} for s,rows in c["checks"].items()}
    for s,rows in observed.items():
        common_rows=report["scenario_evidence"][s]["viewports"]
        g.require({str(row["width"]):row["observed"] for row in common_rows}==rows,
                  "Q5B_SCENARIO_JOIN_"+s)
    evidence={"schema":"ts-ee/generic-browser-evidence/v1","contract_sha256":pin,
              **{k:c[k] for k in ("source","attempt","run_id","run_attempt","engine")},
              "observed":observed}
    log=encode(evidence)
    generic=copy.deepcopy(report)
    generic.pop("scenario_evidence")
    generic["artifacts"]=[]
    for width in q.WIDTHS:
        png=sources[str(width)][2]
        generic["artifacts"].append({"name":"shot-"+str(width)+".png","kind":"SCREENSHOT",
                                    "width":width,"bytes":len(png),"sha256":g.digest(png)})
    generic["artifacts"].append({"name":LOG,"kind":"LOG","bytes":len(log),"sha256":g.digest(log)})
    generic["original"]={"custody":"LOCAL_UNVERIFIED","reference":LOG,
                         "bytes":len(log),"sha256":g.digest(log)}
    generic["limitations"].append("GENERIC_MAPPING_LOCAL_ONLY_REQUIRES_FRESH_SAME_RUN_ORIGINAL_CUSTODY")
    # No mutation of raw/common roots, no reuse of occupied output. The marker
    # denotes complete writer publication, not independent consumer acceptance.
    with q.create_only_output(output_root) as fd:
        for width in q.WIDTHS:
            q.write_create_only(fd,"shot-"+str(width)+".png",sources[str(width)][2])
        q.write_create_only(fd,LOG,log)
        q.write_create_only(fd,RECEIPT,encode(generic))
    return generic

def main():
    p=argparse.ArgumentParser()
    for name in ("raw-root","common-root","output-root","contract"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--contract-sha256",required=True)
    a=p.parse_args()
    try:
        project(a.raw_root,a.common_root,a.output_root,q.read_file(a.contract),a.contract_sha256)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError,RecursionError) as err:
        print(json.dumps({"status":"INVALID_OR_NOT_READY","reason":str(err),"Product_effect":"NONE"}))
        return 1
    print(json.dumps({"status":"LOCAL_PROJECTION_WRITTEN_REQUIRES_CONSUMER",
                      "provider_native_verified":False,"Product_accepted":False,"Product_effect":"NONE"}))
    return 0

if __name__=="__main__":
    sys.exit(main())
