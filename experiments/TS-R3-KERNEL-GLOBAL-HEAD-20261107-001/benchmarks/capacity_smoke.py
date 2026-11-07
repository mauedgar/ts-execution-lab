#!/usr/bin/env python3
"""A003 bounded in-memory performance and memory smoke, experimental NONPRODUCT.

Only uses the frozen 14-event Node synthetic oracle and existing FakeConn;
the simulator has deepcopy transaction overhead and MUST NOT be described as
real PostgreSQL throughput, psycopg client performance or Product parity.
No secrets, network, SQL, file writes or Product mutations.
"""
from __future__ import annotations

import base64
import gc
from hashlib import sha1, sha256
import json
import resource
import signal
from pathlib import Path
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_bridge import FakeConn, GOLDEN, genesis, mutation  # noqa: E402
from ts_global.bridge import apply, initialize, read  # noqa: E402

COUNTS = (0, 1, 7, 14)
MAX_MUTATIONS = len(GOLDEN["mutations"])
GOLDEN_GIT_BLOB = "e9937b4bf48a1e87d8d23d7742d9729334172d68"
CAP_RLIMIT_AS_BYTES = 512 * 1024 * 1024
CAP_CPU_SECONDS = 30
CAP_WALL_SECONDS = 45


def _time_limit(_signal: int, _frame: object) -> None:
    raise TimeoutError("A003_WALL_TIME_LIMIT")


def _preflight() -> None:
    if sys.platform != "linux":
        raise RuntimeError("A003_LINUX_ONLY_RESOURCE_LIMITS")
    fixture = (ROOT / "oracle" / "golden.json").read_bytes()
    git_hash = sha1(b"blob " + str(len(fixture)).encode("ascii") +
                    b"\x00" + fixture).hexdigest()
    if git_hash != GOLDEN_GIT_BLOB:
        raise RuntimeError("A003_FROZEN_FIXTURE_MISMATCH")
    if MAX_MUTATIONS != 14 or COUNTS != (0, 1, 7, 14):
        raise RuntimeError("A003_UNEXPECTED_WORKLOAD")
    resource.setrlimit(resource.RLIMIT_AS,
                       (CAP_RLIMIT_AS_BYTES, CAP_RLIMIT_AS_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU,
                       (CAP_CPU_SECONDS, CAP_CPU_SECONDS))
    signal.signal(signal.SIGALRM, _time_limit)
    signal.alarm(CAP_WALL_SECONDS)


def qualify(count: int) -> dict[str, object]:
    if not 0 <= count <= MAX_MUTATIONS:
        raise ValueError("UNBOUNDED_CAPACITY_CASE")
    gc.collect()
    tracemalloc.start()
    db = FakeConn()
    initial = time.perf_counter_ns()
    view = initialize(db, GOLDEN["scope"], genesis())
    per_mutation: list[int] = []
    for index in range(count):
        before = time.perf_counter_ns()
        receipt = apply(db, mutation(index))
        per_mutation.append(time.perf_counter_ns() - before)
        expected = GOLDEN["mutations"][index]
        if (receipt.disposition != "CONFIRMED" or
                receipt.revision != index + 1 or receipt.replay is not False or
                receipt.event_hash != expected["event_hash"] or
                receipt.fingerprint != mutation(index).fingerprint()):
            raise AssertionError("BAD_SYNTHETIC_RECEIPT")
    before_read = time.perf_counter_ns()
    view = read(db, GOLDEN["scope"])
    final_read_ns = time.perf_counter_ns() - before_read
    total_ns = time.perf_counter_ns() - initial
    _current, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    expected_state = (genesis() if count == 0 else
                      base64.b64decode(GOLDEN["mutations"][count - 1]["state_b64"]))
    expected_stream = b"".join(
        base64.b64decode(GOLDEN["mutations"][i]["line_b64"])
        for i in range(count)
    )
    if (view.revision != count or view.state_bytes != expected_state or
            view.event_bytes != expected_stream or
            view.events_sha256 != sha256(expected_stream).hexdigest() or
            len(db.events) != count or len(db.receipts) != count):
        raise AssertionError("SYNTHETIC_REPLAY_PARITY_FAILED")
    return {
        "count": count,
        "status": "PASS_SYNTHETIC_ONLY",
        "total_ns": total_ns,
        "last_read_ns": final_read_ns,
        "last_mutation_ns": per_mutation[-1] if per_mutation else 0,
        "peak_tracemalloc_bytes": peak_bytes,
        "total_event_bytes": len(expected_stream),
        "snapshot_bytes": len(expected_state),
        "sql_simulated_statement_count": db.queries,
        "backend": "FakeConn/deepcopy",
        "physical_postgresql": "NOT_RUN",
        "psycopg_client": "NOT_RUN",
        "product_js_zod": "NOT_RUN",
    }


def main() -> int:
    _preflight()
    observed = [qualify(n) for n in COUNTS]
    print(json.dumps({
        "schema": "ts-r3-a003-bounded-capacity/v1",
        "source": "frozen 14-event synthetic oracle",
        "source_git_blob": GOLDEN_GIT_BLOB,
        "rlimit_as_bytes": CAP_RLIMIT_AS_BYTES,
        "cpu_seconds_ceiling": CAP_CPU_SECONDS,
        "wall_seconds_ceiling": CAP_WALL_SECONDS,
        "python": sys.version.split()[0],
        "cases": observed,
        "scope": "NONPRODUCT / NO_DB / NOT_SCALE_PROOF",
        "limitations": ("FakeConn deepcopies on transactions; short fixture; "
                        "no PostgreSQL/driver/concurrent authors; "
                        "wall-time and tracemalloc are runner-dependent"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({
            "schema": "ts-r3-a003-bounded-capacity/v2",
            "status": "FAILED",
            "error_type": type(error).__name__,
            "error_code": str(error)[:200],
            "Product": "NONE",
            "PostgreSQL": "NOT_RUN",
        }, sort_keys=True))
        raise SystemExit(2)
