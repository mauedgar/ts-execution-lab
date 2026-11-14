#!/usr/bin/env python3
"""Fail-closed source-only OpenCode JSONL checker; POSIX/WSL candidate v3.

This does NOT validate provider signatures, actual bill, native exit receipt,
model routing, tool denial, semantic quality, or Product authority. No agent run.
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
MAX_EVENTS = 10000
HASH = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,159}\Z")
COMPONENT = re.compile(r"[A-Za-z0-9_.-]{1,120}\Z")
PART_TYPES = {"step_start": "step-start", "step_finish": "step-finish",
              "text": "text", "tool_use": "tool"}
READ_ONLY_TOOLS = {"read", "glob", "grep"}


class Rejected(Exception):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Rejected(reason)


def uniq(pairs: list[tuple[str, object]]) -> dict:
    d: dict = {}
    for k, v in pairs:
        need(k not in d, "DUPLICATE_JSON_KEY")
        d[k] = v
    return d


def bad_constant(_value: str):
    raise Rejected("NONSTANDARD_JSON_CONSTANT")


def parse_json(raw: bytes, context: str) -> dict:
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=uniq,
                         parse_constant=bad_constant)
    except (ValueError, UnicodeError) as exc:
        raise Rejected("MALFORMED_JSON_" + context) from exc
    need(isinstance(obj, dict), "JSON_NOT_OBJECT_" + context)
    return obj


def validate_parts(rel: str, prefix: str) -> list[str]:
    need(isinstance(rel, str) and len(rel) <= 512 and rel != "", "INVALID_PATH")
    need("\\" not in rel and "\x00" not in rel, "INVALID_PATH_SYNTAX")
    parts = rel.split("/")
    need(2 <= len(parts) <= 8 and parts[0] == prefix, "PATH_OUTSIDE_ALLOWLIST")
    need(all(p not in {".", ".."} and COMPONENT.fullmatch(p) for p in parts),
         "UNSAFE_PATH_COMPONENT")
    return parts


def open_directory_chain(root_fd: int, parents: list[str]) -> int:
    """Return new owned fd. Never follow symlinks or evaluate untrusted parents."""
    fd = os.dup(root_fd)
    try:
        for item in parents:
            nxt = os.open(item, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                          | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_original(root_fd: int, original: str, expected_sha256: str) -> bytes:
    parts = validate_parts(original, "results")
    folder = open_directory_chain(root_fd, parts[:-1])
    try:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                     | os.O_CLOEXEC, dir_fd=folder)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode), "SOURCE_NOT_REGULAR_FILE")
            need(0 < before.st_size <= MAX_BYTES, "ORIGINAL_SIZE_OUT_OF_BOUNDS")
            chunks, seen = [], 0
            while True:
                data = os.read(fd, min(65536, MAX_BYTES + 1 - seen))
                if not data:
                    break
                seen += len(data)
                need(seen <= MAX_BYTES, "ORIGINAL_TOO_LARGE")
                chunks.append(data)
            after = os.fstat(fd)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns) ==
                 (after.st_dev, after.st_ino, after.st_size,
                  after.st_mtime_ns, after.st_ctime_ns),
                 "ORIGINAL_CHANGED_DURING_READ")
            raw = b"".join(chunks)
            need(len(raw) == before.st_size, "ORIGINAL_SHORT_READ")
            need(hashlib.sha256(raw).hexdigest() == expected_sha256,
                 "ORIGINAL_SHA256_MISMATCH")
            return raw
        finally:
            os.close(fd)
    finally:
        os.close(folder)


def analyze(raw: bytes, attempt: str, session: str, model: str,
            exit_claim: int, original: str) -> dict:
    need(raw.endswith(b"\n") and not raw.endswith(b"\r\n"),
         "JSONL_NOT_LF_TERMINATED")
    lines = raw.split(b"\n")[:-1]
    need(0 < len(lines) <= MAX_EVENTS, "BAD_EVENT_COUNT")
    active, starts, finishes, texts = False, 0, 0, 0
    types: dict[str, int] = {}
    read_tool_calls, other_tool_calls, tool_errors = 0, 0, 0
    costs: list[float] = []
    for index, line in enumerate(lines, 1):
        need(bool(line), "EMPTY_EVENT")
        item = parse_json(line, "EVENT_" + str(index))
        kind = item.get("type")
        need(kind in PART_TYPES, "UNSUPPORTED_EVENT_KIND")
        need(item.get("sessionID") == session, "SESSION_MISMATCH")
        part = item.get("part")
        need(isinstance(part, dict) and part.get("type") == PART_TYPES[kind],
             "PART_TYPE_MISMATCH")
        types[kind] = types.get(kind, 0) + 1
        if kind == "step_start":
            need(not active, "DUPLICATE_STEP_START")
            active, starts = True, starts + 1
        elif kind == "step_finish":
            need(active, "FINISH_WITHOUT_START")
            cost = part.get("cost")
            need(type(cost) in (int, float) and 0 <= cost <= 1_000_000_000
                 and math.isfinite(float(cost)), "INVALID_REPORTED_COST")
            costs.append(float(cost))
            active, finishes = False, finishes + 1
        elif kind == "text":
            need(active, "TEXT_OUTSIDE_STEP")
            need(isinstance(part.get("text"), str), "INVALID_TEXT_PART")
            texts += 1
        elif kind == "tool_use":
            need(active, "TOOL_OUTSIDE_STEP")
            tool = part.get("tool")
            need(isinstance(tool, str) and COMPONENT.fullmatch(tool),
                 "INVALID_TOOL_NAME")
            state = part.get("state")
            need(isinstance(state, dict) and state.get("status") in
                 {"completed", "error"}, "TOOL_STATUS_NOT_TERMINAL")
            tool_errors += state.get("status") == "error"
            if tool in READ_ONLY_TOOLS:
                read_tool_calls += 1
            else:
                other_tool_calls += 1
    need(not active and starts == finishes and starts > 0 and texts > 0
         and lines and parse_json(lines[-1], "FINAL").get("type") == "step_finish",
         "INCOMPLETE_OR_UNBALANCED_TERMINAL")
    return {
        "schema": "ts-ee-orca-jsonl-parsed-v3-posix-candidate",
        "execution_attempt": attempt,
        "session_id": session,
        "original_path": original,
        "original_byte_length": len(raw),
        "original_sha256": hashlib.sha256(raw).hexdigest(),
        "event_count": len(lines),
        "event_types": dict(sorted(types.items())),
        "step_start_count": starts,
        "step_finish_count": finishes,
        "text_event_count": texts,
        "read_only_tool_events": read_tool_calls,
        "other_tool_events": other_tool_calls,
        "reported_tool_errors": tool_errors,
        "provider_reported_total_cost": round(math.fsum(costs), 10),
        "claimed_model_id": model,
        "claimed_native_exit_code": exit_claim,
        "semantic_review_verdict": "NOT_ASSESSED",
        "native_terminal_verified": False,
        "provider_model_verified_independently": False,
        "provider_billing_verified_independently": False,
        "runtime_permission_enforcement_verified": False,
        "original_digest_precommit_verified_independently": False,
        "result": "BOUNDED_JSONL_PARSED_UNVERIFIED_PROVIDER_SEMANTICS",
    }


def publish_receipt(root_fd: int, relative_receipt: str, result: dict) -> None:
    parts = validate_parts(relative_receipt, "receipts")
    folder = open_directory_chain(root_fd, parts[:-1])
    stage = ".stage-" + uuid.uuid4().hex
    final = parts[-1]
    linked = False
    created_stage = False
    try:
        try:
            fd = os.open(final, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=folder)
        except FileNotFoundError:
            pass
        else:
            os.close(fd)
            raise Rejected("RECEIPT_ALREADY_EXISTS")
        payload = (json.dumps(result, sort_keys=True, indent=2,
                              ensure_ascii=True, allow_nan=False) + "\n").encode()
        fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=folder)
        created_stage = True
        try:
            with os.fdopen(fd, "wb", closefd=True) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            raise
        # POSIX hard-link publication is atomic and create-only (EEXIST on collision).
        os.link(stage, final, src_dir_fd=folder, dst_dir_fd=folder,
                follow_symlinks=False)
        linked = True
        os.fsync(folder)
        checkfd = os.open(final, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                          dir_fd=folder)
        try:
            st = os.fstat(checkfd)
            need(stat.S_ISREG(st.st_mode), "PUBLISHED_NOT_REGULAR")
            actual = b""
            while len(actual) < len(payload) + 1:
                chunk = os.read(checkfd, len(payload) + 1 - len(actual))
                if not chunk:
                    break
                actual += chunk
            need(actual == payload, "PUBLISHED_RECEIPT_MISMATCH")
        finally:
            os.close(checkfd)
        os.unlink(stage, dir_fd=folder)
        created_stage = False
        os.fsync(folder)
    except BaseException:
        if created_stage and not linked:
            os.unlink(stage, dir_fd=folder)
        if linked:
            # Final effect may be present; never retry until exact reconciliation.
            raise Rejected("UNKNOWN_PUBLISH_POSTCONDITION")
        raise
    finally:
        os.close(folder)


def run(root: Path, original: str, digest: str, receipt: str,
        attempt: str, session: str, model: str, exit_claim: int) -> dict:
    need(os.name == "posix" and os.open in os.supports_dir_fd
         and os.link in os.supports_dir_fd, "POSIX_DIRFD_PLATFORM_REQUIRED")
    need(root.is_absolute(), "ROOT_NOT_ABSOLUTE")
    need(bool(HASH.fullmatch(digest)), "INVALID_EXPECTED_DIGEST")
    need(bool(ID.fullmatch(attempt)) and bool(ID.fullmatch(session)),
         "INVALID_ATTEMPT_OR_SESSION_ID")
    need(model == "opencode/deepseek-v4.1-flash-free", "UNQUALIFIED_MODEL_CLAIM")
    need(exit_claim == 0, "NATIVE_EXIT_CLAIM_NONZERO")
    rootfd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                     | os.O_CLOEXEC)
    try:
        raw = read_original(rootfd, original, digest)
        result = analyze(raw, attempt, session, model, exit_claim, original)
        publish_receipt(rootfd, receipt, result)
        return {"status": result["result"], "receipt_path": receipt,
                "event_count": result["event_count"],
                "semantic_verdict": "NOT_ASSESSED"}
    finally:
        os.close(rootfd)


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("root", "original", "original-sha256", "receipt",
                 "attempt", "session", "model"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--provider-exit-claim", type=int, required=True)
    a = p.parse_args()
    try:
        result = run(Path(a.root), a.original, a.original_sha256,
                     a.receipt, a.attempt, a.session, a.model,
                     a.provider_exit_claim)
    except (Rejected, OSError, OverflowError) as exc:
        print(json.dumps({"status": "BLOCKED_PRECONDITION",
                          "reason_code": exc.args[0] if isinstance(exc, Rejected)
                          else type(exc).__name__,
                          "model_calls_started": 0}, sort_keys=True))
        raise SystemExit(42)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
