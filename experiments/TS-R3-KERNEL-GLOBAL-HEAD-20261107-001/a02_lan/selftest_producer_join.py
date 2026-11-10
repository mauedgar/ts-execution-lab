"""A02-LAN SOURCE_ONLY actual writer() -> fsynced JSON -> control_join boundary.

Exercises the real producer function, actual create-only receipt serializer and
the existing strict join validator with a *fake* DB connection and fake native
provider metadata. Never opens SQL or establishes a physical-host proof.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a02_lan import lan_probe
from a02_lan.control_join import check
from a02_lan.selftest_control_join import synthetic
from ts_global.bridge import StorageRejected

T = 1794260000000000000
SOURCE = "0" * 40
PACKET_SHA = "1" * 64
EXPECTED_BACKEND_START = "2026-11-09T21:00:00+00:00"


class Row:
    def fetchone(self):
        return {"started": EXPECTED_BACKEND_START}


class FakeConn:
    def __init__(self, backend_pid):
        self.info = SimpleNamespace(backend_pid=backend_pid)
        self.queries = []
    def execute(self, sql):
        assert sql == (
            "SELECT backend_start::text AS started "
            "FROM pg_catalog.pg_stat_activity WHERE pid=pg_backend_pid()"
        ), "FAKE_DB_QUERY_NOT_IN_READ_ONLY_PREFLIGHT"
        self.queries.append(sql)
        return Row()


class Command:
    def __init__(self, side):
        self.scope = "A10-DISPOSABLE-SINGLE-SCOPE"
        self.mutation_id = "A10-A02-LAN-" + side
        self.expected_revision = 0
        self.side = side
    def fingerprint(self):
        return ("e" if self.side == "A" else "f") * 64


def original_writer_receipts(report, side, home, *, losing):
    native = report["provider"][side]
    site = native["site"]
    command = Command(side)
    conn = FakeConn(native["native_backend_pid"])
    folder = home / ("ts-r3-a02-lan-physical-race-fixture-" + side.lower())
    folder.mkdir(mode=0o700, exist_ok=False)

    def original_apply(_conn, _command):
        assert _conn is conn and _command is command
        original_apply.calls += 1
        if losing:
            raise StorageRejected("STALE_REVISION")
        return SimpleNamespace(disposition="CONFIRMED", revision=1)
    original_apply.calls = 0

    output = StringIO()
    with patch.object(lan_probe, "asserted_host_identity",
                      return_value=(native["host_sha256"],
                                    report["execution_attempt"])), \
         patch.object(lan_probe, "private_receipt_dir", return_value=folder), \
         patch.object(lan_probe, "apply", side_effect=original_apply), \
         patch.object(lan_probe.time, "time_ns",
                      side_effect=[T + 2_000_000_000, T + 40_000_000_000]), \
         patch.dict(os.environ, {lan_probe.SHA_ENV: PACKET_SHA}), \
         redirect_stdout(output):
        lan_probe.writer(conn, command, site, side.lower())
    assert original_apply.calls == 1 and len(conn.queries) == 1

    text = output.getvalue()
    client = json.loads(text)
    intent_bytes = (folder / ("writer-" + side.lower() + ".intent.json")).read_bytes()
    result_bytes = (folder / ("writer-" + side.lower() + ".result.json")).read_bytes()
    intent = json.loads(intent_bytes)
    result = json.loads(result_bytes)
    assert client["disposition"] == result["disposition"]
    assert client["effect"] == result["effect"]
    assert client["revision"] == result["revision"]
    assert result["backend_start"] == EXPECTED_BACKEND_START
    assert intent["backend_start"] == EXPECTED_BACKEND_START
    assert intent["phase"] == "BEFORE_FIRST_DISPATCH"
    assert result["phase"] == "CLIENT_RESULT_DURABLE"
    if losing:
        assert result["disposition"] == "NONE_STALE"
        assert result["revision"] is None and "revision" in result
    else:
        assert result["disposition"] == "CONFIRMED"
        assert result["revision"] == 1

    # Create-only intent blocks any second dispatch, even with same identity.
    with patch.object(lan_probe, "asserted_host_identity",
                      return_value=(native["host_sha256"],
                                    report["execution_attempt"])), \
         patch.object(lan_probe, "private_receipt_dir", return_value=folder), \
         patch.object(lan_probe, "apply", side_effect=original_apply), \
         patch.object(lan_probe.time, "time_ns", return_value=T + 45_000_000_000), \
         patch.dict(os.environ, {lan_probe.SHA_ENV: PACKET_SHA}):
        try:
            lan_probe.writer(conn, command, site, side.lower())
        except FileExistsError:
            pass
        else:
            raise AssertionError("REPLAY_WRITER_DISPATCH_WAS_ACCEPTED")
    assert original_apply.calls == 1, "DUPLICATE_WRITER_SQL_DISPATCH"

    # Native receipt objects below are *synthetic* and never provider proof.
    native["native_client_pid"] = os.getpid()
    native["native_original_output"] = text
    native["native_original_output_sha256"] = sha256(text.encode()).hexdigest()
    native["native_backend_start"] = EXPECTED_BACKEND_START
    body = {k: v for k, v in native.items()
            if k not in ("native_original_output", "native_receipt_sha256",
                         "native_receipt_body")}
    native["native_receipt_body"] = body
    native["native_receipt_sha256"] = sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    report["intents"][side] = intent
    report["results"][side] = result
    return intent_bytes, result_bytes


def main():
    report = synthetic()
    with TemporaryDirectory(prefix="ts-r3-a02-actual-producer-join-",
                            dir=str(Path.home())) as d:
        home = Path(d)
        original_writer_receipts(report, "A", home, losing=False)
        original_writer_receipts(report, "B", home, losing=True)
    result = check(report, frozen_source_commit=SOURCE,
                   frozen_packet_sha256=PACKET_SHA)
    assert result["status"] == (
        "STRUCTURAL_JOIN_COHERENT_PENDING_PROVIDER_NATIVE_READBACK")
    assert result["winner"] == "A" and result["loser"] == "B"
    assert result["physical_two_host_pass"] is False
    negative_cases = [
        ("missing-stale-revision", lambda o:
         o["results"]["B"].pop("revision")),
        ("non-null-stale-revision", lambda o:
         o["results"]["B"].update(revision=0)),
        ("winner-null-revision", lambda o:
         o["results"]["A"].update(revision=None)),
        ("missing-writer-result", lambda o:
         o["results"].pop("B")),
        ("unknown-losing-effect", lambda o:
         o["results"]["B"].update(effect="UNKNOWN",
                                  disposition="UNKNOWN_FENCED")),
        ("backend-start-forgery", lambda o:
         o["results"]["A"].update(backend_start="INJECTED")),
    ]
    rejected = 0
    for label, change in negative_cases:
        altered = deepcopy(report)
        change(altered)
        try:
            check(altered, frozen_source_commit=SOURCE,
                  frozen_packet_sha256=PACKET_SHA)
        except (ValueError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError("PRODUCER_JOIN_FALSE_ACCEPT_" + label)
    assert rejected == 6
    print(json.dumps({
        "status": "A02_LAN_REAL_WRITER_SERIALIZED_RECEIPTS_JOIN_SOURCE_PASS",
        "positive_producer_paths": ["CONFIRMED", "NONE_STALE"],
        "negative_cases": rejected,
        "duplicate_dispatch_rejected": True,
        "postgresql": "NOT_RUN",
        "native_provider_attestation": "NOT_RUN",
        "product_effect": "NONE",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
