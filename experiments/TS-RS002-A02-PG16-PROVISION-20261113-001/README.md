# TS-RS002 A02 PG16 — isolated provisioning candidate (NONPRODUCT)

Status: SOURCE_CANDIDATE_NOT_ADMITTED. Owner: TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL. This branch does not grant physical execution, Product acceptance, Kernel replacement or Beta Run 008.

## Exact frozen subject
- Repository: mauedgar/ts-execution-lab; base main 7d1705fc08b02ae91a2981bfc82bea24386fddc3.
- Proposed Operation: TS-RS002-A02-PG16-PROVISION-20261113-001.
- Proposed, NOT DISPATCHED attempt: TS-RS002-A02-PG16-PROVISION-A001.
- Notebook native host: DESKTOP-DJLBEQH; WSL Ubuntu-24.04; Docker 29.1.3 linux/amd64.
- Container: ts-rs002-a02-pg16-20261113-001.
- Volume: ts-rs002-a02-pg16-data-20261113-001.
- Network: ts-rs002-a02-pg16-net-20261113-001 (internal; no published ports).
- Database: ts_rs002_a02_lab.
- Private WSL workspace: /var/tmp/ts-rs002-a02-pg16-20261113-001.
- Pinned immutable amd64 image: see image.lock (16.15/bookworm per original Docker Hub manifest; independently reattest before dispatch).
- Schema: schema.sql exact Git blob 3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0, original TS-R3 source (not Product).
- Script: provision_pg16.sh, source blob a3b07eabfd82e0173fa42b7276d47a94fc2b7628, SHA-256 eb6e688edee625e00e90c07cddc7e7d121adce5e29518325ff6b7d75daff7f55.
- Lock blob: 2c9b4759cb1f66bd12a1f5caa56c838541dd85ec.
- Negative tests blob: 9ef2cfefd81dd709ae549a0f9ee49167313423a7.

## Strict mode and evidence
- --preflight: checks immutable image syntax, original schema hash, WSL hostname, Docker identity, exclusive root/container/volume/network absence, and local OpenSSL. No DB connections or Docker mutations.
- --apply: NOT ADMITTED; create-only local secrets and startup SQL; pinned image pull; isolated Docker network/volume/container. Never cleans up, replaces, publishes port, touches existing clusters/Neon, or retries.
- If any operation after workspace creation fails, effect is UNKNOWN until reconciled. Successful startup is STARTED_UNVERIFIED, not PASS. Independent provider-native postconditions are still necessary (container/network/volume IDs, actual PG16 system identifier, role/genesis/ACL, independent read-only observer).
- Negative controls (synthetic): Bash syntax PASS; 7/7 source-level blocking tests PASS. Not a real notebook test, independent IR or physical admission.
- MAT-XFORM v1 source is available in ts-execution-lab at main@7d1705f, but a qualified installed extractor and carrier on the notebook remain UNVERIFIED. Never use Commander for semantic repository exploration, file generation, unqualified extraction or retry.
- Prior host precheck: mauedgar/ts-execution-transport@3242a2be3515d04cd5f1b82c73928439e5dfa0a2:receipts/TS-RS002-A02-PG16-PRECHECK-20261113-001/ORIGINAL.md.
- Only after transport qualification, independent WEB_INLINE review, exact runnable input/hash, host reobservation and a competent admission may a distinct frozen actual physical ExecutionAttempt be dispatched once.
- Subsequent P0 read-only admission, P1 oracle, P2 physical observer, P3 original receipt and PA01–PA04 are independent gates.
