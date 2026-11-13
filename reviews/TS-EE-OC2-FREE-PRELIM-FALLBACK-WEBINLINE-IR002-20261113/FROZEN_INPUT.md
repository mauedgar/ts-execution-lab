# TS EE — WEB_INLINE Independent Review IR002 / source preparation only

**Review_ID:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR002-20261113-001`  
**ExecutionAttempt:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR002-A001` (reserved, NOT_DISPATCHED)  
**Binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH_SEPARATE_CONTEXT / SOURCE_ONLY`  
**Authority:** TS EE experimental source method, Product NONE, no actions/workflow/inference permission.  
**R002 subject:** `mauedgar/ts-execution-lab@c07112e4031ca970aff2b4054229989508379e7b`  
**R002 tree:** `346389269fa09841d01a0a49bb3f2c4991d2b11b`  
**Base:** `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`  
**Branch:** `experiment/ts-ee-oc2-free-review-fallback-20261113-001`, not main.

## Exact frozen R002 sources

1. `tools/ts_ee_oc2_free_review_fallback_preflight.py` — Git blob `c82d6ca8ad7c1f9f70c82f4b23890debda909abc`.
2. `.github/workflows/ts-ee-oc2-free-prelim-review-fallback.yml` — Git blob `f952aab0cfae8439d85e8511c71d33e0bcfb1f93`.
3. `docs/execution-engineering/research/TS-EE-OC2-FREE-PRELIM-FALLBACK-20261113-001/OPERATING_DISPOSITION.md` — Git blob `df1b9c6d850f704d4b9948d11f8d6de7d0f6c069`.

## Prior IR001 preserved

Original `NO_RECOMMEND / 7F / 6A` for initial unsafe candidate `0288f0cb7e3f950274fbe69bd044e7a2d1c569f1`:
`mauedgar/ts-execution-transport@5d27d494c9ce027eb04c1a03783555723961d18e:results/TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-20261113-001/ORIGINAL.md` (blob `974f024b0496039ac3dba49037794a0344955068`, SHA-256 `e1e47e7104ce246c3742bd6729be2cad8baa54c5ae25c6d58506c3cc121ae612`).

R002 replaces its unqualified LLM workflow with a **dormant, manual-only, deterministic, ALWAYS-DENY admission candidate**. Do not grade this as a functional OpenCode reviewer; its explicit DoD is *safe source preparation* for a later Developer-authorized runtime qualification.

## Independent reviewer questions

- Verify R002 commit/tree and blobs directly, without relying on the implementer's claims. Check scope and differences from IR001, not just the R002 summary.
- Are all actual workflow triggers manual-only? Is the branch staging inert? Can a hypothetical future `workflow_dispatch` call any LLM, provider, npm install, untrusted diff upload, or Product write?
- Does `github.workflow_sha` pin the control checkout to the workflow source as officially documented? Is the Python script Git blob check and `EXPECTED_WORKFLOW_SHA` shell binding correct, and do they fail closed on mismatch?
- Is the Python script syntactically valid, fail-closed on missing Git roots, malformed ref, duplicate JSON key, dirty checkout, wrong base/head/tree, wrong receipt identity, or receipt absence? Can it ever return an admission success or make a network/model call/write? Check dangerous path escaping and stdout leakage.
- Is it still possible to confuse a self-authored notebook `BLOCKED_CAPACITY / NONE` report with provider-native process liveness? Confirm the candidate **never** trusts it sufficiently to enable fallback.
- Does source-only preparation falsely claim that OpenCode provider pricing, permissions, CLI packaging, runtime negative tests, free model policy, notebook process fencing, privacy or credentials are qualified? These remain future mandatory Developer gates.
- Is there any latent path from this staging branch to an active workflow, PR comments, Product effects, artifacts presented as a review, or automatic paid model selection?
- Assess inherited F01–F07/A01–A06: classify each as **resolved by code**, **neutralized by narrowed scope**, **still-blocking for SOURCE_ONLY**, or **future runtime qualification**. Do not consider a future unqualified model an accepted source implementation.
- Identify needed deterministic tests, assertions, or documentation updates for source-only 0F/0A; no speculative claims of tests not executed. Independence and evidence must be explicit.

## Required result

Return exactly one complete `IR002_ORIGINAL` with Review_ID/ExecutionAttempt, original commit/tree/base and verified blobs, independent fresh-context evidence, coverage, actual test scope, `RECOMMEND_SOURCE_ONLY` or `NO_RECOMMEND` or `BLOCKED_SOURCE`, ALL blocking Fxx/advisory Axx with file:line, evidence and bounded repairs, regression disposition against IR001, and next competent gate.

The result must state `Product_effect=NONE`, `Actions_runs=NONE`, `OpenCode_model_calls=NONE`. Do not modify any source, run code/provider or Actions, self-accept the candidate, touch Product or open PRs.

**Library custody:** If this IR is run via a one-shot scheduled WEB_INLINE task, the actual task prompt MUST include the complete required Library upload/receipt/byte verification and fail-closed clause from `docs/execution-engineering/TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md`, not just refer to this handoff.

**Status:** `FROZEN_SOURCE_IR002_REQUEST / NOT_DISPATCHED`. Even 0F/0A on R002 would not authorize live reviewer execution.
