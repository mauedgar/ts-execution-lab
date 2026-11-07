#!/usr/bin/env bash
# TS R3 Python 3.15 qualification runner v1 — deterministic, NONPRODUCT, offline only.
# This file is DATA until externally admitted and its SHA-256 / Git blob are verified.
set -Eeuo pipefail
umask 077
export PATH=/usr/bin:/bin
export LC_ALL=C
export UV_NO_PROGRESS=1
export UV_NO_CONFIG=1

OP='TS-R3-PY315-NATIVE-QUALIFY-20261107-001-A01'
COMMIT='fd0a183bf815c3d26d6b0eef761334eec8aed01d'
TREE='2d83f8159cb6ed8b02bdcb7b47c18285b319d482'
PREFIX='experiments/TS-REMOTE-STATE-DETERMINISTIC-FIRST-20261106-001'
SOURCE='/home/tsops/ts-remote-state-002/qualification-20261107-001/source'
RESULT='/home/tsops/ts-remote-state-002/qualification-20261107-001/result-a01'
PY='/home/tsops/ts-remote-state-002/py315-deps-smoke-20261106-001/.venv/bin/python'
UV='/home/tsops/.local/bin/uv'

fail() { printf 'BLOCKED_PRECONDITION: %s\n' "$1" >&2; exit 24; }
[[ "$(id -un)" == 'tsops' ]] || fail 'USER_NOT_TSOPS'
[[ "$(uname -s)" == 'Linux' ]] || fail 'NOT_LINUX'
[[ -d "$SOURCE/.git" ]] || { [[ -f "$SOURCE/.git" ]] || fail 'SOURCE_GIT_MISSING'; }
[[ ! -L "$SOURCE" ]] || fail 'SOURCE_SYMLINK'
[[ ! -e "$RESULT" && ! -L "$RESULT" ]] || fail 'RESULT_PATH_EXISTS_NO_RETRY'
[[ -x "$PY" && -x "$UV" ]] || fail 'PYTHON_OR_UV_MISSING'
[[ "$($PY --version)" == 'Python 3.15.2' ]] || fail 'PYTHON_VERSION_MISMATCH'
[[ "$($UV --version)" == 'uv 0.13.1' ]] || fail 'UV_VERSION_MISMATCH'
[[ "$(git -C "$SOURCE" rev-parse HEAD)" == "$COMMIT" ]] || fail 'SOURCE_COMMIT_MISMATCH'
[[ "$(git -C "$SOURCE" rev-parse HEAD^{tree})" == "$TREE" ]] || fail 'SOURCE_TREE_MISMATCH'
[[ -z "$(git -C "$SOURCE" status --porcelain)" ]] || fail 'SOURCE_NOT_CLEAN'

# Pinned manifest from original Git tree. No source inspection, discovery or dynamic executable inputs.
while IFS=' ' read -r expected relative; do
    f="$SOURCE/$PREFIX/$relative"
    [[ -f "$f" && ! -L "$f" ]] || fail 'FILE_MISSING_OR_SYMLINK'
    actual="$(git -C "$SOURCE" hash-object --no-filters -- "$f")"
    [[ "$actual" == "$expected" ]] || fail 'FILE_BLOB_MISMATCH'
done <<'MANIFEST'
861845e450f570a6e923d43052feb4773ecabb88 .python-version
7c5e8f31aa8a3315c984e6fe70df4e0b96938843 README.md
8ff5bb53f394b2e574c879fa38c231168bcb9891 pyproject.toml
feb017c42606f2e3220de5df822d57240be8c64c tests/canonical-vectors.json
0482d635315e19001a4d2ce70df2d2a852b07832 tests/canonical-vectors.test.cjs
9f8a4d2fbe5cd5fe31cb120c26edf5392a0f277d tests/test_canonical_vectors.py
0fe915d51ddf06e70fd9e9f6cfba4e0538ff47e9 tests/test_cli_file.py
474f2e65a4774908ca2a49fca643b4be37c00ab9 tests/test_protocol.py
4566b2562fbc77bcbbea087f53b9c7f4375afa01 ts_detstate/__init__.py
d1399c957c02cb29410484982c6e83c7d71b6d14 ts_detstate/__main__.py
2336e83fef3584119071796e68513926f9fa92b5 ts_detstate/core.py
MANIFEST

mkdir -m 0700 -- "$RESULT" || fail 'RESULT_CREATE_FAILED'
DRIVER_STATUS='NOT_RUN'
DRIVER_EXIT=99
TEST_STATUS='NOT_RUN'
LOCK_STATUS='NOT_RUN'
TEST_EXIT=99
LOCK_EXIT=99
PY_VERSION='Python 3.15.2'
LOCK_SHA256='NONE'

finish() {
    code=$?
    trap - EXIT
    {
        printf 'operation_id=%s\n' "$OP"
        printf 'source_commit=%s\nsource_tree=%s\n' "$COMMIT" "$TREE"
        printf 'python_version=%s\n' "$PY_VERSION"
        printf 'driver_status=%s\ndriver_exit=%s\n' "$DRIVER_STATUS" "$DRIVER_EXIT"
        printf 'test_status=%s\ntest_exit=%s\n' "$TEST_STATUS" "$TEST_EXIT"
        printf 'lock_status=%s\nlock_exit=%s\nlock_sha256=%s\n' "$LOCK_STATUS" "$LOCK_EXIT" "$LOCK_SHA256"
        printf 'process_exit=%s\n' "$code"
        printf 'effect=LOCAL_DISPOSABLE_FILES_ONLY\nproduct=NONE\nneon=NONE\n'
    } > "$RESULT/receipt.txt.tmp"
    mv -n -- "$RESULT/receipt.txt.tmp" "$RESULT/receipt.txt" || true
    exit "$code"
}
trap finish EXIT

DRIVER_STATUS='RUNNING_READONLY_IMPORT'
"$PY" -c 'import psycopg,psycopg.pq; print(psycopg.__version__,psycopg.pq.__impl__); assert psycopg.__version__=="3.3.8" and psycopg.pq.__impl__=="binary"' > "$RESULT/driver-probe.log" 2>&1 || DRIVER_EXIT=$?
if [[ "$DRIVER_EXIT" == 99 ]]; then DRIVER_EXIT=0; fi
if [[ "$DRIVER_EXIT" -eq 0 ]] && grep -qx '3.3.8 binary' "$RESULT/driver-probe.log"; then
    DRIVER_STATUS='PASS_3_3_8_BINARY'
else
    DRIVER_STATUS='FAILED_OR_UNQUALIFIED'
fi

mkdir -m 0700 -- "$RESULT/work"
cp -a -- "$SOURCE/$PREFIX/." "$RESULT/work/"
TEST_STATUS='RUNNING'
(
    cd "$RESULT/work"
    PYTHONPATH=. "$PY" -B -m unittest discover -s tests -v
) > "$RESULT/python315-unittest.log" 2>&1 || TEST_EXIT=$?
if [[ "$TEST_EXIT" == 99 ]]; then TEST_EXIT=0; fi
if [[ "$TEST_EXIT" -eq 0 ]] && grep -q '^Ran 57 tests in ' "$RESULT/python315-unittest.log" && grep -q '^OK$' "$RESULT/python315-unittest.log"; then
    TEST_STATUS='PASS_57_OF_57'
else
    TEST_STATUS='FAILED_OR_INCOMPLETE'
    exit 25
fi

LOCK_STATUS='RUNNING_OFFLINE'
(
    cd "$RESULT/work"
    "$UV" lock --offline --python "$PY"
) > "$RESULT/uv-lock-offline.log" 2>&1 || LOCK_EXIT=$?
if [[ "$LOCK_EXIT" == 99 ]]; then LOCK_EXIT=0; fi
if [[ "$LOCK_EXIT" -eq 0 && -f "$RESULT/work/uv.lock" && ! -L "$RESULT/work/uv.lock" ]]; then
    LOCK_STATUS='PASS_OFFLINE'
    LOCK_SHA256="$(sha256sum "$RESULT/work/uv.lock" | cut -d ' ' -f 1)"
else
    LOCK_STATUS='BLOCKED_OFFLINE_CACHE_OR_METADATA'
fi
exit 0
