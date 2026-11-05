#!/usr/bin/env bash
# TS Execution Engineering only. Synthetic local R2 crash window proof (system Python image v2).
# Execution/result only via Commander; no Product state or consumer access.
set -Eeuo pipefail
if [[ $# -ne 5 ]]; then
  echo 'BLOCKED_PRECONDITION|usage: runner <lab_repo> <source_script> <attempt_root> <attempt_id> <uv_image_digest>' >&2
  exit 2
fi
LAB=$1; SCRIPT=$2; RESULT_ROOT=$3; ATTEMPT_ID=$4; UV_IMAGE=$5
LAB_SHA=76814d5fa5c2bd5f2a19887823d5881cafd81c77
PRODUCT_SHA=35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84
SOURCE_SHA256=7a995c2f8f674a4bc3539f422c5a2cad5d3b015af46275772ac65d8031038aa7
LOCK_BLOB=a1d60169652e96106d6669bc2c0700c008f2b8a0
PYPROJECT_BLOB=122f8a2b4b5f5bd3ccbe673736f8599d7ca68062
PG_IMAGE=postgres@sha256:5db6dac2ef5dcff512f4f00a009c3c332b9f2f28f24277175bf3e4a3d02ef83a
PREFIX=experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001
if ! [[ "$ATTEMPT_ID" =~ ^[a-zA-Z0-9_-]{1,60}$ && "$RESULT_ROOT" = /* && "$UV_IMAGE" =~ ^ghcr.io/astral-sh/uv@sha256:[0-9a-f]{64}$ ]]; then
  echo 'BLOCKED_PRECONDITION|bad_arguments' >&2; exit 2
fi
for c in git docker awk tar mktemp sha256sum; do command -v "$c" >/dev/null || { echo "BLOCKED_PRECONDITION|missing_$c";exit 2; }; done
[[ "$(sha256sum "$SCRIPT" | awk '{print $1}')" = "$SOURCE_SHA256" ]] || { echo 'BLOCKED_PRECONDITION|source_sha256';exit 2; }
[[ "$(git -C "$LAB" cat-file -t "$LAB_SHA")" = commit ]] || { echo 'BLOCKED_PRECONDITION|lab_commit';exit 2; }
[[ "$(git -C "$LAB" rev-parse "$LAB_SHA:$PREFIX/r2-python/uv.lock")" = "$LOCK_BLOB" ]] || { echo 'BLOCKED_PRECONDITION|lock_blob';exit 2; }
[[ "$(git -C "$LAB" rev-parse "$LAB_SHA:$PREFIX/r2-python/pyproject.toml")" = "$PYPROJECT_BLOB" ]] || { echo 'BLOCKED_PRECONDITION|project_blob';exit 2; }
[[ "$(docker info --format '{{.OSType}}')" = linux ]] || { echo 'BLOCKED_PRECONDITION|docker_linux';exit 2; }
docker image inspect "$PG_IMAGE" >/dev/null || { echo 'BLOCKED_PRECONDITION|postgres_image';exit 2; }
docker image inspect "$UV_IMAGE" >/dev/null || { echo 'BLOCKED_PRECONDITION|uv_image';exit 2; }
mkdir -p "$RESULT_ROOT"
DIR="$RESULT_ROOT/$ATTEMPT_ID"
mkdir "$DIR" 2>/dev/null || { echo 'BLOCKED_PRECONDITION|attempt_identity_already_exists';exit 2; }
TMP='';PG_ID='';RESULT=UNKNOWN
cleanup(){
  status=$?
  trap - EXIT
  error=0
  if [[ -n "$PG_ID" ]]; then docker rm -f "$PG_ID" >/dev/null 2>&1 || error=1; fi
  if [[ -n "$TMP" && -d "$TMP" ]]; then rm -rf -- "$TMP" || error=1; fi
  if [[ "$status" = 0 && "$error" = 0 && -f "$DIR/test_pass.pending" ]]; then
    if mv "$DIR/test_pass.pending" "$DIR/terminal.txt"; then cat "$DIR/terminal.txt";exit 0;fi
  fi
  printf 'FAILED|R2_IR002_LOCAL|attempt=%s|test_exit=%s|cleanup_failed=%s\n' "$ATTEMPT_ID" "$status" "$error" > "$DIR/terminal.txt"
  exit 1
}
trap cleanup EXIT
printf 'ATTEMPT_STARTED|subject=%s|id=%s\n' "$LAB_SHA" "$ATTEMPT_ID" > "$DIR/started.txt"
TMP=$(mktemp -d)
mkdir -p "$TMP/lab"
git -C "$LAB" archive "$LAB_SHA" | tar -xf - -C "$TMP/lab"
cp -- "$SCRIPT" "$TMP/lab/$PREFIX/dbos_effect_recovery_r2_ir002.py"
PG_NAME="tsremote-r2-$ATTEMPT_ID"
if docker container inspect "$PG_NAME" >/dev/null 2>&1; then
  echo 'BLOCKED_PRECONDITION|container_name_taken' >&2;exit 2
fi
PG_ID=$(docker run -d --name "$PG_NAME" --env POSTGRES_USER=postgres --env POSTGRES_PASSWORD=synthetic_ci_only --env POSTGRES_DB=postgres "$PG_IMAGE")
if ! [[ "$PG_ID" =~ ^[0-9a-f]{64}$ ]]; then PG_ID=''; echo 'UNKNOWN|postgres_container_identity';exit 1;fi
printf '%s\n' "$PG_ID" > "$DIR/postgres-id.txt"
ready=0
for n in $(seq 1 50); do if docker exec "$PG_ID" pg_isready -U postgres -d postgres >/dev/null 2>&1; then ready=1;break;fi;sleep 1;done
[[ "$ready" = 1 ]] || { echo 'BLOCKED_PRECONDITION|postgres_not_ready';exit 2; }
WORK="$TMP/lab/$PREFIX"
# Prepare exact locked Python 3.15.2 dependencies on isolated temporary filesystem.
docker run --rm --network "container:$PG_ID" --user "$(id -u):$(id -g)" --mount "type=bind,src=$TMP,dst=/workspace" --env HOME=/tmp --env UV_CACHE_DIR=/tmp/uv-cache --env UV_LINK_MODE=copy --workdir "/workspace/lab/$PREFIX/r2-python" "$UV_IMAGE" sh -ec 'test -x /usr/local/bin/python && python --version && uv sync --locked --python /usr/local/bin/python && .venv/bin/python --version && .venv/bin/python -c "import dbos, psycopg"' > "$DIR/dependencies.log" 2>&1
# Each phase is a distinct container process, with the same synthetic PostgreSQL instance.
run_phase(){
  phase=$1;workflow=$2;crash=${3:-0}
  docker run --rm --network "container:$PG_ID" --user "$(id -u):$(id -g)" --mount "type=bind,src=$TMP,dst=/workspace" --env HOME=/tmp --env UV_CACHE_DIR=/tmp/uv-cache --env TS_REMOTE_WORKFLOW_ID="$workflow" --env DBOS_SYSTEM_DATABASE_URL='postgresql://postgres:synthetic_ci_only@127.0.0.1:5432/postgres' --env TS_REMOTE_R2_CRASH_AFTER_EFFECT_COMMIT="$crash" --workdir "/workspace/lab/$PREFIX" "$UV_IMAGE" "r2-python/.venv/bin/python" dbos_effect_recovery_r2_ir002.py "$phase"
}
BASE="ts-remote-r2-ir002-$ATTEMPT_ID-normal"
FAULT="ts-remote-r2-ir002-$ATTEMPT_ID-crash"
run_phase first "$BASE" > "$DIR/first.log" 2>&1
run_phase second "$BASE" > "$DIR/second.log" 2>&1
set +e
run_phase crash "$FAULT" 1 > "$DIR/crash.log" 2>&1
CRASH_CODE=$?
set -e
printf '%s\n' "$CRASH_CODE" > "$DIR/crash_exit.txt"
if [[ "$CRASH_CODE" -ne 73 ]]; then echo "FAIL|injection_expected_exit_73|actual=$CRASH_CODE" >&2;exit 1;fi
run_phase recover "$FAULT" > "$DIR/recover.log" 2>&1
run_phase negative "$FAULT" > "$DIR/negative.log" 2>&1
run_phase concurrent "$FAULT" > "$DIR/concurrent.log" 2>&1
for spec in 'first|phase=first' 'second|phase=second' 'recover|phase=recover' 'negative|payload_revision_authority=rejected' 'concurrent|effects=1'; do
 name=${spec%%|*};marker=${spec#*|};grep -Fq "$marker" "$DIR/$name.log" || { echo "FAIL|missing_marker|$name|$marker" >&2;exit 1; }
done
printf 'PASS|R2_IR002_LOCAL|attempt=%s|lab=%s|product=%s|source_sha256=%s|uv_image=%s|postgres_image=%s|crash_exit=73|test=PASS|cleanup=pending\n' "$ATTEMPT_ID" "$LAB_SHA" "$PRODUCT_SHA" "$SOURCE_SHA256" "$UV_IMAGE" "$PG_IMAGE" > "$DIR/test_pass.pending"
printf 'R2_TESTS_FINISHED|await_cleanup|attempt=%s\n' "$ATTEMPT_ID"
