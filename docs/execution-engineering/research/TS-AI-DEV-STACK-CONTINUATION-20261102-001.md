# TS AI Dev Stack — Continuación de investigación (2026-11-02)

```yaml
artifact:
  id: TS-AI-DEV-STACK-CONTINUATION-20261102-001
  kind: RESEARCH_REPORT_NON_CANONICAL
  owner: TS_EXECUTION_ENGINEERING
  status: RESEARCH_ONLY
  cutoff: 2026-11-02
authority:
  transport_method: SEE_SEPARATE_CANONICAL_v1
  Product: NONE
  TaskCycle: NONE
  repository_or_workstation_upgrade: NONE
  execution_grants: NONE
```

## Baseline and completed dependency

The verified cloud->notebook OneDrive education / SharePoint exact-write and notebook->desktop Taildrop method was promoted to canonical **transport-only**: `docs/execution-engineering/TS-EXECUTION-TRANSPORT-ONEDRIVE-TAILDROP-v1.md`.

The backlog derives from prior research `RADAR_2026-10-26_A_11-01.md` and the portable `HANDOFF-STACK-IA-DEV-TAILSCALE-20261101.md`; do not treat research as deployment or Product acceptance.

## Updated priority matrix

| Priority | Candidate | New primary-source findings / material risks | Decision | Next experimental gate |
|---|---|---|---|---|
| P1 | GitHub Actions dependency lockfiles | GA on Free, Team and Enterprise Cloud 2026-10-28. `github/gh-actions-lock` v0.4.0 still pre-1.0. `--verify-local` is offline **coverage-only**, whereas `--verify` checks provenance online. External reusable workflows at `jobs.*.uses` are not locked; local composite actions may require migration; unpinned containers remain warnings. | HIGH / ISOLATED_STATIC_EVAL / NO_PRODUCT_CHANGE | Create synthetic Actions workflow inventory; test positive coverage, unlisted `uses:`, local actions, external reusable workflows and unpinned image warning. No GitHub Action dispatch, no upgrades. |
| P2 | OpenCode2 2.2.x | Release v2.2.1 adds `/goal` until reviewer deems objective met and opt-in `/schedule`. v2.2.4 persistent Desktop terminal state; v2.2.5 compaction percentages and worktree shortcuts. This may conflict with no retry on UNKNOWN and explicit grant gates. Published v2.2.5 tag dated 2026-10-30; API `releases/latest` ambiguity returns v1 line, so do not infer latest solely from that endpoint. | HIGH / CONTRACT_RISK_REVIEW / NO_UPGRADE | Non-effectful matrix: provider OpenAI + model + reasoning.effort, permission, goal continuation, unknown/no-retry, terminal identity, Orca visibility, worktrees, replay between machines. Synthetic stubs only. |
| P3 | VS Code 1.144 Agent Host / AHP v1.0 | Agent Host separates client from running sessions and supports remote hosts; AHP v1.0 was released 2026-10-02. Neither source proves AHP interoperability with Orca or OpenCode2. VS Code Copilot cloud sessions require eligible paid plan. | MEDIUM_HIGH / RESEARCH / NO_MIGRATION | Design a host/client compatibility table and fictional transport handshake; no host process replacement. |
| P4 | GitHub Agentic Workflows | GA 2026-10-28; Markdown compiles to Actions workflows; uses sandbox, read-only by default, firewall, safe outputs, threat detection. Copilot default engine requires a license and compute/model charges must be controlled. | MEDIUM_HIGH / DESIGN_ONLY / NOT_DEPLOYED | Synthetic `staged:true` markdown outline and permission/threat model, no dispatch, no real repo workflow or grants. |
| P5 | GPT-6.1 Terra visual | Official model card: `reasoning.effort` none/low/medium/high/xhigh/max, Responses API tool calling, standard text token pricing input $1 / output $5 per million (cached input $0.05). API billing separate from ChatGPT; tool calls potentially extra. | MEDIUM / BENCHMARK_CANDIDATE / NO_PAID_RUN | Design identical bounded synthetic screenshot/GUI benchmarks and budget cap, then request separate effect grant. |
| HOLD | TinyFish Browser API vs Playwright | Previous `TF-EVAL-006` preflight ready, original remote dispatch blocked by platform security; offline R1 repair tests PASS. No evidence of provider session for blocked dispatch. | HOLD_EXECUTION_SURFACE / NO_RETRY | Do not bypass blocked run, no paid dispatch or session cleanup without proof. |
| WATCH | GitHub Copilot cloud sessions / mobile continuity | Oct 28 release adds cloud sandboxes and mobile continuity on paid Copilot; underlying Actions compute entitlement shared with sandbox billing starting 2026-11. Useful concept but duplicative with user’s established command topology and has subscription dependencies. | LOW / WATCH_COST / NO_ADOPTION | Revisit only if current Orca/Commander topology fails requirements. |

## Primary-source references consulted (2026-11-02)

- GitHub lockfiles GA: https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/
- gh-actions-lock README + v0.4.0: https://github.com/github/gh-actions-lock and https://github.com/github/gh-actions-lock/releases/tag/v0.4.0
- OpenCode changelog and v2.2.5: https://github.com/anomalyco/opencode/blob/dev/CHANGELOG.md and https://github.com/anomalyco/opencode/releases/tag/v2.2.5
- OpenCode permissions: https://opencode.ai/docs/es/permissions/
- VS Code Agent Host & AHP: https://code.visualstudio.com/updates/v1_144
- GitHub Agentic Workflows GA: https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/
- OpenAI Terra model: https://developers.openai.com/api/docs/models/gpt-6.1-terra
- GitHub Copilot cross-surface cloud: https://github.blog/changelog/2026-10-28-work-from-anywhere-with-a-new-connected-copilot-cloud-experience/

## Compatibility and security boundary

1. Research conclusions are **not** authority for Product acceptance, Phase 2, grants or a new TaskCycle.
2. Do not upgrade OpenCode2 on notebook/desktop, alter Orca, add GitHub Actions to real repos, publish agent workflows, or run paid benchmarks from this report.
3. Any future effectful gate needs its own explicit scope, expected identity, non-interference constraints, negative tests, cost cap and independent review.
4. Commander remains an execution/result surface only. Source review through GitHub/web or other authorized semantic surfaces.
5. Unknown provider/tool effects remain **UNKNOWN_NO_RETRY** until reconciled; no auto-loops even when a tool offers `/goal`, `/schedule` or built-in retry.
6. Transport v1 does not promote an automatic executor. The notebook remains primary, desktop visual, mobile auxiliary.

## Next competent bounded action

**P1 / STATIC_LOCKFILE_MATRIX_001**: in an isolated scratch test fixture, assemble a *non-dispatched* workflow and negative cases documenting coverage vs provenance, local actions and reusable workflows. Publish a distinct candidate and offline test receipt, then independent review before even proposing any real repo adoption. P2 contract matrix can proceed read-only in parallel. No new grants are inferred.
