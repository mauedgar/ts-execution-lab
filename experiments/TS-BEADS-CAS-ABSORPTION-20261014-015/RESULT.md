# TS — Beads 015: Native transactional CAS and broader Tecnotron module absorption

Date: 2026-10-14 (America/Argentina/Jujuy). Continuous experimental Beads/Tecnotron responsibility. **NONPRODUCT only**: no new/altered Product TaskCycles, no grants, integration, physical module retirement, canonical decisions, shared Dolt modifications, or Product repository writes.

## 1. Current immutable subjects and result

- Product `mauedgar/tecnotron-ai:tools@1ecce07708a5760c99d7faf55f2344f2eabbc119`, tree `025ce7524d1b8bf1753cfc4af964ee554d3b0977`, latest at preflight following PR #43. This supersedes the previous pilot's physical `2a42a1bb...` anchor for *current HEAD* interpretation. `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `cac3955f1040e743248f015c974bbc397edb9650`. Product State Kernel final disposition is still `UNDECIDED`.
- Previous shared native Beads remote `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, unchanged in terminal qualified run.
- Experimental branch `experiment/beads-cas-absorption-20261014-015`. Node runner: `experiments/TS-BEADS-CAS-ABSORPTION-20261014-015/native-cas015.mjs`. GitHub workflow `.github/workflows/ts-beads-015-native-cas.yml`. Native `bd v1.3.1` binary SHA-256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`; native Dolt `v2.2.0` archive SHA-256 `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`.
- **Terminal PASS**: [Actions run 38530104879](https://github.com/mauedgar/ts-execution-lab/actions/runs/38530104879), job `115739676133`; execution source commit `e18f3f59d30cef110ec087c4148c8ad79bc3de8c`; job all steps success. Log `TS_BEADS015_NATIVE_CAS=PASS;checks=21;effect=NONE_PRODUCT;atomic_single_key=QUALIFIED`. Log `TS_BEADS015_NO_EXTERNAL_EFFECT=PASS;product=1ecce07708a5760c99d7faf55f2344f2eabbc119;dolt=1f72d68797114170a97fee27641858f2e55a4571`.
- Exact GitHub Actions artifact ID `11878040860`, name `ts-beads-015-native-cas-receipt`, ZIP `sha256:9b250b28f33d2c5163ff5419a8a08a2c7b734f0672bde30d61b81b19930dc747`, expires 2026-10-21T07:43:19Z. The Git source and this report remain after ephemeral artifact expiration.

## 2. Native runtime qualification: 21 checks, zero failed

Dolt server mode in an isolated Git repository with no remotes, fresh `.beads`, loopback-only `bd serve --addr`, real HTTP POST `/v0/beads/issues/{id}:casMetadata`, and separate CLI readback after stopping HTTP. No shared refs, external dispatch, or Product operations were used.

Verified **native** behaviors:
- Persistent exact synthetic issue identity and duplicate explicit ID rejection.
- Loopback native HTTP API successfully accepted CAS for an initially absent metadata key.
- Two concurrent CAS requests on the same absent key yielded **exactly one `swapped:true`**, one `swapped:false`; the loser received the committed `current` value.
- Stale `expected` refused without overwriting the current value.
- A second concurrent pair using the winner's value also yielded exactly one winner, with the loser observing the new final value.
- Independent metadata key survived a concurrent series of changes to another key.
- Native no-op matching CAS returned `swapped:true` and the existing value.
- Native `UNKNOWN` effect metadata was durable, a stale attempted reconciliation failed, an injected *synthetic* receipt supported a guarded transition to `CONFIRMED`, and duplicate outcome replay with stale expected was rejected.
- After stopping `bd serve`, the CLI independently read the exact revision, authority anchor, confirmed effect/receipt, and original issue history.
- The Product HEAD and shared Dolt `refs/dolt/data` remained unchanged after the test.

**Qualified**: *transactional CAS of one Beads metadata key* on an independently running native HTTP service with Dolt SQL server. It can implement an optimistic token for an operational lifecycle *within a single key*, without a separate home-grown compare-and-set store.

**Not qualified**: semantics of Developer grant/independent review, external effect confirmation, multi-entity/issue close as one transaction, native lifecycle `ExpectedVersion` role separately, independent distributed provider crash reconciliation, Git-hosted shared Dolt multiwriter conflict, Product acceptance, physical replacement of State Kernel. An HTTP `actor` is caller-asserted provenance, not Product authority. The synthetic receipt here was injected, NOT a verified real provider ACK.

## 3. Failed attempts preserved; no replay of Product effects

| Run | Outcome | Cause | Effects |
|---|---|---|---|
| [38529423226](https://github.com/mauedgar/ts-execution-lab/actions/runs/38529423226) | FAILED | Local generated `lab-` prefix rejected deterministic synthetic `ts015-` ID before CAS | Disposable only |
| [38529586925](https://github.com/mauedgar/ts-execution-lab/actions/runs/38529586925) | FAILED | Native `bd serve` requires Dolt SQL Server, refuses embedded mode | Disposable only |
| [38529881014](https://github.com/mauedgar/ts-execution-lab/actions/runs/38529881014) | FAILED | Windows Node child killed by signal; test shutdown guard checked `exitCode` without accepting non-null `signalCode` | Disposable only, diagnostic receipt retained |
| [38530104879](https://github.com/mauedgar/ts-execution-lab/actions/runs/38530104879) | PASS | Correct bounded setup (Dolt SQL server) and cleanup; 21 positive/negative assertions | Product NONE, shared Dolt unchanged |

No retry of remote provider writes. Each source/workflow run has its own immutable identity; terminal failures are not rewritten.

## 4. Broader module absorption: significant beyond State Kernel

The exact [MODULE-ABSORPTION-MATRIX.md](./MODULE-ABSORPTION-MATRIX.md) examines the Product source and native Beads v1.3.1 code/docs against **12** areas with evidence labels, ownership and blocked overreach.

**Best reuse candidates**, without automatic Product promotion:
1. **Generic operational index, dependency DAG, discovery, claims and agent frontier:** native `bd ready`, `blocked`, `discovered-from`, claim and molecular/fan-out workflow; avoid an independent duplicate mutable queue. Previous pilots 005/009/010/013 already qualify bounded native examples. Beads `ready` is *not* Developer-ready.
2. **Operational lifecycle storage and concurrency:** native metadata CAS qualifies one-key transitions, issue identity and audit, and could replace much of State Kernel physical persistence through the *existing lifecycle capability ports*. Preserve semantic policy, exact original-effect reconciliation and proper close semantics; do not run two parallel lifecycle owners.
3. **Redundant RunStore and operational projections:** candidate consolidation with native Dolt history, event/audit journal and metadata/KV. At the Product capability-map cutoff RunStore had no active runtime caller, but deletion must rely on a current per-component consumer/equivalence check. A Beads issue event is not automatically a typed RunEvent nor a real provider receipt.
4. **Continuation and coordinator narrowing:** Beads metadata, cross-repo dependencies, molecules, formulas and work assignment can carry the operational work graph and pointers across sessions. Preserve the portable immutable manifest/hash/evidence and current deterministic Recipe and ExecutionSurface owners; Beads does not create a new scheduler or semantic grant.

**Not candidates for native authority replacement:** Product Control, Upper LC/TC Core grants/acceptance, Independent Review semantics, Git/repository Source of Truth, deterministic evidence packaging/source acquisition, actual external execution provider, pricing/FinOps, or event/receipt confirmation. `bd mail` delegates to a separate mail provider; it is not a built-in Web wakeup, and `bd memories` is not canonical Product knowledge.

## 5. Disposition

`015 = PASS_NATIVE_METADATA_CAS_WITH_PRODUCT_SEMANTIC_LIMITS / COMPLETE_WITH_LIMITATIONS`. Scope expansion delivered: prioritized evidence-backed module absorption assessment, not only State Kernel.

**Next recommended bounded experiment, not dispatched**: test *native multi-issue/lifecycle close equivalence and event journal ↔ existing RunStore event semantics*, using separate native lab data and actual source schemas; compare current consumer/cost outcomes and identify which physical components could be removed. If Beads natively covers concurrency/audit/graph, keep only the minimal Product policy and semantic gates that a generic issue database cannot own. Never create duplicate state, schedulers, or providers as a precaution. Product retirement or integration remains a separate competent Product Control decision.
