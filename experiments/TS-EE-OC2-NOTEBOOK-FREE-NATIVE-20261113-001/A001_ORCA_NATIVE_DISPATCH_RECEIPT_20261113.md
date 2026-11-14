# TS EE — Native Orca A001 dispatch receipt (in flight)

**Type:** `CONTROL_DISPATCH_OBSERVATION`, not terminal semantic ORIGINAL, not an Independent Review.
**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.
**Operation:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-OP001`.
**ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001`.
**Effect:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-RESULT-A001`.
**Status at first native observation:** `RUNNING`; no completion verdict yet.
**Authority:** Developer explicitly authorized the one-shot `ORCA_NATIVE_SEMANTIC_DISPATCH_BRIDGE_001` exception for this existing A001. Product authority NONE; no Actions fallback, no additional or duplicate dispatch.

## Immutable input and exact carrier

- Frozen original semantic prompt: `mauedgar/ts-execution-lab@8627cd012355fd771216cd7949c7f87dcf5ebbbf:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/NATIVE_STANDALONE_ADMISSION_A001_20261113.md` (Git blob `2fac18844c5bc10fb6cdaaa54f31f52119af23ed`).
- Strict free-only profile: `mauedgar/ts-execution-lab@f15d04dba49faa08eb3029c26448e10105bd0b67:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_STRICT_FREE_REVIEWER_CONFIG.json` (Git blob `1fcb47b993ebeee75851f600e4ba1d64faa42b0a`).
- Complete previously built runner frozen at `mauedgar/ts-execution-lab@50b9e89c88621e210673696eb2c952f265675f06:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/ORCA_NATIVE_BRIDGE_A001_RUNNER.ps1` (Git blob `721b1b532e89ee30fe339af2a9fe7b95215f9b90`, verified 5,733 UTF-8 bytes).
- No runner was constructed or written on the notebook by Commander. ChatGPT Control loaded that exact immutable source and transported its base64 representation through one bounded `orca terminal send` call. The target Orca terminal decoded/evaluated the frozen batch and ran OpenCode2 inside itself, NOT by a detached Commander `opencode2 run` process.
- Target host `DESKTOP-DJLBEQH`; Orca terminal `term_d3af65b2-91a4-491f-ba1b-1d656bf6f1aa`; incarnation `634b09cf-84a2-4eaa-8d7c-d26e4b09fc0e`.
- Native Orca send receipt `c08838fd-6f02-464e-a6b1-0e6fd06d093a`; exact requestId `8f2822b6-db36-4afa-8b66-94468cdf128e`; `accepted=true`, `bytesWritten=7736`, `replayed=false`. Native provider `unsupported` for send delivery, so Control performed a separate native terminal read, NOT a second dispatch.
- Read-only native terminal observation `orca terminal read --cursor 1713 --limit 600 --json` returned `ok=true`, `status=running`, `nextCursor=1720`, `limited=false`, `truncated=false`. Markers actually executed: `A001_BRIDGE_PREFLIGHT_BEGIN`, `A001_PREFLIGHT_PASS_HEAD=ad73a7df0593f9d6606959dbc97383a74d2faeb7`, `A001_PREFLIGHT_FREE_KIB=1890880`, `A001_OUTPUT_CREATED=results/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001/ORIGINAL.jsonl`, `A001_MODEL_DISPATCH_ONCE_BEGIN`.

## Ownership, state and next join

- Bounded single effect has begun: local output was created exclusively with .NET FileMode.CreateNew and is receiving the raw OpenCode2 JSONL events inside the isolated lab worktree. The output is **not** yet read back, hashed or under GitHub durable custody; do not label it as `PASS`.
- The runner configured `--standalone --agent plan --model opencode/deepseek-v4.1-flash-free --format json`, no GPT/OpenAI or paid model fallback. Native provider model-charge evidence and live tool-denial effects remain to be reconciled.
- Use the **original** Orca terminal and exact local result path to obtain the terminal receipt after a meaningful deferred join. No Commander polling, no duplicate command, no cleanup/overwrite, no Actions fallback, and no semantic acceptance during RUNNING or UNKNOWN.
- The next state may be `PASS`, `FAILED`, `BLOCKED` or `UNKNOWN` only from actual native evidence. A GitHub Control-authored receipt is not the original OpenCode2 output.
- Product effect NONE. TS EE experimental only.

**Current observation:** `A001_RUNNING / ONE_DISPATCH_CONFIRMED / ORIGINAL_LOCAL_INCOMPLETE`.
