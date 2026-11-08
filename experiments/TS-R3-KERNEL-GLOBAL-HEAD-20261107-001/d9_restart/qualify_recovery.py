"""D9 disposable local PostgreSQL restart/reconnect after TCP lost COMMIT response.

Separate process phases are invoked once by one GHA job. No remote Neon, secrets
or Product writes. Restart is tested by PostgreSQL postmaster start timestamp.
"""
from __future__ import annotations
from dataclasses import replace
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import time
import psycopg
from psycopg.rows import dict_row

from d8_ack_loss.qualify_tcp import DropCommitResponse, URI, ROOT, direct, require
from ts_global.bridge import Mutation, EffectUnknown, apply, initialize, read, reconcile

SCHEMA = "ts_r3_global_head_20261107_001"
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
ATTEMPT = os.environ.get("GITHUB_RUN_ATTEMPT", "")
SCOPE = f"ts-r3-d9-local-restart-{RUN_ID}-{ATTEMPT}"

def fixture_command(path):
    fixture = json.loads(Path(path).read_text(encoding="utf-8"))
    require(fixture.get("kind") == "PRODUCT_JS_V0_EXACT_GENERATIONS" and
            fixture.get("product_git_commit") == "26509b74d50207bb247dcc9bdb929a63f5451e88",
            "PRODUCT_ORACLE_FROZEN")
    generations = fixture["generations"]
    require(len(generations) == 20, "HISTORICAL_COUNT")
    b64 = lambda x: base64.b64decode(x, validate=True)
    command = Mutation(SCOPE, "d9-restart-once", 0, None,
                       b64(generations[1]["payload_b64"]),
                       b64(generations[1]["event_line_b64"]),
                       b64(generations[1]["state_b64"]),
                       sha256(b"D9_LOCAL_RESTART_NO_PRODUCT").hexdigest())
    return b64(generations[0]["state_b64"]), command

def before(fixture_path, marker_path):
    initial, command = fixture_command(fixture_path)
    with direct() as admin:
        require(admin.execute(
            "SELECT count(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
            (SCHEMA,)).fetchone()["n"] == 0, "SCHEMA_ALREADY_PRESENT")
        schema_text = (ROOT / "schema.sql").read_text(encoding="utf-8")
        statements = [p.strip() for p in "\n".join(
            line for line in schema_text.splitlines() if not line.lstrip().startswith("--")
        ).split(";") if p.strip()]
        require(len(statements) == 4, "SCHEMA_SHAPE")
        with admin.transaction():
            for statement in statements:
                admin.execute(statement)
        initial_state = initialize(admin, SCOPE, initial)
        require(initial_state.revision == 0, "GENESIS")
        original_postmaster = admin.execute(
            "SELECT pg_postmaster_start_time() AS started").fetchone()["started"].isoformat()

    proxy = DropCommitResponse()
    proxy_uri = URI.replace(":5432/", f":{proxy.port}/")
    try:
        with psycopg.connect(proxy_uri, autocommit=True, row_factory=dict_row,
                             connect_timeout=6) as writer:
            try:
                apply(writer, command)
            except EffectUnknown:
                pass
            else:
                raise AssertionError("ACK_NOT_LOST")
    finally:
        proxy.join()
    require(proxy.commit_response_suppressed.is_set(), "COMMIT_REPLY_NOT_SUPPRESSED")

    # Only test metadata; file has no database credentials or actual Product data.
    payload = {"scope": SCOPE, "run_id": RUN_ID, "run_attempt": ATTEMPT,
               "postmaster_before": original_postmaster,
               "expected_state_sha256": sha256(command.state_bytes).hexdigest(),
               "expected_events_sha256": sha256(command.event_line).hexdigest()}
    with Path(marker_path).open("x", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True)
    print(json.dumps({"status":"D9_BEFORE_COMMIT_REPLY_LOSS_PASS",
                      "client_effect":"UNKNOWN_FENCED","product_effect":"NONE"}))

def outage():
    started = time.monotonic()
    failed_connection = False
    try:
        with direct():
            pass
    except psycopg.OperationalError:
        failed_connection = True
    require(failed_connection, "PG_SERVICE_STILL_AVAILABLE_DURING_STOP")
    time.sleep(8)
    elapsed = round(time.monotonic() - started, 3)
    require(elapsed >= 8, "DISCONNECTION_WINDOW_TOO_SHORT")
    print(json.dumps({"status":"D9_DISCONNECTION_WINDOW_PASS",
                      "connection_refused": True, "outage_s": elapsed,
                      "product_effect": "NONE"}, sort_keys=True))

def after(fixture_path, marker_path, outage_path):
    _, command = fixture_command(fixture_path)
    marker = json.loads(Path(marker_path).read_text(encoding="utf-8"))
    downtime = json.loads(Path(outage_path).read_text(encoding="utf-8"))
    require(marker["scope"] == SCOPE and marker["run_id"] == RUN_ID and
            marker["run_attempt"] == ATTEMPT, "IDENTITY_DRIFT")
    require(downtime["status"] == "D9_DISCONNECTION_WINDOW_PASS" and
            downtime["outage_s"] >= 8 and downtime["connection_refused"], "OUTAGE_NOT_PROVEN")
    with direct() as observer:
        new_postmaster = observer.execute(
            "SELECT pg_postmaster_start_time() AS started").fetchone()["started"].isoformat()
        require(new_postmaster > marker["postmaster_before"], "NO_REAL_POSTGRESQL_RESTART")
        receipt = reconcile(observer, command)
        view = read(observer, SCOPE)
        require(receipt.disposition == "CONFIRMED" and receipt.replay and
                receipt.revision == 1, "RECONCILE_NOT_CONFIRMED")
        require(view.revision == 1 and view.state_bytes == command.state_bytes and
                view.event_bytes == command.event_line, "RESTORED_BYTES_MISMATCH")
        require(sha256(view.state_bytes).hexdigest() == marker["expected_state_sha256"] and
                sha256(view.event_bytes).hexdigest() == marker["expected_events_sha256"],
                "DURABILITY_HASH_MISMATCH")
        counts = observer.execute(
            f"SELECT (SELECT count(*) FROM {SCHEMA}.head) AS heads,"
            f" (SELECT count(*) FROM {SCHEMA}.events) AS events,"
            f" (SELECT count(*) FROM {SCHEMA}.receipts) AS receipts").fetchone()
        require(counts == {"heads": 1, "events": 1, "receipts": 1}, "DURABILITY_ROWS")
        with observer.transaction():
            observer.execute(f"DROP SCHEMA {SCHEMA} CASCADE")
        require(observer.execute(
            "SELECT count(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
            (SCHEMA,)).fetchone()["n"] == 0, "SQL_CLEANUP_FAILED")
    print(json.dumps({"status":"D9_LOCAL_PG_RESTART_AFTER_ACK_LOSS_PASS",
                      "original_effect":"UNKNOWN_FENCED", "after_restart":"CONFIRMED",
                      "restarted_postmaster": True, "outage_s":downtime["outage_s"],
                      "mutations_sent":1,"events":1,"receipts":1,
                      "state_sha256":marker["expected_state_sha256"],
                      "event_stream_sha256":marker["expected_events_sha256"],
                      "sql_cleanup":"PASS","remote_neon":"NOT_RUN",
                      "independent_hosts":"NOT_RUN","product_effect":"NONE"},sort_keys=True))

def main():
    require(RUN_ID.isdecimal() and ATTEMPT == "1", "NATIVE_RUN_IDENTITY")
    phase = sys.argv[1] if len(sys.argv)>1 else ""
    if phase == "before" and len(sys.argv) == 4:
        before(sys.argv[2], sys.argv[3])
    elif phase == "outage" and len(sys.argv) == 2:
        outage()
    elif phase == "after" and len(sys.argv) == 5:
        after(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise AssertionError("D9_PHASE_INVALID")

if __name__ == "__main__":
    main()
