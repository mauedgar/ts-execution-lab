#!/usr/bin/env python3
"""TS-BEADS-032: isolated native Beads history checkpoint.

No Product writes, no shared Dolt writes, no external provider effect.
Every bd invocation is a fresh OS process against one disposable embedded Dolt store.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import traceback

LAB = pathlib.Path(os.environ["LAB_ROOT"]).resolve()
BD = pathlib.Path(os.environ["BD_BIN"]).resolve()
RESULT = pathlib.Path(os.environ["RESULT_PATH"]).resolve()
PRODUCT_SHA = "d4154bd43f26515c39a41be974e462a0c7406a2d"
PRODUCT_TREE = "cbfb71ad8632047e8e64fe2665d8614d835a2c8b"
SHARED_DOLT = "1f72d68797114170a97fee27641858f2e55a4571"
ISSUE_ID = "ts032-history-root"

ENV = dict(os.environ)
ENV.update(
    {
        "BEADS_DIR": str(LAB / ".beads"),
        "BD_NO_PUSH": "1",
        "BD_DOLT_AUTO_PUSH": "false",
        "BD_DOLT_AUTO_COMMIT": "on",
        "BEADS_ACTOR": "TS-BEADS-032-NONPRODUCT",
        "NO_COLOR": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "BD_NON_INTERACTIVE": "1",
    }
)

report = {
    "id": "TS-BEADS-032-NATIVE-HISTORY-20261029-001",
    "authority": "EXPERIMENTAL_CONTROL_ONLY",
    "status": "RUNNING",
    "Product_effect": "NONE",
    "shared_Dolt_effect": "NONE",
    "provider_effect": "NONE",
    "Product_subject": PRODUCT_SHA,
    "Product_tree": PRODUCT_TREE,
    "shared_Dolt_ref": SHARED_DOLT,
    "runtime": {
        "beads": "v1.3.1",
        "dolt": "v2.2.0",
        "storage_mode": "embedded_dolt_disposable",
        "auto_commit": "on",
        "auto_push": False,
        "process_model": "fresh_bd_process_per_command",
    },
    "checks": {},
    "measurements": {"bd_processes": 0},
    "not_qualified": [
        "Semantic equivalence to Kernel global revision/hash-chain/event-count invariants",
        "Real independent external provider effect identity, lost ACK and UNKNOWN recovery without duplicate dispatch",
        "Native exclusive causal writer under privileged alternate bd/Dolt access",
        "Production admission, installed Product integration and Kernel removal",
    ],
}


def run(args: list[str], *, json_mode: bool = False) -> str:
    argv = [str(BD), *args]
    if json_mode:
        argv.append("--json")
    p = subprocess.run(
        argv,
        cwd=LAB,
        env=ENV,
        text=True,
        capture_output=True,
        timeout=45,
    )
    report["measurements"]["bd_processes"] += 1
    if p.returncode != 0:
        raise RuntimeError(
            "BD_COMMAND_FAILED:"
            + " ".join(args)
            + ":"
            + json.dumps(
                {
                    "returncode": p.returncode,
                    "stdout": p.stdout[-1800:],
                    "stderr": p.stderr[-1800:],
                },
                sort_keys=True,
            )
        )
    return (p.stdout or "").strip()


def parse_json(raw: str):
    starts = [i for i in (raw.find("{"), raw.find("[")) if i >= 0]
    if not starts:
        raise RuntimeError("BD_JSON_MISSING:" + raw[-800:])
    return json.loads(raw[min(starts) :])


def runj(args: list[str]):
    return parse_json(run(args, json_mode=True))


def check(name: str, condition: bool, evidence=None):
    report["checks"][name] = {
        "result": "PASS" if condition else "FAIL",
        "evidence": evidence,
    }
    if not condition:
        raise AssertionError(name)


def one_issue(value):
    if isinstance(value, list):
        if len(value) != 1:
            raise RuntimeError(f"EXPECTED_ONE_ISSUE:{len(value)}")
        return value[0]
    if isinstance(value, dict):
        return value
    raise RuntimeError("ISSUE_JSON_SHAPE")


def description(issue: dict):
    for key in ("description", "Description"):
        if key in issue:
            return issue[key]
    raise RuntimeError("ISSUE_DESCRIPTION_MISSING:" + json.dumps(issue)[:900])


def history_entry_issue(entry: dict):
    for key in ("Issue", "issue"):
        if key in entry and isinstance(entry[key], dict):
            return entry[key]
    return {}


def history_hash(entry: dict):
    for key in ("CommitHash", "commit_hash", "commitHash", "hash", "Hash"):
        val = entry.get(key)
        if isinstance(val, str) and val:
            return val
    raise RuntimeError("HISTORY_COMMIT_HASH_MISSING:" + json.dumps(entry)[:900])


def vc_commit():
    value = runj(["vc", "status"])
    if not isinstance(value, dict):
        raise RuntimeError("VC_STATUS_JSON_SHAPE")
    commit = value.get("commit") or value.get("Commit")
    if not isinstance(commit, str) or not commit or commit == "(unknown)":
        raise RuntimeError("VC_COMMIT_UNKNOWN:" + json.dumps(value))
    return commit, value


def history():
    value = runj(["history", ISSUE_ID])
    if not isinstance(value, list):
        raise RuntimeError("HISTORY_JSON_SHAPE:" + json.dumps(value)[:900])
    return value


def write_report():
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")


try:
    LAB.mkdir(parents=True, exist_ok=True)
    if (LAB / ".beads").exists():
        raise RuntimeError("DISPOSABLE_LAB_ALREADY_INITIALIZED")

    git_remote = subprocess.run(
        ["git", "remote"], cwd=LAB, text=True, capture_output=True, timeout=8
    )
    check(
        "isolated_git_has_no_remote_before_init",
        git_remote.returncode == 0 and not git_remote.stdout.strip(),
        git_remote.stdout.strip(),
    )

    run(["init", "--quiet", "--stealth", "--skip-agents", "--skip-hooks", "--non-interactive"])
    check("embedded_dolt_materialized", (LAB / ".beads" / "dolt").exists(), str(LAB / ".beads" / "dolt"))

    base_commit, base_status = vc_commit()
    report["measurements"]["base_vc_status"] = base_status

    created = one_issue(
        runj(
            [
                "create",
                "TS032 synthetic history root",
                "--type",
                "task",
                "--id",
                ISSUE_ID,
                "--force",
                "--description",
                "TS032-V1",
                "--metadata",
                '{"ts032":"v1","nonproduct":true}',
            ]
        )
    )
    check("create_returned_exact_issue", created.get("id") == ISSUE_ID, created.get("id"))
    create_commit, create_status = vc_commit()
    check(
        "create_auto_commit_advanced_head",
        create_commit != base_commit,
        {"before": base_commit, "after": create_commit},
    )

    history_v1 = history()
    v1_entries = [
        e
        for e in history_v1
        if isinstance(e, dict) and description(history_entry_issue(e)) == "TS032-V1"
    ]
    check("history_after_create_contains_v1_snapshot", len(v1_entries) >= 1, len(history_v1))
    create_history_commit = history_hash(v1_entries[0])
    check(
        "create_vc_head_matches_v1_history_commit",
        create_history_commit == create_commit,
        {"vc": create_commit, "history": create_history_commit},
    )

    updated = one_issue(runj(["update", ISSUE_ID, "--description", "TS032-V2"]))
    check("update_returned_exact_issue", updated.get("id") == ISSUE_ID, updated.get("id"))
    update_commit, update_status = vc_commit()
    check(
        "update_auto_commit_advanced_head",
        update_commit != create_commit,
        {"before": create_commit, "after": update_commit},
    )

    history_v2 = history()
    by_desc = {}
    for entry in history_v2:
        if not isinstance(entry, dict):
            continue
        issue = history_entry_issue(entry)
        try:
            desc = description(issue)
            by_desc.setdefault(desc, []).append(entry)
        except Exception:
            pass

    check("history_after_update_contains_v1_snapshot", bool(by_desc.get("TS032-V1")), list(by_desc))
    check("history_after_update_contains_v2_snapshot", bool(by_desc.get("TS032-V2")), list(by_desc))
    v1_hash = history_hash(by_desc["TS032-V1"][0])
    v2_hash = history_hash(by_desc["TS032-V2"][0])
    check(
        "history_has_distinct_per_write_commits",
        v1_hash != v2_hash,
        {"v1": v1_hash, "v2": v2_hash, "entries": len(history_v2)},
    )
    check(
        "update_vc_head_matches_v2_history_commit",
        v2_hash == update_commit,
        {"vc": update_commit, "history": v2_hash},
    )

    asof_v1 = one_issue(runj(["show", ISSUE_ID, "--as-of", v1_hash]))
    asof_v2 = one_issue(runj(["show", ISSUE_ID, "--as-of", v2_hash]))
    current_1 = one_issue(runj(["show", ISSUE_ID]))
    current_2 = one_issue(runj(["show", ISSUE_ID]))
    check("asof_v1_replays_v1", description(asof_v1) == "TS032-V1", description(asof_v1))
    check("asof_v2_replays_v2", description(asof_v2) == "TS032-V2", description(asof_v2))
    check("fresh_process_current_read_1_is_v2", description(current_1) == "TS032-V2", description(current_1))
    check("fresh_process_current_read_2_is_v2", description(current_2) == "TS032-V2", description(current_2))

    history_later = history()
    later_hashes = {history_hash(e) for e in history_later if isinstance(e, dict)}
    check(
        "fresh_process_history_preserves_both_write_commits",
        {v1_hash, v2_hash}.issubset(later_hashes),
        {"required": [v1_hash, v2_hash], "observed_count": len(later_hashes)},
    )

    after_remote = subprocess.run(
        ["git", "remote"], cwd=LAB, text=True, capture_output=True, timeout=8
    )
    check(
        "isolated_git_has_no_remote_after_writes",
        after_remote.returncode == 0 and not after_remote.stdout.strip(),
        after_remote.stdout.strip(),
    )

    report["measurements"].update(
        {
            "base_commit": base_commit,
            "create_commit": create_commit,
            "update_commit": update_commit,
            "history_after_create_entries": len(history_v1),
            "history_after_update_entries": len(history_v2),
            "history_later_entries": len(history_later),
            "create_vc_status": create_status,
            "update_vc_status": update_status,
            "v1_history_commit": v1_hash,
            "v2_history_commit": v2_hash,
        }
    )
    report["status"] = "PASS_NATIVE_HISTORY_AUTOCOMMIT_AND_ASOF_REPLAY"
    report["disposition"] = "B_FIRST_NATIVE_HISTORY_QUALIFIED_EXPERIMENTAL_ONLY"
    report["next"] = (
        "Separate real-provider/effect-identity experiment; preserve no-replay and exact effect identity. "
        "Kernel hash-chain semantic equivalence remains NOT_QUALIFIED."
    )
except Exception as exc:
    report["status"] = "FAIL_NATIVE_HISTORY_CHECKPOINT"
    report["error"] = str(exc)
    report["traceback_tail"] = traceback.format_exc().splitlines()[-12:]
    report["disposition"] = "B_FIRST_HISTORY_REMAINS_NOT_QUALIFIED"
    write_report()
    print("TS_BEADS032_NATIVE_HISTORY=FAIL;" + str(exc))
    raise
else:
    write_report()
    print(
        "TS_BEADS032_NATIVE_HISTORY="
        + report["status"]
        + ";checks="
        + str(len(report["checks"]))
        + ";bd_processes="
        + str(report["measurements"]["bd_processes"])
        + ";Product=NONE;provider=NONE;shared_Dolt=NONE"
    )
