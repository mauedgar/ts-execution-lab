"""G4 parallel Neon branch synthetic race/rollback/recovery qualification."""
import concurrent.futures
import json
import os
import sys
from pathlib import Path

import psycopg

db_url = os.environ["DATABASE_URL"]
run_id = os.environ["GITHUB_RUN_ID"]
candidate = os.environ["G4_CANDIDATE"]
assert candidate in ("a", "b")
assert os.environ["BRANCH_CREATED"] == "true"
assert os.environ["BRANCH_ID"].startswith("br-")
expected_owner = f"{run_id}-{candidate}"


def compete() -> int:
    with psycopg.connect(db_url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ts_ee_g4.claim(id, owner, state)
                   VALUES (1, %s, 'initial')
                   ON CONFLICT (id) DO NOTHING""",
                (expected_owner,),
            )
            return cur.rowcount


def cas() -> int:
    with psycopg.connect(db_url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE ts_ee_g4.claim
                   SET state='acquired'
                   WHERE id=1 AND state='initial'""",
            )
            return cur.rowcount


def run() -> None:
    with psycopg.connect(db_url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            assert cur.fetchone() == ("ts_ee_neon_ci", "ts_ee_neon_ci_owner")
            cur.execute("CREATE SCHEMA ts_ee_g4")
            cur.execute(
                """CREATE TABLE ts_ee_g4.claim(
                     id integer PRIMARY KEY,
                     owner text NOT NULL,
                     state text NOT NULL CHECK(state IN ('initial','acquired','recovered'))
                   )"""
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        inserts = list(pool.map(lambda _: compete(), range(4)))
    assert sorted(inserts) == [0, 0, 0, 1], inserts

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        cas_results = list(pool.map(lambda _: cas(), range(4)))
    assert sorted(cas_results) == [0, 0, 0, 1], cas_results

    try:
        with psycopg.connect(db_url, connect_timeout=20) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO ts_ee_g4.claim(id, owner, state)
                       VALUES (2, %s, 'initial')""",
                    (expected_owner,),
                )
                raise RuntimeError("G4_SIMULATED_ABORT")
    except RuntimeError as exc:
        assert str(exc) == "G4_SIMULATED_ABORT"

    with psycopg.connect(db_url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*)::int FROM ts_ee_g4.claim WHERE id=2")
            assert cur.fetchone()[0] == 0, "rollback did not occur"
            cur.execute(
                """INSERT INTO ts_ee_g4.claim(id, owner, state)
                   VALUES (2, %s, 'recovered')""",
                (expected_owner,),
            )

    with psycopg.connect(db_url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,owner,state FROM ts_ee_g4.claim ORDER BY id")
            assert cur.fetchall() == [
                (1, expected_owner, "acquired"),
                (2, expected_owner, "recovered"),
            ]

    receipt = {
        "gate": "G4",
        "run_id": run_id,
        "candidate": candidate,
        "branch_id": os.environ["BRANCH_ID"],
        "project": "odd-pond-18952360",
        "result": "PASS",
        "positive_tests": ["four_thread_insert_one_winner", "four_thread_cas_one_winner", "isolated_branch_commit_readback"],
        "negative_tests": ["unique_conflict_noop", "rollback_forced_abort", "no_row_after_rollback"],
        "recovery": "fresh_transaction_after_abort",
        "product_effect": "NONE",
    }
    Path(os.environ["G4_SQL_RECEIPT"]).write_text(
        json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("TS_EE_G4_RACE_ROLLBACK_RECOVERY_PASS")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print("TS_EE_G4_SQL_FAILED_" + type(exc).__name__)
        sys.exit(1)
