# TS AI Dev Stack — R2 Deep Dive / 2026-11-02

**Disposition:** `RESEARCH_R2_PASS_WITH_TOOL_INTEGRATION_PENDING`. Owner: TS_EXECUTION_ENGINEERING. Scope: research and local isolated synthetic fixtures only; no Product, no TaskCycle, no upgrades, no CI dispatch, no paid requests.

## Decision change — AHP

**AHP = DEFER / NOT NEEDED NOW** by user architecture ruling. Native OpenCode2 session/terminal persistence is preferred; cross-provider protocol neutrality is not a current requirement and would add a second control and session layer. Revisit only if an observed continuity requirement cannot be satisfied with OpenCode2+Orca and current notebook/desktop topology. Do not create prototype or migrate persistence until needed.

## P1 — GitHub Actions lockfiles: high-value, conditional adoption

GitHub workflow dependency lockfiles GA 2026-10-28 (including GitHub Free). `actions.lock` pins action dependencies including their transitive dependencies; it **does not** pin external reusable workflows (`jobs.<id>.uses`) or Docker job/service images. For external reusable workflows use full commit SHA or independently managed source lockfile. A lockfile is not a vulnerability scanner or a security audit. `--verify-local` is coverage only; full `--verify` checks provenance. Enterprise-wide Require lockfile enforcement and its Evaluate mode are Enterprise Cloud features, not equivalent to general feature availability. Do not enable Require lockfile until all targeted workflows are onboarded.

Read-only workflow evidence (current branch at 2026-11-02):

| Repo/ref | Selected immutable file blob SHA | Observation |
|---|---|---|
| `mauedgar/FitFlow@develop:.github/workflows/deterministic-ci.yml` | `68c1e5be2b1ee5107cf7ec193b43c3e1058ef08d` | checkout@v4, setup-python@v5, setup-node@v4, upload-artifact@v4; postgres:15-alpine and redis:7-alpine image tags |
| `mauedgar/FitFlow@develop:.github/workflows/update-schema.yml` | `a0f44c88677850c2c604b8910d081d1f89c3bc63` | checkout@v4, setup-python@v5, astral-sh/setup-uv@v10, stefanzweifel/git-auto-commit-action@v5; postgres:15-alpine |
| `mauedgar/tecnotron-ai@tools:.github/workflows/native-validation.yml` | `fb3c767652dda651207f743b8e956c20668673d6` | checkout@full SHA, setup-node@full SHA already |
| `mauedgar/ts-execution-lab@main:.github/workflows/ts-exec-reusable.yml` | `2ab940fb1beef9f2bf4da821a56395fca9b0375d` | checkout@v4 and workflow_call; suitable audit first |

**Next gate:** official `gh-actions-lock v0.4.0` pinned release Linux x64 SHA256 `f9da98f2a6e9e0ae77deadf9a2319a8a86bb002b541cc3203b247cc59fb04842`; executable must be acquired and verified in authorized networked isolated lab, then run `--verify-local` in synthetic fixture and `--verify` online separately; inspect resulting lockfile generated *by CLI* (never hand-author canonical lockfile). No deployment, no changes to Product repos. This conversation's container cannot resolve github.com and has no `gh`; **NO upstream CLI pass is claimed**.

Official refs: https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/ ; https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles ; https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles ; https://github.com/github/gh-actions-lock/releases/tag/v0.4.0

## P2 — OpenCode2 V2: security/continuity before upgrade

V2 ordered `permissions` array uses `action/resource/effect` and **last matching rule wins**; no generic V1 `permission` or `bash` assumption. `external_directory` is allowed by the default policy, so add explicit deny/ask. `shell` operates with host user authority; best-effort scanner is not a sandbox. Subsequent per-agent permissions can override global rules and saved approvals may be broad; a dedicated hard-deny policy should be reviewed and verified in the real runtime.

Proposed **non-deployed read-only candidate**: broad deny; explicit limited read/glob/grep and git status/diff/log; explicit deny edit/execute/external_directory/push; no `experimental.schedules`, no `/goal` until a fresh grant and reentrancy protocol. `UNKNOWN`, `RUNNING` and prior `PASS` remain `NO_RETRY` regardless of /goal. Autonomous goal review is not an independent IR.

Model binding in V2: choose actual catalog `provider/model#variant` (e.g. `openai/gpt-6.1-sol#high` *only if available*), verify provider OpenAI, model ID and reasoning variant via `/models` before runs. A selected session model overrides configured default; root model does not persist variant. ChatGPT sign-in (Plus/Pro) can cover supported models within plan quota, whereas separately configured API credentials may incur billing. No host OpenCode2 upgrade authorized or performed.

Official refs: https://dev.opencode.ai/v2/docs/permissions/ ; https://dev.opencode.ai/v2/docs/migrate-v1/ ; https://dev.opencode.ai/v2/docs/models/ ; https://dev.opencode.ai/v2/docs/providers/ ; https://github.com/anomalyco/opencode/releases/tag/v2.2.5

## P3 — GitHub Agentic Workflows: design only

GA 2026-10-28; Markdown compiled to Actions YAML. `safe-outputs.staged: true` only previews built-in safe outputs; **NOT a general sandbox** for custom steps/jobs, external MCP servers, secrets, network side effects or memory/cache. Compile `--dry-run` validates compiler-managed effects but does not neutralize arbitrary custom code. Default read-only GitHub tools and separate safe outputs are favorable; no grant, IR, acceptance or Product semantics are delegated to an agent.

Cost = GitHub Actions runner minutes + AI inference charges, potentially different billing owners; default Copilot requires entitlement or organization AIC, whereas Codex/OpenAI may bill an OpenAI account. Deterministic CI triage should precede agent execution. Recommended future trial: source artifact outside `.github/workflows`, no triggers, no secrets, no third-party MCP; independent `gh aw compile --dry-run` and scanner review in disposable lab before any dispatch. No compiler used this round.

Official refs: https://github.github.com/gh-aw/reference/staged-mode/ ; https://github.github.com/gh-aw/reference/billing/ ; https://github.github.com/gh-aw/reference/compilation-process/

## P4 — GPT-6.1 Terra: benchmark candidate / cost ceiling required

Official model `gpt-6.1-terra`: visual reasoning + computer use, effort `none,low,medium,high,xhigh,max`, Responses API required for tool calling. API standard $1 per million uncached input tokens, $0.05 per million cached input tokens, $5 per million output tokens, excluding extra tool charges, processing modes and long-context uplifts. 10,000 uncached input + 2,000 output tokens = **$0.02** before tools, purely arithmetic. API billed separately from ChatGPT; no keys or paid calls used in R2. Compare with available no-extra-cost models before selecting it.

Official refs: https://developers.openai.com/api/docs/models/gpt-6.1-terra ; https://help.openai.com/en/articles/9624314-model-release-notes

## Synthetic R2 evidence

The local isolated policy validator completed **35/35 PASS** covering representative action lock coverage/caveats, OpenCode V2 deny/allow patterns and no-retry admission, gh-aw staged risks, and Terra token-price arithmetic. This is only a **synthetic policy oracle**, not validation of actual GitHub extension/OpenCode/AHP/GH-AW/Terra binary/provider. No network, CI, Product or paid requests.

Local R2 package SHA256 `513bf91d20b114b7c3a4a0463ea176c45f857270b29fef73cd61db4613bc7229` contains `validate_r2.py`, `RESULT.json`, `DECISION_MATRIX.md`, `OPENCODE_V2_READONLY_CANDIDATE.jsonc`, `GH_AW_STAGED_DESIGN_ONLY.md`. The downloadable package was created in the chat sandbox, not committed to a Product repository.

## Next action / grants

First: real gh-actions-lock CLI isolated qualification using verified binary; second: OpenCode2 permission/runtime contract tests in a sandbox and independent review, prior to a proposed workstation upgrade. Third: gh-aw compiler dry-run, only if demonstrated marginal benefit vs deterministic Actions. Fourth: Terra paid benchmark subject to separate cost and invocation grant. **AHP remains DEFERRED**.

No changes to FitFlow, Tecnotron, Beads, OpenCode installations, Orca, Microsoft transport policy, CI workflows, or SOT grants.
