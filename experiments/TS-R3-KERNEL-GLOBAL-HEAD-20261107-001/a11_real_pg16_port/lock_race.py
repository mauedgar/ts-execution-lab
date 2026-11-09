"""A11 NONPRODUCT real PG16 lock overlap between two real CAS writers.

A third connection owns a disposable head row lock, two other independent
connections call the ORIGINAL bridge.apply() from transaction status IDLE,
while a fourth observes both as PostgreSQL server lock waiters. Never nest
bridge.apply inside a transaction: it forbids false durable savepoint commits.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import sys
import threading
import time

from worker import SCOPE, connect, parse_proposal
from ts_global.bridge import StorageRejected, apply, read


STAGE = "INPUT"


def require(ok: bool, code: str) -> None:
    if not ok:
        raise AssertionError(code)


def competing_writer(name: str, proposal: dict, ready: threading.Event,
                     identities: dict) -> str:
    with connect() as conn:
        # Create and record independent PostgreSQL backend BEFORE real CAS.
        identities[name] = conn.info.backend_pid
        ready.set()
        command, _ = parse_proposal(proposal)
        try:
            result = apply(conn, command)  # top-level durable transaction
        except StorageRejected as exc:
            require(exc.code == "STALE_REVISION",
                    "UNEXPECTED_WRITER_REJECTION_" + name)
            return "NONE_STALE"
        require(result.disposition == "CONFIRMED", "UNEXPECTED_RECEIPT_" + name)
        return result.disposition


def monitor_writers(observer, writer_pids: list[int],
                    holder_pid: int, max_checks: int = 40) -> bool:
    require(len(writer_pids) == 2 and writer_pids[0] != writer_pids[1],
            "INDEPENDENT_WRITERS_REQUIRED")
    for _ in range(max_checks):
        states = []
        for pid in writer_pids:
            row = observer.execute(
                "SELECT wait_event_type,wait_event,pg_blocking_pids(%s) AS blockers "
                "FROM pg_catalog.pg_stat_activity WHERE pid=%s",
                (pid, pid),
            ).fetchone()
            states.append(row)
        if all(row is not None and row["wait_event_type"] == "Lock" and
               len(row["blockers"]) > 0 for row in states):
            # A is held directly by the holder; B may wait behind the
            # holder or the first queued writer.
            require(holder_pid in states[0]["blockers"] or
                    holder_pid in states[1]["blockers"],
                    "NO_HOLDER_IN_POSTGRES_BLOCKING_GRAPH")
            return True
        time.sleep(0.1)
    return False


def main() -> None:
    global STAGE
    STAGE = "REQUEST_PARSE"
    raw = sys.stdin.buffer.read(6 * 1024 * 1024 + 1)
    require(len(raw) <= 6 * 1024 * 1024, "INPUT_BOUND")
    request = json.loads(raw.decode("utf-8", "strict"))
    require(type(request) is dict and set(request) == {"a", "b"}, "EXACT_REQUEST")
    proposal_a, _ = parse_proposal(request["a"])
    proposal_b, _ = parse_proposal(request["b"])
    require(proposal_a.scope == proposal_b.scope == SCOPE, "WRONG_SCOPE")
    require(proposal_a.mutation_id != proposal_b.mutation_id, "ID_COLLISION")
    require(proposal_a.expected_revision == proposal_b.expected_revision == 5,
            "EXACT_CAS_REVISION")
    require(proposal_a.previous_event_hash == proposal_b.previous_event_hash,
            "COMMON_PREDECESSOR_REQUIRED")
    require(proposal_a.event_line != proposal_b.event_line,
            "TWO_DISTINCT_JS_EVENTS_REQUIRED")

    started_a, started_b = threading.Event(), threading.Event()
    identities: dict[str, int] = {}
    executor = ThreadPoolExecutor(max_workers=2)
    try:
        STAGE = "CONNECTION_AND_THREAD"
        with connect() as holder, connect() as observer:
            holder_pid = holder.info.backend_pid
            observer_pid = observer.info.backend_pid
            STAGE = "BEGIN_LOCK_TRANSACTION"
            with holder.transaction():
                locked = holder.execute(
                    "SELECT revision FROM ts_r3_global_head_20261107_001.head "
                    "WHERE scope=%s FOR UPDATE", (SCOPE,),
                ).fetchone()
                require(locked is not None and locked["revision"] == 5,
                        "LOCKED_HEAD_REVISION")
                STAGE = "START_CONTENDER"
                future_a = executor.submit(
                    competing_writer, "A", request["a"], started_a, identities)
                future_b = executor.submit(
                    competing_writer, "B", request["b"], started_b, identities)
                require(started_a.wait(timeout=5.0) and
                        started_b.wait(timeout=5.0),
                        "BOTH_WRITERS_NOT_READY")
                pid_a, pid_b = identities["A"], identities["B"]
                require(len({holder_pid, observer_pid, pid_a, pid_b}) == 4,
                        "FOUR_DISTINCT_PG_BACKENDS_REQUIRED")
                STAGE = "OBSERVE_LOCK_WAIT"
                overlapping = monitor_writers(observer, [pid_a, pid_b], holder_pid)
                require(overlapping, "TWO_REAL_WRITERS_LOCK_OVERLAP_NOT_PROVEN")
                require(not future_a.done() and not future_b.done(),
                        "WRITER_FINISHED_BEFORE_LOCK_RELEASE")
                STAGE = "RELEASE_HOLDER"
            # Lock holder commits NOTHING, releasing row lock; two independent
            # real bridge writers now race from IDLE, one wins, one is stale.
            STAGE = "JOIN_CONTENDER"
            outcomes = [future_a.result(timeout=10.0),
                        future_b.result(timeout=10.0)]
            require(sorted(outcomes) == ["CONFIRMED", "NONE_STALE"],
                    "CAS_SINGLE_WINNER_FAILED")
            STAGE = "READ_POSTCONDITIONS"
            state = read(observer, SCOPE)
            require(state.revision == 6, "FINAL_REVISION_INCONSISTENT")
            row = observer.execute(
                "SELECT (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.head"
                " WHERE scope=%s) AS heads,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.events"
                " WHERE scope=%s) AS events,"
                " (SELECT COUNT(*) FROM ts_r3_global_head_20261107_001.receipts"
                " WHERE scope=%s) AS receipts", (SCOPE, SCOPE, SCOPE),
            ).fetchone()
            require(row == {"heads": 1, "events": 6, "receipts": 6},
                    "CAS_EFFECT_COUNTS")
        STAGE = "EMIT_RESULT"
        print(json.dumps({
            "status": "A11_REAL_PG16_POSITIVE_LOCK_OVERLAP_PASS",
            "host_count": 1,
            "backend_count": 4,
            "writer_backend_count": 2,
            "observer_independent": True,
            "server_blockers_observed": True,
            "two_writers_waited_concurrently": True,
            "wait_event_type": "Lock",
            "winner": "CONFIRMED",
            "contender": "NONE_STALE",
            "winner_side": "A" if outcomes[0] == "CONFIRMED" else "B",
            "heads": 1, "events": 6, "receipts": 6, "revision": 6,
            "neon": "NOT_RUN", "product_effect": "NONE",
        }, sort_keys=True))
    finally:
        executor.shutdown(wait=True, cancel_futures=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Only bounded fixed stage/type marker. Never SQL, DSN, password, stack.
        allowed = {"REQUEST_PARSE", "CONNECTION_AND_THREAD",
                   "BEGIN_LOCK_TRANSACTION", "START_CONTENDER",
                   "OBSERVE_LOCK_WAIT", "RELEASE_HOLDER", "JOIN_CONTENDER",
                   "READ_POSTCONDITIONS", "EMIT_RESULT"}
        stage = STAGE if STAGE in allowed else "UNKNOWN"
        kind = type(exc).__name__
        if kind not in {"AssertionError", "StorageRejected", "OperationalError",
                        "ProgrammingError", "TransactionError", "TimeoutError",
                        "ValueError", "TypeError"}:
            kind = "OTHER"
        print("A11_LOCK_STAGE_" + stage + "_" + kind.upper(),
              file=sys.stderr)
        raise SystemExit(2)
