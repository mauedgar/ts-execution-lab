"""A02-LAN source-only original native join negative checks, no host/SQL I/O."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from a02_lan.control_join import ATTEMPT, SCHEMA, DEVICES, check


def synthetic() -> dict:
    t = 1794260000000000000
    providers, intents, results = {}, {}, {}
    for side, (device, site) in DEVICES.items():
        backend = 201 if side == "A" else 202
        host_hash = ("a" if side == "A" else "b") * 64
        output = "A02_LAN_ORIGINAL_NATIVE_" + side + "_SOURCE_ONLY_FIXTURE"
        providers[side] = {
            "device_id":device, "site":site, "host_sha256":host_hash,
            "native_original_pid":11 if side == "A" else 12,
            "native_run_start_ns":t, "native_run_end_ns":t + 60_000_000_000,
            "native_exit_code":0,
            "native_original_output_sha256":sha256(output.encode("utf-8")).hexdigest(),
            "native_original_output":output,
            "native_backend_pid":backend,
            "native_backend_start":"2026-11-09T21:00:00+00:00",
            "native_client_pid":301 if side == "A" else 302,
            "original_tool":"mcp__Remote_Desktop_Commander__start_process",
        }
        body = {k:v for k,v in providers[side].items()
                if k != "native_original_output"}
        providers[side]["native_receipt_body"] = body
        providers[side]["native_receipt_sha256"] = sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        common = {
            "execution_attempt":ATTEMPT, "writer":side,
            "site_claim":site, "host_sha256":host_hash,
            "client_process_pid":providers[side]["native_client_pid"],
            "backend_pid":backend,
            "backend_start":"2026-11-09T21:00:00+00:00",
            "mutation_id":"A10-A02-LAN-"+side,
            "mutation_fingerprint":("e" if side == "A" else "f") * 64,
            "packet_sha256":"1" * 64, "expected_revision":0,
            "scope":"A10-DISPOSABLE-SINGLE-SCOPE",
            "product_effect":"NONE",
        }
        intents[side] = {
            **common, "phase":"BEFORE_FIRST_DISPATCH",
            "effect":"UNKNOWN_PENDING", "created_ns":t + 2_000_000_000,
        }
        results[side] = {
            **common, "status":"A02_LAN_WRITER_RESULT",
            "disposition":"CONFIRMED" if side=="A" else "NONE_STALE",
            "effect":"CONFIRMED" if side=="A" else "NONE",
            "revision":1 if side=="A" else None,
            "site":site, "host_evidence":"EXTERNAL_PROVIDER_JOIN_REQUIRED",
            "server_effect_only":True,
            "phase":"CLIENT_RESULT_DURABLE",
            "recorded_ns":t + 40_000_000_000,
        }
    return {
        "schema":SCHEMA, "execution_attempt":ATTEMPT,
        "source_commit":"0" * 40, "packet_sha256":"1" * 64,
        "provider":providers, "intents":intents, "results":results,
        "holder":{
            "status":"A02_LAN_HOLDER_RELEASED_NO_MUTATION",
            "backend_pid":100, "acquired_epoch_ns":t+5_000_000_000,
            "released_epoch_ns":t+30_000_000_000,
            "execution_attempt":ATTEMPT, "product_effect":"NONE",
        },
        "witness":{
            "status":"A02_LAN_SERVER_LOCK_GRAPH_AWAITING_HOST_JOIN",
            "expected_holder":100,"observer_pid":303,
            "observed_epoch_ns":t+10_000_000_000,
            "waiters":[
                {"writer":"A","pid":201,"wait_event_type":"Lock",
                 "wait_event":"transactionid","blockers":[100],
                 "backend_start":"2026-11-09T21:00:00+00:00",
                 "client_addr_sha256":"3"*64},
                {"writer":"B","pid":202,"wait_event_type":"Lock",
                 "wait_event":"transactionid","blockers":[201],
                 "backend_start":"2026-11-09T21:00:00+00:00",
                 "client_addr_sha256":"4"*64},
            ],
            "server_lock_graph_only":True,
            "physical_hosts":"EXTERNAL_NATIVE_JOIN_REQUIRED",
            "product_effect":"NONE","neon":"NOT_RUN",
        },
        "database":{
            "status":"A02_LAN_DB_SINGLE_WINNER_AWAITING_CONTROL_JOIN",
            "winner":"A", "revision":1,
            "counts":{"heads":1,"events":1,"receipts":1},
            "state_sha256":"5"*64,"event_sha256":"6"*64,
            "product_js_bytes_exact":True,
            "physical_host_join":"NOT_RUN",
            "writer_acks":"NOT_RECONCILED",
            "product_effect":"NONE","neon":"NOT_RUN",
        },
    }


def main():
    base = synthetic()
    good = check(base, frozen_source_commit="0"*40,
                 frozen_packet_sha256="1"*64)
    assert good["physical_two_host_pass"] is False
    assert good["status"] == "STRUCTURAL_JOIN_COHERENT_PENDING_PROVIDER_NATIVE_READBACK"
    assert good["winner"] == "A" and good["loser"] == "B"
    cases = [
        ("same-device", lambda x: x["provider"]["B"].update(
            device_id=x["provider"]["A"]["device_id"])),
        ("same-host-fingerprint", lambda x: x["provider"]["B"].update(
            host_sha256=x["provider"]["A"]["host_sha256"])),
        ("forged-native-tool", lambda x: x["provider"]["B"].update(
            original_tool="CLAIMED_FROM_APPLICATION")),
        ("wrong-backend", lambda x: x["provider"]["B"].update(native_backend_pid=999)),
        ("absent-writer-result", lambda x: x["results"].pop("B")),
        ("unknown-writer-effect", lambda x: x["results"]["B"].update(
            effect="UNKNOWN",disposition="UNKNOWN_FENCED")),
        ("double-confirmer", lambda x: x["results"]["B"].update(
            effect="CONFIRMED",disposition="CONFIRMED",revision=1)),
        ("wrong-count", lambda x: x["database"]["counts"].update(receipts=2)),
        ("no-holder-overlap", lambda x: x["holder"].update(
            released_epoch_ns=x["holder"]["acquired_epoch_ns"]+1)),
        ("lock-chain-break", lambda x: x["witness"]["waiters"][1].update(blockers=[777])),
        ("wrong-attempt", lambda x: x.update(execution_attempt="REPLAY")),
        ("wrong-packet", lambda x: x["intents"]["A"].update(packet_sha256="0"*64)),
        ("wrong-frozen-source", lambda x: x.update(source_commit="f"*40)),
        ("wrong-frozen-packet", lambda x: x.update(packet_sha256="0"*64)),
        ("provider-output-tampered", lambda x: x["provider"]["A"].update(
            native_original_output="TAMPERED")),
        ("provider-receipt-tampered", lambda x: x["provider"]["B"]["native_receipt_body"].update(
            native_backend_pid=999)),
        ("backend-start-not-bound", lambda x: x["witness"]["waiters"][1].update(
            backend_start="2027-11-09T21:00:00+00:00")),
    ]
    failures = 0
    for name, mutate in cases:
        x = deepcopy(base)
        mutate(x)
        try:
            check(x, frozen_source_commit="0"*40,
                  frozen_packet_sha256="1"*64)
        except (ValueError, KeyError, TypeError):
            failures += 1
        else:
            raise AssertionError("JOIN_NEGATIVE_FALSE_ACCEPT_"+name)
    assert failures == 17, "JOIN_NEGATIVE_COUNT"
    print(json.dumps({
        "status":"A02_LAN_STRUCTURAL_JOIN_SOURCE_NEGATIVES_PASS",
        "negative_cases":failures,
        "native_host_proof":"NOT_RUN",
        "database":"NOT_RUN",
        "product_effect":"NONE",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
