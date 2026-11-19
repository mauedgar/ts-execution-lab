"""TS RS002 P0 SOURCE-ONLY provider custody gate.

Does not execute WSL/Orca/Commander, access secrets, or issue physical grants.
The supplied attestation objects are NOT authenticated by this module: a distinct,
reviewed provider-native readback binding is required before operational use.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Mapping, Protocol


class BlockedPrecondition(ValueError):
    """Fail closed; never interpret this as permission to dispatch/retry."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise BlockedPrecondition(label)


def digest(data: object) -> str:
    wire = json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(wire.encode("ascii")).hexdigest()


def is_native_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._:/-]{8,200}", value))


def is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


HOST = "DESKTOP-DJLBEQH"
DISTRO = "Ubuntu-24.04"
TERMINAL = "term_ad2e6b50-b30d-4e51-b32e-aa762e6a4b7e"
INCARNATION = "8541ed70-1732-4b31-b2b2-04957f984459"
ROOT_PATH = "/var/tmp/ts-rs002-a02-pg16-20261113-001"
SECRET_PATH = ROOT_PATH + "/secrets/observer.pass"
TARGET_PARENT = ROOT_PATH + "/secrets"
UID_OWNER = 1000
UID_OTHER = 65534
NATIVE_PROVIDER = "ORCA_NATIVE_TERMINAL"
ATTEMPT = "TS-RS002-P2-P0-HOST-DAC-20261119-001-A001"


@dataclass(frozen=True)
class Frozen:
    """Original immutable subject. No user-tunable command/path or host values."""
    attempt: str
    host: str
    distro: str
    terminal: str
    incarnation: str
    adapter_sha256: str
    request_ids: Mapping[str, str]


@dataclass(frozen=True)
class StatEntry:
    path: str
    kind: str
    uid: int
    mode: int
    inode: int
    device: int
    nlink: int
    is_symlink: bool


@dataclass(frozen=True)
class NativeReceipt:
    """Untrusted until independently retrieved from a QUALIFIED provider API."""
    stage: str
    request_id: str
    attempt: str
    provider: str
    provider_original_ref: str
    provider_original_sha256: str
    host: str
    distro: str
    terminal: str
    incarnation: str
    adapter_sha256: str
    argv: tuple[str, ...]
    argv_sha256: str
    native_windows_pid: int
    linux_pid: int
    linux_pid_namespace: str
    linux_uid: int
    native_completed: bool
    exit_code: int
    stdout: str
    metadata: tuple[StatEntry, ...] = ()


class OriginalNativeProvider(Protocol):
    """Requires an actual, separately reviewed Orca provider-native binding.

    A caller-constructed dictionary/JSON file is NOT such a binding. This
    protocol alone does not attest a concrete implementation or its authority.
    """
    def read_original(self, request_id: str) -> NativeReceipt: ...


def expected_argv(stage: str) -> tuple[str, ...]:
    if stage == "identity":
        return ("wsl.exe", "-d", DISTRO, "-u", "nobody", "--", "/usr/bin/id", "-u")
    if stage == "denial":
        return ("wsl.exe", "-d", DISTRO, "-u", "nobody", "--", "/usr/bin/test", "-r", SECRET_PATH)
    if stage == "metadata":
        # There is NO qualified, versioned metadata script/argv yet.
        # A synthetic receipt cannot invent one or become a real preflight.
        raise BlockedPrecondition("METADATA_NATIVE_ARGV_NOT_QUALIFIED")
    raise BlockedPrecondition("UNKNOWN_STAGE")


def validate_frozen(frozen: Frozen) -> None:
    require(frozen.attempt == ATTEMPT, "ATTEMPT_MISMATCH")
    require((frozen.host, frozen.distro, frozen.terminal, frozen.incarnation) ==
            (HOST, DISTRO, TERMINAL, INCARNATION), "HOST_TERMINAL_INCAR_MISMATCH")
    require(is_sha256(frozen.adapter_sha256), "ADAPTER_HASH_MISSING")
    require(set(frozen.request_ids) == {"metadata", "identity", "denial"}, "STAGES_NOT_EXACT")
    ids = list(frozen.request_ids.values())
    require(len(set(ids)) == 3 and all(is_native_id(x) for x in ids), "REQUEST_IDS_NOT_DISTINCT_NATIVE")


def validate_common(frozen: Frozen, r: NativeReceipt, stage: str) -> None:
    require(r.stage == stage and r.request_id == frozen.request_ids[stage], "WRONG_ORIGINAL_ID")
    require(r.attempt == frozen.attempt and r.provider == NATIVE_PROVIDER, "WRONG_ATTEMPT_OR_PROVIDER")
    require((r.host, r.distro, r.terminal, r.incarnation) ==
            (frozen.host, frozen.distro, frozen.terminal, frozen.incarnation), "NATIVE_HOST_IDENTITY_DRIFT")
    require(r.adapter_sha256 == frozen.adapter_sha256, "ADAPTER_SOURCE_CHANGED")
    require(is_native_id(r.provider_original_ref) and is_sha256(r.provider_original_sha256), "NATIVE_ORIGINAL_REF_MISSING")
    require(type(r.native_windows_pid) is int and r.native_windows_pid > 0, "WINDOWS_PID_MISSING")
    require(type(r.linux_pid) is int and r.linux_pid > 0, "LINUX_CHILD_PID_MISSING")
    require(is_native_id(r.linux_pid_namespace), "LINUX_PID_NAMESPACE_MISSING")
    require(type(r.linux_uid) is int, "LINUX_UID_MISSING")
    require(r.native_completed is True, "NATIVE_CHILD_NOT_COMPLETED")
    require(type(r.exit_code) is int, "NATIVE_EXIT_UNKNOWN")
    require(type(r.stdout) is str and len(r.stdout.encode("utf-8")) <= 256, "STDOUT_OVERSIZE")
    require(type(r.argv) is tuple and all(isinstance(v, str) for v in r.argv), "UNSTRUCTURED_ARGV")
    require(digest(list(r.argv)) == r.argv_sha256, "NATIVE_ARGV_HASH_MISMATCH")


def validate_meta(frozen: Frozen, r: NativeReceipt) -> None:
    validate_common(frozen, r, "metadata")
    require(r.linux_uid == UID_OWNER and r.exit_code == 0, "METADATA_NATIVE_PRINCIPAL_OR_EXIT")
    require(r.stdout == "", "METADATA_STDOUT_UNEXPECTED")
    require(r.argv == (), "UNQUALIFIED_METADATA_COMMAND_FROZEN")
    expected = [ROOT_PATH, TARGET_PARENT, SECRET_PATH]
    require([e.path for e in r.metadata] == expected, "METADATA_PATH_INVENTORY_MISMATCH")
    for i, e in enumerate(r.metadata):
        require(type(e.uid) is int and e.uid == UID_OWNER, "METADATA_OWNER_MISMATCH")
        require(not e.is_symlink and e.inode > 0 and e.device > 0, "METADATA_SYMLINK_OR_DEVICE")
        require(type(e.mode) is int and 0 <= e.mode <= 0o777, "METADATA_MODE_INVALID")
        if i < 2:
            require(e.kind == "directory" and e.mode == 0o700, "METADATA_PARENT_INSECURE")
        else:
            require(e.kind == "regular" and e.nlink == 1 and (e.mode & 0o077) == 0,
                    "METADATA_SECRET_ABSENT_OR_INSECURE")
    require(len(set((e.device, e.inode) for e in r.metadata)) == 3, "METADATA_INODE_ALIAS")


def validate_identity(frozen: Frozen, r: NativeReceipt) -> None:
    validate_common(frozen, r, "identity")
    require(r.argv == expected_argv("identity"), "IDENTITY_ARGV_NOT_FROZEN")
    require(r.linux_uid == UID_OTHER and r.exit_code == 0, "IDENTITY_UID_OR_EXIT")
    require(r.stdout in ("65534\n", "65534\r\n"), "IDENTITY_STDOUT_NOT_EXACT")
    require(not r.metadata, "UNEXPECTED_METADATA_IN_IDENTITY")


def validate_denial(frozen: Frozen, r: NativeReceipt) -> None:
    validate_common(frozen, r, "denial")
    require(r.argv == expected_argv("denial"), "DENIAL_ARGV_NOT_FROZEN")
    require(r.linux_uid == UID_OTHER, "DENIAL_UID_WRONG")
    require(r.exit_code == 1, "READABILITY_NOT_DENIED_OR_UNKNOWN")
    require(r.stdout == "" and not r.metadata, "DENIAL_OUTPUT_UNEXPECTED")


def evaluate_untrusted_originals(frozen: Frozen, receipts: Mapping[str, NativeReceipt]) -> str:
    """For adversarial source fixtures ONLY. Never confers provider authority."""
    validate_frozen(frozen)
    require(set(receipts) == {"metadata", "identity", "denial"}, "ORIGINAL_COUNT_NOT_EXACT")
    vals = [receipts[s] for s in ("metadata", "identity", "denial")]
    require(len({r.provider_original_ref for r in vals}) == 3, "NATIVE_REF_REUSED")
    require(len({r.native_windows_pid for r in vals}) == 3, "WINDOWS_PID_REUSED")
    require(len({(r.linux_pid_namespace, r.linux_pid) for r in vals}) == 3, "LINUX_PID_REUSED")
    validate_meta(frozen, receipts["metadata"])
    validate_identity(frozen, receipts["identity"])
    validate_denial(frozen, receipts["denial"])
    return "SOURCE_FIELDS_CONSISTENT_UNTRUSTED_NO_DISPATCH"


def qualify_provider_and_physical(frozen: Frozen, provider: OriginalNativeProvider) -> None:
    """Intentionally hard-blocked until native Orca provider readback is qualified.

    Do NOT invoke provider with an unqualified binding or use owner-writable
    JSON/local manifest to stand in for provider-native evidence.
    """
    validate_frozen(frozen)
    raise BlockedPrecondition("P0_NATIVE_PROVIDER_CUSTODY_NOT_QUALIFIED")
