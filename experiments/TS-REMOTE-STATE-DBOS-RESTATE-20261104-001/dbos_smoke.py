"""DBOS synthetic one-workflow replay across two processes, no Product data."""
import os, sys
import psycopg
from dbos import DBOS, SetWorkflowID

URL=os.environ["DBOS_SYSTEM_DATABASE_URL"]
ID="ts-remote-state-20261104-synthetic-workflow-001"

@DBOS.step()
def count_once():
    with psycopg.connect(URL) as c:
        return c.execute("UPDATE ts_demo SET n=n+1 WHERE id=%s RETURNING n",(ID,)).fetchone()[0]

@DBOS.workflow()
def workflow():
    return count_once()

if __name__=="__main__":
    mode=sys.argv[1]
    if mode=="first":
        with psycopg.connect(URL) as c:
            c.execute("CREATE TABLE IF NOT EXISTS ts_demo(id text PRIMARY KEY,n int NOT NULL)")
            c.execute("INSERT INTO ts_demo VALUES (%s,0) ON CONFLICT DO NOTHING",(ID,))
    DBOS(config={"name":"ts_remote_state_lab","application_version":"1","system_database_url":URL})
    try:
        DBOS.launch()
        with SetWorkflowID(ID):
            value=workflow()
        with psycopg.connect(URL) as c:
            count=c.execute("SELECT n FROM ts_demo WHERE id=%s",(ID,)).fetchone()[0]
        assert count==value==1,(mode,count,value)
        print(f"PASS|DBOS|phase={mode}|workflow_id={ID}|step_count={count}")
    finally:
        DBOS.destroy(workflow_completion_timeout_sec=5)
