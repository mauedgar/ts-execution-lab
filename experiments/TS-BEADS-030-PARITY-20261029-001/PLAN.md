# Beads 030 | Control experimental — B-first same Product closure consumer

**Date:** 2026-10-29. **Authority:** Experimental Control for Tecnotron Beads research only. User selected **B as the architectural research priority**; not a Product adoption, grant, Phase 2, TaskCycle admission, Kernel removal or permission to change tools Product.

**Exact Product SOT:** `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, current state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`. Lab main `b30241201d07a9590e1e845abe767cdcf9921479`, shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.

**Previous evidence:** 022 original Product recipe was adapted in-memory with 15 anchored sync-to-async substitutions on a native Beads/Dolt store, measured 127 vs 73 HTTP calls under matched internal-B workload and verified UNKNOWN / ACK / pending obligations. 029 verified current Kernel 36,715 bytes / four source files, adapter 12,020 bytes, and comparison A/B **not performance-comparable** from the previous experiments. 023–028 proved privileged and misconfigured auth bypass, so causal graph authority is **not** qualified even after this parity exercise.

## B-first experiment, same Product semantic consumer

A = **original unmodified** `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js` running with actual `FilesystemStateStore` and `createStateKernelTaskCycleLifecycle`; in a fresh isolated home, real event journal and state history.

B = **same original Product recipe** adapted *in memory* with the 022 verified 15 substitutions, running against local Beads v1.3.1/Dolt v2.2.0 native HTTP GET revision and guarded atomic batch. The B harness reuses the bounded 022 source but pins the **current** Product exact commit and times one positive execute separately. No code in Product is changed.

**Same input family / competing semantics:** five PENDING obligations (review, Developer acceptance, integration, publication, lifecycle reconciliation), identical synthetic evidence/authority refs and original Recipe `req()` builder, TaskCycle ACTIVE and attempt RUNNING; full positive closure and authority attachment; un-reconciled attempt UNKNOWN blocks; synthetic wrong-ACK after one obligation remains CONFIRMED without close; concurrent attempt race aborts with NONE; terminal repeat denied. Also reproduce original source finding: Developer REJECTED and pre-satisfied obligations may yield READY in synthetic state (not proof of real historical reachable Product failure).

**Equality constraints:** compare only normalized outcomes and authority IDs. Kernel uses a **global event history**; Beads test uses a **per-taskcycle experimental epoch**. Event IDs/revision counters are not equivalent and cannot be normalized into a claim of complete Product parity. Timings are **one cold positive sample** on the same runner, with instrumented Kernel read/verify/mutate counts and B HTTP GET/batch/write-item counts, not a production performance measurement. Script/test LOC does not prove removed Product maintenance cost.

**Execution:** isolated Windows runner with pinned vendor binaries and hashes, read-only checkout Product at exact SHA/tree, npm ci, no remote in test git. Original Node receipts `A.json`, `B.json`; source-backed `COMPARE.json`; all exact in `IR-TXT-CARRIER/1` created/verified/extracted via Product `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`; Git published carrier readback checked. No ZIP consumer carrier or external provider effect.

**Failure policy:** preserve each source/run identity and error; repair only exact observed fixture defect. No replay of 022/029 effects. B Product adoption **remains blocked** until global history/effect reconciliation, all native graph writers and real provider UNKNOWN are independently qualified.
