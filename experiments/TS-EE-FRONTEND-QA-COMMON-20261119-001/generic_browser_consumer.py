#!/usr/bin/env python3
"""NONPRODUCT generic browser positive-evidence consumer; no provider or Product admission."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import receipt_validator_v01 as common

MAX_JSON=1024*1024
ID=re.compile(r"^[a-z][a-z0-9_]{0,63}$")
CONTRACT_KEYS={"schema","profile","source","attempt","run_id","run_attempt","engine","log_name","checks"}
SOURCE_KEYS={"repository","commit","tree","subject_kind"}

def require(ok,code):
    if not ok:
        raise ValueError(code)

def exact(obj,keys,code):
    require(isinstance(obj,dict) and set(obj)==keys,code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def pairs(items):
    result={}
    for key,value in items:
        require(key not in result,"DUPLICATE_JSON_KEY")
        result[key]=value
    return result

def strict_json(raw):
    require(0<len(raw)<=MAX_JSON,"JSON_BYTE_LIMIT")
    def invalid_constant(_):
        raise ValueError("INVALID_JSON_CONSTANT")
    return json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_constant=invalid_constant)

def read_at(root_fd,name):
    require(isinstance(name,str) and common.NAME.fullmatch(name),"UNSAFE_NAME")
    return common.secure_read_artifact(root_fd,name)

def expected_contract(contract):
    exact(contract,CONTRACT_KEYS,"CONTRACT_FIELDS")
    require(contract["schema"]=="ts-ee/generic-browser-consumer-contract/v1" and
            contract["profile"]=="GENERIC_BROWSER_V01","CONTRACT_PROFILE")
    src=contract["source"]
    exact(src,SOURCE_KEYS,"SOURCE_FIELDS")
    require(isinstance(src["repository"],str) and
            re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",src["repository"]) and
            all(isinstance(src[k],str) and common.HEX40.fullmatch(src[k]) for k in ("commit","tree")) and
            src["subject_kind"] in common.SUBJECT_KINDS,"SOURCE_IDENTITY")
    require(isinstance(contract["attempt"],str) and common.ATTEMPT.fullmatch(contract["attempt"]),"ATTEMPT")
    require(isinstance(contract["run_id"],str) and re.fullmatch(r"[1-9][0-9]{0,30}",contract["run_id"]) and
            type(contract["run_attempt"]) is int and contract["run_attempt"]>=1,"RUN_IDENTITY")
    require(contract["engine"] in common.ENGINES,"ENGINE")
    require(isinstance(contract["log_name"],str) and common.NAME.fullmatch(contract["log_name"]),"LOG_NAME")
    matrix=contract["checks"]
    exact(matrix,set(common.SCENARIOS),"MATRIX_SCENARIOS")
    for scenario,rows in matrix.items():
        require(isinstance(rows,dict) and 0<len(rows)<=len(common.WIDTHS),"MATRIX_WIDTHS")
        require(set(rows)<=set(map(str,common.WIDTHS)),"MATRIX_WIDTHS")
        if scenario=="viewport":
            require(set(rows)==set(map(str,common.WIDTHS)),"VIEWPORT_MATRIX_INCOMPLETE")
        for checks in rows.values():
            require(isinstance(checks,list) and 0<len(checks)<=32 and
                    all(isinstance(x,str) and ID.fullmatch(x) for x in checks) and
                    len(set(checks))==len(checks),"MATRIX_CHECK_IDS")
    return contract

def verify(report,contract_raw,contract_sha256,root):
    # Caller pins, not producer assertions, select subject, profile and matrix.
    require(isinstance(contract_sha256,str) and common.HEX64.fullmatch(contract_sha256) and
            digest(contract_raw)==contract_sha256,"CONTRACT_HASH_MISMATCH")
    c=expected_contract(strict_json(contract_raw))
    require(isinstance(report,dict),"REPORT_FIELDS")
    require(report.get("source")==c["source"] and report.get("attempt")==c["attempt"],"SUBJECT_MISMATCH")
    runner=report.get("runner")
    require(isinstance(runner,dict) and runner.get("native_run_id")==c["run_id"] and
            type(runner.get("attempt_number")) is int and runner["attempt_number"]==c["run_attempt"] and
            runner.get("engine")==c["engine"],"RUN_MISMATCH")
    stages=report.get("stages")
    require(isinstance(stages,dict) and stages.get("browser")=="PASS","NOT_POSITIVE_BROWSER_RESULT")
    original=report.get("original")
    require(isinstance(original,dict) and original.get("custody")=="LOCAL_UNVERIFIED" and
            original.get("reference")==c["log_name"],"ORIGINAL_CUSTODY_OR_REFERENCE")
    artifacts=report.get("artifacts")
    require(isinstance(artifacts,list),"ARTIFACTS_FIELDS")
    entries=[a for a in artifacts if isinstance(a,dict) and a.get("name")==c["log_name"]]
    require(len(entries)==1 and entries[0].get("kind")=="LOG","ORIGINAL_LOG_REQUIRED")
    fd=common.secure_directory_fd(root)
    try:
        raw=read_at(fd,c["log_name"])
    finally:
        os.close(fd)
    require(type(entries[0].get("bytes")) is int and entries[0]["bytes"]==len(raw) and
            entries[0].get("sha256")==digest(raw) and type(original.get("bytes")) is int and
            original["bytes"]==len(raw) and original.get("sha256")==digest(raw),"ORIGINAL_LOG_BYTES")
    evidence=strict_json(raw)
    exact(evidence,{"schema","contract_sha256","source","attempt","run_id","run_attempt","engine","observed"},"LOG_FIELDS")
    require(evidence["schema"]=="ts-ee/generic-browser-evidence/v1" and
            evidence["contract_sha256"]==contract_sha256 and
            all(evidence[k]==c[k] for k in ("source","attempt","run_id","run_attempt","engine")) and
            type(evidence["run_attempt"]) is int,"LOG_IDENTITY")
    observed=evidence["observed"]
    exact(observed,set(common.SCENARIOS),"LOG_SCENARIOS")
    for scenario,rows in c["checks"].items():
        actual=observed[scenario]
        exact(actual,set(rows),"LOG_WIDTHS_"+scenario)
        for width,checks in rows.items():
            actual_checks=actual[width]
            exact(actual_checks,set(checks),"LOG_CHECKS_"+scenario+"_"+width)
            require(all(actual_checks[x]=="PASS" for x in checks),"LOG_NONPASS_"+scenario+"_"+width)
    result=common.evaluate(report,root,c["source"]["commit"],c["source"]["tree"],c["run_id"],
                           c["engine"],c["source"]["subject_kind"],c["profile"])
    result=common.enforce_consumer_requirements(result,require_local_bytes=True)
    require(result.get("status")=="VALID_SHAPE_UNATTESTED" and
            result.get("artifact_bytes_verified_locally") is True,"COMMON_STRICT_REJECT:"+str(result.get("errors",[])))
    # Source producer's measurements and provider origin are still external.
    return {"status":"VALID_GENERIC_MAPPING_UNATTESTED","contract_sha256":contract_sha256,
            "original_log_sha256":digest(raw),"original_log_bytes":len(raw),
            "observed_scenario_count":len(observed),"functional_browser_status":result["functional_browser_status"],
            "network_assurance_status":result["network_assurance_status"],"terminal_result":result["terminal_result"],
            "artifact_bytes_verified_locally":True,"provider_native_verified":False,"Product_accepted":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--receipt-name",required=True)
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--contract-sha256",required=True)
    a=p.parse_args()
    try:
        fd=common.secure_directory_fd(a.root)
        try: report=strict_json(read_at(fd,a.receipt_name))
        finally: os.close(fd)
        fd=common.secure_directory_fd(a.contract.parent)
        try: raw=read_at(fd,a.contract.name)
        finally: os.close(fd)
        result=verify(report,raw,a.contract_sha256,a.root)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError) as err:
        result={"status":"INVALID_OR_NOT_READY","reason":str(err),"provider_native_verified":False,"Product_accepted":False}
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="VALID_GENERIC_MAPPING_UNATTESTED" else 1

if __name__=="__main__":
    sys.exit(main())
