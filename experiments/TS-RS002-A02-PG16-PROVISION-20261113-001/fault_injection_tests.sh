#!/usr/bin/env bash
# Source-only fault injection on GitHub Actions. All Docker calls are fake.
set -Eeuo pipefail
[[ "$GITHUB_ACTIONS" == true ]] || { echo 'BLOCKED CI-only'; exit 21; }
ORIGIN=$(cd "$(dirname "$0")" && pwd -P)
RUNTIME=$(mktemp -d)
trap 'rm -rf -- "$RUNTIME"' EXIT
mkdir -m 700 "$RUNTIME/fake-bin"
cp "$ORIGIN/provision_pg16.sh" "$ORIGIN/schema.sql" "$ORIGIN/image.lock" "$RUNTIME/"
printf 'SYNTHETIC_REPAIR003_ONLY\n' > "$RUNTIME/admission.lock"
test_hash=$(sha256sum "$RUNTIME/admission.lock" | cut -d' ' -f1)
# No Product runner is modified: only the isolated ephemeral CI copy is test-bound.
sed -i "s|^ROOT='/var/tmp/ts-rs002-a02-pg16-20261113-001'$|ROOT='$RUNTIME/effect_root'|" "$RUNTIME/provision_pg16.sh"
sed -i "s|^EXPECTED_ADMISSION_SHA256='UNBOUND_NO_DISPATCH'$|EXPECTED_ADMISSION_SHA256='$test_hash'|" "$RUNTIME/provision_pg16.sh"
grep -Fxq "ROOT='$RUNTIME/effect_root'" "$RUNTIME/provision_pg16.sh"
grep -Fxq "EXPECTED_ADMISSION_SHA256='$test_hash'" "$RUNTIME/provision_pg16.sh"
cat > "$RUNTIME/fake-bin/hostname" <<'MOCK'
#!/usr/bin/env bash
printf 'DESKTOP-DJLBEQH\n'
MOCK
cat > "$RUNTIME/fake-bin/id" <<'MOCK'
#!/usr/bin/env bash
[[ "$1" == -u ]] && { printf '1000\n'; exit 0; }
exit 77
MOCK
cat > "$RUNTIME/fake-bin/docker" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
net='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
ctr='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
vol='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
if [[ "$1 $2" == 'network create' && "$STUB_FAIL_STAGE" == network_create ]]; then exit 44; fi
if [[ "$1 $2" == 'network create' && "$STUB_FAIL_STAGE" == network_bad_id ]]; then printf 'BAD_NETWORK_ID\n'; exit 0; fi
if [[ "$1 $2" == 'network inspect' && "$STUB_FAIL_STAGE" == network_bad_attest ]]; then printf '%064d\n' 0; exit 0; fi
if [[ "$1 $2" == 'pull --platform' && "$STUB_FAIL_STAGE" == image_pull ]]; then exit 43; fi
if [[ "$1 $2" == 'container create' && "$STUB_FAIL_STAGE" == container_create ]]; then exit 45; fi
if [[ "$1 $2" == 'container create' && "$STUB_FAIL_STAGE" == container_bad_id ]]; then printf 'BAD_CONTAINER_ID\n'; exit 0; fi
if [[ "$1 $2" == 'volume inspect' && "$STUB_FAIL_STAGE" == bad_volume_driver ]]; then printf 'foreign\n'; exit 0; fi
if [[ "$1 $2" == 'container inspect' && "$STUB_FAIL_STAGE" == bad_network_attach && "$*" == *".NetworkSettings.Networks"* ]]; then printf '%064d\n' 0; exit 0; fi
if [[ "$1 $2" == 'container inspect' && "$STUB_FAIL_STAGE" == post_start_exited && "$*" == *".State.Status"* ]]; then printf 'exited\n'; exit 0; fi
if [[ "$1 $2" == 'container inspect' && "$STUB_FAIL_STAGE" == volume_attest && "$*" == *".Mounts"* ]]; then exit 46; fi
if [[ "$1 $2" == 'container start' && "$STUB_FAIL_STAGE" == container_start ]]; then exit 47; fi
case "$1 $2" in
 'context show') printf 'default\n';;
 'version --format') printf '29.1.3\n';;
 'info --format') if [[ "$3" == '{{.ID}}' ]]; then printf '1219e4b8-5972-4880-8ebd-4fd2498a3e83\n'; else printf 'linux/amd64\n'; fi;;
 'container ls'|'volume ls'|'network ls') : ;;
 'pull --platform') : ;;
 'image inspect') if [[ "$*" == *".Config.Env"* ]]; then printf 'PG_VERSION=16.15-1.pgdg12+2\n';else printf 'linux/amd64\n';fi;;
 'network create'|'network inspect') printf '%s\n' "$net";;
 'container create') printf '%s\n' "$ctr";;
 'container inspect')
   if [[ "$*" == *".Mounts"* ]];then printf '%s|volume|true\n' "$vol"
   elif [[ "$*" == *".NetworkSettings.Networks"* ]];then printf '%s\n' "$net"
   elif [[ "$*" == *"{{.Id}}"* ]];then printf '%s\n' "$ctr"
   elif [[ "$*" == *"{{.Name}}"* ]];then if [[ "$STUB_FAIL_STAGE" == post_start_foreign_name ]];then printf '/FOREIGN\n';else printf '/ts-rs002-a02-pg16-20261113-001\n';fi
   elif [[ "$*" == *"ts.rs002.operation"* ]];then if [[ "$STUB_FAIL_STAGE" == post_start_foreign_operation ]];then printf 'FOREIGN\n';else printf 'TS-RS002-A02-PG16-PROVISION-20261113-001\n';fi
   elif [[ "$*" == *"ts.rs002.attempt"* ]];then printf 'TS-RS002-A02-PG16-PROVISION-A001\n'
   else printf 'running\n';fi;;
 'volume inspect') printf 'local\n';;
 'container start')
   [[ "${3:-}" == "$ctr" ]] || { printf 'BLOCKED_BY_FAKE: must start by native ID\n' >&2; exit 78; }
   if [[ "$STUB_FAIL_STAGE" == start_foreign_id ]];then printf '%064d\n' 0;else printf '%s\n' "$ctr";fi;;
 *) printf 'UNEXPECTED_MOCK_COMMAND: %s\n' "$*" >&2; exit 99;;
esac
MOCK
chmod 700 "$RUNTIME/fake-bin/"*
export PATH="$RUNTIME/fake-bin:$PATH"
check_failure() {
  local fault="$1"
  rm -rf -- "$RUNTIME/effect_root"
  if (cd "$RUNTIME" && STUB_FAIL_STAGE="$fault" bash ./provision_pg16.sh --apply) > "$RUNTIME/stdout" 2> "$RUNTIME/stderr"; then
    printf 'FAIL: stage %s unexpectedly PASS\n' "$fault" >&2;exit 1
  fi
  local receipt="$RUNTIME/effect_root/attempt-status.txt"
  [[ -f "$receipt" ]] || { printf 'FAIL: missing receipt at %s\n' "$fault" >&2;exit 1; }
  grep -Fxq 'effect=UNKNOWN' "$receipt" || { printf 'FAIL: did not preserve UNKNOWN at %s\n' "$fault" >&2;exit 1; }
  grep -Fq 'NONTERMINAL_PARTIAL_EFFECT' "$RUNTIME/stderr" || { printf 'FAIL: missing failure banner at %s\n' "$fault" >&2;exit 1; }
  if [[ "$fault" == container_create || "$fault" == volume_attest || "$fault" == container_start || "$fault" == start_foreign_id || "$fault" == post_start_foreign_name || "$fault" == post_start_foreign_operation ]]; then
    grep -Fxq "network_id=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" "$receipt" || { echo "lost network ID at $fault";exit 1; }
  fi
  if [[ "$fault" == volume_attest || "$fault" == container_start || "$fault" == start_foreign_id || "$fault" == post_start_foreign_name || "$fault" == post_start_foreign_operation ]]; then
    grep -Fxq "container_id=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" "$receipt" || { echo "lost container ID at $fault";exit 1; }
  fi
  if [[ "$fault" == container_start || "$fault" == start_foreign_id || "$fault" == post_start_foreign_name || "$fault" == post_start_foreign_operation ]]; then
    grep -Fxq "volume_name=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc" "$receipt" || { echo "lost anonymous volume at $fault";exit 1; }
  fi
  printf 'PASS source-fault-injection %s effect=UNKNOWN preserved\n' "$fault"
}
check_failure image_pull
check_failure network_create
check_failure network_bad_id
check_failure network_bad_attest
check_failure container_create
check_failure container_bad_id
check_failure volume_attest
check_failure bad_volume_driver
check_failure bad_network_attach
check_failure container_start
check_failure start_foreign_id
check_failure post_start_foreign_name
check_failure post_start_foreign_operation
check_failure post_start_exited
rm -rf -- "$RUNTIME/effect_root"
(cd "$RUNTIME" && STUB_FAIL_STAGE=none bash ./provision_pg16.sh --apply) > "$RUNTIME/stdout" 2> "$RUNTIME/stderr"
grep -q 'STARTED_UNVERIFIED' "$RUNTIME/stdout"
grep -Fxq 'status=PENDING_NATIVE_POSTCONDITIONS' "$RUNTIME/effect_root/attempt-status.txt"
printf 'PASS source-mocked-started-unverified 1/1, partial-failure 14/14; all Docker calls mocked\n'
