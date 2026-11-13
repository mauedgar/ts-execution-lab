#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd -P)
RUNTIME=$(mktemp -d)
trap 'rm -rf "$RUNTIME"' EXIT
cp "$ROOT/provision_pg16.sh" "$ROOT/schema.sql" "$RUNTIME/"
BLOCKS=0
assert_blocked() {
  local name="$1"; shift
  if (cd "$RUNTIME" && bash ./provision_pg16.sh "$@") > "$RUNTIME/out" 2>&1; then
    echo "FAIL $name unexpected PASS" >&2; exit 1
  fi
  if [[ -e /var/tmp/ts-rs002-a02-pg16-20261113-001 ]]; then
    echo "FAIL $name potential physical workspace effect" >&2; exit 1
  fi
  BLOCKS=$(( BLOCKS + 1 ))
  echo "PASS $name"
}
assert_blocked missing-image-lock --preflight
printf 'invalid-tag\n' > "$RUNTIME/image.lock"
assert_blocked invalid-image-ref --preflight
printf 'postgres@sha256:%064d\n' 0 > "$RUNTIME/image.lock"
echo '-- malicious fixture' >> "$RUNTIME/schema.sql"
assert_blocked schema-modified --preflight
cp "$ROOT/schema.sql" "$RUNTIME/schema.sql"
assert_blocked wrong-host --preflight
assert_blocked invalid-mode --provision
rm "$RUNTIME/image.lock"
ln -s /etc/hosts "$RUNTIME/image.lock"
assert_blocked symlink-lock --preflight
rm "$RUNTIME/schema.sql"
ln -s /etc/hosts "$RUNTIME/schema.sql"
assert_blocked symlink-schema --preflight
printf 'NEGATIVE_CONTROLS %d/%d PASS (source-level only)\n' "$BLOCKS" "$BLOCKS"
