"""A02-LAN: one fresh PG16 server, two physical client hosts, exact JS CAS.

NONPRODUCT, synthetic-only. No Neon/production DSN and no Product authority.
All inputs are frozen before effect; receipt and JSON stream contain no secrets.
Do not retry a possible-dispatch failure. Host orchestration owns join/fencing.
"""
from __future__ import annotations

import base64
from hashlib import sha256, sha1
import json
import os
import platform
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a11_real_pg16_port.worker import SCOPE, parse_proposal  # exact original A11 parser
from ts_global.bridge import (
    EffectUnknown, StorageRejected, initialize, read, apply, reconcile,
)

import psycopg
from psycopg.rows import dict_row

SCHEMA = "ts_r3_global_head_20261107_001"
PACKET_SCHEMA = "TS_R3_A02_LAN_PROPOSALS_V1"
FROZEN_SCHEMA_GIT_BLOB = "3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0"
DATABASE = "tsr3_a02_lab"
ROLE = "tsr3_a02_lab"
URI_ENV = "TS_R3_A02_LAN_PG_URI"
SHA_ENV = "TS_R3_A02_PACKET_SHA256"
MODE_NAMES = {"validate", "setup", "hold", "writer-a", "writer-b",
              "witness", "verify", "reconcile-a", "reconcile-b"}
STAGE = "ENTRY"


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def strict_packet(filepath: str):
    path = Path(filepath).resolve(strict=True)
    require(path.is_file() and path.stat().st_size < 6 * 1024 * 1024,
            "ARTIFACT_FILE_BOUND")
    data = path.read_bytes()
    expected = os.getenv(SHA_ENV, "")
    require(re.fullmatch(r"[a-f0-9]{64}", expected) is not None,
            "FROZEN_ARTIFACT_HASH_REQUIRED")
    require(sha256(data).hexdigest() == expected, "ARTIFACT_HASH_MISMATCH")
    request = json.loads(data.decode("utf-8", "strict"))
    require(type(request) is dict and set(request) == {
        "schema", "scope", "source", "product_effect",
        "expected_revision_before", "expected_revision_after",
        "genesis_state", "genesis_sha256", "a", "b",
    }, "PACKET_EXACT_KEYS")
    require(request["schema"] == PACKET_SCHEMA and request["scope"] == SCOPE,
            "WRONG_PACKET_SCHEMA_OR_SCOPE")
    require(request["source"] == "FROZEN_ORIGINAL_PRODUCT_V0_JS_VIA_A10_SHADOW"
            and request["product_effect"] == "NONE"
            and type(request["expected_revision_before"]) is int
            and request["expected_revision_before"] == 0
            and type(request["expected_revision_after"]) is int
            and request["expected_revision_after"] == 1, "UNEXPECTED_TEST_CLAIM")
    genesis = base64.b64decode(request["genesis_state"], validate=True)
    require(sha256(genesis).hexdigest() == request["genesis_sha256"],
            "GENESIS_SHA_MISMATCH")
    commands = {}
    for side in ("a", "b"):
        proposal = request[side]
        require(type(proposal) is dict and set(proposal) == {
            "scope", "mutationId", "fingerprint", "expectedRevision",
            "expectedEpoch", "previousEventHash", "eventHash",
            "stateBytes", "eventLine", "stateSha256", "eventLineSha256",
        }, "PROPOSAL_EXACT_KEYS")
        command, meta = parse_proposal(proposal)
        require(command.scope == SCOPE and command.expected_revision == 0 and
                command.previous_event_hash is None, "NOT_COMPETING_GENESIS")
        require(command.mutation_id == "A10-A02-LAN-" + side.upper(),
                "WRONG_MUTATION_ID")
        require(sha256(command.state_bytes).hexdigest() ==
                proposal["stateSha256"] and
                sha256(command.event_line).hexdigest() ==
                proposal["eventLineSha256"], "PROPOSAL_SHA_MISMATCH")
        commands[side] = command
    require(commands["a"].payload_bytes != commands["b"].payload_bytes and
            commands["a"].mutation_id != commands["b"].mutation_id,
            "DIFFERENT_EVENTS_REQUIRED")
    return request, genesis, commands


def preflight_runtime() -> None:
    require(sys.version_info[:3] == (3, 15, 2), "PY3152_REQUIRED")
    require(psycopg.__version__ == "3.3.8" and
            psycopg.pq.__impl__ == "binary", "PSYCOPG338_BINARY_REQUIRED")
    for key in ("TS_R3_NEON_CHILD_DSN", "TS_R3_NEON_CHILD_RO_DSN",
                "DATABASE_URL", "PGPASSWORD"):
        require(not os.getenv(key), "FOREIGN_CREDENTIAL_FORBIDDEN")


def asserted_host_identity():
    # Host hash must be frozen by native Control observation, never invented by
    # application_name, Tailscale address or caller-declared SITE alone.
    observed = sha256(platform.node().strip().casefold().encode("utf-8")).hexdigest()
    expected = os.getenv("TS_R3_A02_EXPECTED_HOST_SHA256", "")
    require(re.fullmatch(r"[a-f0-9]{64}", expected) is not None and
            observed == expected, "NATIVE_HOST_ATTESTATION_MISMATCH")
    attempt = os.getenv("TS_R3_A02_EXECUTION_ATTEMPT")
    require(attempt == "TS-R3-A02-LAN-PHYSICAL-RACE-20261109-001-A001",
            "FROZEN_EXECUTION_ATTEMPT_REQUIRED")
    return observed, attempt


def site_uri():
    side = os.getenv("TS_R3_A02_SITE")
    require(side in ("NOTEBOOK", "DESKTOP"), "EXACT_PHYSICAL_SITE_REQUIRED")
    asserted_host_identity()
    uri = os.getenv(URI_ENV, "")
    require(uri.startswith("postgresql://") and len(uri) < 400,
            "EXACT_SYNTHETIC_URI_REQUIRED")
    p = urlsplit(uri)
    require(p.scheme == "postgresql" and p.username == ROLE and
            p.password is not None and len(p.password) >= 24 and
            p.path == "/" + DATABASE and p.fragment == "",
            "SYNTHETIC_ROLE_DB_REQUIRED")
    host_port = ("127.0.0.1", 55433) if side == "NOTEBOOK" else ("100.64.164.4", 55434)
    require((p.hostname, p.port) == host_port, "UNEXPECTED_HOST_OR_PORT")
    require(parse_qs(p.query, keep_blank_values=True) == {"sslmode": ["disable"]},
            "NO_AMBIENT_CONNECTION_OPTIONS")
    return uri, side


def connect(mode: str):
    preflight_runtime()
    uri, site = site_uri()
    cn = psycopg.connect(
        uri, autocommit=True, row_factory=dict_row, connect_timeout=5,
        application_name="ts-a02-lan-" + mode,
    )
    require(cn.execute("SHOW server_version").fetchone()["server_version"].startswith("16."),
            "PG16_REQUIRED")
    ident = cn.execute("SELECT current_database() AS db,current_user AS user").fetchone()
    require(ident == {"db": DATABASE, "user": ROLE}, "SYNTHETIC_DB_ROLE_MISMATCH")
    expected_system_id = os.getenv("TS_R3_A02_EXPECTED_SYSTEM_IDENTIFIER", "")
    require(re.fullmatch(r"[0-9]{16,20}", expected_system_id) is not None,
            "EXTERNAL_DB_SYSTEM_ID_ATTESTATION_REQUIRED")
    system = cn.execute(
        "SELECT system_identifier::text AS id FROM pg_catalog.pg_control_system()"
    ).fetchone()
    require(system is not None and system["id"] == expected_system_id,
            "DISPOSABLE_SERVER_ID_MISMATCH")
    return cn, site


def user_schemas(conn):
    rows = conn.execute(
        "SELECT nspname FROM pg_catalog.pg_namespace "
        "WHERE nspname <> 'information_schema' "
        "AND nspname NOT LIKE 'pg\\_%' ESCAPE '\\' ORDER BY nspname"
    ).fetchall()
    return [row["nspname"] for row in rows]


def assert_fresh_disposable_catalog(conn):
    """Never create schema in a database with foreign user objects or roles."""
    require(user_schemas(conn) == ["public"], "FOREIGN_USER_SCHEMA_PRESENT")
    checks = (
        ("FOREIGN_PUBLIC_RELATION",
         "SELECT COUNT(*) AS n FROM pg_catalog.pg_class c "
         "JOIN pg_catalog.pg_namespace ns ON ns.oid=c.relnamespace "
         "WHERE ns.nspname='public'"),
        ("FOREIGN_PUBLIC_FUNCTION",
         "SELECT COUNT(*) AS n FROM pg_catalog.pg_proc p "
         "JOIN pg_catalog.pg_namespace ns ON ns.oid=p.pronamespace "
         "WHERE ns.nspname='public'"),
        ("FOREIGN_PUBLIC_TYPE",
         "SELECT COUNT(*) AS n FROM pg_catalog.pg_type t "
         "JOIN pg_catalog.pg_namespace ns ON ns.oid=t.typnamespace "
         "WHERE ns.nspname='public'"),
        ("FOREIGN_PUBLIC_OPERATOR",
         "SELECT COUNT(*) AS n FROM pg_catalog.pg_operator p "
         "JOIN pg_catalog.pg_namespace ns ON ns.oid=p.oprnamespace "
         "WHERE ns.nspname='public'"),
        ("FOREIGN_PUBLIC_TRIGGER",
         "SELECT COUNT(*) AS n FROM pg_catalog.pg_trigger t "
         "JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid "
         "JOIN pg_catalog.pg_namespace ns ON ns.oid=c.relnamespace "
         "WHERE ns.nspname='public' AND NOT t.tgisinternal"),
    )
    for code, query in checks:
        row = conn.execute(query).fetchone()
        require(type(row["n"]) is int and row["n"] == 0, code)
    extensions = [r["extname"] for r in conn.execute(
        "SELECT extname FROM pg_catalog.pg_extension ORDER BY extname").fetchall()]
    require(extensions == ["plpgsql"], "FOREIGN_EXTENSION_PRESENT")
    roles = [r["rolname"] for r in conn.execute(
        "SELECT rolname FROM pg_catalog.pg_roles "
        "WHERE rolname NOT LIKE 'pg\\_%' ESCAPE '\\' ORDER BY rolname").fetchall()]
    require(set(roles) in ({ROLE}, {ROLE, "postgres"}) and
            len(roles) == len(set(roles)), "FOREIGN_DATABASE_ROLE_PRESENT")
    databases = [r["datname"] for r in conn.execute(
        "SELECT datname FROM pg_catalog.pg_database "
        "WHERE NOT datistemplate ORDER BY datname").fetchall()]
    require(databases == ["postgres", DATABASE], "FOREIGN_DATABASE_PRESENT")


def pinned_schema_statements():
    raw = (ROOT / "schema.sql").read_bytes()
    git_blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(git_blob == FROZEN_SCHEMA_GIT_BLOB, "FROZEN_SCHEMA_GIT_BLOB_MISMATCH")
    sql = raw.decode("utf-8", "strict")
    statements = [item.strip() for item in "\n".join(
        line for line in sql.splitlines()
        if not line.lstrip().startswith("--")
    ).split(";") if item.strip()]
    prefixes = (
        "CREATE SCHEMA " + SCHEMA,
        "CREATE TABLE " + SCHEMA + ".head (",
        "CREATE TABLE " + SCHEMA + ".events (",
        "CREATE TABLE " + SCHEMA + ".receipts (",
    )
    require(len(statements) == 4 and statements[0] == prefixes[0] and
            all(statements[i].startswith(prefixes[i]) for i in (1,2,3)),
            "PINNED_SCHEMA_DDL_SHAPE")
    return statements


def setup(conn, genesis):
    assert_fresh_disposable_catalog(conn)
    require(conn.execute(
        "SELECT COUNT(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
        (SCHEMA,)).fetchone()["n"] == 0, "DISPOSABLE_SCHEMA_ALREADY_EXISTS")
    statements = pinned_schema_statements()
    with conn.transaction():
        for item in statements:
            conn.execute(item)
    tables = conn.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename",
        (SCHEMA,)).fetchall()
    require([r["tablename"] for r in tables] == ["events", "head", "receipts"],
            "DISPOSABLE_SCHEMA_SHAPE")
    result = initialize(conn, SCOPE, genesis)
    require(result.revision == 0, "INITIALIZED_REVISION")
    state = read(conn, SCOPE)
    require(state.revision == 0 and state.state_bytes == genesis and
            len(state.event_bytes) == 0, "GENESIS_READBACK_MISMATCH")
    print(json.dumps({
        "status":"A02_LAN_DISPOSABLE_GENESIS_CONFIRMED",
        "revision":0,"physical_site":"NOTEBOOK","product_effect":"NONE",
        "neon":"NOT_RUN","schema":SCHEMA,
    }, sort_keys=True), flush=True)


def holder(conn):
    require(user_schemas(conn) == ["public", SCHEMA], "SCHEMA_NOT_EXACT")
    with conn.transaction():
        row = conn.execute(
            f"SELECT revision FROM {SCHEMA}.head WHERE scope=%s FOR UPDATE",
            (SCOPE,)).fetchone()
        require(row is not None and row["revision"] == 0, "HOLDER_EXPECTS_REVISION_ZERO")
        print(json.dumps({"status":"A02_LAN_HOLDER_LOCK_ACQUIRED",
                          "backend_pid":conn.info.backend_pid,
                          "scope":SCOPE,"hold_seconds":45,
                          "product_effect":"NONE"},sort_keys=True),flush=True)
        time.sleep(45)
    print("A02_LAN_HOLDER_RELEASED_NO_MUTATION", flush=True)


def writer(conn, command, site, side):
    require((site, side) in (("NOTEBOOK", "a"), ("DESKTOP", "b")),
            "PHYSICAL_SITE_WRITER_MISMATCH")
    try:
        result = apply(conn, command)
        require(result.disposition == "CONFIRMED", "NOT_CONFIRMED")
        output = {"disposition":"CONFIRMED", "effect":"CONFIRMED",
                  "revision":result.revision}
    except EffectUnknown:
        output = {"disposition":"UNKNOWN_FENCED", "effect":"UNKNOWN"}
    except StorageRejected as err:
        require(err.code == "STALE_REVISION", "UNEXPECTED_STORAGE_REJECTION")
        output = {"disposition":"NONE_STALE", "effect":"NONE"}
    output.update({"status":"A02_LAN_WRITER_RESULT","writer":side.upper(),
                   "site":site,"backend_pid":conn.info.backend_pid,
                   "mutation_id":command.mutation_id,
                   "product_effect":"NONE"})
    print(json.dumps(output, sort_keys=True), flush=True)


def witness(conn, expected_holder):
    require(type(expected_holder) is int and expected_holder > 0,
            "HOLDER_PID_REQUIRED")
    deadline = time.monotonic() + 24.0
    observed = None
    while time.monotonic() < deadline:
        rows = conn.execute(
            "SELECT pid, application_name, wait_event_type, wait_event,"
            "pg_blocking_pids(pid) AS blockers FROM pg_catalog.pg_stat_activity "
            "WHERE datname=current_database() AND "
            "application_name IN ('ts-a02-lan-writer-a','ts-a02-lan-writer-b') "
            "ORDER BY application_name"
        ).fetchall()
        if len(rows) == 2 and all(
            row["wait_event_type"] == "Lock" and row["blockers"]
            and type(row["pid"]) is int for row in rows
        ) and any(expected_holder in row["blockers"] for row in rows):
            observed = [{
                "writer": "A" if r["application_name"].endswith("-a") else "B",
                "pid":r["pid"],"wait_event_type":r["wait_event_type"],
                "wait_event":r["wait_event"],"blockers":r["blockers"],
            } for r in rows]
            require(observed[0]["pid"] != observed[1]["pid"],
                    "DISTINCT_SERVER_BACKENDS_REQUIRED")
            break
        time.sleep(0.1)
    require(observed is not None, "TRUE_TWO_WRITER_LOCK_GRAPH_NOT_OBSERVED")
    print(json.dumps({
        "status":"A02_LAN_TWO_PHYSICAL_HOST_WRITERS_BLOCKED_PROVEN",
        "expected_holder":expected_holder,
        "observer_pid":conn.info.backend_pid,
        "waiters":observed,
        "neon":"NOT_RUN","product_effect":"NONE",
    },sort_keys=True),flush=True)


def verify(conn, packet, commands):
    state = read(conn, SCOPE)
    require(state.revision == 1, "SINGLE_CAS_REVISION_REQUIRED")
    row = conn.execute(
        f"SELECT "
        f"(SELECT COUNT(*) FROM {SCHEMA}.head WHERE scope=%s) AS heads,"
        f"(SELECT COUNT(*) FROM {SCHEMA}.events WHERE scope=%s) AS events,"
        f"(SELECT COUNT(*) FROM {SCHEMA}.receipts WHERE scope=%s) AS receipts",
        (SCOPE,SCOPE,SCOPE)
    ).fetchone()
    require(row == {"heads":1,"events":1,"receipts":1},
            "ONE_WINNER_NO_DUPLICATE_POSTCONDITIONS")
    wins = [key for key in ("a","b")
            if state.state_bytes == commands[key].state_bytes and
            state.event_bytes == commands[key].event_line]
    require(len(wins) == 1, "EXACT_JS_EVENT_BYTES_PARITY_FAILED")
    print(json.dumps({
        "status":"A02_LAN_SINGLE_WINNER_POSTGRES16_PASS",
        "winner":wins[0].upper(),"revision":state.revision,
        "counts":row,
        "state_sha256":sha256(state.state_bytes).hexdigest(),
        "event_sha256":sha256(state.event_bytes).hexdigest(),
        "product_js_bytes_exact":True,
        "product_effect":"NONE","neon":"NOT_RUN",
    },sort_keys=True),flush=True)


def main():
    global STAGE
    STAGE = "ARGS"
    require(len(sys.argv) in (3,4) and sys.argv[1] in MODE_NAMES,
            "MODE_AND_PACKET_REQUIRED")
    mode = sys.argv[1]
    STAGE = "SOURCE_VALIDATE"
    preflight_runtime()
    packet, genesis, commands = strict_packet(sys.argv[2])
    if mode == "validate":
        print(json.dumps({
            "status":"A02_LAN_SOURCE_ONLY_PACKET_PASS",
            "packet_sha256":sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),
            "mutations":2,"revision":0,"database":"NOT_RUN",
            "product_effect":"NONE","neon":"NOT_RUN",
        },sort_keys=True))
        return
    STAGE = "DB_CONNECT"
    conn, site = connect(mode)
    try:
        STAGE = "OPERATION"
        if mode == "setup":
            require(site == "NOTEBOOK", "SETUP_NOTEBOOK_ONLY")
            setup(conn, genesis)
        elif mode == "hold":
            require(site == "NOTEBOOK", "HOLDER_NOTEBOOK_ONLY")
            holder(conn)
        elif mode in ("writer-a","writer-b"):
            side = mode[-1]
            writer(conn, commands[side], site, side)
        elif mode == "witness":
            require(site == "NOTEBOOK" and len(sys.argv) == 4 and
                    sys.argv[3].isdecimal(), "OBSERVER_ARGS_REQUIRED")
            witness(conn, int(sys.argv[3]))
        elif mode == "verify":
            require(site == "NOTEBOOK", "VERIFY_NOTEBOOK_ONLY")
            verify(conn, packet, commands)
        elif mode in ("reconcile-a","reconcile-b"):
            command = commands[mode[-1]]
            try:
                receipt = reconcile(conn, command)
                print(json.dumps({
                    "status":"A02_LAN_ORIGINAL_ID_READONLY_RECONCILED",
                    "writer":mode[-1].upper(),
                    "disposition":receipt.disposition,"revision":receipt.revision,
                    "product_effect":"NONE",
                },sort_keys=True))
            except EffectUnknown:
                print("A02_LAN_ABSENT_RECEIPT_STILL_UNKNOWN",flush=True)
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Never log SQL, DSN, passwords, sensitive stack or arbitrary stdout.
        kind = type(exc).__name__
        if kind not in {"AssertionError","ValueError","TypeError",
                        "StorageRejected","EffectUnknown","OperationalError",
                        "ProgrammingError","InvalidPassword","ConnectionTimeout"}:
            kind = "OTHER"
        stage = STAGE if STAGE in {"ARGS","SOURCE_VALIDATE","DB_CONNECT","OPERATION"} else "UNKNOWN"
        print("A02_LAN_FAIL_" + stage + "_" + kind.upper(),file=sys.stderr)
        raise SystemExit(2)
