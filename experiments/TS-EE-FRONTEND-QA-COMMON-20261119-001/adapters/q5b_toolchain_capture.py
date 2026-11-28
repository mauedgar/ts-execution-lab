#!/usr/bin/env python3
"""Capture bounded host file/version identity for an isolated NONPRODUCT ChromeDriver run.
Not native PID/cgroup/executable attestation. No secrets or environment variables exported.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

def probe(executable):
    command=shutil.which(executable)
    if not command:
        raise RuntimeError("TOOLCHAIN_NOT_FOUND_"+executable.replace("-","_"))
    path=Path(os.path.realpath(command))
    if not path.is_file():
        raise RuntimeError("TOOLCHAIN_PATH_NOT_FILE")
    result=subprocess.run([command,"--version"],capture_output=True,text=True,timeout=12,check=True)
    version=result.stdout.strip().splitlines()[0][:256]
    if not version or any(ord(ch)<32 for ch in version):
        raise RuntimeError("VERSION_UNSAFE")
    digest=hashlib.sha256()
    total=0
    with path.open("rb") as fp:
        while chunk:=fp.read(1024*1024):
            total+=len(chunk)
            digest.update(chunk)
    if total<=0:
        raise RuntimeError("EMPTY_BINARY")
    return {"version":version,"sha256":digest.hexdigest(),"bytes":total,
            "path":str(path),"source":"HOST_FILE_READ_NOT_PROCESS_ATTESTATION"}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("USAGE: capture.py OUT.json")
    out=Path(sys.argv[1])
    if out.exists() or out.is_symlink():
        raise RuntimeError("CREATE_ONLY_TARGET_COLLISION")
    out.parent.mkdir(parents=True,exist_ok=True)
    data={
      "schema":"ts-ee/q5b/toolchain-local/v0",
      "chrome":probe("google-chrome"),
      "driver":probe("chromedriver"),
      "runner_os":"ubuntu-24.04",
      "provider_native_verified":False,
      "product_accepted":False
    }
    with out.open("x",encoding="utf-8") as fp:
        json.dump(data,fp,sort_keys=True,indent=2)
        fp.write("\n")
    print(json.dumps({"capture":"PASS","browser_bytes":data["chrome"]["bytes"],
      "driver_bytes":data["driver"]["bytes"],"source":"HOST_FILE_ONLY",
      "provider_native_verified":False,"product_accepted":False},sort_keys=True))

if __name__=="__main__":
    main()
