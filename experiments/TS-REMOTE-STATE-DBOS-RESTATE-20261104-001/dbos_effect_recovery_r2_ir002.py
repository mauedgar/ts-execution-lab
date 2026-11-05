"""IR002-F001: isolated DBOS step with SQL receipt, crash-window and collision proof.

This is NONPRODUCT synthetic PostgreSQL on 127.0.0.1 only. A DBOS step is
at-least-once before its checkpoint. The receipt+business UPDATE share a single
psycopg transaction so a retry can reconcile without duplicating the effect.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
import sys

import psycopg
from dbos import DBOS, SetWorkflowID


URL = os.environ["DBOS_SYSTEM_DATABASE_URL"]
ID = os.environ["TS_REMOTE_WORKFLOW_ID"]
assert ID.startswith("ts-remote-r2-ir002-"), "synthetic R2 ID namespace required"
assert ("@127.0.0.1:5432/" in URL or "@localhost:5432/" in URL), (
    "only local synthetic PostgreSQL is permitted"
)
APP_NAME = "ts_remote_r2_ir002_effect_guard"
AUTHORITY = "AUTH-SYNTHETIC-IR002"


def command(id_: str, *, amount: int = 1, expected_revision: int = 0,
            authority: str = AUTHORITY) -> dict:
    assert isinstance(id_, str) and id_.startswith("ts-remote-r2-ir002-")
    assert type(amount) is int and type(expected_revision) is int
    assert isinstance(authority, str) and authority
    return {
        "operation": "increment",
        "workflow_id": id_,
        "amount": amount,
        "expected_revision": expected_revision,
        "authority_refs": [authority],
    }


def fingerprint(cmd: dict) -> str:
    raw = json.dumps(cmd, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()


def schema_and_seed(id_: str) -> None:
    with psycopg.connect(URL) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS ts_r2_ir002_demo(
                workflow_id text PRIMARY KEY, effects integer NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS ts_r2_ir002_receipts(
                workflow_id text PRIMARY KEY,
                fingerprint char(64) NOT NULL,
                original_result integer NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS ts_r2_ir002_invocations(
                invocation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                workflow_id text NOT NULL
            )
        """)
        db.execute("""
            INSERT INTO ts_r2_ir002_demo(workflow_id,effects)
            VALUES (%s,0) ON CONFLICT DO NOTHING
        """, (id_,))


def totals(id_: str) -> tuple[int, int, int]:
    with psycopg.connect(URL) as db:
        value = db.execute(
            "SELECT effects FROM ts_r2_ir002_demo WHERE workflow_id=%s", (id_,)
        ).fetchone()
        receipts = db.execute(
            "SELECT count(*) FROM ts_r2_ir002_receipts WHERE workflow_id=%s", (id_,)
        ).fetchone()[0]
        invocations = db.execute(
            "SELECT count(*) FROM ts_r2_ir002_invocations WHERE workflow_id=%s", (id_,)
        ).fetchone()[0]
    assert value is not None, "missing synthetic aggregate"
    return value[0], receipts, invocations


def apply_effect(cmd: dict) -> tuple[int, bool]:
    """Atomically insert immutable receipt plus effect, or reconcile an exact replay.

    An INSERT conflict waits for the other transaction. The winner increments
    exactly once. A different command reusing the same key is never accepted.
    """
    id_ = cmd["workflow_id"]
    fp = fingerprint(cmd)
    with psycopg.connect(URL) as db:
        inserted = db.execute("""
            INSERT INTO ts_r2_ir002_receipts
              (workflow_id,fingerprint,original_result)
            VALUES (%s,%s,1)
            ON CONFLICT (workflow_id) DO NOTHING
            RETURNING original_result
        """, (id_, fp)).fetchone()
        if inserted:
            # A new command may mutate only the explicitly qualified synthetic
            # target; all validation and the UPDATE are in the receipt transaction.
            if cmd != command(id_):
                raise ValueError("INVALID_SYNTHETIC_COMMAND")
            update = db.execute("""
                UPDATE ts_r2_ir002_demo SET effects=effects+1
                WHERE workflow_id=%s AND effects=0 RETURNING effects
            """, (id_,)).fetchone()
            if update is None or update[0] != 1:
                raise AssertionError("MISSING_OR_NONZERO_INITIAL_STATE")
            return update[0], False

        previous = db.execute("""
            SELECT fingerprint,original_result
            FROM ts_r2_ir002_receipts WHERE workflow_id=%s FOR UPDATE
        """, (id_,)).fetchone()
        if previous is None:
            raise AssertionError("RECEIPT_CONFLICT_WITHOUT_ROW")
        if previous[0].strip() != fp:
            raise ValueError("R2_EFFECT_IDENTITY_COLLISION")
        current = db.execute(
            "SELECT effects FROM ts_r2_ir002_demo WHERE workflow_id=%s",
            (id_,),
        ).fetchone()
        if current is None or current[0] != previous[1]:
            raise AssertionError("RECEIPT_EFFECT_MISMATCH")
        return previous[1], True


@DBOS.step()
def guarded_step() -> int:
    # Separate test-only invocation audit is intentionally not a business effect.
    with psycopg.connect(URL) as db:
        db.execute(
            "INSERT INTO ts_r2_ir002_invocations(workflow_id) VALUES (%s)", (ID,)
        )
    result, _reconciled = apply_effect(command(ID))
    # Crash inside the decorated step AFTER the application COMMIT and BEFORE
    # returning to DBOS, so the DBOS step cannot have checkpointed this return.
    if os.environ.get("TS_REMOTE_R2_CRASH_AFTER_EFFECT_COMMIT") == "1":
        os._exit(73)
    return result


@DBOS.workflow()
def durable() -> int:
    return guarded_step()


def run_dbos(phase: str) -> None:
    DBOS(config={
        "name": APP_NAME,
        "application_version": "1",
        "system_database_url": URL,
    })
    try:
        DBOS.launch()
        with SetWorkflowID(ID):
            result = durable()
        effects, receipts, invocations = totals(ID)
        assert result == effects == receipts == 1, (
            phase, result, effects, receipts, invocations
        )
        if phase == "first":
            assert invocations == 1, ("unexpected duplicate first step", invocations)
        if phase == "second":
            assert invocations == 1, ("completed step re-executed", invocations)
        if phase == "recover":
            assert invocations >= 2, ("missing post-crash step replay", invocations)
        print(
            f"PASS|R2|dbos_effect_guard|phase={phase}|"
            f"effects={effects}|receipts={receipts}|step_invocations={invocations}",
            flush=True,
        )
    finally:
        DBOS.destroy(workflow_completion_timeout_sec=5)


def negative_checks() -> None:
    # Must follow a previously committed original effect with the exact same ID.
    before = totals(ID)
    assert before[0:2] == (1, 1), before
    replay = apply_effect(command(ID))
    assert replay == (1, True), replay
    for altered in (
        command(ID, amount=2),
        command(ID, expected_revision=1),
        command(ID, authority="AUTH-OTHER-IR002"),
    ):
        try:
            apply_effect(altered)
        except ValueError as exc:
            assert str(exc) == "R2_EFFECT_IDENTITY_COLLISION", exc
        else:
            raise AssertionError("MUTATION_COLLISION_ACCEPTED")
        assert totals(ID) == before, "collision mutated synthetic state"
    print("PASS|R2|negative_identity|payload_revision_authority=rejected|no_effect")


def local_race() -> None:
    contender_id = ID + "-two-clients"
    schema_and_seed(contender_id)
    assert totals(contender_id)[:2] == (0, 0), "contender id already consumed"
    with ThreadPoolExecutor(max_workers=2) as pool:
        paired = list(pool.map(lambda _n: apply_effect(command(contender_id)), range(2)))
    assert sorted(paired) == [(1, False), (1, True)], paired
    assert totals(contender_id)[:2] == (1, 1)
    print("PASS|R2|same_key_concurrency|effects=1|receipt=1|reconciled=1")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python dbos_effect_recovery_r2_ir002.py <first|second|crash|recover|negative|concurrent>")
    phase = sys.argv[1]
    assert phase in ("first", "second", "crash", "recover", "negative", "concurrent")
    if phase in ("first", "crash"):
        schema_and_seed(ID)
        assert totals(ID) == (0, 0, 0), "effect ID already used; no retry"
    if phase == "crash":
        assert os.environ.get("TS_REMOTE_R2_CRASH_AFTER_EFFECT_COMMIT") == "1", (
            "crash test must explicitly enable fault injection"
        )
        run_dbos("crash")
        raise AssertionError("injected crash did not occur")
    if phase in ("first", "second", "recover"):
        assert os.environ.get("TS_REMOTE_R2_CRASH_AFTER_EFFECT_COMMIT") != "1"
        run_dbos(phase)
    elif phase == "negative":
        negative_checks()
    elif phase == "concurrent":
        local_race()


if __name__ == "__main__":
    main()
