# TS EE — Independent WEB_INLINE IR001 | OpenCode2 free preliminary reviewer fallback

**Review_ID:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-20261113-001`  
**ExecutionAttempt:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-A001` (reserved; NOT_DISPATCHED)  
**Responsibility:** independent source-only qualification of an experimental GitHub Actions fallback, not a Product review.  
**Review mode:** `WEB_INLINE / STRICT_READ_ONLY / FRESH_SEPARATE_CONTEXT`.  
**Product authority:** NONE. No Code/Actions execution, no merges or acceptance.  
**Subject:** `mauedgar/ts-execution-lab@0288f0cb7e3f950274fbe69bd044e7a2d1c569f1`  
**Tree:** `05a5df089a6043786179e70b50b05e59e196894b`  
**Diff base:** `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`  
**Frozen source ownership:** this branch is candidate-only and cannot by itself qualify native OpenCode2 runtime permissions, model pricing or Actions dispatch.

## Required frozen source reads

Read ONLY exact Git snapshot and relevant already-canonical EE constraints:
1. `tools/ts_ee_oc2_free_review_fallback_preflight.py` — Git blob `e9a21324637c0fddf49e0717d063be8fa227af2c`.
2. `.github/workflows/ts-ee-oc2-free-prelim-review-fallback.yml` — Git blob `4497ee5810090b1eec89e319ca4aa24ea76f97b9`.
3. `docs/execution-engineering/research/TS-EE-OC2-FREE-PRELIM-FALLBACK-20261113-001/OPERATING_DISPOSITION.md` — Git blob `5d72b24da82d8ea53346ccefba964a70d309e880`.
4. Canonical `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`, `docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md` and Runner v0.2 fallback evidence at the SAME immutable subject revision. These establish governing semantics, not the candidate's correctness.
5. Reference only when material: historical OAuth pilot workflow and OpenCode2 hard-deny candidate, to check reuse vs false claims.

## Mandatory independent review questions

- Does `workflow_dispatch` stay manual-only with no `pull_request`/`pull_request_target`/scheduled triggers? Is branch/main gating truly inert before competent adoption, and are GitHub Actions permissions/credentials safe?
- Can the input/local receipt contract be forged, stale, collided, or be an in-progress/UNKNOWN attempt? Does current GitHub current-state/TOCTOU behavior permit remote execution in conflict with notebook work? Are exact input/operation/attempt/baseline identities preserved?
- Is `BLOCKED_CAPACITY / effect_state=NONE / inference_started=false` actually enforced before any paid or external model call? What empirical observation is still missing? Does notebook overload while an inference is already running correctly block fallback?
- Review Python source for syntax, path safety, Git read-only commands, trust boundary, unwanted writes, expected schema and proof freshness; try read-only thought-through negative cases. Do NOT execute unqualified workflows or model calls.
- Review YAML for syntax/quoting/expression expansion, action SHA versions, checkout and diff behavior, source cleanliness, output custody, steps skipped/always semantics, npm install provenance, artifact semantics and CLI arguments (standalone, agent, file).
- Verify the selected models are clearly **non-OpenAI** and currently listed as free, with NO GPT quota, NO API paid fallback, NO OpenRouter balance spend. Check title/compaction/side calls, provider restrictions and cost-qualification assumptions. A catalog listing is not native provider proof; free model retention/privacy may limit Product use.
- Are policy/permission semantics for OpenCode V2 correct and are effective runtime hard-denies actually unqualified? Can an untrusted diff inject behavior? Does the lack of secrets materially constrain review?
- Is the notebook-first parallel plan realistic: one reviewer slot initially, disjoint worktrees, resource-observed admission, exact deferred durable join, no Commander polling, no arbitrary timeouts or active-operation duplicate?
- Does the Actions code currently restrict **only** `ts-execution-lab` and prevent unauthorized Product effects? Any dependency on G3 CLI Catalog? (Should not depend.)
- Is `PASS` of preliminary reviewer explicitly NOT an IR verdict, Developer acceptance or Product integration? Are originals, hashes, outputs and later Web IR boundaries clear?
- Identify missing static/negative tests and runtime qualification before promotion to main, and distinguish blockers from advisories.

## Output contract

One complete `IR001_ORIGINAL` with:
- Review_ID, ExecutionAttempt, exact subject commit/tree/base and all input Git blobs verified;
- independence evidence (separate context, no work), actual checks and explicit limitations;
- verdict `RECOMMEND_SOURCE_ONLY` or `NO_RECOMMEND` or `BLOCKED_SOURCE`;
- ALL `Fxx` blocking findings and `Axx` advisories with severity, exact file:line, mechanism, evidence and bounded repairs;
- whether this SOURCE candidate is acceptable at 0 findings/0 advisories, without pretending operational runtime approval;
- possible regressions, missing negative tests, raw sources and next competent disposition;
- `Product_effect: NONE`, `Actions_dispatch: NONE`, `Provider_model_calls: NONE`.

Reviewer must NOT modify the candidate, open/merge a PR, create a Product TaskCycle, spend LLM provider tokens in OpenCode, run Actions, self-accept, or reuse the implementer's analysis as independent assessment. If evidence is unavailable, report `BLOCKED_SOURCE`, not PASS.

**Original custody:** if executed by a one-shot scheduled WEB_INLINE task, the actual scheduled prompt MUST embed the full mandatory Library-upload and fail-closed clauses from `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` with verified placeholders. A reference to this frozen file alone is not enough. If executed in a new interactive chat, provide the complete original in that separate context and let competent Control verify the source and return it. No scheduled task is created by this document.

**Status:** `FROZEN_REQUEST / NOT_DISPATCHED`. Acceptance and integration stay with competent TS EE control after an independent result. The prior historical IRs and the Notebook/Actions operations are neither dispatched nor altered.
