"""D5 native PostgreSQL16 durable commit with bounded SYNTHETIC client ACK uncertainty.

The connection transport failure is injected AFTER a confirmed psycopg COMMIT
or BEFORE COMMIT, not a real packet drop. Never retry an uncertain mutation.
Only a disposable localhost PostgreSQL16 service and synthetic fixed URI.
"""
from __future__ import annotations

from base64 import b64decode
from contextlib import contextmanager, closing
from dataclasses import replace
import json
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from ts_global.bridge import EffectUnknown, Mutation, apply, initialize, read, reconcile

URI = ("postgresql://tsr3_d5_synthetic:d5_only_local_nonproduction"
       "@127.0.0.1:5432/tsr3_d5_synthetic?sslmode=disable")
ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "ts_r3_global_head_20261107_001"
SCOPES = ("ts-r3-d5-ack-before-20261107-001",
          "ts-r3-d5-ack-after-20261107-001")


def connect():
    return psycopg.connect(URI, autocommit=True, row_factory=dict_row,
                           connect_timeout=5, application_name="ts-r3-d5-disposable")


class FaultConnection:
    """Controlled wrapper; inject client-side error around a REAL SQL commit."""
    def __init__(self, raw, mode):
        assert mode in ("before", "after")
        self.raw = raw
        self.mode = mode
        self.autocommit = raw.autocommit
        self.info = raw.info
        self.once = True

    @contextmanager
    def transaction(self):
        with self.raw.transaction():
            yield self
            if self.once and self.mode == "before":
                self.once = False
                # Exception inside real PostgreSQL transaction -> ROLLBACK.
                raise ConnectionError("SYNTHETIC_DROP_BEFORE_COMMIT")
        if self.once and self.mode == "after":
            self.once = False
            # PostgreSQL has now committed, but this caller observes UNKNOWN.
            # NOT a real network ACK drop; conservatively simulated.
            raise ConnectionError("SYNTHETIC_CLIENT_ACK_LOST_AFTER_REAL_COMMIT")

    @contextmanager
    def cursor(self):
        with self.raw.cursor() as cur:
            yield cur


def source(scope):
    golden = json.loads((ROOT / "oracle" / "golden.json").read_text(encoding="utf8"))
    event = golden["mutations"][0]
    initial = b64decode(golden["genesis_b64"], validate=True)
    command = Mutation(
        scope=scope,
        mutation_id="d5-synthetic-"+scope,
        expected_revision=0,
        previous_event_hash=None,
        payload_bytes=b64decode(event["payload_b64"], validate=True),
        event_line=b64decode(event["line_b64"], validate=True),
        state_bytes=b64decode(event["state_b64"], validate=True),
        authority_fingerprint=event["authority_fingerprint"],
    )
    return initial, command


def check_counts(conn, scope, expected):
    row = conn.execute(
        "SELECT (SELECT COUNT(*) FROM " + SCHEMA + ".events WHERE scope=%s) AS events, "
        "(SELECT COUNT(*) FROM " + SCHEMA + ".receipts WHERE scope=%s) AS receipts",
        (scope, scope),
    ).fetchone()
    assert row["events"] == expected and row["receipts"] == expected, row


def setup(conn):
    # Never split SQL containing comments; exact 4 statements in pinned schema.
    lines = (ROOT / "schema.sql").read_text(encoding="utf-8").splitlines()
    sql = "\n".join(line for line in lines if not line.lstrip().startswith("--"))
    parts = [p.strip() for p in sql.split(";") if p.strip()]
    assert len(parts) == 4 and parts[0].startswith("CREATE SCHEMA ")
    assert all(p.startswith("CREATE TABLE ") for p in parts[1:])
    with conn.transaction():
        for statement in parts:
            conn.execute(statement)


def main() -> int:
    assert os.getenv("TS_R3_NEON_CHILD_DSN") is None
    assert os.getenv("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI
    assert psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary"
    with closing(connect()) as conn:
        version = conn.execute("SHOW server_version").fetchone()["server_version"]
        assert version.startswith("16."), "POSTGRES16_REQUIRED"
        setup(conn)
        summary = {}
        for mode, scope in zip(("before","after"), SCOPES):
            initial, command = source(scope)
            assert initialize(conn, scope, initial).revision == 0
            # A dedicated real connection executes one original mutation.
            with closing(connect()) as writer:
                try:
                    apply(FaultConnection(writer, mode), command)
                except EffectUnknown:
                    pass
                else:
                    raise AssertionError("CLIENT_FAULT_DID_NOT_CAUSE_UNKNOWN")
            # NEW independent read-only client observes original attempt once.
            with closing(connect()) as observer:
                view = read(observer, scope)
                if mode == "before":
                    assert view.revision == 0 and view.event_bytes == b""
                    check_counts(observer, scope, 0)
                    try:
                        reconcile(observer, command)
                    except EffectUnknown:
                        # Absent receipt is UNKNOWN after dispatch; no retry.
                        pass
                    else:
                        raise AssertionError("ABSENT_RECEIPT_FALSE_NONE")
                    summary["before"] = "UNKNOWN_NO_RECEIPT_FENCED"
                else:
                    assert view.revision == 1 and view.last_event_hash is not None
                    assert view.event_bytes == command.event_line
                    assert view.state_bytes == command.state_bytes
                    check_counts(observer, scope, 1)
                    result = reconcile(observer, command)
                    assert result.disposition == "CONFIRMED" and result.replay
                    assert result.event_hash == view.last_event_hash
                    summary["after"] = "CONFIRMED_FROM_ORIGINAL_RECEIPT"
        assert set(summary) == {"before","after"}
        print(json.dumps({
            "status": "PG16_NATIVE_SYNTHETIC_CLIENT_ACK_UNCERTAINTY_FENCING_PASS",
            "original_mutations_dispatched": 2,
            "distinct_disposable_scopes": 2,
            "before_commit": summary["before"],
            "after_real_commit": summary["after"],
            "automatic_retry": False,
            "real_postgresql16_transactions": True,
            "network_packet_loss": "NOT_RUN",
            "neon_remote": "NOT_RUN",
            "product_effect": "NONE",
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
