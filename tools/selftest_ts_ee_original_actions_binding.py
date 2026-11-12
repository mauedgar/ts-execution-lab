"""Synthetic stdlib negative tests for nonProduct original Git transition guard.

Creates only disposable local Git repos inside Python TemporaryDirectory.
It never uses a Product repo, remote credential, network, or GitHub run.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

import ts_ee_original_actions_binding as guard

from ts_ee_original_actions_binding import (
    VERSION, BlockedPrecondition, validate,
)

ATTEMPT = "TS-EE-ACTIONS-IDENTITY-QUAL-20261111-001-A001"
REF = "refs/heads/ee/ts-ee-actions-original-binding-20261111-001"
REPO = "mauedgar/ts-execution-lab"
WORKFLOW = ".github/workflows/ts-ee-original-binding-qual-20261111-001.yml"
MARKER = ".github/ts-ee-original-dispatch/" + ATTEMPT + ".json"
REQUEST = ("mauedgar/ts-execution-transport@" + ("a" * 40) +
           ":requests/TS-EE-ACTIONS-IDENTITY-QUAL-20261111-001/REQUEST.md")


def git(root: Path, *argv: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *argv],
                                   stderr=subprocess.DEVNULL).decode().strip()


def fixture():
    parent = tempfile.TemporaryDirectory(prefix="ts-ee-original-identity-")
    root = Path(parent.name) / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "synthetic@example.invalid")
    git(root, "config", "user.name", "Synthetic EE Test")
    wf = root / WORKFLOW
    wf.parent.mkdir(parents=True)
    wf.write_text("name: identity unit test\non: push\n", encoding="utf-8")
    (root / "README.md").write_text("NONPRODUCT synthetic fixture\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-qm", "source parent frozen")
    source_sha = git(root, "rev-parse", "HEAD")
    source_tree = git(root, "rev-parse", "HEAD^{tree}")
    wf_blob = git(root, "rev-parse", f"HEAD:{WORKFLOW}")
    info = {
        "version": VERSION,
        "execution_attempt": ATTEMPT,
        "repository": REPO,
        "ref": REF,
        "source_parent_commit": source_sha,
        "source_parent_tree": source_tree,
        "workflow_path": WORKFLOW,
        "workflow_blob": wf_blob,
        "marker_path": MARKER,
        "control_request": REQUEST,
    }
    marker = root / MARKER
    marker.parent.mkdir(parents=True)
    marker.write_text(json.dumps(info, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", MARKER)
    git(root, "commit", "-qm", "one original marker commit")
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "123456",
        "GITHUB_REPOSITORY": REPO,
        "GITHUB_REF": REF,
        "GITHUB_SHA": git(root, "rev-parse", "HEAD"),
    }
    return parent, root, info, env


def rejection(label: str, work) -> None:
    tmp, root, info, env = fixture()
    try:
        work(root, info, env)
        try:
            validate(root, MARKER, ATTEMPT, env)
        except BlockedPrecondition:
            print("NEGATIVE_PASS_" + label)
        else:
            raise AssertionError("FALSE_ACCEPT_" + label)
    finally:
        tmp.cleanup()


def hardening_checks() -> None:
    """Deterministic fail-closed tests, never an external GitHub/host action."""
    tmp, root, info, env = fixture()
    try:
        # Git's inherited config/alias/executable/prompt/tracing knobs are
        # ignored regardless of the caller process environment.
        with patch.dict(os.environ, {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.fsmonitor",
            "GIT_CONFIG_VALUE_0": "malicious-command",
            "GIT_EXEC_PATH": "/nonexistent/evil",
            "GIT_TRACE": "/tmp/ts-ee-untrusted-trace",
            "GIT_OPTIONAL_LOCKS": "1",
        }):
            safe = guard._git_env()
            assert not any(k in safe for k in (
                "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0",
                "GIT_CONFIG_VALUE_0", "GIT_EXEC_PATH", "GIT_TRACE",
            ))
            assert safe["GIT_CONFIG_NOSYSTEM"] == "1"
            assert safe["GIT_TERMINAL_PROMPT"] == "0"
            assert validate(root, MARKER, ATTEMPT, env)[
                "status"] == "TS_EE_ORIGINAL_GIT_TRANSITION_PASS"
        print("HARDENING_PASS_INHERITED_GIT_ENV_STRIPPED")

        giant = root / "oversize.txt"
        giant.write_bytes(b"X" * (guard.MAX_MARKER_BYTES + 8192))
        git(root, "add", "oversize.txt")
        git(root, "commit", "-qm", "oversize synthetic read object")
        try:
            guard.git_bytes(root, "show", "HEAD:oversize.txt")
        except BlockedPrecondition as exc:
            assert str(exc) == "GIT_STDOUT_LIMIT_EXCEEDED"
        else:
            raise AssertionError("FALSE_ACCEPT_OVERSIZED_MARKER")
        print("NEGATIVE_PASS_REAL_GIT_OVERSIZED_OBJECT_BOUNDED")

        original_popen = subprocess.Popen

        def expect_program(label, command, expected, *, timeout=None):
            def launch(_argv, **kwargs):
                assert kwargs["shell"] is False
                assert kwargs["start_new_session"] is True
                assert kwargs["stdin"] == subprocess.DEVNULL
                assert kwargs["env"]["GIT_CONFIG_NOSYSTEM"] == "1"
                assert "GIT_CONFIG_COUNT" not in kwargs["env"]
                return original_popen(
                    [sys.executable, "-B", "-c", command], **kwargs
                )
            with patch.object(guard.subprocess, "Popen", side_effect=launch):
                if timeout is not None:
                    with patch.object(guard, "GIT_DEADLINE_SECONDS", timeout):
                        try:
                            guard.git(root, "rev-parse", "HEAD")
                        except BlockedPrecondition as exc:
                            assert str(exc) == expected, (label, str(exc))
                        else:
                            raise AssertionError("FALSE_ACCEPT_" + label)
                else:
                    try:
                        guard.git(root, "rev-parse", "HEAD")
                    except BlockedPrecondition as exc:
                        assert str(exc) == expected, (label, str(exc))
                    else:
                        raise AssertionError("FALSE_ACCEPT_" + label)
            print("NEGATIVE_PASS_" + label + "_" + expected)

        expect_program(
            "OVERSIZED_STDOUT",
            "import sys;sys.stdout.write('X'*70000)",
            "GIT_STDOUT_LIMIT_EXCEEDED",
        )
        expect_program(
            "OVERSIZED_STDERR",
            "import sys;sys.stderr.write('Y'*25000)",
            "GIT_STDERR_LIMIT_EXCEEDED",
        )
        expect_program(
            "NONZERO_CHILD_STATUS",
            "import sys;sys.exit(7)",
            "GIT_IDENTITY_READ_FAILED",
        )
        expect_program(
            "NON_UTF8_CHILD_OUTPUT",
            "import sys;sys.stdout.buffer.write(bytes([255]))",
            "NON_UTF8_GIT_RESPONSE",
        )
        expect_program(
            "CHILD_PROCESS_TIMEOUT",
            "import time;time.sleep(2)",
            "GIT_DEADLINE_EXCEEDED",
            timeout=0.10,
        )

        with patch.object(guard, "GIT_BINARY", "/no/such/trusted/git"):
            try:
                guard.git(root, "rev-parse", "HEAD")
            except BlockedPrecondition as exc:
                assert str(exc) == "TRUSTED_GIT_NOT_FOUND"
            else:
                raise AssertionError("FALSE_ACCEPT_UNTRUSTED_BINARY")
        print("NEGATIVE_PASS_TRUSTED_GIT_BINARY_UNAVAILABLE")
    finally:
        tmp.cleanup()


def main() -> None:
    tmp, root, info, env = fixture()
    try:
        result = validate(root, MARKER, ATTEMPT, env)
        assert result["status"] == "TS_EE_ORIGINAL_GIT_TRANSITION_PASS"
        assert result["source_parent_commit"] == info["source_parent_commit"]
        assert result["source_parent_tree"] == info["source_parent_tree"]
        assert result["workflow_blob"] == info["workflow_blob"]
        assert result["run_id"] == "123456"
        print("SYNTHETIC_POSITIVE_PASS")
    finally:
        tmp.cleanup()

    rejection("SECOND_ATTEMPT", lambda r, i, e: e.update(GITHUB_RUN_ATTEMPT="2"))
    rejection("WRONG_HEAD", lambda r, i, e: e.update(GITHUB_SHA="0" * 40))
    rejection("WRONG_REPO", lambda r, i, e: e.update(GITHUB_REPOSITORY="foreign/repo"))
    rejection("WRONG_BRANCH", lambda r, i, e: e.update(GITHUB_REF="refs/heads/main"))
    rejection("MISSING_RUN_ID", lambda r, i, e: e.update(GITHUB_RUN_ID=""))

    def extra_delta(root, info, env):
        (root / "unexpected.txt").write_text("rogue\n", encoding="utf-8")
        git(root, "add", "unexpected.txt")
        git(root, "commit", "-qm", "unauthorized second commit")
        env["GITHUB_SHA"] = git(root, "rev-parse", "HEAD")
    rejection("NEW_COMMIT_NOT_FROZEN_PARENT", extra_delta)

    def alter_marker(root, info, env):
        marker = root / MARKER
        info["workflow_blob"] = "0" * 40
        marker.write_text(json.dumps(info, sort_keys=True) + "\n",
                          encoding="utf-8")
        git(root, "add", MARKER)
        git(root, "commit", "--amend", "--no-edit", "-q")
        env["GITHUB_SHA"] = git(root, "rev-parse", "HEAD")
    rejection("BAD_WORKFLOW_BLOB", alter_marker)

    def extra_path_same_commit(root, info, env):
        (root / "rogue.txt").write_text("NOT AUTHORISED\n", encoding="utf-8")
        git(root, "add", "rogue.txt")
        git(root, "commit", "--amend", "--no-edit", "-q")
        env["GITHUB_SHA"] = git(root, "rev-parse", "HEAD")
    rejection("EXTRA_DISPATCH_PATH", extra_path_same_commit)

    def wrong_parent(root, info, env):
        info["source_parent_commit"] = "0" * 40
        marker = root / MARKER
        marker.write_text(json.dumps(info, sort_keys=True) + "\n",
                          encoding="utf-8")
        git(root, "add", MARKER)
        git(root, "commit", "--amend", "--no-edit", "-q")
        env["GITHUB_SHA"] = git(root, "rev-parse", "HEAD")
    rejection("WRONG_FROZEN_PARENT", wrong_parent)

    hardening_checks()
    print("TS_EE_ACTIONS_IDENTITY_A03_HARDENED_1_POSITIVE_9_BASE_NEGATIVE_7_HARDENING_PASS")


if __name__ == "__main__":
    main()
