"""Offline byte-for-byte Product JS state-kernel-v0 -> experimental PG bridge.

All data is captured from actual disposable Product JS filesystem generations
in the same GitHub Actions job. FakeConn is an in-memory test double: this
checks code and serialization compatibility, NOT native PostgreSQL semantics.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import sys

from ts_global.bridge import Mutation, StorageRejected, apply, initialize, read, reconcile
from test_bridge import FakeConn


def decoded(value: str) -> bytes:
    assert type(value) is str, "BASE64_STRING_REQUIRED"
    return base64.b64decode(value, validate=True)


def main() -> int:
    assert len(sys.argv) == 2, "ONE_DISPOSABLE_FIXTURE_REQUIRED"
    file = Path(sys.argv[1]).resolve(strict=True)
    fixture = json.loads(file.read_text(encoding="utf-8"))
    assert fixture["kind"] == "PRODUCT_JS_V0_EXACT_GENERATIONS"
    assert fixture["product_git_commit"] == "26509b74d50207bb247dcc9bdb929a63f5451e88"
    assert fixture["source_blobs"] == {
        "contracts": "5d2d3a8a24ebc17339675e0c801595956e0cd353",
        "index": "0219b92e5f546407a6060a6dc449865c14c7f144",
        "store": "f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a",
    }
    scope = fixture["scope"]
    assert scope == "ts-r3-e1-product-bridge-20261107-002"
    captures = fixture["generations"]
    assert type(captures) is list and len(captures) == 20
    assert [row["revision"] for row in captures] == list(range(20))

    db = FakeConn()
    gen = captures[0]
    genbytes = decoded(gen["state_b64"])
    assert gen["payload_b64"] is None and gen["event_line_b64"] is None
    assert decoded(gen["events_b64"]) == b""
    beginning = initialize(db, scope, genbytes)
    assert beginning.revision == 0 and beginning.state_bytes == genbytes
    assert beginning.event_bytes == b""
    assert read(db, scope).state_bytes == genbytes

    prior_hash = None
    wire_events = b""
    auth = hashlib.sha256(b"SYNTHETIC_E1_PRODUCT_GOLDEN_AUTHORITY_ONLY").hexdigest()
    receipts = []
    for rev in range(1, 20):
        stage = captures[rev]
        previous = captures[rev - 1]
        state = decoded(stage["state_b64"])
        payload = decoded(stage["payload_b64"])
        event_line = decoded(stage["event_line_b64"])
        wire_events += event_line
        assert decoded(stage["events_b64"]) == wire_events, "EXACT_PRODUCT_EVENT_BYTES"
        assert stage["previous_hash"] == prior_hash
        assert stage["event_hash"] == hashlib.sha256(payload).hexdigest()
        assert event_line.endswith(b"\n")
        assert state.endswith(b"\n")
        assert len(state) <= 4 * 1024 * 1024
        assert len(payload) <= 4 * 1024 * 1024
        assert len(wire_events) > 0
        assert previous["revision"] + 1 == rev
        command = Mutation(
            scope=scope,
            mutation_id=f"e1-source-stage-{rev:02}",
            expected_revision=rev - 1,
            previous_event_hash=prior_hash,
            payload_bytes=payload,
            event_line=event_line,
            state_bytes=state,
            authority_fingerprint=auth,
        )
        receipt = apply(db, command)
        assert receipt.disposition == "CONFIRMED" and receipt.revision == rev
        assert receipt.replay is False
        assert receipt.event_hash == stage["event_hash"]
        view = read(db, scope)
        assert view.revision == rev and view.state_bytes == state
        assert view.event_bytes == wire_events
        assert view.last_event_hash == stage["event_hash"]
        assert view.state_sha256 == hashlib.sha256(state).hexdigest()
        assert view.events_sha256 == hashlib.sha256(wire_events).hexdigest()
        confirmation = reconcile(db, command)
        assert (confirmation.disposition, confirmation.replay, confirmation.revision) == (
            "CONFIRMED", True, rev
        )
        receipts.append(command)
        # Bind the next event to this source Product generation's exact hash.
        prior_hash = stage["event_hash"]

    # Read-only receipt replay must not append or modify a second event.
    before_head = read(db, scope)
    duplicate = apply(db, receipts[-1])
    assert duplicate.disposition == "CONFIRMED" and duplicate.replay is True
    after_head = read(db, scope)
    assert after_head.state_bytes == before_head.state_bytes
    assert after_head.event_bytes == before_head.event_bytes
    assert after_head.revision == 19

    print(json.dumps({
        "status": "PRODUCT_JS_NATIVE_19_EVENTS_BRIDGE_FAKECONN_BYTE_PARITY_PASS",
        "product_exact_generations": 20,
        "product_events": 19,
        "bridge_receipts": 19,
        "raw_event_sha256": hashlib.sha256(wire_events).hexdigest(),
        "raw_final_state_sha256": hashlib.sha256(after_head.state_bytes).hexdigest(),
        "backend": "FAKECONN_IN_MEMORY_NO_POSTGRESQL",
        "postgresql_transactionality": "NOT_RUN",
        "sql_effect": "NONE",
        "product_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
