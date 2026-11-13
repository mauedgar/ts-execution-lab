# TS EE — OpenCode2 free preliminary reviewer / notebook-first fallback to Actions

**Responsibility:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-20261113-001`  
**Revision:** R002, repaired source-only candidate following independent IR001  
**Status:** `CANDIDATE_PREPARED_INERT / NOT_QUALIFIED_AS_REMOTE_REVIEWER`  
**Authority:** Execution Engineering method only; `Product_authority: NONE`, `Product_effect: NONE`.  
**Repository:** `mauedgar/ts-execution-lab`; isolated branch `experiment/ts-ee-oc2-free-review-fallback-20261113-001`.  
**Main baseline before branch:** `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`.

## Authoritative constraints reused without redefining them

- `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`: one dispatch per attempt, deferred exact provider join, no retry on UNKNOWN, effect/semantic result separated.
- `experiments/TS-EXECUTION-RUNNER-V0.2-001/QUALIFICATION-EVIDENCE.json`: a deterministic local→Actions fallback qualified after `effect_state=NONE` and new remote ExecutionAttempt; this does **not** qualify a semantic reviewer.
- `docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md`: isolated task worktree, visible agent terminal and resource observation; no root mutation or Commander semantic search/polling.
- `docs/execution-engineering/TS-WEB-INLINE-INDEPENDENT-REVIEW-BINDING-v0.md`: WEB_INLINE is the separate competent Independent Review mechanism; preliminary OpenCode2 feedback never substitutes it.
- Existing `.github/workflows/opencode-ci-oauth-pilot.yml` runs `38936506835` and `38940429153`: OpenCode CI transport/package evidence, NOT free-model review or notebook/Actions exclusion.

## Developer routing decision

**Primary:** notebook WSL + Orca + OpenCode2, one preliminary LLM reviewer slot initially, isolated worktree/terminal and explicit read-only permissions. Other independent workers may proceed with disjoint write-sets and observed resource headroom; a historical parallel experiment does not grant unlimited agents.

**Fallback:** Actions only after the notebook attempt is terminal **before semantic inference** with an original trusted `BLOCKED_CAPACITY / effect_state=NONE` receipt, positive native process-state observation, and proof that the same operation is not live. A slow task, an elapsed ETA, `RUNNING`, or `UNKNOWN` cannot trigger failover. The remote attempt must be separately authorized with a new identity on the same immutable request/subject. GitHub Actions `concurrency` does not lock the notebook.

**Model policy:** no OpenAI/GPT reviewer tokens, no paid OpenRouter balance or automatic paid fallback. Specific free non-OpenAI model IDs, provider routing, title/summary/compaction calls, privacy, rates and continued zero price are **UNQUALIFIED**. No provider request, credential, diff upload or inference is implemented in this candidate.

## Independent IR001 source result and exact custody

`TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-20261113-001 / A001` returned `NO_RECOMMEND / 7F / 6A` for source commit `0288f0cb7e3f950274fbe69bd044e7a2d1c569f1`, tree `05a5df089a6043786179e70b50b05e59e196894b`.

Original was verified as 10,286 UTF-8 bytes SHA-256 `e1e47e7104ce246c3742bd6729be2cad8baa54c5ae25c6d58506c3cc121ae612`, published byte-identically into `mauedgar/ts-execution-transport@5d27d494c9ce027eb04c1a03783555723961d18e:results/TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-20261113-001/ORIGINAL.md`. The reviewer executed NO Actions, OpenCode or provider calls.

## R002 repair disposition — bounded by preparation-only

| IR001 | Technical treatment in R002 | Remaining competence boundary |
|---|---|---|
| F01 mutable control checkout | Workflow checks out `github.workflow_sha` and verifies exact tool Git blob SHA in that pinned commit | Workflow source acceptance still requires independent source IR |
| F02 untrusted notebook refusal | Python explicitly treats receipt as **self-attested and untrusted** and ALWAYS returns `BLOCKED_NATIVE_ATTESTATION_UNQUALIFIED` even if all fields pass | Trusted process observation and cross-host fencing NOT implemented; Developer approval required before remote model call |
| F03 mutable free model proof | Removed price proof and all model calls from the workflow; no model can be charged by this source | Free provider + model + native no-paid-fallback requires separate qualification |
| F04 unverified policy | Removed OpenCode runtime/policy from the Actions workflow, not merely hidden behind a flag | Real OpenCode2 hard-deny + negative native tests remain REQUIRED |
| F05 unverified npm/CLI | Removed npm/CLI installation and execution from this candidate | Pin and independently qualify Linux OpenCode2 distribution and CLI invocation in separate gate |
| F06 weak Git boundaries | Pin control to workflow SHA, tool blob, subject HEAD/tree and base ancestry; bind exact request/operation and distinct local/remote attempts; restrict repo to synthetic TS EE lab | Trusted operation manifest and remote/native attempt ownership remain unqualified; all possible remote admissions blocked |
| F07 misleading JSONL/artifacts | Removed reviewer JSONL, nonempty-file PASS shortcut, artifact and all PR comments; exit 42 fail-closed even when source checks pass | A future reviewer must validate actual terminal semantic event, full verdict and durable ORIGINAL |

**Advisories:** A01 measured overload native telemetry NOT qualified; cannot trigger Actions. A02 mutable/naive free-model expiry removed from execution path. A03 zero external diff disclosure. A04 Actions SHA-pinned; no npm dependencies or inferred full supply-chain qualification. A05 no artifact claiming REVIEW_PASS; future custody still must be designed/qualified. A06 claim is explicitly `SOURCE_PREPARATION_ONLY`, never runtime or Product PASS.

## Exact staged source semantics

- `.github/workflows/ts-ee-oc2-free-prelim-review-fallback.yml`: `workflow_dispatch` ONLY; `contents: read`; controller `mauedgar`; explicit `main` gating. The workflow exists only on this isolated branch and is not active from Product or integrated `main`. On a hypothetical later manual run, it can ONLY run a deterministic preflight that exits with BLOCKED status 42. It contains **zero OpenCode or other LLM invocation steps**.
- `tools/ts_ee_oc2_free_review_fallback_preflight.py`: Python stdlib parser verifies bounded lab-only immutable Git refs, unique attempts, receipt SHA/fields with duplicate-key rejection and exact tree; **never returns an admission success**. File/tree writes NONE; stdout reports classification and `actions_model_calls=0`.
- No workflow artifacts, push, PR, automatic triggers, model secrets, paid inference, Product checkout, or irreversible operation.
- A branch-only source change is not an active workflow. No Actions run or notebook reviewer was dispatched by the R002 repair.

## Gates and stop conditions

**R002 Source-only WEB_INLINE IR002:** review exact frozen source against **preparation-only** DoD, assessing whether the fail-closed boundary is truthful and any latent security/syntax defects remain. Do NOT mislabel absence of a functional remote reviewer as a defect in a source-preparation-only gate; instead preserve it as a mandatory next Developer-controlled runtime gate. A positive source-only IR is not qualification to run the LLM.

**Next Developer ruling required before** enabling any actual Actions fallback inference: independent positive+negative native OpenCode2 notebook permission tests; provider model/free price/no paid fallback verified; trusted notebook process/fencing/operation manifest; data retention/private repo review; versioned CLI Linux provenance; exact Actions receipt and IR. No automatic resumption on UNKNOWN. The User explicitly authorized only preparing Actions and notebook-first routing.

**Current disposition:** `STAGED_SOURCE_ONLY / REAL_FALLBACK_BLOCKED`, `ACTIONS_RUNS=0`, `NOTEBOOK_LLM_RUNS=0`, `MODEL_CALLS=0`, `PRODUCT_EFFECT=NONE`.
