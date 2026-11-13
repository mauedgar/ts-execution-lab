# TS EE — OpenCode2 preliminary free reviewer / notebook-first fallback to Actions

**Artifact:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-20261113-001`  
**Status:** `CANDIDATE_PREPARED / NOT_DISPATCHED / WEB_INLINE_IR_PENDING`  
**Authority:** `TS_EXECUTION_ENGINEERING` experimental execution-method only; `Product_authority: NONE`, `Product_effect: NONE`.  
**Source baseline:** `mauedgar/ts-execution-lab@dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`.  
**Branch:** `experiment/ts-ee-oc2-free-review-fallback-20261113-001`, isolated from `main`.

## Reuse-before-build reconciled

1. `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`: single dispatch, exact provider receipt, deferred durable join, no retry for UNKNOWN. Preserve across execution hosts.
2. `experiments/TS-EXECUTION-RUNNER-V0.2-001/PARALLEL-IMPLEMENTATION-PLAN.md`: disjoint worker write-sets, execution identity, serial integration, no generic orchestrator.
3. `experiments/TS-EXECUTION-RUNNER-V0.2-001/QUALIFICATION-EVIDENCE.json`: local→remote fallback semantically qualified for a **deterministic** profile after `effect_state=NONE` and a NEW ExecutionAttempt. This does **not** qualify a new LLM reviewer automatically.
4. `docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md`: root/worktree/terminal separate, visual observation is not Product acceptance; keep UNKNOWN worktrees, no cleanup by age.
5. `.github/workflows/opencode-ci-oauth-pilot.yml` and Actions runs `38936506835`, `38940429153`: existing OpenCode CI transport/run feasibility (OAuth pilot), **not** proof of free model or reviewer.
6. `docs/execution-engineering/research/TS-EE-STACK-GATES-20261102-001/`: OpenCode2 hard-deny policy candidate; 16/16 static assertions, runtime tool-denial unqualified. The current branch reuses design only, not an established runtime PASS.
7. `docs/execution-engineering/TS-WEB-INLINE-INDEPENDENT-REVIEW-BINDING-v0.md`: a separate `WEB_INLINE` review is the competent IR surface; a preliminary OpenCode2 result never substitutes for it.

## Routing decision — notebook first

- Primary binding: **notebook / WSL Ubuntu / OpenCode2 in visible Orca terminal**, exact isolated worktree per attempt. Do not use Codex Cloud or any OpenAI/GPT-backed LLM for this preliminary reviewer.
- Local concurrency: **one active preliminary LLM reviewer slot initially**, not a claim that the notebook can sustain three simultaneous LLMs. Other independent implementers or deterministic tests may run with disjoint write-sets **only when live CPU/RAM/swap and active-process evidence show adequate capacity**. Do not kill or starve productive processes to make room. No unqualified universal resource threshold.
- One operation cannot be active on notebook and Actions at the same time. Prefer the notebook while healthy; waiting or an exceeded ETA is not evidence that its effect is NONE.
- If notebook preflight detects resource overload **before any semantic model invocation/process** and emits `BLOCKED_CAPACITY / effect_state=NONE` with a durable original receipt and no active semantic attempt for this operation, Control **may decide** to admit a **new** Actions ExecutionAttempt for the SAME frozen operation/request/subject.
- If the notebook model already started, is RUNNING, FAILED after a possible effect, or any effect is `UNKNOWN`: **no fallback** until exact competent reconciliation. No blind retry or duplicate review.
- Actions is **manual** `workflow_dispatch` only. An auto-fallback daemon or scheduled failover is NOT authorized.
- The single shared original request SHA-256, subject base/head, Product operation and model criteria are preserved. The remote `ExecutionAttempt` ID must differ from the notebook attempt ID. This is a change of execution surface, not a new semantic task.

## Experimental Actions candidate — NOT ACTIVE

Files (this isolated branch only):
- `.github/workflows/ts-ee-oc2-free-prelim-review-fallback.yml`: manual input gate, subject checkout, static preflight, non-OpenAI free-model review and Actions evidence artifact, no Product writes.
- `tools/ts_ee_oc2_free_review_fallback_preflight.py`: validates exact notebook receipt at immutable Git commit/path/SHA, requested subject and operation identity, `NONE` effect, capacity evidence and independent current free-model qualification.
- This document: operating constraints, known limitations and next IR handoff.

The fallback workflow deliberately checks `github.ref == refs/heads/main`. While it lives **only** on the experiment branch, it cannot pass its job gate; no Actions dispatch was made or is authorized here. No `pull_request`, `push`, `schedule`, `pull_request_target`, PR comment, commit, or Product merge trigger. `contents: read`, `persist-credentials: false`; the model call has no billing secrets.

The candidate chooses ONLY one explicit non-OpenAI free model, e.g. `opencode/deepseek-v4.1-flash-free` (first choice) or `opencode/nemotron-3-ultra-free`; **no automatic model fallback**. OpenCode Zen's currently published catalog lists them at $0 input/output, but free status can change. Notebook/Actions must check provider access, pricing, rate limits, data-retention implications and actual runtime model identity before any inference. OpenCode's built-in title/summary models must not silently select a paid model. Policy denies providers other than `opencode`, hard-denies edit/shell/execute/subagents/network/MCP/skills/plugins and allows only local read/glob/grep. **The enforcement remains unqualified until negative runtime tests and IR.** A prompt saying 'read-only' is not a substitute for native enforcement.

The current Actions preflight **intentionally blocks** until the following are independently published and validated:
- Original notebook-capacity receipt under `evidence/oc2-notebook-capacity/*.json` at immutable commit and exact file SHA-256. Required fields: `contract_version=ts-ee-oc2-notebook-capacity/v0`, `host_binding=OPENCODE2_NOTEBOOK`, `result_status=BLOCKED_CAPACITY`, `effect_state=NONE`, `inference_started=false`, `native_process_started=false`, `active_semantic_attempt=false`, `execution_attempt`, `operation_id`, `request_sha256`, `subject_repository=mauedgar/ts-execution-lab`, `subject_base_sha`, `subject_head_sha`, `resource_evidence.reason=PROCESS_OVERLOAD|MEMORY_PRESSURE|CPU_CONTENTION`. Preserve measured signals in the receipt; do not fabricate them.
- Model qualification under `evidence/oc2-free-model-qualification/<model-slug>.json` on an accepted lab baseline, with `status=PASS_QUALIFIED`, correct `model_id`, `provider=opencode`, zero input/output prices, `no_paid_fallback=true`, expiry in the future and provenance. No such qualified proof has been published by this preparation.
- Qualified npm/OpenCode2 package source and Linux runner compatibility, native hard-deny tests, fixed action SHA validation, artifact durability and no hidden paid inference. Initial scoped CI implementation is **not** ready for Product adoption.

The workflow restricts candidate source to `mauedgar/ts-execution-lab`; it is **NOT** a cross-repository Product PR reviewer. Applying it to Aware, FitFlow, Attendance or Tecnotron would require explicit new Product binding, secure checkout/data privacy review and competent Product approval.

## Expected review output and custody

- Preliminary reviewer output: raw OpenCode events and findings with paths/lines, input diff digest, exact model/provider, attempt and original notebook refusal receipt. Output is **preliminary feedback**, not a formal Independent Review or a recommendation to merge.
- Actions may produce an artifact; run status and artifact digest are separate from model verdict. Commit/push to source, auto-comment and product mutations are forbidden.
- GitHub artifact retention is temporary; eventual durable evidence transport/receipt must be qualified before any adoption. Provider-native run/attempt URL must be captured.
- `UNKNOWN` effect on either host blocks fallback/acceptance. Use exact deferred durable join; never continuously poll Commander.

## Next competent gates

1. **Source-only WEB_INLINE Independent Review** of this candidate branch, its workflow and preflight code, using a fresh separate reviewer and frozen Git commit/tree. Require findings/advisories, security and correctness, 0F/0A adoption discipline. Control must not self-review.
2. Repair any findings within the isolated lab branch; re-freeze and repeat independent Web Inline IR on a new candidate as necessary. Never silently expand Product scope.
3. Only after source IR 0F/0A, qualify notebook permission enforcement and the free-model/no-paid-fallback policy on synthetic work; notebook remains primary. Qualify isolated Actions negative/positive tests separately. Do not dispatch Actions here.
4. Decide experimental adoption in TS EE before any workflow reaches `main`. No Product adoption or IR substitution from this source-only candidate.

**Disposition:** `PREPARED_AWAITING_WEB_INLINE_IR`; `ACTIONS_RUNS_STARTED=0`; `NOTEBOOK_RUNS_STARTED=0`; `PRODUCT_EFFECT=NONE`.
