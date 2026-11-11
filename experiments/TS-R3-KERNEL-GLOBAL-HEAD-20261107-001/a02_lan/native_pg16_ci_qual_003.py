"""NONPRODUCT one-shot native PostgreSQL 16 CI fixture qualification.

Uses ONLY a fresh GitHub Actions disposable PostgreSQL service at 127.0.0.1.
Explicitly authorized separately frozen A003 synthetic roles/database/DDL. Never imports a
Product connection or executes original A02 physical protocol/writers.
Exit nonzero on mismatch. One run/attempt; original receipts are GitHub-native.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a02_lan.role_boundary import (
    OWNER_ROLE, WRITER_ROLE, DATABASE, SCHEMA, assert_writer_boundary,
)

ATTEMPT = "TS-R3-A02-NATIVE-PG16-CI-QUAL-20261111-001-A003"
EXPECTED_SCHEMA_BLOB = "3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0"
ADMIN_PASSWORD = "ci-ephemeral-postgres-not-a-secret"
OWNER_PASSWORD = "ci-ephemeral-owner-not-a-secret"
WRITER_PASSWORD = "ci-ephemeral-writer-not-a-secret"
FIXED_HEAD = "67941b33ee077ba8fc0dbcda0196232dbd7895eb"
ROOT_SCHEMA = ROOT / "schema.sql"
EXPECTED_COLS = {
    "head": (
        ("scope", "text", True), ("revision", "bigint", True),
        ("state_bytes", "bytea", True), ("state_sha256", "text", True),
        ("events_sha256", "text", True), ("last_event_hash", "text", False),
    ),
    "events": (
        ("scope", "text", True), ("revision", "bigint", True),
        ("event_hash", "text", True), ("previous_event_hash", "text", False),
        ("payload_bytes", "bytea", True), ("event_line", "bytea", True),
    ),
    "receipts": (
        ("scope", "text", True), ("mutation_id", "text", True),
        ("command_fingerprint", "text", True), ("expected_revision", "bigint", True),
        ("result_revision", "bigint", True), ("event_hash", "text", True),
        ("authority_fingerprint", "text", True),
    ),
}
EXPECTED_CONSTRAINT_COUNTS = {
    "head": {"p": 1, "c": 4},
    "events": {"p": 1, "u": 1, "f": 1, "c": 2},
    "receipts": {"p": 1, "u": 1, "f": 1, "c": 5},
}
EXPECTED_INDEXES = {
    "events_pkey": True,
    "events_scope_event_hash_key": False,
    "head_pkey": True,
    "receipts_pkey": True,
    "receipts_scope_result_revision_key": False,
}

EXPECTED_INDEX_KEYS = {
    "events_pkey": "1 2",
    "events_scope_event_hash_key": "1 3",
    "head_pkey": "1",
    "receipts_pkey": "1 2",
    "receipts_scope_result_revision_key": "1 5",
}


def require(value: bool, code: str) -> None:
    if not value:
        raise AssertionError(code)


def connection(role: str, database: str):
    require(role in ("postgres", OWNER_ROLE, WRITER_ROLE), "FOREIGN_ROLE")
    require(database in ("postgres", DATABASE), "FOREIGN_DATABASE")
    pw = {"postgres": ADMIN_PASSWORD, OWNER_ROLE: OWNER_PASSWORD,
          WRITER_ROLE: WRITER_PASSWORD}[role]
    return psycopg.connect(host="127.0.0.1", port=5432, dbname=database,
                           user=role, password=pw, connect_timeout=8,
                           autocommit=True, row_factory=dict_row)


def frozen_preflight() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true", "GITHUB_ACTIONS_REQUIRED")
    require(os.environ.get("GITHUB_EVENT_NAME") == "push", "PUSH_ONLY")
    require(os.environ.get("GITHUB_REF") ==
            "refs/heads/ee/ts-r3-a02-native-pg16-qual-20261111-003",
            "FROZEN_NONPRODUCT_BRANCH_ONLY")
    require(os.environ.get("TS_CI_NATIVE_SYNTHETIC_ONLY") == "1",
            "SYNTHETIC_ONLY_REQUIRED")
    require(os.environ.get("GITHUB_SHA") is not None, "NATIVE_GIT_ID_REQUIRED")
    require(OWNER_ROLE == "tsr3_a02_lab" and
            WRITER_ROLE == "tsr3_a02_writer" and
            DATABASE == "tsr3_a02_lab", "FROZEN_ROLE_IDENTITY_CHANGED")
    # Workflow independently pins git blob through git rev-parse HEAD:<path>.
    schema = ROOT_SCHEMA.read_text("utf-8")
    require(schema.count("CREATE TABLE ") == 3 and
            schema.count("CREATE SCHEMA ") == 1 and
            not re.search(r"\bDROP\b|\bALTER ROLE\b", schema),
            "SCHEMA_SOURCE_NOT_DISPOSABLE")
    require("NONPRODUCT" in schema and "pg_catalog" not in schema,
            "SCHEMA_SOURCE_IDENTITY_INVALID")
    require(len(frozen_statements()) == 4, "SCHEMA_STATEMENT_COUNT_CHANGED")


def provision(admin) -> None:
    # Fresh postgres:16-alpine service only. All identifiers and passwords
    # are literal synthetic, unrelated to production and never exported.
    version = admin.execute("SHOW server_version_num").fetchone()["server_version_num"]
    require(160000 <= int(version) < 170000, "PG16_REQUIRED")
    seen = admin.execute(
        "SELECT rolname FROM pg_catalog.pg_roles "
        "WHERE rolname IN (%s,%s) ORDER BY rolname",
        (OWNER_ROLE, WRITER_ROLE),
    ).fetchall()
    require(seen == [], "SYNTHETIC_ROLES_ALREADY_EXIST")
    dbs = admin.execute(
        "SELECT datname FROM pg_catalog.pg_database WHERE datname=%s",
        (DATABASE,),
    ).fetchall()
    require(dbs == [], "SYNTHETIC_DATABASE_ALREADY_EXISTS")
    admin.execute("CREATE ROLE tsr3_a02_lab LOGIN NOSUPERUSER NOCREATEROLE "
                  "NOCREATEDB NOREPLICATION NOBYPASSRLS NOINHERIT "
                  "PASSWORD 'ci-ephemeral-owner-not-a-secret'")
    admin.execute("CREATE ROLE tsr3_a02_writer LOGIN NOSUPERUSER NOCREATEROLE "
                  "NOCREATEDB NOREPLICATION NOBYPASSRLS NOINHERIT "
                  "PASSWORD 'ci-ephemeral-writer-not-a-secret'")
    admin.execute("CREATE DATABASE tsr3_a02_lab OWNER tsr3_a02_lab")
    admin.execute("REVOKE ALL ON DATABASE tsr3_a02_lab FROM PUBLIC")
    admin.execute("GRANT CONNECT ON DATABASE tsr3_a02_lab TO tsr3_a02_writer")


def frozen_statements() -> list[str]:
    schema = ROOT_SCHEMA.read_text("utf-8")
    # The frozen DDL contains only whole-line comments: strip before splitting.
    uncommented = "\n".join(line for line in schema.splitlines()
                              if not line.lstrip().startswith("--"))
    parts = [v.strip() for v in uncommented.split(";") if v.strip()]
    require(len(parts) == 4 and parts[0].startswith("CREATE SCHEMA ") and
            all(v.startswith("CREATE TABLE ") for v in parts[1:]),
            "SCHEMA_STATEMENT_COUNT_CHANGED")
    return parts


def apply_frozen_schema(database: str = DATABASE, *, skip_schema: bool = False) -> None:
    parts = frozen_statements()
    with connection(OWNER_ROLE, database) as owner:
        with owner.transaction():
            for stmt in parts[1:] if skip_schema else parts:
                owner.execute(stmt)


def grant_limited_roles(admin) -> None:
    admin.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    admin.execute("GRANT USAGE ON SCHEMA ts_r3_global_head_20261107_001 "
                  "TO tsr3_a02_writer")
    admin.execute("GRANT SELECT,UPDATE ON "
                  "ts_r3_global_head_20261107_001.head TO tsr3_a02_writer")
    admin.execute("GRANT SELECT,INSERT ON "
                  "ts_r3_global_head_20261107_001.events TO tsr3_a02_writer")
    admin.execute("GRANT SELECT,INSERT ON "
                  "ts_r3_global_head_20261107_001.receipts TO tsr3_a02_writer")
    admin.execute("REVOKE ALL ON FUNCTION "
                  "pg_catalog.pg_control_system() FROM PUBLIC")
    admin.execute("GRANT EXECUTE ON FUNCTION "
                  "pg_catalog.pg_control_system() TO tsr3_a02_writer")


def native_schema_snapshot(conn) -> dict:
    # One repeatable-read, read-only PostgreSQL 16 snapshot, not self-authored
    # FakeConn metadata. Names are immutable source constants.
    with conn.transaction():
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        tables = conn.execute(
            "SELECT c.relname AS table_name, c.relkind AS kind, "
            "c.relrowsecurity AS rls,c.relforcerowsecurity AS force_rls,"
            "c.relpersistence AS persistence,c.relispartition AS partition,"
            "c.reloptions AS options "
            "FROM pg_catalog.pg_class c "
            "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname=%s AND c.relkind='r' ORDER BY c.relname",
            (SCHEMA,),
        ).fetchall()
        cols = conn.execute(
            "SELECT c.relname AS table_name,a.attname AS name,a.attnum AS num,"
            "pg_catalog.format_type(a.atttypid,a.atttypmod) AS dtype,"
            "a.attnotnull AS required,a.atthasdef AS has_default,"
            "a.attidentity AS identity,a.attgenerated AS generated,"
            "a.attacl::text AS acl,a.attcollation::text AS collation_oid,"
            "pg_catalog.pg_get_expr(d.adbin,d.adrelid) AS default_expr "
            "FROM pg_catalog.pg_attribute a "
            "JOIN pg_catalog.pg_class c ON c.oid=a.attrelid "
            "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
            "LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid=a.attrelid "
            "AND d.adnum=a.attnum "
            "WHERE n.nspname=%s AND c.relkind='r' "
            "AND a.attnum>0 AND NOT a.attisdropped "
            "ORDER BY c.relname,a.attnum", (SCHEMA,),
        ).fetchall()
        constraints = conn.execute(
            "SELECT c.relname AS table_name,t.conname AS name,t.contype AS kind,"
            "t.convalidated AS validated,t.condeferrable AS deferrable,"
            "t.condeferred AS deferred,t.conkey::text AS column_keys,"
            "t.confrelid::regclass::text AS fk_target,"
            "t.confkey::text AS fk_columns,"
            "pg_catalog.pg_get_constraintdef(t.oid, true) AS definition "
            "FROM pg_catalog.pg_constraint t "
            "JOIN pg_catalog.pg_class c ON c.oid=t.conrelid "
            "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname=%s ORDER BY c.relname,t.conname",
            (SCHEMA,),
        ).fetchall()
        indexes = conn.execute(
            "SELECT c.relname AS name,i.indisvalid AS valid,"
            "i.indisready AS ready,i.indislive AS live,"
            "i.indisunique AS unique_index,i.indisprimary AS primary_index,"
            "i.indisexclusion AS exclusion,i.indnullsnotdistinct AS nulls_nd,"
            "i.indkey::text AS indexed_columns,"
            "pg_catalog.pg_get_expr(i.indpred,i.indrelid) AS predicate,"
            "pg_catalog.pg_get_expr(i.indexprs,i.indrelid) AS expression,"
            "pg_catalog.pg_get_indexdef(i.indexrelid) AS definition "
            "FROM pg_catalog.pg_index i "
            "JOIN pg_catalog.pg_class c ON c.oid=i.indexrelid "
            "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname=%s ORDER BY c.relname",
            (SCHEMA,),
        ).fetchall()
    return {"tables": tables, "columns": cols, "constraints": constraints,
            "indexes": indexes}


def validate_baseline(snapshot: dict) -> None:
    tables = snapshot["tables"]
    require([r["table_name"] for r in tables] == ["events", "head", "receipts"],
            "NATIVE_EXACT_THREE_TABLES_FAILED")
    for row in tables:
        require(row["kind"] == "r" and row["rls"] is False and
                row["force_rls"] is False and row["persistence"] == "p"
                and row["partition"] is False and row["options"] is None,
                "NATIVE_TABLE_FLAGS_DIVERGE")
    actual_cols: dict[str, list] = {}
    for row in snapshot["columns"]:
        actual_cols.setdefault(row["table_name"], []).append(row)
        require(row["has_default"] is False and
                row["default_expr"] is None and row["identity"] == ""
                and row["generated"] == "" and row["acl"] is None,
                "NATIVE_COLUMN_DEFAULT_IDENTITY_ACL_DIVERGE")
    require(set(actual_cols) == set(EXPECTED_COLS), "NATIVE_COLUMN_TABLE_SET")
    for name, expected in EXPECTED_COLS.items():
        rows = actual_cols[name]
        require(tuple((r["name"], r["dtype"], r["required"]) for r in rows) ==
                expected and [r["num"] for r in rows] ==
                list(range(1, len(expected) + 1)),
                "NATIVE_COLUMN_TYPE_ORDER_NULLABILITY_DIVERGE_" + name.upper())
    actual_cons: dict[str, Counter] = {}
    for row in snapshot["constraints"]:
        actual_cons.setdefault(row["table_name"], Counter())[row["kind"]] += 1
        require(row["validated"] is True and row["deferrable"] is False and
                row["deferred"] is False, "NATIVE_CONSTRAINT_FLAGS_INVALID")
        require(type(row["definition"]) is str and bool(row["definition"]),
                "NATIVE_CONSTRAINT_DEFINITION_MISSING")
    require(set(actual_cons) == set(EXPECTED_CONSTRAINT_COUNTS),
            "NATIVE_CONSTRAINT_TABLE_SET")
    for table, kindcounts in EXPECTED_CONSTRAINT_COUNTS.items():
        require(dict(actual_cons[table]) == kindcounts,
                "NATIVE_CONSTRAINT_TYPE_COUNT_DIVERGE_" + table.upper())
    indexes = snapshot["indexes"]
    require({row["name"] for row in indexes} == set(EXPECTED_INDEXES)
            and len(indexes) == 5, "NATIVE_INDEX_FOOTPRINT_DIVERGE")
    for row in indexes:
        require(row["valid"] is True and row["ready"] is True and
                row["live"] is True and row["unique_index"] is True
                and row["primary_index"] is EXPECTED_INDEXES[row["name"]]
                and row["exclusion"] is False and row["nulls_nd"] is False
                and "USING btree" in row["definition"]
                and SCHEMA in row["definition"]
                and row["indexed_columns"] == EXPECTED_INDEX_KEYS[row["name"]]
                and row["predicate"] is None and row["expression"] is None,
                "NATIVE_INDEX_DEFINITION_OR_FLAGS_INVALID")


def digest(snapshot: dict) -> str:
    return sha256(json.dumps(snapshot, sort_keys=True,
                            separators=(",", ":")).encode()).hexdigest()


def expect_guard_rejects(admin, writer, label: str, alter: str,
                         restore: str, expected_code: str) -> None:
    admin.execute(alter)
    try:
        try:
            assert_writer_boundary(writer)
        except AssertionError as exc:
            require(str(exc) == expected_code,
                    "WRONG_NATIVE_NEGATIVE_" + label)
        else:
            raise AssertionError("NATIVE_GUARD_FALSE_ACCEPT_" + label)
    finally:
        admin.execute(restore)
    # Exact original baseline, no lingering malicious privilege or DDL.
    assert_writer_boundary(writer)


def main() -> None:
    frozen_preflight()
    with connection("postgres", "postgres") as admin:
        provision(admin)
        # Golden is a second native compilation of frozen SQL inside the
        # EXISTING disposable postgres DB, not a foreign physical database.
        admin.execute("CREATE SCHEMA " + SCHEMA + " AUTHORIZATION " + OWNER_ROLE)
    apply_frozen_schema()
    apply_frozen_schema("postgres", skip_schema=True)
    with connection("postgres", DATABASE) as admin, \
         connection(OWNER_ROLE, DATABASE) as owner, \
         connection(WRITER_ROLE, DATABASE) as writer, \
         connection(OWNER_ROLE, "postgres") as golden:
        grant_limited_roles(admin)
        golden_baseline = native_schema_snapshot(golden)
        validate_baseline(golden_baseline)
        baseline = native_schema_snapshot(owner)
        validate_baseline(baseline)
        require(baseline == golden_baseline,
                "NATIVE_GOLDEN_FROZEN_DDL_MISMATCH")
        # Real source guard imported unchanged from frozen candidate.
        assert_writer_boundary(writer)
        system = writer.execute(
            "SELECT system_identifier::text AS id FROM "
            "pg_catalog.pg_control_system()"
        ).fetchone()
        require(system is not None and
                re.fullmatch(r"[0-9]{16,20}", system["id"]) is not None,
                "NATIVE_PG_CONTROL_EXECUTE_NOT_REAL")
        neg = [
            ("missing_head_select",
             "REVOKE SELECT ON " + SCHEMA + ".head FROM " + WRITER_ROLE,
             "GRANT SELECT ON " + SCHEMA + ".head TO " + WRITER_ROLE,
             "WRITER_TABLE_GRANT_INVALID_HEAD_SELECT"),
            ("excess_head_delete",
             "GRANT DELETE ON " + SCHEMA + ".head TO " + WRITER_ROLE,
             "REVOKE DELETE ON " + SCHEMA + ".head FROM " + WRITER_ROLE,
             "WRITER_TABLE_GRANT_INVALID_HEAD_DELETE"),
            ("head_rls_enabled",
             "ALTER TABLE " + SCHEMA + ".head ENABLE ROW LEVEL SECURITY",
             "ALTER TABLE " + SCHEMA + ".head DISABLE ROW LEVEL SECURITY",
             "WRITER_FOREIGN_OBJECT_OR_OWNER"),
            ("user_enum_type",
             "CREATE TYPE " + SCHEMA + ".native_rogue_enum AS ENUM ('x')",
             "DROP TYPE " + SCHEMA + ".native_rogue_enum",
             "WRITER_FOREIGN_USER_TYPE"),
            ("pg_control_execute_revoked",
             "REVOKE EXECUTE ON FUNCTION pg_catalog.pg_control_system() "
             "FROM " + WRITER_ROLE,
             "GRANT EXECUTE ON FUNCTION pg_catalog.pg_control_system() "
             "TO " + WRITER_ROLE,
             "CONTROL_SYSTEM_FUNCTION_ACCESS_NOT_ATTESTED"),
        ]
        for label, alter, restore, code in neg:
            expect_guard_rejects(admin, writer, label, alter, restore, code)
        # Deliberately demonstrate the source guard's known *bounded* scope:
        # it does NOT inspect CHECK definitions. Native read-only schema
        # attestation must reject the extra constraint, without falsely
        # describing this expected source limitation as a regression.
        admin.execute("ALTER TABLE " + SCHEMA +
                      ".head ADD CONSTRAINT native_extra_check "
                      "CHECK (revision >= 0)")
        try:
            assert_writer_boundary(writer)
            tampered = native_schema_snapshot(owner)
            require(digest(tampered) != digest(baseline),
                    "NATIVE_ATTESTATION_FALSE_ACCEPT_EXTRA_CONSTRAINT")
            require(len(tampered["constraints"]) ==
                    len(baseline["constraints"]) + 1,
                    "NATIVE_EXTRA_CONSTRAINT_NOT_OBSERVED")
        finally:
            admin.execute("ALTER TABLE " + SCHEMA +
                          ".head DROP CONSTRAINT native_extra_check")
        assert_writer_boundary(writer)
        require(digest(native_schema_snapshot(owner)) == digest(golden_baseline),
                "NATIVE_FIXTURE_NOT_RESTORED")
        # Three name/count preserving DDL mutations; the source guard is
        # intentionally bounded, while golden must detect semantic changes.
        same_count_cases = (
            ("check_expression",
             ("ALTER TABLE " + SCHEMA + ".head DROP CONSTRAINT head_revision_check",
              "ALTER TABLE " + SCHEMA + ".head ADD CONSTRAINT head_revision_check CHECK (revision >= -1)"),
             ("ALTER TABLE " + SCHEMA + ".head DROP CONSTRAINT head_revision_check",
              "ALTER TABLE " + SCHEMA + ".head ADD CONSTRAINT head_revision_check CHECK (revision >= 0)")),
            ("fk_delete_action",
             ("ALTER TABLE " + SCHEMA + ".events DROP CONSTRAINT events_scope_fkey",
              "ALTER TABLE " + SCHEMA + ".events ADD CONSTRAINT events_scope_fkey FOREIGN KEY(scope) REFERENCES " + SCHEMA + ".head(scope) ON DELETE CASCADE"),
             ("ALTER TABLE " + SCHEMA + ".events DROP CONSTRAINT events_scope_fkey",
              "ALTER TABLE " + SCHEMA + ".events ADD CONSTRAINT events_scope_fkey FOREIGN KEY(scope) REFERENCES " + SCHEMA + ".head(scope)")),
            ("unique_key_swap",
             ("ALTER TABLE " + SCHEMA + ".receipts DROP CONSTRAINT receipts_scope_result_revision_key",
              "ALTER TABLE " + SCHEMA + ".receipts ADD CONSTRAINT receipts_scope_result_revision_key UNIQUE(scope,expected_revision)"),
             ("ALTER TABLE " + SCHEMA + ".receipts DROP CONSTRAINT receipts_scope_result_revision_key",
              "ALTER TABLE " + SCHEMA + ".receipts ADD CONSTRAINT receipts_scope_result_revision_key UNIQUE(scope,result_revision)")),
        )
        for label, edits, restores in same_count_cases:
            for sql in edits:
                admin.execute(sql)
            try:
                assert_writer_boundary(writer)
                changed = native_schema_snapshot(owner)
                require(len(changed["constraints"]) == len(golden_baseline["constraints"])
                        and len(changed["indexes"]) == len(golden_baseline["indexes"]),
                        "NATIVE_SAME_COUNT_FIXTURE_INVALID_" + label.upper())
                require(changed != golden_baseline,
                        "NATIVE_SAME_COUNT_FALSE_ACCEPT_" + label.upper())
            finally:
                for sql in restores:
                    admin.execute(sql)
            assert_writer_boundary(writer)
            require(native_schema_snapshot(owner) == golden_baseline,
                    "NATIVE_SAME_COUNT_NOT_RESTORED_" + label.upper())

        summary = {
            "status": "NATIVE_PG16_CI_GOLDEN_DDL_DEFINITION_PASS",
            "execution_attempt": ATTEMPT,
            "source_git_subject": FIXED_HEAD,
            "pg_major": 16,
            "native_catalog": True,
            "actual_restricted_writer": True,
            "pg_control_system_real_exec": True,
            "negative_guard_scenarios": len(neg),
            "same_count_definition_negatives": len(same_count_cases),
            "native_golden_separate_database": "postgres",
            "native_golden_full_definitions_match": native_schema_snapshot(owner) == golden_baseline,
            "golden_schema_inventory_sha256": digest(golden_baseline),
            "pg_system_identifier_sha256": sha256(system["id"].encode()).hexdigest(),
            "postgres_image_manifest_sha256": "aa6cb33cf4c19c765cefcf48d96176258800870a9a1e930ad126200f9d825139",
            "expected_source_constraint_gap_confirmed": True,
            "native_extra_constraint_attestation_rejects": True,
            "table_count": len(baseline["tables"]),
            "column_count": len(baseline["columns"]),
            "constraint_count": len(baseline["constraints"]),
            "index_count": len(baseline["indexes"]),
            "schema_inventory_sha256": digest(baseline),
            "fixture_database_effect": "EPHEMERAL_CI_ONLY",
            "external_host_effect": "NONE",
            "product_effect": "NONE",
            "neon_effect": "NONE",
            "physical_a02": "NO_GO",
            "real_two_physical_hosts": "NOT_RUN",
            "lost_tcp_commit_ack": "NOT_RUN",
            "restore": "NOT_RUN",
        }
        print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        # The exact native SQL failure class or source guard error code is
        # part of this test; do not print credentials/DSNs, arbitrary SQL or
        # exception traces to a public CI log.
        reason = (str(exc) if type(exc) is AssertionError else
                  type(exc).__name__.upper())
        if not re.fullmatch(r"[A-Z0-9_]{3,96}", reason):
            reason = "REDACTED"
        print("NATIVE_PG16_FAIL_" + reason, file=sys.stderr)
        raise SystemExit(1)
