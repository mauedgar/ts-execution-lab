# TS EE E3 — B002 terminal blind comparison and technical disposition (2026-11-19)

**Responsibility:** `TS-EE-E3-WEBINLINE-COVERAGE-20261119-001`, continued under distinct blind subject B002. **Status:** `B002_TWO_NATIVE_TERMINALS_PASS_CUSTODY / SYNTHETIC_CONTEXT_METHOD_OBSERVED / TECHNICAL_SELECTION_NONPRODUCT_ONLY`. Product authority/effect NONE. This is a *method experiment*, not Tecnotron or Aware Independent Review acceptance.

## SOT and subject

The two original A001 reviewer attempts are terminal, preserved byte-identically, and **never rerun**. A001 baseline explicitly reported `BLINDNESS_COMPROMISED`: provider Git commit metadata unexpectedly exposed the Control oracle in the same candidate commit's diff. The A001 method comparison is statistically/causally invalid for blind defect recall. Keep the original terminal findings, not a retroactive PASS.

**Independent new B002 subject**: `mauedgar/ts-execution-lab@ed1e6e50402d74926821cce28f7e435989dc18c4`; exact tree `0e5fe46cbc65afdcb40f5f3d7770f36124225a92`, parent is the clean `main@935ba9ff1dd2d06a39fb4b454125a51cfc4bbaa9`. Git commit diff is **exactly 17 source files** under `experiments/TS-EE-E3-WEBINLINE-COVERAGE-20261119-002/fixture/`; no Control oracle or related truth file in this commit/tree/ancestry. All 17 source file **Git blobs are identical** to prior A001 fixture source; no fixture code change. The legacy Control oracle is independent in an excluded branch/commit `6f94f83c53bd9f57149a27039dedece9a0a1ed71`, Git blob `c85ff6f380d8486ec4538aa077973df167f92b6d`; **not delivered** to reviewers.

New 4-packet Git commit `c1cbc77e16d3df8b645fc6d793108db67588915d`; manifest commit `251f84ec2d4f73ffe328396c565eb3a534035622`. Independent Control readback verified the four new packets are **identical to the original 17/17 source-verified packet bodies except for source commit/round wrapper labels**. Packet boundaries: 5+4+5+3; zero missing/altered source bodies.

## Exact native B002 attempts and immutable ORIGINAL custody

**Baseline direct-file**:
- Review ID `TS-EE-E3-WEBINLINE-BASELINE-IR002-20261119-002`, Attempt `TS-EE-E3-WEBINLINE-BASELINE-IR002-20261119-002-A001`.
- Frozen input `mauedgar/ts-execution-transport@f2f7defa6ed36e9ce76f7f3df2e4bf58e24c72cc:requests/TS-EE-E3-WEBINLINE-COVERAGE-20261119-002/BASELINE_FROZEN_INPUT.md`.
- Native one-shot automation `6afeb57ba5f481918b57ab1a5181cddb`, provider run `2817fd6d-2374-832d-8d81-01ebd78ce2a3`, terminal `COMPLETED`; no replay or write by reviewer.
- Personal Library `libfile_4a094defd14081918ae41643525769b6`, `file_000000000f2481f5bf868efeba27fd9c`, materialized and SHA verified, **9,153 bytes**, SHA256 `74dbec3810a2a20f61e202b08de419922b2a06a533d69c6e1d01a22a691715b3`.
- Git original `mauedgar/ts-execution-transport@f9ca74d5601c02d49ba6d63dd213fec24307300d:results/TS-EE-E3-WEBINLINE-BASELINE-IR002-20261119-002/ORIGINAL.md`, **identical** Git blob `79eed46ef08fde6d6af58c2c5d3fea7d954cfcea`.

**Adaptive 4-packet**:
- Review ID `TS-EE-E3-WEBINLINE-ADAPTIVE-IR002-20261119-002`, Attempt `TS-EE-E3-WEBINLINE-ADAPTIVE-IR002-20261119-002-A001`.
- Frozen input `mauedgar/ts-execution-transport@4202fcd9dc7a50da737d202718ebf5ceed01711c:requests/TS-EE-E3-WEBINLINE-COVERAGE-20261119-002/ADAPTIVE_FROZEN_INPUT.md`.
- Native one-shot automation `6afeb58e24a8819184171bae77c77015`, provider run `8ce09d0d-9f50-832a-aee3-ac9c644ad805`, terminal `COMPLETED`; no replay or reviewer write.
- Personal Library `libfile_52fca283d0cc8191abb29bb276f3abac`, `file_00000000193481f8b0ec6cc335076a05`, materialized and SHA verified, **8,933 bytes**, SHA256 `76c9a550f20c6df7984f320ac3f81857272604c7b3af626e98645b51a2987c28`.
- Git original `mauedgar/ts-execution-transport@c1d3bfbe214d0509b6d0832bee405d0f9d643bd8:results/TS-EE-E3-WEBINLINE-ADAPTIVE-IR002-20261119-002/ORIGINAL.md`, identical Git blob `617c33bfa39335decd61f6b2f0b84a383db5d965`.

Both originals were actually submitted to Library by the separate reviewers (reported `status=succeeded`), independently materialized by Control, compared by SHA256 and Git blob identity, then published **create-only** after exact Git target absence observation. `LIBRARY_VERIFIED / GIT_BYTES_IDENTICAL`. No new inference or review was run for transport recovery.

## Evaluator-only oracle reconciliation

Control oracle exact 8 seeded defects: color omitted from SKU; overprecision rounded; equal-stock reservation rejected; publication allowed by images OR approval; logged-in nonADMIN edits; city ignored in availability; phone/name logged; stale older search overwrites newer. Negative controls: WhatsApp URLSearchParams encoding and HTTP fetch validation/defensive copy. Four interfaces: SKU↔catalog, approval↔catalog, roles↔catalog, stock↔availability↔checkout.

| Metric | Direct Git baseline B002 | Four-pack adaptive B002 | Evidence/limits |
|---|---:|---:|---|
| semantic `FULL_READ` with first+last source observations | 17/17 | 17/17 | original source ledgers; not merely hashes |
| seeded defect recall (Control adjudicated) | 8/8 | 8/8 | 8 shared underlying causes, IDs normalized against hidden oracle |
| false positives on 2 benign modules | 0/2 | 0/2 | both explicitly recognized WhatsApp/HTTP as safe |
| findings reported | 9 | 9 | each 8 seeded plus distinct additional observation; don't count 9/8 recall |
| advisories reported | 3 | 2 | separate quality/robustness and coverage warnings |
| cross-file reasoning | >=4 | >=4 | four or more grounded interface relationships |
| runtime tests | NOT_RUN | NOT_RUN | source-only assessment, no CI/run claims |
| reviewer original custody | PASS | PASS | actual Library+byte-identical Git originals |
| blind Git subject | no oracle in commit/tree/diff, no exposure reported | same, no exposure reported | no provider-internal memory isolation guarantee |
| source units retrieved | 17 individual files | 4 whole packets | not proven host tool-call count or tokens |
| provider task elapsed (descriptive) | 72.523 s | 93.101 s | provider run timestamps; no calibrated speed or same internal reasoning efforts |
| paid cost/token usage | UNMEASURED | UNMEASURED | no billing proof or price attribution |

**Extra nonseeded finding nuance:** direct-file `F09` is the checkout consequence of already seeded location leakage `S06`, **not an additional independent root defect**. Four-packet `F09` instead observes that failed multi-line quotes return partially decremented *local copied stock*, while not mutating original inventory. This is a **plausible interface-state contract/robustness issue**, unseeded and not independently runtime-qualified; do not automatically count it as a false positive or ninth seeded cause. Candidate for future negative test outside this blind comparison, only if competent research scope includes it.

## Technical determination

1. **`VERBATIM_PACK_SOURCE_FIDELITY: QUALIFIED_BOUNDED_NONPRODUCT`** for these 17 files and four packets. Creation and readback are exact; source pack can reduce source retrieval units while preserving reading opportunity.
2. **`WEB_INLINE_SOURCE_COVERAGE: OBSERVED_17_OF_17_BOTH`**, source-only, distinct fresh contexts, originals immutable. 8/8 known source defects in each valid B002 review; no negative-control false positives.
3. **`ADAPTIVE_SUPERIORITY: NOT_DEMONSTRATED`**. This small 17-file fixture was manageable for direct Git. Adaptive used fewer *source retrieval units* but recorded longer provider elapsed in B002. Actual total model tokens, reasoning effort, costs, network tool calls and distribution not independently comparable; no universal benchmark inference from two tiny cohorts.
4. **`BLINDED_SOURCE_COMMIT_RULE: RECOMMEND_METHOD_BOUNDARY`**. Control oracle must be absent from reviewer subject commit, diff, tree and ancestry, not merely omitted from prompts. A001 proves a real regression if not isolated; B002 demonstrates the repair can support two clean attempts.
5. **`IR_READ_COVERAGE_LEDGER: RECOMMEND_OPTIONAL_OPERATIONAL_METHOD`**. Always distinguish fetched vs semantically read; require path+blob, concrete early/late evidence, missing paths and cross-file checks. Use bounded context packs **conditionally** when actual source breadth/context exceeds reasonable complete single review. Smaller IR shards with explicit integration risk when impossible; not a blanket requirement.
6. **`TECNOTRON_CANONICAL_ADOPTION: NOT_GRANTED`**. No Product acceptance, no new canonical Recipe/Primitive, no modification to shared Review SOT. Present candidate to competent Control separately.

**Current responsibility outcome:** E3 gate `CLOSED_BOUNDED_EXPERIMENTAL` with valid B002 results and preserved invalid A001 caution. Do NOT run more E3 reviewer attempts merely to obtain a different metric. Next independent EE method work may evaluate E2 Browser QA from existing handoff, then E1 web-native execution; neither is implicitly authorized Product implementation. Product effects NONE.
