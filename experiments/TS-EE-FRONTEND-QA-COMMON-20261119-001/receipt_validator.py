#!/usr/bin/env python3
"""TS EE frontend-browser QA v0 report consistency checker.
Input is untrusted report data. This checks structure, NOT provider authenticity.
"""
import argparse
import json
from pathlib import Path
import re
import sys

WIDTHS = (320, 375, 768, 1440)
SCENARIOS = ("viewport", "routing", "history", "deep_link_refresh",
             "sku_negative", "keyboard_focus", "a11y_basic", "console_http")
STAGES = ("identity", "dependencies", "integration", "build", "browser")
STATES = ("PASS", "FAIL", "SKIPPED", "NOT_RUN", "BLOCKED")
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
ATTEMPT = re.compile(r"^[A-Z0-9][A-Z0-9_-]{8,127}$")
SAFE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")

def evaluate(data):
    errors = []
    def need(test, reason):
        if not test:
            errors.append(reason)
    if not isinstance(data, dict):
        return {"status": "INVALID_REPORT", "errors": ["report_not_object"]}
    need(data.get("schema") == "ts-ee/frontend-browser-qa/v0", "wrong_schema")
    need(data.get("product_effect") == "NONE", "product_effect_not_none")
    need(bool(ATTEMPT.fullmatch(str(data.get("attempt", "")))), "bad_attempt")
    source = data.get("source", {})
    if not isinstance(source, dict):
        source = {}
    need(source.get("subject_kind") in ("SYNTHETIC", "PRODUCT_PREVIEW"), "bad_subject_kind")
    need(isinstance(source.get("repository"), str) and "/" in source.get("repository", ""), "bad_repo")
    need(bool(HEX40.fullmatch(str(source.get("commit", "")))), "bad_commit")
    need(bool(HEX40.fullmatch(str(source.get("tree", "")))), "bad_tree")
    runner = data.get("runner", {})
    if not isinstance(runner, dict):
        runner = {}
    need(runner.get("engine") in ("PLAYWRIGHT_PYTHON", "CHROMEDRIVER_NODE"), "bad_engine")
    need(isinstance(runner.get("version"), str) and bool(runner.get("version")), "missing_version")
    need(isinstance(runner.get("os"), str) and bool(runner.get("os")), "missing_os")
    need(isinstance(runner.get("native_run_id"), str) and bool(runner.get("native_run_id")), "missing_native_run_id")
    need(runner.get("head_sha") == source.get("commit"), "native_head_mismatch")
    need(isinstance(runner.get("attempt_number"), int) and not isinstance(runner.get("attempt_number"), bool)
         and runner.get("attempt_number") >= 1, "invalid_attempt_number")
    stages = data.get("stages", {})
    if not isinstance(stages, dict):
        stages = {}
    for stage in STAGES:
        need(stages.get(stage) in STATES, "bad_stage_" + stage)
    scenarios = data.get("scenarios", {})
    if not isinstance(scenarios, dict):
        scenarios = {}
    for scenario in SCENARIOS:
        need(scenarios.get(scenario) in STATES, "bad_scenario_" + scenario)
    widths = data.get("viewports", [])
    if not isinstance(widths, list):
        widths = []
    width_map = {}
    for item in widths:
        if not isinstance(item, dict):
            errors.append("invalid_viewport_item")
            continue
        width = item.get("width")
        need(isinstance(width, int) and not isinstance(width, bool) and width in WIDTHS,
             "unexpected_width")
        need(item.get("status") in STATES, "invalid_viewport_status")
        if width in width_map:
            errors.append("duplicate_viewport_" + str(width))
        width_map[width] = item.get("status")
    need(sorted(width_map) == list(WIDTHS), "missing_viewport")
    if stages.get("browser") == "PASS":
        need(all(width_map.get(w) == "PASS" for w in WIDTHS), "browser_pass_without_all_viewports")
    if source.get("subject_kind") == "PRODUCT_PREVIEW" and stages.get("browser") == "PASS":
        need(stages.get("integration") == "PASS", "product_browser_without_integration")
        need(stages.get("build") == "PASS", "product_browser_without_build")
    if stages.get("browser") == "PASS":
        need(stages.get("identity") == "PASS" and stages.get("dependencies") == "PASS",
             "browser_without_identity_and_dependencies")
    network = data.get("network", {})
    if not isinstance(network, dict):
        network = {}
    need(network.get("enforcement") in ("PREVENTIVE_BROWSER_ABORT", "OBSERVE_ONLY"),
         "bad_network_enforcement")
    need(network.get("service_workers") in ("BLOCKED", "NOT_VERIFIED"),
         "bad_service_workers")
    counts = []
    for k in ("outbound_attempted", "outbound_blocked", "outbound_escaped"):
        v = network.get(k)
        need(isinstance(v, int) and not isinstance(v, bool) and v >= 0, "bad_network_" + k)
        counts.append(v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else -1)
    if all(v >= 0 for v in counts):
        need(counts[1] + counts[2] == counts[0], "inconsistent_network_counts")
    if stages.get("browser") == "PASS" and counts[-1] > 0:
        errors.append("browser_pass_with_network_leak")
    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = []
    names = []
    shots = set()
    trace_or_log = False
    for item in artifacts:
        if not isinstance(item, dict):
            errors.append("artifact_not_object")
            continue
        name, hashv, size, typ = item.get("name"), item.get("sha256"), item.get("bytes"), item.get("kind")
        need(isinstance(name, str) and bool(SAFE_NAME.fullmatch(name)), "unsafe_artifact_name")
        need(bool(HEX64.fullmatch(str(hashv))), "bad_artifact_hash")
        need(isinstance(size, int) and not isinstance(size, bool) and size > 0, "bad_artifact_size")
        need(typ in ("SCREENSHOT", "TRACE", "LOG"), "bad_artifact_kind")
        if isinstance(name, str):
            names.append(name)
        if typ == "SCREENSHOT":
            shots.add(item.get("width"))
        if typ in ("TRACE", "LOG"):
            trace_or_log = True
    need(len(names) == len(set(names)), "duplicate_artifact_name")
    if stages.get("browser") == "PASS":
        need(all(w in shots for w in WIDTHS), "missing_viewport_screenshot")
        need(trace_or_log, "no_trace_or_log")
    original = data.get("original", {})
    if not isinstance(original, dict):
        original = {}
    need(original.get("custody") in ("TEST_VECTOR", "PROVIDER_NATIVE_READBACK", "LIBRARY_VERIFIED",
                                      "GIT_BYTES_VERIFIED"), "bad_custody")
    need(bool(HEX64.fullmatch(str(original.get("sha256", "")))), "bad_original_hash")
    need(isinstance(original.get("bytes"), int) and not isinstance(original.get("bytes"), bool)
         and original.get("bytes") > 0, "bad_original_bytes")
    need(isinstance(original.get("reference"), str) and bool(original.get("reference")),
         "missing_original_reference")
    limitations = data.get("limitations")
    need(isinstance(limitations, list) and all(isinstance(s, str) for s in limitations),
         "bad_limitations")
    if errors:
        return {"status": "INVALID_REPORT", "errors": sorted(set(errors))}
    blockers = []
    if stages["browser"] != "PASS":
        blockers.append("browser_not_pass")
    if any(scenarios[k] != "PASS" for k in SCENARIOS):
        blockers.append("scenario_not_fully_executed")
    if source["subject_kind"] == "PRODUCT_PREVIEW" and (
            stages["integration"] != "PASS" or stages["build"] != "PASS"):
        blockers.append("product_prerequisite_not_pass")
    if network["enforcement"] != "PREVENTIVE_BROWSER_ABORT":
        blockers.append("egress_only_observed")
    if network["service_workers"] != "BLOCKED":
        blockers.append("service_worker_interception_unverified")
    if network["outbound_escaped"] != 0:
        blockers.append("nonloopback_egress_observed")
    if blockers:
        return {"status": "INCOMPLETE_OR_BLOCKED", "reasons": sorted(set(blockers))}
    # Shape correctness is never native provider attestation or Product acceptance.
    return {"status": "SHAPE_PASS_TEST_VECTOR" if original["custody"] == "TEST_VECTOR"
            else "SHAPE_PASS_REQUIRES_INDEPENDENT_NATIVE_ATTESTATION",
            "subject_kind": source["subject_kind"], "scenario_count": len(SCENARIOS),
            "viewports": list(WIDTHS)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    args = ap.parse_args()
    try:
        r = evaluate(json.loads(args.report.read_text(encoding="utf8")))
    except (OSError, ValueError) as error:
        r = {"status": "INVALID_REPORT", "errors": [type(error).__name__]}
    print(json.dumps(r, sort_keys=True))
    return 0 if r["status"].startswith("SHAPE_PASS") else 1

if __name__ == "__main__":
    sys.exit(main())
