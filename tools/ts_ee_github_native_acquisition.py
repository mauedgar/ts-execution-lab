"""NonProduct TS EE GitHub native read-only acquisition (no Product authority).

Inputs must be frozen by competent Control. The authenticated provider API
is the origin for facts; this module does not itself grant Developer authority.
"""
from __future__ import annotations
import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse, parse_qs
from urllib.request import HTTPRedirectHandler, Request, build_opener

VERSION = "TS-EE-GITHUB-NATIVE-ACQUISITION-v1"
REQUEST_VERSION = "TS-EE-GITHUB-NATIVE-REQUEST-v1"
REPO = "mauedgar/ts-execution-lab"
TRANSPORT = "mauedgar/ts-execution-transport"
HEX = re.compile(r"[0-9a-f]{40}\Z")
ATTEMPT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{7,127}\Z")
REF = re.compile(r"refs/heads/ee/[a-z0-9._/-]+\Z")
PATH = re.compile(r"[A-Za-z0-9_.\-/]+\Z")
CONTROL = re.compile(
    r"mauedgar/ts-execution-transport@([0-9a-f]{40}):"
    r"(requests/[A-Za-z0-9_.\-/]+\.md)\Z"
)
LIMIT = 2_500_000
PAGE = 100
MAX_PAGES = 8
REQUEST_FIELDS = frozenset({
    "version", "scope", "qualification_attempt", "source_parent_commit",
    "source_parent_tree", "workflow_path", "workflow_blob",
    "marker_path", "target",
})
TARGET_FIELDS = frozenset({
    "repository", "ref", "run_id", "head_sha", "head_tree",
    "source_parent_commit", "source_parent_tree", "workflow_path",
    "workflow_blob", "marker_path", "marker_blob",
    "control_request", "control_request_blob", "execution_attempt",
})


class BlockedPrecondition(Exception):
    pass


def need(ok, code):
    if not ok:
        raise BlockedPrecondition(code)


def safe_path(path):
    return (type(path) is str and 0 < len(path) <= 250
            and PATH.fullmatch(path) is not None
            and all(x not in ("", ".", "..") for x in path.split("/"))
            and not path.startswith("/") and not path.endswith("/"))


def blob_sha(payload):
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode() + b"\x00" + payload,
    ).hexdigest()


def strict_pairs(pairs):
    result = {}
    for k, v in pairs:
        need(k not in result, "DUPLICATE_JSON_KEY")
        result[k] = v
    return result


def parse_json(payload):
    need(type(payload) is bytes and 0 < len(payload) <= LIMIT,
         "JSON_SIZE_INVALID")
    try:
        value = json.loads(payload.decode("utf-8", "strict"),
                           object_pairs_hook=strict_pairs)
    except (UnicodeError, ValueError) as exc:
        raise BlockedPrecondition("JSON_PARSE_INVALID") from exc
    need(type(value) is dict, "JSON_NOT_OBJECT")
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise BlockedPrecondition("API_REDIRECT_NOT_ALLOWED")


class GitHubRead:
    """Authenticated GET only to the literal api.github.com origin."""

    def __init__(self, token):
        need(type(token) is str and len(token) >= 20 and
             not any(ch.isspace() for ch in token),
             "GITHUB_TOKEN_NOT_AVAILABLE")
        self.token = token
        self.opener = build_opener(NoRedirect())

    def __call__(self, endpoint):
        need(type(endpoint) is str and endpoint.startswith("/repos/"),
             "NATIVE_ENDPOINT_NOT_ALLOWED")
        url = "https://api.github.com" + endpoint
        parts = urlparse(url)
        need(parts.scheme == "https" and parts.netloc == "api.github.com"
             and not parts.fragment and ".." not in parts.path.split("/"),
             "NATIVE_HOST_OR_PATH_INVALID")
        request = Request(url, method="GET", headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ts-ee-nonproduct-native-v1",
        })
        try:
            with self.opener.open(request, timeout=18) as reply:
                need(reply.status == 200, "API_NOT_OK")
                length = reply.headers.get("Content-Length")
                if length:
                    need(length.isdigit() and int(length) <= LIMIT,
                         "NATIVE_RESPONSE_TOO_LARGE")
                raw = reply.read(LIMIT + 1)
                need(0 < len(raw) <= LIMIT, "NATIVE_RESPONSE_TOO_LARGE")
                return parse_json(raw), {"link": reply.headers.get("Link", "")}
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            # Never log URL/authorization header or response body.
            raise BlockedPrecondition("AUTHENTICATED_GITHUB_READ_FAILED") from exc


def get(fetch, url):
    reply = fetch(url)
    need(type(reply) is tuple and len(reply) == 2 and
         type(reply[0]) is dict and type(reply[1]) is dict,
         "UNVERIFIED_NATIVE_TRANSPORT_SHAPE")
    return reply


def file_bytes(fetch, repository, path, ref, expected_sha=None):
    need(repository in (REPO, TRANSPORT) and safe_path(path)
         and HEX.fullmatch(ref) is not None,
         "CONTENT_SOURCE_NOT_FROZEN")
    encoded_path = "/".join(quote(x, safe="") for x in path.split("/"))
    obj, _ = get(fetch, f"/repos/{repository}/contents/{encoded_path}?ref={ref}")
    need(obj.get("type") == "file" and
         obj.get("encoding") == "base64" and
         type(obj.get("content")) is str and
         type(obj.get("sha")) is str and HEX.fullmatch(obj["sha"]) is not None
         and type(obj.get("size")) is int and 0 < obj["size"] <= LIMIT,
         "NATIVE_CONTENT_SHAPE_INVALID")
    try:
        raw = base64.b64decode(
            "".join(obj["content"].split()).encode("ascii"), validate=True
        )
    except (UnicodeError, binascii.Error) as exc:
        raise BlockedPrecondition("NATIVE_CONTENT_ENCODING_INVALID") from exc
    need(len(raw) == obj["size"] and blob_sha(raw) == obj["sha"],
         "NATIVE_CONTENT_BLOB_MISMATCH")
    if expected_sha:
        need(obj["sha"] == expected_sha, "NATIVE_CONTENT_NOT_FROZEN_BLOB")
    return raw, obj["sha"]


def request_json(payload):
    need(len(payload) <= 20000, "CONTROL_REQUEST_TOO_LARGE")
    try:
        text = payload.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise BlockedPrecondition("CONTROL_REQUEST_ENCODING_INVALID") from exc
    triple = chr(96) * 3
    first, last = "\n" + triple + "json\n", "\n" + triple + "\n"
    need(text.count(first) == 1 and text.count(last) == 1,
         "CONTROL_MANIFEST_FRAMING_INVALID")
    a = text.index(first) + len(first)
    b = text.index(last, a)
    obj = parse_json(text[a:b].encode("utf-8"))
    need(set(obj) == REQUEST_FIELDS and
         obj["version"] == REQUEST_VERSION and obj["scope"] == "NONPRODUCT",
         "CONTROL_MANIFEST_INVALID")
    need(type(obj["qualification_attempt"]) is str and
         ATTEMPT.fullmatch(obj["qualification_attempt"]) is not None,
         "QUALIFICATION_ATTEMPT_INVALID")
    for key in ("source_parent_commit", "source_parent_tree",
                "workflow_blob"):
        need(type(obj[key]) is str and HEX.fullmatch(obj[key]) is not None,
             "QUALIFICATION_GIT_ID_INVALID")
    need(safe_path(obj["workflow_path"]) and
         obj["workflow_path"].startswith(".github/workflows/") and
         safe_path(obj["marker_path"]) and
         obj["marker_path"].startswith(".github/ts-ee-original-dispatch/"),
         "QUALIFICATION_PATH_INVALID")
    target = obj["target"]
    need(type(target) is dict and set(target) == TARGET_FIELDS,
         "TARGET_FIELDS_INVALID")
    need(target["repository"] == REPO and
         type(target["ref"]) is str and REF.fullmatch(target["ref"]) is not None,
         "TARGET_REPO_OR_REF_INVALID")
    for key in ("head_sha", "head_tree", "source_parent_commit",
                "source_parent_tree", "workflow_blob", "marker_blob",
                "control_request_blob"):
        need(type(target[key]) is str and HEX.fullmatch(target[key]) is not None,
             "TARGET_GIT_ID_INVALID")
    need(type(target["run_id"]) is int and target["run_id"] > 0 and
         type(target["execution_attempt"]) is str and
         ATTEMPT.fullmatch(target["execution_attempt"]) is not None and
         safe_path(target["marker_path"]) and
         target["marker_path"].startswith(".github/ts-ee-original-dispatch/") and
         safe_path(target["workflow_path"]) and
         target["workflow_path"].startswith(".github/workflows/") and
         type(target["control_request"]) is str and
         CONTROL.fullmatch(target["control_request"]) is not None,
         "TARGET_IDENTITY_OR_PATH_INVALID")
    return obj


def git_tree(fetch, sha):
    need(type(sha) is str and HEX.fullmatch(sha) is not None,
         "TREE_SHA_INVALID")
    obj, _ = get(fetch, f"/repos/{REPO}/git/trees/{sha}?recursive=1")
    need(obj.get("sha") == sha and obj.get("truncated") is False and
         type(obj.get("tree")) is list and len(obj["tree"]) <= 4000,
         "NATIVE_TREE_TRUNCATED")
    entries = {}
    for row in obj["tree"]:
        need(type(row) is dict and safe_path(row.get("path")) and
             type(row.get("sha")) is str and
             HEX.fullmatch(row["sha"]) is not None and
             type(row.get("mode")) is str and type(row.get("type")) is str,
             "NATIVE_TREE_ENTRY_INVALID")
        name = row["path"]
        need(name not in entries, "NATIVE_TREE_DUPLICATE_PATH")
        entries[name] = (row["mode"], row["type"], row["sha"])
    return entries


def exact_marker_delta(old, new, target):
    marker, workflow = target["marker_path"], target["workflow_path"]
    added, removed = set(new) - set(old), set(old) - set(new)
    modified = {x for x in old.keys() & new.keys() if old[x] != new[x]}
    need(added == {marker} and not removed and not modified,
         "NATIVE_GIT_DELTA_NOT_MARKER_ONLY")
    need(new[marker] == ("100644", "blob", target["marker_blob"]),
         "NATIVE_MARKER_BLOB_OR_MODE_INVALID")
    need(workflow in old and old[workflow] == new[workflow] and
         new[workflow] == ("100644", "blob", target["workflow_blob"]),
         "NATIVE_WORKFLOW_NOT_FROZEN")


def has_next(link, page, branch):
    need(type(link) is str and len(link) < 8192,
         "NATIVE_LINK_HEADER_INVALID")
    if not link:
        return False
    found = {}
    for chunk in link.split(","):
        m = re.fullmatch(
            r'\s*<([^>]+)>;\s*rel="(next|prev|first|last)"\s*', chunk
        )
        need(m is not None and m.group(2) not in found,
             "NATIVE_LINK_HEADER_AMBIGUOUS")
        found[m.group(2)] = m.group(1)
    if "next" not in found:
        return False
    p = urlparse(found["next"])
    args = parse_qs(p.query)
    need(p.scheme == "https" and p.netloc == "api.github.com" and
         p.path == f"/repos/{REPO}/actions/runs" and
         args.get("branch") == [branch] and
         args.get("per_page") == [str(PAGE)] and
         args.get("page") == [str(page + 1)],
         "NATIVE_NEXT_PAGE_NOT_CONTIGUOUS")
    return True


def all_branch_runs(fetch, branch):
    need(REF.fullmatch("refs/heads/" + branch) is not None,
         "NATIVE_BRANCH_INVALID")
    ids, total, first_ids, page = [], None, None, 1
    while True:
        need(page <= MAX_PAGES, "NATIVE_RUNS_PAGES_EXCEED_BOUND")
        path = (f"/repos/{REPO}/actions/runs?branch={quote(branch, safe='')}"
                f"&per_page={PAGE}&page={page}")
        data, header = get(fetch, path)
        count, runs = data.get("total_count"), data.get("workflow_runs")
        need(type(count) is int and 0 <= count <= PAGE * MAX_PAGES
             and type(runs) is list and len(runs) <= PAGE,
             "NATIVE_RUN_PAGE_SHAPE_INVALID")
        if total is None:
            total = count
        need(total == count, "NATIVE_RUN_PAGES_INCONSISTENT_TOTAL")
        page_ids = []
        for run in runs:
            need(type(run) is dict and type(run.get("id")) is int
                 and run["id"] > 0 and run.get("head_branch") == branch,
                 "NATIVE_RUN_PAGE_FOREIGN_ENTRY")
            page_ids.append(run["id"])
        need(len(set(page_ids)) == len(page_ids) and
             not set(page_ids) & set(ids),
             "NATIVE_RUN_PAGE_DUPLICATES")
        if page == 1:
            first_ids = page_ids
        ids.extend(page_ids)
        following = has_next(header.get("link", ""), page, branch)
        if following:
            need(len(page_ids) == PAGE and len(ids) < total,
                 "NATIVE_RUN_PAGE_INCONSISTENT_NEXT")
            page += 1
        else:
            need(len(ids) == total, "NATIVE_RUN_PAGE_INCOMPLETE")
            break
    first, _ = get(fetch, f"/repos/{REPO}/actions/runs?"
                   f"branch={quote(branch, safe='')}&per_page={PAGE}&page=1")
    need(first.get("total_count") == total and
         type(first.get("workflow_runs")) is list and
         [x.get("id") for x in first["workflow_runs"]] == first_ids,
         "NATIVE_RUN_LIST_CHANGED_DURING_READ")
    return ids


def acquire(fetch, req):
    target = req["target"]
    original = CONTROL.fullmatch(target["control_request"])
    need(original is not None, "ORIGINAL_REQUEST_REF_INVALID")
    prior_bytes, _ = file_bytes(
        fetch, TRANSPORT, original.group(2), original.group(1),
        target["control_request_blob"]
    )
    need(target["execution_attempt"].encode() in prior_bytes and
         target["source_parent_commit"].encode() in prior_bytes and
         target["workflow_blob"].encode() in prior_bytes,
         "ORIGINAL_CONTROL_REQUEST_SUBJECT_MISMATCH")
    marker, _ = file_bytes(fetch, REPO, target["marker_path"],
                           target["head_sha"], target["marker_blob"])
    obj = parse_json(marker)
    need(obj.get("version") == "TS-EE-ACTIONS-ORIGINAL-BINDING-v1"
         and len(obj) == 10, "NATIVE_MARKER_VERSION_INVALID")
    for key in ("execution_attempt", "repository", "ref", "source_parent_commit",
                "source_parent_tree", "workflow_path", "workflow_blob",
                "marker_path", "control_request"):
        need(obj.get(key) == target[key], "NATIVE_MARKER_SUBJECT_MISMATCH")
    workflow, _ = file_bytes(fetch, REPO, target["workflow_path"],
                             target["head_sha"], target["workflow_blob"])
    need(b"on:" in workflow, "NATIVE_WORKFLOW_CONTENT_INVALID")
    head, _ = get(fetch, f"/repos/{REPO}/git/commits/{target['head_sha']}")
    need(head.get("sha") == target["head_sha"] and
         head.get("tree", {}).get("sha") == target["head_tree"] and
         type(head.get("parents")) is list and len(head["parents"]) == 1 and
         head["parents"][0].get("sha") == target["source_parent_commit"],
         "NATIVE_COMMIT_PARENT_TREE_MISMATCH")
    parent, _ = get(fetch, f"/repos/{REPO}/git/commits/"
                    f"{target['source_parent_commit']}")
    need(parent.get("sha") == target["source_parent_commit"] and
         parent.get("tree", {}).get("sha") == target["source_parent_tree"],
         "NATIVE_PARENT_TREE_MISMATCH")
    left = git_tree(fetch, target["source_parent_tree"])
    right = git_tree(fetch, target["head_tree"])
    exact_marker_delta(left, right, target)
    run, _ = get(fetch, f"/repos/{REPO}/actions/runs/{target['run_id']}")
    branch = target["ref"].removeprefix("refs/heads/")
    need(run.get("id") == target["run_id"] and
         run.get("head_sha") == target["head_sha"] and
         run.get("head_branch") == branch and
         run.get("path") == target["workflow_path"] and
         run.get("event") == "push" and
         run.get("status") == "completed" and
         run.get("conclusion") == "success" and
         run.get("run_attempt") == 1 and
         run.get("repository", {}).get("full_name") == REPO,
         "NATIVE_PROVIDER_RUN_MISMATCH")
    ids = all_branch_runs(fetch, branch)
    need(ids == [target["run_id"]], "NATIVE_ORIGINAL_RUN_NOT_UNIQUE")
    return {
        "status": "TS_EE_GITHUB_NATIVE_EVIDENCE_PASS",
        "provider": "api.github.com",
        "target_run": target["run_id"],
        "head_sha": target["head_sha"],
        "head_tree": target["head_tree"],
        "parent_sha": target["source_parent_commit"],
        "parent_tree": target["source_parent_tree"],
        "marker_blob": target["marker_blob"],
        "workflow_blob": target["workflow_blob"],
        "prior_request_blob": target["control_request_blob"],
        "native_tree_entries_before": len(left),
        "native_tree_entries_after": len(right),
        "all_branch_run_ids": ids,
        "complete_tree_and_run_inventory": True,
        "no_native_write": True,
        "product_effect": "NONE",
        "physical_a02": "NO_GO",
    }


def qualify(fetch, control_ref, guard):
    match = CONTROL.fullmatch(control_ref)
    need(match is not None, "QUALIFICATION_REQUEST_REF_INVALID")
    data, sha = file_bytes(fetch, TRANSPORT, match.group(2), match.group(1))
    req = request_json(data)
    for key in ("source_parent_commit", "source_parent_tree",
                "workflow_blob"):
        need(guard.get(key) == req[key],
             "CURRENT_ORIGINAL_SOURCE_NOT_FROZEN")
    need(guard.get("execution_attempt") == req["qualification_attempt"] and
         guard.get("control_request") == control_ref and
         guard.get("effect") == "READ_ONLY_IDENTITY_PREFLIGHT" and
         guard.get("run_attempt") == 1 and
         guard.get("product_effect") == "NONE",
         "CURRENT_ORIGINAL_GUARD_INVALID")
    result = acquire(fetch, req)
    result.update({
        "qualification_attempt": req["qualification_attempt"],
        "qualification_request": control_ref,
        "qualification_request_blob": sha,
    })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-ref", required=True)
    parser.add_argument("--original-guard", type=Path, required=True)
    opts = parser.parse_args()
    try:
        need(opts.original_guard.is_file() and
             opts.original_guard.stat().st_size <= 8192,
             "ORIGINAL_GUARD_NOT_BOUNDED")
        guard = parse_json(opts.original_guard.read_bytes())
        result = qualify(GitHubRead(os.environ.get("TS_EE_GITHUB_READ_TOKEN")),
                         opts.request_ref, guard)
    except (BlockedPrecondition, OSError, KeyError, TypeError) as exc:
        message = str(exc) if type(exc) is BlockedPrecondition else "INVALID_EVIDENCE"
        if re.fullmatch(r"[A-Z0-9_]{3,96}", message) is None:
            message = "INVALID_EVIDENCE"
        print("TS_EE_NATIVE_BLOCKED_PRECONDITION_" + message, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
