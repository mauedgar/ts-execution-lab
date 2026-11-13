#!/usr/bin/env bash
# TS-RS002-A02-PG16-PROVISION-v1 — isolated nonProduct, no cleanup/retry.
set -Eeuo pipefail
IFS=$'\n\t'
umask 077

# All resource identities are intentionally literal and not CLI-configurable.
OPERATION='TS-RS002-A02-PG16-PROVISION-20261113-001'
ATTEMPT='TS-RS002-A02-PG16-PROVISION-A001'
HOST='DESKTOP-DJLBEQH'
CONTAINER='ts-rs002-a02-pg16-20261113-001'
VOLUME='ts-rs002-a02-pg16-data-20261113-001'
NETWORK='ts-rs002-a02-pg16-net-20261113-001'
DATABASE='ts_rs002_a02_lab'
PGUSER='ts_rs002_admin'
ROOT='/var/tmp/ts-rs002-a02-pg16-20261113-001'
IMAGE_LOCK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/image.lock"
SCHEMA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/schema.sql"
EXPECTED_SCHEMA_SHA256='c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721'

status='NONE'
phase='PRECHECK'
result_file=''
fail() {
  local message="$1"
  printf 'BLOCKED: %s\n' "$message" >&2
  if [[ -n "$result_file" ]]; then
    printf 'operation=%s\nattempt=%s\nphase=%s\neffect=%s\nstatus=BLOCKED_OR_INCOMPLETE\n' \
      "$OPERATION" "$ATTEMPT" "$phase" "$status" > "$result_file" || :
  fi
  exit 21
}
trap 'code=$?; if (( code != 0 )) && [[ "$status" != NONE ]]; then printf "NONTERMINAL_PARTIAL_EFFECT operation=%s attempt=%s phase=%s effect=UNKNOWN do_not_retry\n" "$OPERATION" "$ATTEMPT" "$phase" >&2; fi' EXIT

[[ $# == 1 && ( "$1" == '--preflight' || "$1" == '--apply' ) ]] || fail 'exactly --preflight or --apply required'
mode="$1"
[[ -f "$IMAGE_LOCK" && ! -L "$IMAGE_LOCK" ]] || fail 'image lock missing or symlink'
[[ -f "$SCHEMA" && ! -L "$SCHEMA" ]] || fail 'schema missing or symlink'
[[ "$(sha256sum "$SCHEMA" | cut -d' ' -f1)" == "$EXPECTED_SCHEMA_SHA256" ]] || fail 'schema SHA256 mismatch'
IMAGE="$(cat "$IMAGE_LOCK")"
IMAGE="${IMAGE%$'\n'}"
[[ "$IMAGE" =~ ^postgres@sha256:[0-9a-f]{64}$ ]] || fail 'image.lock must contain an immutable fully qualified official digest'
[[ "$(hostname)" == "$HOST" ]] || fail 'different WSL host identity'
[[ "$(docker context show)" == default ]] || fail 'unexpected docker context'
[[ "$(docker version --format '{{.Server.Version}}')" == 29.1.3 ]] || fail 'docker server version mismatch'
[[ "$(docker info --format '{{.OSType}}/{{.Architecture}}')" == linux/x86_64 || "$(docker info --format '{{.OSType}}/{{.Architecture}}')" == linux/amd64 ]] || fail 'docker engine architecture mismatch'
[[ ! -e "$ROOT" && ! -L "$ROOT" ]] || fail 'isolated output root exists'
! docker container inspect "$CONTAINER" >/dev/null 2>&1 || fail 'container name collision'
! docker volume inspect "$VOLUME" >/dev/null 2>&1 || fail 'volume name collision'
! docker network inspect "$NETWORK" >/dev/null 2>&1 || fail 'network name collision'
command -v openssl >/dev/null 2>&1 || fail 'openssl unavailable'
# No database, SQL or network connection is performed in preflight.
if [[ "$mode" == '--preflight' ]]; then
  printf 'PREFLIGHT_PASS operation=%s host=%s container=%s volume=%s network=%s effect=NONE\n' \
    "$OPERATION" "$HOST" "$CONTAINER" "$VOLUME" "$NETWORK"
  exit 0
fi

# Mutations start only here. All writes are under the exclusive root.
phase='WORKSPACE_CREATE'
mkdir -m 700 -- "$ROOT" || fail 'workspace create collision'
status='UNKNOWN'
result_file="$ROOT/attempt-status.txt"
printf 'operation=%s\nattempt=%s\neffect=UNKNOWN\nphase=%s\n' "$OPERATION" "$ATTEMPT" "$phase" > "$result_file"
mkdir -m 700 -- "$ROOT/init" "$ROOT/secrets"
openssl rand -hex 32 > "$ROOT/secrets/admin.pass"
openssl rand -hex 32 > "$ROOT/secrets/observer.pass"
openssl rand -hex 32 > "$ROOT/secrets/writer_a.pass"
openssl rand -hex 32 > "$ROOT/secrets/writer_b.pass"
cp -- "$SCHEMA" "$ROOT/init/01-schema.sql"
{
  printf '%s\n' 'REVOKE CREATE ON SCHEMA public FROM PUBLIC;'
  printf '%s\n' 'CREATE ROLE ts_rs002_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;'
  printf "CREATE ROLE ts_rs002_observer LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat "$ROOT/secrets/observer.pass")"
  printf "CREATE ROLE ts_rs002_writer_a LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat "$ROOT/secrets/writer_a.pass")"
  printf "CREATE ROLE ts_rs002_writer_b LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat "$ROOT/secrets/writer_b.pass")"
  printf '%s\n' 'ALTER SCHEMA ts_r3_global_head_20261107_001 OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.head OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.events OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.receipts OWNER TO ts_rs002_owner;'
  printf '%s\n' 'REVOKE ALL ON SCHEMA ts_r3_global_head_20261107_001 FROM PUBLIC;'
  printf '%s\n' 'REVOKE ALL ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 FROM PUBLIC;'
  printf '%s\n' 'GRANT USAGE ON SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_observer,ts_rs002_writer_a,ts_rs002_writer_b;'
  printf '%s\n' 'GRANT SELECT ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_observer;'
  printf '%s\n' 'GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_writer_a,ts_rs002_writer_b;'
} > "$ROOT/init/02-roles.sql"
chmod 600 "$ROOT/secrets/"*.pass "$ROOT/init/"*.sql

# Pinning is required, including for initial image download.
phase='IMAGE_PULL'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker pull --platform linux/amd64 "$IMAGE" >/dev/null
phase='NETWORK_CREATE'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker network create --internal --label "ts.rs002.operation=$OPERATION" "$NETWORK" >/dev/null
phase='VOLUME_CREATE'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker volume create --label "ts.rs002.operation=$OPERATION" "$VOLUME" >/dev/null
phase='CONTAINER_CREATE'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker container create --name "$CONTAINER" --network "$NETWORK" \
  --label "ts.rs002.operation=$OPERATION" --label "ts.rs002.attempt=$ATTEMPT" \
  --memory 512m --cpus 1 --pids-limit 256 --restart no \
  --mount "type=volume,src=$VOLUME,dst=/var/lib/postgresql/data" \
  --mount "type=bind,src=$ROOT/init,dst=/docker-entrypoint-initdb.d,readonly" \
  --mount "type=bind,src=$ROOT/secrets/admin.pass,dst=/run/secrets/ts-admin-pass,readonly" \
  --env "POSTGRES_USER=$PGUSER" --env "POSTGRES_DB=$DATABASE" \
  --env 'POSTGRES_PASSWORD_FILE=/run/secrets/ts-admin-pass' \
  --env 'POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256' \
  "$IMAGE" >/dev/null
phase='CONTAINER_START'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker container start "$CONTAINER" >/dev/null
phase='STARTED_UNVERIFIED'
printf 'phase=%s\neffect=CONFIRMED_RESOURCE_CREATE\nstatus=PENDING_NATIVE_POSTCONDITIONS\n' "$phase" >> "$result_file"
# No PASS here: a separate, exact native observation must attest genesis,
# roles/ACLs and pg_controldata system_identifier before provisioning PASS.
printf 'STARTED_UNVERIFIED operation=%s attempt=%s container=%s volume=%s network=%s receipt=%s\n' \
  "$OPERATION" "$ATTEMPT" "$CONTAINER" "$VOLUME" "$NETWORK" "$result_file"
