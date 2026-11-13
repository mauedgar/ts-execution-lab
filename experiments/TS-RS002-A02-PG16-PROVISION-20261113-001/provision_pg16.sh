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
# Anonymous volume is allocated atomically by Docker container create, never looked up by user name.
VOLUME_TARGET='/var/lib/postgresql/data'
NETWORK='ts-rs002-a02-pg16-net-20261113-001'
DATABASE='ts_rs002_a02_lab'
PGUSER='ts_rs002_admin'
ROOT='/var/tmp/ts-rs002-a02-pg16-20261113-001'
IMAGE_LOCK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/image.lock"
SCHEMA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/schema.sql"
EXPECTED_SCHEMA_SHA256='c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721'
EXPECTED_IMAGE_LOCK_SHA256='890f66f58c836087d9c6099e4d9d150d0df1b28ab04ecd0547e8118fd3c37c47'
EXPECTED_DOCKER_DAEMON_ID='1219e4b8-5972-4880-8ebd-4fd2498a3e83'
EXPECTED_WSL_UID='1000'
# Only Control can issue and freeze a separate admission. Current candidate is NOT admitted.
EXPECTED_ADMISSION_SHA256='UNBOUND_NO_DISPATCH'

status='NONE'
phase='PRECHECK'
result_file=''
fail() {
  local message="$1"
  printf 'BLOCKED: %s\n' "$message" >&2
  if [[ -n "$result_file" ]]; then
    # Append, never truncate native IDs already observed after a partial effect.
    printf 'phase=%s\neffect=UNKNOWN\nstatus=BLOCKED_OR_INCOMPLETE\n' \
      "$phase" >> "$result_file" || :
  fi
  exit 21
}
trap 'code=$?; if (( code != 0 )) && [[ "$status" != NONE ]]; then printf "NONTERMINAL_PARTIAL_EFFECT operation=%s attempt=%s phase=%s effect=UNKNOWN do_not_retry\n" "$OPERATION" "$ATTEMPT" "$phase" >&2; fi' EXIT

[[ $# == 1 && ( "$1" == '--preflight' || "$1" == '--apply' ) ]] || fail 'exactly --preflight or --apply required'
mode="$1"
[[ -f "$IMAGE_LOCK" && ! -L "$IMAGE_LOCK" ]] || fail 'image lock missing or symlink'
[[ -f "$SCHEMA" && ! -L "$SCHEMA" ]] || fail 'schema missing or symlink'
[[ "$(sha256sum "$SCHEMA" | cut -d' ' -f1)" == "$EXPECTED_SCHEMA_SHA256" ]] || fail 'schema SHA256 mismatch'
[[ "$(sha256sum "$IMAGE_LOCK" | cut -d' ' -f1)" == "$EXPECTED_IMAGE_LOCK_SHA256" ]] || fail 'image lock SHA256 mismatch'
IMAGE="$(cat "$IMAGE_LOCK")"
IMAGE="${IMAGE%$'\n'}"
[[ "$IMAGE" =~ ^postgres@sha256:[0-9a-f]{64}$ ]] || fail 'image.lock must contain an immutable fully qualified official digest'
[[ "$(hostname)" == "$HOST" ]] || fail 'different WSL host identity'
[[ "$(id -u)" == "$EXPECTED_WSL_UID" ]] || fail 'unexpected host UID'
[[ "$(docker context show)" == default ]] || fail 'unexpected docker context'
[[ "$(docker version --format '{{.Server.Version}}')" == 29.1.3 ]] || fail 'docker server version mismatch'
[[ "$(docker info --format '{{.ID}}')" == "$EXPECTED_DOCKER_DAEMON_ID" ]] || fail 'different Docker daemon identity'
[[ "$(docker info --format '{{.OSType}}/{{.Architecture}}')" == linux/x86_64 || "$(docker info --format '{{.OSType}}/{{.Architecture}}')" == linux/amd64 ]] || fail 'docker engine architecture mismatch'
[[ ! -e "$ROOT" && ! -L "$ROOT" ]] || fail 'isolated output root exists'
# List operations fail closed on daemon, permission or provider errors.
containers=$(docker container ls -a --format '{{.Names}}') || fail 'container inventory unavailable'
volumes=$(docker volume ls --format '{{.Name}}') || fail 'volume inventory unavailable'
networks=$(docker network ls --format '{{.Name}}') || fail 'network inventory unavailable'
if grep -Fxq -- "$CONTAINER" <<< "$containers"; then fail 'container collision'; fi
# Existing foreign named volumes are never selected; Docker will allocate a new anonymous volume.
if grep -Fxq -- "$NETWORK" <<< "$networks"; then fail 'network collision'; fi
command -v openssl >/dev/null 2>&1 || fail 'openssl unavailable'
# No database, SQL or network connection is performed in preflight.
if [[ "$mode" == '--preflight' ]]; then
  printf 'PREFLIGHT_PASS operation=%s host=%s container=%s volume_policy=DAEMON_ANONYMOUS_NEW network=%s effect=NONE\n' \
    "$OPERATION" "$HOST" "$CONTAINER" "$NETWORK"
  exit 0
fi

# --apply additionally requires a separately published, exact native Control admission.
# This source candidate is deliberately unadmitted; no caller can bypass the gate.
[[ "$EXPECTED_ADMISSION_SHA256" =~ ^[0-9a-f]{64}$ ]] || fail 'Control admission not yet frozen; no physical dispatch'
ADMISSION_LOCK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/admission.lock"
[[ -f "$ADMISSION_LOCK" && ! -L "$ADMISSION_LOCK" ]] || fail 'missing independent admission artifact'
[[ "$(sha256sum "$ADMISSION_LOCK" | cut -d' ' -f1)" == "$EXPECTED_ADMISSION_SHA256" ]] || fail 'admission artifact hash mismatch'
# Mutations start only here. All writes are under the exclusive root.
phase='WORKSPACE_CREATE'
mkdir -m 700 -- "$ROOT" || fail 'workspace create collision'
status='UNKNOWN'
result_file="$ROOT/attempt-status.txt"
printf 'operation=%s\nattempt=%s\neffect=UNKNOWN\nphase=%s\n' "$OPERATION" "$ATTEMPT" "$phase" > "$result_file"
mkdir -m 755 -- "$ROOT/init"
mkdir -m 700 -- "$ROOT/secrets"
openssl rand -hex 32 > "$ROOT/secrets/admin.pass"
openssl rand -hex 32 > "$ROOT/secrets/observer.pass"
openssl rand -hex 32 > "$ROOT/secrets/writer_a.pass"
openssl rand -hex 32 > "$ROOT/secrets/writer_b.pass"
cp -- "$SCHEMA" "$ROOT/init/01-schema.sql"
# Secrets have host-private ancestors (0700), but need to be accessible
# through each individual read-only Docker bind mount to PostgreSQL uid 999.
chmod 644 "$ROOT/secrets/"*.pass "$ROOT/init/01-schema.sql"
# This file contains NO passwords. It is sourced by postgres's official
# entrypoint and streams generated SQL directly to psql, not to persistent logs.
cat > "$ROOT/init/02-roles.sh" <<'GENESIS'
#!/usr/bin/env bash
set -Eeuo pipefail
{
  printf '%s\n' 'REVOKE ALL ON DATABASE ts_rs002_a02_lab FROM PUBLIC;'
  printf '%s\n' 'REVOKE ALL ON SCHEMA public FROM PUBLIC;'
  printf '%s\n' 'CREATE ROLE ts_rs002_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;'
  printf "CREATE ROLE ts_rs002_observer LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat /run/secrets/observer.pass)"
  printf "CREATE ROLE ts_rs002_writer_a LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat /run/secrets/writer_a.pass)"
  printf "CREATE ROLE ts_rs002_writer_b LOGIN PASSWORD '%s' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;\n" "$(cat /run/secrets/writer_b.pass)"
  printf '%s\n' 'ALTER SCHEMA ts_r3_global_head_20261107_001 OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.head OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.events OWNER TO ts_rs002_owner;'
  printf '%s\n' 'ALTER TABLE ts_r3_global_head_20261107_001.receipts OWNER TO ts_rs002_owner;'
  printf '%s\n' 'REVOKE ALL ON SCHEMA ts_r3_global_head_20261107_001 FROM PUBLIC;'
  printf '%s\n' 'REVOKE ALL ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 FROM PUBLIC;'
  printf '%s\n' 'GRANT CONNECT ON DATABASE ts_rs002_a02_lab TO ts_rs002_observer,ts_rs002_writer_a,ts_rs002_writer_b;'
  printf '%s\n' 'ALTER ROLE ts_rs002_observer SET default_transaction_read_only = on;'
  printf '%s\n' 'GRANT USAGE ON SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_observer,ts_rs002_writer_a,ts_rs002_writer_b;'
  printf '%s\n' 'GRANT SELECT ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_observer;'
  printf '%s\n' 'GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA ts_r3_global_head_20261107_001 TO ts_rs002_writer_a,ts_rs002_writer_b;'
} | psql --no-psqlrc -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
GENESIS
chmod 644 "$ROOT/init/02-roles.sh"

# Pinning is required, including for initial image download.
phase='IMAGE_PULL'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
docker pull --platform linux/amd64 "$IMAGE" >/dev/null
# Pin actual immutable digest; reject a mismatched architecture/minor image.
image_meta=$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "$IMAGE") || fail 'image metadata unavailable'
[[ "$image_meta" == linux/amd64 ]] || fail 'image platform not linux/amd64'
image_env=$(docker image inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$IMAGE") || fail 'image ENV unavailable'
grep -Fxq 'PG_VERSION=16.15-1.pgdg12+2' <<< "$image_env" || fail 'image PG_VERSION mismatch'
phase='NETWORK_CREATE'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
network_id=$(docker network create --internal --label "ts.rs002.operation=$OPERATION" "$NETWORK") || fail 'network create failed'
# Preserve return identity BEFORE any subsequent attestation; absence is UNKNOWN.
printf 'network_returned_id=%s\n' "$network_id" >> "$result_file"
[[ "$network_id" =~ ^[0-9a-f]{64}$ ]] || fail 'new network ID malformed or unknown'
observed_network_id=$(docker network inspect --format '{{.Id}}' "$network_id") || fail 'network native ID not attested'
[[ "$observed_network_id" == "$network_id" ]] || fail 'network native ID mismatch'
printf 'network_id=%s\n' "$network_id" >> "$result_file"
# Docker allocates an anonymous volume WITH the uniquely created container.
# No separate 'docker volume create NAME' can accidentally reuse foreign storage.
phase='CONTAINER_CREATE'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
container_id=$(docker container create --name "$CONTAINER" --network "$network_id" \
  --label "ts.rs002.operation=$OPERATION" --label "ts.rs002.attempt=$ATTEMPT" \
  --memory 512m --cpus 1 --pids-limit 256 --restart no \
  --mount "type=volume,dst=$VOLUME_TARGET,volume-nocopy" \
  --mount "type=bind,src=$ROOT/init,dst=/docker-entrypoint-initdb.d,readonly" \
  --mount "type=bind,src=$ROOT/secrets/admin.pass,dst=/run/secrets/ts-admin-pass,readonly" \
  --mount "type=bind,src=$ROOT/secrets/observer.pass,dst=/run/secrets/observer.pass,readonly" \
  --mount "type=bind,src=$ROOT/secrets/writer_a.pass,dst=/run/secrets/writer_a.pass,readonly" \
  --mount "type=bind,src=$ROOT/secrets/writer_b.pass,dst=/run/secrets/writer_b.pass,readonly" \
  --env "POSTGRES_USER=$PGUSER" --env "POSTGRES_DB=$DATABASE" \
  --env 'POSTGRES_PASSWORD_FILE=/run/secrets/ts-admin-pass' \
  --env 'POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256' \
  "$IMAGE") || fail 'container create failed'
# Preserve return identity BEFORE inspect: a partial-effect failure cannot erase it.
printf 'container_returned_id=%s\n' "$container_id" >> "$result_file"
[[ "$container_id" =~ ^[0-9a-f]{64}$ ]] || fail 'container ID malformed'
printf 'container_id=%s\n' "$container_id" >> "$result_file"
# Only a single daemon-generated anonymous volume at the EXACT PGDATA target is allowed.
volume_mount=$(docker container inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}' "$container_id") || fail 'anonymous PGDATA mount unavailable'
IFS='|' read -r volume_name volume_type volume_rw <<< "$volume_mount"
[[ "$volume_name" =~ ^[0-9a-f]{64}$ && "$volume_type" == volume && "$volume_rw" == true ]] || fail 'PGDATA volume not daemon-created anonymous volume'
printf 'volume_returned_name=%s\n' "$volume_name" >> "$result_file"
volume_driver=$(docker volume inspect --format '{{.Driver}}' "$volume_name") || fail 'anonymous volume native driver unavailable'
[[ "$volume_driver" == local ]] || fail 'anonymous volume driver not local'
printf 'volume_name=%s\nvolume_type=%s\nvolume_driver=%s\n' "$volume_name" "$volume_type" "$volume_driver" >> "$result_file"
# Docker 29.1.3 reports an empty NetworkSettings.NetworkID for a newly
# created but NEVER STARTED container. Do NOT require an attached endpoint yet.
# The exact native network ID is held by HostConfig.NetworkMode before start.
prestart_network_mode=$(docker container inspect --format '{{.HostConfig.NetworkMode}}' "$container_id") || fail 'container configured network unavailable'
[[ "$prestart_network_mode" == "$network_id" ]] || fail 'container configured for foreign network'
printf 'configured_prestart_network_id=%s\n' "$prestart_network_mode" >> "$result_file"
# NetworkSettings.NetworkID must be reattested after start, when Docker
# actually creates the endpoint; see post-start validation below.
phase='CONTAINER_START'
printf 'phase=%s\neffect=UNKNOWN\n' "$phase" >> "$result_file"
# Start by the exact native container ID captured from create, never a mutable name.
started_id=$(docker container start "$container_id") || fail 'container start failed'
printf 'start_returned_id=%s\n' "$started_id" >> "$result_file"
[[ "$started_id" == "$container_id" ]] || fail 'start returned foreign container identity'
attested_id=$(docker container inspect --format '{{.Id}}' "$container_id") || fail 'started container ID unavailable'
[[ "$attested_id" == "$container_id" ]] || fail 'started native ID mismatch'
attested_name=$(docker container inspect --format '{{.Name}}' "$container_id") || fail 'started name unavailable'
[[ "$attested_name" == "/$CONTAINER" ]] || fail 'started container name mismatch'
attested_owner=$(docker container inspect --format '{{index .Config.Labels "ts.rs002.operation"}}' "$container_id") || fail 'started operation label unavailable'
[[ "$attested_owner" == "$OPERATION" ]] || fail 'started foreign operation label'
attested_attempt=$(docker container inspect --format '{{index .Config.Labels "ts.rs002.attempt"}}' "$container_id") || fail 'started attempt label unavailable'
[[ "$attested_attempt" == "$ATTEMPT" ]] || fail 'started foreign attempt label'
attested_network=$(docker container inspect --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' "$container_id") || fail 'started network unavailable'
[[ "$attested_network" == "$network_id" ]] || fail 'started foreign network'
attested_mount=$(docker container inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}|{{.Type}}|{{.RW}}{{end}}{{end}}' "$container_id") || fail 'started PGDATA mount unavailable'
[[ "$attested_mount" == "$volume_name|volume|true" ]] || fail 'started foreign PGDATA mount'
printf 'post_start_attested_id=%s\npost_start_attested_name=%s\npost_start_attested_network=%s\npost_start_attested_volume=%s\n' "$attested_id" "$attested_name" "$attested_network" "$volume_name" >> "$result_file"
container_state=$(docker container inspect --format '{{.State.Status}}' "$container_id") || fail 'container state unreadable'
printf 'container_state=%s\n' "$container_state" >> "$result_file"
[[ "$container_state" == running ]] || fail 'container not running after start'
phase='STARTED_UNVERIFIED'
printf 'phase=%s\neffect=RESOURCE_IDS_CAPTURED_PENDING_PG_GENESIS\nstatus=PENDING_NATIVE_POSTCONDITIONS\n' "$phase" >> "$result_file"
# No PASS here: a separate, exact native observation must attest genesis,
# roles/ACLs and pg_controldata system_identifier before provisioning PASS.
printf 'STARTED_UNVERIFIED operation=%s attempt=%s container=%s volume=%s network=%s receipt=%s\n' \
  "$OPERATION" "$ATTEMPT" "$CONTAINER" "$volume_name" "$NETWORK" "$result_file"
