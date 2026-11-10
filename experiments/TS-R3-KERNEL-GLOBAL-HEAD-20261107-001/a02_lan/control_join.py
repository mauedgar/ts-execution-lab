"""NONPRODUCT A02-LAN strict structural original-effect join.

This is NOT provider-native attestation. Original Commander process receipts,
device identity and timestamps MUST be independently read back by Control.
Outputs never classify a physical race PASS without that external readback.
No network, SQL, credentials, subprocesses or Product modification.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
import sys
from pathlib import Path

ATTEMPT = "TS-R3-A02-LAN-PHYSICAL-RACE-20261109-001-A001"
SCHEMA = "ts-r3-a02-lan-control-join/v1"
DEVICES = {
    "A": ("40cc0b10-fa7b-4a6a-98cf-1c94f93791b2", "NOTEBOOK"),
    "B": ("777b57a0-70df-4bd6-b9ed-f6a4998e6022", "DESKTOP"),
}
HEX = re.compile(r"[a-f0-9]{64}\Z")
GIT = re.compile(r"[a-f0-9]{40}\Z")
PID = re.compile(r"[1-9][0-9]*\Z")


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def exact(obj, keys, code):
    need(type(obj) is dict and set(obj) == set(keys), code)
    return obj


def digest(value) -> bool:
    return type(value) is str and HEX.fullmatch(value) is not None


def positive(n) -> bool:
    return type(n) is int and 0 < n < 2**31


def zero_or_one(n) -> bool:
    return type(n) is int and n in (0, 1)


def check(report: dict) -> dict:
    exact(report, ("schema", "execution_attempt", "source_commit",
                   "packet_sha256", "provider", "intents", "results",
                   "holder", "witness", "database"), "JOIN_SCHEMA_EXACT")
    need(report["schema"] == SCHEMA and
         report["execution_attempt"] == ATTEMPT,
         "WRONG_ORIGINAL_ATTEMPT")
    need(type(report["source_commit"]) is str and
         GIT.fullmatch(report["source_commit"]) is not None and
         digest(report["packet_sha256"]), "SOURCE_OR_PACKET_HASH")
    provider = exact(report["provider"], ("A", "B"), "PROVIDER_KEYS")
    intents = exact(report["intents"], ("A", "B"), "INTENT_KEYS")
    results = exact(report["results"], ("A", "B"), "RESULT_KEYS")
    pids, hosts, devs = [], [], []
    for side in ("A", "B"):
        device_id, expected_site = DEVICES[side]
        native = exact(provider[side],
                       ("device_id", "site", "host_sha256",
                        "native_original_pid", "native_run_start_ns",
                        "native_run_end_ns", "native_exit_code",
                        "native_original_output_sha256",
                        "native_receipt_sha256", "native_backend_pid",
                        "native_client_pid", "original_tool"),
                       "NATIVE_RECEIPT_KEYS")
        need(native["device_id"] == device_id and native["site"] == expected_site
             and native["original_tool"] ==
             "mcp__Remote_Desktop_Commander__start_process",
             "WRONG_PROVIDER_OR_PHYSICAL_HOST")
        need(digest(native["host_sha256"]) and
             digest(native["native_original_output_sha256"]) and
             digest(native["native_receipt_sha256"]),
             "ORIGINAL_PROVIDER_HASHES_MISSING")
        need(all(positive(native[key]) for key in
                 ("native_original_pid", "native_backend_pid",
                  "native_client_pid", "native_run_start_ns",
                  "native_run_end_ns")) and
             native["native_exit_code"] == 0 and
             native["native_run_start_ns"] < native["native_run_end_ns"],
             "ORIGINAL_NATIVE_PROCESS_NOT_TERMINAL")
        raw_intent = exact(intents[side],
                           ("phase", "effect", "execution_attempt",
                            "writer", "site_claim", "host_sha256",
                            "client_process_pid", "backend_pid",
                            "mutation_id", "mutation_fingerprint",
                            "packet_sha256", "expected_revision", "scope",
                            "product_effect", "created_ns"),
                           "INTENT_RECEIPT_KEYS")
        need(raw_intent["phase"] == "BEFORE_FIRST_DISPATCH" and
             raw_intent["effect"] == "UNKNOWN_PENDING" and
             raw_intent["execution_attempt"] == ATTEMPT and
             raw_intent["writer"] == side and
             raw_intent["site_claim"] == expected_site and
             raw_intent["host_sha256"] == native["host_sha256"] and
             raw_intent["client_process_pid"] == native["native_client_pid"] and
             raw_intent["backend_pid"] == native["native_backend_pid"] and
             raw_intent["mutation_id"] == "A10-A02-LAN-" + side and
             raw_intent["packet_sha256"] == report["packet_sha256"] and
             digest(raw_intent["mutation_fingerprint"]) and
             raw_intent["expected_revision"] == 0 and
             raw_intent["scope"] == "A10-DISPOSABLE-SINGLE-SCOPE" and
             raw_intent["product_effect"] == "NONE" and
             positive(raw_intent["created_ns"]), "INTENT_NOT_BOUND_TO_ORIGINAL")
        raw_result = exact(results[side],
                           tuple(raw_intent) + ("status", "disposition",
                                                "effect", "revision", "site",
                                                "host_evidence",
                                                "server_effect_only",
                                                "phase", "recorded_ns"),
                           "RESULT_RECEIPT_KEYS")
        for field in raw_intent:
            if field in ("phase", "effect", "created_ns"):
                continue
            need(raw_result[field] == raw_intent[field],
                 "RESULT_INTENT_IDENTITY_MISMATCH")
        need(raw_result["status"] == "A02_LAN_WRITER_RESULT" and
             raw_result["phase"] == "CLIENT_RESULT_DURABLE" and
             raw_result["site"] == expected_site and
             raw_result["host_evidence"] == "EXTERNAL_PROVIDER_JOIN_REQUIRED" and
             raw_result["server_effect_only"] is True and
             positive(raw_result["recorded_ns"]) and
             raw_result["recorded_ns"] >= raw_intent["created_ns"],
             "RESULT_NOT_DURABLE_OR_WRONG_SOURCE")
        need((raw_result["disposition"], raw_result["effect"]) in (
                ("CONFIRMED", "CONFIRMED"), ("NONE_STALE", "NONE")),
             "UNKNOWN_EFFECT_MUST_REMAIN_FENCED")
        if raw_result["effect"] == "CONFIRMED":
            need(raw_result["revision"] == 1, "WINNER_REVISION")
        else:
            need(raw_result["revision"] is None, "STALE_MUST_HAVE_NULL_REVISION")
        hosts.append(native["host_sha256"])
        devs.append(native["device_id"])
        pids.append(native["native_backend_pid"])

    need(len(set(hosts)) == 2 and len(set(devs)) == 2 and
         len(set(pids)) == 2, "TWO_PHYSICAL_HOSTS_AND_DISTINCT_BACKENDS_REQUIRED")

    holder = exact(report["holder"],
                   ("status", "backend_pid", "acquired_epoch_ns",
                    "released_epoch_ns", "execution_attempt",
                    "product_effect"), "HOLDER_KEYS")
    need(holder["status"] == "A02_LAN_HOLDER_RELEASED_NO_MUTATION" and
         positive(holder["backend_pid"]) and
         positive(holder["acquired_epoch_ns"]) and
         positive(holder["released_epoch_ns"]) and
         holder["acquired_epoch_ns"] < holder["released_epoch_ns"] and
         holder["execution_attempt"] == ATTEMPT and
         holder["product_effect"] == "NONE", "HOLDER_TIMELINE")

    witness = exact(report["witness"],
                    ("status", "expected_holder", "observer_pid",
                     "observed_epoch_ns", "waiters", "server_lock_graph_only",
                     "physical_hosts", "product_effect", "neon"),
                    "WITNESS_KEYS")
    need(witness["status"] == "A02_LAN_SERVER_LOCK_GRAPH_AWAITING_HOST_JOIN" and
         witness["expected_holder"] == holder["backend_pid"] and
         positive(witness["observer_pid"]) and
         holder["acquired_epoch_ns"] < witness["observed_epoch_ns"] <
         holder["released_epoch_ns"] and
         witness["server_lock_graph_only"] is True and
         witness["physical_hosts"] == "EXTERNAL_NATIVE_JOIN_REQUIRED" and
         witness["product_effect"] == "NONE" and witness["neon"] == "NOT_RUN",
         "LOCK_TIMELINE_OR_SOURCE")
    waiters = witness["waiters"]
    need(type(waiters) is list and len(waiters) == 2, "EXACT_TWO_WAITERS_REQUIRED")
    observed = {}
    for w in waiters:
        exact(w, ("writer", "pid", "wait_event_type", "wait_event",
                  "blockers", "backend_start", "client_addr_sha256"),
              "WAITER_KEYS")
        need(w["writer"] in ("A", "B") and w["writer"] not in observed and
             positive(w["pid"]) and w["wait_event_type"] == "Lock" and
             type(w["blockers"]) is list and w["blockers"] and
             all(positive(k) for k in w["blockers"]) and
             type(w["backend_start"]) is str and len(w["backend_start"]) > 8 and
             digest(w["client_addr_sha256"]), "INVALID_WAITER")
        observed[w["writer"]] = w
    need(set(observed) == {"A", "B"} and
         all(observed[side]["pid"] == provider[side]["native_backend_pid"]
             for side in ("A", "B")), "PROVIDER_BACKEND_BINDING_FAILED")
    blockers = {w["pid"]: w["blockers"] for w in observed.values()}
    def reaches_holder(pid, seen):
        if pid == holder["backend_pid"]:
            return True
        if pid in seen:
            return False
        return any(reaches_holder(n, seen | {pid}) for n in
                   blockers.get(pid, ()) if n == holder["backend_pid"] or n in blockers)
    need(all(reaches_holder(w["pid"], set()) for w in observed.values()),
         "LOCK_GRAPH_NOT_TRANSITIVE_TO_HOLDER")
    db = exact(report["database"],
               ("status", "winner", "revision", "counts",
                "state_sha256", "event_sha256", "product_js_bytes_exact",
                "physical_host_join", "writer_acks", "product_effect", "neon"),
               "DATABASE_VERIFIER_KEYS")
    counts = exact(db["counts"], ("heads", "events", "receipts"), "DB_COUNTS_KEYS")
    need(db["status"] == "A02_LAN_DB_SINGLE_WINNER_AWAITING_CONTROL_JOIN" and
         db["revision"] == 1 and
         counts == {"heads": 1, "events": 1, "receipts": 1} and
         digest(db["state_sha256"]) and digest(db["event_sha256"]) and
         db["product_js_bytes_exact"] is True and
         db["physical_host_join"] == "NOT_RUN" and
         db["writer_acks"] == "NOT_RECONCILED" and
         db["product_effect"] == "NONE" and db["neon"] == "NOT_RUN",
         "DB_PARITY_NOT_PROVEN")
    need(db["winner"] in ("A", "B"), "WINNER_NOT_ID")
    winner = db["winner"]
    loser = "B" if winner == "A" else "A"
    need(results[winner]["effect"] == "CONFIRMED" and
         results[loser]["effect"] == "NONE" and
         results[loser]["disposition"] == "NONE_STALE",
         "WINNER_LOSER_EFFECTS_DO_NOT_MATCH_DB")
    return {
        "status": "STRUCTURAL_JOIN_COHERENT_PENDING_PROVIDER_NATIVE_READBACK",
        "execution_attempt": ATTEMPT,
        "winner": winner,
        "loser": loser,
        "requires": "INDEPENDENT_CONTROL_VERIFICATION_OF_ORIGINAL_PROVIDER_RECEIPTS",
        "physical_two_host_pass": False,
        "product_effect": "NONE",
        "neon": "NOT_RUN",
    }


def main() -> None:
    need(len(sys.argv) == 2, "ONE_INPUT_FILE_REQUIRED")
    path = Path(sys.argv[1]).resolve(strict=True)
    need(path.is_file() and path.stat().st_size <= 48 * 1024,
         "JOIN_INPUT_FILE_LIMIT")
    obj = json.loads(path.read_text("utf-8"))
    print(json.dumps(check(obj), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        code = str(exc)
        if not re.fullmatch(r"[A-Z0-9_]+", code):
            code = "INVALID_JOIN"
        print(code, file=sys.stderr)
        raise SystemExit(2)
