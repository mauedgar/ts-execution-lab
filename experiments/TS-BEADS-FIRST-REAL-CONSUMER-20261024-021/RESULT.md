# TS — Beads 021 | Original Product consumer adapted in memory to async native Beads

**ID:** `TS-BEADS-FIRST-REAL-CONSUMER-20261024-021`  
**Fecha:** 2026-10-24 (Jujuy).  
**Autoridad:** `NONPRODUCT_EXPERIMENTAL_ONLY`. **Disposición:** `PASS_REAL_PRODUCT_CONSUMER_ASYNC_BEADS_FIRST_WITH_LIMITATIONS / COMPLETE_WITH_LIMITATIONS`.  
**Decisión de arquitectura:** `RESEARCH_CANDIDATE_ONLY`. No Product changes, no actual Product TaskCycle, no Developer grant, no Phase 2, no State Kernel deletion, no shared remote Dolt writes.

## 1. Verificable: sujetos y originales

- Current Product SOT observed read-only: `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`. SOT `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- **Consumer original:** `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js`, blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc`. Sus `preflight` y `execute` reales, su `reconcilePostTaskCycle` original y su validación Zod de recibos son ejecutados en la variante experimental. No se reconstruyó ni suplantó con una receta inventada.
- Lab experimental: `mauedgar/ts-execution-lab`, branch `experiment/beads-first-real-consumer-20261024-021`, based on `main@b30241201d07a9590e1e845abe767cdcf9921479`. Source script `experiments/TS-BEADS-FIRST-REAL-CONSUMER-20261024-021/consumer021.mjs`; workflow `.github/workflows/ts-beads-021-real-consumer.yml`; `DESIGN.md` explains coverage and noncoverage.
- **Exact terminal Action:** [run 40094843290](https://github.com/mauedgar/ts-execution-lab/actions/runs/40094843290), job `120874825608`, HEAD of execution `44d52f614d71da5b2d12c4cbed6119d27c496050`, conclusion `completed/success`. Native log:
```text
TS_BEADS021=PASS;checks=26;Product_consumer=ACTUAL_MEMORY_ADAPTED;native_closure=PASS;unknown=BLOCKED;ack_loss=CONFIRMED;Product=NONE
TS_BEADS021_RECEIPT=...beads021-real-consumer-result.json;status=PASS_REAL_PRODUCT_CONSUMER_ASYNC_BEADS_FIRST_WITH_LIMITATIONS
TS_BEADS021_NO_EXTERNAL_EFFECT=PASS;product=7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56;dolt=1f72d68797114170a97fee27641858f2e55a4571
```
- **Original native receipt:** GitHub Actions artifact `ts-beads-021-real-consumer-receipt`, ID `12560069425`, ZIP SHA-256 `2cc12c7ee00e4766116505e93c2b00281c2f1e20a2f148eab4273409c5e07868`, expires `2026-10-31T12:40:49Z`. Original ZIP downloaded and hash **independently matched**; internal `beads021-real-consumer-result.json` read and parsed: **26 checks PASS**, no runner error. This report is the durable summary after artifact retention expires.
- Beads v1.3.1/Dolt v2.2.0 pinned binary archives, local disposable Git without remotes, independent native Beads HTTP/CLI, no provider real writes. Native script and workflow enforce Product exact HEAD/tree/SOT and shared `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` untouched.
- **No replay of historical pilots 001–020.** No historical desktop bases used.

## 2. Attempts preserved, no rewriting of failures

| Attempt | Run/source | Observed terminal | Effects |
| --- | --- | --- | --- |
| 1 | [40094481284](https://github.com/mauedgar/ts-execution-lab/actions/runs/40094481284), `19aed0f1b994faf97857f0f73a135fea45e7a42b` | **FAIL** on incorrect negative expectation: developer `REJECTED` evidence in synthetic already-satisfied TaskCycle was treated as READY, not blocked; no closure reached | Isolated fixtures only |
| 2 | [40094726513](https://github.com/mauedgar/ts-execution-lab/actions/runs/40094726513), `d92b8397bac08ba2da40410bc1892819f552590d` | **FAIL** on experimental harness `ReferenceError: prodRequire is not defined`, before closure | Isolated fixtures only |
| 3 | [40094843290](https://github.com/mauedgar/ts-execution-lab/actions/runs/40094843290), `44d52f614d71da5b2d12c4cbed6119d27c496050` | **PASS**, 26/26 including positive and negative assertions and fresh native CLI readback | Only disposable native synthetic store |

All three were distinct Git subjects/Actions run IDs. Technical repairs were bounded to experimental source; no blind retry of any external Product/provider effect.

## 3. What was actually adapted and executed

The script reads the **exact original** Product `reconcile-and-close-taskcycle.js` inside a detached checkout and compiles a derived copy **in memory** (Node `Module._compile` under original module filepath) so the real Product relative imports and evidence validator remain active. The transformation is anchored and refuses source drift. It changes **15 original expression/function anchors**, primarily `async`/`await` around snapshot, preflight, mutation, bookkeeping and reassessment. This adds **90 bytes** to the original 36,279-byte consumer, **0 source lines** and **0 files to Product**; the native Beads-backed test harness is new experimental code and cannot be counted as eliminated production complexity.

A new *experimental* contract provides:
- A local epoch in the same Beads TaskCycle issue metadata (`ts021_epoch`), **not** a global Store revision or external mutable ledger.
- Exact native `expected_version` tokens for **two causal issues**: TaskCycle candidate and the ExecutionAttempt-like guard.
- Asynchronous real `preflight`/`execute` and `snapshot` over native Beads HTTP; atomic `batchApply` modifying TaskCycle and guarding the related attempt before closing its native issue. The original recipe's authority and evidence semantics remain its own, not inferred from `bd ready` or `bd close`.
- A native readback from a separate fresh CLI after server shutdown.

Two synthetic TaskCycle subjects (`TC-001`, `TC-ACK`) were configured with **all five historical obligations already SATISFIED** and pre-existing synthetic Developer authority. This purposefully exercises **preflight/effect closure** only, not full pending-obligation satisfaction. Neither subject exists in Product.

### Qualified original-consumer behaviors

- **Missing** developer acceptance evidence: original source reconciler blocked with `POST_TASKCYCLE_RECONCILIATION_UNRESOLVED`; zero native TaskCycle effect.
- **Unreconciled UNKNOWN:** original recipe preflight returned `BLOCKED / UNKNOWN_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION`.
- **Related race:** between before-snapshot and guarded native batch, synthetic attempt changed to UNKNOWN; Beads refused the multi-issue transaction (HTTP 409), no partial TaskCycle close. Original recipe returned `FAIL / effect_state NONE` and native root remained `ACTIVE`.
- **Unrelated write:** a separate third Beads issue was changed before closure; without global revision, it did not block a duly guarded mutation. The original Product recipe, adapted to async and per-TC epoch, returned **`PASS / CONFIRMED`** with real original reconciliation `RESOLVED`; native TaskCycle issue reached `closed`.
- **Terminal replay:** on same TaskCycle, original recipe refused a second closure: `FAIL / NONE`.
- **Lost/malformed ACK synthetic only:** on separate TaskCycle, native close **succeeded** while adapter intentionally corrupted returned event ID. Original recipe classified **`FAIL / CONFIRMED`** with `LIFECYCLE_MUTATION_EFFECT_CONFIRMED_BUT_UNACKNOWLEDGED:RECEIPT_CORRESPONDENCE_MISMATCH`; fresh native read confirmed terminal effect. No retry.
- Both synthetic terminal TaskCycles were independently read using Beads native CLI after server stopped.

### Safety-significant observation — ORIGINAL Product semantics, not Beads

The first attempt exposed an unexpected result, then the terminal attempt **reproduced it in both the memory-adapted consumer and the unmodified original Product consumer** with a synchronous synthetic lifecycle snapshot: when all original TaskCycle obligations were already marked `SATISFIED` and a pre-existing synthetic Developer authority was present, new *verified* `developer_acceptance.disposition = REJECTED` produced **`preflight.status = READY`** rather than the expected refusal. The native receipt contains:

```json
{"kind":"REJECTED_DEVELOPER_EVIDENCE_ORIGINAL_PRODUCT_CONSUMER","result_original":"READY","result_adapted":"READY"}
```

Likely mechanism based on source lines: `reconcilePostTaskCycle` classifies a verified `REJECTED` disposition as **fact RESOLVED** (not accepted); in `reconcile-and-close-taskcycle.js`, `reconciledAuthority` checks evidence classification and competence but does **not** check the developer fact disposition, while `sourceSatisfied` verifies `ACCEPTED` only while resolving a **pending** obligation. With already-satisfied obligations, no pending-rule check reasserts acceptance.

**Classification: `POTENTIAL_ORIGINAL_CONSUMER_AUTHORITY_SEMANTIC_GAP / NEEDS_INDEPENDENT_PRODUCT_QUALIFICATION`**. Do not claim a real historical rejected candidate closed, or that this artificial fixture is reachable by legitimate Product transitions; do not treat it as a Developer grant. Do not silently patch Product as part of Beads research. Recommend a separately scoped source-native negative qualification with actual reachable fixtures and competent Control disposition before Product adoption.

## 4. Complexity and performance observations (from original receipt)

| Metric | Original measured value | Interpretation |
| --- | ---: | --- |
| Original consumer bytes | 36,279 | Product source unchanged |
| In-memory adapted consumer bytes | 36,369 (+90) | 15 exact source anchors, 0 extra Product modules |
| Actual native HTTP reads | **61** | Across all test fixtures and negative cases |
| Actual native HTTP batch transactions | **56** | Across test setup, no-op metadata token probes, guards and terminal cases |
| Metadata version-token acquisition calls | **48** | Major opportunity to optimize native revision read API |
| Total native HTTP calls | **117** | Entire synthetic suite, not per Product TaskCycle |
| Native batch items submitted | **62** | Includes guarded no-op metadata updates; **not equivalent to 62 durable semantic changes** |
| Passing assertions | **26** | Suite-specific and includes successful negative controls |
| Source Product files edited | **0** | No adoption, no Code Product effect |

The 117 calls do **not** prove throughput, latency SLO, cost reduction, or maintenance-hours savings. The harness code itself is long and deliberately nonproduction; it is not evidence of reducing total code size. Beads atomicity and causal CAS are viable, but native read-set token reads can be expensive if a writable/no-op roundtrip is required. Qualify true read-only version retrieval, eliminate redundant probes and measure again before recommending refactoring a production consumer.

## 5. Disposition and next research

**021 terminal: `COMPLETE_WITH_LIMITATIONS / RESEARCH_CANDIDATE_ONLY`.** This is a stronger empirical milestone than 020: **the actual original Product recipe preflight + execute** was run in an explicitly changed async/scoped contract against native Beads state without touching Product. It supports the user's direction to **challenge inherited canonical implementation and give native Beads capabilities priority** in future *proposals*. It does not implement nor supersede current Product authority.

**Suggested separately authorized next experiment 022 (not started):** focus on one high-value deficiency before broad migration: (a) actual pending-obligation mutation path with correct authority and a safe malformed/rejected evidence negative, (b) read-set discovery and native token read efficiency under concurrent writers and process restart, and (c) compare net implementation complexity and regression vectors to present Product consumers. The possible ORIGINAL `REJECTED` authority gap deserves an independent qualified research case, not a hidden automatic Product fix. Any future architectural adoption/change requires competent Product Control disposition.

**Effect status:** Product `tools@7a722594...` unchanged; Beads shared `refs/dolt/data@1f72d687...` unchanged. No TaskCycle #34 selection/initiation or historical effect replay.
