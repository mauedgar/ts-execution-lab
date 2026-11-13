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
# Positive PRECHECK only with a fully fake host/engine; never runs a physical docker.
rm "$RUNTIME/schema.sql" "$RUNTIME/image.lock"
cp "$ROOT/schema.sql" "$ROOT/image.lock" "$RUNTIME/"
mkdir -p "$RUNTIME/fake-bin"
cat > "$RUNTIME/fake-bin/hostname" <<'STUB'
#!/usr/bin/env bash
printf 'DESKTOP-DJLBEQH\n'
STUB
cat > "$RUNTIME/fake-bin/id" <<'STUB'
#!/usr/bin/env bash
[[ "$1" == -u ]] && { printf '1000\n'; exit 0; }
exit 42
STUB
cat > "$RUNTIME/fake-bin/docker" <<'STUB'
#!/usr/bin/env bash
if [[ "${STUB_DAEMON_DENIED:-0}" == 1 ]]; then exit 77; fi
case "$1 $2" in
  'context show') printf 'default\n';;
  'version --format') printf '29.1.3\n';;
  'info --format') if [[ "$3" == '{{.ID}}' ]]; then printf '1219e4b8-5972-4880-8ebd-4fd2498a3e83\n'; else printf 'linux/amd64\n'; fi;;
  'container ls') if [[ "${STUB_COLLIDE:-}" == container ]]; then printf 'ts-rs002-a02-pg16-20261113-001\n'; fi;;
  'volume ls'|'network ls') : ;;
  *) printf 'unexpected docker command (mutation blocked)\n' >&2; exit 42;;
esac
STUB
chmod 700 "$RUNTIME/fake-bin/hostname" "$RUNTIME/fake-bin/id" "$RUNTIME/fake-bin/docker"
(cd "$RUNTIME" && PATH="$RUNTIME/fake-bin:$PATH" bash ./provision_pg16.sh --preflight) > "$RUNTIME/out"
grep -q 'PREFLIGHT_PASS' "$RUNTIME/out" || { echo 'FAIL synthetic positive preflight'; exit 1; }
echo 'PASS synthetic-positive-preflight'
if (cd "$RUNTIME" && PATH="$RUNTIME/fake-bin:$PATH" STUB_DAEMON_DENIED=1 bash ./provision_pg16.sh --preflight) > "$RUNTIME/out" 2>&1; then echo 'FAIL daemon-denied'; exit 1; fi
BLOCKS=$((BLOCKS+1)); echo 'PASS daemon-denied'
if (cd "$RUNTIME" && PATH="$RUNTIME/fake-bin:$PATH" STUB_COLLIDE=container bash ./provision_pg16.sh --preflight) > "$RUNTIME/out" 2>&1; then echo 'FAIL container-collision'; exit 1; fi
BLOCKS=$((BLOCKS+1)); echo 'PASS container-collision'
if (cd "$RUNTIME" && PATH="$RUNTIME/fake-bin:$PATH" bash ./provision_pg16.sh --apply) > "$RUNTIME/out" 2>&1; then echo 'FAIL unbound-admission'; exit 1; fi
BLOCKS=$((BLOCKS+1)); echo 'PASS unbound-admission'
printf 'NEGATIVE_CONTROLS %d/%d PASS; synthetic-positive 1/1 PASS (source-level only)\n' "$BLOCKS" "$BLOCKS"
