"""A11 NONPRODUCT real PG16 two-connection lock overlap and original JS CAS.

All mutation payloads come from original Product JS proposals produced by
qualify_lock.cjs. PostgreSQL lock holder and contender are two distinct backends
on ONE ephemeral GitHub runner; never claim two physically independent hosts.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import sys
import threading
import time

from worker import SCOPE, connect, parse_proposal
from ts_global.bridge import StorageRejected, apply, read


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def contender(proposal: dict, ready: threading.Event, observed: list) -> str:
    with connect() as conn:
        observed.append(conn.info.backend_pid)
        ready.set()
        command, _meta = parse_proposal(proposal)
        try:
            value = apply(conn, command)
        except StorageRejected as exc:
            require(exc.code == "STALE_REVISION", "UNEXPECTED_CONTENDER_REJECTION")
            return "NONE_STALE"
        return value.disposition


def main() -> None:
    data = sys.stdin.buffer.read(6 * 1024 * 1024 + 1)
    require(len(data) <= 6 * 1024 * 1024, "INPUT_BOUND")
    request = json.loads(data.decode("utf-8", "strict"))
    require(type(request) is dict and set(request) == {"a", "b"}, "EXACT_REQUEST")
    a_command, _ = parse_proposal(request["a"])
    b_command, _ = parse_proposal(request["b"])
    require(a_command.scope == b_command.scope == SCOPE, "WRONG_SCOPE")
    require(a_command.mutation_id != b_command.mutation_id, "ID_COLLISION")
    require(a_command.expected_revision == b_command.expected_revision == 5,
            "EXACT_CAS_REVISION")
    require(a_command.previous_event_hash == b_command.previous_event_hash,
            "COMMON_PREDECESSOR_REQUIRED")
    require(a_command.event_line != b_command.event_line,
            "TWO_DISTINCT_JS_EVENTS_REQUIRED")
    started = threading.Event()
    b_pid = []
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        with connect() as writer_a, connect() as observer:
            pid_a = writer_a.info.backend_pid
            require(type(pid_a) is int and pid_a > 0, "WRITER_A_BACKEND")
            with writer_a.transaction():
                # Explicit real row-lock hold. The B bridge.apply() will
                # request this SAME global head via SELECT ... FOR UPDATE.
                locked = writer_a.execute(
                    "SELECT revision FROM ts_r3_global_head_20261107_001.head "
                    "WHERE scope=%s FOR UPDATE", (SCOPE,),
                ).fetchone()
                require(locked is not None and locked["revision"] == 5,
                        "LOCKED_HEAD_REVISION")
                future = executor.submit(contender, request["b"], started, b_pid)
                require(started.wait(timeout=5.0), "CONTENDER_NOT_READY")
                require(len(b_pid) == 1 and b_pid[0] != pid_a, "INDEPENDENT_BACKENDS")
                overlap = False
                wait_event = None
                for _ in range(35):
                    row = observer.execute(
                        "SELECT pg_blocking_pids(%s) AS blockers,"
                        " wait_event_type, wait_event FROM pg_stat_activity WHERE pid=%s",
                        (b_pid[0], b_pid[0]),
                    ).fetchone()
                    if row is not None and pid_a in row["blockers"] and                        row["wait_event_type"] == "Lock":
                        overlap = True
                        wait_event = row["wait_event"]
                        break
                    if future.done():
                        break
                    time.sleep(0.1)
                require(overlap, "REAL_SERVER_LOCK_OVERLAP_NOT_OBSERVED")
                require(not future.done(), "WAITER_UNEXPECTEDLY_FINISHED")
                # Existing real PostgreSQL bridge performs the real CAS/write
                # in a nested savepoint; outer transaction makes it durable
                # only after leaving this block, then B sees STALE.
                receipt_a = apply(writer_a, a_command)
                require(receipt_a.disposition == "CONFIRMED" and
                        receipt_a.revision == 6, "WRITER_A_CAS_FAILED")
            # Outer transaction commits, B is now unblocked.
            result_b = future.result(timeout=10.0)
            require(result_b == "NONE_STALE", "CONTENDER_SHOULD_BE_STALE")
            checked = read(observer, SCOPE)
            require(checked.revision == 6, "FINAL_REVISION_INCONSISTENT")
            counts = observer.execute(
                "SELECT (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.head"
                " WHERE scope=%s) AS heads,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.events"
                " WHERE scope=%s) AS events,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.receipts"
                " WHERE scope=%s) AS receipts", (SCOPE, SCOPE, SCOPE),
            ).fetchone()
            require(counts == {"heads": 1, "events": 6, "receipts": 6},
                    "CAS_EFFECT_COUNTS")
        print(json.dumps({
            "status": "A11_REAL_PG16_POSITIVE_LOCK_OVERLAP_PASS",
            "host_count": 1,
            "backend_count": 2,
            "observer_independent": True,
            "server_blockers_observed": True,
            "wait_event_type": "Lock",
            "wait_event": wait_event,
            "winner": "CONFIRMED",
            "contender": "NONE_STALE",
            "heads": 1, "events": 6, "receipts": 6, "revision": 6,
            "neon": "NOT_RUN", "product_effect": "NONE",
        }, sort_keys=True))
    finally:
        executor.shutdown(wait=True, cancel_futures=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Credentials, SQL details and raw exceptions never enter logs.
        print("A11_REAL_PG16_LOCK_PROBE_FAIL_CLOSED", file=sys.stderr)
        raise SystemExit(2)
