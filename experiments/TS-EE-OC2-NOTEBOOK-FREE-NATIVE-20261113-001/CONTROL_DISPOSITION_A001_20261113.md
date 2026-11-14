# TS EE — A001 Control disposition: native Orca bridge pass, semantic reviewer not qualified

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`  
**Operation:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-OP001`  
**ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001` — **terminal, do not replay**  
**Effect_ID:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-RESULT-A001`  
**Disposition:** `ORCA_NATIVE_BRIDGE_FUNCTIONAL_PASS / MODEL_INFERENCE_EXIT_0 / REVIEWER_SEMANTIC_NONCONFORMANCE / NO_RECOMMEND`  
**Authority:** Experimental TS Developer Lab only; no Product authority, adoption, merge or Actions activation. The one-shot bridge exception was explicitly authorized by the Developer for this existing A001 and is NOT an automatic permanent change to the canonical EE contract.

## Exact execution evidence and immutable source

- Frozen original prompt `mauedgar/ts-execution-lab@8627cd012355fd771216cd7949c7f87dcf5ebbbf:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/NATIVE_STANDALONE_ADMISSION_A001_20261113.md`. Its **self-contained** requested review included `function canBook(quantity: number): boolean { return quantity >= 0; }` and the positive-only requirement. It did not require a separate TypeScript fixture or commit.
- Exact Orca bridge runner `mauedgar/ts-execution-lab@50b9e89c88621e210673696eb2c952f265675f06:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/ORCA_NATIVE_BRIDGE_A001_RUNNER.ps1` (Git blob `721b1b532e89ee30fe339af2a9fe7b95215f9b90`). Its UTF-8 source was verified; Commander carried its encoded bytes to Orca native terminal; no direct Commander `opencode2 run`.
- Exact native dispatch `mauedgar/ts-execution-lab@96363e941960b771bab81db7acbe538725e7afb5:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/A001_ORCA_NATIVE_DISPATCH_RECEIPT_20261113.md`.
- Notebook `DESKTOP-DJLBEQH`; Orca terminal `term_d3af65b2-91a4-491f-ba1b-1d656bf6f1aa`, incarnation `634b09cf-84a2-4eaa-8d7c-d26e4b09fc0e`, native send request `8f2822b6-db36-4afa-8b66-94468cdf128e`.
- Exact worktree HEAD during preflight: `ad73a7df0593f9d6606959dbc97383a74d2faeb7`; local create-only ORIGINAL path `C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-notebook-free-native-20261113-001\results\TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001\ORIGINAL.jsonl`.
- Native markers: `A001_BRIDGE_PREFLIGHT_BEGIN`, `A001_PREFLIGHT_PASS_HEAD=ad73a7df...`, `A001_PREFLIGHT_FREE_KIB=1890880`, `A001_OUTPUT_CREATED`, `A001_MODEL_DISPATCH_ONCE_BEGIN`, `A001_MODEL_EXIT_CODE=0`, `A001_MODEL_EXECUTION_TERMINAL`. One confirmed dispatch, no retries. Model `opencode/deepseek-v4.1-flash-free`, agent `plan`, `--standalone`, `--format json`.
- Provider-native OpenCode session `ses_e280576f5ffeFHjktQ8Q7GveAg`.
- ORIGINAL local artifact: **399,890 bytes**, **63 JSONL events**, final LF; SHA-256 **`EA873A99533684F3EE2AB9D7F39FB634031969C689BFF7A95919F5BA53085AE9`**, checked by native mechanical `Get-FileHash`. ORIGINAL remains on notebook, **not yet published to GitHub/Library**. Do NOT represent this Control summary as the ORIGINAL or assume public publication is safe; its tool traces can contain working-directory paths and repository excerpts.
- Deterministic full-file parser on exact authorized ORIGINAL counted **14** `step_finish` events, cumulative native reported cost **0**, **34** `tool_use` events, **2** tool errors, **0** calls using tool names `shell/edit/execute/write`, **1** `text` event and **1** provider session. This is a bounded mechanical event count, not a semantic Independent Review and not proof that all requested denial canaries were attempted.

## Independent Control interpretation — separate from provider's claims

The native model's single final response began `A001 — reconstruction and disposition (plan agent, read-only)` and asserted that the synthetic subject was absent, that no reviewer verdict could be issued, and that `effect_state=NONE`. It proposed building a larger 6-defect fixture.

**This interpretation is demonstrably wrong for the frozen task.** The bug to review was written **inline in the prompt** (`quantity >= 0` improperly admits zero, correct condition `quantity > 0`); no repository fixture was required. The model searched/read additional repository content despite the request forbidding exploration beyond one named file. It did not deliver the required direct bug finding, focused regression tests and complete factual report of the four denial canaries.

Its asserted `effect_state=NONE` is inconsistent with native evidence of an actual model session, 14 inference steps, and an exclusive local output file. The proper effect classification is **`CONFIRMED_EXECUTED`**, with **semantic outcome `FAILED_NONCONFORMANT`**. Do not automatically accept its suggested new A002 or expand the scope.

The two tool errors are only bounded event-count evidence. There is no verified complete real-call denial matrix for shell/edit/sensitive read canaries; no mutation tool was invoked and no Product writes were observed. A static configuration policy PASS and provider call cost 0 do not establish complete behavioral conformity or indefinite free inference.

## Result and next boundary

- `ORCA_TRANSPORT_BRIDGE_001`: one-shot functional **PASS**, qualified only for this exact prebuilt source, identity and Orca target. Do not make it a standing unreviewed bypass of `ORCA-DEVELOPER-UX-v1.md` §7.1.
- `OPENCODE2_FREE_STANDALONE_EXECUTION`: local native **EXIT_0**; cumulative provider-reported charge **0** for this run; no OpenAI/GPT model was configured.
- `SYNTHETIC_PRELIM_REVIEW`: **NO_RECOMMEND / FAILED_SEMANTIC_CONFORMANCE**; model deviated from self-contained task and read scope; canary enforcement incomplete.
- `IR`: **NOT_STARTED** for this runtime candidate. Any independent WEB_INLINE IR must consume exact frozen input and qualified runtime evidence; source/admission PASS cannot substitute runtime IR.
- `Actions_fallback=NOT_STARTED`, `Product_effect=NONE`, `main` untouched by this experiment. Other sessions were neither canceled nor re-run.

**Next Developer ruling proposed:** accept A001 as terminal nonconformant, preserve original local 399,890-byte artifact; decide whether to (a) qualify a narrower prompt/closed-context reviewer profile in a **new expressly granted** attempt with independent IR, or (b) retain this agent only as a cheap exploratory preliminary signal. Before any such attempt, resolve how to deliver a trusted bounded ORIGINAL to durable custody without publishing potentially sensitive raw traces to public GitHub. No blind retry.
