"""D4: actual PostgreSQL16 two-client row-lock contention on disposable localhost.

This test NEVER uses Neon, real environment credentials, Product, or TaskCycle authority.
It pins an exact synthetic local-only URI and reads frozen JS bytes from golden.json.
"""
from __future__ import annotations

from base64 import b64decode
from contextlib import contextmanager, closing
from dataclasses import replace
import json
import os
from pathlib import Path
import threading
import time

import psycopg
from psycopg.rows import dict_row
from ts_global.bridge import (
    Mutation, StorageRejected, apply, initialize, read, reconcile
)

SYNTHETIC_URI = (
    "postgresql://tsr3_d4_synthetic:d4_test_only_never_external"
    "@127.0.0.1:5432/tsr3_d4_synthetic?sslmode=disable"
)
ROOT = Path(__file__).resolve().parent.parent
SCOPE = "ts-r3-d4-real-pg-local-20261107-001"


class HoldCursor:
    def __init__(self, underlying, held: threading.Event, release: threading.Event):
        self.underlying = underlying
        self.held = held
        self.release = release
        self.hold_once = True

    def execute(self, sql, params=()):
        result = self.underlying.execute(sql, params)
        if self.hold_once and "FOR UPDATE" in sql:
            self.hold_once = False
            self.held.set()  # PostgreSQL acquired global-head row lock now.
            if not self.release.wait(timeout=10.0):
                raise RuntimeError("SYNTHETIC_LOCK_RELEASE_TIMEOUT")
        return result

    def fetchone(self):
        return self.underlying.fetchone()

    def fetchall(self):
        return self.underlying.fetchall()


class HoldConnection:
    def __init__(self, raw, held: threading.Event, release: threading.Event):
        self.raw, self.held, self.release = raw, held, release
        self.autocommit = raw.autocommit
        self.info = raw.info

    def transaction(self):
        return self.raw.transaction()

    @contextmanager
    def cursor(self):
        with self.raw.cursor() as cur:
            yield HoldCursor(cur, self.held, self.release)


def connect():
    return psycopg.connect(
        SYNTHETIC_URI, autocommit=True, row_factory=dict_row,
        connect_timeout=5, application_name="ts-r3-d4-synthetic-local"
    )


def first_mutation() -> Mutation:
    golden = json.loads((ROOT / "oracle" / "golden.json").read_text(encoding="utf-8"))
    item = golden["mutations"][0]
    return Mutation(
        scope=SCOPE,
        mutation_id="d4-first-writer-synthetic-a",
        expected_revision=item["expected_revision"],
        previous_event_hash=item["previous_event_hash"],
        payload_bytes=b64decode(item["payload_b64"], validate=True),
        event_line=b64decode(item["line_b64"], validate=True),
        state_bytes=b64decode(item["state_b64"], validate=True),
        authority_fingerprint=item["authority_fingerprint"],
    )


def setup(conn):
    raw_sql = (ROOT / "schema.sql").read_text(encoding="utf-8")
    # Fixed source schema contains a semicolon in an initial SQL comment.
    # Discard standalone "--" line comments before the bounded DDL splitter.
    ddl = "\n".join(
        line for line in raw_sql.splitlines()
        if not line.lstrip().startswith("--")
    )
    statements = [stmt.strip() for stmt in ddl.split(";") if stmt.strip()]
    assert len(statements) == 4, "FROZEN_SCHEMA_FOUR_DDL_STATEMENTS"
    assert statements[0].startswith("CREATE SCHEMA ")
    assert all(stmt.startswith("CREATE TABLE ") for stmt in statements[1:])
    with conn.transaction():
        for statement in statements:
            conn.execute(statement)
    golden = json.loads((ROOT / "oracle" / "golden.json").read_text(encoding="utf-8"))
    initial = b64decode(golden["genesis_b64"], validate=True)
    result = initialize(conn, SCOPE, initial)
    assert result.revision == 0
    assert read(conn, SCOPE).event_bytes == b""


def main() -> int:
    assert os.environ.get("TS_R3_NEON_CHILD_DSN") is None, "NEON_SECRET_NOT_ALLOWED"
    assert os.environ.get("TS_R3_LOCAL_SYNTHETIC_PG_URI") == SYNTHETIC_URI, (
        "LOCAL_TEST_URI_NOT_PINNED"
    )
    assert psycopg.__version__ == "3.3.8"
    assert psycopg.pq.__impl__ == "binary"
    with closing(connect()) as admin, closing(connect()) as a, closing(connect()) as b:
        version = admin.execute("SHOW server_version").fetchone()["server_version"]
        assert version.startswith("16."), "POSTGRESQL16_REQUIRED"
        setup(admin)
        command_a = first_mutation()
        command_b = replace(command_a, mutation_id="d4-second-writer-synthetic-b")
        assert command_a.expected_revision == 0
        assert command_b.expected_revision == 0
        assert command_a.fingerprint() != command_b.fingerprint()

        held = threading.Event()
        release = threading.Event()
        results: dict[str, object] = {}
        errors: dict[str, BaseException] = {}

        def client_a():
            try:
                results["A"] = apply(HoldConnection(a, held, release), command_a)
            except BaseException as exc:
                errors["A"] = exc

        def client_b():
            try:
                results["B"] = apply(b, command_b)
            except StorageRejected as exc:
                results["B_REJECT_CODE"] = exc.code
            except BaseException as exc:
                errors["B"] = exc

        ta = threading.Thread(target=client_a, name="synthetic-writer-a", daemon=True)
        tb = threading.Thread(target=client_b, name="synthetic-writer-b", daemon=True)
        ta.start()
        assert held.wait(timeout=10.0), "A_LOCK_NOT_ACQUIRED"
        tb.start()
        observed_lock = False
        wait_label = None
        try:
            deadline = time.monotonic() + 6.0
            while time.monotonic() < deadline:
                row = admin.execute(
                    "SELECT wait_event_type,wait_event,pg_blocking_pids(pid) AS blockers "
                    "FROM pg_stat_activity WHERE pid=%s",
                    (b.info.backend_pid,),
                ).fetchone()
                if (row and row["wait_event_type"] == "Lock"
                        and row["wait_event"] in ("transactionid", "tuple")
                        and a.info.backend_pid in row["blockers"]):
                    observed_lock = True
                    wait_label = row["wait_event"]
                    break
                time.sleep(0.08)
        finally:
            release.set()
        ta.join(timeout=12)
        tb.join(timeout=12)
        assert not ta.is_alive() and not tb.is_alive(), "CLIENT_JOIN_TIMEOUT"
        assert not errors, "CLIENT_FAILED"
        assert observed_lock, "TWO_CLIENT_PHYSICAL_LOCK_CONTENTION_NOT_OBSERVED"
        assert results["A"].disposition == "CONFIRMED"
        assert results["A"].replay is False and results["A"].revision == 1
        assert results.get("B_REJECT_CODE") == "STALE_REVISION", results
        view = read(admin, SCOPE)
        assert view.revision == 1 and view.last_event_hash == results["A"].event_hash
        receipt = reconcile(admin, command_a)
        assert receipt.disposition == "CONFIRMED" and receipt.replay is True
        counts = admin.execute(
            "SELECT (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.events "
            " WHERE scope=%s) AS events, "
            "(SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.receipts "
            " WHERE scope=%s) AS receipts",
            (SCOPE, SCOPE),
        ).fetchone()
        assert counts == {"events": 1, "receipts": 1}, counts
        b_receipts = admin.execute(
            "SELECT COUNT(*) AS count FROM ts_r3_global_head_20261107_001.receipts "
            "WHERE scope=%s AND mutation_id=%s",
            (SCOPE, command_b.mutation_id),
        ).fetchone()
        assert b_receipts["count"] == 0
        print(json.dumps({
            "status": "PG16_NATIVE_TWO_PSYCOGP_CLIENT_SESSIONS_LOCK_CAS_PASS",
            "postgresql_major": 16,
            "actual_client_sessions": 2,
            "additional_readonly_observer": 1,
            "physical_lock_wait_observed": observed_lock,
            "verified_blocker_pid_is_A": observed_lock,
            "lock_wait_event": wait_label,
            "global_head_revision": view.revision,
            "event_count": counts["events"],
            "receipt_count": counts["receipts"],
            "writer_a": "CONFIRMED",
            "writer_b": "NONE_STALE_REVISION",
            "nonprimary_disposable_local_db": True,
            "remote_neon": "NOT_RUN",
            "two_hosts": "NOT_RUN",
            "product_effect": "NONE",
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
