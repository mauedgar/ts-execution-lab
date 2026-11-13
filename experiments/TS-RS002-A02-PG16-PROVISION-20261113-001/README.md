# TS-RS002 A02 PG16 — isolated provisioning candidate (NONPRODUCT)

Status: SOURCE_REPAIR_003_NOT_ADMITTED; original PR40 IR001 NO_RECOMMEND 4F/5A and PR41 IR002 NO_RECOMMEND 1F/3A preserved unmodified. Owner: TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL. This branch does not grant physical execution, Product acceptance, Kernel replacement or Beta Run 008.

## Exact frozen subject
- Repository: mauedgar/ts-execution-lab; base main 7d1705fc08b02ae91a2981bfc82bea24386fddc3.
- Proposed Operation: TS-RS002-A02-PG16-PROVISION-20261113-001.
- Proposed, NOT DISPATCHED attempt: TS-RS002-A02-PG16-PROVISION-A001.
- Notebook native host: DESKTOP-DJLBEQH; WSL Ubuntu-24.04; Docker 29.1.3 linux/amd64.
- Container: ts-rs002-a02-pg16-20261113-001.
- Volume policy: a newly generated Docker anonymous volume allocated WITH the allowlisted container creation, mounted solely at /var/lib/postgresql/data; native random volume name captured immediately after container creation, no named-volume reuse or `docker volume create`.
- Network: ts-rs002-a02-pg16-net-20261113-001 (internal; no published ports).
- Database: ts_rs002_a02_lab.
- Private WSL workspace: /var/tmp/ts-rs002-a02-pg16-20261113-001.
- Pinned immutable amd64 image: see image.lock (16.15/bookworm per original Docker Hub manifest; independently reattest before dispatch).
- Schema: schema.sql exact Git blob 3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0, original TS-R3 source (not Product).
- Script: provision_pg16.sh, source blob a8fb4f5597d3511239f5ffbd8bc91118aaea6ca0, SHA-256 4299dfec98858b20e6d051a465ffcd3c6b33fa82eb45759002d5814b69a24598.
- Lock blob: 2c9b4759cb1f66bd12a1f5caa56c838541dd85ec.
- Negative tests blob: b48e5927430352b420c76907b86693297c9eb55e, SHA256 8a8afd13ea30c3d304bd199985747e8047ac39dc4910136b572bfac2a28d22cf.

## Strict mode and evidence
- --preflight: checks immutable image syntax, original schema hash, WSL hostname/UID, Docker daemon identity, exclusive root/container/network name absence and native volume inventory availability; anonymous volume cannot preexist because its identity is allocated only on `container create`; no Docker mutation. No DB connections or Docker mutations.
- --apply: NOT ADMITTED (UNBOUND_NO_DISPATCH); create-only local secrets and startup SQL; pinned image pull; isolated native-ID-pinned Docker network and container with new anonymous volume. Never cleans up, replaces, publishes port, touches existing clusters/Neon, or retries.
- If any operation after workspace creation fails, effect is UNKNOWN until reconciled. Successful startup is STARTED_UNVERIFIED, not PASS. Independent provider-native postconditions are still necessary (container/network/volume IDs, actual PG16 system identifier, role/genesis/ACL, independent read-only observer).
- Negative controls (synthetic): prior PR41 CI 10/10 blocking tests PASS; PR42 has 10 negatives + one fake-positive and four new simulated partial-failure stages/one fake started-unverified case awaiting original Actions CI. No physical Docker calls are present in these tests. Not a real notebook test, independent IR or physical admission.
- MAT-XFORM v1 source is available in ts-execution-lab at main@7d1705f, but a qualified installed extractor and carrier on the notebook remain UNVERIFIED. Never use Commander for semantic repository exploration, file generation, unqualified extraction or retry.
- Prior host precheck: mauedgar/ts-execution-transport@3242a2be3515d04cd5f1b82c73928439e5dfa0a2:receipts/TS-RS002-A02-PG16-PRECHECK-20261113-001/ORIGINAL.md.
- Only after transport qualification, independent WEB_INLINE review, exact runnable input/hash, host reobservation and a competent admission may a distinct frozen actual physical ExecutionAttempt be dispatched once.
- Subsequent P0 read-only admission, P1 oracle, P2 physical observer, P3 original receipt and PA01–PA04 are independent gates.

## Independent IR001 disposition and repair boundary
Original PR40 WEB_INLINE IR001 terminal NO_RECOMMEND, 4 findings/5 advisories, original byte-identical Git Transport commit c92141110bfeacac47b131d9341f45a2225bd3b4. This is a NEW distinct candidate, not an IR retry. F01 init/secret path permissions now include an entrypoint shell that streams credentials to psql without persistent password SQL; F02 fail-closed Docker inventory; F03 exact WSL UID 1000, daemon ID 1219e4b8-5972-4880-8ebd-4fd2498a3e83 and externally frozen admission hash (UNBOUND by default); F04 capture native resource identifiers, retain UNKNOWN until PG genesis attested. A01 image metadata must match linux/amd64 and PG_VERSION 16.15 after pull, but original registry digest provenance still independently qualified. A02 removes persisted role passwords; host secret parent remains mode0700. A03 read-only ACL must still undergo native independent physical verification; A04 10 source negatives and 1 fake-positive do not replace physical fault injection; new source-only fault_injection_tests.sh adds four partial-failure mock stages to preserve IDs/UNKNOWN. A05 README blobs corrected. NO physical actions, no new source acceptance, no admission lock, no Product effect.

## IR002 disposition (new distinct repair 003)
Original PR41 WEB_INLINE IR002 is terminal NO_RECOMMEND/1F/3A, review Git blob 73cbab555165635e83fe2d281579681ccd9ef519, native byte-identical Git Transport commit bc14067f14b0edae345ff41c7475be75c876eca8. IR002 F01 high: Docker named volume create may silently reuse an existing name after a race. This repair changes to Docker daemon-allocated anonymous PGDATA volume at container-create time; attached new random volume name, local driver and exactly one matching mount are captured/validated as native postconditions. The network attachment uses the exact returned network ID instead of the potentially ambiguous name. The partial-effect failure recorder now APPENDS failure/effect status to the receipt, not clobbering earlier native IDs. The workflow adds hermetic fake-Docker fault injection for stages network_create, container_create, volume_attest, container_start and a fake STARTED_UNVERIFIED; no actual database/provision effects. IR002 A01/A03 remain physical admission and read-only P0/P1/P2 gates, not source FAIL-closures. This third candidate requires its own native CI and distinct WEB_INLINE IR003; 0/0 cannot be asserted in advance.
