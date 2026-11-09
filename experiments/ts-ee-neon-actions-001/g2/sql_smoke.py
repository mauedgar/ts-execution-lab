"""G2: synthetic PostgreSQL E2E only on a unique disposable Neon branch."""
import json
import os
import re
import sys
from pathlib import Path

import psycopg
from psycopg.errors import UniqueViolation

EXPECTED_DATABASE = "ts_ee_neon_ci"
EXPECTED_ROLE = "ts_ee_neon_ci_owner"


def execute() -> None:
    attempt = os.environ["GITHUB_RUN_ID"]
    if not re.fullmatch(r"[0-9]+", attempt):
        raise ValueError("invalid run identity")
    receipt = Path(os.environ["G2_SQL_RECEIPT"])
    uri = os.environ["DATABASE_URL"]
    if not uri.startswith("postgresql://"):
        raise ValueError("database scheme mismatch")

    with psycopg.connect(uri, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            db, role = cur.fetchone()
            if (db, role) != (EXPECTED_DATABASE, EXPECTED_ROLE):
                raise ValueError("unexpected database/role identity")
            cur.execute("CREATE SCHEMA ts_ee_g2")
            cur.execute(
                "CREATE TABLE ts_ee_g2.probe ("
                " id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,"
                " attempt_id text NOT NULL UNIQUE,"
                " payload text NOT NULL,"
                " created_at timestamptz NOT NULL DEFAULT now())"
            )
            cur.execute(
                "INSERT INTO ts_ee_g2.probe(attempt_id,payload) VALUES (%s,%s)",
                (attempt, "synthetic-only"),
            )
            cur.execute("SAVEPOINT g2_negative_test")
            try:
                cur.execute(
                    "INSERT INTO ts_ee_g2.probe(attempt_id,payload) VALUES (%s,%s)",
                    (attempt, "must-fail"),
                )
            except UniqueViolation:
                cur.execute("ROLLBACK TO SAVEPOINT g2_negative_test")
            else:
                raise AssertionError("unique constraint not enforced")
            cur.execute("RELEASE SAVEPOINT g2_negative_test")

    with psycopg.connect(uri, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT attempt_id, payload FROM ts_ee_g2.probe"
            )
            rows = cur.fetchall()
            if rows != [(attempt, "synthetic-only")]:
                raise AssertionError("transaction commit/readback mismatch")

    receipt.write_text(
        json.dumps(
            {
                "gate": "G2",
                "run_id": attempt,
                "commit": os.environ["GITHUB_SHA"],
                "database": EXPECTED_DATABASE,
                "role": EXPECTED_ROLE,
                "schema": "ts_ee_g2",
                "tests": ["create", "insert", "unique_negative", "commit_readback"],
                "result": "PASS",
                "product_effect": "NONE",
            },
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    print("TS_EE_NEON_G2_SQL_E2E_PASS")


if __name__ == "__main__":
    try:
        execute()
    except Exception as exc:
        print("TS_EE_NEON_G2_SQL_E2E_FAIL_" + type(exc).__name__)
        sys.exit(1)
