#!/usr/bin/env bash
# TS Execution Engineering, NONPRODUCT. One-shot R1 qualification from immutable Git objects.
# No worktree/HEAD edits; only disposable Git archives. This is NOT workflow publication.
set -Eeuo pipefail

EXPECTED_PRODUCT='35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84'
EXPECTED_PRODUCT_TREE='25d1a151d651bb41936c69334fb0b0772ef22519'
EXPECTED_R1_BLOB='5b5f45279396255f3511800251e3f87819dff8f5'
R1_PATH='experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r1_a001_ir004_strict_json.cjs'

if [ "$#" -ne 5 ]; then
  echo 'BLOCKED_PRECONDITION|usage: bash r1-docker-once.sh <lab-repo> <product-repo> <expected-lab-SHA> <absolute-results-dir> <unique-attempt-id>' >&2
  exit 2
fi

LAB="$1"; PRODUCT="$2"; LAB_SHA="$3"; RESULT_ROOT="$4"; ATTEMPT_ID="$5"
if ! [[ "$LAB_SHA" =~ ^[0-9a-f]{40}$ && "$ATTEMPT_ID" =~ ^[A-Za-z0-9_-]{1,50}$ ]]; then
  echo 'BLOCKED_PRECONDITION|invalid-lab-sha-or-attempt-id' >&2
  exit 2
fi
if ! [[ "$RESULT_ROOT" = /* ]]; then
  echo 'BLOCKED_PRECONDITION|absolute-result-path-required' >&2
  exit 2
fi
for bin in git docker tar mktemp awk; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "BLOCKED_PRECONDITION|missing-$bin" >&2
    exit 2
  fi
done
if ! docker info >/dev/null 2>&1; then
  echo 'BLOCKED_PRECONDITION|docker-daemon-unavailable' >&2
  exit 2
fi
if [ "$(docker info --format '{{.OSType}}')" != linux ]; then
  echo 'BLOCKED_PRECONDITION|docker-linux-containers-required' >&2
  exit 2
fi

LAB="$(cd "$LAB" && pwd -P)"
PRODUCT="$(cd "$PRODUCT" && pwd -P)"
# Verify complete immutable Git objects without changing either working tree/HEAD.
LAB_OBJECT_TYPE="$(git -C "$LAB" cat-file -t "$LAB_SHA")"
PRODUCT_OBJECT_TYPE="$(git -C "$PRODUCT" cat-file -t "$EXPECTED_PRODUCT")"
PRODUCT_TREE="$(git -C "$PRODUCT" rev-parse "$EXPECTED_PRODUCT^{tree}")"
R1_BLOB="$(git -C "$LAB" rev-parse "$LAB_SHA:$R1_PATH")"
PRODUCT_ACTUAL="$EXPECTED_PRODUCT"
if [[ "$LAB_OBJECT_TYPE" != commit ||
      "$PRODUCT_OBJECT_TYPE" != commit ||
      "$PRODUCT_TREE" != "$EXPECTED_PRODUCT_TREE" ||
      "$R1_BLOB" != "$EXPECTED_R1_BLOB" ]]; then
  printf 'BLOCKED_PRECONDITION|object_identity_mismatch|lab_type=%s|product_type=%s|product_tree=%s|r1_blob=%s\n' "$LAB_OBJECT_TYPE" "$PRODUCT_OBJECT_TYPE" "$PRODUCT_TREE" "$R1_BLOB" >&2
  exit 2
fi

# Do not retry an attempt or overwrite an earlier terminal/unknown effect.
mkdir -p "$RESULT_ROOT"
ATTEMPT_DIR="$RESULT_ROOT/$ATTEMPT_ID"
if ! mkdir "$ATTEMPT_DIR" 2>/dev/null; then
  echo "BLOCKED_PRECONDITION|attempt-already-exists|path=$ATTEMPT_DIR" >&2
  exit 2
fi
TMP=''
PG_NAME=''
PG_CONTAINER_ID=''
cleanup() {
  result=$?
  trap - EXIT
  local cleanup_failed=0
  # Cleanup is a gate, never a best-effort after publishing PASS.
  # Never remove a container merely because its name matches this attempt.
  # If the precondition found a pre-existing name, PG_CONTAINER_ID is empty.
  # Clean up exclusively the exact container ID returned by *our* docker run.
  if [ -n "$PG_CONTAINER_ID" ]; then
    if ! docker rm -f "$PG_CONTAINER_ID" >/dev/null 2>&1; then cleanup_failed=1; fi
  fi
  if [ -n "$TMP" ] && [ -d "$TMP" ]; then
    if ! rm -rf -- "$TMP"; then cleanup_failed=1; fi
  fi
  if [ "$result" -eq 0 ] && [ "$cleanup_failed" -eq 0 ] && [ -f "$ATTEMPT_DIR/tests_passed.pending" ]; then
    if mv "$ATTEMPT_DIR/tests_passed.pending" "$ATTEMPT_DIR/terminal.txt"; then
      cat "$ATTEMPT_DIR/terminal.txt"
      exit 0
    fi
    cleanup_failed=1
  fi
  printf 'FAILED|R1_LOCAL_DOCKER|subject=%s|attempt=%s|execution_exit=%s|cleanup_failed=%s|test_pending=%s\n' "$LAB_SHA" "$ATTEMPT_ID" "$result" "$cleanup_failed" "$([ -f "$ATTEMPT_DIR/tests_passed.pending" ] && echo true || echo false)" > "$ATTEMPT_DIR/terminal.txt"
  exit 1
}
trap cleanup EXIT

printf 'ATTEMPT_STARTED|subject=%s|product=%s|attempt=%s\n' "$LAB_SHA" "$PRODUCT_ACTUAL" "$ATTEMPT_ID" > "$ATTEMPT_DIR/started.txt"
TMP="$(mktemp -d)"
mkdir -p "$TMP/lab" "$TMP/product"
git -C "$LAB" archive --format=tar -o "$TMP/lab.tar" "$LAB_SHA"
git -C "$PRODUCT" archive --format=tar -o "$TMP/product.tar" "$EXPECTED_PRODUCT"
tar -xf "$TMP/lab.tar" -C "$TMP/lab"
tar -xf "$TMP/product.tar" -C "$TMP/product"
PG_NAME="tsremote-r1-$ATTEMPT_ID"
if docker container inspect "$PG_NAME" >/dev/null 2>&1; then
  echo "BLOCKED_PRECONDITION|postgres-container-already-exists|name=$PG_NAME" >&2
  exit 2
fi

# The only Docker containers are ephemeral synthetic PostgreSQL and Node 22.
# Single provider dispatch; retain provider identity for cleanup and join.
PG_CONTAINER_ID="$(docker run -d --name "$PG_NAME" \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=synthetic_ci_only \
  -e POSTGRES_DB=postgres postgres@sha256:5db6dac2ef5dcff512f4f00a009c3c332b9f2f28f24277175bf3e4a3d02ef83a)"
if ! [[ "$PG_CONTAINER_ID" =~ ^[0-9a-f]{64}$ ]]; then
  echo 'UNKNOWN|missing-or-malformed-created-container-identity' >&2
  # Never infer ownership from a matching name; leave for explicit reconciliation.
  PG_CONTAINER_ID=''
  exit 1
fi
printf '%s\n' "$PG_CONTAINER_ID" > "$ATTEMPT_DIR/postgres-container-id.txt"
READY=0
for n in $(seq 1 30); do
  if docker exec "$PG_NAME" pg_isready -U postgres -d postgres >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done
if [ "$READY" -ne 1 ]; then
  echo 'BLOCKED_PRECONDITION|postgres-not-ready' >&2
  exit 2
fi

# Share postgres' network namespace so the frozen R1_DATABASE_URL remains 127.0.0.1:5432.
docker run --rm \
  --network "container:$PG_NAME" \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$TMP,dst=/workspace" \
  --workdir /workspace \
  --env HOME=/tmp \
  --env npm_config_cache=/tmp/npm-cache \
  --env R1_DATABASE_URL='postgresql://postgres:synthetic_ci_only@127.0.0.1:5432/postgres' \
  node@sha256:18a6d90fd60542269850c80ca03b29b1d9b14d6b221ac7ee8e35b0d33ef904bd sh -ec '
    node --version
    (cd product && npm ci --ignore-scripts --no-audit --no-fund)
    (cd lab/experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r2-node &&
      npm ci --ignore-scripts --no-audit --no-fund)
    node --test product/tests/state-kernel-v0/kernel.test.js \
      product/tests/state-kernel-v0/late-obligation-extension.test.js
    node lab/experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r1_a001_ir004_strict_json.cjs
  ' > "$ATTEMPT_DIR/r1.log" 2>&1

if ! grep -Fq 'PASS|R1|bootstrap_forgery|3_negative_cases|original_kernel_parity=true' "$ATTEMPT_DIR/r1.log" ||
   ! grep -Fq 'PASS|R1|mutation_collision|wrong_payload_revision_authority=rejected|no_effect' "$ATTEMPT_DIR/r1.log" ||
   ! grep -Fq 'PASS|R1|concurrent_same_key|commits=1|reconciled=1|no_unique_violation' "$ATTEMPT_DIR/r1.log" ||
    ! grep -Fq 'PASS|A001|command_families=Create,Transition,Satisfy,AddObligations,BootstrapTaskCycle|historical_effects=NONE|parity=true' "$ATTEMPT_DIR/r1.log" ||
    ! grep -Fq 'PASS|A001|strict_json_domain|malformed=16|same_key_rejected=true|parity=true' "$ATTEMPT_DIR/r1.log"; then
  echo 'FAIL|missing-required-R1-pass-markers' >&2
  exit 1
fi

POSTGRES_IMAGE_ID="$(docker image inspect postgres@sha256:5db6dac2ef5dcff512f4f00a009c3c332b9f2f28f24277175bf3e4a3d02ef83a --format '{{.Id}}')"
NODE_IMAGE_ID="$(docker image inspect node@sha256:18a6d90fd60542269850c80ca03b29b1d9b14d6b221ac7ee8e35b0d33ef904bd --format '{{.Id}}')"
printf 'PASS|R1_LOCAL_DOCKER|subject=%s|product=%s|attempt=%s|postgres_image=%s|node_image=%s|scope=synthetic-only\n' \
  "$LAB_SHA" "$EXPECTED_PRODUCT" "$ATTEMPT_ID" "$POSTGRES_IMAGE_ID" "$NODE_IMAGE_ID" > "$ATTEMPT_DIR/tests_passed.pending"
# The EXIT trap releases Docker and tmp files before publishing terminal PASS.
# Never emit a success-looking message before the trap completes.
printf 'R1_TESTS_FINISHED|await_cleanup|subject=%s|attempt=%s\n' "$LAB_SHA" "$ATTEMPT_ID"
