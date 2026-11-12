"""NonProduct synthetic, exact-code negative tests for external Actions join.

Uses fixture copies of previously observed original GitHub IDs; no network,
GitHub dispatch, Product, host, roles, SQL or persistent effects.
"""
from __future__ import annotations

from copy import deepcopy
import json

from ts_ee_original_actions_control_join import (
    BlockedPrecondition, MARKER_VERSION, VERSION, git_blob_sha,
    reconcile,
)

ATTEMPT = "TS-EE-ACTIONS-IDENTITY-QUAL-20261111-001-A001"
REQ = ("mauedgar/ts-execution-transport@"
       "be230d170a627d87cd2e4af79b60ffa1e492e1fc:"
       "requests/TS-EE-ACTIONS-IDENTITY-QUAL-20261111-001/REQUEST.md")
PARENT = "bc8476c176c1e551017b371df3d6c32225cb4b32"
TREE = "ef9bf32f0ddab405c78b6988b29e515f7acac115"
WORKFLOW = "3fa0cf3e20079a44836b1e920dc810eea16e7c5d"
HEAD = "ddeff2aef7f56b7a3849c0d1c196c3173b90638c"
HEAD_TREE = "4fa977de154fd87ef87293aaeaed451c11db6bdb"
MARKER_PATH = (".github/ts-ee-original-dispatch/"
               "TS-EE-ACTIONS-IDENTITY-QUAL-20261111-001-A001.json")
REF = "refs/heads/ee/ts-ee-actions-original-binding-20261111-001"
RUN = 43046372506


def fixture():
    marker = {
        "version": MARKER_VERSION,
        "execution_attempt": ATTEMPT,
        "repository": "mauedgar/ts-execution-lab",
        "ref": REF,
        "source_parent_commit": PARENT,
        "source_parent_tree": TREE,
        "workflow_path": ".github/workflows/ts-ee-original-binding-qual-20261111-001.yml",
        "workflow_blob": WORKFLOW,
        "marker_path": MARKER_PATH,
        "control_request": REQ,
    }
    raw = (json.dumps(marker, indent=2, ensure_ascii=False) + "\n").encode()
    external = {
        "version": VERSION,
        "scope": "NONPRODUCT",
        "execution_attempt": ATTEMPT,
        "repository": marker["repository"],
        "ref": REF,
        "source_parent_commit": PARENT,
        "source_parent_tree": TREE,
        "workflow_path": marker["workflow_path"],
        "workflow_blob": WORKFLOW,
        "marker_path": MARKER_PATH,
        "marker_blob": git_blob_sha(raw),
        "control_request": REQ,
        "control_request_blob": "45c05b23d5f5ea15580474e382c0c7fb62828d7c",
        "expected_effect": "READ_ONLY_IDENTITY_PREFLIGHT",
    }
    provider = {
        "id": RUN, "status": "completed", "conclusion": "success",
        "event": "push", "run_attempt": 1, "repository": marker["repository"],
        "ref": REF, "head_sha": HEAD, "head_tree": HEAD_TREE,
    }
    guard = {
        **marker,
        "status": "TS_EE_ORIGINAL_GIT_TRANSITION_PASS",
        "effect": "READ_ONLY_IDENTITY_PREFLIGHT",
        "product_effect": "NONE",
        "run_attempt": 1,
        "run_id": str(RUN),
        "head_commit": HEAD,
        "head_tree": HEAD_TREE,
        "marker_blob": git_blob_sha(raw),
    }
    native = {
        "git_request_ref": REQ,
        "git_request_blob": external["control_request_blob"],
        "git_source_parent": PARENT,
        "git_source_tree": TREE,
        "git_workflow_blob": WORKFLOW,
        "git_marker_blob": external["marker_blob"],
        "git_head_commit": HEAD,
        "git_head_tree": HEAD_TREE,
        "git_head_parent": PARENT,
        "git_only_added_path": MARKER_PATH,
        "observed_runs_complete": True,
        "original_run_ids": [RUN],
    }
    return external, raw, provider, guard, native


def negative(label, modify, expected):
    x = deepcopy(fixture())
    e, m, p, g, n = x
    m2 = modify(e, m, p, g, n)
    if m2 is not None:
        m = m2
    try:
        reconcile(e, m, p, g, n)
    except BlockedPrecondition as exc:
        assert str(exc) == expected, (label, "WRONG_CODE", str(exc), expected)
        print("NEGATIVE_PASS_" + label + "_" + expected)
    else:
        raise AssertionError("FALSE_ACCEPT_" + label)


def main():
    e, m, p, g, n = fixture()
    assert git_blob_sha(m) == "1f1df371308a55ec77bab6b96e6cd1394156633c"
    good = reconcile(e, m, p, g, n)
    assert good["status"] == "TS_EE_EXTERNAL_ORIGINAL_CONTROL_JOIN_PASS"
    assert good["run_id"] == RUN
    assert good["product_effect"] == "NONE"
    print("EXTERNAL_CONTROL_JOIN_POSITIVE_PASS")

    negative("FORGED_REQUEST_REF",
             lambda e, m, p, g, n: e.update(
                 control_request=REQ.replace("REQUEST.md", "FORGED.md")),
             "EXTERNAL_MARKER_CONTROL_REQUEST_MISMATCH")
    negative("WRONG_REQUEST_BLOB",
             lambda e, m, p, g, n: n.update(git_request_blob="0" * 40),
             "INDEPENDENT_NATIVE_GIT_PROVENANCE_MISMATCH")
    negative("WRONG_MARKER_BLOB",
             lambda e, m, p, g, n: e.update(marker_blob="0" * 40),
             "EXTERNAL_MARKER_BLOB_MISMATCH")
    negative("DUPLICATE_PROVIDER_RUN",
             lambda e, m, p, g, n: n.update(
                 original_run_ids=[RUN, RUN+1]),
             "PROVIDER_ORIGINAL_UNIQUENESS_NOT_PROVEN")
    negative("SECOND_RUN_ATTEMPT",
             lambda e, m, p, g, n: p.update(run_attempt=2),
             "PROVIDER_RUN_NOT_ORIGINAL_SUCCESS")
    negative("GUARD_WRONG_RUN",
             lambda e, m, p, g, n: g.update(run_id=str(RUN+1)),
             "ORIGINAL_GUARD_OBSERVATION_INVALID")
    negative("EXTRA_ORIGINAL_DELTA",
             lambda e, m, p, g, n: n.update(
                 git_only_added_path=".github/workflows/rogue.yml"),
             "EXTERNAL_ORIGINAL_COMMIT_DELTA_MISMATCH")
    negative("AUTHORITY_SCOPE",
             lambda e, m, p, g, n: e.update(scope="PRODUCT"),
             "CONTROL_AUTHORITY_SCOPE_INVALID")
    negative("MARKER_FIELD_MUTATED",
             lambda e, m, p, g, n:
             m.replace(b'"workflow_blob": "', b'"workflow_blob": "0'),
             "EXTERNAL_MARKER_BLOB_MISMATCH")
    negative("NATIVE_WORKFLOW_MISMATCH",
             lambda e, m, p, g, n: n.update(git_workflow_blob="0" * 40),
             "INDEPENDENT_NATIVE_GIT_PROVENANCE_MISMATCH")
    negative("MISSING_RUN_SCAN",
             lambda e, m, p, g, n: n.update(
                 observed_runs_complete=False),
             "PROVIDER_ORIGINAL_UNIQUENESS_NOT_PROVEN")

    print("TS_EE_EXTERNAL_CONTROL_JOIN_1_POSITIVE_11_NEGATIVES_PASS")


if __name__ == "__main__":
    main()
