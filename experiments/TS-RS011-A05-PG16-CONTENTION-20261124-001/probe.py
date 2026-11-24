#!/usr/bin/env python3
"""Disposable, single-host PostgreSQL 16 lock-contention experiment.

NONPRODUCT. Refuses to run outside an explicit GitHub Actions localhost fixture.
Never connects to Neon, a notebook, Product, or a nonloopback database.
"""
import json
import os
import subprocess
import sys
import time

WORKER_SQL = """
BEGIN;
WITH updated AS (
  UPDATE rs011_a05.head
  SET revision=revision+1
  WHERE scope='fixture' AND revision=0
  RETURNING scope, revision
), event_written AS (
  INSERT INTO rs011_a05.events(scope,revision,writer)
  SELECT scope,revision,'{writer}' FROM updated
  RETURNING scope,revision
), receipt_written AS (
  INSERT INTO rs011_a05.receipts(scope,mutation_id,revision,fingerprint)
  SELECT scope,'mutation-{writer}',revision,'fp-{writer}'
  FROM event_written
  RETURNING scope
)
SELECT (SELECT count(*) FROM updated),
       (SELECT count(*) FROM event_written),
       (SELECT count(*) FROM receipt_written);
{hold}
COMMIT;
"""

SETUP_SQL = """
CREATE SCHEMA rs011_a05;
CREATE TABLE rs011_a05.head(
 scope text PRIMARY KEY, revision integer NOT NULL CHECK(revision >= 0));
CREATE TABLE rs011_a05.events(
 scope text NOT NULL, revision integer NOT NULL, writer text NOT NULL,
 PRIMARY KEY(scope,revision));
CREATE TABLE rs011_a05.receipts(
 scope text NOT NULL, mutation_id text NOT NULL, revision integer NOT NULL,
 fingerprint text NOT NULL, PRIMARY KEY(scope,mutation_id));
INSERT INTO rs011_a05.head VALUES ('fixture',0);
"""

def require_fixture():
    checks = {
        "GITHUB_ACTIONS": "true",
        "TS_RS011_EPHEMERAL": "yes",
        "PGHOST": "127.0.0.1",
        "PGPORT": "5432",
        "PGUSER": "postgres",
        "PGDATABASE": "postgres",
        "PGPASSWORD": "rs011-only-disposable",
    }
    for name, exact in checks.items():
        if os.environ.get(name) != exact:
            raise RuntimeError("BLOCKED_NON_EPHEMERAL_" + name)
    if sys.version_info[:3] != (3, 15, 2):
        raise RuntimeError("BLOCKED_PYTHON_VERSION")

def env_for(app):
    v = os.environ.copy()
    v["PGAPPNAME"] = app
    return v

def psql(sql, app="rs011_observer", timeout=6):
    cmd = ["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1"]
    r = subprocess.run(cmd, input=sql, text=True, capture_output=True,
                       timeout=timeout, check=False, env=env_for(app))
    if r.returncode != 0:
        raise RuntimeError("PSQL_FAILED_" + app + "_RC_" + str(r.returncode)
                           + ": " + r.stderr[-600:])
    if len(r.stdout) > 16384:
        raise RuntimeError("OVERSIZED_OUTPUT")
    return r.stdout.strip()

def spawn(sql, app):
    p = subprocess.Popen(["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, env=env_for(app))
    assert p.stdin is not None
    p.stdin.write(sql)
    p.stdin.close()
    return p

def finish(p, name):
    try:
        rc = p.wait(timeout=24)
    except subprocess.TimeoutExpired as exc:
        p.kill()
        p.wait()
        raise RuntimeError("UNKNOWN_OR_TIMED_OUT_" + name) from exc
    assert p.stdout is not None and p.stderr is not None
    stdout, stderr = p.stdout.read(), p.stderr.read()
    if len(stdout) > 16384 or len(stderr) > 16384:
        raise RuntimeError("WORKER_OUTPUT_TOO_LARGE_" + name)
    if rc != 0:
        raise RuntimeError("WORKER_FAILED_" + name + "_RC_" + str(rc) + ": " + stderr[-600:])
    return stdout

def probe_until(sql, expected, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        got = psql(sql)
        if got == expected:
            return True
        time.sleep(0.08)
    return False

def run():
    require_fixture()
    version = psql("SHOW server_version_num;")
    if not version.startswith("16"):
        raise RuntimeError("BLOCKED_PG_VERSION_" + version)
    psql(SETUP_SQL)

    a = b = None
    try:
        a = spawn(WORKER_SQL.format(writer="A", hold="SELECT pg_sleep(9);"), "rs011_A")
        a_active = probe_until("""
SELECT count(*) FROM pg_stat_activity
WHERE application_name='rs011_A' AND state='active'
AND query LIKE '%pg_sleep%';
""", "1")
        if not a_active:
            raise RuntimeError("NO_A_LOCK_HOLD_OBSERVED")

        b = spawn(WORKER_SQL.format(writer="B", hold=""), "rs011_B")
        b_lock_wait = probe_until("""
SELECT count(*) FROM pg_stat_activity
WHERE application_name='rs011_B' AND wait_event_type='Lock'
AND state='active';
""", "1", seconds=5)
        if not b_lock_wait:
            raise RuntimeError("NO_CONCURRENT_B_LOCK_WAIT_OBSERVED")

        lock_snapshot = psql("""
SELECT application_name || '|' || pid || '|' ||
       COALESCE(wait_event_type,'none')
FROM pg_stat_activity WHERE application_name IN ('rs011_A','rs011_B')
ORDER BY application_name;
""")
        if "rs011_A|" not in lock_snapshot or "rs011_B|" not in lock_snapshot:
            raise RuntimeError("MISSING_DISTINCT_BACKENDS")
        a_pid = b_pid = None
        for line in lock_snapshot.splitlines():
            parts = line.split("|")
            if len(parts) != 3:
                raise RuntimeError("INVALID_LOCK_SNAPSHOT")
            if parts[0] == "rs011_A":
                a_pid = parts[1]
            elif parts[0] == "rs011_B":
                b_pid = parts[1]
                if parts[2] != "Lock":
                    raise RuntimeError("B_NOT_WAITING_ON_LOCK")
        if a_pid == b_pid or not a_pid or not b_pid:
            raise RuntimeError("SAME_BACKEND_PID")

        a_out = finish(a, "A")
        b_out = finish(b, "B")
        if "1|1|1" not in a_out.splitlines():
            raise RuntimeError("A_NOT_SINGLE_WINNER")
        if "0|0|0" not in b_out.splitlines():
            raise RuntimeError("B_NOT_STALE_LOSER")

        final = psql("""
SELECT (SELECT revision FROM rs011_a05.head WHERE scope='fixture'),
       (SELECT count(*) FROM rs011_a05.events),
       (SELECT count(*) FROM rs011_a05.receipts),
       (SELECT count(*) FROM rs011_a05.receipts WHERE mutation_id='mutation-A'),
       (SELECT count(*) FROM rs011_a05.receipts WHERE mutation_id='mutation-B');
""")
        if final != "1|1|1|1|0":
            raise RuntimeError("UNEXPECTED_FINAL_STATE_" + final)
        # This evidence is a one-host/two-connection lock overlap, not two-host failover.
        print(json.dumps({
            "status": "ONE_HOST_PG16_REAL_LOCK_CONTENTION_PASS",
            "server_version_num": version,
            "host_count": 1,
            "independent_postgres_backends": [a_pid, b_pid],
            "b_wait_event_type": "Lock",
            "a_statement_counts": "1|1|1",
            "b_statement_counts": "0|0|0",
            "final_counts": final,
            "physical_p0_p2": "NOT_DISPATCHED",
            "neon": "NOT_CONTACTED",
            "kernel_product_effect": "NONE",
            "lost_commit_ack": "NOT_TESTED",
        }, sort_keys=True))
    finally:
        for p in (a, b):
            if p is not None and p.poll() is None:
                p.kill()
                p.wait(timeout=5)

if __name__ == "__main__":
    run()
