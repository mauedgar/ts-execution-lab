"""Create synthetic table only in a G3 attempt-owned disposable branch."""
import os
import psycopg

if os.environ.get("G3_BRANCH_CREATED") != "true":
    raise SystemExit("G3_OWNERSHIP_PRECONDITION_FAILED")
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user")
        if cur.fetchone() != ("ts_ee_neon_ci", "ts_ee_neon_ci_owner"):
            raise SystemExit("G3_DB_IDENTITY_MISMATCH")
        cur.execute("CREATE SCHEMA ts_ee_g3")
        cur.execute("""CREATE TABLE ts_ee_g3.pulse (
            scheduled_at timestamptz PRIMARY KEY,
            occurrence integer NOT NULL CHECK (occurrence = 1),
            written_at timestamptz NOT NULL DEFAULT clock_timestamp()
        )""")
print("TS_EE_G3_SCHEMA_CREATED")
