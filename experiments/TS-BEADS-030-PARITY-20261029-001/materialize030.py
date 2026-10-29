#!/usr/bin/env python3
"""Qualified Product IR-TXT-CARRIER/1, exact original 030 source and evidence comparison receipt and selection, no new transport format."""
from __future__ import annotations
import hashlib,io,json,os,pathlib,subprocess,sys,tarfile
from pathlib import Path
def cli(*arg):
 r=subprocess.run([str(x) for x in arg],capture_output=True,text=True,timeout=70)
 if r.returncode:raise RuntimeError(f"CLI_{arg[0]}: {r.stderr[-500:]}")
 return r.stdout.strip()
workspace=Path(os.environ["GITHUB_WORKSPACE"])
product=Path(os.environ["PRODUCT_ROOT"])
receipt=Path(os.environ["RESULT_PATH"])
target=workspace/"transport/TS-BEADS-030-PARITY-20261030-001/EVIDENCE_CARRIER.txt"
if target.exists():raise RuntimeError("CREATE_ONLY_NO_OVERWRITE")
raw=receipt.read_bytes()
original=json.loads(raw)
allow={"PASS_B_FIRST_SAME_PRODUCT_CONSUMER_SEMANTIC_PARITY_WITH_LIMITATIONS"}
if original.get("status") not in allow or original.get("Product_effect")!="NONE" or len(original.get("checks",[]))<10:
 raise RuntimeError("UNQUALIFIED_NATIVE_ORIGINAL_RECEIPT")
tool=product/"scripts/review_txt_carrier.py"
if cli("git","-C",product,"hash-object","scripts/review_txt_carrier.py")!="96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4":
 raise RuntimeError("PRODUCT_QUALIFIED_TOOL_IDENTITY_MISMATCH")
items={
 "original/RESULT030.json":raw,
 "original/A_KERNEL.json":Path(os.environ["A_RESULT"]).read_bytes(),
 "original/B_BEADS.json":Path(os.environ["B_RESULT"]).read_bytes(),
 "control/PLAN.md":(workspace/"experiments/TS-BEADS-030-PARITY-20261030-001/PLAN.md").read_bytes(),
 "README.txt":("NONPRODUCT Beads 030 original architecture comparison.\n"
               "Exact GitHub Actions run: "+os.environ["GITHUB_RUN_ID"]+"\n"+
               "Executable Git source: "+os.environ["GITHUB_SHA"]+"\n"+
               "No Product effect. Original attempt executed once. No credentials in this carrier.\n"
               "Native format: IR-TXT-CARRIER/1. No Product Independent Review or grant.\n").encode()
}
tmp=Path(os.environ["RUNNER_TEMP"])/"beads030-original-txt-unique"
if tmp.exists():raise RuntimeError("SCRATCH_EXISTS_NO_REPLAY")
tmp.mkdir(parents=True)
archive=tmp/"internal.tar"
with tarfile.open(archive,"w",format=tarfile.USTAR_FORMAT) as tar:
 for name,data in sorted(items.items()):
  member=tarfile.TarInfo(name)
  member.size=len(data);member.mtime=0;member.mode=0o444;member.uid=member.gid=0;member.uname=member.gname=""
  tar.addfile(member,io.BytesIO(data))
target.parent.mkdir(parents=True,exist_ok=True)
for cmd,args in (
 ("project",[archive,"--out",target,"--report",tmp/"project.json"]),
 ("verify",[target,"--report",tmp/"verify.json"]),
 ("extract",[target,"--out",tmp/"recovered","--report",tmp/"extract.json"])):
 cli(sys.executable,tool,cmd,*args)
for name,data in items.items():
 if (tmp/"recovered"/name).read_bytes()!=data:raise RuntimeError("BYTE_ROUNDTRIP_MISMATCH:"+name)
for name in ("project","verify","extract"):
 result=json.loads((tmp/(name+".json")).read_text())
 if result.get("status")!="PASS" or result.get("member_payload_equivalence")!="PASS":
  raise RuntimeError("QUALIFIED_TXT_VERIFICATION_FAILED:"+name)
carrier=target.read_bytes()
if not carrier.startswith(b"IR-TXT-CARRIER/1\n"):raise RuntimeError("UNKNOWN_CARRIER_FORMAT")
print("TS_BEADS030_TXT=PASS;members=5;format=IR-TXT-CARRIER/1")
print("TS_BEADS030_TXT_SHA256="+hashlib.sha256(carrier).hexdigest())
print("TS_BEADS030_TXT_BYTES="+str(len(carrier)))
print("TS_BEADS030_ORIGINAL_EFFECT_REPLAYED=NONE")
