"""D7/A003 bounded disposable PostgreSQL16 qualification. Never connects to Neon."""
from __future__ import annotations
import base64
from dataclasses import replace
from hashlib import sha256
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import time

import psycopg
from psycopg.rows import dict_row
from ts_global.bridge import (
    Mutation, StorageRejected, MAX_BYTES, apply, initialize, read, reconcile,
)

URI = "postgresql://tsr3_e2_synthetic:e2_local_disposable_only@127.0.0.1:5432/tsr3_e2_synthetic?sslmode=disable"
ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "ts_r3_global_head_20261107_001"
SCOPE = "ts-r3-d7-a003-disposable-20261107-001"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def decoded(value):
    return base64.b64decode(value, validate=True)


def db_open():
    require(os.environ.get("TS_R3_NEON_CHILD_DSN") is None, "NO_NEON")
    require(os.environ.get("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI, "EXACT_DISPOSABLE_URI")
    conn = psycopg.connect(URI, autocommit=True, row_factory=dict_row, connect_timeout=5)
    require(conn.execute("SHOW server_version").fetchone()["server_version"].startswith("16."), "PG16")
    return conn


def prepare(conn):
    source = (ROOT / "schema.sql").read_text(encoding="utf-8")
    statements = [p.strip() for p in "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("--")
    ).split(";") if p.strip()]
    require(len(statements) == 4, "SCHEMA_SHAPE")
    with conn.transaction():
        for statement in statements:
            conn.execute(statement)


def counts(conn):
    return conn.execute(
        f"SELECT (SELECT count(*) FROM {SCHEMA}.events WHERE scope=%s) AS events,"
        f" (SELECT count(*) FROM {SCHEMA}.receipts WHERE scope=%s) AS receipts",
        (SCOPE, SCOPE),
    ).fetchone()


def rejected(conn, command, expected, before):
    try:
        apply(conn, command)
    except StorageRejected as exc:
        require(exc.code == expected, f"EXPECTED_{expected}_GOT_{exc.code}")
    else:
        raise AssertionError(f"UNEXPECTED_ACCEPT_{expected}")
    after = read(conn, SCOPE)
    require((after.revision, after.state_bytes, after.event_bytes) ==
            (before.revision, before.state_bytes, before.event_bytes), "NEGATIVE_CHANGED_HEAD")
    require(counts(conn) == {"events": before.revision, "receipts": before.revision},
            "NEGATIVE_CHANGED_ROWS")


def main():
    require(len(sys.argv) == 2, "ONE_FIXTURE")
    fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    require(fixture["kind"] == "PRODUCT_JS_V0_EXACT_GENERATIONS", "PRODUCT_FIXTURE")
    require(fixture["product_git_commit"] == "26509b74d50207bb247dcc9bdb929a63f5451e88", "PRODUCT_REF")
    generations = fixture["generations"]
    require(len(generations) == 20, "GENERATION_COUNT")
    require([g["revision"] for g in generations] == list(range(20)), "REVISION_ORDER")
    require(psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary", "PSYCOPG_PIN")
    conn = db_open()
    prepare(conn)
    initial = decoded(generations[0]["state_b64"])
    initialize(conn, SCOPE, initial)
    prior_hash = None
    event_stream = b""
    auth = sha256(b"D7_A003_DISPOSABLE_ONLY").hexdigest()
    commands = []
    times = []
    for revision in range(1, 20):
        generation = generations[revision]
        payload = decoded(generation["payload_b64"])
        line = decoded(generation["event_line_b64"])
        state = decoded(generation["state_b64"])
        command = Mutation(SCOPE, f"d7-stage-{revision:02}", revision - 1,
                           prior_hash, payload, line, state, auth)
        started = time.perf_counter_ns()
        receipt = apply(conn, command)
        times.append(time.perf_counter_ns() - started)
        require(receipt.disposition == "CONFIRMED" and not receipt.replay, "CAS_CONFIRM")
        require(receipt.revision == revision, "RECEIPT_REVISION")
        event_stream += line
        view = read(conn, SCOPE)
        require(view.revision == revision and view.state_bytes == state, "STATE_BYTES")
        require(view.event_bytes == event_stream, "EVENT_BYTES")
        require(view.state_sha256 == sha256(state).hexdigest(), "STATE_HASH")
        require(view.events_sha256 == sha256(event_stream).hexdigest(), "EVENTS_HASH")
        require(decoded(generation["events_b64"]) == event_stream, "PRODUCT_EVENTS")
        require(reconcile(conn, command).disposition == "CONFIRMED", "RECONCILE")
        commands.append(command)
        prior_hash = generation["event_hash"]
    final = read(conn, SCOPE)
    observer = db_open()
    observed = read(observer, SCOPE)
    require(observed.state_bytes == final.state_bytes and
            observed.event_bytes == final.event_bytes, "OBSERVER_MISMATCH")
    with tempfile.TemporaryDirectory(prefix="ts-r3-d7-a003-") as temporary:
        folder = Path(temporary)
        snapshot = folder / "state.json"
        events = folder / "events.jsonl"
        with snapshot.open("xb") as f:
            f.write(final.state_bytes)
        with events.open("xb") as f:
            f.write(final.event_bytes)
        require(snapshot.read_bytes() == decoded(generations[-1]["state_b64"]), "RESTORE_STATE")
        require(events.read_bytes() == decoded(generations[-1]["events_b64"]), "RESTORE_EVENTS")
        subprocess.run(["node", str(ROOT / "d7_a003" / "restore_oracle.cjs"), str(Path(sys.argv[1]).resolve().parent), str(snapshot), str(events)], check=True, stdout=sys.stderr)
    require(counts(conn) == {"events": 19, "receipts": 19}, "ROWS")
    replay = apply(conn, commands[-1])
    require(replay.disposition == "CONFIRMED" and replay.replay, "REPLAY")
    before = read(conn, SCOPE)
    rejected(conn, replace(commands[-1], mutation_id="stale-new"), "STALE_REVISION", before)
    rejected(conn, replace(commands[-1], authority_fingerprint="invalid"), "INVALID_HASH", before)
    rejected(conn, replace(commands[-1], event_line=b"invalid"), "EVENT_LINE_FRAMING", before)
    rejected(conn, replace(commands[-1], payload_bytes=b"x" * (MAX_BYTES + 1)), "INVALID_BYTES", before)
    rejected(conn, replace(commands[-1], mutation_id="d7-stage-19", authority_fingerprint=sha256(b"DIFFERENT").hexdigest()), "MUTATION_COLLISION", before)
    observer.close()
    conn.close()
    print(json.dumps({
        "status": "D7_A003_DISPOSABLE_PG16_PARTIAL_PASS",
        "product_effect": "NONE", "neon": "NOT_RUN", "hosts": 1,
        "generations": 20, "events": 19, "receipts": 19,
        "state_sha256": sha256(final.state_bytes).hexdigest(),
        "events_sha256": sha256(final.event_bytes).hexdigest(),
        "negative_cases": 5, "bounded_apply_max_ms": round(max(times) / 1e6, 3),
        "d7_product_js_restore_oracle": "PASS",
        "d7_sql_failure_rollback": "NOT_RUN",
        "a003_capacity_envelope": "NOT_RUN",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
