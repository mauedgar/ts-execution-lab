"""Actual Product JS V0 20 generation bytes -> real disposable PostgreSQL16.

Uses 19 canonical Product events emitted by the original FS store and the
unchanged experimental Python bridge over psycopg3 top-level SQL transactions.
No Neon, network ACK loss, Product mutation, or migration to a live database.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import psycopg
from psycopg.rows import dict_row
from ts_global.bridge import Mutation, apply, initialize, read, reconcile

URI = ("postgresql://tsr3_e2_synthetic:e2_local_disposable_only"
       "@127.0.0.1:5432/tsr3_e2_synthetic?sslmode=disable")
ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA = "ts_r3_global_head_20261107_001"

def open_db():
    assert os.getenv("TS_R3_NEON_CHILD_DSN") is None, "NO_NEON_DSN"
    assert os.getenv("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI
    db = psycopg.connect(URI, autocommit=True, row_factory=dict_row,
                         connect_timeout=5, application_name="ts-r3-e2-local")
    assert db.execute("SHOW server_version").fetchone()["server_version"].startswith("16.")
    return db

def prepare(db):
    raw = (ROOT / "schema.sql").read_text(encoding="utf-8")
    sql = "\n".join(line for line in raw.splitlines()
                    if not line.lstrip().startswith("--"))
    statements = [part.strip() for part in sql.split(";") if part.strip()]
    assert len(statements) == 4 and statements[0].startswith("CREATE SCHEMA ")
    assert all(part.startswith("CREATE TABLE ") for part in statements[1:])
    with db.transaction():
        for statement in statements:
            db.execute(statement)



def decoded(value: str) -> bytes:
    assert type(value) is str, "BASE64_STRING_REQUIRED"
    return base64.b64decode(value, validate=True)


def main() -> int:
    assert len(sys.argv) == 2, "ONE_DISPOSABLE_FIXTURE_REQUIRED"
    file = Path(sys.argv[1]).resolve(strict=True)
    fixture = json.loads(file.read_text(encoding="utf-8"))
    assert fixture["kind"] == "PRODUCT_JS_V0_EXACT_GENERATIONS"
    assert fixture["product_git_commit"] == "26509b74d50207bb247dcc9bdb929a63f5451e88"
    assert fixture["source_blobs"] == {
        "contracts": "5d2d3a8a24ebc17339675e0c801595956e0cd353",
        "index": "0219b92e5f546407a6060a6dc449865c14c7f144",
        "store": "f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a",
    }
    scope = fixture["scope"]
    assert scope == "ts-r3-e1-product-bridge-20261107-002"
    captures = fixture["generations"]
    assert type(captures) is list and len(captures) == 20
    assert [row["revision"] for row in captures] == list(range(20))

    assert psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary"
    db = open_db()
    prepare(db)
    gen = captures[0]
    genbytes = decoded(gen["state_b64"])
    assert gen["payload_b64"] is None and gen["event_line_b64"] is None
    assert decoded(gen["events_b64"]) == b""
    beginning = initialize(db, scope, genbytes)
    assert beginning.revision == 0 and beginning.state_bytes == genbytes
    assert beginning.event_bytes == b""
    assert read(db, scope).state_bytes == genbytes

    prior_hash = None
    wire_events = b""
    auth = hashlib.sha256(b"SYNTHETIC_E1_PRODUCT_GOLDEN_AUTHORITY_ONLY").hexdigest()
    receipts = []
    for rev in range(1, 20):
        stage = captures[rev]
        previous = captures[rev - 1]
        state = decoded(stage["state_b64"])
        payload = decoded(stage["payload_b64"])
        event_line = decoded(stage["event_line_b64"])
        wire_events += event_line
        assert decoded(stage["events_b64"]) == wire_events, "EXACT_PRODUCT_EVENT_BYTES"
        assert stage["previous_hash"] == prior_hash
        assert stage["event_hash"] == hashlib.sha256(payload).hexdigest()
        assert event_line.endswith(b"\n")
        assert state.endswith(b"\n")
        assert len(state) <= 4 * 1024 * 1024
        assert len(payload) <= 4 * 1024 * 1024
        assert len(wire_events) > 0
        assert previous["revision"] + 1 == rev
        command = Mutation(
            scope=scope,
            mutation_id=f"e1-source-stage-{rev:02}",
            expected_revision=rev - 1,
            previous_event_hash=prior_hash,
            payload_bytes=payload,
            event_line=event_line,
            state_bytes=state,
            authority_fingerprint=auth,
        )
        receipt = apply(db, command)
        assert receipt.disposition == "CONFIRMED" and receipt.revision == rev
        assert receipt.replay is False
        assert receipt.event_hash == stage["event_hash"]
        view = read(db, scope)
        assert view.revision == rev and view.state_bytes == state
        assert view.event_bytes == wire_events
        assert view.last_event_hash == stage["event_hash"]
        assert view.state_sha256 == hashlib.sha256(state).hexdigest()
        assert view.events_sha256 == hashlib.sha256(wire_events).hexdigest()
        confirmation = reconcile(db, command)
        assert (confirmation.disposition, confirmation.replay, confirmation.revision) == (
            "CONFIRMED", True, rev
        )
        receipts.append(command)
        # Bind the next event to this source Product generation's exact hash.
        prior_hash = stage["event_hash"]

    # Read-only receipt replay must not append or modify a second event.
    before_head = read(db, scope)
    duplicate = apply(db, receipts[-1])
    assert duplicate.disposition == "CONFIRMED" and duplicate.replay is True
    after_head = read(db, scope)
    assert after_head.state_bytes == before_head.state_bytes
    assert after_head.event_bytes == before_head.event_bytes
    assert after_head.revision == 19

    sql_counts = db.execute(
        "SELECT (SELECT COUNT(*) FROM " + SCHEMA + ".events WHERE scope=%s) AS events,"
        " (SELECT COUNT(*) FROM " + SCHEMA + ".receipts WHERE scope=%s) AS receipts",
        (scope, scope)
    ).fetchone()
    assert sql_counts == {"events": 19, "receipts": 19}, sql_counts
    db.close()
    # Verify committed bytes and revision from a DISTINCT PostgreSQL client.
    observer = open_db()
    final_view = read(observer, scope)
    assert final_view.revision == 19
    assert final_view.state_bytes == before_head.state_bytes
    assert final_view.event_bytes == wire_events
    observer.close()

    print(json.dumps({
        "status": "PRODUCT_JS_NATIVE_19_EVENTS_REAL_PG16_BRIDGE_BYTE_PARITY_PASS",
        "product_exact_generations": 20,
        "product_events": 19,
        "bridge_receipts": 19,
        "raw_event_sha256": hashlib.sha256(wire_events).hexdigest(),
        "raw_final_state_sha256": hashlib.sha256(after_head.state_bytes).hexdigest(),
        "backend": "DISPOSABLE_REAL_POSTGRESQL16",
        "postgresql_transactionality": "CONFIRMED_LOCAL",
        "db_events": sql_counts["events"],
        "db_receipts": sql_counts["receipts"],
        "remote_neon": "NOT_RUN",
        "two_hosts": "NOT_RUN",
        "real_network_ack_loss": "NOT_RUN",
        "sql_effect": "SYNTHETIC_DISPOSABLE_LOCAL_ONLY",
        "product_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
