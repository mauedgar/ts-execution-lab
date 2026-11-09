"""A11 disposable SQL schema create-only / guarded cleanup. NONPRODUCT."""
from __future__ import annotations

import os
from pathlib import Path
import sys

import psycopg
from psycopg.rows import dict_row

SCHEMA = "ts_r3_global_head_20261107_001"
SCOPE = "A10-DISPOSABLE-SINGLE-SCOPE"
URI = ("postgresql://tsr3_a11_synthetic:a11_disposable_only"
       "@127.0.0.1:5432/tsr3_a11_synthetic?sslmode=disable")
ROOT = Path(__file__).resolve().parent.parent


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AssertionError(reason)


def main():
    require(len(sys.argv) == 2 and sys.argv[1] in ("prepare", "cleanup"), "EXACT_MODE")
    require(os.getenv("TS_R3_LOCAL_SYNTHETIC_PG_URI") == URI, "LOCAL_DISPOSABLE_ONLY")
    require(not os.getenv("TS_R3_NEON_CHILD_DSN") and not os.getenv("DATABASE_URL") and
            not os.getenv("PGPASSWORD"), "NO_REMOTE_CREDENTIALS")
    require(psycopg.__version__ == "3.3.8" and psycopg.pq.__impl__ == "binary",
            "PINNED_PSYCOPG")
    with psycopg.connect(URI, autocommit=True, row_factory=dict_row, connect_timeout=5) as conn:
        ident = conn.execute("SELECT current_database() AS db,current_user AS owner").fetchone()
        require(ident == {"db": "tsr3_a11_synthetic", "owner": "tsr3_a11_synthetic"},
                "SYNTHETIC_ID_MISMATCH")
        require(conn.execute("SHOW server_version").fetchone()["server_version"].startswith("16."),
                "PG16_REQUIRED")
        exists = conn.execute(
            "SELECT COUNT(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
            (SCHEMA,)).fetchone()["n"]
        if sys.argv[1] == "prepare":
            require(exists == 0, "DISPOSABLE_SCHEMA_PREEXISTS")
            sql = (ROOT / "schema.sql").read_text(encoding="utf-8")
            statements = [part.strip() for part in "\n".join(
                line for line in sql.splitlines() if not line.lstrip().startswith("--")
            ).split(";") if part.strip()]
            require(len(statements) == 4 and statements[0] == "CREATE SCHEMA " + SCHEMA,
                    "SCHEMA_SHAPE")
            with conn.transaction():
                for statement in statements:
                    conn.execute(statement)
            tables = conn.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename",
                (SCHEMA,)).fetchall()
            require([row["tablename"] for row in tables] == ["events", "head", "receipts"],
                    "SCHEMA_TABLES")
            print("A11_DISPOSABLE_SCHEMA_CREATED_PASS")
        else:
            require(exists == 1, "EXPECTED_DISPOSABLE_SCHEMA_ABSENT")
            scopes = [row["scope"] for row in conn.execute(
                f"SELECT scope FROM {SCHEMA}.head ORDER BY scope").fetchall()]
            require(scopes == [SCOPE], "FOREIGN_SCOPE_PROTECTION")
            row = conn.execute(
                f"SELECT (SELECT COUNT(*) FROM {SCHEMA}.head) AS heads,"
                f" (SELECT COUNT(*) FROM {SCHEMA}.events) AS events,"
                f" (SELECT COUNT(*) FROM {SCHEMA}.receipts) AS receipts"
            ).fetchone()
            require(row == {"heads": 1, "events": 4, "receipts": 4},
                    "DISPOSABLE_COUNTS_MISMATCH")
            with conn.transaction():
                conn.execute(f"DROP SCHEMA {SCHEMA} CASCADE")
            after = conn.execute(
                "SELECT COUNT(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
                (SCHEMA,)).fetchone()["n"]
            require(after == 0, "DISPOSABLE_CLEANUP_FAILED")
            print("A11_DISPOSABLE_SCHEMA_CLEANUP_PASS")


if __name__ == "__main__":
    main()
