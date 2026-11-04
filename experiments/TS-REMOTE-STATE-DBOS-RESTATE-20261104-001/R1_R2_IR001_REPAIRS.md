# TS-REMOTE-STATE R1/R2 — IR001 repair candidate, experimental only

**Scope**: No Product writes, no TaskCycle, no Phase 2, no R3 provider provisioning, no historical dispatch or migration. Retain original R1/R2 candidate and run `41874040175` as immutable evidence.

**Exact Product baseline:** `mauedgar/tecnotron-ai:tools@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`, tree `25d1a151d651bb41936c69334fb0b0772ef22519`. The repair lives solely on new lab branch `experiment/ts-remote-state-r1-r2-ir001-repair-20261104-001`, based on lab `28a13ca0ecf8d9d2bee664b78c40a36698400e4b`.

## Independent IR001 source
`mauedgar/ts-execution-transport@29c2210380a99160e3dcdb5f137f1f9d575e48fd:reviews/TS-REMOTE-STATE-R1-R2-IR001-20261104-001/REVIEW_RESULT.md`, verdict `NO_RECOMMEND`, 3 F / 4 A.

## Repairs
- **F001**: mirror the original `FilesystemStateStore.read()` event invariants in experimental `RamStore.verify()`: event kind, bootstrap TaskCycle/first revision, authority and timestamp provenance, nonterminal import, aggregate identity correspondence and exactly replayed state. Negative tests create internally hash-consistent forgeries and verify BOTH frozen Product and PG adapter reject them; original Product is unmodified.
- **F002**: keyed synthetic mutation requires an explicit immutable typed command envelope (operation, expected revision, target, fields and exact authority references). Persist a SHA-256 fingerprint and the original full receipt in the same SQL transaction as state/events. Reused key with different payload, revision or authority raises `MUTATION_IDENTITY_COLLISION`; confirmed matching key returns `{reconciled:true,original}` without a new effect. Do NOT infer authority from a receipt.
- **F003**: acquire global `r1_data FOR UPDATE` row lock **before** receipt lookup. Under `READ COMMITTED` the second same-key client observes the committed original receipt, verifies fingerprint and reconciles, rather than attempting a duplicate insert. Concurrent same-key test asserts exactly one commit and one reconciliation.
- **A001**: supplement differential cases with attempted illegal transitions, postterminal late obligations, missing success guard, and hash-consistent bootstrap forgeries. Exhaustive state-space enumeration not claimed.
- **A002**: test still uses synchronous Product reducer and staging store with one ephemeral PG instance. Explicitly retain `R3_R4_R5_NOT_QUALIFIED`; durable multi-host backup and production schema **cannot** be proved without separate provider boundary. No claim of resolution outside R1/R2 scope.
- **A003**: new CI is read-only, no generated versions, no `git push`, pinned GitHub Actions to inspected immutable commit SHA and checkout by event `github.sha`. Exact `uv.lock`/`package-lock.json` from original final candidate; no mutable branch checkout. Published lab commit/tree and original job receipt determine evidence.
- **A004**: isolated Linux test executes a real two-process DBOS durable workflow with new synthetic workflow ID scoped to this candidate, plus Node pg transaction/rollback against real PostgreSQL16. Python 3.15.2 lock replay and TypeScript pin qualification on Linux + Windows. No notebook/desktop global installs, no production DBOS service claim.

The R1 RAM adapter is **not** the proposed production PostgreSQL backend: it only establishes bounded differential parity for frozen Product trace vectors. The Product's separately filesystem-backed invocation artifact store remains unresolved under later authority. A fresh independent IR002 over the exact repaired commit/tree is required before any Product adoption decision.
