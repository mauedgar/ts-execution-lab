"""Isolated read-only Orca CLI *source candidate* for RS002 P0.

This probe cannot qualify physical WSL evidence. It never sends terminal input,
creates terminals, runs WSL, reads secrets, or grants any Product effect.
A live native Orca provider/binary binding is required before deploying this code.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence
from uuid import UUID

SOURCE_ONLY = "ORCA_STATUS_READONLY_SOURCE_OBSERVATION_NOT_NATIVE_P0"
MAX_STDOUT = 131072
MAX_STDERR = 4096
MAX_EXE_BYTES = 300 * 1024 * 1024


class BlockedPrecondition(Exception):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise BlockedPrecondition(code)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value.lower()
    except (ValueError, AttributeError):
        return False


@dataclass(frozen=True)
class Frozen:
    attempt: str
    subject_commit: str
    expected_exe_sha256: str
    exe_path: str
    expected_terminal: str
    expected_execution_host_id: str


def validate_frozen(f: Frozen) -> None:
    require(bool(re.fullmatch(r"TS-RS002-P0-ORCA-P00-[A-Z0-9-]{6,100}-A[0-9]{3}", f.attempt)), "ATTEMPT_NOT_FROZEN")
    for h in (f.subject_commit, f.expected_exe_sha256):
        require(bool(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", h)), "HASH_MALFORMED")
    require(len(f.subject_commit) == 40 and len(f.expected_exe_sha256) == 64, "HASH_LENGTH_WRONG")
    require(bool(re.fullmatch(r"term_[A-Za-z0-9_-]{8,120}", f.expected_terminal)), "TERMINAL_HANDLE_INVALID")
    require(bool(re.fullmatch(r"[A-Za-z0-9._:-]{8,128}", f.expected_execution_host_id)), "EXECUTION_HOST_ID_INVALID")
    path = Path(f.exe_path)
    require(path.is_absolute(), "CLI_PATH_NOT_ABSOLUTE")
    require(path.suffix.lower() == ".exe", "WINDOWS_ORCA_EXECUTABLE_REQUIRED_NOT_CMD")


def check_exe(f: Frozen) -> None:
    """Fail-closed file identity check. Symlinks, stale binaries and giant files deny.

    Not a code-signature or provider authentication check. No Windows signer
    evaluation is available on non-Windows fixtures.
    """
    path = Path(f.exe_path)
    require(not path.is_symlink() and path.is_file(), "CLI_MISSING_OR_SYMLINK")
    st_before = path.stat()
    require(0 < st_before.st_size <= MAX_EXE_BYTES, "CLI_SIZE_INVALID")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while part := stream.read(1024 * 1024):
            h.update(part)
    st_after = path.stat()
    require((st_before.st_dev, st_before.st_ino, st_before.st_size, st_before.st_mtime_ns) ==
            (st_after.st_dev, st_after.st_ino, st_after.st_size, st_after.st_mtime_ns), "CLI_CHANGED_DURING_HASH")
    require(h.hexdigest() == f.expected_exe_sha256, "CLI_HASH_MISMATCH")


def _unwrap(raw: bytes, expected: str) -> dict:
    require(0 < len(raw) <= MAX_STDOUT, "CLI_STDOUT_EMPTY_OR_TOO_LARGE")
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, UnicodeError) as err:
        raise BlockedPrecondition("CLI_NONJSON_OR_WRAPPER_SILENCE") from err
    require(type(obj) is dict and obj.get("ok") is True, f"{expected}_CLI_NOT_OK")
    require(type(obj.get("result")) is dict, f"{expected}_RESULT_MISSING")
    return obj


def _runtime(obj: dict) -> str:
    r = obj["result"]
    runtime = r.get("runtime")
    require(type(runtime) is dict, "STATUS_RUNTIME_MISSING")
    require(runtime.get("reachable") is True and runtime.get("state") == "ready", "ORCA_RUNTIME_NOT_READY")
    require(type(r.get("app")) is dict and r["app"].get("running") is True, "ORCA_APP_NOT_RUNNING")
    runtime_id = runtime.get("runtimeId")
    require(_uuid(runtime_id), "ORCA_RUNTIME_ID_MISSING")
    require(type(obj.get("_meta")) is dict and obj["_meta"].get("runtimeId") == runtime_id,
            "STATUS_PROVIDER_META_RUNTIME_MISMATCH")
    return runtime_id


def _terminal_list(obj: dict, runtime_id: str, f: Frozen) -> dict:
    require(type(obj.get("_meta")) is dict and obj["_meta"].get("runtimeId") == runtime_id,
            "LIST_RUNTIME_DRIFT")
    r = obj["result"]
    scope = r.get("hostScope")
    require(type(scope) is dict, "HOST_SCOPE_UNVERIFIABLE")
    hosts = scope.get("hostIds")
    omitted = scope.get("omittedHostIds")
    # The exact field names are a narrow source hypothesis. Requalify on real
    # provider output; do NOT assume missing fields mean empty/complete scope.
    require(type(hosts) is list and all(isinstance(x, str) for x in hosts), "HOST_SCOPE_COVERED_NOT_EXPLICIT")
    require(type(omitted) is list and all(isinstance(x, str) for x in omitted), "HOST_SCOPE_OMITTED_NOT_EXPLICIT")
    require(f.expected_execution_host_id in hosts and f.expected_execution_host_id not in omitted,
            "TARGET_HOST_NOT_NATIVE_COVERED")
    terminals = r.get("terminals")
    require(type(terminals) is list and len(terminals) <= 500, "TERMINALS_INVALID_OR_TRUNCATED")
    matches = [x for x in terminals if type(x) is dict and x.get("handle") == f.expected_terminal]
    require(len(matches) == 1, "TARGET_TERMINAL_MISSING_OR_DUPLICATED")
    terminal = matches[0]
    require(terminal.get("executionHostId") == f.expected_execution_host_id, "TERMINAL_HOST_MISMATCH")
    require(terminal.get("connected") is True and terminal.get("orphaned") is False,
            "TERMINAL_ORPHANED_OR_NOT_CONNECTED")
    return terminal


Runner = Callable[..., subprocess.CompletedProcess]


def inspect_readonly(f: Frozen, runner: Runner = subprocess.run) -> dict:
    """Live-status *candidate*, not physical qualification or permission to dispatch.

    Requires external Orca-owned terminal/native provenance for competence. This
    process only queries status/list/status; it has no send/create/wait/WSL path.
    """
    validate_frozen(f)
    check_exe(f)
    env = os.environ.copy()
    # Windows vendor workaround is not automatically activated. Explicit
    # executable hash + normal direct invocation must be separately qualified.
    argv_commands: tuple[tuple[str, ...], ...] = (
        (f.exe_path, "status", "--json"),
        (f.exe_path, "terminal", "list", "--json"),
        (f.exe_path, "status", "--json"),
    )
    observations: list[dict] = []
    for seq, argv in enumerate(argv_commands):
        try:
            p = runner(list(argv), input=None, capture_output=True, timeout=8, check=False, shell=False, env=env)
        except (subprocess.TimeoutExpired, OSError) as err:
            raise BlockedPrecondition("NATIVE_CLI_QUERY_UNVERIFIABLE_NO_RETRY") from err
        require(type(p.returncode) is int and p.returncode == 0, "NATIVE_CLI_EXIT_NONZERO")
        require(isinstance(p.stdout, bytes) and isinstance(p.stderr, bytes), "NATIVE_CLI_NOT_BYTE_STREAMS")
        require(len(p.stderr) <= MAX_STDERR, "CLI_STDERR_OVERSIZE")
        name = "status" if seq != 1 else "list"
        parsed = _unwrap(p.stdout, name.upper())
        observations.append({"parsed": parsed, "sha256_raw": _sha(p.stdout), "argv": list(argv)})
    first, listing, last = observations
    runtime_a = _runtime(first["parsed"])
    runtime_b = _runtime(last["parsed"])
    require(runtime_a == runtime_b, "ORCA_RUNTIME_RESTARTED_DURING_OBSERVATION")
    terminal = _terminal_list(listing["parsed"], runtime_a, f)
    # This string is NEVER a physical permit. The caller must preserve provider
    # ORIGINAL responses separately and qualify transport/caller identity.
    return {
        "classification": SOURCE_ONLY,
        "attempt": f.attempt,
        "source_commit": f.subject_commit,
        "terminal": f.expected_terminal,
        "execution_host_id": f.expected_execution_host_id,
        "runtime_id": runtime_a,
        "terminal_connected": terminal["connected"],
        "original_stdout_sha256": [x["sha256_raw"] for x in observations],
        "physical_p0_dispatch": "NOT_DISPATCHED",
        "physical_p2_dispatch": "NOT_DISPATCHED",
        "linux_pid": "NOT_ATTESTED",
        "linux_uid": "NOT_ATTESTED",
        "linux_exit": "NOT_ATTESTED",
        "product_effect": "NONE",
    }


def physical_admission(*_args: object, **_kwargs: object) -> None:
    raise BlockedPrecondition("ORCA_WSL_CHILD_PID_UID_EXIT_PROVIDER_CUSTODY_NOT_QUALIFIED")


if __name__ == "__main__":
    print("BLOCKED_SOURCE_ONLY_CANDIDATE_NOT_DEPLOYED", file=sys.stderr)
    raise SystemExit(3)
