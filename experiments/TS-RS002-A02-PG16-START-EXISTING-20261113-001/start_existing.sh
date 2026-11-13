#!/usr/bin/env bash
# NONPRODUCT: independent B001 starts ONLY the existing original A001 container.
set -Eeuo pipefail
IFS=$'\n\t'
umask 077

OP='TS-RS002-A02-PG16-START-EXISTING-20261113-001'
ATTEMPT='TS-RS002-A02-PG16-START-EXISTING-B001'
OLD_OP='TS-RS002-A02-PG16-PROVISION-20261113-001'
OLD_ATTEMPT='TS-RS002-A02-PG16-PROVISION-A001'
HOST='DESKTOP-DJLBEQH'
DAEMON='1219e4b8-5972-4880-8ebd-4fd2498a3e83'
CID='5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88'
CNAME='/ts-rs002-a02-pg16-20261113-001'
NID='6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35'
VOLUME='e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899'
IMAGE='postgres@sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e'
ORIGINAL_ROOT='/var/tmp/ts-rs002-a02-pg16-20261113-001'
RECEIPT_ROOT='/var/tmp/ts-rs002-a02-pg16-start-existing-20261113-001'
EXPECTED_ADMISSION_SHA256='UNBOUND_NO_DISPATCH'
HERE=$(cd "$(dirname "$0")" && pwd -P)
phase='PRECHECK'; effect='NONE'; receipt=''; terminal_written=0
fail() {
  printf 'BLOCKED: %s\n' "$1" >&2
  if [[ -n "$receipt" ]]; then
    if printf 'phase=%s\neffect=UNKNOWN\nstatus=BLOCKED_OR_INCOMPLETE\n' "$phase" >> "$receipt"; then terminal_written=1; fi
  fi
  exit 21
}
on_exit() {
  local code=$?
  # A shell error, command substitution, or handled signal after an effect
  # must not leave a fabricated PASS or silently lose UNKNOWN.
  if [[ "$effect" == UNKNOWN && "$code" -ne 0 ]]; then
    if [[ -n "$receipt" && "$terminal_written" != 1 ]]; then
      printf 'phase=%s\neffect=UNKNOWN\nstatus=BLOCKED_OR_INCOMPLETE\nexit_code=%s\n' "$phase" "$code" >> "$receipt" || :
    fi
    printf 'NONTERMINAL_PARTIAL_EFFECT original=A001 distinct=B001 phase=%s effect=UNKNOWN do_not_retry\n' "$phase" >&2
  fi
}
trap on_exit EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
eq() { [[ "$2" == "$3" ]] || fail "$1 differs from immutable resource identity"; }
c() { docker container inspect --format "$1" "$CID"; }
n() { docker network inspect --format "$1" "$NID"; }
v() { docker volume inspect --format "$1" "$VOLUME"; }

[[ $# == 1 && ( "$1" == '--preflight' || "$1" == '--start-existing' ) ]] || fail 'invalid exact mode'
mode="$1"
eq 'host' "$(hostname)" "$HOST"
eq 'UID' "$(id -u)" 1000
eq 'Docker context' "$(docker context show)" default
eq 'Docker server' "$(docker version --format '{{.Server.Version}}')" 29.1.3
eq 'Docker daemon' "$(docker info --format '{{.ID}}')" "$DAEMON"
platform=$(docker info --format '{{.OSType}}/{{.Architecture}}')
[[ "$platform" == linux/x86_64 || "$platform" == linux/amd64 ]] || fail 'unexpected Docker platform'
[[ ! -e "$RECEIPT_ROOT" && ! -L "$RECEIPT_ROOT" ]] || fail 'B001 receipt root collision'
eq 'container ID' "$(c '{{.Id}}')" "$CID"
eq 'container name' "$(c '{{.Name}}')" "$CNAME"
eq 'original operation label' "$(c '{{index .Config.Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'original A001 label' "$(c '{{index .Config.Labels "ts.rs002.attempt"}}')" "$OLD_ATTEMPT"
eq 'container prestart status' "$(c '{{.State.Status}}')" created
eq 'container started flag' "$(c '{{.State.Running}}')" false
eq 'container StartedAt' "$(c '{{.State.StartedAt}}')" '0001-01-01T00:00:00Z'
eq 'container restart count' "$(c '{{.RestartCount}}')" 0
eq 'configured original network ID' "$(c '{{.HostConfig.NetworkMode}}')" "$NID"
eq 'container OCI reference' "$(c '{{.Config.Image}}')" "$IMAGE"
eq 'container OCI descriptor' "$(c '{{.ImageManifestDescriptor.digest}}')" 'sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e'
eq 'container OCI os/arch' "$(c '{{index .ImageManifestDescriptor.platform "os"}}/{{index .ImageManifestDescriptor.platform "architecture"}}')" 'linux/amd64'
eq 'memory bytes' "$(c '{{.HostConfig.Memory}}')" 536870912
eq 'nano CPUs' "$(c '{{.HostConfig.NanoCpus}}')" 1000000000
eq 'PID limit' "$(c '{{.HostConfig.PidsLimit}}')" 256
eq 'privileged' "$(c '{{.HostConfig.Privileged}}')" false
eq 'published ports' "$(c '{{json .HostConfig.PortBindings}}')" '{}'
eq 'publish-all' "$(c '{{.HostConfig.PublishAllPorts}}')" false
eq 'restart policy' "$(c '{{.HostConfig.RestartPolicy.Name}}')" no
eq 'original network native ID' "$(n '{{.Id}}')" "$NID"
eq 'original network name' "$(n '{{.Name}}')" 'ts-rs002-a02-pg16-net-20261113-001'
eq 'original network driver' "$(n '{{.Driver}}')" bridge
eq 'original network internal' "$(n '{{.Internal}}')" true
eq 'original network operation label' "$(n '{{index .Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'original volume native name' "$(v '{{.Name}}')" "$VOLUME"
eq 'original volume driver' "$(v '{{.Driver}}')" local
eq 'original PGDATA volume' "$(c '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}')" "$VOLUME|volume|true"

[[ -d "$ORIGINAL_ROOT" && ! -L "$ORIGINAL_ROOT" ]] || fail 'original root missing or symlink'
eq 'original root canonical path' "$(realpath -e -- "$ORIGINAL_ROOT")" "$ORIGINAL_ROOT"
eq 'original root DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT")" '700:1000:1000'
[[ -d "$ORIGINAL_ROOT/secrets" && ! -L "$ORIGINAL_ROOT/secrets" ]] || fail 'original secrets root invalid'
eq 'original secret root canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/secrets")" "$ORIGINAL_ROOT/secrets"
eq 'original secrets DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/secrets")" '700:1000:1000'
[[ -d "$ORIGINAL_ROOT/init" && ! -L "$ORIGINAL_ROOT/init" ]] || fail 'original init root invalid'
eq 'original init canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/init")" "$ORIGINAL_ROOT/init"
eq 'original init DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/init")" '755:1000:1000'
for name in admin.pass observer.pass writer_a.pass writer_b.pass; do
  source="$ORIGINAL_ROOT/secrets/$name"
  [[ -f "$source" && ! -L "$source" ]] || fail 'missing or linked original credential'
  eq 'secret canonical path' "$(realpath -e -- "$source")" "$source"
  eq 'secret owner/DAC' "$(stat -c '%a:%u:%g' "$source")" '644:1000:1000'
  target="/run/secrets/$name"
  [[ "$name" == admin.pass ]] && target='/run/secrets/ts-admin-pass'
  template="{{range .Mounts}}{{if eq .Destination \"$target\"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}"
  eq 'frozen read-only bind' "$(c "$template")" "bind|$source|false"
done
[[ -f "$ORIGINAL_ROOT/init/01-schema.sql" && ! -L "$ORIGINAL_ROOT/init/01-schema.sql" ]] || fail 'original SQL missing'
eq 'original SQL canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/init/01-schema.sql")" "$ORIGINAL_ROOT/init/01-schema.sql"
eq 'original SQL sha256' "$(sha256sum "$ORIGINAL_ROOT/init/01-schema.sql" | cut -d' ' -f1)" 'c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721'
[[ -f "$ORIGINAL_ROOT/init/02-roles.sh" && ! -L "$ORIGINAL_ROOT/init/02-roles.sh" ]] || fail 'original roles missing'
eq 'original role script canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/init/02-roles.sh")" "$ORIGINAL_ROOT/init/02-roles.sh"
eq 'original roles owner/DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/init/02-roles.sh")" '644:1000:1000'
eq 'original roles genesis SHA256' "$(sha256sum "$ORIGINAL_ROOT/init/02-roles.sh" | cut -d' ' -f1)" '67737d584aeeb167ec84c70fef2437d71f11fac10e77e92d989e4418add3f2cd'
eq 'frozen init mount' "$(c '{{range .Mounts}}{{if eq .Destination "/docker-entrypoint-initdb.d"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}')" "bind|$ORIGINAL_ROOT/init|false"

if [[ "$mode" == --preflight ]]; then
  printf 'PREFLIGHT_PASS original=A001 distinct=B001 existing_container_id=%s effect=NONE\n' "$CID"
  exit 0
fi

[[ "$EXPECTED_ADMISSION_SHA256" =~ ^[0-9a-f]{64}$ ]] || fail 'B001 not admitted; source is UNBOUND'
LOCK="$HERE/admission.lock"
[[ -f "$LOCK" && ! -L "$LOCK" ]] || fail 'B001 grant lock missing'
eq 'grant digest' "$(sha256sum "$LOCK" | cut -d' ' -f1)" "$EXPECTED_ADMISSION_SHA256"
python3 - "$LOCK" "$OP" "$ATTEMPT" "$CID" "$NID" "$VOLUME" "$DAEMON" <<'B001_LOCK' || fail 'B001 grant semantic validation failed'
import json,sys
path, op, attempt, container, network, volume, daemon = sys.argv[1:]
with open(path, encoding="utf-8") as f: a=json.load(f)
expected_keys = {"contract_version","disposition","responsibility","operation_id","attempt_id","physical_effect_allowlist","original_attempt","original_container_id","original_network_id","original_volume_id","host","docker_daemon_id","source_review","physical_admission_review","Product_effect","kernel_replacement","Beta_Run_008","no_retry"}
assert type(a) is dict and set(a)==expected_keys
assert a["contract_version"]=="TS-RS002-A02-PG16-EXISTING-START-ADMISSION/v1"
assert a["disposition"]=="ADMITTED_NONPRODUCT_EXISTING_CONTAINER_START_B001"
assert a["responsibility"]=="TS_REMOTE_STATE_002"
assert a["operation_id"]==op and a["attempt_id"]==attempt
assert a["physical_effect_allowlist"]==["EXACT_EXISTING_CONTAINER_START_ONLY"]
assert a["original_attempt"]=="TS-RS002-A02-PG16-PROVISION-A001"
assert a["original_container_id"]==container and a["original_network_id"]==network and a["original_volume_id"]==volume
assert a["host"]=="DESKTOP-DJLBEQH" and a["docker_daemon_id"]==daemon
assert a["source_review"]=="TERMINAL_0F_0A"
assert a["physical_admission_review"]=="TERMINAL_0F_0A_PROCESSED_BY_CONTROL"
assert a["Product_effect"]=="NONE" and a["kernel_replacement"]=="NO_GO"
assert a["Beta_Run_008"]=="BLOCKED" and a["no_retry"] is True
B001_LOCK

# Exclusive one-shot receipt, then exactly ONE docker container start by ID.
phase='RECEIPT_CREATE'
# A crash between directory creation and initial receipt is still a partial
# uncertain B001 effect: an isolated root collision blocks ALL future retries.
effect='UNKNOWN'
mkdir -m 700 -- "$RECEIPT_ROOT" || fail 'receipt create-only collision'
receipt="$RECEIPT_ROOT/attempt-status.txt"
( set -C; printf 'operation=%s\nattempt=%s\noriginal_attempt=%s\ncontainer_id=%s\nnetwork_id=%s\nvolume_id=%s\nphase=RECEIPT_CREATE\neffect=UNKNOWN\n' "$OP" "$ATTEMPT" "$OLD_ATTEMPT" "$CID" "$NID" "$VOLUME" > "$receipt" ) || fail 'receipt create-only failure'
phase='IMMEDIATE_PRESTART_RECHECK'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$receipt"
# Recheck ALL frozen security invariants after grant and receipt, before
# the ONLY Docker start; this is not atomic against external daemon changes.
eq 'immediate current daemon' "$(docker info --format '{{.ID}}')" "$DAEMON"
eq 'immediate original name' "$(c '{{.Name}}')" "$CNAME"
eq 'immediate native ID' "$(c '{{.Id}}')" "$CID"
eq 'immediate original operation label' "$(c '{{index .Config.Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'immediate original attempt label' "$(c '{{index .Config.Labels "ts.rs002.attempt"}}')" "$OLD_ATTEMPT"
eq 'immediate unstarted status' "$(c '{{.State.Status}}')" created
eq 'immediate running flag' "$(c '{{.State.Running}}')" false
eq 'immediate restart count' "$(c '{{.RestartCount}}')" 0
eq 'immediate never started timestamp' "$(c '{{.State.StartedAt}}')" '0001-01-01T00:00:00Z'
eq 'immediate configured network ID' "$(c '{{.HostConfig.NetworkMode}}')" "$NID"
eq 'immediate network name' "$(n '{{.Name}}')" 'ts-rs002-a02-pg16-net-20261113-001'
eq 'immediate network driver' "$(n '{{.Driver}}')" bridge
eq 'immediate internal network' "$(n '{{.Internal}}')" true
eq 'immediate network operation label' "$(n '{{index .Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'immediate volume native ID' "$(v '{{.Name}}')" "$VOLUME"
eq 'immediate volume driver' "$(v '{{.Driver}}')" local
eq 'immediate exact PGDATA volume' "$(c '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}')" "$VOLUME|volume|true"
eq 'immediate OCI digest' "$(c '{{.ImageManifestDescriptor.digest}}')" 'sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e'
eq 'immediate original OCI reference' "$(c '{{.Config.Image}}')" "$IMAGE"
eq 'immediate OCI platform' "$(c '{{index .ImageManifestDescriptor.platform "os"}}/{{index .ImageManifestDescriptor.platform "architecture"}}')" linux/amd64
eq 'immediate privileged flag' "$(c '{{.HostConfig.Privileged}}')" false
eq 'immediate port bindings' "$(c '{{json .HostConfig.PortBindings}}')" '{}'
eq 'immediate publish all' "$(c '{{.HostConfig.PublishAllPorts}}')" false
eq 'immediate restart policy' "$(c '{{.HostConfig.RestartPolicy.Name}}')" no
eq 'immediate memory' "$(c '{{.HostConfig.Memory}}')" 536870912
eq 'immediate nano CPUs' "$(c '{{.HostConfig.NanoCpus}}')" 1000000000
eq 'immediate PIDs' "$(c '{{.HostConfig.PidsLimit}}')" 256
eq 'immediate root canonical path' "$(realpath -e -- "$ORIGINAL_ROOT")" "$ORIGINAL_ROOT"
eq 'immediate root DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT")" '700:1000:1000'
eq 'immediate secrets canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/secrets")" "$ORIGINAL_ROOT/secrets"
eq 'immediate init canonical path' "$(realpath -e -- "$ORIGINAL_ROOT/init")" "$ORIGINAL_ROOT/init"
eq 'immediate init DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/init")" '755:1000:1000'
eq 'immediate frozen SQL SHA256' "$(sha256sum "$ORIGINAL_ROOT/init/01-schema.sql" | cut -d' ' -f1)" 'c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721'
eq 'immediate original init mount' "$(c '{{range .Mounts}}{{if eq .Destination "/docker-entrypoint-initdb.d"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}')" "bind|$ORIGINAL_ROOT/init|false"
eq 'immediate secrets root DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/secrets")" '700:1000:1000'
eq 'immediate frozen init SHA256' "$(sha256sum "$ORIGINAL_ROOT/init/02-roles.sh" | cut -d' ' -f1)" '67737d584aeeb167ec84c70fef2437d71f11fac10e77e92d989e4418add3f2cd'
for name in admin.pass observer.pass writer_a.pass writer_b.pass; do
  original="$ORIGINAL_ROOT/secrets/$name"
  [[ -f "$original" && ! -L "$original" ]] || fail 'immediate original credential missing or linked'
  eq 'immediate credential canonical path' "$(realpath -e -- "$original")" "$original"
  eq 'immediate credential owner/DAC' "$(stat -c '%a:%u:%g' "$original")" '644:1000:1000'
  target="/run/secrets/$name"
  [[ "$name" == admin.pass ]] && target='/run/secrets/ts-admin-pass'
  template="{{range .Mounts}}{{if eq .Destination \"$target\"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}"
  eq 'immediate frozen secret read-only bind' "$(c "$template")" "bind|$original|false"
done
phase='EXACT_EXISTING_CONTAINER_START'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$receipt"
returned=$(docker container start "$CID") || fail 'docker container start failure or ambiguous effect'
printf 'start_returned=%s\n' "$returned" >> "$receipt"
[[ "$returned" == "$CID" || "$returned" == 'ts-rs002-a02-pg16-20261113-001' ]] || fail 'unexpected start return'
eq 'poststart native ID' "$(c '{{.Id}}')" "$CID"
eq 'poststart name' "$(c '{{.Name}}')" "$CNAME"
eq 'poststart original operation label' "$(c '{{index .Config.Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'poststart original label' "$(c '{{index .Config.Labels "ts.rs002.attempt"}}')" "$OLD_ATTEMPT"
eq 'poststart OCI image' "$(c '{{.Config.Image}}')" "$IMAGE"
eq 'poststart OCI descriptor' "$(c '{{.ImageManifestDescriptor.digest}}')" 'sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e'
eq 'poststart OCI os/arch' "$(c '{{index .ImageManifestDescriptor.platform "os"}}/{{index .ImageManifestDescriptor.platform "architecture"}}')" 'linux/amd64'
eq 'poststart privileged' "$(c '{{.HostConfig.Privileged}}')" false
eq 'poststart published ports' "$(c '{{json .HostConfig.PortBindings}}')" '{}'
eq 'poststart publish-all' "$(c '{{.HostConfig.PublishAllPorts}}')" false
eq 'poststart restart policy' "$(c '{{.HostConfig.RestartPolicy.Name}}')" no
eq 'poststart original network mode' "$(c '{{.HostConfig.NetworkMode}}')" "$NID"
eq 'poststart memory' "$(c '{{.HostConfig.Memory}}')" 536870912
eq 'poststart CPUs' "$(c '{{.HostConfig.NanoCpus}}')" 1000000000
eq 'poststart PIDs' "$(c '{{.HostConfig.PidsLimit}}')" 256
eq 'poststart attached network' "$(c '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')" "$NID"
eq 'poststart PGDATA' "$(c '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}')" "$VOLUME|volume|true"
eq 'poststart original network name' "$(n '{{.Name}}')" 'ts-rs002-a02-pg16-net-20261113-001'
eq 'poststart original network driver' "$(n '{{.Driver}}')" bridge
eq 'poststart original internal network' "$(n '{{.Internal}}')" true
for name in admin.pass observer.pass writer_a.pass writer_b.pass; do
  original="$ORIGINAL_ROOT/secrets/$name"
  target="/run/secrets/$name"
  [[ "$name" == admin.pass ]] && target='/run/secrets/ts-admin-pass'
  template="{{range .Mounts}}{{if eq .Destination \"$target\"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}"
  eq 'poststart frozen credential RO bind' "$(c "$template")" "bind|$original|false"
done
eq 'poststart frozen init RO bind' "$(c '{{range .Mounts}}{{if eq .Destination "/docker-entrypoint-initdb.d"}}{{.Type}}|{{.Source}}|{{.RW}}{{end}}{{end}}')" "bind|$ORIGINAL_ROOT/init|false"
state=$(c '{{.State.Status}}')
printf 'poststart_status=%s\n' "$state" >> "$receipt"
[[ "$state" == running ]] || fail 'container not running after start'
phase='STARTED_UNVERIFIED'
effect='STARTED_PENDING_PG_GENESIS'
printf 'phase=%s\neffect=%s\nstatus=PENDING_INDEPENDENT_PG_GENESIS_AND_ACL\n' "$phase" "$effect" >> "$receipt"
printf 'STARTED_UNVERIFIED original=A001 distinct=B001 container_id=%s receipt=%s\n' "$CID" "$receipt"
