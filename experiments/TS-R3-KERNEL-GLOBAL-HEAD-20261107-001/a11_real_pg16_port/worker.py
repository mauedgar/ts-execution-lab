"""A11 NONPRODUCT disposable PG16 adapter worker; local test only.

One JSON request over stdin, one JSON response over stdout. No secret values,
Neon credentials, Product writes, external authorities or lifecycle transitions.
All SQL effects come from the existing byte-preserving verified bridge.
"""
from __future__ import annotations

import base64
from hashlib import sha256
import json
import os
import re
import sys
from pathlib import Path

# Exact sibling ts_global package; no ambient PYTHONPATH or host imports.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg
from psycopg.rows import dict_row

from ts_global.bridge import (
    EffectUnknown, Mutation, StorageRejected, apply, initialize, read, reconcile,
)

SCOPE = "A10-DISPOSABLE-SINGLE-SCOPE"
URI = ("postgresql://tsr3_a11_synthetic:a11_disposable_only"
       "@127.0.0.1:5432/tsr3_a11_synthetic?sslmode=disable")
ROOT = Path(__file__).resolve().parent.parent
AUTH = sha256(b"A11_SYNTHETIC_DISPOSABLE_AUTHORITY_NOT_PRODUCT").hexdigest()
SHA = re.compile(r"[0-9a-f]{64}\Z")


def require(ok: bool, code: str = "INVALID_REQUEST") -> None:
    if not ok:
        raise ValueError(code)


def b64(value: str) -> bytes:
    require(type(value) is str, "INVALID_BASE64")
    return base64.b64decode(value, validate=True)


def read_request() -> dict:
    raw = sys.stdin.buffer.read(6 * 1024 * 1024 + 1)
    require(len(raw) <= 6 * 1024 * 1024, "OVERSIZED_MESSAGE")
    message = json.loads(raw.decode("utf-8", "strict"))
    require(type(message) is dict, "INVALID_MESSAGE")
    require(message.get("scope") == SCOPE, "WRONG_SYNTHETIC_SCOPE")
    require(message.get("op") in ("init", "read", "apply", "reconcile", "counts"),
            "INVALID_OPERATION")
    return message


def connect():
    require(os.getenv("TS_R3_NEON_CHILD_DSN") is None, "NEON_SECRET_FORBIDDEN")
    require(os.getenv("DATABASE_URL") is None, "PRODUCTION_DB_URL_FORBIDDEN")
    require(os.getenv("PGPASSWORD") is None, "DB_PASSWORD_ENV_FORBIDDEN")
    require(os.getenv("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI, "LOCAL_DB_ID_MISMATCH")
    require(psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary",
            "PINNED_PSYCOPG_REQUIRED")
    conn = psycopg.connect(
        URI, autocommit=True, row_factory=dict_row,
        connect_timeout=5, application_name="ts-r3-a11-disposable-only",
    )
    require(conn.execute("SHOW server_version").fetchone()["server_version"].startswith("16."),
            "POSTGRES16_REQUIRED")
    ident = conn.execute(
        "SELECT current_database() AS db, current_user AS role, "
        "inet_server_port() AS backend_port"
    ).fetchone()
    require(ident["db"] == "tsr3_a11_synthetic" and
            ident["role"] == "tsr3_a11_synthetic" and
            type(ident["backend_port"]) is int,
            "LOCAL_DISPOSABLE_ROLE_DB_MISMATCH")
    return conn


def parse_proposal(p: dict) -> tuple[Mutation, dict]:
    require(type(p) is dict and p.get("scope") == SCOPE, "INVALID_SCOPE")
    require(type(p.get("mutationId")) is str and
            re.fullmatch(r"A10-[A-Z0-9-]+", p["mutationId"]) is not None,
            "INVALID_MUTATION_ID")
    expected = p.get("expectedRevision")
    epoch = p.get("expectedEpoch")
    require(type(expected) is int and 0 <= expected <= (1 << 53) - 1,
            "INVALID_REVISION")
    require(type(epoch) is int and epoch == 1, "LOCAL_EPOCH_ONLY")
    previous = p.get("previousEventHash")
    require(previous is None or (type(previous) is str and SHA.fullmatch(previous)),
            "INVALID_PREVIOUS_HASH")
    event_hash = p.get("eventHash")
    require(type(event_hash) is str and SHA.fullmatch(event_hash), "INVALID_EVENT_HASH")
    state = b64(p.get("stateBytes"))
    line = b64(p.get("eventLine"))
    require(line.endswith(b'"}\n') and len(line) <= 4 * 1024 * 1024,
            "INVALID_EVENT_LINE")
    # JS Product always appends hash as the final event key.
    marker = b',"hash":"'
    head, sep, tail = line[:-1].rpartition(marker)
    require(bool(sep) and tail == event_hash.encode("ascii") + b'"}',
            "INVALID_JS_EVENT_FRAMING")
    payload = head + b"}"
    require(sha256(payload).hexdigest() == event_hash, "INVALID_EVENT_PAYLOAD_HASH")

    state_hash = sha256(state).hexdigest()
    line_hash = sha256(line).hexdigest()
    fp = p.get("fingerprint")
    require(type(fp) is str and SHA.fullmatch(fp), "INVALID_SHADOW_FINGERPRINT")
    # The frozen experimental JS source joins with literal backslash + zero.
    parts = [SCOPE, p["mutationId"], str(expected), str(epoch),
             previous if previous is not None else "<GENESIS>",
             event_hash, state_hash, line_hash]
    require(sha256(r"\0".join(parts).encode()).hexdigest() == fp,
            "SHADOW_FINGERPRINT_MISMATCH")

    return Mutation(
        scope=SCOPE, mutation_id=p["mutationId"], expected_revision=expected,
        previous_event_hash=previous, payload_bytes=payload, event_line=line,
        state_bytes=state, authority_fingerprint=AUTH,
    ), {
        "scope": SCOPE, "mutationId": p["mutationId"], "fingerprint": fp,
        "expectedEpoch": epoch, "eventHash": event_hash,
        "stateSha256": state_hash, "eventLineSha256": line_hash,
    }


def reply_receipt(record, meta: dict) -> dict:
    return {
        **meta,
        "disposition": record.disposition,
        "effect": "CONFIRMED" if record.disposition == "CONFIRMED" else "NONE",
        "revision": record.revision, "eventHash": record.event_hash,
        "postgresBridgeFingerprint": record.fingerprint,
        "replay": record.replay,
    }


def main() -> int:
    req = read_request()
    conn = connect()
    try:
        op = req["op"]
        if op == "init":
            data = b64(req.get("stateBytes"))
            result = initialize(conn, SCOPE, data)
            output = {"status": "INIT_DISPOSABLE_POSTGRES16", "revision": result.revision}
        elif op == "read":
            state = read(conn, SCOPE)
            output = {
                "revision": state.revision, "epoch": 1,
                "stateBytes": base64.b64encode(state.state_bytes).decode("ascii"),
                "eventBytes": base64.b64encode(state.event_bytes).decode("ascii"),
                "stateSha256": state.state_sha256, "eventsSha256": state.events_sha256,
            }
        elif op == "counts":
            rec = conn.execute(
                "SELECT (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.head WHERE scope=%s) AS heads,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.events WHERE scope=%s) AS events,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.receipts WHERE scope=%s) AS receipts",
                (SCOPE, SCOPE, SCOPE),
            ).fetchone()
            output = {key: int(rec[key]) for key in ("heads", "events", "receipts")}
        else:
            command, meta = parse_proposal(req.get("proposal"))
            if op == "apply":
                try:
                    result = apply(conn, command)
                except StorageRejected as error:
                    if error.code == "STALE_REVISION":
                        output = {"disposition": "NONE_STALE", "effect": "NONE"}
                    elif error.code == "MUTATION_COLLISION":
                        # Deterministically rejected NEW request, original ID
                        # may already have CONFIRMED history. Never label that
                        # existing effect NONE or leak the command.
                        output = {
                            "disposition": "REJECTED_MUTATION_COLLISION",
                            "reason_code": "MUTATION_COLLISION",
                            "effect": "NONE_FOR_THIS_REQUEST",
                        }
                    else:
                        raise
                else:
                    output = reply_receipt(result, meta)
                    if req.get("simulate_lost_reply") is True:
                        # Confirmed real PG commit, synthetic IPC reply loss.
                        # Do NOT print a receipt: caller must reconcile original ID.
                        return 53
            else:
                result = reconcile(conn, command)  # READ-ONLY by bridge contract
                output = reply_receipt(result, meta)
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (StorageRejected, EffectUnknown, ValueError, KeyError,
            UnicodeError, psycopg.Error) as error:
        # Never leak URI, password, full exception or SQL.
        code = getattr(error, "code", None) or "A11_FAIL_CLOSED"
        print(str(code) if re.fullmatch(r"[A-Z0-9_]+", str(code)) else
              "A11_FAIL_CLOSED", file=sys.stderr)
        raise SystemExit(2)
