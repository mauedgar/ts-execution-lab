"""TS EE original Actions execution identity guard v1 (nonProduct).

Validates one create-only dispatch marker commit against its *exact* frozen
source parent and workflow Git blob. This guard makes no Product decision.
The corresponding immutable Control request must be published BEFORE the
marker commit and reconciled through the original GitHub Actions run receipt.
Python stdlib; works on CPython 3.15.2 (legacy CI Python 3 also supported).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

VERSION = "TS-EE-ACTIONS-ORIGINAL-BINDING-v1"
MAX_MARKER_BYTES = 4096
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
ATTEMPT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{7,127}\Z")
EXPECTED_KEYS = frozenset({
    "version", "execution_attempt", "repository", "ref",
    "source_parent_commit", "source_parent_tree", "workflow_path",
    "workflow_blob", "marker_path", "control_request",
})
SENTINEL_ROOT = ".github/ts-ee-original-dispatch/"
WORKFLOW_ROOT = ".github/workflows/"


class BlockedPrecondition(Exception):
    """Not a reviewer verdict, Product gate, or permission to retry."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise BlockedPrecondition(code)


def safe_path(value: object, prefix: str) -> bool:
    return (type(value) is str and value.startswith(prefix)
            and len(value) <= 250 and
            re.fullmatch(r"[a-zA-Z0-9/_.-]+", value) is not None
            and all(p not in ("", ".", "..") for p in value.split("/"))
            and not value.endswith("/"))


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=15,
    )
    require(result.returncode == 0, "GIT_IDENTITY_READ_FAILED")
    try:
        return result.stdout.decode("utf-8", "strict").strip()
    except UnicodeDecodeError as exc:
        raise BlockedPrecondition("NON_UTF8_GIT_RESPONSE") from exc


def git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=15,
    )
    require(result.returncode == 0, "GIT_BLOB_READ_FAILED")
    return result.stdout


def validate(root: Path, marker_path: str, attempt: str,
             env: dict[str, str]) -> dict[str, object]:
    """Fail closed on any mismatched original-boundary observation.

    The external Control must verify that the immutable Control request
    contains the exact marker bytes/Git blob before authorizing dispatch.
    Do not mistake self-reported marker fields for independent authority.
    """
    require(root.is_dir(), "REPO_ROOT_NOT_FOUND")
    require(safe_path(marker_path, SENTINEL_ROOT), "UNSAFE_MARKER_PATH")
    require(type(attempt) is str and ATTEMPT.fullmatch(attempt) is not None,
            "INVALID_ORIGINAL_ATTEMPT")
    require(env.get("GITHUB_ACTIONS") == "true", "GITHUB_ACTIONS_REQUIRED")
    require(env.get("GITHUB_EVENT_NAME") == "push", "PUSH_EVENT_REQUIRED")
    require(env.get("GITHUB_RUN_ATTEMPT") == "1",
            "NO_ORIGINAL_REEXECUTION")
    require(re.fullmatch(r"[0-9]+", env.get("GITHUB_RUN_ID", "")) is not None,
            "NATIVE_RUN_ID_REQUIRED")
    head = git(root, "rev-parse", "HEAD")
    require(HEX40.fullmatch(head) is not None, "INVALID_GIT_HEAD")
    require(env.get("GITHUB_SHA") == head, "GITHUB_SHA_NOT_CHECKOUT_HEAD")

    raw = git_bytes(root, "show", f"HEAD:{marker_path}")
    require(0 < len(raw) <= MAX_MARKER_BYTES,
            "MARKER_BYTES_NOT_BOUNDED")
    try:
        obj = json.loads(raw.decode("utf-8", "strict"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise BlockedPrecondition("MARKER_JSON_INVALID") from exc
    require(type(obj) is dict and set(obj) == EXPECTED_KEYS,
            "MARKER_FIELDS_NOT_EXACT")
    require(obj["version"] == VERSION and obj["execution_attempt"] == attempt,
            "MARKER_ATTEMPT_NOT_ORIGINAL")
    require(type(obj["repository"]) is str and
            re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+",
                         obj["repository"]) is not None,
            "MARKER_REPOSITORY_INVALID")
    require(obj["repository"] == env.get("GITHUB_REPOSITORY"),
            "REPOSITORY_NOT_FROZEN")
    require(type(obj["ref"]) is str and
            obj["ref"].startswith("refs/heads/ee/") and
            re.fullmatch(r"refs/heads/ee/[a-z0-9._/-]+", obj["ref"])
            is not None and ".." not in obj["ref"],
            "MARKER_REF_NOT_ALLOWED")
    require(obj["ref"] == env.get("GITHUB_REF"), "ORIGINAL_REF_MISMATCH")
    require(obj["marker_path"] == marker_path,
            "ORIGINAL_MARKER_PATH_MISMATCH")
    require(safe_path(obj["workflow_path"], WORKFLOW_ROOT) and
            obj["workflow_path"].endswith((".yml", ".yaml")),
            "WORKFLOW_PATH_NOT_ALLOWED")
    for key in ("source_parent_commit", "source_parent_tree",
                "workflow_blob"):
        require(type(obj[key]) is str and
                HEX40.fullmatch(obj[key]) is not None,
                "FROZEN_GIT_VALUE_INVALID")
    require(type(obj["control_request"]) is str and
            re.fullmatch(
                r"mauedgar/ts-execution-transport@[0-9a-f]{40}:"
                r"requests/[A-Za-z0-9_./-]+\.md",
                obj["control_request"]) is not None,
            "EXTERNAL_CONTROL_REQUEST_NOT_PINNED")

    parents = git(root, "rev-list", "--parents", "-n", "1", "HEAD").split()
    require(len(parents) == 2 and parents[0] == head,
            "ORIGINAL_COMMIT_NOT_SINGLE_PARENT")
    require(parents[1] == obj["source_parent_commit"],
            "FROZEN_SOURCE_PARENT_MISMATCH")
    require(git(root, "rev-parse", "HEAD^{tree}") !=
            obj["source_parent_tree"],
            "NO_NEW_MARKER_COMMIT")
    require(git(root, "rev-parse", "HEAD^^{tree}") ==
            obj["source_parent_tree"],
            "FROZEN_SOURCE_TREE_MISMATCH")
    diff = git(root, "diff-tree", "--no-commit-id",
               "--name-status", "-r", "HEAD^", "HEAD")
    require(diff == "A\t" + marker_path,
            "UNAUTHORIZED_DISPATCH_COMMIT_DELTA")
    wf_at_parent = git(root, "rev-parse",
                       f"HEAD^:{obj['workflow_path']}")
    wf_at_head = git(root, "rev-parse",
                     f"HEAD:{obj['workflow_path']}")
    require(wf_at_parent == obj["workflow_blob"] and
            wf_at_head == obj["workflow_blob"],
            "WORKFLOW_BLOB_NOT_FROZEN")

    observed_marker_blob = git(root, "rev-parse", f"HEAD:{marker_path}")
    require(HEX40.fullmatch(observed_marker_blob) is not None,
            "DISPATCH_MARKER_BLOB_UNKNOWN")
    # The external Control manifest must independently bind this blob.
    result = {
        "status": "TS_EE_ORIGINAL_GIT_TRANSITION_PASS",
        "effect": "READ_ONLY_IDENTITY_PREFLIGHT",
        "version": VERSION,
        "execution_attempt": attempt,
        "repository": obj["repository"],
        "ref": obj["ref"],
        "run_id": env["GITHUB_RUN_ID"],
        "run_attempt": 1,
        "head_commit": head,
        "head_tree": git(root, "rev-parse", "HEAD^{tree}"),
        "source_parent_commit": parents[1],
        "source_parent_tree": obj["source_parent_tree"],
        "workflow_blob": obj["workflow_blob"],
        "marker_blob": observed_marker_blob,
        "control_request": obj["control_request"],
        "product_effect": "NONE",
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--marker", required=True)
    ap.add_argument("--attempt", required=True)
    args = ap.parse_args()
    try:
        output = validate(args.root, args.marker, args.attempt, dict(os.environ))
    except (BlockedPrecondition, OSError, subprocess.TimeoutExpired) as exc:
        code = (str(exc) if type(exc) is BlockedPrecondition
                else "READ_ONLY_OBSERVATION_UNAVAILABLE")
        if not re.fullmatch(r"[A-Z0-9_]{3,96}", code):
            code = "REDACTED_BLOCK"
        print("TS_EE_BLOCKED_PRECONDITION_" + code, file=sys.stderr)
        return 2
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
