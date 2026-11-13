#!/usr/bin/env python3
"""Non-effectful notebook-first fallback admission inspection, source candidate v0.2.

IMPORTANT: this tool NEVER authorizes Actions inference or switching to a new
review attempt. It verifies selected immutable inputs and ALWAYS DENIES remote
admission until a separate, qualified provider-native process/fencing gate is
implemented and independently reviewed. Run only on synthetic TS EE lab refs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,159}\Z")
RECEIPT_PREFIX = "evidence/oc2-notebook-capacity/"
REPO = "mauedgar/ts-execution-lab"


class Rejected(Exception):
    pass


def guard(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=15,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise Rejected("GIT_SOURCE_OR_IDENTITY_UNVERIFIED") from exc


def json_unique(data: bytes) -> dict:
    def no_duplicate(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise Rejected("DUPLICATE_RECEIPT_JSON_KEY")
            result[key] = value
        return result

    try:
        result = json.loads(data, object_pairs_hook=no_duplicate)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Rejected("BAD_RECEIPT_JSON") from exc
    guard(isinstance(result, dict), "RECEIPT_NOT_AN_OBJECT")
    return result


def probe(a: argparse.Namespace) -> dict:
    control = Path(a.control_root).resolve(strict=True)
    subject = Path(a.subject_root).resolve(strict=True)
    guard(control.is_dir() and subject.is_dir(), "CHECKOUT_ROOT_MISSING")
    guard(control != subject, "ROOTS_NOT_ISOLATED")
    for value in (a.subject_base, a.subject_head, a.subject_tree,
                  a.notebook_receipt_commit):
        guard(bool(SHA.fullmatch(value or "")), "INVALID_GIT_SHA")
    for value in (a.notebook_receipt_sha256, a.request_sha256):
        guard(bool(HASH.fullmatch(value or "")), "INVALID_SHA256")
    for value in (a.operation_id, a.attempt_id):
        guard(bool(IDENT.fullmatch(value or "")), "INVALID_ID")
    guard(a.notebook_receipt_path.startswith(RECEIPT_PREFIX)
          and a.notebook_receipt_path.endswith(".json")
          and ".." not in Path(a.notebook_receipt_path).parts
          and "\\" not in a.notebook_receipt_path,
          "RECEIPT_PATH_NOT_ALLOWED")
    for root in (control, subject):
        guard(
            git(root, "rev-parse", "--show-toplevel").decode().strip() == str(root),
            "GIT_ROOT_MISMATCH",
        )
        guard(not git(root, "status", "--porcelain=v1", "--untracked-files=all").strip(),
              "CHECKOUT_DIRTY")
    guard(git(subject, "rev-parse", "--verify", "HEAD").decode().strip()
          == a.subject_head, "SUBJECT_HEAD_MISMATCH")
    guard(git(subject, "rev-parse", "--verify", "HEAD^{tree}").decode().strip()
          == a.subject_tree, "SUBJECT_TREE_MISMATCH")
    git(subject, "cat-file", "-e", a.subject_base + "^{commit}")
    try:
        subprocess.run(
            ["git", "-C", str(subject), "merge-base", "--is-ancestor",
             a.subject_base, a.subject_head],
            check=True, timeout=15, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise Rejected("BASE_NOT_ANCESTOR") from exc

    # Hash of an original Git blob detects corruption, NOT whether the author
    # was an authorized notebook controller or whether processes are idle.
    raw = git(control, "show",
              a.notebook_receipt_commit + ":" + a.notebook_receipt_path)
    guard(hashlib.sha256(raw).hexdigest() == a.notebook_receipt_sha256,
          "RECEIPT_SHA256_MISMATCH")
    receipt = json_unique(raw)
    expected = {
        "contract_version": "ts-ee-oc2-notebook-capacity/v0",
        "host_binding": "OPENCODE2_NOTEBOOK",
        "result_status": "BLOCKED_CAPACITY",
        "effect_state": "NONE",
        "inference_started": False,
        "native_process_started": False,
        "active_semantic_attempt": False,
        "subject_repository": REPO,
        "subject_base_sha": a.subject_base,
        "subject_head_sha": a.subject_head,
        "subject_tree_sha": a.subject_tree,
        "request_sha256": a.request_sha256,
        "operation_id": a.operation_id,
    }
    guard(all(receipt.get(key) == value for key, value in expected.items()),
          "NOTEBOOK_RECEIPT_FIELDS_MISMATCH")
    local_attempt = receipt.get("execution_attempt")
    guard(isinstance(local_attempt, str) and
          bool(IDENT.fullmatch(local_attempt)) and
          local_attempt != a.attempt_id, "ATTEMPT_ID_COLLISION")
    evidence = receipt.get("resource_evidence")
    guard(isinstance(evidence, dict)
          and evidence.get("reason") in
          {"PROCESS_OVERLOAD", "MEMORY_PRESSURE", "CPU_CONTENTION"},
          "RESOURCE_EVIDENCE_MISSING")

    return {
        "operation_id": a.operation_id,
        "request_sha256": a.request_sha256,
        "local_execution_attempt": local_attempt,
        "proposed_remote_attempt": a.attempt_id,
        "subject_head_sha": a.subject_head,
        "subject_tree_sha": a.subject_tree,
        "receipt_sha256": a.notebook_receipt_sha256,
        "receipt_content": "SELF_ATTESTED_NOT_TRUSTED_AS_NATIVE_PROCESS_STATE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in (
        "control-root", "subject-root", "subject-base", "subject-head",
        "subject-tree", "notebook-receipt-commit", "notebook-receipt-path",
        "notebook-receipt-sha256", "operation-id", "request-sha256",
        "attempt-id",
    ):
        parser.add_argument("--" + name, required=True)
    a = parser.parse_args()
    try:
        data = probe(a)
    except (Rejected, OSError, UnicodeError) as exc:
        result = {"status": "BLOCKED_PRECONDITION", "reason": str(exc),
                  "effect_state": "NONE", "inference_started": False,
                  "actions_model_calls": 0}
    else:
        # Deliberately NON-OVERRIDABLE in this source version. Signatures and
        # process fencing, provider identity, model-free proof and permission
        # enforcement are future separately qualified requirements.
        result = {**data, "status": "BLOCKED_NATIVE_ATTESTATION_UNQUALIFIED",
                  "effect_state": "NONE", "inference_started": False,
                  "actions_model_calls": 0}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(42)


if __name__ == "__main__":
    main()
