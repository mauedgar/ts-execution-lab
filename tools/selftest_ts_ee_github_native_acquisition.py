"""Exact-reason nonProduct tests for real adapter parser and provider-shaped data.

Mock transport is used ONLY for negative fixtures. A separate one-time
GitHub Actions step executes authenticated HTTPS against an already terminal
original run. Never claim these fakes are independently verified provider data.
"""
from __future__ import annotations

import base64
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import ts_ee_github_native_acquisition as native
from urllib.parse import quote

from ts_ee_github_native_acquisition import (
    BlockedPrecondition, REPO, TRANSPORT, REQUEST_VERSION, PAGE,
    blob_sha, qualify, all_branch_runs, request_json,
)

RUN_ID = 43071422341
OLD_HEAD = "34ed8e6c28c338e454889f9dfcf51f3cf1af899b"
OLD_TREE = "bc75b5f1d6c93741ebb6230773ae115c7476d6b0"
OLD_PARENT = "acbe105f08b08ea098fd38641fe17470314cb8bc"
OLD_PARENT_TREE = "abff337a7b159a74ec178ec6891fddd87d3b9332"
OLD_WF = ".github/workflows/ts-ee-control-join-qual-20261111-001.yml"
OLD_MARKER = (
    ".github/ts-ee-original-dispatch/"
    "TS-EE-CONTROL-JOIN-QUAL-20261111-001-A001.json"
)
OLD_REF = "refs/heads/ee/ts-ee-actions-original-binding-20261111-002"
OLD_REQUEST = (
    "mauedgar/ts-execution-transport@"
    "6fa4cc8ce05ae1d16b87945704e20e6387f1dc23:"
    "requests/TS-EE-CONTROL-JOIN-QUAL-20261111-001/REQUEST.md"
)
OLD_ATTEMPT = "TS-EE-CONTROL-JOIN-QUAL-20261111-001-A001"
NEW_ATTEMPT = "TS-EE-GITHUB-NATIVE-ACQ-20261111-001-A001"
NEW_WF = ".github/workflows/ts-ee-github-native-qual-20261111-001.yml"
NEW_MARKER = ".github/ts-ee-original-dispatch/" + NEW_ATTEMPT + ".json"
NEW_REQ = ("mauedgar/ts-execution-transport@" + ("a" * 40) +
           ":requests/TS-EE-GITHUB-NATIVE-ACQ-20261111-001/REQUEST.md")
NEW_PARENT, NEW_TREE = "b" * 40, "c" * 40
NEW_WF_BYTES = b"name: current original test\non: push\n"
NEW_WF_BLOB = blob_sha(NEW_WF_BYTES)
CURRENT_RUN = 1234567
CURRENT_HEAD = "e" * 40
CURRENT_TREE = "9" * 40
CURRENT_REF = "refs/heads/ee/ts-ee-github-native-currentrun-20261111-003"
CURRENT_BRANCH = CURRENT_REF.removeprefix("refs/heads/")
CURRENT_RUNS_ENDPOINT = (
    f"/repos/{TRANSPORT}/actions/runs?branch="
    + quote(CURRENT_BRANCH, safe="") + "&per_page=100&page=1"
)
RUNS_ENDPOINT = ("/repos/" + REPO + "/actions/runs?branch=" +
                 quote(OLD_REF.removeprefix("refs/heads/"), safe="") +
                 "&per_page=100&page=1")


def file_record(raw):
    return {
        "type": "file", "encoding": "base64",
        "content": base64.b64encode(raw).decode(),
        "sha": blob_sha(raw), "size": len(raw),
    }


def fixture():
    old_source = (
        f"ExecutionAttempt {OLD_ATTEMPT}\n"
        f"Frozen parent commit {OLD_PARENT}\n"
        "Workflow blob follows in original external receipt.\n"
    )
    wf_source = "name: frozen\non:\n  push: true\n"
    wf_sha = blob_sha(wf_source.encode())
    old_source += wf_sha + "\n"
    marker = {
        "version": "TS-EE-ACTIONS-ORIGINAL-BINDING-v1",
        "execution_attempt": OLD_ATTEMPT,
        "repository": REPO,
        "ref": OLD_REF,
        "source_parent_commit": OLD_PARENT,
        "source_parent_tree": OLD_PARENT_TREE,
        "workflow_path": OLD_WF,
        "workflow_blob": wf_sha,
        "marker_path": OLD_MARKER,
        "control_request": OLD_REQUEST,
    }
    marker_raw = (json.dumps(marker, sort_keys=True) + "\n").encode()
    marker_sha = blob_sha(marker_raw)
    target = {
        "repository": REPO, "ref": OLD_REF, "run_id": RUN_ID,
        "head_sha": OLD_HEAD, "head_tree": OLD_TREE,
        "source_parent_commit": OLD_PARENT,
        "source_parent_tree": OLD_PARENT_TREE,
        "workflow_path": OLD_WF, "workflow_blob": wf_sha,
        "marker_path": OLD_MARKER, "marker_blob": marker_sha,
        "control_request": OLD_REQUEST,
        "control_request_blob": blob_sha(old_source.encode()),
        "execution_attempt": OLD_ATTEMPT,
    }
    request = {
        "version": REQUEST_VERSION, "scope": "NONPRODUCT",
        "qualification_attempt": NEW_ATTEMPT,
        "source_parent_commit": NEW_PARENT,
        "source_parent_tree": NEW_TREE,
        "workflow_path": NEW_WF,
        "workflow_blob": NEW_WF_BLOB,
        "marker_path": NEW_MARKER,
        "target": target,
    }
    code_fence = chr(96) * 3
    request_bytes = (
        "# Competent Control original experimental request\n" +
        code_fence + "json\n" + json.dumps(request, sort_keys=True) +
        "\n" + code_fence + "\n"
    ).encode()
    control_ref = NEW_REQ
    new_ref_sha = "a" * 40
    new_path = "requests/TS-EE-GITHUB-NATIVE-ACQ-20261111-001/REQUEST.md"
    old_ref_sha = OLD_REQUEST.split("@")[1].split(":")[0]
    old_path = OLD_REQUEST.split(":")[1]
    old_payload = old_source.encode()
    left = [
        {"path": ".github", "mode": "040000", "type": "tree", "sha": "2"*40},
        {"path": ".github/workflows", "mode": "040000", "type": "tree", "sha": "3"*40},
        {"path": OLD_WF, "mode": "100644", "type": "blob", "sha": wf_sha},
        {"path": "README.md", "mode": "100644", "type": "blob", "sha": "f"*40},
    ]
    right = deepcopy(left) + [
        {"path": ".github/ts-ee-original-dispatch",
         "mode": "040000", "type": "tree", "sha": "4"*40},
        {"path": OLD_MARKER, "mode": "100644", "type": "blob",
         "sha": marker_sha},
    ]
    right[0]["sha"] = "5"*40  # expected parent-directory tree change
    old_run = {
        "id": RUN_ID, "event": "push", "status": "completed",
        "conclusion": "success", "run_attempt": 1,
        "head_branch": OLD_REF.removeprefix("refs/heads/"),
        "head_sha": OLD_HEAD, "path": OLD_WF,
        "repository": {"full_name": REPO},
    }
    listing = {"total_count": 1, "workflow_runs": [
        {"id": RUN_ID, "head_branch": old_run["head_branch"]}
    ]}
    urls = {
        f"/repos/{TRANSPORT}/contents/{new_path}?ref={new_ref_sha}":
            (file_record(request_bytes), {}),
        f"/repos/{TRANSPORT}/contents/{old_path}?ref={old_ref_sha}":
            (file_record(old_payload), {}),
        f"/repos/{REPO}/contents/{OLD_MARKER}?ref={OLD_HEAD}":
            (file_record(marker_raw), {}),
        f"/repos/{REPO}/contents/{OLD_WF}?ref={OLD_HEAD}":
            (file_record(wf_source.encode()), {}),
        f"/repos/{REPO}/git/commits/{OLD_HEAD}": ({
            "sha": OLD_HEAD, "parents": [{"sha": OLD_PARENT}],
            "tree": {"sha": OLD_TREE},
        }, {}),
        f"/repos/{REPO}/git/commits/{OLD_PARENT}": ({
            "sha": OLD_PARENT, "tree": {"sha": OLD_PARENT_TREE},
        }, {}),
        f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1": ({
            "sha": OLD_TREE, "truncated": False, "tree": right,
        }, {}),
        f"/repos/{REPO}/git/trees/{OLD_PARENT_TREE}?recursive=1": ({
            "sha": OLD_PARENT_TREE, "truncated": False, "tree": left,
        }, {}),
        f"/repos/{REPO}/actions/runs/{RUN_ID}": (old_run, {}),
        RUNS_ENDPOINT: (listing, {"link": ""}),
    }
    current_marker = {
        "version": "TS-EE-ACTIONS-ORIGINAL-BINDING-v1",
        "execution_attempt": NEW_ATTEMPT,
        "repository": TRANSPORT,
        "ref": CURRENT_REF,
        "source_parent_commit": NEW_PARENT,
        "source_parent_tree": NEW_TREE,
        "workflow_path": NEW_WF,
        "workflow_blob": NEW_WF_BLOB,
        "marker_path": NEW_MARKER,
        "control_request": NEW_REQ,
    }
    current_marker_bytes = (json.dumps(current_marker, sort_keys=True) + "\n").encode()
    current_marker_blob = blob_sha(current_marker_bytes)
    current_run = {
        "id": CURRENT_RUN, "event": "push", "status": "in_progress",
        "conclusion": None, "run_attempt": 1,
        "head_branch": CURRENT_BRANCH, "head_sha": CURRENT_HEAD,
        "path": NEW_WF,
        "repository": {"full_name": TRANSPORT},
    }
    urls.update({
        f"/repos/{TRANSPORT}/actions/runs/{CURRENT_RUN}": (current_run, {}),
        f"/repos/{TRANSPORT}/git/commits/{CURRENT_HEAD}": ({
            "sha": CURRENT_HEAD, "tree": {"sha": CURRENT_TREE},
            "parents": [{"sha": NEW_PARENT}],
        }, {}),
        f"/repos/{TRANSPORT}/git/commits/{NEW_PARENT}": ({
            "sha": NEW_PARENT, "tree": {"sha": NEW_TREE},
        }, {}),
        f"/repos/{TRANSPORT}/commits/{CURRENT_HEAD}": ({
            "sha": CURRENT_HEAD, "files": [{
                "filename": NEW_MARKER, "status": "added",
                "sha": current_marker_blob,
            }],
        }, {}),
        f"/repos/{TRANSPORT}/contents/{NEW_MARKER}?ref={CURRENT_HEAD}": (
            file_record(current_marker_bytes), {}),
        f"/repos/{TRANSPORT}/contents/{NEW_WF}?ref={CURRENT_HEAD}": (
            file_record(NEW_WF_BYTES), {}),
        CURRENT_RUNS_ENDPOINT: ({
            "total_count": 1, "workflow_runs": [
                {"id": CURRENT_RUN, "head_branch": CURRENT_BRANCH}
            ],
        }, {"link": ""}),
    })
    runtime = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": TRANSPORT,
        "GITHUB_REF": CURRENT_REF,
        "GITHUB_SHA": CURRENT_HEAD,
        "GITHUB_RUN_ID": str(CURRENT_RUN),
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_EVENT_NAME": "push",
    }
    guard = {
        "version": "TS-EE-ACTIONS-ORIGINAL-BINDING-v1",
        "status": "TS_EE_ORIGINAL_GIT_TRANSITION_PASS",
        "execution_attempt": NEW_ATTEMPT,
        "repository": TRANSPORT,
        "ref": CURRENT_REF,
        "run_id": str(CURRENT_RUN),
        "head_commit": CURRENT_HEAD,
        "head_tree": CURRENT_TREE,
        "marker_blob": current_marker_blob,
        "source_parent_commit": NEW_PARENT,
        "source_parent_tree": NEW_TREE,
        "workflow_blob": NEW_WF_BLOB,
        "control_request": NEW_REQ,
        "effect": "READ_ONLY_IDENTITY_PREFLIGHT",
        "product_effect": "NONE", "run_attempt": 1,
    }
    return urls, guard, runtime


class FakeRead:
    def __init__(self, urls):
        self.urls = urls
        self.queries = []
    def __call__(self, path):
        self.queries.append(path)
        if path not in self.urls:
            raise AssertionError("UNSUPPORTED_FAKE_URL")
        return deepcopy(self.urls[path])


def run_case(name, change, expected):
    urls, guard, runtime = fixture()
    change(urls, guard)
    fake = FakeRead(urls)
    try:
        qualify(fake, NEW_REQ, guard, runtime)
    except BlockedPrecondition as exc:
        assert str(exc) == expected, (name, expected, str(exc))
        print("NEGATIVE_PASS_" + name + "_" + expected)
    else:
        raise AssertionError("FALSE_ACCEPT_" + name)


def modify(urls, path, operation):
    old, head = urls[path]
    value = deepcopy(old)
    operation(value)
    urls[path] = value, head


def main():
    urls, guard, runtime = fixture()
    fake = FakeRead(urls)
    good = qualify(fake, NEW_REQ, guard, runtime)
    assert good["status"] == "TS_EE_GITHUB_NATIVE_OBSERVATION_ONLY"
    assert good["control_authority"] == "NOT_VERIFIED_BY_ADAPTER"
    assert good["execution_admitted"] is False
    assert good["operational_entrypoint_authorized"] is False
    assert good["run_list_atomic_snapshot"] is False
    assert good["complete_tree_and_run_inventory"] is True
    assert good["all_branch_run_ids"] == [RUN_ID]
    assert good["product_effect"] == "NONE"
    assert fake.queries.count(RUNS_ENDPOINT) == 2
    print("SYNTHETIC_PROVIDER_SHAPE_POSITIVE_PASS")

    run_case("FORGED_REQUEST_BODY", lambda u, g:
             modify(u, "/repos/" + TRANSPORT +
                    "/contents/requests/TS-EE-GITHUB-NATIVE-ACQ-20261111-001/REQUEST.md?ref=" + "a"*40,
                    lambda x: x.update(content=base64.b64encode(
                        b"forged JSON control").decode())),
             "NATIVE_CONTENT_BLOB_MISMATCH")
    run_case("FORGED_OLD_REQUEST", lambda u, g:
             modify(u, "/repos/" + TRANSPORT + "/contents/" +
                    OLD_REQUEST.split(":")[1] + "?ref=" +
                    OLD_REQUEST.split("@")[1].split(":")[0],
                    lambda x: x.update(sha="0"*40)),
             "NATIVE_CONTENT_BLOB_MISMATCH")
    run_case("FORGED_MARKER_BLOB", lambda u, g:
             modify(u, f"/repos/{REPO}/contents/{OLD_MARKER}?ref={OLD_HEAD}",
                    lambda x: x.update(sha="0"*40)),
             "NATIVE_CONTENT_BLOB_MISMATCH")
    run_case("TRUNCATED_TREE", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x.update(truncated=True)),
             "NATIVE_TREE_TRUNCATED")
    run_case("DUPLICATE_TREE_DIRECTORY", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append(deepcopy(x["tree"][0]))),
             "NATIVE_TREE_DUPLICATE_PATH")
    run_case("MALFORMED_TREE_MODE", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"][0].update(mode="100644")),
             "NATIVE_TREE_TYPE_MODE_INVALID")
    run_case("ORPHAN_EMPTY_TREE", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append({
                        "path": "orphan", "mode": "040000",
                        "type": "tree", "sha": "1"*40
                    })),
             "NATIVE_EMPTY_OR_ORPHAN_TREE")
    run_case("BLOB_DIRECTORY_COLLISION", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append({
                        "path": "README.md/child", "mode": "100644",
                        "type": "blob", "sha": "1"*40
                    })),
             "NATIVE_TREE_NONCANONICAL_HIERARCHY")
    run_case("UNEXPECTED_SYMLINK", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append({
                        "path": "new-symlink", "mode": "120000",
                        "type": "blob", "sha": "1"*40
                    })),
             "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    run_case("UNEXPECTED_SUBMODULE", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append({
                        "path": "new-submodule", "mode": "160000",
                        "type": "commit", "sha": "1"*40
                    })),
             "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    run_case("HIDDEN_EXTRA_MODIFIED", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"][3].update(sha="1"*40)),
             "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    run_case("HIDDEN_EXTRA_ADDED", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].append({
                        "path": "rogue.py", "mode": "100644",
                        "type": "blob", "sha": "1"*40,
                    })),
             "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    run_case("MARKER_DELETED", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"].pop()),
             "NATIVE_EMPTY_OR_ORPHAN_TREE")
    run_case("MARKER_RENAMED", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"][-1].update(path=".github/ts-ee-original-dispatch/renamed.json")),
             "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    run_case("MARKER_WRONG_MODE", lambda u, g:
             modify(u, f"/repos/{REPO}/git/trees/{OLD_TREE}?recursive=1",
                    lambda x: x["tree"][-1].update(mode="120000")),
             "NATIVE_MARKER_BLOB_OR_MODE_INVALID")
    run_case("INCOMPLETE_RUN_PAGE", lambda u, g:
             modify(u, RUNS_ENDPOINT,
                    lambda x: x.update(total_count=2)),
             "NATIVE_BRANCH_NOT_SINGLE_RUN")
    run_case("DUPLICATE_RUN_IDS", lambda u, g:
             modify(u, RUNS_ENDPOINT, lambda x: x.update(
                 total_count=2, workflow_runs=[
                     x["workflow_runs"][0], x["workflow_runs"][0],
                 ])),
             "NATIVE_BRANCH_NOT_SINGLE_RUN")
    run_case("SPOOFED_NEXT_PAGE", lambda u, g:
             u.__setitem__(RUNS_ENDPOINT, (u[RUNS_ENDPOINT][0], {
                 "link": "<https://api.github.com/repos/" + REPO +
                         "/actions/runs?branch=ee%2Funknown&per_page=100&page=2>; rel=\"next\""
             })),
             "NATIVE_UNEXPECTED_PAGINATION_LINK")
    run_case("MALFORMED_NEXT_LINK", lambda u, g:
             u.__setitem__(RUNS_ENDPOINT, (u[RUNS_ENDPOINT][0], {
                 "link": "https://evil.invalid/run?page=2"
             })),
             "NATIVE_UNEXPECTED_PAGINATION_LINK")
    run_case("FOREIGN_RUN_BRANCH", lambda u, g:
             modify(u, RUNS_ENDPOINT,
                    lambda x: x["workflow_runs"][0].update(
                        head_branch="main")),
             "NATIVE_RUN_PAGE_FOREIGN_ENTRY")
    run_case("WRONG_NATIVE_RUN", lambda u, g:
             modify(u, f"/repos/{REPO}/actions/runs/{RUN_ID}",
                    lambda x: x.update(run_attempt=2)),
             "NATIVE_PROVIDER_RUN_MISMATCH")
    run_case("FORGED_GUARD", lambda u, g:
             g.update(source_parent_commit="0"*40),
             "CURRENT_ORIGINAL_SOURCE_NOT_FROZEN")
    # Current original: separately authenticated provider run/commit/marker.
    run_case("CURRENT_GUARD_STATUS", lambda u, g:
             g.update(status="FORGED_PASS"),
             "CURRENT_GUARD_STATUS_INVALID")
    run_case("CURRENT_GUARD_RUN_ID", lambda u, g:
             g.update(run_id=str(CURRENT_RUN+1)),
             "CURRENT_GUARD_RUN_ID_INVALID")
    run_case("CURRENT_GUARD_REPOSITORY", lambda u, g:
             g.update(repository=REPO),
             "CURRENT_GUARD_REPOSITORY_INVALID")
    run_case("CURRENT_GUARD_REF", lambda u, g:
             g.update(ref="refs/heads/ee/forged"),
             "CURRENT_GUARD_REF_INVALID")
    run_case("CURRENT_GUARD_HEAD", lambda u, g:
             g.update(head_commit="0"*40),
             "CURRENT_GUARD_HEAD_INVALID")
    run_case("CURRENT_GUARD_TREE", lambda u, g:
             g.update(head_tree="0"*40),
             "CURRENT_NATIVE_COMMIT_MISMATCH")
    run_case("CURRENT_GUARD_MARKER", lambda u, g:
             g.update(marker_blob="0"*40),
             "CURRENT_NATIVE_MARKER_ONLY_DELTA_INVALID")
    run_case("CURRENT_PROVIDER_RUN", lambda u, g:
             modify(u, f"/repos/{TRANSPORT}/actions/runs/{CURRENT_RUN}",
                    lambda x: x.update(status="completed")),
             "CURRENT_NATIVE_RUN_MISMATCH")
    run_case("CURRENT_PROVIDER_MARKER", lambda u, g:
             modify(u,
                    f"/repos/{TRANSPORT}/contents/{NEW_MARKER}?ref={CURRENT_HEAD}",
                    lambda x: x.update(sha="0"*40)),
             "NATIVE_CONTENT_BLOB_MISMATCH")
    run_case("CURRENT_PROVIDER_DUPLICATE", lambda u, g:
             modify(u, CURRENT_RUNS_ENDPOINT,
                    lambda x: x.update(total_count=2)),
             "CURRENT_NATIVE_ORIGINAL_RUN_NOT_UNIQUE")
    # The adapter never accepts caller-provided 'native' or 'external'
    # dictionaries. A coherent forged JSON tuple can pass legacy reconcile
    # in isolation, but is not a supported input to this native acquisition.
    from ts_ee_github_native_acquisition import GitHubRead
    try:
        GitHubRead("")
    except BlockedPrecondition as exc:
        assert str(exc) == "GITHUB_TOKEN_NOT_AVAILABLE"
        print("NEGATIVE_PASS_MISSING_AUTHENTICATED_TOKEN")
    else:
        raise AssertionError("FALSE_ACCEPT_UNAUTHENTICATED_NATIVE_MODE")
    # A fully self-consistent provider-shaped fixture MUST NOT become authority
    # merely by passing native observational checks or the CLI exit contract.
    with tempfile.TemporaryDirectory(prefix="ts-ee-native-observer-") as scratch:
        guard_file = Path(scratch) / "original_guard.json"
        guard_file.write_text(json.dumps(guard), encoding="utf-8")
        output = io.StringIO()
        with patch("ts_ee_github_native_acquisition.GitHubRead",
                   return_value=FakeRead(urls)), \
             patch("sys.argv", ["ts_ee_github_native_acquisition",
                                "--request-ref", NEW_REQ,
                                "--original-guard", str(guard_file)]), \
             patch.dict(os.environ, runtime, clear=False), \
             redirect_stdout(output):
            cli_exit = native.main()
        observed = json.loads(output.getvalue())
        assert cli_exit == 3
        assert observed["status"] == "TS_EE_GITHUB_NATIVE_OBSERVATION_ONLY"
        assert observed["control_authority"] == "NOT_VERIFIED_BY_ADAPTER"
        assert observed["execution_admitted"] is False
        print("NEGATIVE_PASS_SELF_CONSISTENT_REQUEST_NOT_CONTROL_APPROVAL")

    print("TS_EE_NATIVE_ADAPTER_1_POSITIVE_33_NEGATIVES_1_AUTHORITY_BOUNDARY_PASS")


if __name__ == "__main__":
    main()
