# TS AI Dev Stack — Research round R1, 2026-11-02

```yaml
artifact:
  id: TS-AI-DEV-STACK-R1-RESEARCH-20261102-001
  kind: EVIDENCE_BASED_RESEARCH_NON_PRODUCT
  status: RESEARCH_COMPLETED_GATE_PENDING
authority:
  product: NONE
  taskcycle: NONE
  configuration_changes: NONE
  actual_software_upgrade: NONE
  CI_dispatch: NONE
  paid_model_invocation: NONE
```

## Research baseline
User explicitly authorized research after canonical **OneDrive education + SharePoint cloud->notebook + bidirectional Taildrop** transport was established. The existing transport policy is **not** changed by this research. The current source of truth for grants, independent reviews, UNKNOWN states, and execution boundaries remains the previously accepted Execution Engineering contract.

## Ranked evaluation

### P1 — GitHub Actions workflow dependency lockfiles: CANDIDATE / ISOLATED CLI GATE NEXT
**Verified first-party documents:** GitHub Actions lockfiles GA on Free/Team/Enterprise Cloud 2026-10-28. `gh actions-lock` supports `--verify-local` (offline coverage only), `--verify` (online provenance), `--no-fix` (nonmutating network report), and `--relock` (mutating). `gh-actions-lock` is pre-1.0; flags/format subject to change. The lockfile is `.github/workflows/actions.lock`, not GitHub Agentic Workflows `.lock.yml`.

**Adoption blockers to test:** external `jobs.<id>.uses` reusable workflows are not locked by consumer lockfile; local `./` composite actions must be migrated or explicitly handled; unpinned container images warn; old-but-valid commits may still be vulnerable; `--verify-local` is not a provenance gate.

**Bounded next gate:** execute the actual pinned CLI in a temporary synthetic repository checkout with zero Actions triggers, test positive+negative cases, review lockfile and CLI version SHA. Explicitly NO modifications to FitFlow/Tecnotron/TS transport workflows. Do not activate "Require lockfile" policy before audit and review.

Sources:
- https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/
- https://github.com/github/gh-actions-lock
- https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies

### P2 — OpenCode2 2.2.5: CONTRACT RISK / SIMULATION COMPLETE / NO HOST UPGRADE
OpenCode V2 changelog v2.2.1 adds `/goal` (continuation until reviewed objective) and opt-in `/schedule` (scheduled prompts). V2.2.5 fixes large stdio MCP messages, compaction, worktree shortcuts, model switching reasoning continuity. Those improvements **do not authorize** recurring tasks, retries, model switching, code patching, or effects.

**Critical config discrepancy**: V2 permissions schema is `permissions` ordered `{action:'shell',resource:'...',effect:'ask|deny|allow'}`, **last matching rule wins**, rather than V1 `permission/bash/task`. Correct provider must be OpenAI, correct model and reasoning effort explicitly bound, with current environment-specific available values verified; do not guess from model picker.

**Gate:** offline matrix for `READY/UNKNOWN/RUNNING/PASS/BLOCKED`; signed identity, model/provider/effort, re-entered `/goal`, scheduled task lacking grant, restored Orca session and worktrees; all effects default-denied until independent authorization. No OpenCode2 launch or upgrade.

Sources:
- https://github.com/anomalyco/opencode/blob/dev/CHANGELOG.md
- https://dev.opencode.ai/v2/docs/permissions/
- https://github.com/anomalyco/opencode/releases/tag/v2.2.5

### P3 — AHP / VS Code Agent Host: PROTOCOL RESEARCH / NO ORCA MIGRATION
Agent Host owns persistent sessions; clients subscribe to snapshot + ordered action stream. AHP over WebSocket supports reconnect with `lastSeenServerSeq`; replay available actions or snapshot when gap exceeds replay window. **This synchronizes UI state and is not proof of repeat-safe external effects.** Session ids/capabilities come from host; must not synthesize host identity or assume Orca/OpenCode2 implements AHP.

**Gate:** mocked host/client test spanning notebook visual host, desktop client, Android observer; disconnect, buffer exhaustion, partial sessions, version drift, capability negotiation and external authority; no real AHP server deployed.

Sources:
- https://code.visualstudio.com/docs/agents/concepts/agent-host
- https://microsoft.github.io/agent-host-protocol/
- https://github.com/microsoft/agent-host-protocol/blob/main/docs/specification/lifecycle.md

### P4 — GitHub Agentic Workflows: DESIGN CANDIDATE / NO DEPLOYMENT
GA 2026-10-28, Markdown compiled to Actions YAML, default read-only sandbox + firewall, threat detection and safe outputs on default path; `staged:true` previews proposed outputs. Controls can be configured/overridden and therefore cannot replace Tecnotron's grant/IR/acceptance contract. Default Copilot CLI engine requires license; runner/model cost remains a separate budget issue.

**Gate:** isolated design-only workflow for CI triage with no writes or secrets, compile/static review in disposable lab when authorized; never dispatch to canonical product repos or silently accept output.

Sources:
- https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available/
- https://github.github.com/gh-aw/introduction/ai-transparency/
- https://github.github.com/gh-aw/

### P5 — OpenAI GPT-6.1 Terra: BENCHMARK DESIGN ONLY / NO BILLABLE REQUEST
Official API model `gpt-6.1-terra` for visual computer use; reasoning effort `none,low,medium,high,xhigh,max`, default medium; tools through Responses API. Standard token prices $1/1M input, $0.05/1M cached input, $5/1M output; API is billed separately from ChatGPT, with tool fees potentially additional. ChatGPT Work/Codex access is not evidence of API entitlements.

**Gate:** design a matched visual benchmark with public/synthetic screenshots and OCR-agnostic evaluator, budget cap, identical traces and pass/fail counters, token/tool accounting; only run after cost grant. Avoid using it for routine engineering if an existing free/low-cost model passes.

Sources:
- https://developers.openai.com/api/docs/models/gpt-6.1-terra
- https://openai.com/index/introducing-gpt-6-1-terra/

## Offline safety oracle

16/16 synthetic policy tests **PASS**. This tests only our policy model, not upstream tools:
- Actions: missing lock entry, external reusable workflow, local action path, unpinned container, coverage-vs-provenance.
- OpenCode2: UNKNOWN_NO_RETRY, missing grant, unbounded schedule, bounded synthetic schedule.
- AHP: replay for display only, missing sequence snapshot, session id mismatch, sequence regression.

**Crucial limit:** No actual `gh-actions-lock` invocation or provenance verification, no OpenCode runtime `/goal`/`/schedule`, no AHP server, no gh-aw dispatch and no paid model call. Therefore `RESEARCH_PASS` **not** `TOOL_COMPATIBILITY_PASS`, Product adoption or upgrades.

Test harness: `docs/execution-engineering/research/TS-AI-DEV-STACK-ISOLATED-20261102-001/static_gate_tests.py`.

## Decision / priority
1. **P1 actual CLI in isolated synthetic fixture**, then independent review. Does not enable a canonical Actions lockfile until the real CLI qualifies.
2. **P2 OpenCode V2 permissions/goal static contract**, prioritizing no-retry authority, OpenAI provider and correct effort. Do not migrate host.
3. **P3 AHP mock protocol compatibility** only if Orca session continuity still has measurable gaps.
4. **P4 staged gh-aw design**, not deployment.
5. **P5 Terra only with separate paid API quota and budget authorization**.

## SharePoint permissions
Observed the ChatGPT **SharePoint-specific** override: `Allow all actions`; global default is `Allow low-risk actions`. Recommend the user select `Allow read actions (ask before making changes)` in Settings > Plugins > SharePoint > Permissions. No programmatic change was made because the request did not specify one of the exact modes; plugin setting mutation requires explicit choice. This is distinct from institutional Microsoft OAuth scopes.

## Invariants
Transport-only v1 stays canonical within its qualified envelope. No Product/TaskCycle/grants/Phase 2/IR transferred. No real repo changes, CI runs, Work/Cloud Browser side effects, paid model requests, unconfirmed retries or remote execution bypasses. Semantic research only through approved file/GitHub/web surfaces. Unresolved effects preserve UNKNOWN and block duplicate attempts.
