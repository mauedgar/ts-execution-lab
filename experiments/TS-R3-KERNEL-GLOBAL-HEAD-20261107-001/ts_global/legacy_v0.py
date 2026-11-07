"""Conservative read-only mirror of the *frozen* State Kernel V0 wire contract.

Source oracle: tecnotron-ai@26509b74d50207bb247dcc9bdb929a63f5451e88
contracts.js blob 5d2d3a8a24ebc17339675e0c801595956e0cd353;
store.js blob f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a.

NOT Product authority: never selects legal transitions, authorizes operations,
issues grants or decides whether an external execution effect may retry. Only
checks untrusted saved state/bytes against frozen transport invariants; the real
Product validator remains the semantic oracle at cutover.
"""
from __future__ import annotations

from datetime import datetime
import json
import re
from typing import Any

VERSION = "tecnotron-state-kernel/v0"
KINDS = ("Milestone", "TaskCycle", "Operation", "ExecutionAttempt")
STATES = {
    "Milestone": ("PLANNED", "ACTIVE", "CLOSED", "CANCELLED"),
    "TaskCycle": ("READY", "ACTIVE", "BLOCKED", "PENDING_ACCEPTANCE", "CLOSED", "CANCELLED"),
    "Operation": ("DEFINED", "READY", "RUNNING", "BLOCKED", "COMPLETED", "FAILED", "CANCELLED"),
    "ExecutionAttempt": ("PREPARED", "DISPATCHED", "RUNNING", "COMPLETED", "BLOCKED", "FAILED", "UNAVAILABLE", "CANCELLED", "UNKNOWN"),
}
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
ISO_PATTERN = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
HEX_GIT = re.compile(r"[a-f0-9]{40,64}\Z")
REF_TYPES = ("AUTHORITY", "EVIDENCE", "ARTIFACT", "GIT_OBJECT")


def ensure(ok: bool, code: str = "PRODUCT_V0_CONTRACT_MISMATCH") -> None:
    if not ok:
        raise ValueError(code)


def obj(value: Any, fields: set[str]) -> None:
    ensure(type(value) is dict and set(value) == fields)


def string(value: Any) -> bool:
    return type(value) is str and bool(value) and value.strip() == value


def refstring(value: Any) -> bool:
    return string(value)


def identifier(value: Any) -> bool:
    return string(value) and ID_PATTERN.fullmatch(value) is not None and value not in (
        "__proto__", "constructor", "prototype")


def iso(value: Any) -> bool:
    if type(value) is not str or ISO_PATTERN.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return True


def refs(value: Any, *, expected_kind: str | None = None) -> None:
    ensure(type(value) is list)
    for r in value:
        ensure(type(r) is dict and set(r).issubset({"kind", "id", "location", "sha256", "git_oid"})
               and {"kind", "id"}.issubset(r))
        ensure(r["kind"] in REF_TYPES and refstring(r["id"]))
        if expected_kind is not None:
            ensure(r["kind"] == expected_kind)
        if "location" in r:
            p = r["location"]
            ensure(string(p) and not p.startswith("/") and ".." not in p and
                   not re.match(r"^[A-Za-z]:", p))
        if "sha256" in r:
            ensure(type(r["sha256"]) is str and HEX64.fullmatch(r["sha256"]) is not None)
        if "git_oid" in r:
            ensure(type(r["git_oid"]) is str and HEX_GIT.fullmatch(r["git_oid"]) is not None)
        ensure(r["kind"] != "GIT_OBJECT" or "git_oid" in r)


def validate_aggregate(a: Any, kind: str, ident: str) -> None:
    common = {"schema_version", "kind", "id", "revision", "state", "created_at", "updated_at",
              "authority_refs", "related_ids", "last_event_id"}
    extras = {
        "Milestone": {"title"},
        "TaskCycle": {"responsibility", "obligations", "terminal_disposition_ref"},
        "Operation": {"taskcycle_id", "objective", "result_ref"},
        "ExecutionAttempt": {"operation_id", "outcome", "reconciliation_required", "result_refs"},
    }
    ensure(kind in KINDS and identifier(ident))
    obj(a, common | extras[kind])
    base_order = ("schema_version", "kind", "id", "revision", "state", "created_at",
                  "updated_at", "authority_refs", "related_ids", "last_event_id")
    extra_order = {
        "Milestone": ("title",),
        "TaskCycle": ("responsibility", "obligations", "terminal_disposition_ref"),
        "Operation": ("taskcycle_id", "objective", "result_ref"),
        "ExecutionAttempt": ("operation_id", "outcome", "reconciliation_required", "result_refs"),
    }
    ensure(tuple(a) == base_order + extra_order[kind], "PRODUCT_V0_ORDER_MISMATCH")
    ensure(a["schema_version"] == VERSION and a["kind"] == kind and a["id"] == ident)
    ensure(type(a["revision"]) is int and 1 <= a["revision"] <= (1 << 53) - 1)
    ensure(a["state"] in STATES[kind] and iso(a["created_at"]) and iso(a["updated_at"]))
    ensure(type(a["related_ids"]) is list and all(string(v) for v in a["related_ids"]) and
           len(set(a["related_ids"])) == len(a["related_ids"]))
    ensure(a["last_event_id"] is None or string(a["last_event_id"]))
    refs(a["authority_refs"])
    if kind == "Milestone":
        ensure(string(a["title"]))
    elif kind == "TaskCycle":
        ensure(string(a["responsibility"]) and type(a["obligations"]) is list)
        names: set[str] = set()
        for o in a["obligations"]:
            obj(o, {"id", "status", "authority_ref"})
            ensure(string(o["id"]) and o["id"] not in names and o["status"] in ("PENDING", "SATISFIED")
                   and (o["authority_ref"] is None or string(o["authority_ref"])))
            names.add(o["id"])
        ensure(a["terminal_disposition_ref"] is None or string(a["terminal_disposition_ref"]))
    elif kind == "Operation":
        ensure(string(a["taskcycle_id"]) and string(a["objective"]) and
               (a["result_ref"] is None or string(a["result_ref"])))
    elif kind == "ExecutionAttempt":
        ensure(string(a["operation_id"]) and a["outcome"] in (
            None, "PASS", "FAIL", "BLOCKED", "UNAVAILABLE", "CANCELLED", "UNKNOWN"))
        ensure(type(a["reconciliation_required"]) is bool and
               ((a["state"] == "UNKNOWN") == a["reconciliation_required"]) and
               (a["state"] != "UNKNOWN" or a["outcome"] == "UNKNOWN"))
        refs(a["result_refs"])


def validate_state(s: Any, revision: int) -> None:
    obj(s, {"schema_version", "revision", "aggregates"})
    ensure(tuple(s) == ("schema_version", "revision", "aggregates"), "PRODUCT_V0_ORDER_MISMATCH")
    ensure(s["schema_version"] == VERSION and type(s["revision"]) is int and
           s["revision"] == revision and 0 <= revision <= (1 << 53) - 1)
    obj(s["aggregates"], set(KINDS))
    ensure(tuple(s["aggregates"]) == KINDS, "PRODUCT_V0_ORDER_MISMATCH")
    for kind in KINDS:
        amap = s["aggregates"][kind]
        ensure(type(amap) is dict)
        for ident, aggregate in amap.items():
            validate_aggregate(aggregate, kind, ident)


def validate_event(event: Any) -> None:
    ensure(type(event) is dict)
    required = {"id", "sequence", "kind", "aggregate_id", "before_revision", "after",
                "previous_hash", "at", "action"}
    ensure(set(event) in (required, required | {"bootstrap_provenance"}))
    order = ("id", "sequence", "kind", "aggregate_id", "before_revision", "after",
             "previous_hash", "at", "action")
    ensure(tuple(event) in (order, order + ("bootstrap_provenance",)), "PRODUCT_V0_ORDER_MISMATCH")
    ensure(type(event["sequence"]) is int and event["sequence"] >= 1 and
           event["id"] == f"event-{event['sequence']}")
    ensure(event["kind"] in KINDS and identifier(event["aggregate_id"]) and iso(event["at"]))
    ensure(type(event["before_revision"]) is int and event["before_revision"] >= 0)
    ensure(event["previous_hash"] is None or (type(event["previous_hash"]) is str and
           HEX64.fullmatch(event["previous_hash"]) is not None))
    ensure(string(event["action"]))
    validate_aggregate(event["after"], event["kind"], event["aggregate_id"])
    if event["action"] == "BOOTSTRAP_IMPORT":
        ensure(event["kind"] == "TaskCycle" and event["before_revision"] == 0 and
               "bootstrap_provenance" in event, "BOOTSTRAP_CONTRACT_MISMATCH")
        p=event["bootstrap_provenance"]
        obj(p, {"mode", "cutover_at", "historical_events_reconstructed", "authority_refs", "evidence_refs"})
        ensure(p["mode"] == "IMPORTED_ESTABLISHED_STATE" and iso(p["cutover_at"]) and
               p["historical_events_reconstructed"] is False, "BOOTSTRAP_CONTRACT_MISMATCH")
        refs(p["authority_refs"], expected_kind="AUTHORITY")
        refs(p["evidence_refs"], expected_kind="EVIDENCE")
        ensure(bool(p["authority_refs"]) and bool(p["evidence_refs"]), "BOOTSTRAP_CONTRACT_MISMATCH")
        after=event["after"]
        ensure(after["created_at"] == p["cutover_at"] and after["updated_at"] == p["cutover_at"] and
               after["authority_refs"] == p["authority_refs"] and
               after["terminal_disposition_ref"] is None and
               after["state"] not in ("CLOSED", "CANCELLED"), "BOOTSTRAP_CONTRACT_MISMATCH")
        if after["state"] == "PENDING_ACCEPTANCE":
            ensure(all(o["status"] == "SATISFIED" for o in after["obligations"]),
                   "BOOTSTRAP_CONTRACT_MISMATCH")
        imported_ids = {r["id"] for r in p["authority_refs"]}
        for o in after["obligations"]:
            if o["status"] == "SATISFIED" and o["authority_ref"] is not None:
                ensure(o["authority_ref"] in imported_ids, "BOOTSTRAP_CONTRACT_MISMATCH")
    else:
        ensure("bootstrap_provenance" not in event, "BOOTSTRAP_CONTRACT_MISMATCH")


def _js_keys(obj: dict) -> list[str]:
    """ECMAScript own enumerable object string-key order for JSON-derived maps."""
    indexes=[]
    other=[]
    for key in obj:
        if (key.isascii() and key.isdigit() and len(key) <= 10 and key == str(int(key)) and
            0 <= int(key) < (1 << 32) - 1):
            indexes.append(key)
        else:
            other.append(key)
    indexes.sort(key=int)
    return indexes + other


def _js_order(value: Any) -> Any:
    if type(value) is dict:
        return {key: _js_order(value[key]) for key in _js_keys(value)}
    if type(value) is list:
        return [_js_order(x) for x in value]
    return value


def exact_js_event_payload(payload: Any) -> bytes:
    """Product V0 JSON.stringify(payload) for the supported no-float JSON subset.

    Preserve insertion order except ECMAScript array-index property ordering.
    Any unsupported Unicode or number representation must fail closed: this
    source mirror cannot silently change the persisted event hash input.
    """
    ensure(type(payload) is dict)
    try:
        return json.dumps(_js_order(payload), ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False).encode("utf-8", "strict")
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise ValueError("PRODUCT_V0_ENCODING_UNSUPPORTED") from exc


def exact_js_snapshot(s: Any) -> bytes:
    """JS JSON.stringify(s, null, 2)+'\\n' for the accepted no-float V0 JSON subset.

    Unsupported Unicode encodings fail closed; this does not grant Product
    competence. The final acceptance still compares native JS Product outputs.
    """
    try:
        encoded=(json.dumps(_js_order(s), ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8','strict')
    except (UnicodeError, ValueError, TypeError, RecursionError) as e:
        raise ValueError('PRODUCT_V0_ENCODING_UNSUPPORTED') from e
    return encoded
