#!/usr/bin/env python3
"""TS R3 A001 child-only psycopg3 read-only connection preflight.

Experimental NONPRODUCT. Never prints a DSN, password, SQL errors, or traceback.
No DDL/DML, no data changes, no Product or TaskCycle authority.
Native write/ACK-loss tests require distinct future reviewed attempts.
"""
from __future__ import annotations

import json
import os
import sys
from urllib.parse import parse_qs, unquote, urlsplit
import re

EXPECTED_HOST = "ep-lucky-waterfall-b6244mdy.c-2.sa-east-1.aws.neon.tech"
EXPECTED_ROLE = "tsr3_host_a_rw"
EXPECTED_DB = "ts_remote_r3"
EXPECTED_SCOPE = "scope-tsr3-ack-native-20261107-a01"
EXPECTED_APP = "tsr3-a001-readonly-c01"
SECRET_ENV = "TS_R3_NEON_CHILD_DSN"
MAX_DSN_CHARS = 4096


class BlockedPrecondition(ValueError):
    pass


def ensure(condition: bool, code: str) -> None:
    if not condition:
        raise BlockedPrecondition(code)


def validate_dsn(dsn: str) -> None:
    """Validate metadata only; never return, hash, log or echo any credential."""
    ensure(type(dsn) is str and 0 < len(dsn) <= MAX_DSN_CHARS, "NO_SECURE_DSN")
    ensure(all(ord(c) >= 32 for c in dsn), "UNSAFE_DSN_CHARACTER")
    parsed = urlsplit(dsn)
    ensure(parsed.scheme == "postgresql", "UNSUPPORTED_DSN_SCHEME")
    ensure(parsed.hostname == EXPECTED_HOST, "BRANCH_COMPUTE_HOST_MISMATCH")
    ensure("-pooler" not in parsed.hostname, "POOLED_ENDPOINT_FORBIDDEN")
    ensure(unquote(parsed.username or "") == EXPECTED_ROLE, "ROLE_MISMATCH")
    ensure(parsed.password is not None and bool(parsed.password), "MISSING_PASSWORD")
    # Malformed percent escapes can be decoded inconsistently by URL parsers.
    ensure(re.search(r"%(?![A-Fa-f0-9]{2})", parsed.password) is None,
           "MALFORMED_PASSWORD_ESCAPING")
    ensure(bool(unquote(parsed.password)), "EMPTY_DECODED_PASSWORD")
    ensure(chr(0) not in unquote(parsed.password), "PASSWORD_CONTAINS_NUL")
    ensure(parsed.path == "/" + EXPECTED_DB, "DATABASE_MISMATCH")
    ensure(parsed.port in (None, 5432), "INVALID_PORT")
    ensure(not parsed.fragment, "UNEXPECTED_FRAGMENT")
    options = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
    ensure(set(options).issubset({"sslmode", "channel_binding"}), "UNEXPECTED_DSN_OPTION")
    ensure(len(options.get("sslmode", [])) == 1 and
           options["sslmode"][0] in ("require", "verify-ca", "verify-full"),
           "TLS_REQUIRED")
    # Absence is NOT equivalent to libpq's explicit channel_binding=require.
    ensure(len(options.get("channel_binding", [])) == 1 and
           options["channel_binding"][0] == "require",
           "CHANNEL_BINDING_NOT_STRICT")


def self_test() -> None:
    stem = (
        "postgresql://" + EXPECTED_ROLE + ":fake-only-placeholder@"
        + EXPECTED_HOST + "/" + EXPECTED_DB
    )
    validate_dsn(stem + "?sslmode=require&channel_binding=require")
    validate_dsn(stem + "?sslmode=verify-full&channel_binding=require")
    validate_dsn(stem.replace("fake-only-placeholder",
             "encoded%40colon%3Aslash%2Fpercent%25") +
             "?sslmode=verify-full&channel_binding=require")
    valid_suffix = "?sslmode=require&channel_binding=require"
    invalid = (
        # Missing channel_binding was the independent F001 false accept.
        stem + "?sslmode=require",
        stem + "?sslmode=verify-full",
        stem.replace(EXPECTED_HOST, EXPECTED_HOST.replace("ep-", "ep-other-", 1))
            + valid_suffix,
        stem.replace(EXPECTED_ROLE, "tsr3_owner", 1) + valid_suffix,
        stem.replace(EXPECTED_HOST, EXPECTED_HOST.replace(".c-2.", "-pooler.c-2.", 1))
            + valid_suffix,
        stem + "?sslmode=disable&channel_binding=require",
        stem + "?sslmode=require&sslmode=disable&channel_binding=require",
        stem + "?sslmode=require&options=superuser&channel_binding=require",
        stem + "?sslmode=require&channel_binding=disable",
        stem + "?sslmode=require&channel_binding=prefer",
        stem + "?sslmode=require&channel_binding=",
        stem + "?sslmode=require&channel_binding=require&channel_binding=prefer",
        stem.replace("/" + EXPECTED_DB, "/postgres") + valid_suffix,
        stem.replace("fake-only-placeholder", "broken%escape") + valid_suffix,
        stem.replace("fake-only-placeholder", "%00") + valid_suffix,
        stem.replace("fake-only-placeholder", "") + valid_suffix,
        stem + "?sslmode=require&channel_binding=require&application_name=other",
    )
    for case in invalid:
        try:
            validate_dsn(case)
        except (BlockedPrecondition, ValueError):
            continue
        raise AssertionError("MALFORMED_DSN_ACCEPTED")


def qualify() -> dict[str, object]:
    ensure(sys.version_info[:3] == (3, 15, 2), "PYTHON_VERSION_MISMATCH")
    # No import or DB action occurs before a usable secret is provided.
    dsn = os.environ.get(SECRET_ENV, "")
    validate_dsn(dsn)
    import psycopg
    from psycopg.rows import dict_row

    ensure(psycopg.__version__ == "3.3.8", "PSYCOPG_VERSION_MISMATCH")
    ensure(psycopg.pq.__impl__ == "binary", "PSYCOPG_BINARY_REQUIRED")
    connection = None
    try:
        connection = psycopg.connect(
            dsn, autocommit=True, row_factory=dict_row,
            connect_timeout=10, application_name=EXPECTED_APP,
        )
        ensure(connection.info.transaction_status.name == "IDLE",
               "NOT_TOP_LEVEL_IDLE")
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(
                    """
                    SELECT current_database() AS database_name,
                           current_user AS role_name,
                           current_setting('server_version_num')::int AS version_num,
                           current_setting('transaction_isolation') AS isolation,
                           s.ssl AS tls_in_use,
                           has_schema_privilege(
                               current_user, 'ts_r3_global_head_20261107_001',
                               'USAGE') AS schema_use,
                           has_database_privilege(
                               current_user, current_database(), 'CREATE'
                           ) AS db_create,
                           has_table_privilege(
                               current_user,
                               'ts_r3_global_head_20261107_001.head',
                               'UPDATE') AS head_update,
                           (SELECT count(*) FROM
                            ts_r3_global_head_20261107_001.head
                            WHERE scope=%s) AS head_count,
                           (SELECT count(*) FROM
                            ts_r3_global_head_20261107_001.events
                            WHERE scope=%s) AS event_count,
                           (SELECT count(*) FROM
                            ts_r3_global_head_20261107_001.receipts
                            WHERE scope=%s) AS receipt_count
                    FROM pg_stat_ssl s WHERE s.pid=pg_backend_pid()
                    """,
                    (EXPECTED_SCOPE, EXPECTED_SCOPE, EXPECTED_SCOPE),
                )
                row = cursor.fetchone()
                ensure(row is not None, "NO_TLS_SESSION_ROW")
                ensure(set(row) == {
                    "database_name", "role_name", "version_num", "isolation",
                    "tls_in_use", "schema_use", "db_create", "head_update",
                    "head_count", "event_count", "receipt_count",
                }, "UNEXPECTED_DB_RESULT")
                ensure(row["database_name"] == EXPECTED_DB and
                       row["role_name"] == EXPECTED_ROLE, "DB_IDENTITY_MISMATCH")
                ensure(160000 <= row["version_num"] < 170000,
                       "POSTGRES_16_REQUIRED")
                ensure(row["isolation"] == "read committed", "ISOLATION_MISMATCH")
                ensure(row["tls_in_use"] is True, "TLS_INACTIVE")
                ensure(row["schema_use"] is True and
                       row["head_update"] is True and
                       row["db_create"] is False, "DB_PRIVILEGE_MISMATCH")
                ensure(tuple(row[k] for k in (
                    "head_count", "event_count", "receipt_count",
                )) == (0, 0, 0), "NEW_SCOPE_NOT_EMPTY")
        ensure(connection.info.transaction_status.name == "IDLE",
               "TRANSACTION_NOT_CLOSED")
    finally:
        if connection is not None:
            connection.close()
    return {
        "schema": "ts-r3-a001-psycopg-readonly-preflight/v1",
        "status": "PASS_READ_ONLY",
        "python": "3.15.2",
        "psycopg": "3.3.8",
        "db": EXPECTED_DB,
        "role": EXPECTED_ROLE,
        "postgres": "16",
        "host_match": True,
        "tls": True,
        "scope": EXPECTED_SCOPE,
        "head_events_receipts": [0, 0, 0],
        "product_effect": "NONE",
        "network_commit_ack_test": "NOT_RUN",
    }


def main(args: list[str]) -> int:
    if args == ["--self-test"]:
        self_test()
        print(json.dumps({"status": "PASS_DSN_METADATA_SELFTEST", "network": "NOT_RUN"}))
        return 0
    if args:
        print('{"status":"BLOCKED_UNEXPECTED_ARGUMENTS"}')
        return 2
    try:
        result = qualify()
    except Exception as exc:
        # Never print exception text: libpq and provider failures can carry DSNs.
        print(json.dumps({"status": "BLOCKED_PRECONDITION",
                          "error_type": type(exc).__name__,
                          "product_effect": "NONE"}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
