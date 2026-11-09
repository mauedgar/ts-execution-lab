"""G5 failure-retry synthetic table, isolated to a verified owned branch."""
import os
import psycopg

assert os.environ.get("BRANCH_CREATED") == "true", "branch ownership missing"
assert os.environ.get("BRANCH_ID", "").startswith("br-"), "branch ID missing"
assert os.environ["BRANCH_ID"] != "br-cool-sea-bc75qsj1", "main forbidden"
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user")
        assert cur.fetchone() == ("ts_ee_neon_ci", "ts_ee_neon_ci_owner"), "wrong connection"
        cur.execute("CREATE SCHEMA ts_ee_g5")
        cur.execute("""CREATE TABLE ts_ee_g5.failure_events(
          scheduled_at timestamptz PRIMARY KEY,
          attempts integer NOT NULL CHECK (attempts >= 1),
          state text NOT NULL CHECK (state IN ('failed_once', 'recovered'))
        )""")
print("TS_EE_G5_FAILURE_TABLE_CREATED")
