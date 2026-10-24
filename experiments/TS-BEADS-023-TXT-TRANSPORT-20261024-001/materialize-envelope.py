#!/usr/bin/env python3
"""023 transport-only: materialize original *text* artifacts using Product-qualified IR-TXT-CARRIER/1."""
from __future__ import annotations
import hashlib, io, json, os, pathlib, shutil, subprocess, sys, tarfile

LAB_REF="4d1fa2ec6a81a45f30782f271f6ac2d51d4e3125"
PRODUCT_REF="7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56"
PRODUCT_TREE="8caa56d36f3efeba359bbbf65b158ffb01a19da6"
TOOL_BLOB="96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4"
PREFIX="experiments/TS-BEADS-023-DEBT-QUALIFICATION-20261024/"
MEMBERS={
 "authority-native":(40104370902,"ts-beads-023-source-native-authority-receipt",
 "beads023-source-native-reachability.json","4a15b5b3651349cf8da0ea63a723095fcc8dc91fcacef771e88f37e5b91c8e9a"),
 "graph-negative":(40104466243,"ts-beads-023-native-graph-receipt",
 "beads023-causal-graph-result.json","570966abdda2ddcf502a1f3c2d3e44d5f15039c7159ceef2f3a2594e017f7e6e"),
 "graph-mitigation":(40104741250,"ts-beads-023-controlled-writer-receipt",
 "beads023-guarded-writer-result.json","7f99f8badb776bbeca21d8a1fea89fa0fd17e94baecfd6d6d87270bd2933c0b4"),
 "authority-guard":(40104867163,"ts-beads-023-authority-guard-receipt",
 "beads023-guard-native-result.json","4a0534dc3366df1a782cf13b770a4add56219c3e04f7c710a2a0267375706686"),
 "provider-original":(40104370902,"ts-beads-023-external-provider-40104370902",
 "ts-beads-023-external-original.json","14bd7b15c34957c4cd851be1fcef01d7e0bf654a45469741308e36d3360822b5"),
}
REPORTS=["RESULT.md","BEADS_FIRST_PRODUCT_CHANGE_CANDIDATE.md"]
OUTPUT="transport/TS-BEADS-023-REVIEW-TXT-20261024-001/EVIDENCE_CARRIER.txt"
def run(*args, cwd=None):
 r=subprocess.run(args,cwd=cwd,encoding="utf-8",capture_output=True,check=False,timeout=120)
 if r.returncode:raise RuntimeError(f"command failed {args[:3]!r}: {r.stderr[-600:]}")
 return r.stdout.strip()
def sha(b):return hashlib.sha256(b).hexdigest()
def assert_equal(actual,expected,label):
 if actual!=expected:raise RuntimeError(f"{label} expected {expected}, observed {actual}")
def git_at(ref,filename):
 return subprocess.check_output(["git","show",f"{ref}:{filename}"],timeout=25)
def project_file(tool,mode,*args):
 run(sys.executable,str(tool),mode,*map(str,args))
def materialize():
 root=pathlib.Path.cwd().resolve()
 workspace=pathlib.Path(os.environ["RUNNER_TEMP"])/"ts-beads-023-txt-envelope-001"
 if workspace.exists():raise RuntimeError("no replay - workspace exists")
 workspace.mkdir(parents=True)
 if pathlib.Path(OUTPUT).exists():raise RuntimeError("create-only output already exists")
 # Acquire existing qualified Product tool mechanically. No Product write or attempt restart.
 product=workspace/"product-qualified-tool"
 run("git","clone","--quiet","--filter=blob:none","--no-checkout",
  "https://github.com/mauedgar/tecnotron-ai.git",str(product))
 run("git","-C",str(product),"checkout","--quiet","--detach",PRODUCT_REF)
 assert_equal(run("git","-C",str(product),"rev-parse","HEAD"),PRODUCT_REF,"Product HEAD")
 assert_equal(run("git","-C",str(product),"rev-parse","HEAD^{tree}"),PRODUCT_TREE,"Product tree")
 tool=product/"scripts/review_txt_carrier.py"
 assert_equal(run("git","-C",str(product),"hash-object","scripts/review_txt_carrier.py"),TOOL_BLOB,"Product qualified TXT tool")
 objects={}
 for tag,(rid,artifact,filename,expected) in MEMBERS.items():
  loc=workspace/"source"/tag
  loc.mkdir(parents=True)
  run("gh","run","download",str(rid),"--repo","mauedgar/ts-execution-lab",
   "--name",artifact,"--dir",str(loc))
  files=[p for p in loc.rglob("*") if p.is_file()]
  if len(files)!=1 or files[0].name!=filename:raise RuntimeError(f"artifact {tag} original member mismatch")
  value=files[0].read_bytes()
  assert_equal(sha(value),expected,f"original {tag} JSON bytes")
  json.loads(value)
  objects[f"evidence/{tag}/{filename}"]=value
 for file in REPORTS:
  value=git_at(LAB_REF,PREFIX+file)
  value.decode("utf-8")
  objects[f"reports/{file}"]=value
 objects["CONSUME.txt"]=(
  "TS-BEADS-023 TEXT ENVELOPE - READONLY RESEARCH TRANSFER\n"
  "Qualified format: IR-TXT-CARRIER/1 (reuse exact Product script blob "+TOOL_BLOB+")\n"
  "Original research subject: mauedgar/ts-execution-lab@"+LAB_REF+"\n"
  "Product read-only subject: mauedgar/tecnotron-ai:tools@"+PRODUCT_REF+"\n"
  "Purpose: evidence acquisition and competent review preparation, not Product acceptance.\n"
  "Preserve original GitHub Actions run, source sha and artifact zip digests in RESULT.md.\n"
  "No rerun. No Product mutation. No Developer grant. No TaskCycle transition.\n"
 ).encode("utf-8")
 # Deterministic, uncompressed intermediate TAR only, NOT the published transport format.
 archive=workspace/"original.tar"
 with tarfile.open(archive,"w",format=tarfile.USTAR_FORMAT) as tar:
  for name,data in sorted(objects.items()):
   obj=tarfile.TarInfo(name)
   obj.size=len(data)
   obj.mtime=0
   obj.mode=0o444
   obj.uid=obj.gid=0
   obj.uname=obj.gname=""
   tar.addfile(obj,io.BytesIO(data))
 dest=root/OUTPUT;dest.parent.mkdir(parents=True,exist_ok=True)
 creation=workspace/"create-report.json"
 verification=workspace/"verify-report.json"
 extraction=workspace/"extract-report.json"
 recovery=workspace/"recovered"
 project_file(tool,"project",archive,"--out",dest,"--report",creation)
 project_file(tool,"verify",dest,"--report",verification)
 project_file(tool,"extract",dest,"--out",recovery,"--report",extraction)
 for name,data in objects.items():
  assert_equal((recovery/name).read_bytes(),data,f"roundtrip {name}")
 for report in (creation,verification,extraction):
  obj=json.loads(report.read_text(encoding="utf-8"))
  if obj.get("status")!="PASS" or obj.get("member_payload_equivalence")!="PASS":
   raise RuntimeError(f"qualified verification failed {report.name}")
 raw=dest.read_bytes()
 if not raw.startswith(b"IR-TXT-CARRIER/1\n"):raise RuntimeError("wrong carrier format")
 if len(objects)!=8:raise RuntimeError("unexpected envelope inventory")
 print("TS_BEADS023_TXT_ENVELOPE=PASS;members=8;format=IR-TXT-CARRIER/1;Product=NONE")
 print("TS_BEADS023_ENVELOPE_SHA256="+sha(raw))
 print("TS_BEADS023_ENVELOPE_BYTES="+str(len(raw)))
 print("TS_BEADS023_ORIGINAL_ATTEMPTS_REPLAYED=0")
 return dest
if __name__=="__main__":
 materialize()
