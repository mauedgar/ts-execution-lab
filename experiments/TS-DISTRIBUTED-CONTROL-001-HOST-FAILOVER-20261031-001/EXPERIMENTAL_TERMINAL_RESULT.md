# TECNOTRON-DISTRIBUTED-CONTROL-001 — DC043 terminal experimental result

**Cutoff:** 2026-10-31 UTC. **Authority:** `EXPERIMENTAL_CONTROL_ONLY`. **Product effect:** NONE. **Terminal:** `PASS_BOUNDARY_REMOTE_ARTIFACT_CROSS_RUNNER_UNKNOWN_RECOVERY / COMPLETE_WITH_LIMITATIONS`. **Architecture-level verdict:** `HOST_INDEPENDENCE_INCOMPLETE` for **live persistent Dolt remote**, not a Product migration or adoption grant.

## Original frozen identity

- Repository: `mauedgar/ts-execution-lab`.
- Run source commit `a0066651aa98d3a75661c172bf207ca6ba7ed6b6` on `experiment/distributed-control-001-host-failover-20261031-001`.
- [Original Actions run #41176626803](https://github.com/mauedgar/ts-execution-lab/actions/runs/41176626803), `run_attempt=1`, terminal workflow conclusion `failure` **EXPECTED** due to intentionally injected ACK loss. Workflow was dispatched once via a scoped branch push; do not rerun.
- Source `host_failover043.py`, Git blob `a77f845fc545c7b729508a4508010f4ff6613870`; prospective `DOD.md` committed before run, no DoD post-hoc repair.
- Identity `TS-DISTRIBUTED-CONTROL-001-HOST-FAILOVER-20261031-001`; original effect `TS-DC043-EXTERNAL-EFFECT-ATTEMPT-001`. Beads 1.3.1 ZIP sha256 `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`, Dolt 2.2.0 ZIP sha256 `1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6`.

## Terminal job evidence

1. **Host A**, job `124465414131`: setup, frozen source check, native Beads graph, UNKNOWN checkpoint, external effect publication all **SUCCESS**. Explicit step `Inject irreversible lost acknowledgement after successful remote publication` **FAILURE** from deliberate `exit 73` at `2026-10-31T06:27:04Z`. Original log marker `TS_DC043_EXPECTED_ACKLOSS_EXIT_73;provider_artifact_published=YES;do_not_retry=YES`. This is the *only* reason the workflow is marked failure; no retry.
2. **Host B**, job `124465492939`, fresh runner: **completed/success**, verified producer failure, exactly one original provider effect artifact, both original artifact downloads and ZIP hashes, native Beads/Dolt reconstruction, original UNKNOWN, native causal join, no re-dispatch and final artifact publication. Original log `TS_DC043_B=PASS_FRESH_HOST_REMOTE_ARTIFACT_UNKNOWN_RECONCILED_NO_REDISPATCH;original_attempt=TS-DC043-EXTERNAL-EFFECT-ATTEMPT-001;redispatch=0;provider_artifact=13033267614;Product=NONE`.
3. Original `NATIVE_BEADS_STORE.tar` SHA256 `67f5d80c1ceff8630e0f8650f0050f5deca9642cf61475409ebc2c767e8c43ba` and original external `EFFECT043.json` SHA256 `0a6c66e096515099f101e36ec33a33f77f3cfef08fd16d1a73bdd67455347776` from producer log, independently checked by consumer program before ANY native close. `provider_redispatch_count=0`.
4. Exact remote artifact original IDs and provider SHA256 ZIP:
   - [Checkpoint #13032887936](https://github.com/mauedgar/ts-execution-lab/actions/runs/41176626803/artifacts/13032887936): `sha256:b67f640694efc766f4e7d993921683b623caf16f2227b7621447fa48e1f9a0fb`, 464966 bytes.
   - [Original provider effect #13033267614](https://github.com/mauedgar/ts-execution-lab/actions/runs/41176626803/artifacts/13033267614): `sha256:dbfe4ca1f40292aa408d55bf7eb58939b1a3e0793cc95aafead264669789f783`, 437 bytes.
   - [Final consumer result #13033191509](https://github.com/mauedgar/ts-execution-lab/actions/runs/41176626803/artifacts/13033191509): `sha256:40d4159db56477b98416a0daf4be33cbc5d0d45fe1dd87a48e031b5b8a59e5b2`, 485465 bytes. Contains original RESULT043.json, final native store TAR, DOD and member SHA256 manifest.
   - All artifact metadata `expired=false`, provider retention to approximately 2026-11-30T06:27Z. Those binary ZIPs are external receipts, **not** permanent repo knowledge or offsite backup.

## What is actually demonstrated

- An **unmodified native Beads/Dolt workgraph** and its prior native history can be reconstructed on a second GitHub Actions runner **without the first runner's workspace or State Kernel**.
- First runner's externally published effect survives its **injected missing acknowledgement**; second runner checks exact identity/receipt from GitHub provider independently and changes native work state only **after** verification.
- `UNKNOWN` did **not** cause redispatch: original attempt was reconciled; no new attempt or duplicate synthetic external publication.
- Native Beads readiness is not treated as Product authorization. The experimental writer is trusted, and all Product gates remain outside the experiment.

## Scope ceiling and blockers

- This is a **remote immutable GitHub Actions artifact** recovery test, **not** a live remote-native Dolt Git/server test, concurrent multiwriter test, replication or stable long-term storage.
- Failure was an injected process/job exit after artifact upload, **not actual physical host disappearance**. Execution is synthetic and the provider effect is one GitHub artifact publication, not a real external business operation or LLM agent.
- Native Beads/Dolt history is **not proven equivalent** to Product `revision/event_count/hash-chain/snapshot HEAD`. Privileged writer bypass of experiment 028, credential fencing, production `UNKNOWN` with opaque providers, read/restore backups and downtime are unresolved.
- No measurable Product simplification yet: `0 bytes` removed; Beads 029 measured a 36,715-byte Kernel source and 12,020-byte adapter as candidate contact surface, not savings.
- Separate Product owner, authority, IR, acceptance, Phase2 and migration grants are required. `#35 OPEN / TASKCYCLE_NOT_INITIALIZED` and Control H6 Attendance without Beads dependency remain unchanged.

## Architectural disposition and next boundary

`GO_EXPERIMENTAL` for bounded cross-runner snapshot recovery and provider-receipt reconciliation. Overall `HOST_INDEPENDENCE_INCOMPLETE` for the stated target because native persistent live remote/writer isolation/backups/cost parity are unverified. Preferred next test is a scoped remote-native Dolt store with a single trusted writer and fresh-client recovery, then isolated restore/outage/UNKNOWN cases. Do not build a replacement ledger or scheduler, import Product authority, mutate the lab's shared `refs/dolt/data`, or automatically dispatch another attempt.

Historical receipts are preserved; no Product repo, #35, State Kernel or TC Core modification was made.
