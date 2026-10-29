# TS Beads 033 — B-first provider-native identity result

**Authority:** EXPERIMENTAL_CONTROL_ONLY; no Product acceptance, TaskCycle transition, independent review or Phase 2.
**Disposition:** PASS_REAL_PROVIDER_RUN_AND_ARTIFACT_IDENTITY; UNKNOWN_RECOVERY_NOT_QUALIFIED.

## Original exact provider attempt (do not replay)

- Operation: TS-BEADS-033-PROVIDER-20261029-001
- ExecutionAttempt: TS-BEADS-033-PROVIDER-20261029-001/ATTEMPT-001
- Provider: GitHub Actions
- Source: mauedgar/ts-execution-lab@eebf8e72b83df5aed61416ffc0fa81e84fdf55ea
- Workflow: TS Beads 033 External Provider Identity
- Native run: 40930288498; run_attempt: 1
- Job: 123646594227
- Terminal: completed/success
- Native artifact ID: 12921817863
- Native artifact name: ts-beads-033-provider-attempt-001
- Artifact ZIP size: 477 bytes
- Provider ZIP digest: sha256:329d05a218ea04dd740ab1579aed31d00a3f110700670e4d380993a0bde98dc6
- Expiration reported by GitHub: 2026-11-05T18:23:12Z
- Request hash from original job log: 350fb2c516c5ae94cf34cac7c38f5ea10ef11e3d715bf35826dadbce25dfdfe2
- Receipt subject: mauedgar/ts-execution-lab@eebf8e72b83df5aed61416ffc0fa81e84fdf55ea
- Provider run, job, upload step and provider artifact metadata were independently acquired by exact IDs after the action was terminal.
- No second dispatch, rerun or provider artifact write was requested.

## What was qualified

The actual GitHub provider performed one externally durable artifact upload. Its native run/job/artifact metadata and logged source/attempt/request identifiers correlate, and the artifact record exists independently from the original job output.

The consumer did not rely on an initial synchronous ACK as its authoritative success signal: it later joined via provider-native results. This is a **client-ACK-discard** observation, NOT a demonstrated network outage or loss of an actual provider ACK. The artifact ZIP's internal contents were not independently downloaded and rehashed in this verdict, so claims of full byte-for-byte original receipt verification remain open.

## Open gates

1. Actual lost ACK or provider timeout under a controlled real failure; reconcile unchanged effect without dispatch duplication.
2. Store and recover the precise provider identity as an experimental Beads ExecutionAttempt after restart, with fail-closed UNKNOWN guard and no privileged fixture bypass.
3. Exclusive causal writer boundary under alternate native privileged bd/Dolt mutation.
4. Capability-level equivalence to Product requirements, without requiring a new Kernel architecture.
5. Product adoption, acceptance, integration and Kernel retirement.

## Architecture principle

Prefer **B-first capabilities**, not copying Kernel internals. Candidate: native Beads graph/history for scoped lifecycle state + authoritative GitHub provider-native run/artifact evidence + Control-owned authority and reconciliation. Retain explicit no-retry, correlation, causal and effect-state safeguards. Do not add a duplicate state owner by default.

**Product:** frozen read-only at tools@d4154bd43f26515c39a41be974e462a0c7406a2d.
**Shared Dolt:** frozen at refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571.
**Product effects:** NONE. **Shared Dolt effects:** NONE.
