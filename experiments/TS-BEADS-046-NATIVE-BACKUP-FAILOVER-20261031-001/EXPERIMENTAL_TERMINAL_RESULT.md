# TS-BEADS-046 — Terminal original two-host nonterminal native Dolt backup recovery

**Date:** 2026-10-31. **Authority:** EXPERIMENTAL_CONTROL_ONLY. **Product effect:** NONE. **Disposition:** `PASS_REMOTE_NATIVE_BACKUP_NONTERMINAL_HOST_FAILOVER_WITH_LIMITATIONS`. **Live shared remote SQL:** `NOT_TESTED / BLOCKED_EXTERNAL_ENDPOINT`.

## I. Original frozen execution and verified identities

- Operation: `TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001`.
- Producer ExecutionAttempt: `TS-BEADS-046-A-ATTEMPT-001`.
- Consumer ExecutionAttempt: `TS-BEADS-046-B-ATTEMPT-001`.
- Original Git subject: `mauedgar/ts-execution-lab@2495310245468bd4cf1bd1865624ba5c0fb8ee28`, tree `60c2bcf34befcbfb4117e4dfd0b8fcb19c4ecae7`, branch `experiment/beads-046-native-backup-failover-20261031-001`.
- Frozen source: `experiments/TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001/native046.py`, Git blob `47921fceae8ad93760b912224afd8c4d9cf70a99`.
- Frozen DoD: `experiments/TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001/DOD.md`, Git blob `1eeb45cd800be02b980c9eda0de0a1331689bf5f`.
- Original GitHub Actions run: https://github.com/mauedgar/ts-execution-lab/actions/runs/41210661485, `run_attempt=1`, `completed/success`. Distinct producer runner job `124564750003`, distinct consumer runner job `124564810508`, both `completed/success`.
- A original provider artifact: https://github.com/mauedgar/ts-execution-lab/actions/runs/41210661485/artifacts/13046092435 ; ZIP SHA-256 `677b20585c256235f4b6d2ca52180e308e251a9c1066fedd047ca0bcd52d9e55`, original RESULT046_A.json SHA-256 `381392fd37fb3bab6ae97fcebb6cfa43294d51ac0f4d9e1d7cb6ba18c645404c`, original native BACKUP046.tar.gz SHA-256 `5fd9bb304c5183b8c9c70e188b5184d42cdd484d1d04a622e906282910e4a8bd`.
- B original provider artifact: https://github.com/mauedgar/ts-execution-lab/actions/runs/41210661485/artifacts/13046207133 ; ZIP SHA-256 `8541f76fd4d7b646be8043bc011f3fa7a3ab259c6585c94eba2f731f4c001031`, original RESULT046_B.json SHA-256 `747d86632d6a1e6efbda143264a587913b8f1054e418b8da4a5cffe00e45a2b6`.
- Both GitHub ZIP hashes independently matched the provider-declared digests. Both original internal SHA256 manifests matched every named file. Original native backup TAR contains Dolt backup `manifest` and `.darc` data, not merely JSONL or a transplanted Kernel folder. Artifact retention is finite, expires approximately 2026-11-30 14:33 UTC; **not a permanent operational SOT**.

## II. What actually passed

- Host A, fresh GitHub Actions runner with fresh Git workspace and no remote: native Beads 1.3.1, five native issues, dependencies `preflight → alpha/beta → join → parent`. It closed preflight and Alpha, left Beta `in_progress` with Join and Parent blocked. `15/15 PASS` original checks; no Provider re-dispatch.
- Host A used native `bd backup init` + `bd backup sync`, not a reimplementation of Dolt backup, and published the remote GitHub Actions artifact.
- Host B ran on a separate fresh GitHub-hosted runner after A job finished. Its workspace lacked A's original `.beads` directory or Kernel. It downloaded the immutable original A artifact, verified manifest and exact run identity, initialized a fresh native Beads store, then `bd backup restore --force` from the native Dolt backup.
- Host B verified restored Alpha terminal, Beta in progress, Join and Parent still blocked, the intact external provider witness and native history. It closed Beta, then Join and Parent only as each became native `ready`. All five issues closed, final `ready=[]`. `28/28 PASS` original checks; no provider retry.
- Original prior provider witness read-only: 045 run `41177022889`, Git subject `aae4dabd9c2b6d37a24bba896d2eaa2199533287`, artifact `13032823741`, ZIP SHA256 `07b70ea4902d4bfec9efdda08e939b3d753287a2d2b74c6a7e4fe93f38ee33f4`. This witness **was not** claimed to be the synthetic Beta effect or a true UNKNOWN reconciliation.
- Existing shared lab `refs/dolt/data` was reobserved unchanged at `1f72d68797114170a97fee27641858f2e55a4571`. Product SOT `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` unchanged at observation; no Product writes, grants, Beta Control, #35, FitFlow, Kernel or real agent actions.

## III. Precise capability decision and remaining blockers

| Goal | Current evidence | Decision |
| --- | --- | --- |
| Native workgraph/dependencies without State Kernel | 042 (real parallel synthetic workers), 045 (native server), 046 (two-host backup recovery) | GO_EXPERIMENTAL in laboratory |
| Two independent hosts with original nonterminal state recovered after source host ends | 046 A/B PASS, original provider artifacts verified | GO_EXPERIMENTAL for COLD RESTORE ONLY |
| Read-only bootstrap from already published native GitHub Dolt ref by two hosts | Separate DC044 original run `41177310449` PASS, subject scoped read-only | Qualified separately, no mutation |
| Live mutable shared SQL state from two hosts on an independent durable Dolt primary | No endpoint/TLS scoped credentials provisioned | NOT_TESTED / BLOCKED_EXTERNAL_ENDPOINT |
| Host A forcibly crashes with in-flight provider UNKNOWN; B reconciles without replay | No actual in-flight provider effect tested in 046 | NOT_TESTED |
| Permanent backup, RPO/RTO, restore under network partition, credential revocation and writer bypass 028 | No durable infrastructure; artifact retention 30 days | INCOMPLETE |
| Delete/adopt State Kernel/adapter/Recipe code in Product | Product 036/045 read-only footprint 85,014 bytes for three classes, actual deletions 0 | NO automatic deletion, requires Product authority |

## IV. Next competent dependency

To satisfy the original **live remote SQL** host independence goal, independently provision a durable isolated Dolt SQL primary with verified TLS/private-network transport, distinct least-privileged credentials and provider-managed secret storage for at least two fresh clients. A paid infrastructure commitment and persistent public SQL exposure must not be inferred from an experimental grant.

Then separately freeze a distinct subject/DoD and one `ExecutionAttempt` to prove simultaneous read/write from two physically distinct runners, A loss, B recovery, authoritative original provider receipt reconciliation, alternate-write denial, backup/restore to third environment and RPO/RTO. Reuse native Beads/Dolt plus GitHub/Transport, no homegrown Kernel/ledger/scheduler.

Without an authorized endpoint, return `BLOCKED_EXTERNAL_ENDPOINT` for live SQL interhost, **not** another synthetic retry. Research on capacity absorption may continue read-only; no Product lifecycle is altered. 046 is terminal, never re-dispatch.
