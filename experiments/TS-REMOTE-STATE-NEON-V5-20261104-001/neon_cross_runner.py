"""Synthetic DBOS + managed PostgreSQL across two GitHub-hosted runners.

No Product state. Never use a personal or Production Neon database.
Do not print the DSN, secrets or connection exceptions verbatim.
"""
import os
import sys
from urllib.parse import parse_qs, urlsplit

import psycopg
from dbos import DBOS, SetWorkflowID

APP = "ts_remote_state_neon_v5"
TABLE = "ts_remote_state_neon_v5_counter"
WORKFLOW = os.environ.get("TS_SYNTHETIC_WORKFLOW_ID", "")
URL = os.environ.get("DBOS_SYSTEM_DATABASE_URL", "")
PHASE = sys.argv[1] if len(sys.argv) == 2 else ""

def validate_preconditions():
    assert PHASE in ("seed", "recover"), "BLOCKED_PRECONDITION:phase"
    assert WORKFLOW.startswith("ts-neon-v5-") and WORKFLOW.removeprefix("ts-neon-v5-").isdigit(), "BLOCKED_PRECONDITION:id"
    parsed = urlsplit(URL)
    assert parsed.scheme in ("postgres", "postgresql") and parsed.hostname, "BLOCKED_PRECONDITION:external_postgres"
    assert parse_qs(parsed.query).get("sslmode", [""])[0] in ("require", "verify-ca", "verify-full"), "BLOCKED_PRECONDITION:TLS"
    # The user owns the Neon project; source itself cannot prove its isolation.
    print(f"PASS|NEON_V5|precondition|phase={PHASE}|synthetic_only=true")

validate_preconditions()

@DBOS.step()
def increment_exactly_if_first_completion():
    with psycopg.connect(URL, connect_timeout=20) as connection:
        row = connection.execute(
            f"UPDATE {TABLE} SET n=n+1 WHERE id=%s RETURNING n",
            (WORKFLOW,),
        ).fetchone()
        assert row and row[0] == 1, "STEP_RESULT_UNEXPECTED"
        return row[0]

@DBOS.workflow()
def workflow():
    return increment_exactly_if_first_completion()

if PHASE == "seed":
    with psycopg.connect(URL, connect_timeout=20) as connection:
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {TABLE} (id text PRIMARY KEY, n integer NOT NULL)"
        )
        connection.execute(
            f"INSERT INTO {TABLE} (id,n) VALUES (%s,0) ON CONFLICT (id) DO NOTHING",
            (WORKFLOW,),
        )
DBOS(config={"name": APP, "application_version": "neon-v5-001", "system_database_url": URL})
try:
    DBOS.launch()
    with SetWorkflowID(WORKFLOW):
        result = workflow()
    with psycopg.connect(URL, connect_timeout=20) as connection:
        row = connection.execute(f"SELECT n FROM {TABLE} WHERE id=%s", (WORKFLOW,)).fetchone()
    assert row and row[0] == result == 1, "DURABLE_REPLAY_FAILED"
    print(f"PASS|NEON_V5|phase={PHASE}|same_workflow=true|count={row[0]}")
finally:
    DBOS.destroy(workflow_completion_timeout_sec=5)
