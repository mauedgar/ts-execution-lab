# TS EE — OC2 Notebook Free Reviewer | source and admission qualification

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`  
**ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001` — RESERVED, NOT_DISPATCHED, `effect_state=NONE` for the proposed model inference.  
**Authority:** Developer authorized an isolated notebook-first synthetic qualification, non-OpenAI zero-price model only; Product_authority NONE; Actions NOT authorized for this attempt.  
**Disposition:** `SOURCE_POLICY_STATIC_PASS_23_OF_23 / NATIVE_INFERENCE_BLOCKED_HOST_SLOT_UNVERIFIED`.

## Immutable observed sources

- Original request `mauedgar/ts-execution-lab@8957fa3a79bbaf43c4ed166ee1dcb7030318d0ef:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/REQUEST.md`.
- Orca materialization and native visible-terminal preflight receipt `mauedgar/ts-execution-lab@d9254fda8ce634f0ab1f0c48704edf071775758c:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/ORCA_REMOTE_MATERIALIZATION_20261113_001.md`.
- Repaired strict model/permission candidate `mauedgar/ts-execution-lab@f15d04dba49faa08eb3029c26448e10105bd0b67:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_STRICT_FREE_REVIEWER_CONFIG.json`, exact Git blob `1fcb47b993ebeee75851f600e4ba1d64faa42b0a`. This config is a **source artifact**, NOT installed or applied to the notebook/global settings.
- Model source: official `https://opencode.ai/docs/console/models/`, observed 2026-11-13. It currently lists `DeepSeek V4.1 Flash Free` at FREE for input/output/cached read, limited-time offering and provider zero-retention/no-training. Pricing and privacy conditions may change; a published page does NOT prove account-level runtime billing.
- V2 authoritative sources `https://opencode.ai/docs/permissions/`, `https://opencode.ai/docs/policies/`, schema `https://opencode.ai/config.json`. V2 policies can deny providers/tools/MCP/skills/plugins after agent permissions. Deprecated `small_model` remains a defense-in-depth setting, not sufficient evidence alone for title/summary behavior.

## Static qualification after repair

The source config pins **all** `model`, deprecated `small_model`, and `agents.plan/title/summary/compaction.model` to `opencode/deepseek-v4.1-flash-free`; disables session sharing and automatic compaction. Its V2 ordered policy denies every provider before allowing only `opencode`. Tool-use policy denies `*` first, then only permits `read`, `glob` and `grep` to defer to explicit agent permissions; sensitive read patterns and external-directory denial take precedence. MCP, skill and plugin use are denied.

An independent Control-side **static model** of V2 last-match rules ran 23 cases and returned **23/23 PASS**. Covered positive `read/glob/grep` and `opencode`; negative `openai/anthropic/openrouter`, shell, edits, execution, subagents, web, MCP, skill/plugin, external_directory, top-level and nested secrets, SSH, and dotenv.

The earlier version failed `read:secrets/credentials.json` because `*/secrets/*` did not cover a top-level relative directory. This was repaired at `f15d04db...` with extra `secrets/*`, `.ssh/*`, and `*.env*` denies in permission and hard policy lists; then 23/23 passed. **This is a static rule-order simulation, not actual native policy enforcement or a permission-denial LLM execution.**

## Notebook-native observations and capacity boundary

- Authorized host `DESKTOP-DJLBEQH`, Orca worktree `de17644d-bbf9-4c3b-b6be-52b51954e854::C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-oc2-notebook-free-native-20261113-001`; visible terminal `02 · TS · Experiment`, handle `term_d3af65b2-91a4-491f-ba1b-1d656bf6f1aa`. Exact preflight root/HEAD `ad73a7df0593f9d6606959dbc97383a74d2faeb7`, clean Git, `opencode v2.2.5` already verified there.
- Orca bounded read-only OS snapshot from the own experiment terminal reported `FreePhysicalMemory=2088112 KiB`, `TotalVisibleMemorySize=8278296 KiB`, `FreeVirtualMemory=6980448 KiB`. This is a point-in-time capacity observation, not a calibrated threshold or proof of capacity for a second inference.
- Unrelated Orca-native terminal `term_067361de-1b90-419a-ae4f-765977f8c708` had `agentIdentity=opencode`, `connected=true` and `agentWait=null`, with no attested running/idle semantic-turn state. **Do not treat agentWait=null as proof that its inference slot is free**; do not inspect its content or interfere.
- No host-native semantic-slot reservation/ownership proof was acquired, no effective OpenCode2 config inspection or live negative permission tests were executed, and account-level billable routing/sidecalls remain unverified. Notebook is the primary binding; no automatic Actions switch.
- The source profile has NOT been injected into a native process or verified as effective. This attempt has `MODEL_CALLS=0`, `ACTIONS_RUNS=0`, `PRODUCT_EFFECT=NONE`.

## Next exact authorized boundary

`NATIVE_INFERENCE_BLOCKED_HOST_SLOT_UNVERIFIED` is a valid fail-closed precondition. Before launching A001, the competent controller must observe the unrelated agent's **provider-native semantic turn status** without acting on it; confirm one available reviewer slot from reliable host/process evidence; bind and inspect the exact free-only source config in a new **Orca** terminal process and validate native denials (not merely this static simulation) and provider charge routing. Preserve the model, request/attempt, worktree and terminal identities; no new attempt ID, no blind retry, no Commander-side direct semantic model launch.

If native status or effective enforcement remains unknowable, return `BLOCKED_PRECONDITION` and preserve the frozen A001. A future runtime IR remains WEB_INLINE, separate from the preliminary reviewer, and a source PASS never authorizes Product adoption or Actions.
