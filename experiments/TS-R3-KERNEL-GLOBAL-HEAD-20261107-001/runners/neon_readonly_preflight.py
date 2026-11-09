#!/usr/bin/env python3
"""TS R3 A001 child-only psycopg3 read-only connection preflight.

Experimental NONPRODUCT. Never prints a DSN, password, SQL errors, or traceback.
No DDL/DML, no data changes, no Product or TaskCycle authority.
Native write/ACK-loss tests require distinct future reviewed attempts.
"""
from __future__ import annotations

import json
import re
import os
import sys
from urllib.parse import parse_qs, unquote, urlsplit

EXPECTED_HOST = "ep-lucky-waterfall-b6244mdy.c-2.sa-east-1.aws.neon.tech"
EXPECTED_ROLE = "tsr3_a001_neon_ro_20261109"
EXPECTED_DB = "ts_remote_r3"
EXPECTED_SCOPE = "scope-tsr3-ack-native-20261107-a01"
EXPECTED_APP = "tsr3-a001-leastpriv-ro-20261109"
SECRET_ENV = "TS_R3_NEON_CHILD_RO_DSN"
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
    ensure(re.search(r"%(?![0-9a-fA-F]{2})", dsn) is None,
           "INVALID_URI_PERCENT_ENCODING")
    try:
        parsed = urlsplit(dsn)
        host = parsed.hostname
        port = parsed.port
        user = unquote(parsed.username or "", errors="strict")
        password = (
            unquote(parsed.password, errors="strict")
            if parsed.password is not None else None
        )
    except (ValueError, UnicodeError):
        raise BlockedPrecondition("INVALID_DSN_URI") from None
    ensure(all(ord(c) >= 32 for c in user) and
           (password is None or all(ord(c) >= 32 for c in password)),
           "UNSAFE_DSN_CHARACTER")
    ensure(parsed.scheme == "postgresql", "UNSUPPORTED_DSN_SCHEME")
    ensure(host is not None and "-pooler" not in host,
           "POOLED_ENDPOINT_FORBIDDEN")
    ensure(host == EXPECTED_HOST, "BRANCH_COMPUTE_HOST_MISMATCH")
    ensure(user == EXPECTED_ROLE, "ROLE_MISMATCH")
    ensure(password is not None and bool(password), "MISSING_PASSWORD")
    ensure(parsed.path == "/" + EXPECTED_DB, "DATABASE_MISMATCH")
    ensure(port in (None, 5432), "INVALID_PORT")
    ensure(not parsed.fragment, "UNEXPECTED_FRAGMENT")
    try:
        options = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise BlockedPrecondition("INVALID_DSN_OPTIONS") from None
    ensure(all(ord(c) >= 32 for values in options.values()
               for value in values for c in value),
           "UNSAFE_DSN_CHARACTER")
    ensure(set(options).issubset({"sslmode", "channel_binding"}), "UNEXPECTED_DSN_OPTION")
    ensure(len(options.get("sslmode", [])) == 1 and
           options["sslmode"][0] in ("require", "verify-ca", "verify-full"),
           "TLS_REQUIRED")
    ensure(options.get("channel_binding") == ["require"],
           "CHANNEL_BINDING_NOT_STRICT")



def secure_connection_kwargs() -> dict[str, str]:
    """Overrides any weaker options from the stored secret or PG* environment.

    Libpq's actual connection is required to authenticate a TLS server,
    validate its name with system CA roots, and use SCRAM channel binding.
    """
    return {
        "sslmode": "verify-full",
        "sslrootcert": "system",
        "channel_binding": "require",
        "gssencmode": "disable",
    }


def self_test() -> int:
    stem = (
        "postgresql://" + EXPECTED_ROLE + ":fake-only-placeholder@"
        + EXPECTED_HOST + "/" + EXPECTED_DB
    )
    validate_dsn(stem + "?sslmode=require&channel_binding=require")
    validate_dsn(stem + "?sslmode=verify-full&channel_binding=require")
    required = secure_connection_kwargs()
    assert required == {
        "sslmode": "verify-full",
        "sslrootcert": "system",
        "channel_binding": "require",
        "gssencmode": "disable",
    }
    allowed = "?sslmode=require&channel_binding=require"
    invalid = (
        (stem.replace(EXPECTED_HOST, EXPECTED_HOST.replace("ep-", "ep-other-", 1))
         + allowed, "BRANCH_COMPUTE_HOST_MISMATCH"),
        (stem.replace(EXPECTED_ROLE, "tsr3_owner", 1) + allowed, "ROLE_MISMATCH"),
        (stem.replace(EXPECTED_HOST, EXPECTED_HOST.replace(".c-2.", "-pooler.c-2.", 1))
         + allowed, "POOLED_ENDPOINT_FORBIDDEN"),
        (stem + "?sslmode=disable&channel_binding=require", "TLS_REQUIRED"),
        (stem + "?sslmode=require&sslmode=disable&channel_binding=require",
         "TLS_REQUIRED"),
        (stem + allowed + "&options=superuser", "UNEXPECTED_DSN_OPTION"),
        (stem + "?sslmode=require&channel_binding=disable", "CHANNEL_BINDING_NOT_STRICT"),
        (stem + "?sslmode=require", "CHANNEL_BINDING_NOT_STRICT"),
        (stem + "?sslmode=verify-full", "CHANNEL_BINDING_NOT_STRICT"),
        (stem.replace("/" + EXPECTED_DB, "/postgres") + allowed,
         "DATABASE_MISMATCH"),
        (stem.replace(":fake-only-placeholder@", "@", 1) + allowed,
         "MISSING_PASSWORD"),
        (stem + allowed + "#fragment", "UNEXPECTED_FRAGMENT"),
        (stem.replace("postgresql://", "postgres://", 1) + allowed,
         "UNSUPPORTED_DSN_SCHEME"),
        ("", "NO_SECURE_DSN"),
        (stem.replace(EXPECTED_HOST, EXPECTED_HOST + ":5433") + allowed,
         "INVALID_PORT"),
        (stem.replace(EXPECTED_HOST, EXPECTED_HOST + ":notaport") + allowed,
         "INVALID_DSN_URI"),
        (stem.replace(EXPECTED_HOST, EXPECTED_HOST + ":65536") + allowed,
         "INVALID_DSN_URI"),
        (stem.replace(EXPECTED_HOST, "[::1]") + allowed,
         "BRANCH_COMPUTE_HOST_MISMATCH"),
        (stem.replace(EXPECTED_HOST, "[::1") + allowed,
         "INVALID_DSN_URI"),
        (stem.replace(EXPECTED_ROLE + ":", ":") + allowed,
         "ROLE_MISMATCH"),
        (stem.replace(EXPECTED_ROLE + ":", EXPECTED_ROLE + "%00:") + allowed,
         "UNSAFE_DSN_CHARACTER"),
        (stem.replace(":fake-only-placeholder@", ":%00fake@") + allowed,
         "UNSAFE_DSN_CHARACTER"),
        (stem.replace(":fake-only-placeholder@", ":%ZZfake@") + allowed,
         "INVALID_URI_PERCENT_ENCODING"),
        (stem.replace(":fake-only-placeholder@", ":%FFfake@") + allowed,
         "INVALID_DSN_URI"),
        (stem + allowed + "&channel_binding=require",
         "CHANNEL_BINDING_NOT_STRICT"),
        (stem + allowed + "&sslmode=require",
         "TLS_REQUIRED"),
        (stem + allowed + "&channel_binding=%ZZ",
         "INVALID_URI_PERCENT_ENCODING"),
        (stem + allowed + "%0A", "UNSAFE_DSN_CHARACTER"),
        (stem + allowed + "&sslrootcert=system",
         "UNEXPECTED_DSN_OPTION"),
    )
    for case, expected_code in invalid:
        try:
            validate_dsn(case)
        except BlockedPrecondition as exc:
            ensure(str(exc) == expected_code,
                   "NEGATIVE_WRONG_REJECTION_" + expected_code)
        else:
            raise AssertionError("NEGATIVE_UNEXPECTED_ACCEPT_" + expected_code)
    return len(invalid)


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
            **secure_connection_kwargs(),
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
                           has_schema_privilege(
                               current_user, 'ts_r3_global_head_20261107_001',
                               'CREATE') AS schema_create,
                           (SELECT NOT (r.rolsuper OR r.rolcreatedb OR r.rolcreaterole)
                            FROM pg_roles r WHERE r.rolname=current_user
                           ) AS role_nonadmin,
                           NOT pg_has_role(current_user, 'neon_superuser',
                                           'member') AS not_neon_superuser,
                           NOT (
                               has_table_privilege(current_user,
                                   'ts_r3_global_head_20261107_001.head',
                                   'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                               OR has_table_privilege(current_user,
                                   'ts_r3_global_head_20261107_001.events',
                                   'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                               OR has_table_privilege(current_user,
                                   'ts_r3_global_head_20261107_001.receipts',
                                   'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                           ) AS no_table_write,
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
                    "tls_in_use", "schema_use", "schema_create",
                    "role_nonadmin", "not_neon_superuser", "no_table_write",
                    "db_create", "head_update",
                    "head_count", "event_count", "receipt_count",
                }, "UNEXPECTED_DB_RESULT")
                ensure(row["database_name"] == EXPECTED_DB and
                       row["role_name"] == EXPECTED_ROLE, "DB_IDENTITY_MISMATCH")
                ensure(160000 <= row["version_num"] < 170000,
                       "POSTGRES_16_REQUIRED")
                ensure(row["isolation"] == "read committed", "ISOLATION_MISMATCH")
                ensure(row["tls_in_use"] is True, "TLS_INACTIVE")
                ensure(row["schema_use"] is True and
                       row["schema_create"] is False and
                       row["role_nonadmin"] is True and
                       row["not_neon_superuser"] is True and
                       row["no_table_write"] is True and
                       row["head_update"] is False and
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
        "schema": "ts-r3-a001-psycopg-readonly-preflight/v3-leastpriv-full",
        "status": "PASS_READ_ONLY",
        "python": "3.15.2",
        "psycopg": "3.3.8",
        "db": EXPECTED_DB,
        "role": EXPECTED_ROLE,
        "postgres": "16",
        "host_match": True,
        "tls": True,
        "libpq_sslmode": "verify-full",
        "libpq_sslrootcert": "system",
        "libpq_channel_binding": "require",
        "scope": EXPECTED_SCOPE,
        "head_events_receipts": [0, 0, 0],
        "product_effect": "NONE",
        "network_commit_ack_test": "NOT_RUN",
    }


def main(args: list[str]) -> int:
    if args == ["--self-test"]:
        tested = self_test()
        print(json.dumps({"status": "PASS_DSN_METADATA_SELFTEST",
                          "negative_exact_reject_cases": tested, "network": "NOT_RUN"}))
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
