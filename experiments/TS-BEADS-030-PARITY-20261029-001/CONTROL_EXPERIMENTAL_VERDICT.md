# TS — Beads 030 | Dictamen de Control experimental: prioridad B, mismo consumidor Product

**ID:** `TS-BEADS-030-B-FIRST-CONSUMER-PARITY-20261029-001`  
**Fecha:** 2026-10-29.  
**Estado experimental terminal:** `COMPLETE_WITH_EFFECT_CLASSIFICATION_DIVERGENCE_AND_AUTHORITATIVE_MIGRATION_BLOCKERS`.  
**Resultado mecánico:** `PASS_B_FIRST_SHARED_TASKCYCLE_OUTCOMES_EFFECT_CLASSIFICATION_DIVERGENCE`, comparación **12/12 PASS** (A Kernel original **10/10 PASS**, B native Beads **31/31 PASS**).  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`. User has selected **B (Beads-first authoritative design)** as research priority; this is **not** Product adoption, TaskCycle authority, acceptance, Independent Review, Developer grant or Phase 2.

## 1. Competent read-only Product, exact experimental subjects

- `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`, `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Unmodified Product Recipe `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js`, Git blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc`, SHA256 UTF-8 `cd07ef9243b05b04021210e745069f9b397ca21d8e696afb536969b0a4e1ce5f`, **36,279 bytes**.
- A: same **unmodified** Product Recipe against original `FilesystemStateStore` and Product `createStateKernelTaskCycleLifecycle`, with actual local file journal and native Kernel obligations. B: same original Product Recipe adapted **in memory** through 15 anchored sync-to-async substitutions, **36,369 bytes (+90)**, native Beads v1.3.1/Dolt v2.2.0 on separate disposable store with exact GET row revisions and atomic `batchApply`.
- No installed Product modules modified or deleted. The historical 029 comparison remains `mauedgar/ts-execution-lab@6c03915493594a38cbb21c80235e7ac81e0e26af`; its short-term A preference is **superseded for experimental priority by explicit user selection of B**, not rewritten as a Product ruling.
- Shared Dolt remote `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, Product `tools` unchanged at postflight. Lab main `b30241201d07a9590e1e845abe767cdcf9921479`, experimental branch `experiment/beads-030-b-first-consumer-parity-20261029-001`.

## 2. Original attempts, reconciled independently

| Attempt | GitHub Actions run | Exact source commit | Terminal observation |
| --- | --- | --- | --- |
| 1 | [40880913422](https://github.com/mauedgar/ts-execution-lab/actions/runs/40880913422) | `2624450a49d7cc7eea7b111e15261ff9716adf7a` | **FAIL**: original Kernel `fsync` EPERM on Windows, before B executed |
| 2 | [40881277453](https://github.com/mauedgar/ts-execution-lab/actions/runs/40881277453) | `f428c53421ac437b5e2580b2cb7813ac12f9f413` | **FAIL**: on same Linux runner A Kernel conservatively classified concurrent attempt mutation as `UNKNOWN`, first test expected `FAIL/NONE` |
| 3 | [40881761707](https://github.com/mauedgar/ts-execution-lab/actions/runs/40881761707) | `5e91adbdc888e2a00dfa17468dfa34880cede485` | **FAIL**: A's exact race observed `status=UNKNOWN, effect_state=UNKNOWN`; test still wrongly required `status=FAIL` |
| 4 | [40882040812](https://github.com/mauedgar/ts-execution-lab/actions/runs/40882040812) | `b0211b70bfb98db11f3b27c0cde5dc9f5da92f7f` | A **10 PASS**, B original complete, comparison **12 PASS**, but workflow **FAIL** after tests due wrong TXT materializer PLAN path. Source evidence wasn't durably published and that attempt remains FAIL |
| 5 | [40882306183](https://github.com/mauedgar/ts-execution-lab/actions/runs/40882306183), job `123476761771` | `9d37dda92ec5e3ba66e827ee0b77b5ebc844f603` | **SUCCESS**, A 10, B 31, comparison 12; original five-member TXT generated/verified/extracted and published |

All attempts have independent commit/run identities. Failures were in bounded disposable fixtures; no historic real Product/provider effects were replayed. Correction did not change Product behavior or force false effect-state parity.

## 3. Frozen original receipts and postpublication readback

**Portable original carrier:** `mauedgar/ts-execution-lab@11934b997c5c466dd480e914df535f928a7b12d1:transport/TS-BEADS-030-PARITY-20261029-001/EVIDENCE_CARRIER.txt`.

- Git blob `7a249a61fb16026ae507b7a702778a6656db916e`; SHA256 UTF-8 `e88a5ab182c4d1f34b5221568b27e997c2b8b41acc073f9b6577a90156a637be`; **20,485 bytes**.
- Existing `IR-TXT-CARRIER/1`, five members: `README.txt`, `control/PLAN.md`, `original/A_KERNEL.json` (SHA256 `21e4ef7c7697758208dbb3d0db531ec7efea1436e567f06c85bd18fc63a4a062`), `original/B_BEADS.json` (SHA256 `ec90186e86b6f29cc5cda7f0a532b0597bd2f06372ba4284acf17776abf1941a`), `original/RESULT030.json` (SHA256 `d36565472da4dd2dc37dde8e7440fe70ec10ab0cea41f8b9382880875382f32c`). Product `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`: project/verify/extract and byte-equivalence **PASS**.
- **Independent read-only postpublication verification:** [Actions 40882583821](https://github.com/mauedgar/ts-execution-lab/actions/runs/40882583821), job `123477743507`, source `5daca1deb677cafc0c8d95cc004fff13590bfad4`, **SUCCESS**. Reobtained the persisted immutable Git blob, checked 20,485 bytes/SHA256, ran Product verify and extract on **persisted bytes**, and checked each of three original result hashes and expected statuses. Log: `TS_BEADS030_PERSISTED_GIT_TXT=PASS;bytes=20485;five_members=VERIFIED;A_B_COMPARE=EXACT;Product=NONE`. This extra step addresses the 024 truncated-carrier lesson without rewriting 024.

## 4. True shared outcomes, and the material classification difference

The original Product Recipe was tested against synthetic but structurally competent evidence of the same five obligations and Developer/reviewer/effect authority references.

| Behavior | A — current original State Kernel | B — native Beads-first async port |
| --- | --- | --- |
| Preflight and full close | PASS / CONFIRMED; real Kernel filesystem journal | PASS / CONFIRMED; native Beads CAS and actual original Recipe |
| Five obligations | SATISFIED; TaskCycle CLOSED | SATISFIED; TaskCycle CLOSED |
| Attached authorities | reviewer, Developer, effect — same IDs | same |
| Attempt UNKNOWN before preflight | BLOCKED | BLOCKED |
| Wrong ACK after first obligation | FAIL / CONFIRMED, one satisfied and four pending, no close | same |
| Terminal retry | FAIL / NONE | FAIL / NONE |
| Concurrent attempt changes to UNKNOWN during obligation CAS | **UNKNOWN / UNKNOWN**, all five obligations remain pending | **FAIL / NONE**, all five remain pending |
| Direct inspect/readback | original Kernel event history | CLI native Beads readback |

**Why the race differs:** A uses a global event revision and sees a concurrent attempt's transition to UNKNOWN while evaluating the failure to satisfy a TaskCycle obligation; its original `invokeMutation` returns `UNKNOWN` conservatively because *the global state changed*. B's causal read-set guards both the exact TaskCycle root and the related attempt issue. Native batch refuses the stale gate revision; TaskCycle root remains unchanged, so the adapted Recipe can classify `NONE` in this fixture. This is *not* proof of global Product equivalence nor universal safety if an unenumerated dependency graph edge can be written behind the guard.

**Developer REJECTED gap:** A's fixture with valid Kernel snapshots and already-satisfied obligations returned original Recipe `READY` when the synthetic Developer evidence disposition was `REJECTED`; B likewise reproduces this pre-satisfied fixture behavior. This shows the behavior isn't a Beads-only bug. The fixture constructed state through valid Kernel APIs, but **does not prove a legitimate real Product lifecycle would ever supply that rejected evidence after acceptance**, nor that a historical unauthorized close occurred. Independent Product reachability and authority qualification remains open.

## 5. Real measurements; no false performance ranking

Run 5 original, **single cold timed positive execute each**, on the same Ubuntu runner and same Recipe/verified evidence:

| Metric | A | B |
| --- | ---: | ---: |
| Positive execute wall time | **32.555 ms** | **739.650 ms** |
| Kernel `read` calls | 56 | — |
| Kernel `verify` calls | 16 | — |
| Kernel `mutate` calls | 6 | — |
| Native Beads HTTP GET | — | 31 |
| Native Beads HTTP batch | — | 6 |
| Native Beads batch items | — | 13 |

These are implementation-dependent and only **one cold sample** each. A includes local filesystem journal fsync, while B uses native Beads/Dolt HTTP and independently guarded row updates. A/B counts are not directly equivalent operations, no error bars/variance, no real multi-agent load, and no measured production throughput. In this one experiment **A was numerically faster**, but no claim of a production winner or net maintenance cost is justified. The B implementation's 15 in-memory edits change 36,279 to 36,369 bytes (+90) with zero Product modules modified or deleted. State Kernel source footprint 36,715 bytes/4 files and adapter 12,020 bytes from 029 are not proven net deletable.

## 6. Experimental Control decision: PRIORITIZE B, retain blockers

- **SELECT B FIRST** for next bounded architecture and native lifetime research because the explicit user preference is Beads-authoritative design and 022–030 demonstrate the original closure consumer can retain required *bounded TaskCycle outcomes* with native transactions. This experimental selection supersedes previous A priority, not the competent Product architecture SOT.
- **DO NOT CLAIM AUTHORITATIVE PARITY YET**: global Kernel event/audit history, real provider UNKNOWN/ACK recovery, dynamic causal dependency discovery, all privileged writers, per-operation grants, multi-runner concurrency, installed Product consumer integration, and net module deletion still lack demonstrated equivalence.
- **MATERIAL WRITE GAP PRESERVED**: 023–028 show `bd dep add`, direct privileged CLI, same-UID token, and unauthenticated alternate server can mutate graph edges without root revision invalidation. A selected secure launcher doesn't prevent all privileged paths; B cannot yet safely become authoritative Product graph source.
- **PRESERVE AUTHORITY**: 030 PASS is a technical result, not Developer acceptance, Independent Review, Phase 2, source-of-truth update, or Product Kernel shutdown.
- **Next bounded B-first priority (not started):** `031` should qualify audit/history and external-provider effect identity + UNKNOWN recovery for an immutable native Beads TaskCycle, while explicitly testing privileged graph edge bypass with the same causal read-set (or proving the selected write boundary cannot be bypassed). Reuse native Dolt transactions, Git/Transport receipts, and existing permissions; do not add a global ledger, scheduler or role by default. Separate the developer REJECTED semantic reachability investigation under Product authority.

**Terminal disposition:** `030 COMPLETE_WITH_EFFECT_CLASSIFICATION_DIVERGENCE_AND_AUTHORITATIVE_MIGRATION_BLOCKERS`. Product/tools and shared Dolt remote unchanged.
