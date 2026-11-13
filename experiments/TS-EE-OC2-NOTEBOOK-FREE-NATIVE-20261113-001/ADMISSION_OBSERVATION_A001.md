# TS EE — OpenCode2 notebook synthetic A001 / Orca admission observation

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`  
**Request:** `mauedgar/ts-execution-lab@8957fa3a79bbaf43c4ed166ee1dcb7030318d0ef:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/REQUEST.md`  
**ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001` — **RESERVED_NOT_DISPATCHED**  
**Observation:** `BLOCKED_ORCA_BINDING / NOT_ADMITTED`. No inference started, no original semantic result; `effect_state=NONE` **for this gate only**, no Product effects.  
**Authority:** Developer granted bounded synthetic notebook-first qualification; no Product/Actions/Cloud integration authority.  
**Orca rule:** `mauedgar/ts-execution-lab@d5d0823ed64502226c9a81ac561560728b04af38:docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md` §7.1 and canonical EE contract.

## Native/mechanical observations, read-only

Host: notebook `DESKTOP-DJLBEQH`, Commander mechanical device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2`. Old desktop DISABLED_FOR_NEW_DISPATCH by prior station routing.

1. Prior native OpenCode2 `--version` returned `2.2.5`, wrapper SHA-256 `4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49`; the wrapper hash is NOT a complete runtime/hash qualification.
2. A native OpenCode2 model catalogue call previously returned `ServiceUnavailableError: Location plugins did not finish activating`; a later distinct read-only catalogue observation listed `opencode/deepseek-v4.1-flash-free`, `opencode/glm-5.3-flash-free`, `opencode/mimo-v2.6-flash-free`. No provider billing/access, full model execution or effective permission policy qualified.
3. Orca CLI `orca --version` produced no attested version text. Its earlier process `7316` did not leave an active Commander session; this is not a version PASS.
4. Orca native `orca worktree list --json`: provider PID `11812`, exit code 0. The only TS Execution Lab worktrees in the returned inventory were unrelated historical paths `C:/TS/station/worktrees/ts-ee-llm040-source-20261030-001` and `C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/llm044-negative-001`. No worktree for current A001.
5. Orca native `orca terminal list --include-visual-layouts --json`: provider PID `8328`, exit 0; returned 2 connected terminals under neutral `C:\TS\station`. One terminal carried `agentIdentity=opencode` for a separate responsibility and must not be taken over. No terminal is tied to the current TS EE synthetic request.
6. No Orca worktree materialization, new terminal, `orca agent launch`, `opencode2 run`, LLM provider call, GitHub Actions run, Product code or credentials mutation occurred. No actual CPU/RAM pressure observation or trusted `BLOCKED_CAPACITY` receipt exists. Thus this does NOT enable Actions fallback.

## Decision / next boundary

`ORCA_NATIVE_CLI_LIST_PASS / CURRENT_TASK_WORKTREE_ABSENT / CURRENT_TASK_TERMINAL_ABSENT / SEMANTIC_DISPATCH_NOT_ADMITTED`.

- A new isolated worktree/terminal must be materialized through qualified Orca UI/CLI on the notebook, with exact Git root, branch and new worktree/terminal IDs. Do not reuse any historical worktree or existing unrelated OpenCode session.
- The visible Orca terminal must confirm correct Windows/WSL binding, OpenCode2 runtime and current model/provider, read-only permission enforcement and capacity evidence. No fallback to Commander terminal.
- Only after all gate preconditions PASS can Control dispatch A001 once from the Orca terminal. A historical model catalogue listing is not a cost guarantee; no OpenAI/GPT reviewer calls or paid fallback allowed.
- If an Orca-native dispatch channel is unavailable from this ChatGPT environment, preserve request and ask for manual Orca-side launch/receipt. Do not improvise a detached shell or claim a completed run.
- **No new Developer ruling** is inferred for Product, Actions activation, cost-bearing providers, or unrelated processes. Stop on uncertain occupancy or model cost.

**Terminal state:** `BLOCKED_ORCA_BINDING / EFFECT_NONE / MODEL_CALLS=0 / ACTIONS_RUNS=0 / PRODUCT_EFFECT=NONE`. This is an operational preflight observation, not a semantic reviewer verdict.
