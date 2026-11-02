# TS Execution Engineering — Real CLI gates and OpenCode V2 assessment, 2026-11-02

**Gate:** `TS-EE-STACK-GATES-20261102-001`  
**Authority:** user authorized continuation to isolated lockfile CLI and OpenCode V2 tests. No Product, TaskCycle, SQL, automatic retries, paid model calls, or workstation upgrades.

## Decision

| Component | Evidence | Disposition |
|---|---|---|
| gh-actions-lock v0.4.0 official Windows binary | Official release SHA-256 match; `--verify-local` synthetic positive 0, absent dependency 1, missing lock 1; `--verify` online synthetic positive 0; lockfile hash unchanged | **PASS_LIMITED**, candidate for isolated real generation/IR, **NOT** canonical Product adoption |
| Local action `./.github/actions/local` | `--verify-local` warns but exit 0 | **ADVISORY_BLOCKER** if used as sole safety gate |
| Container image `alpine:latest` and external reusable job `uses` | `--verify-local` exits 0, no comprehensive enforcement | Independent controls needed; don't infer lockfile protection |
| OpenCode V2.2.5 binary | Official x64 archive SHA-256 match, `opencode v2.2.5`, standalone `debug config` and `debug agents` exit 0 | **RUNTIME_CONFIG_DISCOVERY_PASS**, **permission enforcement NOT YET qualified** |
| OpenCode candidate hard-deny review profile | New V2 profile with explicit `permissions` and `policies`; static 16/16 policy-oracle assertions PASS | **CANDIDATE_ONLY**, NOT deployed or runtime tool-denial proved |
| AHP | Native OpenCode persistence already meets current need | **DEFER**, per user architecture decision |
| gh-aw and Terra | Earlier R2 research unchanged | Design-only / no deployment, no API charge |

## Actual CLI provenance

`github/gh-actions-lock v0.4.0` Windows amd64 official SHA-256:
`a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`.

- Synthetic positive `actions/checkout@v4.4.0`, manually authored `actions.lock` using published schema: offline `exit 0` and online `exit 0`. Online output: `Scanning 1 workflow; All 1 workflow valid`.
- Synthetic added dependency `actions/setup-python@v5` with unchanged lockfile: offline `exit 1`.
- Missing `actions.lock`: offline `exit 1`.
- Workspace-local action: offline `exit 0` with `Cannot follow 1 workspace-local action` diagnostic.
- Mutable container and external reusable workflow: offline `exit 0` (coverage not enough).
- The lockfile was manually assembled for an isolated test, not generated via `gh actions-lock`. **Do not call this full onboarding qualification**.

Source docs: https://github.com/github/gh-actions-lock ; https://github.com/github/gh-actions-lock/releases/tag/v0.4.0

## OpenCode V2 runtime/contract

Official `anomalyco/opencode v2.2.5` Windows x64 archive SHA-256:
`2f3bfd6b3527c60c2a882557b20ddc9ba6bdff4b5a8fe61c853da8fcfb3076e8`.

The original test runner incorrectly assumed that `opencode debug config` returns a single effective-config object. The real output was **two source records**, exposing `type,path` and `type,path,info`. That `CONFIG_DIFFERENCE` was a **test harness interpretation issue**, not evidence that OpenCode ignored the config. A separate diagnostic returned `scratch_source_listed=True` and `debug agents` exit 0 with JSON array output.

The V2 candidate uses `tool.use` hard policies for edit/external_directory/execute, shell deny with narrow git status/diff/log exceptions, protected read paths, and MCP/skill/plugin denial. Official docs state that a `tool.use` policy is enforced after agent and saved-approval rules, unlike permissions alone. **Actual tool invocations were not attempted**; therefore do not call this policy runtime-certified. No paid inference or shared server change occurred.

The fourth isolated runner emitted its diagnostic but the wrapper terminal session remained listed; the exact lab session PID was then terminated, and a subsequent session listing confirmed it absent. This is a **lab runtime lifecycle advisory** to investigate before adopting an automatic test harness. No user OpenCode service was deliberately stopped or reconfigured.

Source docs: https://dev.opencode.ai/v2/docs/permissions/ ; https://dev.opencode.ai/v2/docs/policies/ ; https://dev.opencode.ai/v2/docs/cli/commands/

## Transport schema amendment

The SharePoint connector changed its live action schemas after the user disconnected the personal Microsoft account, leaving only the educational connection. Commands like `update_file_exact` now omit `link_id`. Passing the historical two-account parameter produces `InvalidActionArgumentsError`. After verifying `get_profile({})` as educational and exact zero-byte cloud slots, the no-`link_id` `update_file_exact` delivered both synthetic fixture ZIP and PowerShell runners. Notebook SHA-256 verified the source bytes. Canonical v1 transport policy, operating recipe, and private account binding were updated; transport scope not expanded.

## Next competent gates, no implicit grants

1. **P1: SOURCE_GENERATED_LOCKFILE_AND_IR_001** — Generate `actions.lock` using the real extension against a new disposable fixture (requires GitHub network), verify offline+online and inspect transitive pins, expected warnings, and a mismatch. Independent review before any PR against Execution Engineering, let alone FitFlow/Tecnotron. No Actions dispatch.
2. **P2: OPENCODE_RUNTIME_DENIAL_001** — In a dedicated portable `--standalone` and visualized Orca session, run actual *nonproductive* tool requests for `edit`, `external_directory`, shell allowed/blocked and saved approvals, using a test fixture and an explicit model/provider/effort binding. Separate quota/agent-execution grant required. Validate lifecycle/cleanup and external resources. No Product, no SQL, no user global config update.
3. **P3: gh-aw compiler-only candidate** only after P1, with no triggers, secrets or MCP.
4. **P4: Terra benchmark** only with explicit budget grant, no model calls yet.
5. **AHP:** DEFERRED until measured cross-host continuity gap.

## Evidence/SOT

Detailed machine results: `docs/execution-engineering/research/TS-EE-STACK-GATES-20261102-001/RECEIPT.json`.  
New review-only profile: `docs/execution-engineering/research/TS-EE-STACK-GATES-20261102-001/OPENCODE2-V2-HARD-DENY-REVIEW-CANDIDATE.jsonc`.

**Status:** `RUNTIME_GATES_PARTIAL_WITH_LIMITS`. Nothing is accepted Product; no independent IR was performed.
