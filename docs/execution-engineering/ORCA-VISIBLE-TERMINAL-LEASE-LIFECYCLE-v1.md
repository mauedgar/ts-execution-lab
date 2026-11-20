# Orca visible terminal leases — per-repository acquire / settle / close v1

status: OPERATIONAL_NONPRODUCT_METHOD_BOUNDED
authority: TS_EXECUTION_ENGINEERING_METHOD_ONLY
Product_authority: NONE
Product_effect: NONE
Developer ruling: a local OpenCode semantic launch happens only from an Orca-owned visible terminal in the exact authorized Windows or native WSL repository/worktree
Date: 2026-11-20
Parent method: docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md
Native reference: stablyai/orca@v1.4.265 docs/site/content/docs/cli/reference.mdx, §Terminals; Git blob 63ebcf7baa035812ac6c09ccadd979396b61ae16
Trial request: mauedgar/ts-execution-transport@f01cd5a0de1088eb35ee9ce10b06bbb1aa8a25e1:requests/TS-EE-ORCA-REPO-TERMINAL-LIFECYCLE-20261120-001/REQUEST.md

## Principle: a terminal is a leased responsibility resource

The controller, not Orca's board label, identifies a competent responsibility / ExecutionAttempt, candidate, repo/worktree and expected effects. Terminal acquisition is an independent native provider effect. Terminal release/close is a REQUIRED part of responsibility close, provided that results and original effects have settled. A pending external task, UNKNOWN effect, running agent or shared terminal prevents automatic closure.

Do not pre-create persistent shells for every Product. Keep permanent repo/worktree navigation records; acquire visible terminals **on demand** in the correct already-qualified repo and close the owned terminals when that responsibility reaches a terminal disposition. This reduces stale panes and process resource retention.

## A. Acquire: discover the *native* existing workspace then create exactly once

1. Competent Product/control freezes grant, subject, repo/worktree, host, branch/HEAD/tree where applicable, attempt, model/cost/permissions if an agent is intended. Do not treat Orca status as Product approval.
2. Read Orca `status --json`, `worktree ps --json` / `worktree show --worktree <selector> --json`, and `terminal list --json`. Match a unique existing, safe owned worktree and current runtime host; don't invent IDs, aliases or Product roots from prior trials. Do not create a worktree unless Product authorizes a separate materialization gate. Avoid setup hooks which copy secrets, auto-install dependencies or share native modules.
3. On a Windows repo in Orca, use one native:
   `orca terminal create --worktree path:<grounded-native-Windows-path> --title "ROLE | <attempt>" --json`.
   The exact per-attempt command text is derived and frozen before invoking. On an existing WSL UNC-native repo (`\\wsl.localhost\Ubuntu-24.04\home\tsops\...`), use the exact registered `path:` selector and allow Orca to choose its Linux shell; **do not force an unqualified `--shell` override**. An explicit `--command "wsl.exe -d Ubuntu-24.04"` was qualified only for an isolated Windows station diagnostic, not as a generic repo mapping.
4. Capture native receipt: `ok`, `surface=visible`, runtime ID, `executionHostId`, terminal handle, incarnation, tab and worktree IDs; verify `show` says connected, writable, not orphaned and the shell preview/prompt is in the *correct repo* with the correct native OS. In a WSL environment ensure `opencode`, Node/npm and repo cwd are Linux-native; never accidentally invoke Windows binary from injected PATH.
5. Launch semantic OpenCode only by the separate explicit competent grant, with **`--agent opencode`** or the exact qualified native `opencode` inside that owned visible terminal. Do NOT accept Orca's historical default `opencode2`; do not invoke a model during a terminal readiness test. Freeze provider/model/effort and quotas per attempt. Commander is a read-only or bounded mechanical transport, not an alternative model launch surface.
6. One attempt → one send / launch. For accepted but unobservable input, inspect the same terminal and durable receipt; no blind resend or new terminal under UNKNOWN.

## B. Settle: separate execution completion from Product acceptance

- Reconcile the original model/process/Actions native session, exact input, output/receipt, exit where available, terminal identity, artifacts and any pending asynchronous child/server. Terminal echo or `accepted=true` is **not** a complete process PID/UID/exit attestation.
- Publish exact non-secret evidence on GitHub/Transport with commit, hashes, cutoff and subject IDs, or return `PENDING_EXTERNAL_RESULT` and a durable reference.
- Product validation, Independent Review, Developer acceptance, merge and close belong to competent Product SOT; no inference from Orca terminal status.
- A shell can stay open after work, so a visible prompt alone does not imply no child/server. Check native process ownership and terminal type. If a long-running app is intentionally retained, transfer terminal ownership explicitly to another responsibility with an original reference; otherwise its owning attempt must close it.

## C. Release/Close: *mandatory gate before declaring a responsibility fully closed*

1. Inventory **only terminals owned by this attempt**, matching original handle + incarnation + Orca runtime + worktree + host and native `terminal show`. Validate each original effect is `CONFIRMED terminal` or `NONE` with persisted result; no RUNNING/UNKNOWN, shared interactive shell, pending server or active agent attached to that handle.
2. Native one-at-a-time `orca terminal close --terminal <verified_runtime_scoped_handle> --json`. The documented close stops the PTY process. Require native `ok=true`, same handle/tab, `close.ptyKilled=true`, no replay. If the terminal self-exited/was absent, first check native `hostScope` and original effect; do not manufacture a close receipt.
3. Re-read `orca terminal list --json`: `hostScope.hostIds` must include the original execution host and `omittedHostIds=[]`, current expected runtime and no matching handle. Only then terminal release is `CONFIRMED`. If host unreachable/partial, report `UNKNOWN_CLEANUP`; do not retry or claim closure.
4. Persist `terminal_correspondence`, closing receipt and remaining exceptions in the original responsibility. Release claim/owner only after verified close. Mark Orca board `Done` only when terminal obligations and technical obligations are reconciled; this board move is still not Product acceptance.
5. `orca terminal close --worktree <selector> --all --json` is **not** the default. It kills every terminal in that workspace *and saved layouts/resume records*, so use it only when every affected process/session/owner is verified and closing all is explicitly authorized. Never bulk-close old, orphaned, shared, or foreign Product terminals. `orca worktree rm`, workspace cleanup run and host daemon restart are separate destructive gates, not substitutes.
6. If preserving an intentional paused session for future continuation, use documented workspace Sleep where appropriate rather than terminal Close, with a specific owner and durable deferred join. No silent indefinite reservations.

## Reproduced per-repo lifecycle test (no Product)

- Native registered nonProduct TS EE root: `C:/TS/station/worktrees/ts-ee-llm040-source-20261030-001`, Orca `worktree ps` observed one unique root, local Win32, no live terminals at preflight. No repo source content touched.
- One `orca terminal create`, original Commander PID `10756`, provider `ok=true`, runtime `247c3eb7-94c7-4615-a1a9-f485ddcb0a68`, `surface=visible`, `handle=term_3a99b9e9-4a4a-4e51-999b-6f13185c6d25`, `tabId=c518b144-5075-4f4c-a009-fc4a33ade7f8`, incarnation `a4802729-d0e2-419b-8689-188d02d59e85`, `executionHostId=local`.
- `terminal show` original PID10364 and `terminal read --screen` PID6564 both `ok=true`; non-orphaned, connected/writable, PowerShell prompt `PS C:\TS\station\worktrees\ts-ee-llm040-source-20261030-001>`. No commands/agents/models were sent to this proof terminal.
- One `terminal close --terminal <exact handle> --json`, original PID16152, `ok=true`, returned same handle/tab and `ptyKilled=true`.
- Postclose native `terminal list --json`, original PID6832, `ok=true`, runtime unchanged, `totalCount=13`, `hostScope.hostIds=[local]`, `omittedHostIds=[]`, exact new handle absent and no terminal for this root. `PASS_VISIBLE_PER_REPO_ACQUIRE_SETTLE_CLOSE`, original effect confirmed, no replay.
- Existing 13 historical terminal records include some `orphaned=true`/unknown owner; NOT included in this proof cleanup. They need individual independent reconciliation to justify any termination; this method does not confer that authority.

## Existing Orca per-repository registration, observation only

Read-only Orca worktree ps --json, original Commander PID3256, exit0: 19 registered worktrees, current observed Orca runtime at that cutoff 247c3eb7-94c7-4615-a1a9-f485ddcb0a68. **Registration is not canonical Product SOT or a fresh execution permit.** The same exact Product repo may have more than one registered root with different execution platforms. Each future competent Control must select the correct existing registered worktree by unique ID, SOT/candidate/HEAD and OS, and qualify its own native new-terminal binding before any model.

| Registered surface observed | Orca terminalPlatform | Safe operational interpretation |
| --- | --- | --- |
| TS EE lab main worktree C:/TS/station/worktrees/ts-ee-llm040-source-20261030-001 | win32 | Per-worktree visible terminal acquire/close qualified today, no Product |
| Tecnotron Linux root \\wsl.localhost\Ubuntu-24.04\home\tsops\workspaces\tecnotron-ai | linux | Native WSL registered, suitable only after competent Tecnotron SOT/attempt preflight |
| Tecnotron Windows C:\TS\repos\tecnotron-ai | linux | Navigation-only historical root with counterintuitive platform; HOLD for new model launches |
| FitFlow Windows C:/TS/repos/FitFlow | win32 | Existing Windows root, candidate for a competent FitFlow Windows attempt |
| FitFlow WSL \\wsl.localhost\Ubuntu-24.04\home\tsops\workspaces\FitFlow | win32 | WSL path marked win32: **HOLD for any assumed native WSL launch** until repaired and requalified |
| Aware Commerce C:/TS/station/aware-commerce-p0-20261109-001 | win32 | Registered historical local root; no inference that this is current Product authoritative checkout |
| Attendance | no matching registration in this 19-item observed snapshot | No preexisting exact Orca workspace; register the competent SOT-selected root in an authorized separate gate before starting a terminal |

Do not create or pre-open permanent terminals for each Product and do not repair Product registries merely because a historical Orca registration looks stale. If a user specifically asks "open OpenCode in this Product", a competent Product Control must choose exact repo/worktree and authorized operation, and the station then creates its fresh visible terminal, returning a provider receipt. On completion, close its exact handle per this method. Reuse existing native evidence rather than re-probing historical worktrees en masse.

## Non-goals

No worktree creation, source edit, test Product, grant to use models, default agent settings mutation, account/secret read, blanket orphan cleanup, WSL child PID/UID/namespace/exit qualification, Kernel or Beta Run effects. Current method qualifies visible terminal ownership and closure at a workstation level only.
