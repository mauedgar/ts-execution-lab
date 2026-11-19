# E3 A001 — independent reviewer outcomes and blind-source repair gate (2026-11-19)

**Responsibility** `TS-EE-E3-WEBINLINE-COVERAGE-20261119-001` (research NONPRODUCT). Authority Product NONE. No Product or Tecnotron source mutations. No reviewer restart/semantic retry.

## Immutable cohort A001

Fixture `ts-execution-lab@6f94f83c53bd9f57149a27039dedece9a0a1ed71`, tree `a9d9664c25ff9cdc2c43fd4b31f67cb7e2a664bf`. 17 required source files, 8 Control-only seeded defects, two negative controls, four inter-file relations. Four packet sources frozen with exact labels, full delimiter pairs; Control independently matched **17/17 actual source contents byte-for-byte** against packet sections. Control validation is distinct from reviewer semantic reads.

**Baseline** `TS-EE-E3-WEBINLINE-BASELINE-IR001-20261119-001-A001`, scheduled native task `6afeb26a6b8c8191bcb8604ccf935778`, provider run `e739add6-d2ec-832a-b27b-7939d6bd5ea7`, terminal `completed`. Original personal Library `libfile_0daa4da5353c819195a788e743eb66a8` / `file_00000000cbb8822fb8b016653d7be68a`, exactly **9,640 bytes**, SHA256 `0e00257c3cc4e27b337abddd4814247efe5b1308fc21b31f43924e6651f0b33c`. Byte-identical Git transport `mauedgar/ts-execution-transport@135b719dcc48b92981625f35937618374a89a6ac:results/TS-EE-E3-WEBINLINE-BASELINE-IR001-20261119-001/ORIGINAL.md`, blob `afc43dc0ed437175626d6754da9901d3ebec7ef6`.

**Adaptive** `TS-EE-E3-WEBINLINE-ADAPTIVE-IR001-20261119-001-A001`, scheduled native task `6afeb2823a94819194af48761466e1df`, provider run `ffe49ec4-14b0-8329-a86a-d6add9f437a6`, terminal `completed`. Library `libfile_2efdea3fcdc88191bcd462e8030b21e4` / `file_00000000f1ec81f7822d7b31c859dcbe`, exactly **10,561 bytes**, SHA256 `ff858fd4473025e80de85c24e24251cf4f3e4a93a29c48bb7ae758aa9dd82c98`. Byte-identical Transport `mauedgar/ts-execution-transport@9385cc7e5aebd52fd15de10f662d965f78039211:results/TS-EE-E3-WEBINLINE-ADAPTIVE-IR001-20261119-001/ORIGINAL.md`, blob `abb939cb24aaf0203ebef3e5dc33e171f0a55040`.

## Observed, not extrapolated

| Evidence | Baseline direct-Git | Adaptive four-pack |
|---|---|---|
| source bodies reviewer claims full read | 17/17 | 17/17 |
| source-supported seeded defects recognized | 8/8 | 8/8 |
| findings / advisories | 8F/2A | 8F/2A |
| negative-control false positives | 0/2 | 0/2 |
| four specified inter-file relationships | 4/4 | 4/4 |
| reviewer-executed tests | NOT_RUN | NOT_RUN |
| independently verified ORIGINAL Library+Git | PASS | PASS |
| blind source isolation | **FAIL** | reviewer reported no contamination |
| reviewer self-certified source bytes | 17 file-return blob IDs matched manifest | 17 packet labels matched manifest, individual original bytes NOT_VERIFIED by reviewer |
| provider observed task elapsed | 63.993 s | 61.103 s |

Elapsed timings are descriptive single-task provider records, NOT inference-only durations or calibrated performance. Baseline original reports 17 individual file reads grouped into three connector invocations, plus metadata/manifest/request retrieval; adaptive read four packet files. These are source acquisition units, not independently audited total tool-call counts; token count and billable cost UNMEASURED.

**Critical validity blocker:** the original fixture commit was built with `control/ORACLE_PRIVATE_DO_NOT_SEND_TO_REVIEWERS.json` in the SAME Git tree. The baseline reviewer fetched commit metadata and the plugin unexpectedly exposed a diff including that excluded truth. Reviewer itself preserved `BLINDNESS_COMPROMISED`; no reviewer claim of 8/8 counts as an unbiased baseline. Preserve both terminal originals, do not redo A001. The peer reviewer's non-contamination does NOT remove baseline contamination or prove causal superiority.

## Authorized B002: new blind Git subject, not a retry

To repair protocol, a **distinct** fixture Git subject `mauedgar/ts-execution-lab@ed1e6e50402d74926821cce28f7e435989dc18c4`, tree `0e5fe46cbc65afdcb40f5f3d7770f36124225a92`, was created from unrelated `main@935ba9ff1dd2d06a39fb4b454125a51cfc4bbaa9`. Its commit diff contains exactly 17 fixture paths, reusing **the same 17 blob IDs**; no control/oracle path in its tree, commit diff or ancestry. Four packet wrappers were transformed from prior verified sources by changing only provenance labels; native Git readback verifies **17/17 unchanged file bodies**. New pack commit `c1cbc77e16d3df8b645fc6d793108db67588915d`; manifest commit `251f84ec2d4f73ffe328396c565eb3a534035622`.

Two **new and distinct** review interfaces were frozen on Transport for B002, not under A001 identities:
- `ts-execution-transport@f2f7defa6ed36e9ce76f7f3df2e4bf58e24c72cc:requests/TS-EE-E3-WEBINLINE-COVERAGE-20261119-002/BASELINE_FROZEN_INPUT.md`, blob `3b1b4494d59f0b125ac7f0886403c6d1218a92e8`.
- `ts-execution-transport@4202fcd9dc7a50da737d202718ebf5ceed01711c:requests/TS-EE-E3-WEBINLINE-COVERAGE-20261119-002/ADAPTIVE_FROZEN_INPUT.md`, blob `6b329285952e64e4d47d7aaa4e776a16e291675f`.

Prospective native one-shot scheduled tasks accepted:
- B002 baseline `6afeb57ba5f481918b57ab1a5181cddb`, original `TS-EE-E3-WEBINLINE-BASELINE-IR002-20261119-002-A001`.
- B002 adaptive `6afeb58e24a8819184171bae77c77015`, original `TS-EE-E3-WEBINLINE-ADAPTIVE-IR002-20261119-002-A001`.
Pre-dispatch check: 0 other enabled tasks, no matching prior attempts, both expected Git ORIGINAL destinations returned 404. Their creation is `SCHEDULED` only, not an inference/review result; reconcile exact provider state once at meaningful join, preserve reviewer ORIGINAL bytes and Library custody.

## Technical decision ceiling

- `A001_BOTH_TERMINAL_AND_ORIGINAL_PUBLISHED / A001_COMPARISON_INVALID_BLINDNESS`.
- `B002_SOURCE_AND_PACKS_QUALIFIED / B002_REVIEW_PENDING_NATIVE_RESULT`.
- No automatic Product adoption, no mandatory Reviewer binding, no A001 reexecution, no merged candidate changes, no paid provider calls.
- Any method recommendation after B002 must separate coverage evidence, defect recall/false positives, source byte custody, transport custody and fairness. Two small cohorts are descriptive, not universal proof of optimality.
