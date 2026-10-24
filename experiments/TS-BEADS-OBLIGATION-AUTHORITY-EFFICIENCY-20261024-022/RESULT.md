# TS — Beads 022: obligaciones pendientes, autoridad y versiones nativas

**Fecha:** 2026-10-24. **Estado terminal:** COMPLETE_WITH_LIMITATIONS. **Adopción Product:** NONE. **Resultado:** PASS_READONLY_NATIVE_GET_REVISION_PRODUCT_CONSUMER_WITH_LIMITATIONS.

## Sujetos competentes e identidad

- Product read-only: mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56; tree 8caa56d36f3efeba359bbbf65b158ffb01a19da6.
- SOT docs/SOURCE_OF_TRUTH.md blob dd8d34a7e3ef3094805d014f9e59741d2c553957; docs/current-state.md blob 0d8a6426f51020d51d74bfb50dc8702a07f02837.
- Real original consumer: src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js blob 1e89df1a1885e3d0d24576338f0ffbd9b79890bc; imported original reconciliation, authority, Zod validation and receipts, with 15 pinned in-memory async substitutions. No Product file edit.
- Lab branch: experiment/beads-first-obligations-readset-authority-20261024-022; based on main@b30241201d07a9590e1e845abe767cdcf9921479; scripts consumer022.mjs (baseline) and consumer022-readonly-revision.mjs (optimized), workflow ts-beads-022-obligation-authority-efficiency.yml and DESIGN.md.
- Shared Dolt ref unchanged: refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571. Local Beads 1.3.1 and Dolt 2.2.0 isolated, no git remote in disposable test store, no Product TaskCycles or provider effect.

## Dos intentos nuevos, exactos y exitosos

1. [022 baseline run 40101479718](https://github.com/mauedgar/ts-execution-lab/actions/runs/40101479718), job 120894364331, executed source 7a0f3450b82f74d3762a601f90e8414331536d2e: **29/29 PASS**, status PASS_BOUNDED_PRODUCT_PENDING_OBLIGATIONS_AND_AUTHORITY_NEGATIVE_WITH_LIMITATIONS. Original artifact 12562957468 (ts-beads-022-obligation-authority-efficiency-receipt), ZIP SHA256 eb29efa6fe74b7dd339fc2f15147eb3e92b9e0963a9abf9a5cbc4795e08bad87.
2. [022 read-only-token run 40101787789](https://github.com/mauedgar/ts-execution-lab/actions/runs/40101787789), job 120895277607, executed source 007601ed2d199be0ba7ccf46def3843d1c881571: **31/31 PASS**, status PASS_READONLY_NATIVE_GET_REVISION_PRODUCT_CONSUMER_WITH_LIMITATIONS. Original artifact 12563021632 (ts-beads-022-readonly-native-revision-receipt), ZIP SHA256 36e1316527b24ea06a863c19d57ecb821a7b4dcdbf82a71bf2016543f0813f61.
- Both artifact ZIPs downloaded, independently hashed, JSON contents parsed and checked; provider logs confirmed Product HEAD and shared Dolt unchanged. These artifacts expire 2026-10-31; this report preserves exact Git subjects and durable analytical findings.
- No reexecution of old pilots 001–021. The second 022 attempt was a **distinct authorized technical optimization** after reconciling the terminal baseline and its native revision evidence.

## Full pending-obligation Product consumer pathway

- The actual Product recipe, compiled in memory with scoped asynchronous reads/writes, started from a synthetic TaskCycle with five PENDING obligations (INDEPENDENT_REVIEW, DEVELOPER_ACCEPTANCE, CANONICAL_INTEGRATION, REMOTE_PUBLICATION, LIFECYCLE_RECONCILIATION), no initially attached Developer authority, and synthetic internally verified evidence.
- Product original preflight/execution logic passed: five obligation satisfactions, references of reviewer/developer/effect authority attached according to fixture, and native atomic Beads TaskCycle close guarded by version tokens for exact TaskCycle and related attempt issue.
- Final synthetic TaskCycle CLOSED with five SATISFIED; per-TaskCycle experimental epoch 50→56; aggregate revision 7→13; synthetic event-56, independently recovered from native CLI after server shutdown. These synthetic counters do NOT establish global Product event history.
- UNKNOWN synthetic ExecutionAttempt blocked preflight; terminal replay returned FAIL/NONE. A malformed acknowledgment after first obligation satisfaction resulted in FAIL/CONFIRMED, exactly CANONICAL_INTEGRATION satisfied, four PENDING and TaskCycle ACTIVE, without blind retry or closure.
- In optimized 022 a native writer changed the related issue between read and batch. The guarded batch rejected, Product consumer returned FAIL/NONE, all five obligations remained pending. This additional race scenario costs 11 GET and 3 batch calls. An unrelated issue does not need to be part of the read set, although complete causal dependency discovery has not been qualified.

## Independent negative finding: original Product authority semantics

Without Beads and without modifying the Product recipe, its original preflight was run with synthetic synchronous port snapshots and verified synthetic evidence developer_acceptance.disposition = REJECTED.

| Existing Developer obligation | Original Product preflight | Interpretation |
| --- | --- | --- |
| PENDING | BLOCKED: OBLIGATION_SOURCE_NOT_COMPETENT:DEVELOPER_ACCEPTANCE:developer_acceptance | Rejected fact cannot satisfy pending obligation |
| Already SATISFIED, developer authority attached to snapshot | READY | Potential gap: fact REJECTED may be reconciled as RESOLVED without rechecking acceptance when no pending rules remain |

The same pending negative blocks in the Beads-first variant. This behavior is **original Product semantics, not introduced by Beads**. It does NOT prove that such a post-satisfaction/rejection snapshot is reachable from legitimate Product transitions or that a real unauthorized closure occurred. Classification: POTENTIAL_ORIGINAL_PRODUCT_AUTHORITY_SEMANTIC_GAP / INDEPENDENT_REACHABILITY_REVIEW_REQUIRED. Do not silently rewrite history or interpret REJECTED as Developer grant.

## Efficiency: native GET revision eliminates 54 needless batches

Baseline native HTTP GET returned a revision string matching the expected_version token obtained by an extra guarded same-value metadata update, measured independently in both root and gate rows. Optimized readSet uses GET(root).revision and GET(gate).revision directly, then batchApply expected_version for atomic causal write protection. No global duplicate mutable ledger is created.

| Measured in original artifact | Baseline, 29 PASS | Optimized incl. extra race, 31 PASS |
| --- | ---: | ---: |
| HTTP GET | 64 | 75 |
| HTTP batch | 63 | 12 |
| Extra metadata batches solely for tokens | 54 | 0 |
| Total HTTP | **127** | **87** |
| Batch items recorded | 71 | 21 |

Optimized additional race uses 11 GET + 3 batch. Subtracting exactly those from the optimized measured run yields **64 GET + 9 batch = 73 requests** for the matched baseline workload, versus 127: **54 fewer = 42.5% fewer calls**. This comparison is actual instrumented test counts, not claimed production latency/throughput improvement. Two sequential GETs do not constitute an atomic read snapshot; the multiissue batch protects only the explicitly complete causal read set.

## Complexity, debt and disposition

- Original consumer 36,279 bytes; in-memory derived consumer 36,369 bytes (+90 bytes), 15 anchored substitutions, zero Product modules or lines added. The experimental provider/harness code has nontrivial complexity and is NOT yet evidence of net reduced Product lines or maintenance effort.
- Product semantics of competent authority, exact provider identity, Independent Review, UNKNOWN effects, receipts and historical acceptance must remain accountable when redesigning; Beads open/ready/close alone grants none of these.
- Not qualified: source-native actual TaskCycle lifecycle, global Product journal equivalence, all original consumer regressions, dynamic read-set discovery, multi-runner/remote concurrency, real external lost-ACK, installed consumer migration, net code reduction, or safe State Kernel removal.
- **Result:** Beads-first async/native causal-version architecture is supported for this bounded real consumer experimental slice. It is a candidate for Product proposal, not adopted Product or a new default gate/role/orchestrator.
- Next suggested independent Product-facing qualification: test reachability of the already-SATISFIED plus new REJECTED state and authority flow with exact legitimate transition evidence. Separately investigate safe complete causal read-set discovery, real provider UNKNOWN and net dependency/code deletion before proposing a scoped Product redesign.

**Product and shared Dolt unchanged, no TaskCycles real affected.**
