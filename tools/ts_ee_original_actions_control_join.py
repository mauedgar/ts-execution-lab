"""Control-side independent original Actions run reconciliation, nonProduct v1.

Inputs MUST originate from separately verified GitHub native APIs and an
immutable external Control request. This code never fetches, mutates, grants
authority, or executes an original. It fails closed on mismatched identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION = "TS-EE-ACTIONS-CONTROL-JOIN-v1"
MARKER_VERSION = "TS-EE-ACTIONS-ORIGINAL-BINDING-v1"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
DECIMAL = re.compile(r"[1-9][0-9]*\Z")
REQ_REF = re.compile(
    r"mauedgar/ts-execution-transport@[0-9a-f]{40}:requests/"
    r"[A-Za-z0-9_./-]+\.md\Z"
)
FIELDS = frozenset({
    "version", "scope", "execution_attempt", "repository", "ref",
    "source_parent_commit", "source_parent_tree", "workflow_path",
    "workflow_blob", "marker_path", "marker_blob",
    "control_request", "control_request_blob", "expected_effect",
})
MARKER_FIELDS = frozenset({
    "version", "execution_attempt", "repository", "ref",
    "source_parent_commit", "source_parent_tree", "workflow_path",
    "workflow_blob", "marker_path", "control_request",
})


class BlockedPrecondition(Exception):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise BlockedPrecondition(code)


def marker_json(raw: bytes) -> dict:
    require(0 < len(raw) <= 4096, "MARKER_NOT_BOUNDED")
    def unique_keys(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "DUPLICATE_MARKER_JSON_KEY")
            out[key] = value
        return out
    try:
        obj = json.loads(raw.decode("utf-8", "strict"),
                         object_pairs_hook=unique_keys)
    except (UnicodeError, ValueError) as exc:
        raise BlockedPrecondition("MARKER_PARSE_INVALID") from exc
    require(type(obj) is dict and set(obj) == MARKER_FIELDS,
            "MARKER_FIELDS_INVALID")
    return obj


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\x00" + raw,
    ).hexdigest()


def reconcile(external: dict, marker_raw: bytes, provider_run: dict,
              guard: dict, native: dict) -> dict:
    """Fail closed; the trusted Control MUST verify all GitHub provenance."""
    require(type(external) is dict and set(external) == FIELDS,
            "CONTROL_ENVELOPE_FIELDS_NOT_EXACT")
    require(external["version"] == VERSION and
            external["scope"] == "NONPRODUCT" and
            external["expected_effect"] == "READ_ONLY_IDENTITY_PREFLIGHT",
            "CONTROL_AUTHORITY_SCOPE_INVALID")
    marker = marker_json(marker_raw)
    require(marker["version"] == MARKER_VERSION,
            "MARKER_VERSION_INVALID")
    require(type(external["marker_blob"]) is str and
            HEX40.fullmatch(external["marker_blob"]) is not None and
            git_blob_sha(marker_raw) == external["marker_blob"],
            "EXTERNAL_MARKER_BLOB_MISMATCH")

    expected_pairs = (
        "execution_attempt", "repository", "ref",
        "source_parent_commit", "source_parent_tree",
        "workflow_path", "workflow_blob", "marker_path", "control_request",
    )
    for key in expected_pairs:
        require(marker[key] == external[key],
                "EXTERNAL_MARKER_" + key.upper() + "_MISMATCH")
    require(type(external["execution_attempt"]) is str and
            len(external["execution_attempt"]) >= 8,
            "EXECUTION_ATTEMPT_INVALID")
    require(external["repository"] == "mauedgar/ts-execution-lab" and
            type(external["ref"]) is str and
            external["ref"].startswith("refs/heads/ee/"),
            "REPOSITORY_REF_OUT_OF_SCOPE")
    for key in ("source_parent_commit", "source_parent_tree",
                "workflow_blob", "control_request_blob"):
        require(type(external[key]) is str and
                HEX40.fullmatch(external[key]) is not None,
                "INVALID_CONTROL_GIT_IDENTITY")
    require(type(external["control_request"]) is str and
            REQ_REF.fullmatch(external["control_request"]) is not None,
            "CONTROL_GIT_REQUEST_REF_INVALID")
    require(type(native) is dict and
            native.get("git_request_ref") == external["control_request"] and
            native.get("git_request_blob") == external["control_request_blob"] and
            native.get("git_source_parent") == external["source_parent_commit"] and
            native.get("git_source_tree") == external["source_parent_tree"] and
            native.get("git_workflow_blob") == external["workflow_blob"] and
            native.get("git_marker_blob") == external["marker_blob"],
            "INDEPENDENT_NATIVE_GIT_PROVENANCE_MISMATCH")

    require(type(provider_run) is dict and
            provider_run.get("status") == "completed" and
            provider_run.get("conclusion") == "success" and
            provider_run.get("event") == "push" and
            provider_run.get("run_attempt") == 1 and
            provider_run.get("repository") == external["repository"] and
            provider_run.get("ref") == external["ref"],
            "PROVIDER_RUN_NOT_ORIGINAL_SUCCESS")
    run_id = provider_run.get("id")
    require(type(run_id) is int and run_id > 0,
            "PROVIDER_RUN_ID_NOT_NATIVE")
    head = provider_run.get("head_sha")
    tree = provider_run.get("head_tree")
    require(type(head) is str and HEX40.fullmatch(head) is not None and
            type(tree) is str and HEX40.fullmatch(tree) is not None,
            "PROVIDER_GIT_SUBJECT_UNKNOWN")
    require(type(native.get("observed_runs_complete")) is bool and
            native["observed_runs_complete"] is True and
            native.get("original_run_ids") == [run_id],
            "PROVIDER_ORIGINAL_UNIQUENESS_NOT_PROVEN")

    require(type(guard) is dict and
            guard.get("status") == "TS_EE_ORIGINAL_GIT_TRANSITION_PASS" and
            guard.get("effect") == "READ_ONLY_IDENTITY_PREFLIGHT" and
            guard.get("product_effect") == "NONE" and
            guard.get("version") == MARKER_VERSION and
            guard.get("run_attempt") == 1 and
            guard.get("run_id") == str(run_id) and
            guard.get("head_commit") == head and
            guard.get("head_tree") == tree,
            "ORIGINAL_GUARD_OBSERVATION_INVALID")
    for key in expected_pairs:
        require(guard.get(key) == external[key] if key != "marker_path"
                else True, "GUARD_" + key.upper() + "_MISMATCH")
    require(guard.get("marker_blob") == external["marker_blob"] and
            guard.get("source_parent_commit") == external["source_parent_commit"] and
            guard.get("source_parent_tree") == external["source_parent_tree"] and
            guard.get("workflow_blob") == external["workflow_blob"] and
            guard.get("control_request") == external["control_request"],
            "GUARD_GIT_SUBJECT_NOT_FROZEN")
    # The provider run's HEAD SHA/tree are obtained from the native GitHub
    # commit and run APIs, not the self-reported source code or marker.
    require(native.get("git_head_commit") == head and
            native.get("git_head_tree") == tree and
            native.get("git_head_parent") == external["source_parent_commit"] and
            native.get("git_only_added_path") == external["marker_path"],
            "EXTERNAL_ORIGINAL_COMMIT_DELTA_MISMATCH")
    return {
        "status": "TS_EE_EXTERNAL_ORIGINAL_CONTROL_JOIN_PASS",
        "execution_attempt": external["execution_attempt"],
        "run_id": run_id,
        "head_sha": head,
        "head_tree": tree,
        "source_parent_commit": external["source_parent_commit"],
        "source_parent_tree": external["source_parent_tree"],
        "workflow_blob": external["workflow_blob"],
        "marker_blob": external["marker_blob"],
        "request_blob": external["control_request_blob"],
        "effect": "READ_ONLY_RECONCILIATION",
        "product_effect": "NONE",
        "review_or_product_acceptance": "NOT_GRANTED",
    }


def _load(path: Path, limit: int = 65536) -> bytes:
    require(path.is_file() and path.stat().st_size <= limit,
            "LOCAL_EVIDENCE_NOT_BOUNDED")
    return path.read_bytes()


def main() -> int:
    ap = argparse.ArgumentParser()
    for key in ("external", "marker", "run", "guard", "native"):
        ap.add_argument("--" + key, required=True, type=Path)
    args = ap.parse_args()
    try:
        e = json.loads(_load(args.external))
        p = json.loads(_load(args.run))
        g = json.loads(_load(args.guard))
        n = json.loads(_load(args.native))
        result = reconcile(e, _load(args.marker), p, g, n)
    except (BlockedPrecondition, OSError, ValueError, TypeError) as exc:
        code = str(exc) if type(exc) is BlockedPrecondition else "INVALID_EVIDENCE"
        if re.fullmatch(r"[A-Z0-9_]{3,96}", code) is None:
            code = "INVALID_EVIDENCE"
        print("TS_EE_CONTROL_BLOCKED_PRECONDITION_" + code, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
