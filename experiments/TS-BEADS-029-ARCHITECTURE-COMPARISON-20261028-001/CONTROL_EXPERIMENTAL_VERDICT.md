# TS — Beads 029 | Dictamen de Control experimental: comparación económica sin equivalencia ficticia

**ID:** `TS-BEADS-029-ARCHITECTURE-COST-COMPARISON-20261028-001`  
**Fecha:** 2026-10-28.  
**Estado terminal:** `COMPLETE_WITH_MEASURED_SOURCE_BOUNDARIES_AND_UNMEASURED_NET_REPLACEMENT_COST`.  
**Resultado mecánico:** `PASS_MEASURED_SOURCE_FOOTPRINT_WITH_NONCOMPARABLE_RUNTIME_TELEMETRY`; **16/16 controles PASS**.  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`, no Product adoption/TaskCycle/Independent Review/Developer grant/Phase 2; no Product or shared Dolt effects.

## Competent subjects and provenance

- Product frozen for measurement: `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`. The active architecture/ownership SOT retains State Kernel `NARROW`, disposition `UNDECIDED`, with active runtime consumers and conformance required before removal.
- Lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`, isolated branch `experiment/beads-029-architecture-cost-comparison-20261028-001`. Shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` intact.
- Prior native 022 `@32f86383c979ba015024d0e70ccd98c61858e132` original RESULT; 024 original JSON recovered from `@4a2511e1fa02858b765715ac76e7d19a32aa67da`; 028 fully qualified original envelope `@9e8016004ef5d3ca74abd67914d8e1a03ffcd851`. None of these effects was retried; 029 performs deterministic source inventory and evidence reuse, **not a new native A/B latency benchmark**.

## Attempt history and original receipt

- Attempt 1: [Actions run 40787563446](https://github.com/mauedgar/ts-execution-lab/actions/runs/40787563446), source `fd4139737d5d46e611dbd6ef8cad582a76a6e973`, **FAIL** before source measurement: qualified Product `review_txt_carrier.py verify` found `truncated member payload` in historical 024 TXT. No new Product/provider effect.
- Attempt 2: [Actions run 40787776443](https://github.com/mauedgar/ts-execution-lab/actions/runs/40787776443), job `123165197893`, source `ca953402f27c866b284ee73d5286e372f09d574b`, terminal **SUCCESS**. It preserved the 024 negative, recovered only its intact original JSON member with exact `sha256=cddc0b9bf943e6d3edffb64d9526ae73e33195145ecb3ed08ec37c503c06c9b3`, verified/extracted the complete 028 TXT, measured Product source, and published the complete 029 TXT.
- Original verified `IR-TXT-CARRIER/1`: `mauedgar/ts-execution-lab@c89158d907341c6ab30f8ee3bfaf5097a2a62db4:transport/TS-BEADS-029-ARCHITECTURE-COMPARISON-20261028-001/EVIDENCE_CARRIER.txt`, Git blob `43042ffdfc843be89a9e5536a0b0a47b968aba73`, original UTF-8 SHA256 `b7a4334162369cf66be9aa747ead62aa37a497e7c755e2266cf4044c23c4a694`, 13,872 bytes. Three original members: `README.txt`, `control/PLAN.md`, `original/RESULT029.json` (sha256 `f22524821730653c731ace9b19c6d1323c778e577160670b796ebeb0a1a8e08b`). Reused qualified Product TXT projector/verify/extract, exact byte equivalence PASS. No ZIP delivery.
- No Product writes, no Dolt shared writes, no TaskCycle reinitialization, no imported external authority.

## Product code footprint, measured on exact frozen repository

Product source sample: 111 JS/TS/MJS source files under `src/` and `src-typescript/`, 56 JS/TS/MJS test files under `tests/`.

| Existing component | Files | Lines | UTF-8 source bytes | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `src/state-kernel-v0/` | 4 | 481 | **36,715** | Existing authoritative implementation footprint, **not savings** |
| `src/operational-spine-v0/state-kernel-adapter.js` | 1 | 368 | **12,020** | Binding to lifecycle; replacement would need equivalent semantics |
| `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js` | 1 | 1,008 | **36,279** | Product evidence/authority/UNKNOWN handling; **cannot be dropped** merely by adopting Beads |
| `src/core/run-store.js` | 1 | 158 | **4,752** | Separate mechanism; SOT already classifies RunStore as conditional absorption candidate, not proven redundant with Beads |

The mechanical scan found **10 source files containing State Kernel tokens/symbols**, including **3 internal kernel files**, TypeScript declarations and active invocation/adapter files; **7 test files** reference them. This is a conservative contact-surface inventory, not 10 distinct consumer migrations or a lower-bound on implementation work. In particular, `RESULT029.json` contains a legacy field `installed_consumer_binding_touch_points_lower_bound: 10` which **must be interpreted as total matching source files, including internal Kernel files**, NOT 10 external importers or proven mandatory edits. No claims of physical deletion, net LOC reduction or cost saved are supported.

## Measured prior native costs, which are NOT commensurable across A/B

- **022 / Option B internal optimization:** same original synthetic consumer workload: 127 native HTTP calls with extra version-acquisition batches versus **73** with GET native revision and scoped CAS; 54 fewer, **42.5% fewer calls**. The optimized full suite included an extra race (11 GET + 3 batches), resulting in 87 total; normalized matched workload is 73. Not a performance comparison with Option A nor throughput/latency proof.
- **024 / Option A informational reader:** original intact JSON reports **41 GET requests across 5 read-model rounds**, four classified samples, 18 checks. Detects concurrent edge expansion and ancestor version change without Product authority, but two equal scans are **not an atomic snapshot**. These GETs are from a different suite, not directly comparable to the 022 full lifecycle.
- **028 / Option B security constraints:** original fully verified JSON reports 35 checks, **41 native routes, 20 writes protected under bearer in the selected service**, but privileged native CLI and unauthenticated alternate start can still mutate an edge without incrementing root revision. This is a **measured safety blocker**, not a hypothetical performance tax.

## Architecture comparison and decision

**A — Beads informational/read-only + current Product authority**
- Strengths: native graph/ready/status for observability and operational projection; 024 already provides an isolated nonauthoritative read model and race detection; Product authority, effect reconciliation, historical contracts and State Kernel remain unchanged. Reader can use SELECT-only SQL; no extra privileged Beads mutator is necessary to implement these observational capabilities.
- Constraints: no automatic Product TaskCycle decision from Beads; no measured Kernel deletion; adding a read projection to a Product runtime requires its own authorized consumer selection. No claim that a new persisted projection was installed.
- **Control experimental disposition:** `PREFERRED_NEAR_TERM_EXPERIMENTAL_INCREMENT` because it adds informational value without requiring unresolved authoritative writer invariants.

**B — Beads-first authoritative state with isolated writer, eventual Kernel replacement**
- Strengths: native Dolt versions, scoped async read sets, transactions and graph semantics; 022 has a real Product consumer adapted **in-memory** with native synthetic positive/negative cases, and clear HTTP read-set optimization. Potential to replace or absorb current Kernel/adapter responsibilities once equivalence is proved.
- Material obligations: all causally relevant edge mutations must invalidate the root/read set or fail closed; the protected launcher is bypassable by privileged CLI/other native serve; identity and credential security must survive recovery, concurrent writers and external effects; Developer acceptance `REJECTED`, IR and `UNKNOWN` semantics need full independent source-native equivalence; installed consumers and history require migration plan.
- Quantitative uncertainty: **net Product lines deleted = 0 currently**; net maintenance effort, production latency, operational overhead and future source footprint **UNKNOWN**. The 36,715 kernel bytes and 12,020 adapter bytes are not safe automatic savings, and original closure Recipe semantics must survive.
- **Control experimental disposition:** `PREFERRED_LONG_TERM_DESIGN_HYPOTHESIS_WITH_MATERIAL_CONFORMANCE_BLOCKERS`, **NOT READY FOR AUTHORITATIVE PRODUCT ADOPTION**. This does NOT freeze existing SOT choices forever, but replacement needs proper Product decision after independent evidence.

## Separate integrity debt — historical 024 carrier

The Git-backed 024 `IR-TXT-CARRIER/1` has **27 fewer bytes** in `selection/PLAN.md` than declared by its manifest (expected 2,937; actual 2,910). Original valid prepublication projection/verify/extract in the 024 workflow does not prove the Git blob persisted identical. Product verifier correctly rejects the Git version. Original 024 JSON member has exactly 5,767 bytes and its declared SHA256, and was recovered only as a **verified member**, not a verified whole envelope. No historical file was rewritten; no fabricated validity. The cause of the loss (publication, text conversion, or other) remains **UNDETERMINED**. For future handoffs, verify the **Git-persisted** carrier after publication, not only the local precommit bytes. Independent transport-integrity research may continue without holding unrelated Product work.

## Final recommendation and next bounded experiment (not started)

1. **Do not adopt B authoritatively now.** Prefer A for near-term isolated exploratory read-only usage while preserving full freedom to rearchitect Product later.
2. For a meaningful future A/B migration decision, select **030**: same bounded *Product consumer* fixture against two isolated ports (A: existing Kernel + informational Beads read, B: async Beads-first causal store guarded write) with identical receipt/authority constraints, measure wall-time, read/write counts and actual code diff including tests; include privileged-bypass negative, security/recovery and identical semantic outcomes. Decide only on evidence; don't introduce new Product tasks or an unnecessary scheduler.
3. Keep the Developer `REJECTED` source-native semantic gap from 023 separate; neither A nor B changes Developer grant.
4. Record 024 carrier persistence defect as transport-only debt; require postpublication exact Git blob byte-length/SHA roundtrip in future experiments.

**Terminal:** `029 COMPLETE_WITH_MEASURED_SOURCE_BOUNDARIES_AND_UNMEASURED_NET_REPLACEMENT_COST`. Product and shared Dolt verified unchanged.
