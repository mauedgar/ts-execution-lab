# TS Beads-first architecture — experimental hypotheses after 019 (020)

**Class:** NONPRODUCT_EXPERIMENTAL_RESEARCH / PROPOSAL_NOT_ADOPTED  
**Cutoff read-only Product:** `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`.  
**SOT remains the competent current Product authority:** `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.

This document deliberately treats the **existing implementation and lifecycle ports as changeable design inputs**, not timeless architecture laws. No historical Product receipt/acceptance/TaskCycle/IR status is rewritten by that permission; only competent later Product decisions could adopt a proposal.

## Thesis

A *Beads-first* Tecnotron would prefer native Dolt/Beads durable issues, `ready`/dependency graph, CAS by issue, native grouped atomic batches and event history for **operational state and coordination**. It would retain Tecnotron's authority semantics, verification of exact provider effects and developer approval from competent evidence, not map `bd close` directly to acceptance.

The strongest cost-saving hypothesis is **eliminating repeated generic storage and scheduling/index abstractions** rather than wrapping Beads inside a duplicate filesystem Kernel.

## Options (not decisions)

| Option | Changes | Expected gains | Safety / complexity cost | 020 test status |
| --- | --- | --- | --- | --- |
| A — Drop-in Beads for current lifecycle | Keep global numeric `store_revision`, global `event_count`, sync API, exact prior recipe returns | Little Product rewrite | Requires bridging async and manufacturing global order; effectively recreates a Kernel | **019 refutes native drop-in** |
| B — Beads-first async scoped concurrency | Convert selected Recipe/consumer to `async`; replace global expected revision with **version vector on the exact causally relevant read set**, protect all read-set members in one native batch, reconcile original external effects | Reject only conflicting related writes; no new global mutable ledger; native graph/storage first | Native `batchApply` has no general read-only `assertVersion` item. Guarding read set via `update` may create incidental revisions/events and extra writes. No total order by design | **020 tests mechanism, not Product** |
| C — Hybrid staged | Keep existing authoritative lifecycle for active TaskCycles while replacing duplicate planning/index/queue/claim/persistence elsewhere with Beads | Reuse reliable native coordination early; risk of Product drift limited | Transitional adapters and dual systems until consumer-by-consumer migration; must avoid duplicate writable truths | Research candidate, no implementation |
| D — Product contracts redesigned around native entities | Explicitly replace global revision contract and adapt semantic lifecycle, error codes, receipts, bindings and tests with scoped concurrency + async | Maximize Beads value; future code reduction | **Separate competent Product redesign/selection needed**; imported historical terminal evidence must remain checkable | Not authorized in Product |

## Target candidate boundaries

**Native Beads owns (candidate):**
- Durable operational work item identity, graph, labels/metadata, claim readiness and conflict detection, workload frontier and recoverable checkpoints.
- Native Dolt issue commits; guarded multiissue mutations where read/write set is known; no independent TS queue, leased scheduler or second issue ledger by default.
- Synthetic readiness/blocked state as planning *data*, never Product Developer grant or Independent Review.

**Tecnotron still owns (subject to a competent redesign):**
- Product authority and evidence, subject Git identity, TaskCycle initiation/closure rules, IR and Developer acceptance, `NONE/CONFIRMED/UNKNOWN` original-execution effect reconciliation, external provider receipt identity.
- Portable Git evidence as exact immutable results/handoffs, since local Beads journal alone is not identical to portable typed RunEvent history.

**Candidates to adapt or retire only after qualification:**
- `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts`: replace sync+global revision port **only for selected next-generation consumers**, not historic TaskCycle operations.
- `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js`: treat as one exact high-stakes consumer. Its `expected_state_revision`, `before.event_count + 1`, `invoke()` synchronous flow must be redesigned and negative-tested, not silently shimmed.
- `src/operational-spine-v0/state-kernel-adapter.js`: legacy adapter remains until all selected Product consumers have a qualified alternative; `State Kernel` cannot be retired due to a working isolated test.
- `RunStore`/SQLite and operational queues: evaluate actual installed/dynamic consumers, then possibly **remove rather than reimplement** redundant mechanisms.

## Hypothesized safety invariants under version vectors

1. **Read-set closure:** before an effect, discover and name every Beads issue whose state affects authorization/readiness (target, blocker, linked attempt and any source evidence pointers relevant to that action). If that set is unknown, do not claim concurrency safety.
2. **Atomic validation + effect:** require native issue versions on *each relevant row in the same transaction*. If native API lacks a read-only version precondition, a guarded 'unchanged' update might be used only after **measuring write amplification and read-only races**; this is not free.
3. **Authority is not status:** Beads `open/ready/closed` is not Product acceptance. Synthetic fixture authority used in experiments is not a Developer grant.
4. **External effect identity:** a native transaction protecting work graph does not make a GitHub/Actions/provider call atomic. Confirm original provider effects and exact receipts before retry; `UNKNOWN` stays blocked.
5. **No global ledger by accident:** adding a single global Beads issue bumped on every mutation reintroduces serial bottleneck and mutation journal obligations. It should be treated as a new design with measured need, not a 'free adapter'.
6. **Old audit preservation:** a new event model need not mimic historical global counters, but must preserve verifiable exact historical Product receipts and allow explicit read compatibility for existing completed records.
7. **Portable recovery:** multi-process/native persistence and remote Git receipts should remain correlated; an unarchived local journal alone is insufficient for cross-run review.

## Verification requirements before a competent Product proposal

- A current **real consumer** migrated in an experimental fork with before/after tests for permitted/denied admission, stale relevant reads, unrelated concurrent changes, human authority checks, `UNKNOWN` and post-crash recovery.
- Measure number of native operations/round-trips/writes and diff added vs duplicate code removed, not just PASS count.
- Test multi-writer simultaneous versions, transaction rollback, original provider lost-ACK after observable effect and independent verification, scoped `bd ready` still not conferring authority.
- Determine whether Beads native read-set validation can be truly read-only; if it requires synthetic writes, quantify amplification or reject this exact design.
- Decide portability/backup/DR and security once deployment is under consideration.
- Produce a **Product Change Proposal** *later* identifying superseded interfaces and a migration/compatibility plan; requires competent Product selection and Independent Review, not a research receipt.

**Experimental scope guard:** no Product modifications, no GitHub Issues/Projects synchronization, no migration, no global scheduler, no new Product states, no State Kernel removal. 020 readout is in RESULT.md once provider terminal evidence is reconciled.
