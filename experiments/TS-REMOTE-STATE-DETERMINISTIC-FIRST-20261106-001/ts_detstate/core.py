"""Synthetic-only deterministic PostgreSQL state protocol. No network at import time.

No Product aggregate, credentials, migrations, retry engine, agent, DBOS, or scheduler.
Connection MUST be a verified, autocommit=True, psycopg dict_row connection.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
import unicodedata
from typing import Any

SCHEMA = "ts_r3_synthetic_20261105_001"  # Static, never user-provided SQL identifier.
AUTHORITY = "AUTH-SYNTHETIC-R3"  # Experimental marker, NOT a Product grant.
MAX_REVISION = 1000
MAX_JSON_BYTES = 16_384
_ID = re.compile(r"R3-DET-[A-Za-z0-9_-]{8,72}\Z")
_KEYS = frozenset(("kind", "operation_id", "attempt_id", "mutation_id", "state_id", "expected_revision", "authority_ref", "state"))


class Rejected(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class CommitUnknown(Rejected):
    def __init__(self):
        super().__init__("COMMIT_OUTCOME_UNKNOWN")
        self.retry_authorized = False


def _validate_json(v: Any, depth: int = 0) -> None:
    if depth > 16:
        raise Rejected("JSON_DEPTH")
    if v is None or type(v) is bool:
        return
    if type(v) is int:
        if abs(v) > 9_007_199_254_740_991:
            raise Rejected("JSON_INTEGER_RANGE")
        return
    if type(v) is str:
        if len(v) > 4096 or unicodedata.normalize("NFC", v) != v:
            raise Rejected("JSON_UNSAFE_TEXT")
        try:
            v.encode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise Rejected("JSON_UNSAFE_TEXT") from exc
        return
    if type(v) is list:
        if len(v) > 256:
            raise Rejected("JSON_LIST_LIMIT")
        for item in v:
            _validate_json(item, depth + 1)
        return
    if type(v) is dict:
        if len(v) > 256:
            raise Rejected("JSON_MAP_LIMIT")
        for k, item in v.items():
            if type(k) is not str or k in ("__proto__", "constructor", "prototype"):
                raise Rejected("JSON_UNSAFE_KEY")
            _validate_json(k, depth + 1)
            _validate_json(item, depth + 1)
        return
    raise Rejected("JSON_UNSUPPORTED_TYPE")  # float, Decimal, tuple, exotic objects forbidden.


def canonical(value: Any) -> str:
    """Python-only canonical JSON v0. Cross-language canonicality NOT claimed."""
    _validate_json(value)
    s = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(s.encode("utf-8")) > MAX_JSON_BYTES:
        raise Rejected("JSON_BYTES_LIMIT")
    return s


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def strict_loads(data: str) -> Any:
    if type(data) is not str or len(data.encode("utf-8")) > MAX_JSON_BYTES:
        raise Rejected("JSON_BYTES_LIMIT")

    def pairs(kvs):
        out = {}
        for k, v in kvs:
            if k in out:
                raise Rejected("JSON_DUPLICATE_KEY")
            out[k] = v
        return out

    def no_float(_):
        raise Rejected("JSON_FLOAT_FORBIDDEN")

    def no_nonfinite(_):
        raise Rejected("JSON_NONFINITE_FORBIDDEN")

    try:
        obj = json.loads(data, object_pairs_hook=pairs, parse_float=no_float, parse_constant=no_nonfinite)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise Rejected("JSON_PARSE_FAILED") from exc
    canonical(obj)
    return obj


@dataclass(frozen=True, init=False)
class Command:
    operation_id: str
    attempt_id: str
    mutation_id: str
    state_id: str
    expected_revision: int
    _state_json: str

    @property
    def state(self) -> dict:
        # A new JSON object for each access: no mutable state escapes the validated snapshot.
        return json.loads(self._state_json)

    @staticmethod
    def from_dict(raw: Any) -> "Command":
        if type(raw) is not dict or set(raw) != _KEYS:
            raise Rejected("COMMAND_SHAPE")
        if raw["kind"] != "SyntheticState" or raw["authority_ref"] != AUTHORITY:
            raise Rejected("NON_SYNTHETIC_OR_UNBOUND_AUTHORITY")
        for key in ("operation_id", "attempt_id", "mutation_id", "state_id"):
            if type(raw[key]) is not str or not _ID.fullmatch(raw[key]):
                raise Rejected("COMMAND_IDENTITY")
        rev = raw["expected_revision"]
        if type(rev) is not int or not (0 <= rev < MAX_REVISION):
            raise Rejected("EXPECTED_REVISION")
        if type(raw["state"]) is not dict or raw["state"].get("synthetic") is not True:
            raise Rejected("NON_SYNTHETIC_STATE")
        canonical(raw)  # Forbid floats, malformed Unicode, overlarge JSON.
        cmd = object.__new__(Command)
        for key in ("operation_id", "attempt_id", "mutation_id", "state_id", "expected_revision"):
            object.__setattr__(cmd, key, raw[key])
        object.__setattr__(cmd, "_state_json", canonical(raw["state"]))
        return cmd

    def wire(self) -> dict:
        return {"kind": "SyntheticState", "authority_ref": AUTHORITY,
                "operation_id": self.operation_id, "attempt_id": self.attempt_id,
                "mutation_id": self.mutation_id, "state_id": self.state_id,
                "expected_revision": self.expected_revision, "state": self.state}

    def fingerprint(self) -> str:
        return digest(self.wire())

    def event_id(self) -> str:
        return self.mutation_id + "-event"


def _guard_command(cmd: Command) -> None:
    if type(cmd) is not Command or not isinstance(getattr(cmd, "_state_json", None), str):
        raise Rejected("COMMAND_NOT_VALIDATED")


def _guard_connection(conn) -> None:
    if getattr(conn, "autocommit", None) is not True:
        raise Rejected("AUTOCOMMIT_REQUIRED")


# Every SQL identifier is static; every value is a bound parameter.
_CLAIM = f"""INSERT INTO {SCHEMA}.receipts
(mutation_id,command_fingerprint,original_revision,result)
VALUES (%s,%s,%s,%s::jsonb)
ON CONFLICT (mutation_id) DO NOTHING RETURNING mutation_id"""
_RECEIPT_LOCK = f"SELECT mutation_id,command_fingerprint,original_revision,result FROM {SCHEMA}.receipts WHERE mutation_id=%s FOR UPDATE"
_RECEIPT_READ = f"SELECT mutation_id,command_fingerprint,original_revision,result FROM {SCHEMA}.receipts WHERE mutation_id=%s"
_STATE_LOCK = f"SELECT revision,state,last_event_sha256 FROM {SCHEMA}.aggregate_state WHERE id=%s FOR UPDATE"
_STATE_READ = f"SELECT revision,state,last_event_sha256 FROM {SCHEMA}.aggregate_state WHERE id=%s"
_CHAIN = f"SELECT event_id,sequence,previous_hash,event_hash,payload FROM {SCHEMA}.events WHERE id=%s ORDER BY sequence LIMIT 1001"
_STATE_INSERT = f"INSERT INTO {SCHEMA}.aggregate_state(id,revision,state,last_event_sha256) VALUES (%s,%s,%s::jsonb,%s)"
_STATE_UPDATE = f"UPDATE {SCHEMA}.aggregate_state SET revision=%s,state=%s::jsonb,last_event_sha256=%s WHERE id=%s AND revision=%s RETURNING revision"
_EVENT_INSERT = f"INSERT INTO {SCHEMA}.events(event_id,id,sequence,previous_hash,event_hash,payload) VALUES (%s,%s,%s,%s,%s,%s::jsonb)"
_RECEIPT_UPDATE = f"UPDATE {SCHEMA}.receipts SET result=%s::jsonb WHERE mutation_id=%s AND command_fingerprint=%s RETURNING mutation_id"


def _rows_chain(cur, state_id: str, state_row: dict | None) -> list[dict]:
    cur.execute(_CHAIN, (state_id,))
    rows = cur.fetchall()
    if len(rows) > MAX_REVISION:
        raise Rejected("CHAIN_LIMIT")
    if state_row is None:
        if rows:
            raise Rejected("ORPHAN_EVENTS")
        return []
    if not rows or state_row["revision"] != len(rows):
        raise Rejected("CHAIN_REVISION_MISMATCH")
    previous = None
    for i, row in enumerate(rows, start=1):
        p = row["payload"]
        if (row["sequence"] != i or row["previous_hash"] != previous
            or type(p) is not dict or p.get("state_id") != state_id
            or p.get("revision") != i or p.get("previous_hash") != previous
            or p.get("authority_ref") != AUTHORITY
            or type(p.get("state")) is not dict or p["state"].get("synthetic") is not True
            or any(type(p.get(k)) is not str or not _ID.fullmatch(p[k]) for k in
                   ("mutation_id", "attempt_id", "operation_id"))
            or row["event_id"] != p["mutation_id"] + "-event"
            or row["event_hash"] != digest(p)) :
            raise Rejected("CHAIN_HASH_MISMATCH")
        previous = row["event_hash"]
    if state_row["last_event_sha256"] != previous or state_row["state"] != rows[-1]["payload"]["state"]:
        raise Rejected("AGGREGATE_CHAIN_MISMATCH")
    return rows


def _verify_receipt(cur, cmd: Command, receipt: dict) -> dict:
    if receipt["mutation_id"] != cmd.mutation_id or receipt["command_fingerprint"] != cmd.fingerprint():
        raise Rejected("MUTATION_IDENTITY_COLLISION")
    expected_new = cmd.expected_revision + 1
    if receipt["original_revision"] != expected_new:
        raise Rejected("RECEIPT_REVISION_MISMATCH")
    cur.execute(_STATE_READ, (cmd.state_id,))
    current = cur.fetchone()
    chain = _rows_chain(cur, cmd.state_id, current)
    if expected_new > len(chain):
        raise Rejected("INCOMPLETE_EFFECT")
    event = chain[expected_new - 1]
    p = event["payload"]
    result = {"revision": expected_new, "event_id": cmd.event_id(),
              "event_hash": event["event_hash"], "synthetic": True}
    if (event["event_id"] != cmd.event_id() or p.get("state") != cmd.state
        or p.get("attempt_id") != cmd.attempt_id or p.get("operation_id") != cmd.operation_id
        or p.get("authority_ref") != AUTHORITY or receipt["result"] != result):
        raise Rejected("RECEIPT_EVENT_MISMATCH")
    return result


def _rollback(cur) -> None:
    try:
        cur.execute("ROLLBACK")
    except Exception:
        pass  # Never re-dispatch after any ambiguous connection failure.


def apply_once(conn, cmd: Command) -> dict:
    """One authorized attempt; does not open/retry a connection. Caller owns secure auth.

    COMMIT transmission failure => UNKNOWN (no automatic replay, ever).
    Other driver failures => fail closed; reconcile before any future write.
    """
    _guard_command(cmd)
    _guard_connection(conn)
    with conn.cursor() as cur:
        started = False
        commit_sent = False
        try:
            cur.execute("BEGIN")
            started = True
            cur.execute(_CLAIM, (cmd.mutation_id, cmd.fingerprint(), cmd.expected_revision + 1, '{"pending":true}'))
            claimed = cur.fetchone()
            if claimed is None:
                cur.execute(_RECEIPT_LOCK, (cmd.mutation_id,))
                prior = cur.fetchone()
                if prior is None:
                    raise Rejected("RECEIPT_NOT_VISIBLE")
                result = _verify_receipt(cur, cmd, prior)
                commit_sent = True
                cur.execute("COMMIT")
                return {"disposition": "RECONCILED", "effect": "CONFIRMED", "retry_authorized": False, **result}

            cur.execute(_STATE_LOCK, (cmd.state_id,))
            current = cur.fetchone()
            if current is None:
                if cmd.expected_revision != 0:
                    raise Rejected("STALE_REVISION")
                prev_hash = None
            else:
                if current["revision"] != cmd.expected_revision:
                    raise Rejected("STALE_REVISION")
                _rows_chain(cur, cmd.state_id, current)
                prev_hash = current["last_event_sha256"]
            new_revision = cmd.expected_revision + 1
            payload = {"mutation_id": cmd.mutation_id, "state_id": cmd.state_id,
                       "operation_id": cmd.operation_id, "attempt_id": cmd.attempt_id,
                       "authority_ref": AUTHORITY, "revision": new_revision,
                       "previous_hash": prev_hash, "state": cmd.state}
            event_hash = digest(payload)
            if current is None:
                cur.execute(_STATE_INSERT, (cmd.state_id, new_revision, canonical(cmd.state), event_hash))
            else:
                cur.execute(_STATE_UPDATE, (new_revision, canonical(cmd.state), event_hash, cmd.state_id, cmd.expected_revision))
                if cur.fetchone() is None:
                    raise Rejected("STALE_REVISION")
            cur.execute(_EVENT_INSERT, (cmd.event_id(), cmd.state_id, new_revision, prev_hash, event_hash, canonical(payload)))
            result = {"revision": new_revision, "event_id": cmd.event_id(), "event_hash": event_hash, "synthetic": True}
            cur.execute(_RECEIPT_UPDATE, (canonical(result), cmd.mutation_id, cmd.fingerprint()))
            if cur.fetchone() is None:
                raise Rejected("RECEIPT_UPDATE_MISSING")
            commit_sent = True
            cur.execute("COMMIT")
            return {"disposition": "COMMITTED", "effect": "CONFIRMED", "retry_authorized": False, **result}
        except Exception as exc:
            if commit_sent:
                raise CommitUnknown() from None
            if started:
                _rollback(cur)
            if isinstance(exc, Rejected):
                raise
            raise Rejected("PRECOMMIT_FAILED_RECONCILE_FIRST") from None


def reconcile_readonly(conn, cmd: Command) -> dict:
    """A brand-new read-only transaction, including receipt/chain in one snapshot."""
    _guard_command(cmd)
    _guard_connection(conn)
    with conn.cursor() as cur:
        try:
            cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
            cur.execute(_RECEIPT_READ, (cmd.mutation_id,))
            receipt = cur.fetchone()
            if receipt is None:
                cur.execute("COMMIT")
                return {"disposition": "NOT_OBSERVED", "effect": "UNKNOWN", "retry_authorized": False}
            result = _verify_receipt(cur, cmd, receipt)
            cur.execute("COMMIT")
            return {"disposition": "RECONCILED", "effect": "CONFIRMED", "retry_authorized": False, **result}
        except Rejected:
            _rollback(cur)
            raise
        except Exception:
            _rollback(cur)
            raise Rejected("READ_UNAVAILABLE_NO_RETRY") from None
