# TS — Beads ↔ Tecnotron | Real Product consumer shadow 012

**Date:** 2026-10-14 (America/Argentina/Jujuy)  
**Classification:** NONPRODUCT_EXPERIMENTAL / READ_ONLY_PRODUCT_SHADOW  
**Disposition:** `PASS_MODEL_ONLY_WITH_LIMITATIONS; NO_CANONICAL_ADOPTION`  
**Product authority/effects:** `NONE / NONE`  
**Replayed Product TaskCycles, ExecutionAttempts, prior Beads pilots, or Dolt writes:** `0`  
**Experimental branch:** `experiment/beads-consumer-shadow-20261014-012`.

## 1. Exact observation and selected real subject

- Source handoff: `mauedgar/ts-execution-transport@7e5b6365319c6238165045195d2d7a72d8b01d8b:handoffs/TS-BEADS-CONSUMER-SHADOW-ROTATION-20261014-001/HANDOFF.md`, blob `bc61d44296f6c93bc165b862d6cee2d3d4a9cd4e`. Consumed in receiving chat; no source-chat retirement.
- Product: `mauedgar/tecnotron-ai:tools@2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89`, tree `04e57337ac129bd40774d48cf2cfee041f904cfa`. Actual live branch was independently reobserved and matched handoff.
- `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; `docs/current-state.md` blob `cac3955f1040e743248f015c974bbc397edb9650`; `docs/architecture-knowledge-ownership-baseline.md` blob `330fdc82f75e1126939cd718c1facb28abe00c62`. Post-Close §16.5 keeps CONTROL_DELTA different from Product promotion, and Product promotion different from TaskCycle initialization.
- Exact *historical closed* subject: `TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001`, Product current-state disposition `CLOSED_PASS`, candidate `34ab96c00ca5f8c9c87d69a31371d275eeb5f6d9` and its tree `d79640a7fcc614ecfac0fe76f0ca600b41beac6b`. Historic commit/tree were independently reobserved. `docs/tasks/TEC-TC-RECIPE-KERNEL-DECOUPLING-001/TASK.md` blob `96d85ee7918b35d8281c889518bc4d3f2686cd52`; its historical `next_gate: NOT_AUTHORIZED` is assignment provenance, **not** a present blockage or an invitation to reinitialize the completed subject.
- Current real consumer source: `src/deterministic-taskcycle-substrate-v0/continuation.js` blob `39714164b666b59132f95d82605f720aa00d8e63` still validates portable continuation identity/evidence; `src-typescript/operational-spine-v0/recipe-invocation.ts` blob `f606143577ef93b3f41012aeb0f05c1eb6729a64` still imports the compatibility binding, with `executionLifecycle` injection as an existing port; `tests/operational-spine-v0/recipe-kernel-decoupling.test.js` blob `9afbc9f371aa690db816a3453a786b858273e841` checks confinement of Kernel imports to the explicit adapter. Read-only observation, not a new full conformance test.
- Earlier Beads consumer fit: `mauedgar/ts-execution-lab@5aae136a3f8ab9c9bae8f97befcf3effe6239ff3:experiments/TS-BEADS-CONSUMER-FIT-20261013-011/REAL-CONSUMER-ABSORPTION-ASSESSMENT.md` (blob `df4990a1e0f660e0aa1af5847a20af9ade7d86be`). Its prior Beads 001–011 evidence is not rerun. `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` was independently reobserved; contains synthetic operational obligations, not Product authority.

## 2. Two projections of the same real subject

**A — competent Product observation.** Exact closed TaskCycle and candidate, source SOT, archived assignment/evidence and Product authority boundaries. A remains authoritative about lifecycle, effects, gates and receipts. This subject cannot be reinitialized by a shadow index. Any new Post-Close discovery must remain evidence or candidate until explicitly admitted.

**B — hypothetical Beads index at an existing Control checkpoint.** A non-authoritative record with `origin_ref`, native operational `ready|closed`, dependencies, claim and duplicate-origin observations. This model uses *previously qualified Beads native behavior* from pilot 011; **no live Beads issue for this Product subject was observed or created**, no `bd` CLI/provider operation was performed in 012, and all Beads entries here are explicitly synthetic counterfactual projections. It is a shadow of a real Product consumer, **not** an end-to-end native Beads integration test.

The decision rule does not transfer lifecycle authority from B to A: missing source -> incomplete; original effect UNKNOWN -> original effect reconciliation; duplicate semantic source -> identity/readback; Product closed -> no reopen; interrupted original -> same identity after original gate; dependency unresolved -> blocked; `claim` -> allocation only; Product authority absent -> no dispatch. Even a separately authorized, unblocked, Beads-ready synthetic item is **only presented for consideration at an existing checkpoint**.

## 3. Reproducible bounded shadow

Artifacts in this experimental directory:
- `shadow012.mjs` — self-contained deterministic Node.js runner, 15 cases. Exact Git blob `b5c971415ddcc7c05e6a6062b01f0d0846b15b57`, SHA-256 `a12122520bb9a4e28fda589606f5abdba25300b1f6455ffc3169f124f80c2170`.
- `RESULT.json` — output from `node shadow012.mjs` on Node `v22.16.0`, Git blob `fec8d4572fcd4296f633c90a81edbaec2675358e`, SHA-256 `36e862acef282fac5a1485e3c42ea3369494befd106d8a5875e4c634a36baffe`.

**Observed result:** `15 PASS / 0 FAIL`. The first case compares actual Product CLOSED_PASS with *synthetic* Beads ready; other cases are intentionally synthetic counterfactuals. Cases cover post-close discovery, unmet/UNKNOWN dependency, already-authorized independent work, missing grant, same-identity interrupted continuation, exact-ID duplicate, cross-ID semantic-origin collision, original UNKNOWN effect, claim without grant, Beads closed ≠ Product close, missing refs, duplicate dependencies, and unqualified index status. Every test asserted `Product_effect: NONE`, no dispatch, no new TaskCycle and zero Product repository writes **inside the projection**.

**Evidence level:** `MODEL_PASS` — tested decision projection, not an empirical measurement of live Beads ready/claim queries, distributed races, installed consumer integration, Product transitions or throughput. It does not supersede pilot 009/010 limitations.

## 4. Fresh consumer disposition / possible simplification

| Consumer | Disposition | Justification and boundary |
| --- | --- | --- |
| Product Control at pre-existing checkpoint | **ADAPT_CANDIDATE**, not accepted | An optional Beads query could index cross-chat dependencies/discoveries while Control uses exact Product SOT/receipts to decide. The model preserves all authority boundaries. |
| Cross-module discovery / nonauthoritative inbox | **POTENTIAL_ABSORPTION**, conditional | Native `discovered-from`, `blocks`, ready and qualified claim could remove a redundant **operational** discovery/assignment list *if a real caller and redundant state owner are established*. None was inventoried as independently removable in 012. |
| TaskCycle continuation / portable semantic handoff | **RETAIN_AND_LINK** | Beads may locate original Git carrier; it does not replace `continuation.js` manifest hash, evidence sufficiency or immutable source identities. |
| Operational Spine / Coordinator / Recipes | **RETAIN** | Native Beads graph does not prove exact candidate review, conditioned effect/UNKNOWN reconciliation or Developer acceptance. |
| State Kernel compatibility/lifecycle | **KEEP**, physical disposition unresolved | `recipe-invocation.ts` still defaults to Kernel compatibility. An injection port is not proof of Beads-backed lifecycle equivalence. No physical migration/removal authorized. |
| GitHub Issues/Projects | **RETAIN_AS_PROJECTION** | Provider Ready has its own unqualified field mapping; no automatic Beads↔Project synchronization. |
| RunStore | **SEPARATE REMOVAL EVALUATION ONLY** | Historical lack of a runtime consumer cannot by itself authorize deletion or tie deletion to Beads adoption. |

No quantified improvement in recovery latency, maintenance hours or storage complexity was measured. The model suggests which **read/coordination view** could shrink, not that production code can yet be removed. A Beads query **adds** infrastructure/tool/version/ref management unless it demonstrably displaces a real redundant manual index. No second mutable truth, new scheduler or new lifecycle controller is recommended.

## 5. Next disposition / limits

`PASS_MODEL_ONLY_WITH_LIMITATIONS` justifies a **bounded Product Control interconsultation proposal**, **not** Product selection, adoption or migration. For further empirical qualification, perform **one isolated native Beads read/query shadow** against a pinned copy of synthetic experimental state and an exact Product source pointer; validate stable native ID/readback, ready/blocked and source correlation at a *pre-existing* Control checkpoint without Product writes. Do not write the old shared `refs/dolt/data` or promote a Beads status to Product authority. Then compare measured retrieval operations/costs against current Control workflow before considering actual consumer adaptation.

Remaining unqualified: real integrated Product Control reader, real two-agent Product concurrency, native source-origin semantic dedup without deterministic-ID discipline, effect UNKNOWN across external provider, long-term remote DR, lifecycle equivalence and concrete physical consumer retirement. Reobserve live refs before any subsequent effect-dependent task. **All Product effects NONE.**
