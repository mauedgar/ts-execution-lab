#!/usr/bin/env python3
"""TS EE experimental POSIX/WSL JSONL checker, R006 SOURCE_ONLY.

No model, provider, network or runner invocation. This parser does NOT verify
native provider provenance, a USD bill, permission enforcement, semantic
conformance or Product acceptance. The receipt-directory trust model REQUIRES
exclusive ownership (0700) AND trusted, non-replaceable ancestry entries:
no untrusted UID may modify parent entries. A compromised same-UID process
or a hostile privileged process is OUTSIDE this source-only threat model.

The output names a SHA-256 digest and inode observed AT RETURN. It is not a
perpetual/immutable reference; downstream custody must bind the digest at a
separately trusted surface. On ambiguous publication effects, NEVER retry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
import uuid
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 10_000
MAX_EVENT_BYTES = 1024 * 1024
MAX_JSON_DEPTH = 128
SUPPORT_DIRFD = os.open in os.supports_dir_fd and os.link in os.supports_dir_fd
HASH = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,159}\Z")
COMPONENT = re.compile(r"[A-Za-z0-9_.-]{1,120}\Z")
PART_TYPES = {
    "step_start": "step-start", "step_finish": "step-finish",
    "text": "text", "tool_use": "tool",
}
SAFE_TOOLS = {"read", "glob", "grep"}


class Rejected(Exception):
    pass


def require(value: bool, reason: str) -> None:
    if not value:
        raise Rejected(reason)


def no_duplicates(items: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in items:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def invalid_constant(_value: str) -> None:
    raise Rejected("NONSTANDARD_JSON_CONSTANT")


def parse_event(line: bytes, index: int) -> dict:
    require(len(line) <= MAX_EVENT_BYTES, "EVENT_EXCEEDS_BYTE_LIMIT")
    # Count structural JSON nesting, ignoring quoted content and escapes.
    depth, quoted, escaped = 0, False, False
    for ch in line:
        if quoted:
            if escaped:
                escaped = False
            elif ch == 92:
                escaped = True
            elif ch == 34:
                quoted = False
        elif ch == 34:
            quoted = True
        elif ch in (91, 123):
            depth += 1
            require(depth <= MAX_JSON_DEPTH, "JSON_DEPTH_LIMIT")
        elif ch in (93, 125):
            depth -= 1
            require(depth >= 0, "JSON_UNBALANCED_BRACKETS")
    require(not quoted and depth == 0, "JSON_UNBALANCED_BRACKETS")
    try:
        item = json.loads(line.decode("utf-8"), object_pairs_hook=no_duplicates,
                          parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Rejected("MALFORMED_JSON_EVENT_" + str(index)) from exc
    require(isinstance(item, dict), "EVENT_NOT_OBJECT")
    return item


def validate_path(path: str, expected_prefix: str) -> list[str]:
    require(isinstance(path, str) and 0 < len(path) <= 512,
            "BAD_RELATIVE_PATH")
    require("\\" not in path and "\x00" not in path,
            "PATH_WITH_BACKSLASH_OR_NUL")
    parts = path.split("/")
    require(2 <= len(parts) <= 8 and parts[0] == expected_prefix,
            "PATH_OUTSIDE_ALLOWLIST")
    require(all(p not in {".", ".."} and COMPONENT.fullmatch(p)
                for p in parts), "PATH_UNSAFE_COMPONENT")
    return parts


def verify_trusted_ancestry_edge(parent_fd: int, child_fd: int) -> None:
    """Fail closed if an untrusted UID can modify this pathname edge.

    Owner UID and write permissions are checked for EVERY edge. Root-owned
    sticky directories (like /tmp) are allowed only for trusted-owned child
    entries. Same-UID processes and privileged actors remain out of scope.
    """
    parent = os.fstat(parent_fd)
    child = os.fstat(child_fd)
    trusted = {0, os.geteuid()}
    require(stat.S_ISDIR(parent.st_mode) and stat.S_ISDIR(child.st_mode),
            "ANCESTOR_NOT_DIRECTORY")
    require(parent.st_uid in trusted and child.st_uid in trusted,
            "UNTRUSTED_ANCESTOR_OWNER")
    untrusted_can_write = bool(stat.S_IMODE(parent.st_mode) & 0o022)
    sticky_protects_entry = bool(parent.st_mode & stat.S_ISVTX)
    require(not untrusted_can_write or sticky_protects_entry,
            "UNTRUSTED_MUTABLE_ANCESTOR")


def close_owned_fd(fd: int, effect_possible: bool = False) -> None:
    """Never downgrade an existing UNKNOWN when a descriptor close fails."""
    previous = sys.exc_info()[1]
    try:
        os.close(fd)
    except BaseException as exc:
        if isinstance(previous, Rejected) and str(previous).startswith("UNKNOWN_"):
            return
        if effect_possible:
            raise Rejected("UNKNOWN_PUBLISH_POSTCONDITION") from exc
        if previous is None:
            raise Rejected("BLOCKED_DESCRIPTOR_CLOSE_PRECONDITION") from exc
        # Preserve the original pre-effect failure rather than mask its cause.


def open_chain(base_fd: int, parents: list[str]) -> int:
    """Owned directory FD; each ancestry entry has an explicit trust proof."""
    fd = os.dup(base_fd)
    for name in parents:
        try:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY |
                            os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
        except BaseException:
            close_owned_fd(fd)
            raise
        try:
            verify_trusted_ancestry_edge(fd, child)
        except BaseException:
            try:
                close_owned_fd(child)
            finally:
                close_owned_fd(fd)
            raise
        try:
            close_owned_fd(fd)
        except BaseException:
            close_owned_fd(child)
            raise
        fd = child
    return fd


def open_root(root: Path) -> int:
    require(os.name == "posix" and SUPPORT_DIRFD and hasattr(os, "O_NOFOLLOW"),
            "POSIX_DIRFD_PLATFORM_REQUIRED")
    require(root.is_absolute(), "ROOT_NOT_ABSOLUTE")
    # Traverse from '/' so an ancestor symlink cannot silently replace root.
    names = [p for p in root.parts if p != "/"]
    start = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        return open_chain(start, names)
    finally:
        os.close(start)


def original_bytes(rootfd: int, relative: str, digest: str) -> bytes:
    parts = validate_path(relative, "results")
    folder = open_chain(rootfd, parts[:-1])
    try:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW |
                     os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=folder)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode), "SOURCE_NOT_REGULAR")
            require(0 < before.st_size <= MAX_BYTES, "BAD_ORIGINAL_SIZE")
            chunks, count = [], 0
            while True:
                chunk = os.read(fd, min(65536, MAX_BYTES + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                require(count <= MAX_BYTES, "ORIGINAL_TOO_LARGE")
                chunks.append(chunk)
            after = os.fstat(fd)
            values = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns,
                                s.st_ctime_ns)
            require(values(before) == values(after), "SOURCE_CHANGED_WHILE_READING")
            raw = b"".join(chunks)
            require(len(raw) == before.st_size, "SHORT_READ")
            require(hashlib.sha256(raw).hexdigest() == digest,
                    "ORIGINAL_DIGEST_MISMATCH")
            # A hard-linked alias or a same-UID writer remains out of scope;
            # caller-supplied digest is NOT independent custody attestation.
            return raw
        finally:
            os.close(fd)
    finally:
        os.close(folder)


def analyze(raw: bytes, attempt: str, session: str, original: str,
            model: str, exit_claim: int) -> dict:
    # Validate either uniform LF or CRLF without changing the source bytes,
    # its SHA-256, or the immutable original stored outside this checker.
    require(raw.endswith(b"\n"), "ORIGINAL_MISSING_LINE_TERMINATOR")
    source_line_ending = "CRLF" if raw.endswith(b"\r\n") else "LF"
    records = raw.split(b"\n")[:-1]
    require(0 < len(records) <= MAX_EVENTS, "BAD_EVENT_COUNT")
    if source_line_ending == "CRLF":
        require(all(row.endswith(b"\r") for row in records),
                "MIXED_LINE_ENDINGS")
        records = [row[:-1] for row in records]
    else:
        require(all(not row.endswith(b"\r") for row in records),
                "MIXED_LINE_ENDINGS")
    active = False
    started = ended = text_count = read_tools = other_tools = tool_errors = 0
    kinds: dict[str, int] = {}
    costs = []
    for index, data in enumerate(records, 1):
        require(bool(data), "EMPTY_EVENT")
        entry = parse_event(data, index)
        kind = entry.get("type")
        require(kind in PART_TYPES, "UNSUPPORTED_EVENT_KIND")
        require(entry.get("sessionID") == session, "SESSION_ID_MISMATCH")
        part = entry.get("part")
        require(isinstance(part, dict) and part.get("type") == PART_TYPES[kind],
                "PART_TYPE_INVALID")
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind == "step_start":
            require(not active, "SECOND_STEP_START")
            active, started = True, started + 1
        elif kind == "step_finish":
            require(active, "FINISH_WITHOUT_START")
            cost = part.get("cost")
            require(type(cost) in (int, float) and
                    0 <= cost <= 1_000_000_000 and math.isfinite(float(cost)),
                    "INVALID_REPORTED_COST")
            costs.append(float(cost))
            active, ended = False, ended + 1
        elif kind == "text":
            require(active and isinstance(part.get("text"), str),
                    "INVALID_TEXT_INSIDE_STEP")
            text_count += 1
        elif kind == "tool_use":
            require(active, "TOOL_OUTSIDE_STEP")
            tool = part.get("tool")
            require(isinstance(tool, str) and COMPONENT.fullmatch(tool),
                    "INVALID_TOOL_NAME")
            state = part.get("state")
            require(isinstance(state, dict) and
                    state.get("status") in {"completed", "error"},
                    "TOOL_STATE_NOT_TERMINAL")
            tool_errors += state.get("status") == "error"
            read_tools += tool in SAFE_TOOLS
            other_tools += tool not in SAFE_TOOLS
    require(not active and started == ended and started > 0 and text_count > 0
            and parse_event(records[-1], len(records)).get("type") == "step_finish",
            "TERMINAL_SEQUENCE_INCOMPLETE")
    return {
        "schema": "ts-ee-orca-jsonl-v6-posix-source-only",
        "execution_attempt": attempt,
        "session_id": session,
        "original_path": original,
        "original_byte_length": len(raw),
        "original_sha256": hashlib.sha256(raw).hexdigest(),
        "event_count": len(records),
        "source_line_ending": source_line_ending,
        "events_by_type": dict(sorted(kinds.items())),
        "step_start_count": started,
        "step_finish_count": ended,
        "text_event_count": text_count,
        "read_only_tool_events": read_tools,
        "other_tool_events": other_tools,
        "reported_tool_errors": tool_errors,
        "provider_reported_total_cost": round(math.fsum(costs), 10),
        "claimed_model": model,
        "claimed_exit_code": exit_claim,
        "provider_signature_verified": False,
        "independent_billing_verified": False,
        "native_terminal_verified": False,
        "semantic_review_verdict": "NOT_ASSESSED",
        "runtime_permission_enforcement_verified": False,
        "directory_trust_assumption": "exclusive_POSIX_uid_0700_same_uid_trusted",
        "result": "BOUNDED_JSONL_PARSED_UNVERIFIED_PROVIDER_SEMANTICS",
    }


def private_dir(fd: int) -> None:
    st = os.fstat(fd)
    require(stat.S_ISDIR(st.st_mode), "RECEIPT_NOT_DIRECTORY")
    require(st.st_uid == os.geteuid() and
            stat.S_IMODE(st.st_mode) == 0o700,
            "RECEIPT_DIRECTORY_NOT_EXCLUSIVE_0700")


def same_inode(a: os.stat_result, b: os.stat_result) -> bool:
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def publish(rootfd: int, receipt: str, result: dict) -> dict:
    parts = validate_path(receipt, "receipts")
    folder = open_chain(rootfd, parts[:-1])
    try:
        private_dir(folder)
        stage = ".stage-" + uuid.uuid4().hex
        final = parts[-1]
        payload = (json.dumps(result, sort_keys=True, indent=2,
                              allow_nan=False, ensure_ascii=True) + "\n").encode("utf-8")
        payload_digest = hashlib.sha256(payload).hexdigest()
        created_stage = False
        link_attempted = False
        # Never publish if final exists, but always use atomic os.link for the
        # authoritative collision check. An existing symlink also blocks.
        fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=folder)
        created_stage = True
        stage_identity = None
        try:
            with os.fdopen(fd, "wb", closefd=True) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
                stage_identity = os.fstat(stream.fileno())
            # Before os.link, switch permanently to uncertain-effect mode.
            # Even if os.link raises, it might have created final first.
            link_attempted = True
            os.link(stage, final, src_dir_fd=folder,
                    dst_dir_fd=folder, follow_symlinks=False)
            os.fsync(folder)
            checkfd = os.open(final, os.O_RDONLY | os.O_NOFOLLOW |
                              os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=folder)
            try:
                checkstat = os.fstat(checkfd)
                require(stat.S_ISREG(checkstat.st_mode) and
                        same_inode(checkstat, stage_identity),
                        "FINAL_INODE_MISMATCH")
                content = bytearray()
                while len(content) < len(payload) + 1:
                    chunk = os.read(checkfd, len(payload) + 1 - len(content))
                    if not chunk:
                        break
                    content.extend(chunk)
                require(bytes(content) == payload, "PUBLISHED_BYTES_MISMATCH")
            finally:
                os.close(checkfd)
            # Do not remove final on any error. Cleanup stage AFTER publication.
            os.unlink(stage, dir_fd=folder)
            created_stage = False
            os.fsync(folder)
            current = os.stat(final, dir_fd=folder, follow_symlinks=False)
            require(stat.S_ISREG(current.st_mode) and
                    same_inode(current, stage_identity), "FINAL_REPLACED_AFTER_READBACK")
            require(stat.S_IMODE(current.st_mode) == 0o600 and
                    current.st_uid == os.geteuid(),
                    "FINAL_FILE_NOT_PRIVATE")
            return {
                "status": "RECEIPT_PUBLISHED_AT_OBSERVATION",
                "receipt_sha256": payload_digest,
                "receipt_bytes": len(payload),
                "receipt_device": int(current.st_dev),
                "receipt_inode": int(current.st_ino),
                "trust_assumption": "same_uid_and_privileged_writers_trusted",
            }
        except BaseException as exc:
            if link_attempted:
                # Preserve stage + possible final. No retry, regardless of a
                # second fsync/unlink error or os.link error before its return.
                raise Rejected("UNKNOWN_PUBLISH_POSTCONDITION") from exc
            if created_stage:
                try:
                    os.unlink(stage, dir_fd=folder)
                except BaseException as cleanup_exc:
                    raise Rejected("UNKNOWN_STAGE_CLEANUP_POSTCONDITION") from cleanup_exc
            raise
    finally:
        # Directory close is also part of the publication postcondition.
        close_owned_fd(folder, effect_possible=bool(locals().get("link_attempted", False)))


def run(root: Path, original: str, digest: str, receipt: str,
        attempt: str, session: str, model: str, exit_claim: int) -> dict:
    require(bool(HASH.fullmatch(digest)), "INVALID_EXPECTED_DIGEST")
    require(bool(ID.fullmatch(attempt)) and bool(ID.fullmatch(session)),
            "INVALID_ATTEMPT_OR_SESSION")
    require(model == "opencode/deepseek-v4.1-flash-free",
            "MODEL_CLAIM_NOT_ALLOWED")
    require(exit_claim == 0, "NONZERO_EXIT_CLAIM")
    rootfd = open_root(root)
    publication_possible = False
    try:
        raw = original_bytes(rootfd, original, digest)
        summary = analyze(raw, attempt, session, original, model, exit_claim)
        # Conservative effect fence: a call to publish may make a durable entry.
        publication_possible = True
        outcome = publish(rootfd, receipt, summary)
        return {
            **outcome,
            "original_sha256": summary["original_sha256"],
            "original_event_count": summary["event_count"],
            "source_line_ending": summary["source_line_ending"],
            "semantic_verdict": "NOT_ASSESSED",
        }
    finally:
        close_owned_fd(rootfd, effect_possible=publication_possible)


def main() -> None:
    parser = argparse.ArgumentParser()
    for item in ("root", "original", "original-sha256", "receipt",
                 "attempt", "session", "model"):
        parser.add_argument("--" + item, required=True)
    parser.add_argument("--provider-exit-claim", type=int, required=True)
    args = parser.parse_args()
    try:
        response = run(Path(args.root), args.original, args.original_sha256,
                       args.receipt, args.attempt, args.session,
                       args.model, args.provider_exit_claim)
    except (Rejected, OSError, OverflowError, RecursionError) as exc:
        # A post-effect ambiguity is a terminal UNKNOWN. NEVER blindly retry.
        status = (str(exc) if isinstance(exc, Rejected) else type(exc).__name__)
        print(json.dumps({"status": status if status.startswith("UNKNOWN_")
                          else "BLOCKED_PRECONDITION",
                          "reason_code": status,
                          "model_calls_started": 0}, sort_keys=True))
        raise SystemExit(42)
    print(json.dumps(response, sort_keys=True))


if __name__ == "__main__":
    main()
