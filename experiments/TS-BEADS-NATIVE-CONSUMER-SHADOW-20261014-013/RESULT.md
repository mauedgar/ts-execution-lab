# TS — Beads ↔ Tecnotron: native consumer shadow 013

**Date:** 2026-10-14 (America/Argentina/Jujuy)  
**Authority:** NONPRODUCT_EXPERIMENTAL_ONLY. **Product effects:** NONE.  
**Terminal result:** `PASS_NATIVE_READ_ONLY_WITH_LIMITATIONS`; next Product action: NONE.

## Exact qualified evidence

- Product canonical `mauedgar/tecnotron-ai:tools@2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89`, tree `04e57337ac129bd40774d48cf2cfee041f904cfa`. Verified inside native runner via public git `ls-remote`, GitHub Git commit/tree API and `docs/current-state.md` exact text. The real selected historical case is `TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001`, `CLOSED_PASS`, candidate `34ab96c00ca5f8c9c87d69a31371d275eeb5f6d9`. No reopened Product lifecycle.
- Native Beads/Dolt Git remote `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, checked before and after; no `bd dolt push` or other remote mutation.
- Native binary `beads v1.3.1`, Windows archive SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`; fresh GitHub Actions Windows 2022 runner, native `bd bootstrap`, `bd list --all --json`, `bd ready --json`, `bd show producer-avr --json`.
- **Terminal run:** [38511937396](https://github.com/mauedgar/ts-execution-lab/actions/runs/38511937396), workflow source `eb028472c2eb668e0b414db7b30db173a074ffff`, job `115682172063`, `conclusion: success`.
- Verified log: `TS_BEADS013_NATIVE_SHADOW=PASS;product=2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89;dolt=1f72d68797114170a97fee27641858f2e55a4571;records=4;ready=3;closed_synthetic=producer-avr;Product_effect=NONE`.
- Independent final log: `TS_BEADS013_REMOTE_UNCHANGED=PASS`.
- Native artifact `ts-beads-013-native-shadow-receipt`, GitHub artifact ID `11870261279`, archive digest `sha256:5b22926730a99736cbacb1d0e191f4439ee1cae727acc7461e31e390746bb781`, expires `2026-10-21T04:33:08Z`. Logs and this Git report outlive the optional artifact retention.

## Attempt chain and exact repaired failure

1. Run [38511562451](https://github.com/mauedgar/ts-execution-lab/actions/runs/38511562451), source `cc638ab38a4da212a385ae8dc15526ee19942486`: FAILED after native bootstrap. PowerShell `JsonBd` used automatic variable `$Args` as a named parameter, so it invoked `bd` without query arguments; parsing help text produced a JSON error. No Product effects or remote writes.
2. Run [38511705816](https://github.com/mauedgar/ts-execution-lab/actions/runs/38511705816), source `bf187110e25232761da73396549ff2a48c94d860`: FAILED workflow registration (zero jobs) due to replacement-string interpolation corrupting YAML. No workflow execution or Product effects.
3. Run [38511835792](https://github.com/mauedgar/ts-execution-lab/actions/runs/38511835792), source `8f2311e8f9c5d5c34647326bb0c4dcb499a8410f`: FAILED at `BEADS_JSON_MISSING_`, exposing the retained PowerShell automatic `Args` binding bug. Native bootstrap succeeded; no read result or remote write.
4. Run [38511937396](https://github.com/mauedgar/ts-execution-lab/actions/runs/38511937396), source `eb028472c2eb668e0b414db7b30db173a074ffff`: PASS after adopting the existing historical `$Items` parameter binding. Exactly one new qualified terminal result; prior attempts preserved.

No blind retry of an effectful Product attempt. Workflows were read-only and distinct GitHub run IDs. All experimental intermediate commits are retained.

## Interpretation: maximize Beads while retiring duplicate mechanisms

**Qualified now:** native GitHub-hosted Dolt persistence can be bootstrapped by a fresh independent consumer; it recovered four prior synthetic obligations and computed three ready. The prior missing-ACK synthetic handoff remained closed and excluded from ready; original Product TaskCycle independently remained closed. This makes Beads credible as the *operational index* for agent work, dependencies, discovery and allocation at existing authorized Control checkpoints.

**Not yet qualified:** automatic admission of a Product TaskCycle, exact lifecycle mutations/expected-revision CAS, authority/evidence binding, ExecutionAttempt identity and `NONE/CONFIRMED/UNKNOWN`, no-blind-retry after arbitrary provider failures, autonomous multi-agent Product execution or backup/DR. Observed native Beads operational `closed` and `ready` are not Product lifecycle evidence. This native run is read-only, not a Product-backed Beads query or a lifecycle backend conformance test.

**Current Product code still present:** `src-typescript/operational-spine-v0/recipe-invocation.ts` uses default `createStateKernelCompatibilityBinding`, while existing `executionLifecycle` and `taskcycleLifecycle` capability ports allow a non-Kernel provider. `State Kernel` final physical disposition remains `UNDECIDED`. Beads-native durable issues/events/metadata and custom statuses are a promising *single operational storage backend*, but the exact Product invariants are not natively guaranteed by ordinary `bd ready`/`bd claim`. Do not retain two mutable owners of the same lifecycle.

## Next proposed experiment (not Product authorization)

**014 — Beads-backed lifecycle parity in an isolated synthetic laboratory:** implement only a test double of Tecnotron's *existing* `ExecutionLifecycleCapability` and `TaskCycleLifecycleCapability`, backed by native Beads and immutable Git receipt refs. Exercise the exact original-attempt identity, lifecycle legal transitions, metadata authority refs, expected-revision rejection, durable audit and independent readback, `UNKNOWN` reconciliation/no-retry, duplicates, conflicts and terminal close. Verify native Beads capabilities versus Product-specific validation, rather than renaming kernel APIs or introducing an orchestrator. Prefer an existing adapter port, reuse existing CI execution and a disposable Dolt store; no shared `refs/dolt/data` writes, Product TaskCycles or Product source changes. Record any unproven invariant as `NOT_QUALIFIED`.

If these equivalences pass, propose a *replacement*, not parallel coexistence, for the State Kernel physical persistence implementation. Retain Git Product decisions, immutable candidates/reviews/receipts, Developer authority and Upper LC, without making Beads an independent semantic authority. Physical removal/integration still requires competent Product Control selection and grant.
