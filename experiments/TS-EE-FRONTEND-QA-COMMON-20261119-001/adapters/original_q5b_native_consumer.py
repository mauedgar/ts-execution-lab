#!/usr/bin/env python3
"""Consume exact *historical* GitHub Q5B native ZIP using new strict v0.1 caller pins.
NONPRODUCT, isolated Ubuntu CI. No browser subprocess and no Product acceptance.
"""
import argparse
import hashlib
import io
import json
import os
import pathlib
import stat
import zipfile

NATIVE_RUN=45229561752
NATIVE_ARTIFACT=14847471289
NATIVE_HEAD="8eb4e4d16b8ca0aea956c1e8d8e15be012470b01"
NATIVE_TREE="2e7adb5f424f055a52f869e7e0d0ca8423060808"
NATIVE_SHA="8f3b07c110a612f9821b367ffb50583c86e76e65d1a9052043716f42e9ae58ac"
NATIVE_BYTES=107550
NATIVE_ATTEMPT="TS-EE-004-IR005-F01F02-20261123-001-A001"
WIDTHS=(320,375,768,1440)
NAMES=sorted(
  ["TOOLCHAIN.json","common/COMMON_RECEIPT_V01.json","common/VALIDATION.json",
   "common/sanitized-q5b-log.json"]+
  [f"{w}/Q5B_REPORT.json" for w in WIDTHS]+
  [f"{w}/q5b-{w}.png" for w in WIDTHS]+
  [f"common/shot-{w}.png" for w in WIDTHS])
BOUNDARY=b"\n--Q5B-BOUNDARY--\n"
MAX_ZIP_BYTES=250000
MAX_MEMBER_BYTES=8*1024*1024
MAX_TOTAL_UNCOMPRESSED=800000

def require(value,msg):
    if not value: raise ValueError(msg)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def checked_json(raw):
    return json.loads(raw.decode("utf-8"))
def verify_provider_meta(run,artifact):
    require(run.get("id")==NATIVE_RUN,"NATIVE_RUN_ID_MISMATCH")
    require(run.get("head_sha")==NATIVE_HEAD,"NATIVE_RUN_HEAD_MISMATCH")
    require(run.get("run_attempt")==1 and run.get("status")=="completed" and
            run.get("conclusion")=="success","NATIVE_RUN_NOT_ORIGINAL_SUCCESS")
    require(artifact.get("id")==NATIVE_ARTIFACT,"NATIVE_ARTIFACT_ID_MISMATCH")
    require(artifact.get("size_in_bytes")==NATIVE_BYTES and
            artifact.get("digest")=="sha256:"+NATIVE_SHA,"NATIVE_ARTIFACT_METADATA_MISMATCH")
    require(artifact.get("expired") is False,"ORIGINAL_NATIVE_ARTIFACT_EXPIRED")
    link=artifact.get("workflow_run") or {}
    require(link.get("id")==NATIVE_RUN and link.get("head_sha")==NATIVE_HEAD,
            "NATIVE_ARTIFACT_RUN_HEAD_MISMATCH")

def verify_zip(raw, expected_hash=NATIVE_SHA):
    require(len(raw)==NATIVE_BYTES and len(raw)<=MAX_ZIP_BYTES and sha(raw)==expected_hash,
            "NATIVE_ZIP_HASH_OR_SIZE_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(raw),"r") as z:
        names=z.namelist()
        require(len(names)==len(NAMES) and len(set(names))==len(NAMES) and
                sorted(names)==NAMES,"NATIVE_MEMBER_INVENTORY_MISMATCH")
        total=0
        for info in z.infolist():
            require(not info.is_dir() and
                    (info.external_attr>>16)&stat.S_IFMT(0o170000) in (0,stat.S_IFREG),
                    "UNSAFE_ZIP_MEMBER_MODE")
            require(info.file_size<=MAX_MEMBER_BYTES,"OVERSIZE_ZIP_MEMBER")
            total+=info.file_size
        require(total<=MAX_TOTAL_UNCOMPRESSED,"ZIP_BOMB_LIMIT")
        require(z.testzip() is None,"ZIP_CRC_MISMATCH")
        members={name:z.read(name) for name in names}
    return members

def verify_original_members(members):
    report=checked_json(members["common/COMMON_RECEIPT_V01.json"])
    require(report.get("schema")=="ts-ee/frontend-browser-qa/v0.1","WRONG_SCHEMA")
    require(report.get("source",{}).get("commit")==NATIVE_HEAD and
            report.get("source",{}).get("tree")==NATIVE_TREE,
            "ORIGINAL_COMMON_SOURCE_MISMATCH")
    runner=report.get("runner",{})
    require(runner.get("native_run_id")==str(NATIVE_RUN) and runner.get("attempt_number")==1 and
            runner.get("engine")=="CHROMEDRIVER_NODE","ORIGINAL_COMMON_RUNNER_MISMATCH")
    require(report.get("attempt")==NATIVE_ATTEMPT and
            report.get("source",{}).get("subject_kind")=="SYNTHETIC",
            "ORIGINAL_COMMON_PROFILE_MISMATCH")
    original=report.get("original",{})
    composite=BOUNDARY.join([members["TOOLCHAIN.json"]]+
                            [members[f"{w}/Q5B_REPORT.json"] for w in WIDTHS])
    require(original.get("custody")=="LOCAL_UNVERIFIED" and
            original.get("bytes")==len(composite) and original.get("sha256")==sha(composite),
            "ORIGINAL_Q5B_COMPOSITE_HASH_MISMATCH")
    artifacts={a["name"]:a for a in report.get("artifacts",[])}
    require(set(artifacts)=={f"shot-{w}.png" for w in WIDTHS}|{"sanitized-q5b-log.json"},
            "ORIGINAL_COMMON_ARTIFACT_SET_MISMATCH")
    manifest={}
    for name,raw in members.items():manifest[name]={"bytes":len(raw),"sha256":sha(raw)}
    for w in WIDTHS:
        png=members[f"{w}/q5b-{w}.png"]
        checked=members[f"common/shot-{w}.png"]
        original_report=checked_json(members[f"{w}/Q5B_REPORT.json"])
        require(png==checked and
                original_report.get("screenshot",{}).get("sha256")==sha(png) and
                artifacts[f"shot-{w}.png"]["sha256"]==sha(checked),
                "ORIGINAL_SCREENSHOT_CROSS_HASH_MISMATCH")
        require(original_report.get("overall")=="PASS_BOUNDED_Q5B_BROWSER" and
                len(original_report.get("checks",{}))==14 and
                all(v=="PASS" for v in original_report["checks"].values()),
                "ORIGINAL_Q5B_FIXTURE_CHECKS_MISSING")
    log=members["common/sanitized-q5b-log.json"]
    require(artifacts["sanitized-q5b-log.json"]["sha256"]==sha(log),
            "ORIGINAL_COMMON_LOG_HASH_MISMATCH")
    require(report["network_assurance_status"]=="OBSERVE_ONLY_UNATTESTED" and
            report["functional_browser_status"]=="PASS" and
            report["Product_accepted"] is False and report["provider_native_verified"] is False,
            "SECURITY_SCOPE_OVERCLAIM")
    return report,manifest

def create_only_output(out, members, manifest):
    require(not out.exists() and not out.is_symlink(),"CREATE_ONLY_OUTPUT_COLLISION")
    out.mkdir(parents=False,mode=0o700,exist_ok=False)
    try:
        for name in sorted(members):
            if not name.startswith("common/") or name=="common/VALIDATION.json":continue
            local=out/name[len("common/"):]
            require("/" not in local.name and local.name not in ("", ".", ".."),"UNSAFE_OUTPUT")
            with local.open("xb") as stream:stream.write(members[name])
        with (out/"ORIGINAL_MANIFEST.json").open("x",encoding="utf8") as stream:
            json.dump({"source":"NATIVE_GITHUB_ACTIONS_ZIP_ORIGINAL",
                       "native_run_id":NATIVE_RUN,"artifact_id":NATIVE_ARTIFACT,
                       "archive_sha256":NATIVE_SHA,"archive_bytes":NATIVE_BYTES,
                       "source_commit":NATIVE_HEAD,"source_tree":NATIVE_TREE,
                       "members":manifest,"new_browser_sessions":0,
                       "Product_effect":"NONE","method_accepted":False},stream,sort_keys=True,indent=2)
            stream.write("\n")
    except BaseException:
        (out/"INCOMPLETE_ORIGINAL_CONSUMER").touch(exist_ok=False)
        raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=pathlib.Path,required=True)
    p.add_argument("--run-meta",type=pathlib.Path,required=True)
    p.add_argument("--artifact-meta",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    run=json.loads(a.run_meta.read_text("utf8"))
    artifact=json.loads(a.artifact_meta.read_text("utf8"))
    verify_provider_meta(run,artifact)
    members=verify_zip(a.zip.read_bytes())
    report,manifest=verify_original_members(members)
    create_only_output(a.out,members,manifest)
    print(json.dumps({"status":"NATIVE_HISTORICAL_BYTES_JOIN_PASS",
                      "source_run":NATIVE_RUN,"source_artifact":NATIVE_ARTIFACT,
                      "source_sha256":NATIVE_SHA,"member_count":len(NAMES),
                      "expected_engine":"CHROMEDRIVER_NODE",
                      "expected_subject_kind":"SYNTHETIC",
                      "expected_evidence_profile":"Q5B_SYNTHETIC_LOCAL_V01",
                      "new_browser_sessions":0,"Product_effect":"NONE"},sort_keys=True))

if __name__=="__main__": main()
