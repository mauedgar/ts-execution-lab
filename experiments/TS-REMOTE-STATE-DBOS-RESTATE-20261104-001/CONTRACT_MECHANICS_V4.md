# TS Remote State contract mechanics V4 — scoped experimental proof

**Identity:** TS-REMOTE-STATE-CONTRACT-MECHANICS-V4-20261104-001.
**Profile:** OPERATIONAL / synthetic only / Product authority NONE.
**Base:** `mauedgar/ts-execution-lab@8457060682923e5e8fe6b14017f8d890a97acb3a` (the previous 3.15.2 DBOS PASS subject).
**Product source cutoff:** `mauedgar/tecnotron-ai:tools@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`.
**SOT:** docs/SOURCE_OF_TRUTH.md, architecture baseline; State Kernel NARROW / final disposition UNDECIDED.
**Original readonly contract:** src/state-kernel-v0/contracts.js, src/state-kernel-v0/index.js and docs/state-kernel-v0/README.md at that same Product cutoff.

## Design intention

Retain the existing `ExecutionLifecycleCapability` and `TaskCycleLifecycleCapability` boundaries; substitute only physical persistence and execution durability, preferably reusing DBOS and PostgreSQL rather than cloning Kernel Product semantics. The existing Recipe default still uses `createStateKernelCompatibilityBinding` and filesystem artefacts when no explicit provider is injected; real removal requires a separately accepted consumer migration and artifactory decision.

## Exactly scoped hosted synthetic test

New GitHub Actions run on the V4 branch, PostgreSQL 16 ephemeral service, DBOS 3.4.0, Python 3.15.2, all data synthetic:
- DBOS completes a durable workflow then a fresh Python process reuses the same ID without duplicating its completed step.
- PostgreSQL fixture writes four aggregate-shaped state documents and hash-chain events transactionally, reading state in separate processes.
- Two concurrent threads race with the same *global* revision against different aggregate IDs; exactly one commits, the other returns STALE_REVISION, and the audit history remains consistent.
- Synthetic UNKNOWN existing attempt prevents creating a new attempt under the same Operation; rolled-back write leaves no state/audit effect.
- Synthetic events replay into a clean table to reconstruct the same state.

**Strict qualification ceiling:** The Python fixture is **not** the Product transition reducer, authorization validator, TaskCycle semantics, actual Kernel implementation, two physical hosts, true backup/disaster recovery, or live remote managed PostgreSQL. DBOS only qualifies the workflow pieces, PostgreSQL qualifies the transaction pieces. No external provider side-effect 'exactly-once' claim. This pilot does not authorize Product deletion, refactor, migration, new TaskCycle, closure, or changes to historical UNKNOWN fences.

## Ordered next decisions (avoid overlap)

1. Experimental DBOS/PostgreSQL mechanical conformance — verify this original CI run and exact log receipts.
2. Product-owned behavioral equivalence at same frozen source ref — reuse existing validators/TC Core; independent IR and negative case coverage; no new parallel lifecycle machinery.
3. Managed PostgreSQL dual-independent-host and backup/restore/secret custody; must have user-authorized provider credentials and reviewed one-shot operations. No implicit Neon enrollment.
4. Accepted Product candidate for swapping Recipe default consumer and artifact persistence, separately governed Phase 2 and actual effect reconciliation. Preserve old Kernel read-only until final cutover.
5. Remove only the filesystem Kernel implementation after all active consumers, provenance, and exact migration proofs; no replay or cleanup of historical UNKNOWN.

This document is an experiment not an adopted ADR.
