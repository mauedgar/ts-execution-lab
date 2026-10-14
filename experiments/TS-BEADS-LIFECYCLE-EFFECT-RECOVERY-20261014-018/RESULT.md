# TS — Beads 018 | Lifecycle capability contract and synthetic external-effect recovery

**Experiment identity:** `TS-BEADS-LIFECYCLE-EFFECT-RECOVERY-20261014-018` (2026-10-14, America/Argentina/Jujuy). **Experimental terminal:** `PASS_BOUNDED_LIFECYCLE_SHADOW_WITH_MATERIAL_GAPS / COMPLETE_WITH_LIMITATIONS`. **Authority:** NONE_PRODUCT; no Product TaskCycle initiated, reopened, accepted or integrated. No Product/remote-Dolt writes.

## 1. Reobserved subjects and immutable results

### Exact Product observation and source

- `mauedgar/tecnotron-ai:tools@f40236d24023159bc38aca06b3fa3862ac62608c`, Git tree `786758a44bd4c0170d864cb1391af934b5cdc75b`.
- Source of Truth `docs/SOURCE_OF_TRUTH.md` Git blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; current state `docs/current-state.md` blob `cac3955f1040e743248f015c974bbc397edb9650`.
- `src/state-kernel-v0/contracts.js` blob `5d2d3a8a24ebc17339675e0c801595956e0cd353`; `src/operational-spine-v0/taskcycle-lifecycle-capability.js` blob `9458a4baab04046e3e49bc07ecf06aafb15f3719`; TS source `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts` blob `2ab6e2655944fd98653d673d5d5a4dce69da3a06`; existing compatibility adapter `src/operational-spine-v0/state-kernel-adapter.js` blob `b8970d6e78b77878a8cb8ef0fbd3c2568954c82e`. Reobserved after PR #44, **all these contract blobs were unchanged** from original 017 Product anchor.
- PR #44 committed a narrow historical TaskCycle close lineage repair, touching only `src/deterministic-taskcycle-substrate-v0/taskcycle-close-evidence-qualification.js` and `tests/deterministic-taskcycle-substrate-v0/taskcycle-post-phase1-lifecycle.test.js`. The move of `tools` does not authorize this experiment to amend Product semantics; User specifically requested isolated Beads research.
- Shared independent lab remote reference `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` remained unchanged in successful Action's before/after ref reconciliation.
- Experimental branch `experiment/beads-lifecycle-effect-recovery-20261014-018`. Native script `experiments/TS-BEADS-LIFECYCLE-EFFECT-RECOVERY-20261014-018/native018.mjs` pinned by workflow source commit `7c97a70e6a141889e203f0a3475be274698a828a`. CI workflow `.github/workflows/ts-beads-018-lifecycle-effect-recovery.yml`. Native Beads binary v1.3.1 SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`, local Dolt v2.2.0 archive SHA256 `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`.
- **Terminal native run:** [GitHub Actions 38548780855](https://github.com/mauedgar/ts-execution-lab/actions/runs/38548780855), job `115801334471`, `completed/success`. `TS_BEADS018_NATIVE=PASS;checks=32;unknown=BLOCKED_THEN_SYNTHETIC_RECONCILED;stale_batch=ROLLED_BACK;Product=NONE` and `TS_BEADS018_NO_EXTERNAL_EFFECT=PASS;product=f40236d24023159bc38aca06b3fa3862ac62608c;dolt=1f72d68797114170a97fee27641858f2e55a4571`.
- **Immutable ephemeral native receipt:** `ts-beads-018-lifecycle-effect-recovery-receipt`, artifact ID `11886150655`, ZIP digest SHA-256 `9e7cf79165611573fa57122f0dd23f53861e79aaac75da4ca6c44f83c85e83c4`, expires 2026-10-21T10:20:38Z. This report and exact workflow/script Git blobs are durable beyond artifact TTL.

### Stopped initial attempt (preserve, do not confuse with failed Beads semantics)

First workflow [38548579718](https://github.com/mauedgar/ts-execution-lab/actions/runs/38548579718) at source SHA `6d1634c465c911d06b807fdf7a2b0a8971d408d5` **failed closed before any native lab work**: guarded Product exact-HEAD comparison expected old `tools@1ecce07708a5760c99d7faf55f2344f2eabbc119`, but observed current `f40236d24023159bc38aca06b3fa3862ac62608c` after PR #44. No receipt file was created because execution stopped at preflight. Reobserved SOT/tree/contracts, pinned only now-current Product identity and dispatched a new distinct bounded attempt. No blind retry, no prior Product effect.

## 2. What the native experiment actually exercised (32 PASS)

All Product aggregates were checked against the **actual frozen `validateAggregate`** and lifecycle transition vocabulary loaded from the exact current Product checkout. Synthetic names `TC-018-LAB`, `OP-018-LAB`, `AT-018-LAB` and synthetic authority `DEV-018-SYNTHETIC` never address real Product TaskCycles. One disposable Git repository with **no remotes** and local Dolt SQL Server held native Beads issues, relationships and metadata.

- **Structural real-port discovery:** the imported actual Product `requireExecutionLifecycleCapability` and `requireTaskCycleLifecycleCapability` recognize a partial experimental method set by name. **The method signatures and return contract are not fully qualified**: source ports are synchronous; test methods use async Promise; several methods deliberately throw `UNQUALIFIED` outside the narrowly tested subset. This is *not* functional full-port or drop-in conformance.
- **Scoped operation and attempt:** observe the native Operation/attempt; persist Product-compatible synthetic `ExecutionAttempt UNKNOWN` with `reconciliation_required=true` through Beads metadata CAS. A Product-owned semantic guard rejects a new attempt for the same Operation while unreconciled. Beads native alone does NOT enforce that semantics; a caller could create a second native issue.
- **Provider receipt lost-ack and recovery:** a **disposable, independent local filesystem provider fixture**, outside the Beads workspace, writes one durable `CONFIRMED` receipt to a unique identity path; a repeated request reobserves exactly the same bytes and does not write again. Wrong attempt or wrong request hash is rejected. No actual external provider was invoked and no Product grant asserted. Restart of native Beads HTTP server retains `UNKNOWN`; independent provider fixture receipt still read back.
- **Native optimistic multi-issue reconciliation:** `batchApply` acquired equality-only native issue row-version tokens for attempt and operation, then a competing synthetic writer advanced the operation's version. A batch trying to reconcile both issues with a stale token refused **all items**; the attempt retained UNKNOWN. Fresh-token atomic batch wrote the verified fixture's evidence ref into the attempt, marked both Product-compatible aggregates COMPLETED and closed native attempt/operation issues in one native database transaction.
- **Guarded TaskCycle close:** a Product-owned test guard rejected premature close while outstanding obligation/UNKNOWN; wrong authority refused obligation satisfaction, and stale TaskCycle revision refused close. Correct synthetic authority/reference satisfied the obligation via native CAS; final native batch with `expected_version` set terminal Product-compatible TaskCycle metadata and closed its Beads issue. Native CLI after server shutdown confirmed persistent terminal state and receipt digest. **This qualifies storage behavior on synthetic subjects only.**
- **Negative global-revision result:** native TaskCycle metadata revision did **not** change as unrelated attempt/operation issues changed; the original Product `TaskCycleLifecycleCapability.snapshot` exposes a globally comparable `store_revision` and `event_count`. Per-issue native row versions and CAS **do not automatically supply** this cross-aggregate temporal property. Close consumers that assume it cannot be reused unchanged.
- **Native batch retry nuance:** Beads `issueops.BatchApplier` [source](https://github.com/gastownhall/beads/blob/v1.3.1/issueops/batchapplier.go) explicitly does not provide a built-in idempotency key; a caller must make a correlation/idempotency record part of a guarded request, or reconcile exact existing effects before retries. Its `MetadataCAS` is single-key and cannot be inserted directly as an item inside batchApply. Do **not** claim atomic metadata semantic equality across every issue based on independent CAS and batch successes.

## 3. Qualified vs remaining equivalence

| Area | Direct result | Competent interpretation |
| --- | --- | --- |
| Native local metadata CAS | PASS | Candidate storage mechanic; not Developer authorization. |
| Per-issue version guarded multi-item Dolt transaction | PASS (stale miss rolls whole batch back) | Valuable for owned multi-aggregate mutations. |
| External receipt and lost acknowledgment | PASS **fixture only** | Protocol concept demonstrated; actual GitHub/Actions/Transport/provider identity and aftermath not yet tested. |
| UNKNOWN retry guard | PASS via explicit Product-owned experimental check | It is Tecnotron policy; Beads alone does not block a second issue. |
| Native server restart | PASS | Durable local readback; not multi-replica remote recovery. |
| Product lifecycle port shape | PARTIAL; method names checked | Async/sync mismatch and incomplete implementations prevent drop-in substitution. |
| Global revision/event sequence | **GAP OBSERVED** | Must explicitly design/preserve or prove no caller depends on exact global semantics; no implicit acceptance of per-issue clock. |
| Semantic authority / independent review | NOT QUALIFIED | Retain existing Product Control and Developer grants/IR evidence distinctions. |
| Cross-runner shared remote and provider effects | NOT QUALIFIED | Needed before any physical replacement or canonical adoption. |
| RunStore consumer removal | NOT EXECUTED | Experimental static evidence 017 remains candidate only, independent disposition. |

## 4. Decision boundary and recommended research direction

**Terminal:** `COMPLETE_WITH_LIMITATIONS` for experimental 018; **NO Product effect and NO shared Dolt remote mutation**. The strongest new observation is a real storage primitive fit **and** a material non-equivalence: the Product global lifecycle revision model cannot simply be replaced by native Beads row versions. A narrow adapter is plausible; arbitrary direct replacement is not qualified.

Recommended **019, experimental only and not initiated**: measure precisely which **active Product consumers** require the global revision/event_count and synchronous return semantics; explore one minimal native candidate with no duplicate mutable ledger (or demonstrate and document why no such candidate can preserve them). Combine cross-runner remote sync and real-provider loss-ack only if isolated provider actions can be safely qualified. Factor current Upper LC backlog/decisions by verified competence and adoption cutoff; do not gate isolated Beads research globally on beta closure, but block Product migration until relevant capabilities have competent disposition.

No proposed change to the accepted `Upper_LC_v1` semantic boundaries, frozen `TC_Core_v1`, historical TaskCycles, automatic Developer approval, PR #44 work or Recipe/Provider policy. Experimental findings are evidence, not Product decisions.
