#!/usr/bin/env python3
"""Reuse exact Product-qualified IR-TXT-CARRIER/1: project, verify, extract original 024 result."""
import hashlib, io, json, os, pathlib, subprocess, sys, tarfile
def command(*args):
 x=subprocess.run(args,check=False,capture_output=True,text=True,timeout=75)
 if x.returncode:raise RuntimeError(f"{args[0]} failed: {x.stderr[-650:]}")
 return x.stdout.strip()
root=pathlib.Path(os.environ["GITHUB_WORKSPACE"]).resolve()
product=pathlib.Path(os.environ["PRODUCT_ROOT"]).resolve()
receipt=pathlib.Path(os.environ["RESULT_PATH"]).resolve()
target=root/"transport/TS-BEADS-024-READ-MODEL-20261024-001/EVIDENCE_CARRIER.txt"
if target.exists():raise RuntimeError("CREATE_ONLY_ENVELOPE_EXISTS_NO_RETRY")
result=receipt.read_bytes()
data=json.loads(result)
if data.get("status")!="PASS_NONAUTHORITATIVE_READ_MODEL_WITH_RACE_DETECTION" or data.get("Product_effect")!="NONE" or len(data.get("checks",[]))<15:
 raise RuntimeError("ORIGINAL_RUN_NOT_QUALIFIED")
rel="experiments/TS-BEADS-024-GRAPH-READ-MODEL-20261024-001/"
plan=(root/rel/"PLAN.md").read_bytes()
readme=(f"TS Beads 024 original non-Product result\nProduct authority: NONE\n"
        f"GitHub original run: {os.environ['GITHUB_RUN_ID']}\n"
        f"Original code Git SHA: {os.environ['GITHUB_SHA']}\n"
        "Source: original result.json + exact selection PLAN.md\n"
        "Transport format: IR-TXT-CARRIER/1 (reuse qualified Product script)\n"
        "This is a read model, not an acceptance or Independent Review.\n").encode()
members={
 "CONTROL_EXPERIMENTAL.txt":readme,
 "evidence/ORIGINAL_024_RESULT.json":result,
 "selection/PLAN.md":plan
}
scratch=pathlib.Path(os.environ["RUNNER_TEMP"])/"beads024-envelope-unique"
if scratch.exists():raise RuntimeError("SCRATCH_IDENTITY_ALREADY_EXISTS")
scratch.mkdir(parents=True)
tar=scratch/"source-internal.tar"
with tarfile.open(tar,"w",format=tarfile.USTAR_FORMAT) as f:
 for key,value in sorted(members.items()):
  t=tarfile.TarInfo(key)
  t.size=len(value);t.mode=0o444;t.mtime=0;t.uid=t.gid=0;t.uname=t.gname=""
  f.addfile(t,io.BytesIO(value))
qualified=product/"scripts/review_txt_carrier.py"
expected="96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4"
actual=command("git","-C",str(product),"hash-object","scripts/review_txt_carrier.py")
if actual!=expected:raise RuntimeError("PRODUCT_QUALIFIED_TXT_TOOL_HASH_CHANGED")
target.parent.mkdir(parents=True,exist_ok=True)
project=scratch/"project.json"
verify=scratch/"verify.json"
extraction=scratch/"extract.json"
recovered=scratch/"recovered"
command(sys.executable,str(qualified),"project",str(tar),"--out",str(target),"--report",str(project))
command(sys.executable,str(qualified),"verify",str(target),"--report",str(verify))
command(sys.executable,str(qualified),"extract",str(target),"--out",str(recovered),"--report",str(extraction))
for name,original in members.items():
 if (recovered/name).read_bytes()!=original:raise RuntimeError("TXT_ROUNDTRIP_MISMATCH "+name)
for file in (project,verify,extraction):
 status=json.loads(file.read_text(encoding="utf8"))
 if status.get("status")!="PASS" or status.get("member_payload_equivalence")!="PASS":
  raise RuntimeError("PRODUCT_QUALIFIED_CARRIER_VERIFICATION_NOT_PASS")
payload=target.read_bytes()
if not payload.startswith(b"IR-TXT-CARRIER/1\n"):raise RuntimeError("TXT_MAGIC_INVALID")
digest=hashlib.sha256(payload).hexdigest()
print("TS_BEADS024_TXT=PASS;members=3;format=IR-TXT-CARRIER/1")
print("TS_BEADS024_TXT_SHA256="+digest)
print("TS_BEADS024_TXT_BYTES="+str(len(payload)))
print("TS_BEADS024_NO_ORIGINAL_PROVIDER_REPLAY=PASS")
