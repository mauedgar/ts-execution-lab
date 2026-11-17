#!/usr/bin/env python3
"""TS Remote State 002: one-time nonProduct C001 PostgreSQL catalog observer.

Only changes the execution surface for previously frozen read-only SQL.
No dynamic SQL, arbitrary shell, privilege escalation, new database or Product writes.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import stat
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

OWNER = "TS_REMOTE_STATE_002"
RUNNER_ID = "TS-RS002-P1-C001-STRUCTURED-20261117-002"
HOST = "DESKTOP-DJLBEQH"
DAEMON = "1219e4b8-5972-4880-8ebd-4fd2498a3e83"
CID = "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88"
NETWORK = "6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35"
VOLUME = "e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899"
ORIGINAL_RECEIPT = Path("/var/tmp/ts-rs002-a02-pg16-recovery-20261115-001/attempt-status.txt")
ORIGINAL_RECEIPT_SHA256 = "c66f4359dededc7221f13564178aa0749310f9d31d4dcc0541f65b35f529bd06"
RESULTS = Path("/home/tsops/ts-remote-state-002/p1-c001-structured-20261117-002")
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

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def json_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_read(path: Path, *, private: bool = False) -> bytes:
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_nlink != 1:
        fail("UNTRUSTED_RECEIPT_FILE")
    if st.st_mode & (0o077 if private else 0o022):
        fail("UNSAFE_RECEIPT_MODE")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st2 = os.fstat(fd)
        if (st2.st_ino, st2.st_dev) != (st.st_ino, st.st_dev):
            fail("FILE_RACE_REJECTED")
        data = os.read(fd, 16000)
        if len(data) == 16000:
            fail("RECEIPT_SIZE_EXCEEDED")
        return data
    finally:
        os.close(fd)

def admission() -> tuple[str, str]:
    # Trust root: external qualified UTF-8 materializer must independently
    # verify BOTH file digests against the pinned reviewed Git object.
    path = Path(__file__).resolve().with_name("admission.json")
    data = safe_read(path)
    manifest = json.loads(data)
    expected = {
        "runner_id": RUNNER_ID,
        "source_git_commit": manifest.get("source_git_commit"),
        "source_git_blob": manifest.get("source_git_blob"),
        "runner_sha256": json_sha256(Path(__file__).read_bytes()),
        "sql_source_git_blob": SQL_SOURCE_BLOB,
        "container_id": CID,
        "review_verdict": "RECOMMEND",
        "review_original_blob": manifest.get("review_original_blob"),
        "allowed_phases": ["A", "B", "C"],
        "protocol": "TS-RS002-P1-C001-STRUCTURED-v2",
    }
    if manifest != expected:
        fail("UNADMITTED_SOURCE_OR_ARTIFACT_HASH")
    if not re.fullmatch(r"[0-9a-f]{40}", manifest["source_git_commit"]):
        fail("UNVERIFIED_SOURCE_COMMIT")
    if not re.fullmatch(r"[0-9a-f]{40}", manifest["source_git_blob"]):
        fail("UNVERIFIED_SOURCE_BLOB")
    if not re.fullmatch(r"[0-9a-f]{40}", manifest["review_original_blob"]):
        fail("UNVERIFIED_INDEPENDENT_REVIEW")
    return json_sha256(data), manifest["runner_sha256"]

def ensure_private_directory(path: Path) -> None:
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        fail("UNTRUSTED_PHASE_DIRECTORY")

def read_prior(phase: str, admission_hash: str, runner_hash: str) -> str:
    earlier = "A" if phase == "B" else "B"
    folder = RESULTS / earlier
    ensure_private_directory(folder)
    intent_data = safe_read(folder / "intent.json", private=True)
    terminal_data = safe_read(folder / "terminal.json", private=True)
    intent = json.loads(intent_data)
    result = json.loads(terminal_data)
    if earlier == "A" and intent.get("previous_terminal_sha256") != "GENESIS":
        fail("PRIOR_GENESIS_CHAIN_INVALID")
    if earlier == "B" and intent.get("previous_terminal_sha256") != read_prior("B", admission_hash, runner_hash):
        fail("PRIOR_CHAIN_ROOT_MISMATCH")
    if intent != {
        "runner_id": RUNNER_ID, "phase": earlier, "container_id": CID,
        "sql_sha256": json_sha256(SQL[earlier].encode("utf-8")),
        "runner_sha256": runner_hash, "admission_sha256": admission_hash,
        "original_r001_sha256": ORIGINAL_RECEIPT_SHA256,
        "previous_terminal_sha256": intent.get("previous_terminal_sha256"),
        "start_utc": intent.get("start_utc"), "host_pid": intent.get("host_pid"),
        "Product_effect": "NONE", "effect": "PENDING_READONLY",
    }:
        fail("PRIOR_INTENT_IDENTITY_INVALID")
    if (result.get("status") != "PASS" or result.get("runner_id") != RUNNER_ID or
        result.get("phase") != earlier or result.get("container_id") != CID or
        result.get("sql_sha256") != intent["sql_sha256"] or
        result.get("admission_sha256") != admission_hash or
        result.get("runner_sha256") != runner_hash or
        result.get("intent_sha256") != json_sha256(intent_data) or
        result.get("previous_terminal_sha256") != intent["previous_terminal_sha256"] or
        result.get("exit_code") != 0 or
        tuple(result.get("stdout", ())) != EXPECTED[earlier] or
        result.get("database_mutation") != "NONE_READ_ONLY"):
        fail("PRIOR_TERMINAL_NOT_AUTHENTICATED")
    return json_sha256(terminal_data)

def read_only_preflight(phase: str) -> tuple[str, str, str]:
    if os.uname().nodename.upper() != HOST or os.getuid() != 1000:
        fail("WRONG_HOST_OR_UID")
    if sys.version_info[:3] != (3, 15, 2):
        fail("WRONG_PYTHON_RUNTIME")
    admission_hash, runner_hash = admission()
    if hashlib.sha256(ORIGINAL_RECEIPT.read_bytes()).hexdigest() != ORIGINAL_RECEIPT_SHA256:
        fail("ORIGINAL_R001_RECEIPT_MISMATCH")
    if subprocess_output([DOCKER, "info", "--format", "{{.ID}}"]) != DAEMON:
        fail("DOCKER_DAEMON_MISMATCH")
    doc = json.loads(subprocess_output([DOCKER, "container", "inspect", CID]))
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
    # Configured immutable digest must agree with effective image ID.
    if c["Image"] != subprocess_output([DOCKER, "image", "inspect", "--format", "{{.Id}}", c["Config"]["Image"]]):
        fail("EFFECTIVE_IMAGE_ID_MISMATCH")
    for m in c["Mounts"]:
        if m["Type"] == "bind" and m["RW"] is not False:
            fail("MUTABLE_EXTERNAL_BIND")
    if RESULTS.exists():
        ensure_private_directory(RESULTS)
    if (RESULTS / phase).exists() or (RESULTS / phase).is_symlink():
        fail("PHASE_ATTEMPT_ALREADY_EXISTS_NO_RETRY")
    prior = "GENESIS"
    if phase != "A":
        prior = read_prior(phase, admission_hash, runner_hash)
    return prior, admission_hash, runner_hash

def write_exclusive(path: Path, record: dict) -> bytes:
    data = (json.dumps(record, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    # Durable create-only directory entry, not merely a flushed file body.
    dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)
    return data

def run_phase(phase: str) -> None:
    prior, admission_hash, runner_hash = read_only_preflight(phase)
    if not RESULTS.exists():
        RESULTS.mkdir(mode=0o700)
    ensure_private_directory(RESULTS)
    dest = RESULTS / phase
    dest.mkdir(mode=0o700)
    ensure_private_directory(dest)
    sql_hash = json_sha256(SQL[phase].encode("utf-8"))
    intent_data = write_exclusive(dest / "intent.json", {
        "runner_id": RUNNER_ID, "phase": phase, "container_id": CID,
        "sql_sha256": sql_hash, "runner_sha256": runner_hash,
        "admission_sha256": admission_hash,
        "original_r001_sha256": ORIGINAL_RECEIPT_SHA256,
        "previous_terminal_sha256": prior, "start_utc": utc_now(),
        "host_pid": os.getpid(), "Product_effect": "NONE",
        "effect": "PENDING_READONLY"
    })
    cmd = [DOCKER, "exec", "--user", "postgres", CID, "psql",
           "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-U", USER, "-d", DB, "-c", SQL[phase]]
    start = utc_now()
    status = "NOT_DISPATCHED"
    code = "PRESPAWN_UNKNOWN"
    child_pid = None
    exit_code = None
    stdout = ()
    try:
        # Exactly one native read-only invocation. Do not use shell, retries,
        # alternate drivers, detached subprocesses or dynamic SQL.
        child = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                 errors="replace")
        child_pid = child.pid
        status = "UNKNOWN"
        write_exclusive(dest / "running.json", {
            "runner_id": RUNNER_ID, "phase": phase, "pid": child_pid,
            "status": "RUNNING", "start_utc": start,
            "intent_sha256": json_sha256(intent_data)
        })
        out, _ = child.communicate(timeout=30)
        exit_code = child.returncode
        if exit_code != 0:
            status, code = "FAILED", "PSQL_NONZERO_EXIT"
        else:
            try:
                check_result(phase, out)
                stdout = normalize(out)
                status, code = "PASS", "OK"
            except RuntimeError:
                status, code = "FAILED", "READONLY_CATALOG_MISMATCH_" + phase
    except subprocess.TimeoutExpired:
        # Original Docker/psql child may remain running; never kill or retry.
        status, code = "UNKNOWN", "NATIVE_PROCESS_TIMEOUT_UNRECONCILED"
    except Exception:
        # If a child was spawned, evidence is UNKNOWN. Before Popen => NONE.
        status, code = ("UNKNOWN" if child_pid is not None else "NOT_DISPATCHED"), "NATIVE_EXECUTION_EXCEPTION"
    terminal = {
        "runner_id": RUNNER_ID, "phase": phase, "status": status, "code": code,
        "sql_sha256": sql_hash, "runner_sha256": runner_hash,
        "admission_sha256": admission_hash, "container_id": CID,
        "intent_sha256": json_sha256(intent_data),
        "previous_terminal_sha256": prior, "child_pid": child_pid,
        "exit_code": exit_code, "start_utc": start,
        "end_utc": utc_now(), "stdout": stdout,
        "Product_effect": "NONE",
        "database_mutation": "NONE_READ_ONLY" if status == "PASS" else "NOT_PROVEN",
        "no_retry": True
    }
    write_exclusive(dest / "terminal.json", terminal)
    print(json.dumps(terminal, sort_keys=True))
    if status != "PASS":
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
