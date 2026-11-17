#!/usr/bin/env python3
"""TS Remote State 002: one-time nonProduct C001 PostgreSQL catalog observer.

Only changes the execution surface for previously frozen read-only SQL.
No dynamic SQL, arbitrary shell, privilege escalation, new database or Product writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

OWNER = "TS_REMOTE_STATE_002"
RUNNER_ID = "TS-RS002-P1-C001-STRUCTURED-20261117-001"
HOST = "DESKTOP-DJLBEQH"
DAEMON = "1219e4b8-5972-4880-8ebd-4fd2498a3e83"
CID = "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88"
NETWORK = "6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35"
VOLUME = "e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899"
ORIGINAL_RECEIPT = Path("/var/tmp/ts-rs002-a02-pg16-recovery-20261115-001/attempt-status.txt")
ORIGINAL_RECEIPT_SHA256 = "c66f4359dededc7221f13564178aa0749310f9d31d4dcc0541f65b35f529bd06"
RESULTS = Path("/home/tsops/ts-remote-state-002/p1-c001-structured-20261117-001")
SQL_SOURCE_BLOB = "250a4e647b4f4cc780a7db3766244422d0b32bc3"
DOCKER = "/usr/bin/docker"
DB = "ts_rs002_a02_lab"
USER = "ts_rs002_admin"
SQL = {
    "A": "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY; SELECT current_database(), current_setting('server_version_num'), (SELECT system_identifier FROM pg_control_system()), (SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='ts_r3_global_head_20261107_001' AND c.relkind='r'), (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='ts_r3_global_head_20261107_001'); COMMIT;",
    "B": "BEGIN TRANSACTION READ ONLY; SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname IN ('ts_rs002_owner','ts_rs002_observer','ts_rs002_writer_a','ts_rs002_writer_b') ORDER BY rolname; COMMIT;",
    "C": "BEGIN TRANSACTION READ ONLY; SELECT has_database_privilege('ts_rs002_observer','ts_rs002_a02_lab','CONNECT'),has_database_privilege('ts_rs002_observer','ts_rs002_a02_lab','CREATE'),has_database_privilege('ts_rs002_observer','ts_rs002_a02_lab','TEMP'),has_schema_privilege('ts_rs002_observer','ts_r3_global_head_20261107_001','USAGE'),has_schema_privilege('ts_rs002_observer','ts_r3_global_head_20261107_001','CREATE'); SELECT c.relname,has_table_privilege('ts_rs002_observer',c.oid,'SELECT'),has_table_privilege('ts_rs002_observer',c.oid,'INSERT'),has_table_privilege('ts_rs002_observer',c.oid,'UPDATE'),has_table_privilege('ts_rs002_observer',c.oid,'DELETE'),has_table_privilege('ts_rs002_observer',c.oid,'TRUNCATE') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='ts_r3_global_head_20261107_001' AND c.relkind='r' ORDER BY c.relname; COMMIT;",
}
EXPECTED = {
    "A": ("ts_rs002_a02_lab|160015|7708034138639147047|3|19",),
    "B": (
        "ts_rs002_observer|t|f|f|f|f|f",
        "ts_rs002_owner|f|f|f|f|f|f",
        "ts_rs002_writer_a|t|f|f|f|f|f",
        "ts_rs002_writer_b|t|f|f|f|f|f",
    ),
    "C": (
        "t|f|f|t|f",
        "events|t|f|f|f|f",
        "head|t|f|f|f|f",
        "receipts|t|f|f|f|f",
    ),
}

def fail(code: str) -> None:
    raise RuntimeError(code)

def subprocess_output(argv: list[str], timeout: int = 25) -> str:
    result = subprocess.run(argv, shell=False, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout, check=False)
    if result.returncode != 0:
        fail("MECHANICAL_COMMAND_FAILED")
    if len(result.stdout) > 32000:
        fail("OUTPUT_LIMIT")
    return result.stdout.strip()

def normalize(stdout: str) -> tuple[str, ...]:
    if "\x00" in stdout or len(stdout) > 6000:
        fail("UNSAFE_SQL_STDOUT")
    return tuple(x.strip() for x in stdout.splitlines()
                 if x.strip() not in ("BEGIN", "COMMIT") and x.strip())

def check_result(phase: str, stdout: str) -> None:
    if normalize(stdout) != EXPECTED[phase]:
        fail("READONLY_CATALOG_MISMATCH_" + phase)

def read_only_preflight(phase: str) -> None:
    if os.uname().nodename.upper() != HOST or os.getuid() != 1000:
        fail("WRONG_HOST_OR_UID")
    if sys.version_info[:3] != (3, 15, 2):
        fail("WRONG_PYTHON_RUNTIME")
    if hashlib.sha256(ORIGINAL_RECEIPT.read_bytes()).hexdigest() != ORIGINAL_RECEIPT_SHA256:
        fail("ORIGINAL_R001_RECEIPT_MISMATCH")
    if subprocess_output([DOCKER, "info", "--format", "{{.ID}}"]) != DAEMON:
        fail("DOCKER_DAEMON_MISMATCH")
    raw = subprocess_output([DOCKER, "container", "inspect", CID])
    doc = json.loads(raw)
    if type(doc) is not list or len(doc) != 1:
        fail("CONTAINER_INSPECT_NOT_EXACT")
    c = doc[0]
    if c["Id"] != CID or c["State"]["Running"] is not True:
        fail("ORIGINAL_CONTAINER_NOT_RUNNING")
    if c["State"]["Status"] != "running" or c["RestartCount"] != 0:
        fail("ORIGINAL_CONTAINER_STATE_DRIFT")
    if c["HostConfig"]["Privileged"] or c["HostConfig"].get("PortBindings"):
        fail("EXCESS_CONTAINER_PRIVILEGE_OR_HOST_PORT")
    networks = c["NetworkSettings"]["Networks"]
    if len(networks) != 1 or next(iter(networks.values()))["NetworkID"] != NETWORK:
        fail("ORIGINAL_INTERNAL_NETWORK_MISMATCH")
    vols = [m for m in c["Mounts"] if m["Destination"] == "/var/lib/postgresql/data"]
    if len(vols) != 1 or vols[0]["Type"] != "volume" or vols[0]["Name"] != VOLUME:
        fail("ORIGINAL_PGDATA_VOLUME_MISMATCH")
    if c["Config"]["Image"] != "postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e":
        fail("ORIGINAL_IMAGE_DIGEST_MISMATCH")
    # All original credential/bootstrap external file binds remain read-only.
    for m in c["Mounts"]:
        if m["Type"] == "bind" and m["RW"] is not False:
            fail("MUTABLE_EXTERNAL_BIND")
    result_dir = RESULTS / phase
    if result_dir.exists() or result_dir.is_symlink():
        fail("PHASE_ATTEMPT_ALREADY_EXISTS_NO_RETRY")
    if phase != "A":
        prior = RESULTS / ("A" if phase == "B" else "B") / "terminal.json"
        result = json.loads(prior.read_text(encoding="utf-8"))
        if result.get("status") != "PASS" or result.get("phase") != ("A" if phase == "B" else "B") or result.get("runner_id") != RUNNER_ID:
            fail("PRIOR_PHASE_NOT_PROVEN_PASS")

def write_exclusive(path: Path, record: dict) -> None:
    data = (json.dumps(record, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

def run_phase(phase: str) -> None:
    read_only_preflight(phase)
    if not RESULTS.exists():
        RESULTS.mkdir(mode=0o700)
    if RESULTS.is_symlink() or RESULTS.stat().st_uid != os.getuid():
        fail("UNTRUSTED_RECEIPT_PARENT")
    dest = RESULTS / phase
    dest.mkdir(mode=0o700)
    write_exclusive(dest / "intent.json", {
        "runner_id": RUNNER_ID, "phase": phase, "container_id": CID,
        "sql_source_git_blob": SQL_SOURCE_BLOB, "effect": "PENDING_READONLY",
        "Product_effect": "NONE"
    })
    cmd = [DOCKER, "exec", "--user", "postgres", CID, "psql",
           "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-U", USER, "-d", DB, "-c", SQL[phase]]
    # No shell. Exactly one native SQL invocation per pre-committed phase identity.
    try:
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=30, check=False)
        if result.returncode != 0:
            fail("PSQL_NONZERO_EXIT")
        check_result(phase, result.stdout)
        terminal = {"runner_id": RUNNER_ID, "phase": phase, "status": "PASS",
                    "sql_source_git_blob": SQL_SOURCE_BLOB, "exit_code": result.returncode,
                    "stdout": normalize(result.stdout), "Product_effect": "NONE",
                    "database_mutation": "NONE_READ_ONLY"}
    except Exception as exc:
        code = str(exc)
        if not re.fullmatch(r"[A-Z0-9_]{3,100}", code):
            code = "UNVERIFIED_NATIVE_ERROR"
        terminal = {"runner_id": RUNNER_ID, "phase": phase, "status": "UNKNOWN_OR_FAILED",
                    "error": code, "Product_effect": "NONE", "no_retry": True}
    write_exclusive(dest / "terminal.json", terminal)
    print(json.dumps(terminal, sort_keys=True))
    if terminal["status"] != "PASS":
        sys.exit(3)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("A", "B", "C"), required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            read_only_preflight(args.phase)
            print("PREFLIGHT_PASS phase=" + args.phase + " effect=NONE")
        else:
            run_phase(args.phase)
    except Exception as exc:
        code = str(exc)
        if not re.fullmatch(r"[A-Z0-9_]{3,100}", code):
            code = "PRECONDITION_OR_RUNTIME_BLOCKED"
        print("BLOCKED_" + code, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
