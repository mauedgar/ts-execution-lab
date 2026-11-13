# TS EE — Orca remote worktree/terminal materialization receipt

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`  
**Semantic ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001` — `RESERVED_NOT_DISPATCHED`  
**Control authority:** Developer authorized remote materialization of Orca worktree/terminal on notebook; no Product authority or remote Actions activation.  
**Frozen request:** `mauedgar/ts-execution-lab@8957fa3a79bbaf43c4ed166ee1dcb7030318d0ef:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/REQUEST.md`  
**Prior observation:** `mauedgar/ts-execution-lab@ad73a7df0593f9d6606959dbc97383a74d2faeb7:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/ADMISSION_OBSERVATION_A001.md`  
**Current disposition:** `ORCA_MATERIALIZATION_PASS / TERMINAL_PREFLIGHT_PASS / MODEL_INFERENCE_NOT_DISPATCHED`.

## Provider-native original effects and reconciliation

- Authorized notebook `DESKTOP-DJLBEQH`, device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2`; no operation on the older desktop.
- A first Orca `worktree create` invocation, mechanical PID `11640`, returned `invalid_argument` because `--reference` accepts PR/issue URLs rather than a GitHub file URL. No target worktree appeared in the subsequent exact native `worktree list` observation (PID `13924`). This rejected request was not replayed.
- A separately corrected create-only materialization from the same frozen source, without invalid `--reference`, returned success and exit 0 under mechanical PID `8852`, Orca native receipt `900607e3-557c-43eb-b00f-1989506272ff`, `warnings=[]`.
- Orca creation options: `--repo id:de17644d-bbf9-4c3b-b6be-52b51954e854`, `--name ts-ee-oc2-notebook-free-native-20261113-001`, `--base-branch origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001`, `--no-parent`, `--setup skip`, `--activate`, `--json`; **no `--agent`**, no model launch, no setup hook.
- GitHub project: `github:mauedgar/ts-execution-lab`. Worktree ID: `de17644d-bbf9-4c3b-b6be-52b51954e854::C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-oc2-notebook-free-native-20261113-001`.
- Worktree native identity: `wt2:local:b90df112-3542-4070-89b9-57629f514bfb`, `parentWorktreeId=null`, `workspaceStatus=in-progress`.
- Verified exact checkout HEAD `ad73a7df0593f9d6606959dbc97383a74d2faeb7`; local branch `refs/heads/mauedgar/ts-ee-oc2-notebook-free-native-20261113-001`; base ref `refs/remotes/origin/experiment/ts-ee-oc2-notebook-free-native-20261113-001`. GitHub frozen branch HEAD before this evidence publication matches that SHA.

## Native terminal identities

Orca `terminal list --include-visual-layouts --json` completed exit 0 under PID `7752`, found three connected, writable, non-orphaned terminals for this one worktree (other existing terminals untouched):

- `01 · TS · Control`: `term_b4308231-2a2e-4542-a01e-4086e3659bea`
- `02 · TS · Experiment`: `term_d3af65b2-91a4-491f-ba1b-1d656bf6f1aa`
- `03 · TS · Evidence`: `term_9f289b92-4ba8-44d6-b464-8c743d24c8d7`

Exact `02 · TS · Experiment` terminal received **only** a bounded read-only command sequence `git rev-parse --show-toplevel`, `git rev-parse --verify HEAD`, `git status --porcelain=v1 --untracked-files=all`, and `opencode2.cmd --version` bracketed by `PREFLIGHT_BEGIN`/`PREFLIGHT_END`.
- Orca `terminal send --json` reported input accepted, request `48c6bec8-4562-4d18-9043-ed178c1d0c98`, `provider=unsupported` for delivery; **no duplicate send**.
- The exact native Orca terminal screen read returned both markers, the correct worktree root, HEAD `ad73a7df0593f9d6606959dbc97383a74d2faeb7`, no porcelain status entries and `opencode v2.2.5`, followed by the ready shell prompt. This reconciles the read-only input as executed despite unsupported send-delivery reporting.
- Orca `terminal switch` returned `ok=true` and `navigated=true` for `02 · TS · Experiment`, native receipt `b7b9359a-2f23-400d-8d58-ccd4d810ef03`; tabId `9eecf1ea-9060-402e-9856-e22cccbef073`.

## Scope and remaining limits

- **Only materialization and identity preflight were completed.** There is no running or completed semantic OpenCode2 model attempt under A001. No LLM model calls, paid providers, GitHub Actions runs, Product repository mutation or Independent Review occurred.
- Previously observed OpenCode2 catalogue lists `opencode/deepseek-v4.1-flash-free`, but live provider price, auth, quota and privacy, hidden title/summary routes and native read-only permission enforcement remain **UNQUALIFIED**. One unrelated active Orca agent session exists in the neutral station and is not owned by this responsibility; do not interfere.
- Notebook CPU/RAM/process headroom and enforcement of effective OpenCode2 permission-denial policy are not yet attested.
- Commander acted as a bounded carrier of **Orca-native worktree/terminal creation, read-only operational observation and read-only preflight**; it did not execute `opencode2 run`, edit Product code or act as a semantic model runner.
- A native Orca model-launch channel must be independently qualified before invoking one authorized synthetic agent. No bare Commander/PowerShell shell fallback; no Actions launch merely because model gate remains pending. `UNKNOWN` or running attempts block conflicting effects.

**Next boundary:** `ORCA_MATERIALIZATION_DONE / RUNTIME_MODEL_PERMISSION_AND_COST_GATE_PENDING`. Preserve the frozen A001 identity and terminal; do not reinterpret the materialization as a semantic reviewer PASS.
