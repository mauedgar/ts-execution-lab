# Reuse-Before-Build Addendum — TS Execution Runner v0.2

## Decision

This addendum narrows the implementation after reconciling the existing DevLab cross-harness research.

The runner SHALL NOT rebuild:
- agent sessions or resume;
- semantic worker dispatch;
- subagent/task graphs;
- permission/sandbox systems;
- worktree management;
- generic headless agent JSON/event transport;
- model/provider invocation;
- agent telemetry;
- GitHub run/queue mechanics.

Those remain harness/provider-native where competent (OpenCode/Orca, Codex, Gemini CLI, Claude Code, GitHub Actions).

## Narrow core owned here

`ts-exec` exists only to provide portable deterministic mechanics where cross-harness invariants are required:

1. validate portable JSON execution requests;
2. resolve a registered deterministic profile;
3. execute known code, never arbitrary transported commands;
4. preserve Product_operation / ExecutionAttempt / exact subject / effect identity;
5. emit portable result + receipt;
6. expose timings/subprocess/tool-efficiency facts;
7. allow the SAME profile contract to be invoked through local Commander or remote Actions;
8. remain callable from harness-native structured/headless surfaces rather than replacing them.

## Harness-native reuse

- OpenCode/Orca: retain session/agent/task/worktree/permission/runtime ownership.
- Codex: retain App Server/SDK/thread/event/result/sandbox/handoff ownership where selected.
- Gemini CLI: retain headless JSON/stream-JSON, hooks, policies, skills, telemetry and agent runtime where selected.
- Claude Code: retain session/task/subagent/hooks/permissions/worktree/runtime mechanics where selected.
- GitHub: retain Actions run identity, queues, artifacts, reusable workflows, Git object/forge identities.

Portable receipts correlate native evidence; they do not duplicate provider-native state.

## Adoption authority for this lab

If every mandatory DoD item passes after independent Web reconciliation:

- fast-forward/adopt the qualified runner result into `mauedgar/ts-execution-lab:main`;
- keep experimental evidence/history;
- preserve `Product_authority: NONE`;
- preserve `Product_effect: NONE`;
- do NOT modify or auto-adopt into Tecnotron/FitFlow/other Product repositories.

If DoD fails or material semantics diverge, do NOT adopt to main.

## Additional optimization criterion

A feature that merely wraps a capability already supplied by a competent harness/provider without adding a cross-harness invariant must be REMOVED or NOT_BUILT during this experiment.
