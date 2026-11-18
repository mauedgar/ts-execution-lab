# R007 B1 — Reconciled static inputs and native fail-closed gate (2026-11-18)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`, same ongoing experimental line; no new TaskCycle or Product adoption.
**Authority:** TS Developer Lab execution mechanics only; `Product_authority=NONE`, `Product_effect=NONE`.
**Disposition:** `B0_PASS / B1_STATIC_INPUT_31_OF_31_PASS / B1_NATIVE_EFFECTIVE_POLICY_BILLING_BLOCKED / B2_NOT_DISPATCHED / B3_NOT_STARTED`.
**New model inference:** `0`. **Actions fallback:** `NONE`. **Historical A001:** terminal `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`, untouched, no retry.

## Immutable source inventory and deterministic check

Subject branch: `experiment/ts-ee-oc2-notebook-free-native-20261113-001`.
Observed before this disposition: commit `2f3cb91b1498a952e3230e5aebadbde976a56c34`.

- Plan `R007_OPTIONAL_OC2_QUALIFICATION_AND_BOUNDED_IR_PLAN_20261117.md`, blob `14c4b782822cecee38042fd478536635ffedb1e6`.
- B1 prior preflight `R007_B1_NATIVE_READONLY_PREFLIGHT_20261117.md`, blob `b870720da12893393ea79aab641cdc21be47bd6e`.
- Strict-free closed-context candidate `OC2_CLOSED_CONTEXT_FREE_NO_TOOLS_CONFIG_CANDIDATE.json`, blob `16ed6e50bddf955db6f27484624b47cbe762fb3b`.
- Frozen three cases `OC2_CLOSED_CONTEXT_SEMANTIC_CASES_V1.json`, blob `c0be212f4e64b6ee1d8ac64346f7ed20ab62194a`.
- Independent R006 parser source verdict: `RECOMMEND_SOURCE_ONLY / 0F / 5A`, published ORIGINAL at `mauedgar/ts-execution-transport@a33a1ded3c5b6230bbf1d5c41ccbdf14eebccbf0:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR002-20261117-001/ORIGINAL.md`, blob `86699cdba05bddc1b11cb39fa7bf4d7809356654`.

One read-only GitHub-source validation of the **exact source contents** above returned **31/31 PASS**, zero failure: pinned blobs (2), exact top-level key set, pinned primary/small models and default agent, disabled auto-update/sharing/snapshots/compaction, four auxiliary agent models and all-agent explicit zero-tool permissions, global zero-tool permission, exact nine ordered policy clauses, frozen case schema/state/zero-tool expectation, exact three case IDs and requirements for buggy/control/adversarial-comment case prompts. This is **STATIC_INPUT_ONLY**, not an executed OpenCode2 native test, model review or external invoice verification. The case assertions check frozen expected fixtures, not semantic LLM accuracy.

## Native evidence and residual blocking conditions

Prior native preflight on the authorized notebook `DESKTOP-DJLBEQH` established OpenCode2 v2.2.5, CMD shim SHA256 `4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49` (shim only), `models --standalone` exit 0 and the advertised candidate `opencode/deepseek-v4.1-flash-free`. Shared-server model activation previously failed. It did **not** attest the full executable, effective native loaded policies, actual signed-out account/integration identity, host-wide exclusive lease or billed-zero routing. Candidate config is not proved to have been applied and rejected invalid policy clauses may be silently dropped after logging warnings.

Official upstream checks on 2026-11-18:
- `https://opencode.ai/docs/policies/`: a malformed policy statement can be dropped with a warning; the last matching rule wins. `integration.use` distinguishes the bare `opencode` free-tier integration from an authenticated `opencode#account` binding. Native effective configuration and log evidence, not JSON alone, are mandatory.
- `https://opencode.ai/docs/models/`: model catalog/default and active session can differ; explicit unavailable models may fail, and the documentation also says a signed-out `opencode` provider can be absent until account connection. This introduces an availability ambiguity requiring native disambiguation, **not** an invitation to log in, switch provider or consume credits.
- `https://opencode.ai/docs/console/models/`: the DeepSeek Flash Free offer is explicitly limited-time; advertised free price does not prove connected account billing.

## B1 next technical batch — admission before any inference

1. Preserve historical A001 and this same R007 candidate. Do not invent `retryN`, re-dispatch A001, reuse its unqualified runner, or update a global OpenCode installation.
2. Prepare one **new versioned source-only** Orca-terminal runner/manifest and fixed cross-worktree create-only attempt ledger, carrying exact attempt/carrier/prompt/full executable hashes, host + Orca terminal incarnation, preconditions, separate stdout/stderr files, durable terminal/UNKNOWN receipts and R006 raw JSONL structural check. Validate on isolated synthetic fixtures without invoking an LLM. Respect the pre-existing Runner v0.2 and ORCA Developer UX v1 instead of introducing an orchestrator.
3. In a **bounded read-only native Orca preflight**, identify current authorized worktree/terminal and running-session state, verify actual binary/package SHA256, load/attest effective config from the intended standalone process, inspect warning-free policy resolution and exact signed-out/free integration, reject fallback accounts/providers, and confirm resource + exclusive owner slot. Mask credentials and private traces. No semantic model invocation merely to obtain an attestation.
4. Use **one** independent `STRICT_READ_ONLY` grouped `IR-SOURCE-BATCH` only after source, tests, native admission and frozen PRIMARY-file inventory are complete. Treat any missing file/false Git hash as `BLOCKED_COVERAGE`. Do not create micro-IRs for every change.
5. If cost-free provider routing, effective deny-policy or native custody is not provable, terminal disposition for this *qualification attempt* is `METHOD_NOT_QUALIFIED / DEFERRED_NONBLOCKING`; optional OpenCode2 must not block independently authorized Product development.
6. Only after B1 PASS may distinct, newly frozen B2 synthetic attempts run once from the visible Orca-owned terminal. Tool-denial behavioral canary is a **separate** future attempt if required; it cannot be retroactively inferred from zero tool calls, nor may it be smuggled into the three semantic cases. After all B2 originals, run **one** grouped `IR-BEHAVIOR-BATCH`.

**B1 result for this observation:** `BLOCKED_PRECONDITION` (effective provider/policy/billing and new bridge not qualified). **Effect classification for new inference:** `NONE`. No runtime wait or retry is pending. Source review/candidate is useful reusable evidence only, not semantic reviewer qualification or Product acceptance.
