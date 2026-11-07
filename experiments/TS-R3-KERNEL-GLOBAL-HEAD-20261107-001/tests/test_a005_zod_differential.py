"""A005 independent source-oracle differential: frozen Product JS/Zod vs Python mirror.

No database, credentials, Product mutations, or executable payload from inputs.
The expected disagreements are hypotheses being confirmed, not approved repairs.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ts_global import legacy_v0

VERSION = "tecnotron-state-kernel/v0"
STAMP = "2026-11-07T00:00:00.000Z"


def empty_state():
    return {"schema_version": VERSION, "revision": 0,
            "aggregates": {kind: {} for kind in legacy_v0.KINDS}}


def milestone_state():
    state = empty_state()
    state["revision"] = 1
    item = {
        "schema_version": VERSION, "kind": "Milestone", "id": "MS-A005-SYNTHETIC",
        "revision": 1, "state": "PLANNED",
        "created_at": STAMP, "updated_at": STAMP,
        "authority_refs": [], "related_ids": [], "last_event_id": "event-1",
        "title": "A005 synthetic state only",
    }
    state["aggregates"]["Milestone"][item["id"]] = item
    return state


def inputs():
    a = empty_state()
    b = milestone_state()
    top = {key: deepcopy(a[key])
           for key in ("aggregates", "revision", "schema_version")}
    maps = deepcopy(a)
    maps["aggregates"] = {
        key: maps["aggregates"][key] for key in reversed(legacy_v0.KINDS)
    }
    item = deepcopy(b)
    original = item["aggregates"]["Milestone"]["MS-A005-SYNTHETIC"]
    item["aggregates"]["Milestone"]["MS-A005-SYNTHETIC"] = {
        key: deepcopy(original[key]) for key in ("title", *[k for k in original if k != "title"])
    }
    extra = deepcopy(a)
    extra["debug"] = True
    missing = deepcopy(a)
    del missing["aggregates"]
    negative = deepcopy(a)
    negative["revision"] = -1
    bad_state = deepcopy(b)
    bad_state["aggregates"]["Milestone"]["MS-A005-SYNTHETIC"]["state"] = "UNKNOWN"
    no_title = deepcopy(b)
    del no_title["aggregates"]["Milestone"]["MS-A005-SYNTHETIC"]["title"]
    bad_date = deepcopy(b)
    bad_date["aggregates"]["Milestone"]["MS-A005-SYNTHETIC"]["created_at"] = "2026-13-07T00:00:00.000Z"
    return [
        ("canonical_empty", a),
        ("canonical_milestone", b),
        ("reordered_top", top),
        ("reordered_aggregates", maps),
        ("reordered_milestone", item),
        ("extra_state", extra),
        ("missing_aggregates", missing),
        ("negative_revision", negative),
        ("unknown_milestone_state", bad_state),
        ("missing_milestone_title", no_title),
        ("invalid_date", bad_date),
    ]


EXPECTED_JS = {
    "canonical_empty": True, "canonical_milestone": True,
    "reordered_top": True, "reordered_aggregates": True, "reordered_milestone": True,
    "extra_state": False, "missing_aggregates": False, "negative_revision": False,
    "unknown_milestone_state": False, "missing_milestone_title": False,
    "invalid_date": False,
}
EXPECTED_PY = {
    **EXPECTED_JS,
    "reordered_top": False,
    "reordered_aggregates": False,
    "reordered_milestone": False,
}
DIVERGENT = {"reordered_top", "reordered_aggregates", "reordered_milestone"}


def main(oracle_path):
    vectors = inputs()
    payload = [{"name": name, "state": state} for name, state in vectors]
    # Node executes the exact frozen Product contracts.js, copied beside the
    # oracle and exact npm-locked Zod 4.6.7; it never imports Product writes.
    proc = subprocess.run(["node", str(oracle_path)], input=json.dumps(payload),
                          text=True, capture_output=True, check=True, timeout=25)
    result = json.loads(proc.stdout)
    if result.get("zodVersion") != "4.6.7":
        raise AssertionError("ZOD_VERSION_MISMATCH")
    js = {item["name"]: item["accepted"] for item in result["results"]}
    py = {}
    for name, state in vectors:
        try:
            legacy_v0.validate_state(state, state.get("revision", -1))
            py[name] = True
        except (ValueError, KeyError, TypeError):
            py[name] = False
    semantic = {}
    for name, state in vectors:
        try:
            legacy_v0.validate_state_semantic(state, state.get("revision", -1))
            semantic[name] = True
        except (ValueError, KeyError, TypeError):
            semantic[name] = False
    if semantic != js or semantic != EXPECTED_JS:
        raise AssertionError("SEMANTIC_VALIDATION_PARITY_MISMATCH")
    if js != EXPECTED_JS:
        raise AssertionError("UNEXPECTED_PRODUCT_CONTRACT_RESULT")
    if py != EXPECTED_PY:
        raise AssertionError("UNEXPECTED_PYTHON_MIRROR_RESULT")
    if {name for name in js if js[name] != py[name]} != DIVERGENT:
        raise AssertionError("UNEXPECTED_PARITY_DELTA")
    print("A005_SEMANTIC_PARITY_11_CASES_PASS_WIRE_VALIDATOR_UNCHANGED")
    print("A005_NATIVE_PRODUCT_ZOD_4_6_7_FALSE_REJECT_CONFIRMED_3_CASES")
    print(json.dumps({"status": "SOURCE_ORACLE_DIFFERENTIAL_CONFIRMED",
                      "js_zod": "4.6.7", "cases": len(vectors),
                      "python_false_reject": sorted(DIVERGENT),
                      "other_cases_agree": len(vectors) - len(DIVERGENT),
                      "product_effect": "NONE"}, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("USAGE: test_a005_zod_differential.py ORACLE_PATH")
    main(Path(sys.argv[1]))
