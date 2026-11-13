# TS Remote State 002 — exact existing Docker container B001 (NONPRODUCT)

**Status: SOURCE_CANDIDATE_NOT_ADMITTED / PHYSICAL_EFFECT_NONE / Product_effect NONE.** Source owner TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL. No new Product actor, gate, scheduler or Kernel state. This laboratory source may not execute physical Docker until a distinct independent source IR, bounded physical admission IR, competent Control/Developer grant, delivery verification and exact native preflight.

## Why this exists

The original one-time PostgreSQL 16 provisioning `TS-RS002-A02-PG16-PROVISION-20261113-001 / A001` is **terminal BLOCKED_PARTIAL_CONFIRMED / NONREPLAYABLE**. It created the original exclusive workspace and image cache, isolated network, container and anonymous PGDATA volume, but never ran `docker container start` or SQL. The original source required an attached NetworkID before Docker start; actual Docker returned empty until start. Never re-dispatch A001, clean up or re-create its resources.

Original native provider reconciliation: `mauedgar/ts-execution-transport@044b7554bce5093f8e21e52321264c18b8308be0:receipts/TS-RS002-A02-PG16-A001-PARTIAL-RECONCILIATION-20261113-001/ORIGINAL.md`. The empirical source fix was independently approved and integrated in `mauedgar/ts-execution-lab:main@b4a1426fb4d89a48e99ba710ca7b6319a4f25d38` via PR46 IR007 0F/0A SOURCE, but **that original provisioning runner remains unbound and cannot be used to resume A001**.

## Distinct proposed B001 operation, fixed write-set

Operation `TS-RS002-A02-PG16-START-EXISTING-20261113-001`, separate attempt `TS-RS002-A02-PG16-START-EXISTING-B001`. This candidate is NOT a replay or retry of A001, even though it explicitly references the same existing container.

Exactly one potentially allowed Docker mutation after admission: `docker container start 5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88`, by original immutable native ID, not by name. No new `docker pull`, container/network/volume create, stop, removal, rename, cleanup or foreign resource touch. The only additionally writable location is new create-only isolated B001 receipt root `/var/tmp/ts-rs002-a02-pg16-start-existing-20261113-001`, mode0700. Original A001 workspace and receipt remain unchanged. No original A001 exit-code inference.

Frozen original resources:
- Physical notebook `DESKTOP-DJLBEQH`, WSL Ubuntu24.04 UID1000, Docker default context Engine29.1.3 and daemon ID `1219e4b8-5972-4880-8ebd-4fd2498a3e83`.
- Container ID `5ce2b0833fa7ab04eac1b0c78e51ead0ed7c5e1dc2aede5621dba397b3c20d88`, original operation/attempt labels A001, state `created`, never started; image official postgres16.15 Bookworm linux/amd64 pinned manifest `sha256:5983db9a9c6ad225a48a46cfe2e03e6680b1826662befd0465eb05b34cb1c64e`.
- Internal network native ID `6c94a1fa2e3854335cdbb4b646439e8a03d4f9c3301b7a65b05a467856f5cc35`. Before start `HostConfig.NetworkMode` is exactly that ID, but `NetworkSettings.NetworkID` may be empty. Require exact runtime `NetworkSettings.NetworkID` only AFTER start.
- Anonymous PGDATA volume name `e0f82fa682d2559142b6d90e0c9d23aec384728b2ec618ee3344faa1fa3da899`, driver local, exact mount. No named-volume reuse or Docker automatic cleanup.
- Original root `/var/tmp/ts-rs002-a02-pg16-20261113-001`, DAC `0700` UID1000, private secrets root DAC `0700`, host generated secret files `0644` and mounted individually read-only for PostgreSQL uid. Script only checks metadata and never reads/discloses passwords. Original fixed `schema.sql` SHA256 `c1f8c85b911ef8b04585321448bc823c17c92f531cbdb7b62236082026b3b721`, original generated `init/02-roles.sh` SHA256 `67737d584aeeb167ec84c70fef2437d71f11fac10e77e92d989e4418add3f2cd` and DAC `644:1000:1000`, both hash/DAC independently read-only observed on notebook.

## Source controls and evidence

- `--preflight`: bounded read-only by exact native IDs. Verifies actual original Docker resource state/labels/OCI/network/volume/DAC and no B001 result directory collision. Does not create a receipt root, mutate Docker or inspect secret contents. Fail closed if original resources were started, changed, removed, relabeled or reconfigured.
- `--start-existing`: strictly denies by default via `EXPECTED_ADMISSION_SHA256=UNBOUND_NO_DISPATCH`. A future Control-bound source copy must verify SHA-256 of a frozen `admission.lock`, parse exact v1 contract semantics, original resource IDs, responsible actor, original A001 and distinct B001 operation/attempt, distinct source/physical 0F/0A gates, Product NONE, NO_GO Kernel and Beta Run008. A hash by itself is insufficient authority, and these string assertions do not replace an external competent Control decision.
- After preflight+admission, creates only a private B001 result directory and a create-only original receipt; then issues exactly ONE `docker container start` by captured original ID, records returned identity, and independently checks original labels, network native ID, PGDATA volume and `running` state. Any uncertain outcome maps to `UNKNOWN`; preserve original attempt and new receipt, no blind retry. Even `STARTED_UNVERIFIED` is NOT PostgreSQL genesis PASS.
- GitHub-hosted CI `fake_docker_tests.sh` is the only synthetic execution surface; `GITHUB_ACTIONS=true` and fake Docker/host tools are mandatory, temporary roots only. Tests cover exact-ID-only preflight, UNBOUND physical denial, foreign daemon/status/op/network/volume, four partial start failures and one fake STARTED_UNVERIFIED. No real Docker/SQL.
- The previously observed private OneDrive Business + native WSL SHA256 delivery method has only a bounded, historical NONPRODUCT qualification. No B001 runner/lock has been delivered, installed, executed or admitted as of this source candidate. No MAT-XFORM TypeScript extractor qualification is inferred from a transport receipt.

## Next independent physical gates

First source candidate must obtain native CI and independently reviewed `0F/0 actionable SOURCE A`. Competent Control may decide to integrate ONLY the experimental source (not Product). Then separately freeze the exact derived bound runner and admission.lock, verify no changes to original resources, qualify/create-only transport and independent native hash, obtain a distinct WEB_INLINE physical admission `0F/0A` and Control decision. Only then single original B001 dispatch.

After start, independent P0/P1 inspection must obtain native Docker running + exact IDs, PostgreSQL server 16.15 `system_identifier`, original three tables/19 columns, owner/observer/writer role ACL and secret-permission denial evidence; P2 authenticated read-only observer negative tests and P3 original durable WEB_INLINE IR follow as distinct grants. PA01–PA04 two-host/ACK/restart/Neon/DBOS later; no Product Kernel replacement or Beta Run008 grant from this workflow.

Frozen separate proposal: `mauedgar/ts-execution-transport@41f8923eba15bdd9c38b456d77867fb61116244d:candidates/TS-RS002-A02-PG16-EXISTING-CONTAINER-START-20261113-001/CONTRACT.md`. Scope authority is nonProduct and conditional.
