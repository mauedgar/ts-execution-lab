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


def inventory(conn) -> None:
    """Fail closed before any cleanup if the schema contains foreign objects."""
    relations = conn.execute(
        """SELECT c.relname, c.relkind FROM pg_catalog.pg_class c
           JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname=%s ORDER BY c.relname""",
        (SCHEMA,),
    ).fetchall()
    expected = [
        ("events", "r"), ("events_pkey", "i"),
        ("events_scope_event_hash_key", "i"), ("head", "r"),
        ("head_pkey", "i"), ("receipts", "r"),
        ("receipts_pkey", "i"), ("receipts_scope_result_revision_key", "i"),
    ]
    require([(x["relname"], x["relkind"]) for x in relations] == expected,
            "SCHEMA_UNEXPECTED_RELATION")
    types = conn.execute(
        """SELECT t.typname, t.typtype FROM pg_catalog.pg_type t
           JOIN pg_catalog.pg_namespace n ON n.oid=t.typnamespace
           WHERE n.nspname=%s ORDER BY t.typname""",
        (SCHEMA,),
    ).fetchall()
    require([(t["typname"], t["typtype"]) for t in types] ==
            [("_events", "b"), ("_head", "b"), ("_receipts", "b"),
             ("events", "c"), ("head", "c"), ("receipts", "c")],
            "SCHEMA_UNEXPECTED_TYPE")
    funcs = conn.execute(
        """SELECT count(*) AS n FROM pg_catalog.pg_proc p
           JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
           WHERE n.nspname=%s""", (SCHEMA,)).fetchone()["n"]
    require(funcs == 0, "SCHEMA_UNEXPECTED_FUNCTION")
    triggers = conn.execute(
        """SELECT count(*) AS n FROM pg_catalog.pg_trigger t
           JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid
           JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname=%s AND NOT t.tgisinternal""",
        (SCHEMA,),
    ).fetchone()["n"]
    require(triggers == 0, "SCHEMA_UNEXPECTED_TRIGGER")
    for table in ("head", "events", "receipts"):
        scopes = conn.execute(
            f"SELECT DISTINCT scope FROM {SCHEMA}.{table} ORDER BY scope",
        ).fetchall()
        require([row["scope"] for row in scopes] in ([], [SCOPE]),
                "SCHEMA_FOREIGN_SCOPE_" + table.upper())


def user_schemas(conn) -> list[str]:
    rows = conn.execute(
        """SELECT nspname FROM pg_catalog.pg_namespace
           WHERE nspname <> 'information_schema'
             AND nspname NOT LIKE 'pg\\_%' ESCAPE '\\'
           ORDER BY nspname"""
    ).fetchall()
    return [row["nspname"] for row in rows]


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
        require(user_schemas(conn) ==
                (["public"] if sys.argv[1] == "prepare" else
                 ["public", SCHEMA]), "FOREIGN_USER_SCHEMA_PRESENT")
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
            inventory(conn)
            # Disposable negative proof: foreign objects must fail the guard
            # and be rolled back before the actual qualification begins.
            class ExpectedRollback(Exception):
                pass

            try:
                with conn.transaction():
                    conn.execute(f"CREATE TABLE {SCHEMA}.foreign_object_probe (id int)")
                    try:
                        inventory(conn)
                    except AssertionError as error:
                        require(str(error) == "SCHEMA_UNEXPECTED_RELATION",
                                "FOREIGN_OBJECT_WRONG_REJECTION")
                    else:
                        raise AssertionError("FOREIGN_OBJECT_ACCEPTED")
                    raise ExpectedRollback()
            except ExpectedRollback:
                pass
            inventory(conn)
            print("A11_FOREIGN_OBJECT_GUARD_NEGATIVE_PASS")
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
            require(row == {"heads": 1, "events": 6, "receipts": 6},
                    "DISPOSABLE_COUNTS_MISMATCH")
            inventory(conn)
            with conn.transaction():
                # No CASCADE: external dependencies cause a blocked cleanup, not data loss.
                conn.execute(f"DROP TABLE {SCHEMA}.receipts, {SCHEMA}.events")
                conn.execute(f"DROP TABLE {SCHEMA}.head")
                conn.execute(f"DROP SCHEMA {SCHEMA} RESTRICT")
            after = conn.execute(
                "SELECT COUNT(*) AS n FROM pg_catalog.pg_namespace WHERE nspname=%s",
                (SCHEMA,)).fetchone()["n"]
            require(after == 0 and user_schemas(conn) == ["public"],
                    "DISPOSABLE_CLEANUP_FAILED")
            print("A11_DISPOSABLE_SCHEMA_CLEANUP_PASS")


if __name__ == "__main__":
    main()
