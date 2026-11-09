# TS R3 A10 — Upper LC / TaskCycle Core compatibility when changing State Kernel storage

**Class:** NONPRODUCT_EXPERIMENTAL_BINDING, **Owner:** TS_EXECUTION_ENGINEERING / TS Remote State 002, **decision type:** PROPOSED TECHNICAL ADAPTER. This file does **not** replace the canonical Product SOT, grant Developer acceptance, authorize Product code changes, open a TaskCycle, select an actor, or close any existing Product work.

## Frozen subjects / authority

- Product source of truth: `mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88` (tree `eecf5c4e52b8ca511d45ecebd9495ffb051997ac`).
- Product Upper LC v1: `docs/architecture-knowledge-ownership-baseline.md`, Git blob `330fdc82f75e1126939cd718c1facb28abe00c62`, §16.1: **ADOPT / ADAPT / REUSE semantic dispositions**, not a second state store.
- Product TaskCycle Core v1: `DOD: PASS`, `FROZEN_MAINTENANCE`, not reopened. Upper LC is the policy/control boundary around the existing Core.
- Canonical synchronous JS V0 source: `src/state-kernel-v0/contracts.js` blob `5d2d3a8a24ebc17339675e0c801595956e0cd353`; `index.js` blob `0219b92e5f546407a6060a6dc449865c14c7f144`; `store.js` blob `f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a`.
- Experimental PG16 bridge `ts_global/bridge.py` blob `61be5ce70662a31118f9ffe442d1a03a5e9f195d`. It stores canonical JS state/event bytes, global revision CAS and mutation receipts; its `authority_fingerprint` is a claim, **never** proof that Developer/Control granted authority.
- Local non-Product D7/A003 IR002 had 0/0 LOCAL for 20 Product JS generations/19 exact events, restore, rollback; GHA run `42517094445` with native code. Remote authenticated psycopg remains `BLOCKED_PRECONDITION` and Product cutover `NO_GO`.

## What migrates, what does not

| Contract / owner | Storage replacement disposition | Nonnegotiable preservation rule |
| --- | --- | --- |
| Developer terminal acceptance / Product Control work selection | **PRESERVE EXTERNAL** | Neither SQL data, passing CI, review, nor a receipt grants or selects Product authority. |
| Upper LC lifecycle identity / receipts | **REUSE** | Product work item, responsibility, Operation, ExecutionAttempt, provider run, effect and Git subject remain distinct. No new central identity ledger. |
| Upper LC actor/model/harness | **PRESERVE** | Binding may execute already-admitted mechanics; it cannot create Product actors, gates or acceptance decisions. |
| Upper LC Context, Handoff, Capability/Asset | **REUSE** | Git SOT and action-relative evidence stay with their owners; remote DB is not Product knowledge authority or mandatory context service. |
| Upper LC Feedback / Post-Close | **REUSE** | Observations and CONTROL_DELTA are evidence; next work requires Control selection, not event-store auto-scheduling. |
| TaskCycle Core V1 | **PRESERVE FROZEN** | Four KINDS, statuses, transitions, obligations, revision rules, UNKNOWN reconciliation, authority/evidence checks unchanged. |
| TaskCycle late obligations | **PRESERVE** | Monotonic append only while READY/ACTIVE/BLOCKED and with existing/supplied explicit AUTHORITY reference; pending blocks acceptance/close. |
| TaskCycle bootstrap imports | **PRESERVE** | Only accepted nonterminal historical facts; `historical_events_reconstructed=false`; never fabricate events or terminal history. |
| Storage/serialization | **REPLACE CANDIDATE** | Exact JS bytea state/events and hash chain. One global CAS HEAD and append-only receipt/event transaction in PostgreSQL16. |
| Execution attempt storage effects | **REPLACE BACKEND ONLY** | `NONE`, `CONFIRMED`, `UNKNOWN` remain semantically distinct; uncertain result never retried without same-attempt read-only reconcile. |

**No rule migration is needed.** There is a storage and application-caller migration only. The existing Product semantic validator, authority adjudication and original JS rule engine remain authoritative. Existing accepted historical receipts and TaskCycles are retained, not rewritten to make a new database appear authoritative.

## Proposed storage port, asynchronous and fail-closed

The current `FilesystemStateStore` exposes synchronous `initialize/read/mutate/verify`, and the original `index.js` calls `store.mutate(expectedRevision, callback)` synchronously. A PostgreSQL operation **cannot** be substituted for that function without changing the caller contract.

A bounded **future Product candidate** would introduce a storage-neutral, explicitly asynchronous caller boundary:

1. `await read()` -> exact observed global revision, JS bytes, validated event history and receipts. Verify original JS/Zod semantics and all authority/evidence gates **before** selecting a mutation attempt.
2. Build exactly one domain change in a deterministic **original JS semantic proposal** (not SQL implementing domain transitions), keeping `event-id`, `previous_hash`, `sequence`, `after`, and JS `JSON.stringify` insertion-order bytes, snapshot two-space JSON plus trailing newline.
3. `await apply(mutation_id, expected_revision, previous_event_hash, exact_payload_bytes, exact_event_line, exact_state_bytes, authority_fingerprint)` in a single PostgreSQL transaction: current `head` row locked for CAS, immutable event+receipt written atomically. No extra global authority actor.
4. If `CONFIRMED`, re-read independently and return Product projection. If `NONE_STALE`, fail closed and require new competent deliberate planning; never silently regenerate a mutation ID to retry. If `UNKNOWN`, block successor effects and perform `await reconcile(original_mutation)` through the **same identity** and a separate read-only connection. Missing receipt alone does not certify NONE.
5. Read-only `inspect/obligations/render` must use an explicit async wrapper; the old synchronous `index.js` / CLI callers require a complete inventory and compatibility tests. Do not implement `spawnSync`, unqualified IPC, background scheduler or dual authority as a convenience.
6. SQL driver may verify bytes/CAS/receipt identities and reject malformed input, but MUST NOT decide which TaskCycle transition, Actor action, Phase 2, Developer acceptance or next-work selection is legal.

This port is a design interface; it is not yet installed, callable by Product or accepted for integration.

## Safe migration / rollback (future conditioned Product effect)

1. Reobserve live Product `tools` commit/tree and authoritative filesystem HEAD, confirm current consumer, source and grants. Require independent native backup, exact capture of generation, `state.json`, `events.ndjson`, HEAD checksums, event-chain integrity, and no unreconciled UNKNOWN.
2. Isolated child PostgreSQL scope **shadow only**, no live Product writes. Import exact bytes, compare full state/event hash chain against original JS reader, preserve authority_refs, result_refs, evidence provenance and TaskCycle obligation sets; preserve event ordering and global revision.
3. Quiesce a **single** authoritative writer only by competent Product grant; take a final source checkpoint and reconcile open effects. Test deny when source advances, any hash differs, scope occupied, chronology diverges or import reconstructs historical events.
4. After independent review and exact Developer acceptance + Phase 2 authorization, perform one guarded route switch using a pinned candidate, fencing token/epoch and complete receipt; old filesystem source becomes read-only. Never run simultaneous independent authoritative writers.
5. At loss of ACK, crash, partition or ambiguous switch, freeze further Product mutations until original effect is reconciled by exact identity. A confirmed event is NEVER replayed as a new mutation to achieve symmetry.
6. Rollback only to an isolated create-only filesystem target verified by original JS reader, with original event chain and all confirmed post-cutover mutations captured. Do not switch back to an older divergent snapshot or overwrite immutable generation. No automatic reverse cutover without a fresh guarded competent effect.
7. Only after postconditions: original JS semantic parity across four kinds + acceptance, authority, obligations, bootstrap, post-close, UNKNOWN + remote host/TLS/CAS/ACK/partition evidence, IR and Developer acceptance, may Control recommend canonical Product integration.

## Qualifiable DoD without changing Product

- The real frozen Product JavaScript (three exact blobs) executes deterministic **negative and positive** semantic canaries for: TaskCycle acceptance/closure authority/obligations, UNKNOWN attempt no-retry/reconcile, monotonic late obligation, and bootstrap no fabricated history.
- The test demonstrates that naive replacement of synchronous `store.read()/mutate()` with a Promise-based implementation breaks the original `index.js` contract, so an explicit async adapter/caller change remains a required separate Product acceptance gate.
- Test runs on Node 22 with pinned Zod 4.6.7 in an isolated temporary directory. No Neon, credentials, Product repository writes or Product authority. No re-run of earlier E2/D7 effects.
- Review and eventual acceptance concern this bounded experiment only. **Source PASS does not authorize Product cutover, migration of rules, secret-bearing execution, or reopening frozen TC Core.**
