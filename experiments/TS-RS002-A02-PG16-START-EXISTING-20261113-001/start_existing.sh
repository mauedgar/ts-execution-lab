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
phase='PRECHECK'; effect='NONE'; receipt=''
fail() {
  printf 'BLOCKED: %s\n' "$1" >&2
  if [[ -n "$receipt" ]]; then
    printf 'phase=%s\neffect=UNKNOWN\nstatus=BLOCKED_OR_INCOMPLETE\n' "$phase" >> "$receipt" || :
  fi
  exit 21
}
trap 'if [[ "$effect" == UNKNOWN ]]; then printf "NONTERMINAL_PARTIAL_EFFECT original=A001 distinct=B001 phase=%s do_not_retry\n" "$phase" >&2; fi' EXIT
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
eq 'privileged' "$(c '{{.HostConfig.Privileged}}')" false
eq 'published ports' "$(c '{{json .HostConfig.PortBindings}}')" '{}'
eq 'publish-all' "$(c '{{.HostConfig.PublishAllPorts}}')" false
eq 'restart policy' "$(c '{{.HostConfig.RestartPolicy.Name}}')" no
eq 'original network native ID' "$(n '{{.Id}}')" "$NID"
eq 'original network internal' "$(n '{{.Internal}}')" true
eq 'original network operation label' "$(n '{{index .Labels "ts.rs002.operation"}}')" "$OLD_OP"
eq 'original volume native name' "$(v '{{.Name}}')" "$VOLUME"
eq 'original volume driver' "$(v '{{.Driver}}')" local
eq 'original PGDATA volume' "$(c '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}')" "$VOLUME|volume|true"

[[ -d "$ORIGINAL_ROOT" && ! -L "$ORIGINAL_ROOT" ]] || fail 'original root missing or symlink'
eq 'original root DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT")" '700:1000:1000'
[[ -d "$ORIGINAL_ROOT/secrets" && ! -L "$ORIGINAL_ROOT/secrets" ]] || fail 'original secrets root invalid'
eq 'original secrets DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/secrets")" '700:1000:1000'
[[ -d "$ORIGINAL_ROOT/init" && ! -L "$ORIGINAL_ROOT/init" ]] || fail 'original init root invalid'
eq 'original init DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/init")" '755:1000:1000'
for name in admin.pass observer.pass writer_a.pass writer_b.pass; do
  source="$ORIGINAL_ROOT/secrets/$name"
  [[ -f "$source" && ! -L "$source" ]] || fail 'missing or linked original credential'
  eq 'secret owner/DAC' "$(stat -c '%a:%u:%g' "$source")" '644:1000:1000'
  target="/run/secrets/$name"
  [[ "$name" == admin.pass ]] && target='/run/secrets/ts-admin-pass'
  template="{{range .Mounts}}{{if eq .Destination \"$target\"}}{{.Source}}|{{.RW}}{{end}}{{end}}"
  eq 'frozen read-only bind' "$(c "$template")" "$source|false"
done
[[ -f "$ORIGINAL_ROOT/init/01-schema.sql" && ! -L "$ORIGINAL_ROOT/init/01-schema.sql" ]] || fail 'original SQL missing'
eq 'original SQL sha256' "$(sha256sum "$ORIGINAL_ROOT/init/01-schema.sql" | cut -d' ' -f1)" 'c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721'
[[ -f "$ORIGINAL_ROOT/init/02-roles.sh" && ! -L "$ORIGINAL_ROOT/init/02-roles.sh" ]] || fail 'original roles missing'
eq 'original roles owner/DAC' "$(stat -c '%a:%u:%g' "$ORIGINAL_ROOT/init/02-roles.sh")" '644:1000:1000'
eq 'original roles genesis SHA256' "$(sha256sum "$ORIGINAL_ROOT/init/02-roles.sh" | cut -d' ' -f1)" '67737d584aeeb167ec84c70fef2437d71f11fac10e77e92d989e4418add3f2cd'
eq 'frozen init mount' "$(c '{{range .Mounts}}{{if eq .Destination "/docker-entrypoint-initdb.d"}}{{.Source}}|{{.RW}}{{end}}{{end}}')" "$ORIGINAL_ROOT/init|false"

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
mkdir -m 700 -- "$RECEIPT_ROOT" || fail 'receipt create-only collision'
effect='UNKNOWN'
receipt="$RECEIPT_ROOT/attempt-status.txt"
( set -C; printf 'operation=%s\nattempt=%s\noriginal_attempt=%s\ncontainer_id=%s\nnetwork_id=%s\nvolume_id=%s\nphase=RECEIPT_CREATE\neffect=UNKNOWN\n' "$OP" "$ATTEMPT" "$OLD_ATTEMPT" "$CID" "$NID" "$VOLUME" > "$receipt" ) || fail 'receipt create-only failure'
phase='EXACT_EXISTING_CONTAINER_START'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$receipt"
returned=$(docker container start "$CID") || fail 'docker container start failure or ambiguous effect'
printf 'start_returned=%s\n' "$returned" >> "$receipt"
[[ "$returned" == "$CID" || "$returned" == 'ts-rs002-a02-pg16-20261113-001' ]] || fail 'unexpected start return'
eq 'poststart native ID' "$(c '{{.Id}}')" "$CID"
eq 'poststart original label' "$(c '{{index .Config.Labels "ts.rs002.attempt"}}')" "$OLD_ATTEMPT"
eq 'poststart attached network' "$(c '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')" "$NID"
eq 'poststart PGDATA' "$(c '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}')" "$VOLUME|volume|true"
state=$(c '{{.State.Status}}')
printf 'poststart_status=%s\n' "$state" >> "$receipt"
[[ "$state" == running ]] || fail 'container not running after start'
phase='STARTED_UNVERIFIED'
effect='STARTED_PENDING_PG_GENESIS'
printf 'phase=%s\neffect=%s\nstatus=PENDING_INDEPENDENT_PG_GENESIS_AND_ACL\n' "$phase" "$effect" >> "$receipt"
printf 'STARTED_UNVERIFIED original=A001 distinct=B001 container_id=%s receipt=%s\n' "$CID" "$receipt"
