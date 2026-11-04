"""R2 experimental DBOS durable two-process replay; isolated synthetic CI PostgreSQL only."""
import os
import sys
import psycopg
from dbos import DBOS, SetWorkflowID

URL = os.environ["DBOS_SYSTEM_DATABASE_URL"]
ID = os.environ["TS_REMOTE_WORKFLOW_ID"]
assert ID.startswith("ts-remote-r2-ir001-repair-"), ID

@DBOS.step()
def single_effect():
    with psycopg.connect(URL) as db:
        return db.execute("UPDATE ts_r2_demo SET effects=effects+1 WHERE id=%s RETURNING effects",(ID,)).fetchone()[0]

@DBOS.workflow()
def durable():
    return single_effect()

if __name__ == "__main__":
    phase = sys.argv[1]
    assert phase in ("first","second"), phase
    if phase == "first":
        with psycopg.connect(URL) as db:
            db.execute("CREATE TABLE IF NOT EXISTS ts_r2_demo(id text PRIMARY KEY,effects int NOT NULL)")
            db.execute("INSERT INTO ts_r2_demo VALUES (%s,0) ON CONFLICT DO NOTHING",(ID,))
    DBOS(config={"name":"ts_remote_r2_ir001_repair","application_version":"1","system_database_url":URL})
    try:
        DBOS.launch()
        with SetWorkflowID(ID):
            result = durable()
        with psycopg.connect(URL) as db:
            effects = db.execute("SELECT effects FROM ts_r2_demo WHERE id=%s",(ID,)).fetchone()[0]
        assert result == effects == 1, (phase,result,effects)
        print(f"PASS|R2|dbos_durable_replay|phase={phase}|effects={effects}")
    finally:
        DBOS.destroy(workflow_completion_timeout_sec=5)
