#!/usr/bin/env python3
"""Deterministic TS EE OpenCode JSONL checker (candidate; no model execution).

This is evidence parsing ONLY. It does not verify independent provider billing,
actual permission enforcement, the model identity or the semantic review verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 10000
HASH = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,159}\Z")
SAFE_TOOLS = {"read", "glob", "grep"}


class InvalidEvidence(Exception):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise InvalidEvidence(reason)


def unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise InvalidEvidence("DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def target(root: Path, rel: str, prefix: str, must_exist: bool) -> Path:
    r = Path(rel)
    require(bool(r.parts) and not r.is_absolute()
            and ".." not in r.parts and "\\" not in rel,
            "UNSAFE_RELATIVE_PATH")
    require(r.parts[0] == prefix, "PATH_NOT_IN_ALLOWED_AREA")
    path = (root / r).resolve(strict=must_exist)
    require(path.is_relative_to(root), "PATH_ESCAPE")
    return path


def inspect(root: Path, original: str, digest: str, receipt: str,
            attempt: str, session: str, model: str, exit_claim: int) -> dict:
    root = root.resolve(strict=True)
    require(root.is_dir(), "ROOT_NOT_DIRECTORY")
    require(bool(HASH.fullmatch(digest)), "INVALID_SHA256")
    require(bool(ID.fullmatch(attempt)), "INVALID_ATTEMPT_ID")
    require(bool(ID.fullmatch(session)), "INVALID_SESSION_ID")
    require(model.startswith("opencode/") and "openai" not in model.lower(),
            "MODEL_NOT_EXPLICITLY_NON_OPENAI")
    require(exit_claim == 0, "PROVIDER_EXIT_NOT_ZERO")
    source = target(root, original, "results", True)
    dest = target(root, receipt, "receipts", False)
    require(source.is_file() and dest != source, "INVALID_SOURCE_OR_TARGET")
    require(dest.parent.is_dir() and not dest.exists(), "RECEIPT_NOT_CREATE_ONLY")
    before = source.stat()
    require(0 < before.st_size <= MAX_BYTES, "ORIGINAL_OUTSIDE_BOUNDS")
    raw = source.read_bytes()
    after = source.stat()
    require(before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns,
            "ORIGINAL_CHANGED_DURING_READ")
    require(raw.endswith(b"\n"), "JSONL_UNTERMINATED")
    require(hashlib.sha256(raw).hexdigest() == digest, "ORIGINAL_DIGEST_MISMATCH")
    lines = raw.split(b"\n")[:-1]
    require(0 < len(lines) <= MAX_EVENTS, "INVALID_EVENT_COUNT")

    types, tools, unsafe, costs = {}, {}, {}, []
    seen_sessions = set()
    text_count = 0
    last = ""
    for n, line in enumerate(lines, 1):
        require(bool(line), "EMPTY_EVENT")
        try:
            entry = json.loads(line.decode("utf-8"), object_pairs_hook=unique_keys)
        except (UnicodeError, ValueError) as exc:
            raise InvalidEvidence("BAD_EVENT_" + str(n)) from exc
        require(isinstance(entry, dict), "EVENT_NOT_OBJECT")
        kind, sid = entry.get("type"), entry.get("sessionID")
        require(isinstance(kind, str) and 0 < len(kind) <= 80,
                "INVALID_EVENT_TYPE")
        require(isinstance(sid, str) and bool(sid), "INVALID_EVENT_SESSION")
        seen_sessions.add(sid)
        types[kind] = types.get(kind, 0) + 1
        last = kind
        if kind == "step_finish":
            part = entry.get("part")
            require(isinstance(part, dict), "STEP_PART_INVALID")
            cost = part.get("cost")
            require(type(cost) in (int, float)
                    and 0 <= cost <= 1_000_000_000
                    and math.isfinite(float(cost)),
                    "STEP_COST_INVALID")
            costs.append(float(cost))
        elif kind == "tool_use":
            part = entry.get("part")
            require(isinstance(part, dict), "TOOL_PART_INVALID")
            tool = part.get("tool")
            require(isinstance(tool, str) and bool(tool), "TOOL_NAME_INVALID")
            tools[tool] = tools.get(tool, 0) + 1
            if tool not in SAFE_TOOLS:
                unsafe[tool] = unsafe.get(tool, 0) + 1
        elif kind == "text":
            text_count += 1

    require(seen_sessions == {session}, "SESSION_MISMATCH")
    require(bool(costs) and text_count > 0 and last == "step_finish",
            "INCOMPLETE_TERMINAL_SEQUENCE")
    return {
        "schema": "ts-ee-orca-jsonl-receipt-v2-candidate",
        "execution_attempt": attempt,
        "session_id": session,
        "original_path": original,
        "original_bytes": len(raw),
        "original_sha256": digest,
        "event_count": len(lines),
        "events_by_type": dict(sorted(types.items())),
        "tools_by_name": dict(sorted(tools.items())),
        "unexpected_tool_names": dict(sorted(unsafe.items())),
        "step_count": len(costs),
        "provider_reported_cost_total": round(math.fsum(costs), 10),
        "caller_claimed_provider_exit": exit_claim,
        "caller_claimed_model": model,
        "provider_billing_independently_verified": False,
        "model_identity_independently_verified": False,
        "semantic_review_verdict": "NOT_ASSESSED",
        "runtime_qualification": "NOT_QUALIFIED",
        "result": "UNSAFE_TOOL_REPORTED" if unsafe else "JSONL_STRUCTURALLY_VERIFIED",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    for arg in ("root", "original", "original-sha256", "receipt",
                "attempt", "session", "model"):
        p.add_argument("--" + arg, required=True)
    p.add_argument("--provider-exit-claim", type=int, required=True)
    a = p.parse_args()
    try:
        root = Path(a.root).resolve(strict=True)
        result = inspect(root, a.original, a.original_sha256, a.receipt,
                         a.attempt, a.session, a.model, a.provider_exit_claim)
        destination = target(root, a.receipt, "receipts", False)
        with destination.open("x", encoding="utf-8", newline="\n") as file:
            json.dump(result, file, sort_keys=True, indent=2)
            file.write("\n")
        print(json.dumps({"status": result["result"], "receipt": a.receipt,
                          "semantic_verdict": "NOT_ASSESSED"}, sort_keys=True))
    except (InvalidEvidence, OSError) as exc:
        print(json.dumps({"status": "BLOCKED_PRECONDITION", "reason": str(exc),
                          "model_calls_started_by_checker": 0}, sort_keys=True))
        raise SystemExit(42)


if __name__ == "__main__":
    main()
