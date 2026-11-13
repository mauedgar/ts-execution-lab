#!/usr/bin/env python3
"""Fail-closed notebook-capacity-to-Actions admission; experimental, not Product authority.

This script validates immutable local refusal evidence before inference. It does not
dispatch, start OpenCode, approve a review, or publish a Product result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{7,159}\Z")
ALLOWED_MODELS = {
    "opencode/deepseek-v4.1-flash-free": "deepseek-v4.1-flash-free",
    "opencode/nemotron-3-ultra-free": "nemotron-3-ultra-free",
}
RECEIPT_PREFIX = "evidence/oc2-notebook-capacity/"
CATALOG_PREFIX = "evidence/oc2-free-model-qualification/"


def stop(reason: str) -> None:
    print(json.dumps({"status": "BLOCKED_PRECONDITION", "reason": reason,
                      "effect_state": "NONE", "inference_started": False},
                     sort_keys=True))
    raise SystemExit(42)


def git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        stop("GIT_READ_OR_IDENTITY_FAILED")


def object_from_commit(root: Path, sha: str, path: str) -> bytes:
    if not SHA.fullmatch(sha) or not path or path.startswith("/") or ".." in Path(path).parts:
        stop("INVALID_IMMUTABLE_REF")
    return git(root, "show", f"{sha}:{path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--control-root", required=True)
    p.add_argument("--subject-root", required=True)
    p.add_argument("--subject-base", required=True)
    p.add_argument("--subject-head", required=True)
    p.add_argument("--notebook-receipt-commit", required=True)
    p.add_argument("--notebook-receipt-path", required=True)
    p.add_argument("--notebook-receipt-sha256", required=True)
    p.add_argument("--operation-id", required=True)
    p.add_argument("--request-sha256", required=True)
    p.add_argument("--attempt-id", required=True)
    p.add_argument("--model-id", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    control, subject = Path(a.control_root).resolve(), Path(a.subject_root).resolve()
    if not control.is_dir() or not subject.is_dir():
        stop("CHECKOUT_ABSENT")
    if not all(SHA.fullmatch(v or "") for v in
               (a.subject_head, a.subject_base, a.notebook_receipt_commit)):
        stop("INVALID_COMMIT")
    if not HASH.fullmatch(a.notebook_receipt_sha256 or "") or not HASH.fullmatch(a.request_sha256 or ""):
        stop("INVALID_HASH")
    if not ID.fullmatch(a.operation_id or "") or not ID.fullmatch(a.attempt_id or ""):
        stop("INVALID_ID")
    if a.model_id not in ALLOWED_MODELS or "openai" in a.model_id.lower():
        stop("MODEL_NOT_EXPLICITLY_FREE_NON_OPENAI")

    for root in (control, subject):
        if git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
            stop("ROOT_MISMATCH")
    if git(subject, "rev-parse", "--verify", "HEAD").decode().strip() != a.subject_head:
        stop("SUBJECT_HEAD_MISMATCH")
    git(subject, "cat-file", "-e", f"{a.subject_base}^{{commit}}")
    try:
        subprocess.run(
            ["git", "-C", str(subject), "merge-base", "--is-ancestor",
             a.subject_base, a.subject_head],
            check=True, timeout=15, capture_output=True
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        stop("SUBJECT_BASE_NOT_ANCESTOR")
    if git(subject, "status", "--porcelain=v1", "--untracked-files=all").strip():
        stop("SUBJECT_NOT_CLEAN")
    if git(control, "status", "--porcelain=v1", "--untracked-files=all").strip():
        stop("CONTROL_NOT_CLEAN")

    if (not a.notebook_receipt_path.startswith(RECEIPT_PREFIX)
        or not a.notebook_receipt_path.endswith(".json")):
        stop("RECEIPT_PATH_NOT_ALLOWED")
    raw = object_from_commit(control, a.notebook_receipt_commit, a.notebook_receipt_path)
    if hashlib.sha256(raw).hexdigest() != a.notebook_receipt_sha256:
        stop("RECEIPT_DIGEST_MISMATCH")
    try:
        receipt = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        stop("BAD_RECEIPT_JSON")
    expected = {
        "contract_version": "ts-ee-oc2-notebook-capacity/v0",
        "host_binding": "OPENCODE2_NOTEBOOK",
        "result_status": "BLOCKED_CAPACITY",
        "effect_state": "NONE",
        "inference_started": False,
        "native_process_started": False,
        "subject_repository": "mauedgar/ts-execution-lab",
        "subject_base_sha": a.subject_base,
        "subject_head_sha": a.subject_head,
        "request_sha256": a.request_sha256,
        "operation_id": a.operation_id,
    }
    if not isinstance(receipt, dict) or any(receipt.get(k) != v for k, v in expected.items()):
        stop("NOTEBOOK_BLOCK_RECEIPT_NOT_QUALIFIED")
    local_attempt = receipt.get("execution_attempt")
    evidence = receipt.get("resource_evidence")
    if not isinstance(local_attempt, str) or not ID.fullmatch(local_attempt) or local_attempt == a.attempt_id:
        stop("ATTEMPT_COLLISION_OR_INVALID")
    if not isinstance(evidence, dict) or not evidence.get("reason") in {
        "PROCESS_OVERLOAD", "MEMORY_PRESSURE", "CPU_CONTENTION"
    }:
        stop("CAPACITY_EVIDENCE_MISSING")
    if receipt.get("active_semantic_attempt", True) is not False:
        stop("LOCAL_SEMANTIC_ATTEMPT_STILL_ACTIVE_OR_UNKNOWN")

    model_key = ALLOWED_MODELS[a.model_id]
    proof_path = f"{CATALOG_PREFIX}{model_key}.json"
    # Publication of this proof requires separate qualification of current catalog,
    # provider configuration, no paid fallback and no credentials exposed.
    try:
        proof = json.loads((control / proof_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stop("FREE_MODEL_QUALIFICATION_NOT_PRESENT")
    if not isinstance(proof, dict) or any([
        proof.get("status") != "PASS_QUALIFIED",
        proof.get("model_id") != a.model_id,
        proof.get("input_price_usd_per_mtok") != 0,
        proof.get("output_price_usd_per_mtok") != 0,
        proof.get("no_paid_fallback") is not True,
        proof.get("provider") != "opencode",
    ]):
        stop("FREE_MODEL_NOT_QUALIFIED")
    try:
        expires = datetime.fromisoformat(proof["expires_at"].replace("Z", "+00:00"))
    except (KeyError, ValueError, TypeError):
        stop("FREE_MODEL_PROOF_INVALID_EXPIRY")
    if expires <= datetime.now(timezone.utc):
        stop("FREE_MODEL_PROOF_EXPIRED")

    # The caller chooses the output in runner temp, not inside either checkout.
    output = Path(a.output).resolve()
    if output.exists() or control in output.parents or subject in output.parents:
        stop("OUTPUT_LOCATION_NOT_ISOLATED_OR_EXISTS")
    result = {
        "status": "ADMISSION_PASS_ONLY",
        "effect_state": "NONE",
        "inference_started": False,
        "operation_id": a.operation_id,
        "request_sha256": a.request_sha256,
        "remote_attempt": a.attempt_id,
        "local_attempt": local_attempt,
        "notebook_receipt_commit": a.notebook_receipt_commit,
        "notebook_receipt_path": a.notebook_receipt_path,
        "notebook_receipt_sha256": a.notebook_receipt_sha256,
        "subject_base_sha": a.subject_base,
        "subject_head_sha": a.subject_head,
        "model_id": a.model_id,
        "source": "VERIFIED_RECEIPT_PLUS_MODEL_QUALIFICATION",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
