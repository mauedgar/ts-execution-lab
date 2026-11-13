# TS Remote State 002 — PG16 physical gate matrix, NONPRODUCT

Status: PREPARED_NOT_ADMITTED. This manifest is NOT an original physical receipt, a source IR finding waiver, a Product decision or a permission to invoke Docker. Owner TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL.

## Provenance and image (source-level evidence)

The pinned pullable official Docker Registry manifest for `postgres:16.15-bookworm`, `linux/amd64`, is `sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e`. Original Docker Hub manifest page:
https://hub.docker.com/layers/library/postgres/16.15-bookworm/images/sha256-5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e

Documented OCI image environment: `PG_MAJOR=16`, `PG_VERSION=16.15-1.pgdg12+2`, `PGDATA=/var/lib/postgresql/data`. Docker docs for unnamed volumes and `volume-nocopy`:
https://docs.docker.com/engine/storage/volumes/

Prior `efdf07c2...` in PR42 was an **image config/layer identifier**, not an attested registry *manifest* for `docker pull postgres@sha256:...`. It has been replaced; do not silently reuse historical source approvals.

Source CI can verify manifest availability/readability but actual host image identity and daemon state MUST be attested independently at an authorized physical gate. No host image pull is authorized by this document.

## Admission and original effects

- The frozen source runner deliberately contains `EXPECTED_ADMISSION_SHA256=UNBOUND_NO_DISPATCH`. This condition MUST remain unchanged in unadmitted source and cannot be satisfied by an ad-hoc Commander's script or CI fixture.
- Before any physical operation: Control establishes exact authorized notebook identity `DESKTOP-DJLBEQH`, user UID 1000, actual WSL2 Docker daemon ID and server version; binds original Operation, a fresh single ExecutionAttempt (not historical synthetic), immutable runner digest, image manifest, resource allowlist, least-privilege permissions, exclusive workspace and create-only semantics. Verify no foreign effects or UNKNOWN and a qualified carrier/host-bound runner.
- On effect, Docker creates an internal-only network; the exact native ID is recorded. Docker creates a uniquely named container containing a separately allocated, random anonymous PGDATA volume; capture container ID, volume ID/name, mount type, driver, labels, exact network binding and result status. Any partial creation/uncertain return: UNKNOWN; never repair by deleting unknown resources or retrying.
- After container start (not PostgreSQL PASS), independently obtain `pg_controldata` system_identifier, `server_version_num` and native catalog/role/ACL evidence; confirm genesis SQL executed without errors, three expected tables, 19 columns and intended constraints/indexes; verify host/container/volume/exclusive network provenance. Preserve secrets outside GitHub logs.
- Only after create PASS and separate P0 identity read-only admission can P1 independent golden/oracle qualification, P2 single REPEATABLE READ READ ONLY catalog observation and P3 original durable receipts/WEB_INLINE IR occur. Writer effects PA01–PA04 and separate Neon/DBOS persistence require further grants. Product filesystem Kernel remains authoritative and Beta Run 008 blocked.

## Expected observer security assertions (physical gate, not source PASS)

1. `ts_rs002_observer` is LOGIN but NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, NO BYPASSRLS; no role memberships with grant options or implicit owner/writer privileges.
2. On dedicated `ts_rs002_a02_lab`, observer has CONNECT only; `has_database_privilege(observer, database, 'CREATE')` and `TEMP` must be false; PUBLIC CREATE/CONNECT/TEMP revoked on the dedicated database.
3. Observer has schema USAGE but no CREATE on `ts_r3_global_head_20261107_001`, and no CREATE on `public`. No unrestricted SECURITY DEFINER functions or unexpected extension grants.
4. For each of `head`, `events`, `receipts`: observer SELECT=true; INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER=false; membership and `pg_catalog.pg_control_system()` access separately confirmed rather than assumed.
5. Independent read-only credential executes an original negative authorization check where writing, temp object creation and privilege escalation are denied. `default_transaction_read_only=on` is an extra defense in depth, **not** proof of privileges: the role can change session defaults. The real P2 catalog observation must use an explicitly READ ONLY transaction.
6. Separate writer A/B grants are evaluated only in their own later admission; no implicit physical writer operations from source.
7. All queries and receipts are bound to original host+container+volume+PG system_identifier and immutable request IDs; capture no password, DSN or private tokens.

## Source-only vs physical review disposition

PR40 IR001 NO_RECOMMEND 4F/5A, PR41 IR002 NO_RECOMMEND 1F/3A, PR42 IR003 RECOMMEND_BOUNDED_SOURCE_ONLY 0F/4A remain immutable original reviews. This matrix addresses documentation/provenance and freezes *future required checks*; it is not a claim of completed A03/A04 physical checks, and cannot be used to assert full A02 0F0A. Distinct source reviewer must adjudicate whether any actionable source advisory remains. The physical gates and Product acceptance are intentionally separated.
