#!/usr/bin/env python3
"""Experimental TS Remote State 002 P2: authenticated observer negative evidence.

Fixed original PG16 container, no Product or Neon access. Password stays INSIDE
PostgreSQL container; native host executes only fixed Docker argv (shell=False).
Nothing here authorizes itself: external source/IR admission is mandatory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

RUNNER_ID = "TS-RS002-P2-OBSERVER-20261118-001"
HOST = "DESKTOP-DJLBEQH"
CID = "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88"
DAEMON = "1219e4b8-5972-4880-8ebd-4fd2498a3e83"
NETWORK = "6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35"
VOLUME = "e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899"
IMAGE = "postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e"
DB = "ts_rs002_a02_lab"
OBSERVER = "ts_rs002_observer"
ADMIN = "ts_rs002_admin"
DOCKER = "/usr/bin/docker"
SOURCE_ROOT = Path("/home/tsops/ts-remote-state-002/p1-c001-structured-20261117-003")
RECEIPTS = SOURCE_ROOT / "P2-observer-20261118-001"
ADMISSION = SOURCE_ROOT / "admission_P2.json"
R001 = Path("/var/tmp/ts-rs002-a02-pg16-recovery-20261115-001/attempt-status.txt")
R001_SHA = "c66f4359dededc7221f13564178aa0749310f9d31d4dcc0541f65b35f529bd06"
C_TERMINAL = SOURCE_ROOT / "C" / "terminal.json"
C_SHA = "7aef5dff689e1ceb5575084f2445caf25116cff5a22917815400693d99316852"
SCHEMA = "ts_r3_global_head_20261107_001"
SECRET_MOUNT = "/run/secrets/observer.pass"

# Host HBA SCRAM is independently checked before any observer login.
HBA = "BEGIN READ ONLY; SELECT (SELECT COUNT(*) FROM pg_hba_file_rules WHERE error IS NOT NULL),(SELECT COUNT(*) FROM pg_hba_file_rules WHERE type IN ('host','hostssl','hostnossl') AND address IN ('127.0.0.1','0.0.0.0','all') AND auth_method='scram-sha-256'),(SELECT COUNT(*) FROM pg_hba_file_rules WHERE type IN ('host','hostssl','hostnossl') AND auth_method <> 'scram-sha-256'); COMMIT;"
SNAPSHOT = f"BEGIN READ ONLY; SELECT (SELECT COUNT(*) FROM {SCHEMA}.head),(SELECT COUNT(*) FROM {SCHEMA}.events),(SELECT COUNT(*) FROM {SCHEMA}.receipts); COMMIT;"
POSITIVE = f"BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; SELECT session_user,current_user,current_database(),current_setting('transaction_read_only'),current_setting('default_transaction_read_only'); SELECT COUNT(*) FROM {SCHEMA}.head; COMMIT;"
# Zero affected rows even if unauthorized DELETE surprisingly succeeds, then
# explicit rollback; READ WRITE intentionally probes ACL rather than being
# masked by observer's default_transaction_read_only=on.
DENY_DELETE = f"BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE; DELETE FROM {SCHEMA}.head WHERE FALSE; ROLLBACK;"
# Temporary object is session-local and transaction-rolled-back if privilege
# surprisingly exists; never writes the durable public or Product schema.
DENY_TEMP = "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE; CREATE TEMP TABLE ts_rs002_p2_negative_probe (id integer); ROLLBACK;"
DENY_ROLE = "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; SET ROLE ts_rs002_owner; ROLLBACK;"
STEPS = (
    ("hba", HBA, False),
    ("snapshot_before", SNAPSHOT, False),
    ("observer_read", POSITIVE, True),
    ("deny_delete", DENY_DELETE, True),
    ("deny_temp", DENY_TEMP, True),
    ("deny_role", DENY_ROLE, True),
    ("snapshot_after", SNAPSHOT, False),
)
# The shell is executed inside the original *isolated container* only. It
# reads the readonly mounted secret and execs psql. No password appears in
# host argv, Docker CLI environment, stdout, receipt, or Git transport.
OBSERVER_WRAPPER = 'PGPASSWORD=$(cat /run/secrets/observer.pass); export PGPASSWORD; exec psql -X -qAt -v ON_ERROR_STOP=1 -h 127.0.0.1 -U ts_rs002_observer -d ts_rs002_a02_lab -c "$1"'


def fail(code: str) -> None:
    raise RuntimeError(code)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_read(path: Path, limit: int = 16000) -> bytes:
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_nlink != 1 or st.st_mode & 0o022:
        fail("UNTRUSTED_INPUT_FILE")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st2 = os.fstat(fd)
        if (st.st_dev, st.st_ino) != (st2.st_dev, st2.st_ino):
            fail("INPUT_RACE")
        data = os.read(fd, limit + 1)
        if len(data) > limit:
            fail("INPUT_SIZE")
        return data
    finally:
        os.close(fd)


def private_dir(path: Path) -> None:
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        fail("UNTRUSTED_RESULT_DIR")


def admittance() -> tuple[str, str]:
    raw = safe_read(ADMISSION)
    j = json.loads(raw)
    required = {"protocol", "runner_id", "source_commit", "source_blob", "source_sha256", "review_original_blob", "review_verdict", "container_id", "prior_C_terminal_sha256", "allowed_effect"}
    if set(j) != required or j["protocol"] != "TS-RS002-P2-OBSERVER-20261118-v1" or j["runner_id"] != RUNNER_ID:
        fail("P2_ADMISSION_SCHEMA")
    if j["source_sha256"] != sha(Path(__file__).read_bytes()) or j["container_id"] != CID or j["prior_C_terminal_sha256"] != C_SHA:
        fail("P2_ADMISSION_SOURCE_MISMATCH")
    if j["allowed_effect"] != "P2_OBSERVER_ONE_SHOT" or j["review_verdict"] != "RECOMMEND":
        fail("P2_ADMISSION_NOT_GRANTED")
    for k in ("source_commit", "source_blob", "review_original_blob"):
        if not re.fullmatch("[0-9a-f]{40}", j[k]):
            fail("P2_UNVERIFIED_REF")
    # External Control MUST independently bind these refs/hashes to original
    # Git+IR; this local self-reference check alone grants no execution.
    return sha(raw), j["source_sha256"]


def read_output(argv: list[str], limit: int = 32000) -> str:
    child = subprocess.Popen(argv, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", errors="replace")
    try:
        stdout, _ = child.communicate(timeout=25)
    except subprocess.TimeoutExpired:
        # Preserve original process for reconciliation; never kill or retry.
        fail("NATIVE_INSPECTION_TIMEOUT_UNRECONCILED")
    if child.returncode != 0 or len(stdout) > limit:
        fail("NATIVE_PREFLIGHT_COMMAND_FAILED")
    return stdout.strip()


def preflight() -> tuple[str, str]:
    if os.uname().nodename.upper() != HOST or os.getuid() != 1000 or sys.version_info[:3] != (3, 15, 2):
        fail("WRONG_HOST_UID_OR_RUNTIME")
    private_dir(SOURCE_ROOT)
    admission_hash, source_hash = admittance()
    if sha(safe_read(C_TERMINAL)) != C_SHA:
        fail("PREVIOUS_C_ORIGINAL_DIGEST")
    c = json.loads(safe_read(C_TERMINAL))
    if c.get("status") != "PASS" or c.get("phase") != "C" or c.get("exit_code") != 0 or c.get("database_mutation") != "NONE_READ_ONLY" or c.get("container_id") != CID:
        fail("PREVIOUS_C_NOT_PASS")
    if sha(R001.read_bytes()) != R001_SHA:
        fail("ORIGINAL_R001_MISMATCH")
    if read_output([DOCKER,"info","--format","{{.ID}}"] ) != DAEMON:
        fail("WRONG_DOCKER_DAEMON")
    v = json.loads(read_output([DOCKER,"container","inspect",CID]))
    if type(v) is not list or len(v) != 1:
        fail("CONTAINER_INSPECT_UNEXPECTED")
    c = v[0]
    if c.get("Id") != CID or c["State"].get("Running") is not True or c["State"].get("RestartCount",0) != 0 or c.get("RestartCount") != 0:
        fail("CONTAINER_STATE_DRIFT")
    if c["Config"].get("Image") != IMAGE or c["HostConfig"].get("Privileged") or c["HostConfig"].get("PortBindings"):
        fail("CONTAINER_PRIVILEGE_OR_IMAGE_DRIFT")
    nets = c["NetworkSettings"]["Networks"]
    if len(nets) != 1 or next(iter(nets.values())).get("NetworkID") != NETWORK:
        fail("CONTAINER_NETWORK_DRIFT")
    mounts = c["Mounts"]
    if len([m for m in mounts if m.get("Destination") == "/var/lib/postgresql/data" and m.get("Name") == VOLUME and m.get("Type") == "volume"]) != 1:
        fail("CONTAINER_PGDATA_DRIFT")
    secret = [m for m in mounts if m.get("Destination") == SECRET_MOUNT]
    if len(secret) != 1 or secret[0].get("RW") is not False or secret[0].get("Type") != "bind":
        fail("OBSERVER_SECRET_MOUNT_DRIFT")
    if c.get("Image") != read_output([DOCKER,"image","inspect","--format","{{.Id}}",IMAGE]):
        fail("EFFECTIVE_IMAGE_DRIFT")
    if RECEIPTS.exists() or RECEIPTS.is_symlink():
        fail("P2_ATTEMPT_ALREADY_EXISTS_NO_RETRY")
    return admission_hash, source_hash


def cmd_for(sql: str, observer: bool) -> list[str]:
    base = [DOCKER,"exec","--user","postgres",CID]
    if observer:
        return base + ["sh","-ec",OBSERVER_WRAPPER,"p2-fixed",sql]
    return base + ["psql","-X","-qAt","-v","ON_ERROR_STOP=1","-U",ADMIN,"-d",DB,"-c",sql]


def parse_rows(stdout: str) -> list[str]:
    if "\x00" in stdout or len(stdout) > 6000:
        fail("UNSAFE_NATIVE_OUTPUT")
    return [s.strip() for s in stdout.splitlines() if s.strip() not in ("BEGIN","COMMIT","ROLLBACK") and s.strip()]


def interpret(step: str, returncode: int, stdout: str, stderr: str, before: list[str] | None) -> list[str]:
    if step == "hba":
        rows = parse_rows(stdout)
        if returncode != 0 or len(rows) != 1 or not re.fullmatch(r"0\|[1-9][0-9]*\|0",rows[0]):
            fail("HOST_SCRAM_HBA_NOT_ATTESTED")
        return rows
    if step in ("snapshot_before","snapshot_after"):
        rows = parse_rows(stdout)
        if returncode != 0 or len(rows) != 1 or not re.fullmatch(r"[0-9]+\|[0-9]+\|[0-9]+",rows[0]):
            fail("SNAPSHOT_INVALID")
        if step == "snapshot_after" and rows != before:
            fail("SCHEMA_ROWS_CHANGED")
        return rows
    if step == "observer_read":
        rows = parse_rows(stdout)
        if returncode != 0 or len(rows) != 2 or rows[0] != "ts_rs002_observer|ts_rs002_observer|ts_rs002_a02_lab|on|on" or not re.fullmatch("[0-9]+",rows[1]):
            fail("OBSERVER_TCP_READ_NOT_PROVEN")
        return rows
    errors = {"deny_delete":"permission denied for table head", "deny_temp":"permission denied to create temporary tables", "deny_role":"permission denied to set role"}
    if step not in errors:
        fail("UNRECOGNIZED_STEP")
    # psql ON_ERROR_STOP returns 3 for actual SQL errors. In particular, a
    # READ ONLY error does not pass the ACL denial test; DELETE uses READ WRITE.
    if returncode != 3 or errors[step] not in stderr.lower():
        fail("OBSERVER_NEGATIVE_FAILED_" + step.upper())
    return ["ERROR: " + errors[step]]


def write_once(path: Path, obj: dict) -> bytes:
    raw = (json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True) + "\n").encode()
    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    dfd = os.open(path.parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try: os.fsync(dfd)
    finally: os.close(dfd)
    return raw


def execute() -> None:
    admission_sha, source_sha = preflight()
    RECEIPTS.mkdir(mode=0o700)
    private_dir(RECEIPTS)
    intent = write_once(RECEIPTS/"intent.json", {"runner_id":RUNNER_ID,"admission_sha256":admission_sha,"source_sha256":source_sha,"prior_C_original_sha256":C_SHA,"container_id":CID,"status":"PENDING","start_utc":now(),"Product_effect":"NONE"})
    status = "UNKNOWN"
    code = "P2_UNVERIFIED"
    steps: list[dict] = []
    before = None
    try:
        for name, sql, observer in STEPS:
            cmd = cmd_for(sql, observer)
            child = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
            step = {"name":name,"pid":child.pid,"sql_sha256":sha(sql.encode()),"observer":observer,"start_utc":now(),"status":"UNKNOWN"}
            write_once(RECEIPTS/("start_"+name+".json"),step)
            try:
                stdout, stderr = child.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                fail("NATIVE_CHILD_TIMEOUT_UNRECONCILED")
            rows = interpret(name,child.returncode,stdout,stderr,before)
            if name == "snapshot_before": before = rows
            step.update({"status":"PASS","end_utc":now(),"exit_code":child.returncode,
                         "result":rows,"stderr_sha256":sha(stderr.encode("utf-8"))})
            write_once(RECEIPTS/("result_"+name+".json"),step)
            steps.append({"name":name,"result":rows,"exit_code":child.returncode,"status":"PASS"})
        status,code = "PASS","OK"
    except RuntimeError as e:
        code = str(e) if re.fullmatch("[A-Z0-9_]{3,100}",str(e)) else "P2_STEP_BLOCKED"
        status = "UNKNOWN" if code == "NATIVE_CHILD_TIMEOUT_UNRECONCILED" else "FAILED"
    except Exception:
        status,code = "UNKNOWN","UNEXPECTED_NATIVE_EXCEPTION"
    terminal = {"runner_id":RUNNER_ID,"status":status,"code":code,"container_id":CID,"admission_sha256":admission_sha,"source_sha256":source_sha,"prior_C_original_sha256":C_SHA,"intent_sha256":sha(intent),"steps":steps,"end_utc":now(),"Product_effect":"NONE","database_mutation":"NONE_READONLY_OR_ROLLEDBACK" if status == "PASS" else "NOT_PROVEN","no_retry":True}
    write_once(RECEIPTS/"terminal.json",terminal)
    print(json.dumps(terminal,sort_keys=True))
    if status != "PASS": sys.exit(3)


def main() -> None:
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight",action="store_true")
    group.add_argument("--run",action="store_true")
    args=ap.parse_args()
    try:
        if args.preflight:
            preflight()
            print("P2_PREFLIGHT_PASS effect=NONE")
        else: execute()
    except Exception as e:
        c=str(e) if re.fullmatch("[A-Z0-9_]{3,100}",str(e)) else "P2_PRECONDITION_BLOCKED"
        print("BLOCKED_"+c,file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
