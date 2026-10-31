#!/usr/bin/env python3
"""Experimental host A lost-ACK / fresh host B recovery using native Beads/Dolt.

GitHub Actions artifacts are the remote immutable substrate in this bounded trial.
No Product/State Kernel, network mutation by this script, or provider redispatch.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

NAME = "TS-DISTRIBUTED-CONTROL-001-HOST-FAILOVER-20261031-001"
ATTEMPT = "TS-DC043-EXTERNAL-EFFECT-ATTEMPT-001"
PREFIX = "d043"
BD = Path(os.environ["BD_BIN"]).resolve()
BASE = Path(os.environ["TS043_BASE"]).resolve()
WORK = BASE / "native-work"
ENV = {**os.environ, "BEADS_DIR": str(WORK / ".beads"),
       "BD_NO_PUSH": "1", "BD_DOLT_AUTO_PUSH": "false",
       "BD_NON_INTERACTIVE": "1", "GIT_TERMINAL_PROMPT": "0",
       "BEADS_ACTOR": "TS043-TRUSTED-EXPERIMENTAL-WRITER",
       "NO_COLOR": "1"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def bd(*args, json_out=False):
    argv = [str(BD), *map(str, args)] + (["--json"] if json_out else [])
    proc = subprocess.run(argv, cwd=WORK, env=ENV, text=True,
                          capture_output=True, timeout=65)
    if proc.returncode:
        raise RuntimeError(f"BD_FAIL:{args}:{proc.returncode}:{proc.stderr[-500:]}")
    if not json_out:
        return proc.stdout
    raw = proc.stdout
    positions = [p for p in (raw.find("{"), raw.find("[")) if p >= 0]
    require(bool(positions), "BD_JSON_MISSING")
    return json.loads(raw[min(positions):])


def rows(obj):
    if isinstance(obj, list):
        return obj
    for key in ("issues", "data", "results", "ready"):
        if isinstance(obj.get(key), list):
            return obj[key]
    return [obj]


def ready():
    return sorted(str(row["id"]) for row in rows(bd("ready", json_out=True)))


def show(name):
    items = rows(bd("show", PREFIX + "-" + name, json_out=True))
    require(len(items) == 1, "SHOW_NOT_UNIQUE")
    return items[0]


def native_tar(path):
    with tarfile.open(path, mode="w") as tar:
        tar.add(WORK / ".beads", arcname=".beads")


def producer():
    require(not BASE.exists(), "BASE_MUST_BE_FRESH")
    BASE.mkdir(parents=True)
    WORK.mkdir()
    stage = BASE / "stage"
    checkpoint = stage / "checkpoint"
    effect_dir = stage / "effect"
    checkpoint.mkdir(parents=True)
    effect_dir.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(WORK)], check=True, timeout=15)
    require("1.3.1" in bd("--version"), "BEADS_NOT_PINNED")
    bd("init", "--quiet", "--stealth", "--skip-agents",
       "--skip-hooks", "--non-interactive")
    for part in ("preflight", "effect", "join", "parent"):
        bd("create", "DC043 experimental " + part, "--id",
           PREFIX + "-" + part, "--force", "--type", "task",
           "--description", "Experimental native work only; Product NONE")
    for child, dep in (("effect", "preflight"), ("join", "effect"),
                       ("parent", "join")):
        bd("dep", "add", PREFIX + "-" + child, PREFIX + "-" + dep)
    require(ready() == [PREFIX + "-preflight"], "INITIAL_DEPENDENCIES_WRONG")
    bd("close", PREFIX + "-preflight")
    require(ready() == [PREFIX + "-effect"], "EFFECT_NOT_READY")
    bd("update", PREFIX + "-effect", "--description",
       "Original " + ATTEMPT + "; external effect UNKNOWN pending independent provider readback; NO RETRY")
    require(ATTEMPT in show("effect").get("description", ""), "IDENTITY_NOT_PERSISTED")
    require(ready() == [PREFIX + "-effect"], "UNKNOWN_PREMATURELY_CLOSED")
    require(not (WORK / "state-kernel").exists(), "STATE_KERNEL_FOUND")
    subject = os.environ["GITHUB_SHA"]
    run = str(os.environ["GITHUB_RUN_ID"])
    effect = {"experiment": NAME, "attempt": ATTEMPT,
              "effect_id": "TS-DC043-REMOTE-PROVIDER-EFFECT-001",
              "subject_git_sha": subject, "run_id": run,
              "effect": "CONFIRMED", "kind": "REMOTE_GITHUB_ACTIONS_ARTIFACT",
              "payload": "one_authorized_synthetic_provider_publication",
              "product_effect": "NONE"}
    write_json(effect_dir / "EFFECT043.json", effect)
    native_tar(checkpoint / "NATIVE_BEADS_STORE.tar")
    manifest = {"experiment": NAME, "attempt": ATTEMPT, "source_git_sha": subject,
                "run_id": run, "native_store_sha256": sha(checkpoint / "NATIVE_BEADS_STORE.tar"),
                "effect_sha256": sha(effect_dir / "EFFECT043.json"),
                "initial_ready": [PREFIX + "-effect"], "original_effect_state": "UNKNOWN",
                "kernel_used": False, "product_effect": "NONE",
                "external_effect_dispatch_count": 1,
                "expected_ack_loss": True}
    write_json(checkpoint / "CHECKPOINT043.json", manifest)
    print("TS_DC043_A=PASS_UNKNOWN_CHECKPOINT_PREPARED;effect_attempt=" + ATTEMPT +
          ";original_store_sha256=" + manifest["native_store_sha256"] +
          ";provider_effect_sha256=" + manifest["effect_sha256"] + ";Product=NONE", flush=True)


def consumer():
    require(not BASE.exists(), "CONSUMER_BASE_MUST_BE_FRESH")
    BASE.mkdir(parents=True)
    WORK.mkdir()
    checkpoint = Path(os.environ["TS043_CHECKPOINT_DIR"]).resolve()
    effect_dir = Path(os.environ["TS043_EFFECT_DIR"]).resolve()
    manifest = json.loads((checkpoint / "CHECKPOINT043.json").read_text(encoding="utf-8"))
    require(manifest["experiment"] == NAME and manifest["attempt"] == ATTEMPT,
            "ORIGINAL_IDENTITY_MISMATCH")
    require(manifest["source_git_sha"] == os.environ["GITHUB_SHA"] and
            manifest["run_id"] == str(os.environ["GITHUB_RUN_ID"]), "SOURCE_MISMATCH")
    require(manifest["kernel_used"] is False and manifest["product_effect"] == "NONE",
            "PRODUCT_OR_KERNEL_FORBIDDEN")
    store_tar = checkpoint / "NATIVE_BEADS_STORE.tar"
    effect_path = effect_dir / "EFFECT043.json"
    require(sha(store_tar) == manifest["native_store_sha256"], "STORE_HASH_MISMATCH")
    require(sha(effect_path) == manifest["effect_sha256"], "EFFECT_HASH_MISMATCH")
    effect = json.loads(effect_path.read_text(encoding="utf-8"))
    require(effect["experiment"] == NAME and effect["attempt"] == ATTEMPT and
            effect["run_id"] == str(os.environ["GITHUB_RUN_ID"]) and
            effect["subject_git_sha"] == os.environ["GITHUB_SHA"] and
            effect["effect"] == "CONFIRMED" and effect["product_effect"] == "NONE",
            "PROVIDER_RECEIPT_IDENTITY_MISMATCH")
    require(effect["effect_id"] == "TS-DC043-REMOTE-PROVIDER-EFFECT-001",
            "EFFECT_ID_MISMATCH")
    provider_id = os.environ["TS043_PROVIDER_ARTIFACT_ID"]
    require(provider_id.isdigit(), "PROVIDER_ARTIFACT_ID_MISSING")
    subprocess.run(["git", "init", "-q", str(WORK)], check=True, timeout=15)
    with tarfile.open(store_tar, "r") as archive:
        for entry in archive.getmembers():
            require(entry.name == ".beads" or entry.name.startswith(".beads/"),
                    "UNEXPECTED_ARCHIVE_MEMBER")
            require(not entry.issym() and not entry.islnk(), "SYMLINK_NOT_ALLOWED")
        archive.extractall(WORK, filter="data")
    require("1.3.1" in bd("--version"), "CONSUMER_BEADS_NOT_PINNED")
    require(ready() == [PREFIX + "-effect"], "FRESH_HOST_NOT_ORIGINAL_READY")
    before = show("effect")
    require(before.get("status") != "closed" and
            "UNKNOWN" in before.get("description", "") and
            ATTEMPT in before.get("description", ""), "UNKNOWN_NOT_RECOVERED")
    require(ready() != [PREFIX + "-join"], "JOIN_WRONGLY_UNBLOCKED")
    bd("update", PREFIX + "-effect", "--description",
       "CONFIRMED from independent GitHub provider artifact ID " + provider_id +
       "; original " + ATTEMPT + "; exact sha256 " + manifest["effect_sha256"] +
       "; redispatch_count=0")
    bd("close", PREFIX + "-effect")
    require(ready() == [PREFIX + "-join"], "JOIN_NOT_READY_AFTER_RECONCILIATION")
    bd("update", PREFIX + "-join", "--description",
       "Verified external effect once; original " + ATTEMPT +
       "; no new provider attempt created")
    bd("close", PREFIX + "-join")
    require(ready() == [PREFIX + "-parent"], "PARENT_NOT_READY")
    bd("close", PREFIX + "-parent")
    require(ready() == [], "NATIVE_GRAPH_NOT_TERMINAL")
    require(all(show(x).get("status") == "closed"
                for x in ("preflight", "effect", "join", "parent")), "CLOSE_INVALID")
    history = rows(bd("history", PREFIX + "-effect", json_out=True))
    require(len(history) >= 2, "DOLT_HISTORY_NOT_RECOVERED")
    result = {"experiment": NAME, "attempt": ATTEMPT,
              "status": "PASS_FRESH_HOST_REMOTE_ARTIFACT_UNKNOWN_RECONCILED_NO_REDISPATCH",
              "producer_job_expected_failure": True,
              "product_effect": "NONE", "kernel_used": False,
              "original_store_sha256": manifest["native_store_sha256"],
              "original_effect_sha256": manifest["effect_sha256"],
              "verified_external_provider_artifact_id": provider_id,
              "original_effect_dispatch_count": 1,
              "provider_redispatch_count": 0,
              "fresh_host": True, "native_history_count": len(history),
              "native_terminal_ready": [], "remote_substrate": "GITHUB_ACTIONS_ARTIFACTS",
              "limitations": ["Artifact store expires; not live Dolt Git replication.",
                              "Injected lost acknowledgement, not actual host disappearance.",
                              "Trusted writer, no Product authority/IR/Phase2 equivalence.",
                              "Provider effect is one synthetic GitHub artifact publication."]}
    native_tar(BASE / "FINAL_NATIVE_STORE.tar")
    result["final_native_store_sha256"] = sha(BASE / "FINAL_NATIVE_STORE.tar")
    write_json(BASE / "RESULT043.json", result)
    print("TS_DC043_B=" + result["status"] + ";original_attempt=" + ATTEMPT +
          ";redispatch=0;provider_artifact=" + provider_id +
          ";Product=NONE", flush=True)


if __name__ == "__main__":
    require(len(sys.argv) == 2 and sys.argv[1] in ("producer", "consumer"),
            "EXPECTED_PRODUCER_OR_CONSUMER")
    (producer if sys.argv[1] == "producer" else consumer)()
