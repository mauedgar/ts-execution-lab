# TS EE — Notebook-first OpenCode2 free-model native qualification

**Request_ID:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`  
**Operation_ID:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-OP001`  
**ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001` (reserved; NOT_DISPATCHED)  
**Effect_ID:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-RESULT-A001` (NONE until verified)  
**Owner:** TS Execution Engineering / experimental Developer Lab.  
**Authority:** Developer 2026-11-13: one notebook-first isolated synthetic qualification, non-OpenAI free model, no paid fallback, no Product effects.  
**Execution surface:** Orca-owned visible task terminal on authorized notebook `DESKTOP-DJLBEQH`; Windows or WSL chosen from actual native worktree binding. **No raw Commander/PowerShell/WSL semantic OpenCode2 launch.**  
**Source contract:** `mauedgar/ts-execution-lab@d5d0823ed64502226c9a81ac561560728b04af38:docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md`, §7.1, and corresponding canonical EE contract.  
**Input repository:** `mauedgar/ts-execution-lab`, synthetic isolated worktree, no Product checkout, baseline `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`.  
**Preliminary model candidate:** `opencode/deepseek-v4.1-flash-free`, explicitly no OpenAI/GPT provider or OpenRouter paid balance. A catalog listing is not proof of zero cost.  
**Allowed target:** only one synthetic review request/receipt in a new isolated task worktree or qualified durable Transport path.  
**Status:** `PREPARED / BLOCKED_ORCA_BINDING_UNVERIFIED / MODEL_CALLS=0`.

## Pre-effect observations already recorded by Control

- Host identified as `DESKTOP-DJLBEQH`, Commander device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2` (mechanical observations only).
- `opencode2.cmd --version` returned `opencode v2.2.5`; launcher SHA256 `4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49`. Hash covers the wrapper, NOT runtime binary provenance.
- Shared OpenCode service status returned `http://127.0.0.1:28894`; native info: version `2.2.5`, server PID `8608`, host `DESKTOP-DJLBEQH`.
- One `models` query returned `ServiceUnavailableError: Location plugins did not finish activating`. A *later distinct read-only models invocation* returned `opencode/deepseek-v4.1-flash-free`, `opencode/glm-5.3-flash-free`, `opencode/mimo-v2.6-flash-free` in the visible catalog. A model listing does NOT qualify provider access, price, quota, privacy or actual model output.
- Read-only `opencode2 run --help` confirmed explicit `--model`, `--agent`, `--format json`, `--file`, `--title` and `--standalone`; no inference launched in these preflights.
- A bounded read-only Commander command `orca --version` produced no version in the first provider observation; same PID `7316` is not yet terminally reconciled. No new Orca terminal/worktree/session has been attested. **Do not infer Orca installed/ready from documentation alone.**

## Admission: mandatory gates before one model call

1. Reobserve original attempts and all active sessions for this operation. No duplicate launch, takeover, cleanup or retry if RUNNING/UNKNOWN.
2. Verify a **working Orca binding** on the authorized notebook: actual CLI/native version; existing task worktree or qualified isolated new worktree, OS/platform, exact Git HEAD/tree, `orca_worktree_id`, `orca_terminal_id` and owned terminal correspondence. Windows/WSL must match the worktree's native runtime. Do not force unqualified shell overrides. **Fail `BLOCKED_ORCA_BINDING` if the Orca CLI/terminal cannot be verified.**
3. Confirm the notebook has capacity for one active reviewer slot with actual CPU/RAM/swap/process evidence. Existing worker ownership is respected; never kill a busy process or reroute on elapsed ETA alone.
4. Verify actual OpenCode2 resolved executable/version/hash **inside the selected Orca terminal** (a Windows .cmd wrapper hash alone is insufficient), correct provider/model ID, authenticated zero-cost path, rate and privacy constraints, with no implicit paid fallback (including title/summary/compaction calls). No API or OAuth OpenAI access for reviewer. If free status or provider identity is unverified, STOP before inference.
5. Reuse the pinned `OPENCODE2-V2-HARD-DENY-REVIEW-CANDIDATE.jsonc` as *unqualified source only*. Establish real config schema and native tool/permission enforcement via bounded negative tests. Specifically check filesystem edit/write, shell execute, external directories, web/MCP/plugins, secrets access, agent delegation and permission prompting. Fail closed on unknown mechanisms; a textual instruction of read-only is not security.
6. Freeze complete synthetic request and the explicit independent local write-set/expected result location. Verify create-only receipt, ownership, exact ExecutionAttempt and no competing Product process. If any gate fails, report `BLOCKED_PRECONDITION` with `effect_state=NONE`, do not launch.

## One permitted synthetic model task, *only if every admission PASS*

Using a **qualified Orca terminal**, run ONE OpenCode2 plan/read-only review against a synthetic deliberately buggy diff with predeclared expected findings. Use the exact model `opencode/deepseek-v4.1-flash-free`; never silently change to paid/OpenAI or launch another model if it fails.

Collect: Orca worktree/terminal, provider-native OpenCode session, request/attempt/model identity, provider endpoint and access evidence without leaking secrets, model billing/cost verification, reviewer findings, negative permission outcomes, any deviations, immutable raw original output and cryptographic digest. Return `QUALIFIED_LOCAL_SYNTHETIC` / `BLOCKED_PRECONDITION` / `FAILED` / `UNKNOWN` plus exact receipt. `PASS` on fixture correctness does NOT qualify real Product reviews.

## Explicit exclusions

- No GitHub Actions run, automatic overload fallback, Product repository or modifications, integration/merge/deploy, PR comment, independent review adjudication, OpenAI/GPT/ChatGPT OAuth consumption for reviewer, paid OpenRouter, provider auto-fallback, credentials publication or generic new orchestrator.
- Commander is mechanical-only; it MUST NOT launch `opencode2 run`, execute semantic tool discovery/patching or replace Orca.
- If Orca remains unverified, stop exactly at `BLOCKED_ORCA_BINDING`; preparing this request is not an execution.
- Future source-only WEB_INLINE Independent Review remains separate; a successful local run is not an independent verdict.
