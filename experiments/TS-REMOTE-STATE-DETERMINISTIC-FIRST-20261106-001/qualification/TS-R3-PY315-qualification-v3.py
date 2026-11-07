#!/usr/bin/env python3
"""TS Remote State 002: single-purpose, local-only, fail-closed Python 3.15 qualification.

VERSION 3. DATA UNTIL independently reviewed, materialized by normal Git/Orca
surfaces, pinned by Git blob and SHA256, and explicitly admitted for one attempt.
Does not connect to SQL, clone code, install dependencies, or alter Product.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import pwd
import stat
import subprocess
import sys
import time
import traceback

OPERATION = "TS-R3-PY315-NATIVE-QUALIFY-V3-20261107-001-A01"
SOURCE_COMMIT = "fd0a183bf815c3d26d6b0eef761334eec8aed01d"
SOURCE_TREE = "2d83f8159cb6ed8b02bdcb7b47c18285b319d482"
PREFIX = "experiments/TS-REMOTE-STATE-DETERMINISTIC-FIRST-20261106-001"
BASE = Path("/home/tsops/ts-remote-state-002/qualification-20261107-001")
SOURCE = BASE / "source"
RUNNER = BASE / "runner" / "TS-R3-PY315-qualification-v3.py"
RESULT = BASE / "result-v3-a01"
PYTHON = Path("/home/tsops/ts-remote-state-002/py315-deps-smoke-20261106-001/.venv/bin/python")
UV = Path("/home/tsops/.local/bin/uv")
GIT = Path("/usr/bin/git")
UV_EXPECTED_SHA256 = "db919fb9428cc8ad04377ba3c898e0ec5fbee83700da5b982b1c9539f1e1b34f"

# All files in the EXACT original Git source prefix. Every byte gets independently
# rechecked after copying, before any source code is executed.
MANIFEST = {
    ".python-version": (7, "861845e450f570a6e923d43052feb4773ecabb88"),
    "README.md": (3679, "7c5e8f31aa8a3315c984e6fe70df4e0b96938843"),
    "pyproject.toml": (164, "8ff5bb53f394b2e574c879fa38c231168bcb9891"),
    "tests/canonical-vectors.json": (1724, "feb017c42606f2e3220de5df822d57240be8c64c"),
    "tests/canonical-vectors.test.cjs": (1911, "0482d635315e19001a4d2ce70df2d2a852b07832"),
    "tests/test_canonical_vectors.py": (1586, "9f8a4d2fbe5cd5fe31cb120c26edf5392a0f277d"),
    "tests/test_cli_file.py": (3404, "0fe915d51ddf06e70fd9e9f6cfba4e0538ff47e9"),
    "tests/test_protocol.py": (22483, "474f2e65a4774908ca2a49fca643b4be37c00ab9"),
    "ts_detstate/__init__.py": (360, "4566b2562fbc77bcbbea087f53b9c7f4375afa01"),
    "ts_detstate/__main__.py": (2381, "d1399c957c02cb29410484982c6e83c7d71b6d14"),
    "ts_detstate/core.py": (20131, "2336e83fef3584119071796e68513926f9fa92b5"),
}
EXPECTED_MODULES = frozenset(("test_protocol", "test_cli_file", "test_canonical_vectors"))
INVENTORY_FILE = BASE / "runner" / "test-inventory-v1.txt"
INVENTORY_GIT_BLOB = "d560cbfdcf0f5a1d485b60bb8f24010c0bd66b64"
INVENTORY_BYTES = 3994


class Blocked(RuntimeError):
    pass


def check(condition: bool, code: str) -> None:
    if not condition:
        raise Blocked(code)


def is_trusted_dir(p: Path, owner: int) -> bool:
    try:
        st = os.lstat(p)
    except OSError:
        return False
    return (stat.S_ISDIR(st.st_mode) and st.st_uid == owner and
            not (st.st_mode & (stat.S_IWGRP | stat.S_IWOTH)))


def sha256_file(path: Path, max_size: int = 250_000_000) -> str:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        check(stat.S_ISREG(st.st_mode) and st.st_size <= max_size, "TOOL_NOT_REGULAR_OR_TOO_LARGE")
        h = hashlib.sha256()
        while chunk := os.read(fd, 65536):
            h.update(chunk)
        return h.hexdigest()
    finally:
        os.close(fd)


def blob_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data,
                        usedforsecurity=False).hexdigest()


def open_trusted_dir_at(parentfd: int, name: str, owner: int) -> int:
    check(name not in (".", "..", "") and "/" not in name, "INVALID_DIRECTORY_COMPONENT")
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                 dir_fd=parentfd)
    st = os.fstat(fd)
    if not (st.st_uid == owner and stat.S_ISDIR(st.st_mode)
            and not (st.st_mode & (stat.S_IWGRP | stat.S_IWOTH))):
        os.close(fd)
        raise Blocked("UNTRUSTED_DIRECTORY_FD")
    return fd


def open_beneath(basefd: int, components: tuple[str, ...], owner: int) -> int:
    current = os.dup(basefd)
    try:
        for component in components:
            following = open_trusted_dir_at(current, component, owner)
            os.close(current)
            current = following
        return current
    except BaseException:
        os.close(current)
        raise


def read_exact_fd(basefd: int, relative: str, size: int, owner: int) -> bytes:
    parts = tuple(relative.split("/"))
    check(parts and all(component not in (".", "..", "") for component in parts),
          "UNSAFE_RELATIVE_FILE")
    dirfd = open_beneath(basefd, parts[:-1], owner)
    try:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW |
                     os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=dirfd)
        try:
            st = os.fstat(fd)
            check(stat.S_ISREG(st.st_mode) and st.st_uid == owner, "SOURCE_FILE_OWNER_OR_TYPE")
            check(st.st_size == size, "SOURCE_FILE_SIZE")
            pieces = []
            remaining = size + 1
            while remaining:
                chunk = os.read(fd, min(remaining, 65536))
                if not chunk:
                    break
                pieces.append(chunk)
                remaining -= len(chunk)
            data = b"".join(pieces)
            check(len(data) == size, "SOURCE_FILE_CHANGED_OR_EXTRA")
            return data
        finally:
            os.close(fd)
    finally:
        os.close(dirfd)


def safe_env(home: Path) -> dict[str, str]:
    return {
        "HOME": str(home), "PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
        "UV_NO_CONFIG": "1", "UV_OFFLINE": "1", "UV_NO_PROGRESS": "1",
        "UV_CACHE_DIR": str(home / "uv-cache"),
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
    }


def run(args: list[str], *, cwd: Path | None = None, timeout: int = 20,
        env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, check=False, text=True,
                          encoding="utf-8", errors="replace", capture_output=True,
                          timeout=timeout)


def test_inventory(work: Path) -> list[str]:
    actual_ids: list[str] = []
    for module in sorted(EXPECTED_MODULES):
        path = work / "tests" / (module + ".py")
        tree = ast.parse(path.read_bytes(), filename=module)
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef) and any(
                    isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    for base in cls.bases):
                actual_ids.extend(module + "." + cls.name + "." + meth.name
                                  for meth in cls.body
                                  if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef))
                                  and meth.name.startswith("test_"))
    actual_ids.sort()
    check(len(actual_ids) == 57 and len(set(actual_ids)) == 57, "INVENTORY_NOT_EXACTLY_57")
    return actual_ids


# A trusted constant process, executed with Python -I; JSON results, not log greps.
TEST_WORKER = r'''
import contextlib,io,json,pathlib,sys,unittest
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root))
out=io.StringIO()
with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
    loader=unittest.TestLoader()
    suite=loader.discover(start_dir=str(root/'tests'), pattern='test_*.py')
    def flat(items):
        for item in items:
            if isinstance(item,unittest.TestSuite):
                yield from flat(item)
            else:
                yield item
    ids=sorted(t.id() for t in flat(suite))
    result=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
print(json.dumps({'ids':ids,'run':result.testsRun,'passed':result.wasSuccessful(),
                  'failures':len(result.failures),'errors':len(result.errors),
                  'skipped':len(result.skipped),'unexpected':len(result.unexpectedSuccesses),
                  'output':out.getvalue()[-8000:]},sort_keys=True))
sys.exit(0 if result.wasSuccessful() else 31)
'''


def materialize_exclusive(workfd: int, relative: str, data: bytes, owner: int) -> None:
    """No-follow openat chain; only fixed allowlisted leaf files, never cp -a."""
    pieces = PurePosixPath(relative).parts
    check(pieces and all(part not in (".", "..", "") for part in pieces), "INVALID_RELATIVE_PATH")
    folder_fd = os.dup(workfd)
    try:
        for component in pieces[:-1]:
            try:
                os.mkdir(component, mode=0o700, dir_fd=folder_fd)
            except FileExistsError:
                pass
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=folder_fd)
            meta = os.fstat(next_fd)
            check(meta.st_uid == owner and stat.S_ISDIR(meta.st_mode) and
                  not (meta.st_mode & (stat.S_IWGRP | stat.S_IWOTH)),
                  "DESTINATION_DIRECTORY_UNTRUSTED")
            os.close(folder_fd)
            folder_fd = next_fd
        name = pieces[-1]
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     mode=0o600, dir_fd=folder_fd)
        try:
            start = 0
            while start < len(data):
                start += os.write(fd, data[start:])
            os.fsync(fd)
        finally:
            os.close(fd)
        verify_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW,
                            dir_fd=folder_fd)
        try:
            st = os.fstat(verify_fd)
            check(stat.S_ISREG(st.st_mode) and st.st_uid == owner and
                  st.st_size == len(data), "COPIED_FILE_OWNER_OR_SIZE")
            verify_bytes = bytearray()
            while len(verify_bytes) <= len(data):
                chunk = os.read(verify_fd, min(65536, len(data) + 1 - len(verify_bytes)))
                if not chunk:
                    break
                verify_bytes.extend(chunk)
            check(bytes(verify_bytes) == data, "COPIED_FILE_BYTES_MISMATCH")
        finally:
            os.close(verify_fd)
        os.fsync(folder_fd)
    finally:
        os.close(folder_fd)


def atomic_receipt(dirfd: int, document: dict[str, object]) -> None:
    data = (json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
    fd = os.open(".receipt.json.tmp", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=dirfd)
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)
    os.link(".receipt.json.tmp", "receipt.json", src_dir_fd=dirfd, dst_dir_fd=dirfd,
            follow_symlinks=False)  # atomic CREATE_ONLY; EEXIST is terminal error
    os.unlink(".receipt.json.tmp", dir_fd=dirfd)
    verify_fd = os.open("receipt.json", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd)
    try:
        check(os.read(verify_fd, len(data) + 1) == data, "RECEIPT_POSTVERIFY_FAILED")
    finally:
        os.close(verify_fd)
    os.fsync(dirfd)


def preconditions() -> tuple[int, dict[str, str], int, int, int, int]:
    check(sys.version_info[:3] == (3, 15, 2), "NOT_PYTHON_3_15_2")
    check(pwd.getpwuid(os.getuid()).pw_name == "tsops", "WRONG_USER")
    check(sys.platform == "linux", "NOT_LINUX")
    owner = os.getuid()
    for p in (Path("/home/tsops"), Path("/home/tsops/ts-remote-state-002"), BASE,
              SOURCE, RUNNER.parent):
        check(is_trusted_dir(p, owner), "UNTRUSTED_ANCESTOR_" + p.name)
    check(os.path.realpath(RUNNER) == str(RUNNER) and not RUNNER.is_symlink(),
          "RUNNER_PATH_ALIAS")
    runner_meta = os.lstat(RUNNER)
    check(stat.S_ISREG(runner_meta.st_mode) and runner_meta.st_uid == owner
          and not (runner_meta.st_mode & (stat.S_IWGRP | stat.S_IWOTH)), "RUNNER_NOT_TRUSTED")
    check(not RESULT.exists() and not RESULT.is_symlink(), "RESULT_ALREADY_EXISTS")
    check(PYTHON.is_file() and os.access(PYTHON, os.X_OK) and
          UV.is_file() and os.access(UV, os.X_OK) and GIT.is_file(), "NATIVE_TOOLS_ABSENT")
    env = safe_env(BASE)
    py_v = run([str(PYTHON), "-I", "--version"], timeout=10, env=env)
    uv_v = run([str(UV), "--version"], timeout=10, env=env)
    check(py_v.returncode == 0 and py_v.stdout.strip() == "Python 3.15.2", "PYTHON_VERSION")
    check(uv_v.returncode == 0 and uv_v.stdout.strip() == "uv 0.13.1", "UV_VERSION")
    head = run([str(GIT), "-C", str(SOURCE), "rev-parse", "HEAD"], env=env)
    tree = run([str(GIT), "-C", str(SOURCE), "rev-parse", "HEAD^{tree}"], env=env)
    detached = run([str(GIT), "-C", str(SOURCE), "symbolic-ref", "-q", "HEAD"], env=env)
    check(head.returncode == 0 and head.stdout.strip() == SOURCE_COMMIT, "COMMIT_MISMATCH")
    check(tree.returncode == 0 and tree.stdout.strip() == SOURCE_TREE, "TREE_MISMATCH")
    check(detached.returncode == 1, "NOT_DETACHED_HEAD")
    prefixdir = SOURCE / PREFIX
    for p in (SOURCE / "experiments", prefixdir,
              prefixdir / "tests", prefixdir / "ts_detstate"):
        check(is_trusted_dir(p, owner), "UNTRUSTED_SOURCE_DIR")
    all_files: set[str] = set()
    for dirpath, dirname, filename in os.walk(prefixdir, topdown=True, followlinks=False):
        for name in dirname:
            check(is_trusted_dir(Path(dirpath) / name, owner), "UNTRUSTED_SUBDIRECTORY")
        for name in filename:
            all_files.add(str((Path(dirpath) / name).relative_to(prefixdir)))
    check(all_files == set(MANIFEST), "EXTRA_OR_MISSING_SOURCE_FILES")
    metadata = {
        "runner_sha256": sha256_file(RUNNER),
        "python_sha256": sha256_file(PYTHON.resolve()),
        "uv_sha256": sha256_file(UV.resolve()),
        "git_sha256": sha256_file(GIT.resolve()),
    }
    check(metadata["uv_sha256"] == UV_EXPECTED_SHA256, "UV_BINARY_HASH_MISMATCH")
    # Keep directory handles open through entire snapshot and process execution.
    homefd = os.open("/home/tsops", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        basefd = open_beneath(homefd, ("ts-remote-state-002", "qualification-20261107-001"), owner)
        sourcefd = open_trusted_dir_at(basefd, "source", owner)
        prefixfd = open_beneath(sourcefd, ("experiments", "TS-REMOTE-STATE-DETERMINISTIC-FIRST-20261106-001"), owner)
        runnerfd = open_trusted_dir_at(basefd, "runner", owner)
        return owner, metadata, basefd, sourcefd, prefixfd, runnerfd
    finally:
        os.close(homefd)


def main() -> int:
    try:
        owner, binaries, base_fd, source_fd, prefix_fd, runner_fd = preconditions()
    except Exception as e:
        print(json.dumps({"status": "BLOCKED_PRECONDITION", "code": str(e),
                          "effect": "NONE", "attempt": OPERATION}), file=sys.stderr)
        return 24

    # Exclusive root: if present, ANY previous attempt is terminal/unknown and cannot replay.
    try:
        os.mkdir("result-v3-a01", 0o700, dir_fd=base_fd)
        root_fd = open_trusted_dir_at(base_fd, "result-v3-a01", owner)
        check(os.stat(RESULT, follow_symlinks=False).st_ino == os.fstat(root_fd).st_ino,
              "RESULT_PATH_CHANGED")
    except (OSError, Blocked) as e:
        for fd_name in ("root_fd",):
            if fd_name in locals():
                os.close(locals()[fd_name])
        for fd in (prefix_fd, source_fd, runner_fd, base_fd):
            os.close(fd)
        print(json.dumps({"status": "BLOCKED_PRECONDITION", "code": str(e),
                          "effect": "NONE_OR_UNCERTAIN", "attempt": OPERATION}), file=sys.stderr)
        return 24

    receipt: dict[str, object] = {
        "schema": "ts-r3-py315-native-runner/v3", "attempt": OPERATION,
        "subject_commit": SOURCE_COMMIT, "subject_tree": SOURCE_TREE,
        "driver": "NOT_RUN", "tests": "NOT_RUN", "lock": "NOT_RUN",
        "status": "RUNNING", "effect": "LOCAL_DISPOSABLE_ONLY",
        "product": "NONE", "neon": "NONE", "binaries": binaries,
        "runner_path": str(RUNNER), "source_path": str(SOURCE),
        "result_path": str(RESULT), "uid": owner,
    }
    exit_code = 70
    try:
        work = RESULT / "work-tests"
        lockwork = RESULT / "work-lock"
        os.mkdir("work-tests", 0o700, dir_fd=root_fd)
        os.mkdir("work-lock", 0o700, dir_fd=root_fd)
        workfd = open_trusted_dir_at(root_fd, "work-tests", owner)
        lockfd = open_trusted_dir_at(root_fd, "work-lock", owner)
        try:
            # Copy ONLY original Git blobs from pinned source dir FD into isolated test tree.
            materialized: list[dict[str, object]] = []
            for relative, (size, expected_sha) in MANIFEST.items():
                data = read_exact_fd(prefix_fd, relative, size, owner)
                check(blob_hash(data) == expected_sha, "SOURCE_BLOB_HASH_MISMATCH_" + relative)
                materialize_exclusive(workfd, relative, data, owner)
                if relative in (".python-version", "pyproject.toml"):
                    # Lock resolution uses an entirely separate input workspace.
                    materialize_exclusive(lockfd, relative, data, owner)
                materialized.append({"file": relative, "bytes": size, "git_blob": expected_sha,
                                     "sha256": hashlib.sha256(data).hexdigest()})
            os.fsync(workfd)
            os.fsync(lockfd)
        finally:
            os.close(workfd)
            os.close(lockfd)
        receipt["copied_files"] = materialized

        # The independent test list is a separate Git-pinned runner manifest.
        inventory_data = read_exact_fd(runner_fd, "test-inventory-v1.txt", INVENTORY_BYTES, owner)
        check(blob_hash(inventory_data) == INVENTORY_GIT_BLOB, "INDEPENDENT_INVENTORY_HASH")
        externally_pinned_ids = inventory_data.decode("ascii").strip().split("\n")
        expected_ids = test_inventory(work)
        check(expected_ids == externally_pinned_ids, "INVENTORY_MISMATCH_INDEPENDENT_MANIFEST")
        ids_sha = hashlib.sha256(("\n".join(expected_ids) + "\n").encode()).hexdigest()
        receipt["test_inventory_sha256"] = ids_sha
        env = safe_env(RESULT)
        (RESULT / "uv-cache").mkdir(mode=0o700)
        driver = run([str(PYTHON), "-I", "-B", "-c",
                      "import psycopg,psycopg.pq; print(psycopg.__version__,psycopg.pq.__impl__)"] ,
                     cwd=work, timeout=15, env=env)
        receipt["driver"] = "PASS_IMPORT_ONLY" if driver.returncode == 0 and driver.stdout.strip() == "3.3.8 binary" else "FAILED_DRIVER_IMPORT"
        receipt["driver_exit"] = driver.returncode
        check(receipt["driver"] == "PASS_IMPORT_ONLY", "DRIVER_IMPORT_GATE")

        result = run([str(PYTHON), "-I", "-B", "-c", TEST_WORKER, str(work)],
                     cwd=work, timeout=60, env=env)
        try:
            report = json.loads(result.stdout)
        except (ValueError, TypeError):
            report = {"raw_tail": result.stdout[-500:]}
        receipt["test_report"] = report
        receipt["tests"] = "PASS_57_OF_57" if (
            result.returncode == 0 and report.get("ids") == expected_ids and
            report.get("run") == 57 and report.get("passed") is True and
            report.get("errors") == 0 and report.get("failures") == 0 and
            report.get("skipped") == 0 and report.get("unexpected") == 0) else "FAILED_OR_WRONG_INVENTORY"
        check(receipt["tests"] == "PASS_57_OF_57", "TEST_GATE")

        # No network, NO INSTALL; local cache is isolated to this attempt.
        # Never resolve from the mutable test execution tree; lock input is separate.
        lock = run([str(UV), "lock", "--offline", "--python", str(PYTHON)],
                   cwd=lockwork, timeout=60, env=env)
        receipt["lock_exit"] = lock.returncode
        receipt["lock_log_tail"] = (lock.stderr + lock.stdout)[-1000:]
        lockfile = lockwork / "uv.lock"
        if lock.returncode == 0 and lockfile.is_file() and not lockfile.is_symlink():
            receipt["lock"] = "PASS_OFFLINE_GENERATED"
            receipt["lock_sha256"] = sha256_file(lockfile, max_size=1_000_000)
        else:
            receipt["lock"] = "BLOCKED_OFFLINE_CACHE_OR_METADATA"
            raise Blocked("LOCK_OFFLINE_GATE")
        receipt["status"] = "PASS_PY315_TESTS_DRIVER_AND_OFFLINE_LOCK"
        exit_code = 0
    except subprocess.TimeoutExpired as e:
        receipt["status"] = "BLOCKED_TIMEOUT_NO_RETRY"
        receipt["error"] = str(e)[:180]
        exit_code = 33
    except Blocked as e:
        receipt["status"] = "PARTIAL_OR_BLOCKED_NO_RETRY"
        receipt["error"] = str(e)
        exit_code = 31
    except Exception as e:
        receipt["status"] = "FAILED_INTERNAL_NO_RETRY"
        receipt["error"] = type(e).__name__  # no DSN or driver traceback leaks
        exit_code = 32
    finally:
        receipt["process_exit"] = exit_code
        try:
            atomic_receipt(root_fd, receipt)
        except Exception as e:
            print("RECEIPT_WRITE_UNKNOWN: " + type(e).__name__, file=sys.stderr)
            exit_code = 41
        os.close(root_fd)
        os.close(prefix_fd)
        os.close(source_fd)
        os.close(runner_fd)
        os.close(base_fd)
    print(json.dumps({"attempt": OPERATION, "status": receipt["status"],
                      "receipt": str(RESULT / "receipt.json"), "process_exit": exit_code}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
