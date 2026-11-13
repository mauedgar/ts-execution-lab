#!/usr/bin/env bash
# Hosted GitHub CI only. Fake exact original Docker resources and B001 effects.
set -Eeuo pipefail
[[ "$GITHUB_ACTIONS" == true ]] || { echo 'BLOCKED: CI fixture only' >&2; exit 21; }
ORIGIN=$(cd "$(dirname "$0")" && pwd -P)
RUNTIME=$(mktemp -d)
trap 'rm -rf -- "$RUNTIME"' EXIT
mkdir -m 700 "$RUNTIME/fake-bin" "$RUNTIME/original"
mkdir -m 700 "$RUNTIME/original/secrets"
mkdir -m 755 "$RUNTIME/original/init"
cp "$ORIGIN/start_existing.sh" "$RUNTIME/source_unbound.sh"
cp "$ORIGIN/start_existing.sh" "$RUNTIME/bound.sh"
BASE="$ORIGIN/../TS-RS002-A02-PG16-PROVISION-20261113-001"
cp "$BASE/schema.sql" "$RUNTIME/original/init/01-schema.sql"
python3 - "$BASE/provision_pg16.sh" "$RUNTIME/original/init/02-roles.sh" <<'GENESIS_FIXTURE'
import hashlib, pathlib, sys
src=pathlib.Path(sys.argv[1]).read_text()
marker='cat > "$ROOT/init/02-roles.sh" <<'+"'GENESIS'"+'\n'
assert src.count(marker)==1
generated=src.split(marker,1)[1].split('\nGENESIS\n',1)[0]+'\n'
assert hashlib.sha256(generated.encode()).hexdigest()=="67737d584aeeb167ec84c70fef2437d71f11fac10e77e92d989e4418add3f2cd"
pathlib.Path(sys.argv[2]).write_text(generated)
GENESIS_FIXTURE
chmod 644 "$RUNTIME/original/init/"*
for name in admin.pass observer.pass writer_a.pass writer_b.pass; do
  printf 'SYNTHETIC-NOT-A-CREDENTIAL\n' > "$RUNTIME/original/secrets/$name"
done
chmod 644 "$RUNTIME/original/secrets/"*.pass

# Only synthetic files are ever created. The original physical paths are
# replaced in both temporary runner copies; nothing under /var/tmp is touched.
for file in "$RUNTIME/source_unbound.sh" "$RUNTIME/bound.sh"; do
  sed -i "s|^ORIGINAL_ROOT='/var/tmp/ts-rs002-a02-pg16-20261113-001'$|ORIGINAL_ROOT='$RUNTIME/original'|" "$file"
  sed -i "s|^RECEIPT_ROOT='/var/tmp/ts-rs002-a02-pg16-start-existing-20261113-001'$|RECEIPT_ROOT='$RUNTIME/result'|" "$file"
  grep -Fxq "ORIGINAL_ROOT='$RUNTIME/original'" "$file"
  grep -Fxq "RECEIPT_ROOT='$RUNTIME/result'" "$file"
done

cat > "$RUNTIME/admission.lock" <<'FAKE_ADMISSION'
{
  "contract_version": "TS-RS002-A02-PG16-EXISTING-START-ADMISSION/v1",
  "disposition": "ADMITTED_NONPRODUCT_EXISTING_CONTAINER_START_B001",
  "responsibility": "TS_REMOTE_STATE_002",
  "operation_id": "TS-RS002-A02-PG16-START-EXISTING-20261113-001",
  "attempt_id": "TS-RS002-A02-PG16-START-EXISTING-B001",
  "physical_effect_allowlist": ["EXACT_EXISTING_CONTAINER_START_ONLY"],
  "original_attempt": "TS-RS002-A02-PG16-PROVISION-A001",
  "original_container_id": "5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88",
  "original_network_id": "6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35",
  "original_volume_id": "e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899",
  "host": "DESKTOP-DJLBEQH",
  "docker_daemon_id": "1219e4b8-5972-4880-8ebd-4fd2498a3e83",
  "source_review": "TERMINAL_0F_0A",
  "physical_admission_review": "TERMINAL_0F_0A_PROCESSED_BY_CONTROL",
  "Product_effect": "NONE",
  "kernel_replacement": "NO_GO",
  "Beta_Run_008": "BLOCKED",
  "no_retry": true
}
FAKE_ADMISSION
test_hash=$(sha256sum "$RUNTIME/admission.lock" | cut -d' ' -f1)
sed -i "s|^EXPECTED_ADMISSION_SHA256='UNBOUND_NO_DISPATCH'$|EXPECTED_ADMISSION_SHA256='$test_hash'|" "$RUNTIME/bound.sh"
grep -Fxq "EXPECTED_ADMISSION_SHA256='$test_hash'" "$RUNTIME/bound.sh"

cat > "$RUNTIME/fake-bin/hostname" <<'MOCK'
#!/usr/bin/env bash
echo DESKTOP-DJLBEQH
MOCK
cat > "$RUNTIME/fake-bin/id" <<'MOCK'
#!/usr/bin/env bash
[[ "$1" == -u ]] && { echo 1000; exit 0; }
exit 77
MOCK
cat > "$RUNTIME/fake-bin/stat" <<'MOCK'
#!/usr/bin/env bash
[[ "$1" == -c && "$2" == '%a:%u:%g' ]] || exit 72
mode=$(/usr/bin/stat -c '%a' "$3") || exit 73
printf '%s:1000:1000\n' "$mode"
MOCK
cat > "$RUNTIME/fake-bin/docker" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
CID='5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88'
NID='6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35'
VOL='e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899'
IMG='postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e'
case "$1 $2" in
 'context show') echo default;;
 'version --format') echo 29.1.3;;
 'info --format')
    if [[ "$3" == '{{.ID}}' ]]; then
      if [[ "$STUB_FAIL" == foreign_daemon ]]; then echo FOREIGN; else echo 1219e4b8-5972-4880-8ebd-4fd2498a3e83; fi
    else echo linux/amd64; fi;;
 'container inspect')
    [[ "$3" == --format && "$5" == "$CID" ]] || exit 75
    fmt="$4"
    case "$fmt" in
      '{{.Id}}') echo "$CID";;
      '{{.Name}}')
        if [[ "$STUB_FAIL" == poststart_foreign_name && -f "$STUB_STARTED" ]];then echo /FOREIGN;else echo /ts-rs002-a02-pg16-20261113-001;fi;;
      *'ts.rs002.operation'*)
          if [[ "$STUB_FAIL" == foreign_operation || ( "$STUB_FAIL" == poststart_foreign_operation && -f "$STUB_STARTED" ) ]];then echo FOREIGN
          else echo TS-RS002-A02-PG16-PROVISION-20261113-001;fi;;
      *'ts.rs002.attempt'*) echo TS-RS002-A02-PG16-PROVISION-A001;;
      '{{.State.Status}}')
         if [[ -f "$STUB_STARTED" ]]; then
           if [[ "$STUB_FAIL" == poststart_exited ]]; then echo exited; else echo running; fi
         elif [[ "$STUB_FAIL" == foreign_status ]]; then echo running
         else echo created; fi;;
      '{{.State.Running}}') echo false;;
      '{{.State.StartedAt}}') echo 0001-01-01T00:00:00Z;;
      '{{.RestartCount}}') echo 0;;
      '{{.HostConfig.NetworkMode}}') if [[ "$STUB_FAIL" == foreign_network_mode ]]; then echo FOREIGN; else echo "$NID"; fi;;
      '{{.Config.Image}}') echo "$IMG";;
      '{{.ImageManifestDescriptor.digest}}')
        if [[ "$STUB_FAIL" == poststart_foreign_oci && -f "$STUB_STARTED" ]];then echo sha256:$(printf '0%.0s' {1..64});else echo sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e;fi;;
      '{{index .ImageManifestDescriptor.platform "os"}}/{{index .ImageManifestDescriptor.platform "architecture"}}')
        if [[ "$STUB_FAIL" == foreign_platform ]];then echo linux/arm64;else echo linux/amd64;fi;;
      '{{.HostConfig.Memory}}')
        if [[ "$STUB_FAIL" == foreign_memory ]];then echo 128;else echo 536870912;fi;;
      '{{.HostConfig.NanoCpus}}') if [[ "$STUB_FAIL" == foreign_cpu ]];then echo 0;else echo 1000000000;fi;;
      '{{.HostConfig.PidsLimit}}') if [[ "$STUB_FAIL" == foreign_pids ]];then echo 128;else echo 256;fi;;
      '{{.HostConfig.Privileged}}'|'{{.HostConfig.PublishAllPorts}}') echo false;;
      '{{json .HostConfig.PortBindings}}')
        if [[ "$STUB_FAIL" == poststart_exposed_port && -f "$STUB_STARTED" ]];then echo '{"5432/tcp":[{"HostPort":"55432"}]}';else echo '{}';fi;;
      '{{.HostConfig.RestartPolicy.Name}}') echo no;;
      *'"/var/lib/postgresql/data"'*)
          if [[ "$STUB_FAIL" == foreign_volume ]];then echo FOREIGN'|volume|true';else echo "$VOL|volume|true";fi;;
      *'"/docker-entrypoint-initdb.d"'*) echo "$STUB_ORIGINAL/init|false";;
      *'/run/secrets/ts-admin-pass'*) echo "$STUB_ORIGINAL/secrets/admin.pass|false";;
      *'/run/secrets/observer.pass'*)
        if [[ "$STUB_FAIL" == poststart_foreign_secret && -f "$STUB_STARTED" ]];then echo '/tmp/foreign-secret|false';else echo "$STUB_ORIGINAL/secrets/observer.pass|false";fi;;
      *'/run/secrets/writer_a.pass'*) echo "$STUB_ORIGINAL/secrets/writer_a.pass|false";;
      *'/run/secrets/writer_b.pass'*) echo "$STUB_ORIGINAL/secrets/writer_b.pass|false";;
      *'.NetworkSettings.Networks'*)
         if [[ "$STUB_FAIL" == poststart_network_missing ]];then echo
         elif [[ -f "$STUB_STARTED" ]];then echo "$NID"
         else echo;fi;;
      *) echo "INVALID_MOCK_CONTAINER_INSPECT_FORMAT: $fmt" >&2; exit 80;;
    esac;;
 'network inspect')
    [[ "$5" == "$NID" ]] || exit 82
    case "$4" in
      '{{.Id}}') echo "$NID";;
      '{{.Name}}') if [[ "$STUB_FAIL" == foreign_network_name ]];then echo FOREIGN;else echo ts-rs002-a02-pg16-net-20261113-001;fi;;
      '{{.Driver}}') if [[ "$STUB_FAIL" == foreign_network_driver ]];then echo host;else echo bridge;fi;;
      '{{.Internal}}') echo true;;
      *'ts.rs002.operation'*) echo TS-RS002-A02-PG16-PROVISION-20261113-001;;
      *) exit 83;;
    esac;;
 'volume inspect')
    [[ "$5" == "$VOL" ]] || exit 84
    case "$4" in
      '{{.Name}}') echo "$VOL";;
      '{{.Driver}}') echo local;;
      *) exit 85;;
    esac;;
 'container start')
    [[ "$3" == "$CID" ]] || { echo 'START-BY-ID-REQUIRED' >&2;exit 86; }
    if [[ "$STUB_FAIL" == start_failure ]];then exit 87;fi
    : > "$STUB_STARTED"
    if [[ "$STUB_FAIL" == start_wrong_return ]];then echo WRONG;else echo "$CID";fi;;
 *) echo "UNEXPECTED_MOCK_DOCKER_COMMAND: $*" >&2; exit 99;;
esac
MOCK
chmod 700 "$RUNTIME/fake-bin/"*
export PATH="$RUNTIME/fake-bin:$PATH"
export STUB_ORIGINAL="$RUNTIME/original"
export STUB_STARTED="$RUNTIME/fake-docker-started"

# Read-only positive preflight (uses unbound source, all exact data and fake Docker).
(cd "$RUNTIME" && STUB_FAIL=none bash ./source_unbound.sh --preflight) > "$RUNTIME/out" 2> "$RUNTIME/err"
grep -Fq 'PREFLIGHT_PASS original=A001 distinct=B001' "$RUNTIME/out"
[[ ! -e "$RUNTIME/result" && ! -e "$STUB_STARTED" ]] || exit 70
echo 'PASS isolated existing-resource preflight effect=NONE'

# No caller may launch source UNBOUND even when all physical identities match.
if (cd "$RUNTIME" && STUB_FAIL=none bash ./source_unbound.sh --start-existing) > "$RUNTIME/out" 2> "$RUNTIME/err";then exit 71;fi
grep -Fq 'B001 not admitted' "$RUNTIME/err"
[[ ! -e "$RUNTIME/result" && ! -e "$STUB_STARTED" ]] || exit 72
echo 'PASS source UNBOUND_NO_DISPATCH denies physical start'

precheck_failure() {
  local fault="$1"
  rm -f -- "$STUB_STARTED"
  if (cd "$RUNTIME" && STUB_FAIL="$fault" bash ./bound.sh --preflight) > "$RUNTIME/out" 2> "$RUNTIME/err";then
    echo "FAIL: preflight fault $fault accepted" >&2;exit 73
  fi
  [[ ! -e "$RUNTIME/result" && ! -e "$STUB_STARTED" ]] || exit 74
  echo "PASS fake-native-preflight-negative $fault"
}
precheck_failure foreign_daemon
precheck_failure foreign_status
precheck_failure foreign_operation
precheck_failure foreign_network_mode
precheck_failure foreign_volume
precheck_failure foreign_network_name
precheck_failure foreign_network_driver
precheck_failure foreign_memory
precheck_failure foreign_cpu
precheck_failure foreign_pids
precheck_failure foreign_platform

# Fully staged synthetic B001, faulting only inside new isolated CI fixture.
start_failure() {
  local fault="$1"
  rm -rf -- "$RUNTIME/result"
  rm -f -- "$STUB_STARTED"
  if (cd "$RUNTIME" && STUB_FAIL="$fault" bash ./bound.sh --start-existing) > "$RUNTIME/out" 2> "$RUNTIME/err";then
    echo "FAIL: start fault $fault accepted" >&2; exit 75
  fi
  local receipt="$RUNTIME/result/attempt-status.txt"
  [[ -f "$receipt" ]] || exit 76
  grep -Fxq 'effect=UNKNOWN' "$receipt" || exit 77
  grep -Fxq 'status=BLOCKED_OR_INCOMPLETE' "$receipt" || exit 78
  grep -Fxq 'container_id=5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88' "$receipt" || exit 79
  echo "PASS fake-existing-only-start-failure $fault preserves UNKNOWN/ID"
}
start_failure start_failure
start_failure start_wrong_return
start_failure poststart_network_missing
start_failure poststart_exited
start_failure poststart_foreign_name
start_failure poststart_foreign_operation
start_failure poststart_foreign_oci
start_failure poststart_exposed_port
start_failure poststart_foreign_secret

rm -rf -- "$RUNTIME/result"
rm -f -- "$STUB_STARTED"
(cd "$RUNTIME" && STUB_FAIL=none bash ./bound.sh --start-existing) > "$RUNTIME/out" 2> "$RUNTIME/err"
grep -Fq 'STARTED_UNVERIFIED original=A001 distinct=B001' "$RUNTIME/out"
grep -Fxq 'status=PENDING_INDEPENDENT_PG_GENESIS_AND_ACL' "$RUNTIME/result/attempt-status.txt"
grep -Fxq 'network_id=6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35' "$RUNTIME/result/attempt-status.txt"
[[ -f "$STUB_STARTED" ]] || exit 88
echo 'PASS fake-existing-only B001 started-unverified; 11 preflight negatives / 9 partial effects; no real Docker'
