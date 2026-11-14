# TS EE — WEB_INLINE Independent Review IR001 | Orca Native Semantic Dispatch Bridge

**Review_ID:** `TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001`  
**ExecutionAttempt:** `TS-EE-ORCA-NATIVE-BRIDGE-IR001-A001` — reserved, NOT_DISPATCHED  
**Reviewer binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH_INDEPENDENT_CONTEXT`  
**Authority:** TS Developer Lab, experiment only, `Product_authority: NONE`, `Product_effect: NONE`.  
**Review subject:** `mauedgar/ts-execution-lab@3f9db9086cc11e0ca01affff92738c89d28f4bf8`  
**Tree:** `ffb70e4f3945f260e22b3d22af1c57e6d596b52d`  
**Expected ORIGINAL return:** `mauedgar/ts-execution-transport:results/TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001/ORIGINAL.md` (Control publication only).  
**User ruling:** OpenCode2, WEB_INLINE or another review harness is an explicit competent per-responsibility choice. This selected WEB_INLINE review of the bridge does **not** make OpenCode2 canonical or the universal reviewer.

## Independent review scope

Assess whether the **specific prebuilt and single-dispatch Commander→Orca→OpenCode2 bridge** is safe to reuse as a qualified bounded *mechanical transport* in TS EE, and distinguish (1) source design, (2) observed native execution/receipts, (3) semantic conformance of A001, and (4) future adoption/qualification limits. **Do not** presume the local 399,890-byte ORIGINAL is accessible to you merely because Control summarized it; verify any original bytes that you actually have access to, or report `NOT_DIRECTLY_VERIFIED`.

An independent result should evaluate the actual PowerShell runner and terminal-bound identity, not reimplement Product work or pronounce any canonical adoption. Do not run code, Orca, Commander, OpenCode2, LLM provider, Actions, Product tools, git mutations, or submit a second review of A001.

## Mandatory source reads, exact immutable refs

1. This subject Git commit/tree `3f9db9086cc11e0ca01affff92738c89d28f4bf8` / `ffb70e4f3945f260e22b3d22af1c57e6d596b52d`, and target/source inventory blobs below.
2. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/ORCA_NATIVE_BRIDGE_A001_RUNNER.ps1` — blob `721b1b532e89ee30fe339af2a9fe7b95215f9b90`.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/A001_ORCA_NATIVE_DISPATCH_RECEIPT_20261113.md` — blob `570a0f556dad97c1ae1fe951c06b79ccfce8e3ec`.
4. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/CONTROL_DISPOSITION_A001_20261113.md` — blob `dae009369fe6aa9604eeaf45b6463aaa268fb387`.
5. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/NATIVE_STANDALONE_ADMISSION_A001_20261113.md` — blob `2fac18844c5bc10fb6cdaaa54f31f52119af23ed`.
6. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_STRICT_FREE_REVIEWER_CONFIG.json` — blob `1fcb47b993ebeee75851f600e4ba1d64faa42b0a`.
7. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OPTIONAL_PRELIMINARY_REVIEWER_CANDIDATE.md` — blob `c1df2afc606d406068b7ec5492fbaf741af94c04`. Review only that it is unmistakably OPTIONAL / not selected or executed.
8. The operative Orca launch instruction at `mauedgar/ts-execution-lab@d5d0823ed64502226c9a81ac561560728b04af38:docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md` §7.1 (blob `635653e592fde3b22e453f2b5f84cb35020ed406`), plus canonical EE operating-contract pointer in same commit `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md` (blob `5640781527c2807433430d4a6675e6102d083285`).
9. Exact Git-only binding-selection rules at `mauedgar/ts-execution-lab@099a82cd167b8943a13cbf813533339bd3645ac9:docs/execution-engineering/TS-WEB-INLINE-INDEPENDENT-REVIEW-BINDING-v0.md` (blob `2d803c871a0107b5d28242e16f33939485e8c4d3`).

## Known observed runtime evidence and its custody limitation

A001 finished terminally `A001_MODEL_EXIT_CODE=0`, `A001_MODEL_EXECUTION_TERMINAL`, provider session `ses_e280576f5ffeFHjktQ8Q7GveAg`; Commander→Orca carrier send had `accepted=true`, `replayed=false`, native request `8f2822b6-db36-4afa-8b66-94468cdf128e`, terminal `term_d3af65b2-91a4-491f-ba1b-1d656bf6f1aa`, incarnation `634b09cf-84a2-4eaa-8d7c-d26e4b09fc0e`. A001 single-original local artifact `results/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001/ORIGINAL.jsonl` on notebook; 399,890 bytes, 63 JSONL events; native SHA-256 `EA873A99533684F3EE2AB9D7F39FB634031969C689BFF7A95919F5BA53085AE9`. Control's bounded event count: 14 step_finish, reported cost sum 0, 34 tool_use, 2 tool errors, zero tool names shell/edit/execute/write, one text final. A001 model responded about supposed absence of fixture, contradicting its own frozen inline TypeScript task. Control classified `BRIDGE_FUNCTIONAL_PASS / REVIEWER_NO_RECOMMEND`. This is **derived evidence**; full provider ORIGINAL is **not** currently available in GitHub or Library to the independent reviewer. Do not call it independently verified or infer that all four tool-denial canaries succeeded. Do not publish private raw traces to public GitHub.

## Mandatory questions / review DoD

- Is the Orca/Commander separation real for the bounded observed command? Was the script already built/frozen and downloaded by exact blob, and did Commander merely deliver the encoded immutable source to `orca terminal send` rather than call `opencode2 run` directly? Is the one-shot send identity enough? Are there unchecked replay paths?
- Check the PowerShell source for shell-version compatibility, quote/b64/framing hazards, input integrity and fixed request hash, unexpected shell execution or injection, path/worktree/HEAD/tree conditions, read-only config/provider enforcement, process/output create-only semantics, collision/race handling, buffered streaming, stdout vs stderr, fail-closed errors, and clean terminal receipt. Does it truly enforce the claimed zero paid fallback and no inference when preflight blocks?
- Does the source/receipt prove a single semantic model invocation and exact original custody? Is the original raw JSONL inaccessible to you? What separate provider-native or independent checks must precede operational qualification?
- Are the flags `--standalone --agent plan --model opencode/deepseek-v4.1-flash-free --format json` and auxiliary model config sufficient for no OpenAI/GPT model, or are implicit title/summary/cost privacy gates unverified? No assumption that all provider cost receipts are independent proof of an external USD invoice.
- Evaluate the semantic drift: inline bug `quantity >= 0` vs required strictly positive, yet model explored repo/declared nonexistent subject; do not conflate `effect_state` with result verdict. Could the bridge be marked mechanically PASS even though the reviewer is NO_RECOMMEND?
- Evaluate safety and trust of terminal screen evidence, terminal incarnation, model session ID, persistent config in Orca shell, other sessions, private worktree, no automatic Actions fallback, no Product change, and whether direct native Orca receipt is sufficient for later full qualification.
- Does `OPTIONAL_PRELIMINARY_REVIEWER_CANDIDATE.md` preserve free reviewer as an optional separate profile rather than a canonical Product review path or ungranted A002? No default `WEB_INLINE` either — current Developer choice applies to this bridge IR only.
- Separate (a) blocking findings for **source bridge qualification**, (b) advisories, and (c) **independent evidence gap** for the inaccessible original. If inaccessible original blocks full runtime qualification, mark full-runtime conclusion `BLOCKED_EVIDENCE`, not PASS. Only `SOURCE_ONLY_RECOMMEND` may be recommended on source facts, and only with explicit limitation.

## Single reviewer ORIGINAL contract

Produce ONE full `IR001_ORIGINAL` containing review identity/attempt, all source commits/trees/blobs verified, independent reasoning and coverage, verdict `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, runtime evidence classification `VERIFIED | PARTIAL_NOT_VERIFIED | BLOCKED_EVIDENCE`, all Fxx findings and Axx advisories with exact file:line, severity, mechanism, bounded repair, regression risks, checks not executed, and qualified next gate. State explicitly whether source reaches 0F/0A without conferring Product or reviewer-default authority. If full ORIGINAL unavailable, never claim complete runtime verification. No automatic retries, no new runtime dispatch, no unqualified bridge adoption and no Product changes.

**Custody:** For an independent *scheduled* WEB_INLINE run, the actual prompt MUST inline full `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` upload/verification/fail-closed clauses. This file alone does not guarantee a Library upload.

**Review request state:** `FROZEN / NOT_DISPATCHED`. Product NONE; Action runs 0; reviewer choice remains explicit.
