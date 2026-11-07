"""Experimental byte-preserving PostgreSQL storage for the existing Tecnotron JS Kernel.

This code does NOT decide TaskCycle transitions, grants or execution retries. The
trusted JS caller must validate a candidate via its canonical Product contracts;
this layer verifies exact historical bytes, global revision and transactionality.

Requires psycopg 3's explicit transaction() and dict_row connection configuration.
No SQL is executed during import. No schema creation, network or credentials here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any

from . import legacy_v0

SCHEMA = "ts_r3_global_head_20261107_001"
HEAD = f"{SCHEMA}.head"
EVENTS = f"{SCHEMA}.events"
RECEIPTS = f"{SCHEMA}.receipts"
KINDS = ("Milestone", "TaskCycle", "Operation", "ExecutionAttempt")
MAX_SAFE = (1 << 53) - 1
MAX_BYTES = 4 * 1024 * 1024  # bounded synthetic qualification, not a Product scale decision
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")


class StorageRejected(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class EffectUnknown(StorageRejected):
    """Transaction may have committed. Never automatically re-dispatch it."""
    def __init__(self):
        super().__init__("UNKNOWN_EFFECT_REQUIRES_RECONCILIATION")


def _require(condition: bool, code: str = "INVALID_CONTRACT") -> None:
    if not condition:
        raise StorageRejected(code)


def _id(value: Any) -> None:
    _require(type(value) is str and _ID.fullmatch(value) is not None and
             value not in ("__proto__", "constructor", "prototype"), "INVALID_ID")


def _hash(value: Any) -> None:
    _require(type(value) is str and _SHA.fullmatch(value) is not None, "INVALID_HASH")


def _integer(value: Any, *, minimum: int = 0) -> None:
    _require(type(value) is int and minimum <= value <= MAX_SAFE, "INVALID_REVISION")


def _bytes(value: Any) -> bytes:
    if isinstance(value, memoryview):
        value = value.tobytes()
    _require(type(value) is bytes and len(value) <= MAX_BYTES, "INVALID_BYTES")
    return value


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _exact_payload_bytes(payload_bytes: bytes, payload: Any) -> None:
    """Require bytes from Product V0 compact JSON.stringify, not just valid JSON."""
    _require(type(payload) is dict, "INVALID_EVENT")
    try:
        expected = legacy_v0.exact_js_event_payload(payload)
    except ValueError as exc:
        raise StorageRejected("PRODUCT_V0_ENCODING_UNSUPPORTED") from exc
    _require(payload_bytes == expected, "EVENT_JS_BYTES_MISMATCH")


def _expected_event_line(payload_bytes: bytes, event_hash: str) -> bytes:
    """Exact JS Product v0 append of a final `hash` property, no JSONB roundtrip."""
    payload_bytes = _bytes(payload_bytes)
    _hash(event_hash)
    _require(payload_bytes.startswith(b"{") and payload_bytes.endswith(b"}"), "PAYLOAD_FRAMING")
    line = payload_bytes[:-1] + b',"hash":"' + event_hash.encode("ascii") + b'"}\n'
    return _bytes(line)


def _no_dupes(pairs: list[tuple[str, Any]]) -> dict:
    d = {}
    for k, v in pairs:
        if k in d:
            raise StorageRejected("DUPLICATE_JSON_KEY")
        d[k] = v
    return d


def _parse(data: bytes) -> Any:
    data = _bytes(data)
    try:
        def parse_int(value: str) -> int:
            result = int(value)
            if abs(result) > MAX_SAFE:
                raise StorageRejected("UNSAFE_JSON_INTEGER")
            return result
        def reject_constant(_: str) -> None:
            raise StorageRejected("NONFINITE_JSON")
        return json.loads(data.decode("utf-8", "strict"), object_pairs_hook=_no_dupes,
                          parse_int=parse_int, parse_constant=reject_constant,
                          parse_float=lambda _: (_ for _ in ()).throw(StorageRejected("UNSUPPORTED_JSON_FLOAT")))
    except (UnicodeError, ValueError, RecursionError, TypeError) as exc:
        raise StorageRejected("INVALID_JSON") from exc


def _structure(snapshot: Any, revision: int) -> None:
    _require(type(snapshot) is dict and set(snapshot) == {"schema_version", "revision", "aggregates"}, "INVALID_SNAPSHOT")
    _require(snapshot["schema_version"] == "tecnotron-state-kernel/v0", "INVALID_SNAPSHOT")
    _integer(snapshot["revision"])
    _require(snapshot["revision"] == revision, "SNAPSHOT_REVISION_MISMATCH")
    aggs = snapshot["aggregates"]
    _require(type(aggs) is dict and set(aggs) == set(KINDS), "INVALID_SNAPSHOT")
    for k in KINDS:
        _require(type(aggs[k]) is dict, "INVALID_SNAPSHOT")
        for ident, agg in aggs[k].items():
            _id(ident)
            _require(type(agg) is dict and agg.get("kind") == k and agg.get("id") == ident,
                     "INVALID_SNAPSHOT")
    try:
        legacy_v0.validate_state(snapshot, revision)
    except ValueError as exc:
        raise StorageRejected("PRODUCT_V0_CONTRACT_MISMATCH") from exc


def _exact_snapshot_bytes(state_bytes: bytes, state: dict) -> None:
    try:
        expected = legacy_v0.exact_js_snapshot(state)
    except ValueError as exc:
        raise StorageRejected("PRODUCT_V0_ENCODING_UNSUPPORTED") from exc
    _require(state_bytes == expected, "SNAPSHOT_JS_BYTES_MISMATCH")


def _product_event(payload: dict) -> None:
    try:
        legacy_v0.validate_event(payload)
    except ValueError as exc:
        raise StorageRejected("PRODUCT_V0_EVENT_MISMATCH") from exc


def _exact_row(row: Any, keys: set[str]) -> None:
    _require(type(row) is dict and set(row) == keys, "DB_ROW_INVALID")


@dataclass(frozen=True)
class StateView:
    scope: str
    revision: int
    state_bytes: bytes
    event_bytes: bytes
    last_event_hash: str | None
    state_sha256: str
    events_sha256: str


@dataclass(frozen=True)
class Mutation:
    scope: str
    mutation_id: str
    expected_revision: int
    previous_event_hash: str | None
    payload_bytes: bytes    # exact JS JSON.stringify(event without 'hash') bytes
    event_line: bytes      # exact JS JSON.stringify({...payload,hash}) + '\n'
    state_bytes: bytes     # exact JS serialize(state): pretty JSON + '\n'
    authority_fingerprint: str  # hash of externally admitted immutable grant/context; DB does not issue it

    def fingerprint(self) -> str:
        """Framed fingerprint, unambiguous across scope, auth, bytes and revisions."""
        values = [self.scope.encode(), self.mutation_id.encode(), str(self.expected_revision).encode(),
                  (self.previous_event_hash or "").encode(), self.authority_fingerprint.encode(),
                  self.payload_bytes, self.event_line, self.state_bytes]
        digest = sha256(b"ts-r3-global-command/v0\x00")
        for part in values:
            digest.update(len(part).to_bytes(8, "big"))
            digest.update(part)
        return digest.hexdigest()


@dataclass(frozen=True)
class Receipt:
    disposition: str  # CONFIRMED or NONE; unexpected network result raises EffectUnknown
    revision: int
    event_hash: str | None
    fingerprint: str
    replay: bool


def _preflight_mutation(m: Mutation) -> tuple[str, dict, dict]:
    _require(type(m) is Mutation, "INVALID_COMMAND")
    _id(m.scope)
    _id(m.mutation_id)
    _integer(m.expected_revision)
    _hash(m.authority_fingerprint)
    if m.previous_event_hash is not None:
        _hash(m.previous_event_hash)
    payload = _parse(m.payload_bytes)
    _exact_payload_bytes(m.payload_bytes, payload)
    state = _parse(m.state_bytes)
    line = _bytes(m.event_line)
    _require(line.endswith(b"\n") and not line.endswith(b"\n\n"), "EVENT_LINE_FRAMING")
    _require(line == _expected_event_line(m.payload_bytes, _sha(m.payload_bytes)), "EVENT_BYTES_MISMATCH")
    event = _parse(line[:-1])
    _require(type(payload) is dict and type(event) is dict, "INVALID_EVENT")
    _require(set(event) == set(payload) | {"hash"} and event.get("hash") == _sha(m.payload_bytes), "INVALID_EVENT_HASH")
    _require({k: v for k, v in event.items() if k != "hash"} == payload, "EVENT_LINE_PAYLOAD_MISMATCH")
    _require(type(payload.get("kind")) is str and payload["kind"] in KINDS, "INVALID_EVENT_KIND")
    _require(payload.get("id") == f"event-{m.expected_revision + 1}", "INVALID_EVENT_ID")
    _require(type(payload.get("sequence")) is int and payload["sequence"] == m.expected_revision + 1,
             "EVENT_SEQUENCE_MISMATCH")
    _require(payload.get("previous_hash") == m.previous_event_hash, "EVENT_PREVIOUS_HASH_MISMATCH")
    _require(type(payload.get("after")) is dict, "INVALID_EVENT_AFTER")
    _structure(state, m.expected_revision + 1)
    _exact_snapshot_bytes(m.state_bytes, state)
    _product_event(payload)
    target_kind = payload["kind"]
    target_id = payload.get("aggregate_id")
    _id(target_id)
    _require(payload["after"].get("id") == target_id and payload["after"].get("kind") == target_kind,
             "INVALID_EVENT_AFTER")
    _integer(payload.get("before_revision"))
    _integer(payload["after"].get("revision"), minimum=1)
    _require(payload["after"]["revision"] == payload["before_revision"] + 1 and
             payload["after"].get("last_event_id") == payload["id"] and
             payload["after"].get("schema_version") == "tecnotron-state-kernel/v0",
             "INVALID_EVENT_AFTER")
    _require(state["aggregates"][target_kind].get(target_id) == payload["after"], "SNAPSHOT_EVENT_MISMATCH")
    return event["hash"], payload, state


def _require_conn(conn: Any) -> None:
    # Autocommit=True guarantees the psycopg transaction() block is top-level.
    _require(getattr(conn, "autocommit", None) is True, "AUTOCOMMIT_TRUE_REQUIRED")
    _require(callable(getattr(conn, "transaction", None)) and callable(getattr(conn, "cursor", None)),
             "INVALID_CONNECTION")
    # psycopg3 conn.transaction() inside an existing transaction opens a
    # SAVEPOINT; success there would be a *false* durable-commit claim.
    info = getattr(conn, "info", None)
    status = getattr(getattr(info, "transaction_status", None), "name", None)
    _require(status == "IDLE", "TRANSACTION_NOT_IDLE")


def _snapshot_from_cursor(cur: Any, scope: str, *, locked: bool = False) -> StateView:
    tail = " FOR UPDATE" if locked else ""
    cur.execute(f"SELECT revision,state_bytes,state_sha256,events_sha256,last_event_hash FROM {HEAD} WHERE scope=%s{tail}",
                (scope,))
    row = cur.fetchone()
    _require(row is not None, "UNINITIALIZED")
    _exact_row(row, {"revision", "state_bytes", "state_sha256", "events_sha256", "last_event_hash"})
    _integer(row["revision"])
    revision = row["revision"]
    state_bytes = _bytes(row["state_bytes"])
    _hash(row["state_sha256"])
    _hash(row["events_sha256"])
    _require(_sha(state_bytes) == row["state_sha256"], "SNAPSHOT_TAMPERED")
    parsed_state = _parse(state_bytes)
    _structure(parsed_state, revision)
    _exact_snapshot_bytes(state_bytes, parsed_state)
    cur.execute(f"SELECT revision,event_hash,previous_event_hash,payload_bytes,event_line FROM {EVENTS} "
                "WHERE scope=%s ORDER BY revision", (scope,))
    rows = cur.fetchall()
    _require(type(rows) is list and len(rows) == revision, "EVENT_COUNT_MISMATCH")
    prev = None
    previous_state = {"schema_version": "tecnotron-state-kernel/v0", "revision": 0,
                      "aggregates": {k: {} for k in KINDS}}
    event_parts = []
    for seq, event_row in enumerate(rows, 1):
        _exact_row(event_row, {"revision", "event_hash", "previous_event_hash", "payload_bytes", "event_line"})
        _integer(event_row["revision"], minimum=1)
        _require(event_row["revision"] == seq, "EVENT_SEQUENCE_MISMATCH")
        _hash(event_row["event_hash"])
        payload_bytes = _bytes(event_row["payload_bytes"])
        line = _bytes(event_row["event_line"])
        _require(line.endswith(b"\n") and not line.endswith(b"\n\n"), "EVENT_LINE_FRAMING")
        _require(line == _expected_event_line(payload_bytes, event_row["event_hash"]),
                 "EVENT_BYTES_MISMATCH")
        payload = _parse(payload_bytes)
        _exact_payload_bytes(payload_bytes, payload)
        line_event = _parse(line[:-1])
        _require(type(payload) is dict and type(line_event) is dict and
                 set(line_event) == set(payload) | {"hash"} and
                 line_event.get("hash") == event_row["event_hash"] and
                 {k: v for k, v in line_event.items() if k != "hash"} == payload,
                 "EVENT_LINE_PAYLOAD_MISMATCH")
        _require(_sha(payload_bytes) == event_row["event_hash"], "EVENT_HASH_MISMATCH")
        _product_event(payload)
        _require(event_row["previous_event_hash"] == prev and payload.get("previous_hash") == prev,
                 "EVENT_CHAIN_MISMATCH")
        _require(payload.get("id") == f"event-{seq}" and payload.get("sequence") == seq,
                 "EVENT_SEQUENCE_MISMATCH")
        kind = payload.get("kind")
        _require(kind in KINDS and type(payload.get("after")) is dict, "EVENT_KIND_INVALID")
        ident = payload.get("aggregate_id")
        _id(ident)
        after = payload["after"]
        before = previous_state["aggregates"][kind].get(ident)
        _require(after.get("kind") == kind and after.get("id") == ident and
                 type(after.get("revision")) is int and
                 type(payload.get("before_revision")) is int and
                 payload["before_revision"] == (before or {}).get("revision", 0) and
                 after["revision"] == payload["before_revision"] + 1 and
                 after.get("last_event_id") == payload["id"], "EVENT_REPLAY_MISMATCH")
        previous_state["aggregates"][kind][ident] = after
        previous_state["revision"] = seq
        prev = event_row["event_hash"]
        event_parts.append(line)
    _require(prev == row["last_event_hash"], "HEAD_EVENT_MISMATCH")
    event_bytes = b"".join(event_parts)
    _require(_sha(event_bytes) == row["events_sha256"], "EVENT_STREAM_TAMPERED")
    _require(previous_state == _parse(state_bytes), "SNAPSHOT_REPLAY_MISMATCH")
    _exact_snapshot_bytes(state_bytes, previous_state)
    return StateView(scope, revision, state_bytes, event_bytes, prev,
                     row["state_sha256"], row["events_sha256"])


def read(conn: Any, scope: str) -> StateView:
    """A single repeatable-read snapshot; read-only, no external effects."""
    _id(scope)
    _require_conn(conn)
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                return _snapshot_from_cursor(cur, scope)
    except StorageRejected:
        raise
    except Exception as exc:
        raise StorageRejected("READ_UNAVAILABLE") from exc


def initialize(conn: Any, scope: str, state_bytes: bytes) -> StateView:
    """Exclusive genesis. Unknown commit ACK must reconcile by read(scope)."""
    _id(scope)
    _require_conn(conn)
    state = _parse(state_bytes)
    _structure(state, 0)
    _exact_snapshot_bytes(state_bytes, state)
    _require(all(not state["aggregates"][k] for k in KINDS), "GENESIS_NOT_EMPTY")
    virgin = {"schema_version": "tecnotron-state-kernel/v0", "revision": 0,
              "aggregates": {k: {} for k in KINDS}}
    _require(state_bytes == legacy_v0.exact_js_snapshot(virgin), "GENESIS_BYTES_MISMATCH")
    state_bytes = _bytes(state_bytes)
    attempted = False
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                attempted = True  # before dispatch: lost response is UNKNOWN
                cur.execute(f"INSERT INTO {HEAD}(scope,revision,state_bytes,state_sha256,events_sha256,last_event_hash) "
                            "VALUES(%s,0,%s,%s,%s,NULL) ON CONFLICT DO NOTHING RETURNING revision",
                            (scope, state_bytes, _sha(state_bytes), _sha(b"")))
                _require(cur.fetchone() is not None, "ALREADY_INITIALIZED")
    except StorageRejected:
        raise
    except Exception as exc:
        if attempted:
            raise EffectUnknown() from exc
        raise StorageRejected("INIT_UNAVAILABLE") from exc
    return read(conn, scope)


def apply(conn: Any, command: Mutation) -> Receipt:
    """One global CAS transaction. A dispatch/commit failure is UNKNOWN, never retried."""
    event_hash, _, next_state = _preflight_mutation(command)
    _require_conn(conn)
    fingerprint = command.fingerprint()
    dispatched = False
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                # Serialization on the *global* head, not per-aggregate revision.
                current = _snapshot_from_cursor(cur, command.scope, locked=True)
                cur.execute(f"SELECT command_fingerprint,result_revision,event_hash FROM {RECEIPTS} "
                            "WHERE scope=%s AND mutation_id=%s", (command.scope, command.mutation_id))
                old = cur.fetchone()
                if old is not None:
                    _exact_row(old, {"command_fingerprint", "result_revision", "event_hash"})
                    _hash(old["command_fingerprint"])
                    _hash(old["event_hash"])
                    _integer(old["result_revision"], minimum=1)
                    _require(old["command_fingerprint"] == fingerprint, "MUTATION_COLLISION")
                    _require(old["result_revision"] <= current.revision and
                             _sha(command.payload_bytes) == old["event_hash"], "RECEIPT_INCONSISTENT")
                    cur.execute(f"SELECT event_hash FROM {EVENTS} WHERE scope=%s AND revision=%s",
                                (command.scope, old["result_revision"]))
                    event = cur.fetchone()
                    _exact_row(event, {"event_hash"})
                    _require(event["event_hash"] == old["event_hash"], "RECEIPT_INCONSISTENT")
                    # replay is read only: never executes a second mutation
                    return Receipt("CONFIRMED", old["result_revision"], old["event_hash"], fingerprint, True)
                if current.revision != command.expected_revision or current.last_event_hash != command.previous_event_hash:
                    raise StorageRejected("STALE_REVISION")
                _require(next_state["revision"] == current.revision + 1, "SNAPSHOT_REVISION_MISMATCH")
                # Deep replay of proposed next bytes catches changes to unrelated aggregates.
                previous = _parse(current.state_bytes)
                proposed = _parse(command.state_bytes)
                target = _parse(command.payload_bytes)
                kind = target["kind"]
                ident = target["aggregate_id"]
                before = previous["aggregates"][kind].get(ident)
                _require(target["before_revision"] == (before or {}).get("revision", 0),
                         "AGGREGATE_REVISION_MISMATCH")
                previous["aggregates"][kind][ident] = target["after"]
                previous["revision"] += 1
                _require(previous == proposed, "SNAPSHOT_REPLAY_MISMATCH")
                _require(legacy_v0.exact_js_snapshot(previous) == command.state_bytes,
                         "SNAPSHOT_JS_BYTES_MISMATCH")
                new_stream = current.event_bytes + command.event_line
                dispatched = True  # before UPDATE dispatch, including lost SQL response
                cur.execute(f"UPDATE {HEAD} SET revision=%s,state_bytes=%s,state_sha256=%s,"
                            "events_sha256=%s,last_event_hash=%s WHERE scope=%s AND revision=%s "
                            "AND last_event_hash IS NOT DISTINCT FROM %s RETURNING revision",
                            (current.revision + 1, command.state_bytes, _sha(command.state_bytes),
                             _sha(new_stream), event_hash, command.scope, current.revision,
                             current.last_event_hash))
                _require(cur.fetchone() is not None, "STALE_REVISION")
                cur.execute(f"INSERT INTO {EVENTS}(scope,revision,event_hash,previous_event_hash,payload_bytes,event_line) "
                            "VALUES(%s,%s,%s,%s,%s,%s)",
                            (command.scope, current.revision + 1, event_hash, command.previous_event_hash,
                             command.payload_bytes, command.event_line))
                cur.execute(f"INSERT INTO {RECEIPTS}(scope,mutation_id,command_fingerprint,expected_revision,"
                            "result_revision,event_hash,authority_fingerprint) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (command.scope, command.mutation_id, fingerprint, command.expected_revision,
                             current.revision + 1, event_hash, command.authority_fingerprint))
    except StorageRejected:
        # A source-controlled rejected mutation is NONE; transaction context rolls back.
        # If an exception happens after dispatch of SQL, conservatively UNKNOWN.
        if dispatched:
            raise EffectUnknown() from None
        raise
    except Exception as exc:
        if dispatched:
            raise EffectUnknown() from exc
        raise StorageRejected("TRANSACTION_UNAVAILABLE") from exc
    return Receipt("CONFIRMED", command.expected_revision + 1, event_hash, fingerprint, False)


def reconcile(conn: Any, command: Mutation) -> Receipt:
    """One read-only snapshot of original uncertain effect; never calls apply()."""
    event_hash, _, _ = _preflight_mutation(command)
    _require_conn(conn)
    try:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                current = _snapshot_from_cursor(cur, command.scope)
                cur.execute(f"SELECT command_fingerprint,result_revision,event_hash FROM {RECEIPTS} "
                            "WHERE scope=%s AND mutation_id=%s", (command.scope, command.mutation_id))
                row = cur.fetchone()
                if row is None:
                    # Absence of receipt is not proof of NONE after an uncertain ACK.
                    raise EffectUnknown()
                _exact_row(row, {"command_fingerprint", "result_revision", "event_hash"})
                _integer(row["result_revision"], minimum=1)
                _hash(row["command_fingerprint"])
                _hash(row["event_hash"])
                _require(row["command_fingerprint"] == command.fingerprint() and
                         row["event_hash"] == event_hash and row["result_revision"] <= current.revision,
                         "RECEIPT_INCONSISTENT")
                cur.execute(f"SELECT event_hash FROM {EVENTS} WHERE scope=%s AND revision=%s",
                            (command.scope, row["result_revision"]))
                event = cur.fetchone()
                _exact_row(event, {"event_hash"})
                _require(event["event_hash"] == row["event_hash"], "RECEIPT_INCONSISTENT")
                return Receipt("CONFIRMED", row["result_revision"], event_hash, command.fingerprint(), True)
    except StorageRejected:
        raise
    except Exception as exc:
        raise StorageRejected("RECONCILE_UNAVAILABLE") from exc
