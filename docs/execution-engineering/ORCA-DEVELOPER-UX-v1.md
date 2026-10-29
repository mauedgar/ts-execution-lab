# Orca Developer UX v1

Status: candidate operating contract

Scope: desktop workstation, Orca GUI, WSL worktrees and observable developer sessions

Authority: Execution Engineering mechanics only; Product authority `NONE`

## 1. Purpose and boundary

Orca is the local control and observation surface for development. It owns neither Product meaning nor lifecycle acceptance. Product repositories, their competent controls and their Upper LC sources continue to decide responsibility, baseline, DoD, validation, review, acceptance, integration and close.

The workstation contract is:

```text
permanent root = stable control surface
task worktree = one bounded responsibility
terminal = one visible role or process
Orca status = operational state, never Product authority
```

No Orca setup may copy `.env`, install dependencies, share `node_modules`, open a browser, launch an agent or start an application. Setup and initial tab commands are informational and must return to the prompt.

## 2. Canonical roots and bases

| Product | Permanent root | New-worktree base | Root board state |
| --- | --- | --- | --- |
| Tecnotron WSL | `/home/tecnotron/workspaces/tecnotron-ai` | `origin/tools` | `Done`, pinned |
| FitFlow WSL | `/home/tecnotron/workspaces/FitFlow` | `origin/develop` | `Done`, pinned |
| TS Execution Lab | `C:/Proyectos-Web/Checkpoint/TS-Execution-Lab` | `origin/main` | `Done`, pinned |

The historical Tecnotron Windows root remains `In progress` while original PID 27032 has unresolved effect state. A default base changes only future materialization; it never updates the root checkout or grants Product authority.

## 3. Standard layouts

Tecnotron:

1. `01 · TEC · Control`
2. `02 · TEC · Shell`
3. `03 · TEC · Validate`

FitFlow:

1. `01 · FF · Control`
2. `02 · FF · App`
3. `03 · FF · Playwright`
4. `04 · FF · Logs`

TS Execution Lab:

1. `01 · TS · Control`
2. `02 · TS · Experiment`
3. `03 · TS · Evidence`

An agent is launched only after the carrier and authority have been checked. Its tab is renamed `10 · Agent · <role>`.

## 4. Worktree creation contract

Before creation, reobserve the competent SOT, base ref and commit/tree, authority, responsibility, DoD, ownership and known effects. Then create without an agent:

```text
orca worktree create \
  --repo id:<repo> \
  --name <product>-<responsibility>-<run> \
  --base-branch <origin/ref> \
  --parent-worktree id:<root> \
  --setup run \
  --reference <issue-or-review-url> \
  --comment "stage=materialized; subject=<exact>; authority=<ref>; DoD=<ref>; attempt=<id>; next=<gate>" \
  --activate \
  --json
```

Persist the creation JSON as the materialization receipt and place the card in `Todo`. Verify the exact carrier before a separate launch:

```text
orca agent launch \
  --agent <agent> \
  --worktree id:<worktree> \
  --surface terminal \
  --prompt <carrier> \
  --json
```

Never place credentials, tokens or private payloads in an Orca comment.

## 5. Board semantics

| Orca state | Operational meaning |
| --- | --- |
| `Todo` | Materialized and bounded; no active attempt |
| `In progress` | Exactly one implementation attempt or external observation is active |
| `In review` | Deterministic validation or independent review is pending |
| `Done` | Terminal return is persisted and all operational obligations are closed |

`Done` does not mean Product acceptance, merge or close. Permanent roots are pinned in `Done` because they are surfaces, not responsibilities. Only real task worktrees circulate through active columns.

## 6. Receipts and terminal correspondence

Every significant execution records:

```yaml
subject:
precondition:
request:
binding:
provider_native_ref:
result:
effect_state:
receipt_ref:
terminal_correspondence:
next_competent_boundary:
```

Distinguish execution success, validation success, Independent Review, Developer acceptance, Product integration and Product close. A technical `PASS` advances only the gate authorized by the competent Product contract.

## 7. Observation and waiting

Use one dispatch per exact `ExecutionAttempt`. While it runs, advance only disjoint authorized work. At the dependency boundary, observe the exact durable result once and reconcile identity and effects.

- Commander is never used for polling or semantic decisions.
- A missing file or silent terminal is not proof of no effect.
- `UNKNOWN` blocks retry, kill, acceptance, integration and cleanup.
- When no qualified wait is available, return `PENDING_EXTERNAL_RESULT` with exact references.
- Never relaunch an attempt merely because its result is late.

## 8. FitFlow Issue #25 — ADMIN Playwright

Materialize `fitflow-issue25-admin-playwright-001` only from a freshly observed `origin/develop` and link Issue #25. Start the authorized application stack explicitly in `02 · FF · App`, then discover the listener:

```text
orca ports --worktree id:<worktree> --json
```

Do not hardcode a port. In `03 · FF · Playwright`, use an ephemeral named headed session:

```text
playwright-cli -s=fitflow-issue25-admin-001 open <advertised-or-connect-url> --headed
```

Keep the terminal and browser visible. Use `console`, `requests`, tracing, screenshots or video only as required by the DoD. Credentials come from secure local environment injection, never from chat history or Orca comments. Close the Playwright session at the end, persist the trace or equivalent evidence, return the technical result to FitFlow Control, and verify that the worktree has no accidental changes.

## 9. Tecnotron Beta Run 001

Reconcile attempt 002 and its external result before any new implementation. Do not replay Phase 1 or create another attempt. While the original provider effect is unresolved, preserve `PENDING_EXTERNAL_RESULT`.

Only after the exact OpenCode v2.2.1 binding returns competent `PASS` may the same binding be qualified on desktop and a Phase 1 worktree be materialized from `origin/tools` with Issue #34. Implementation, deterministic validation and independent review use separate sessions. Phase 2 remains prohibited until competent acceptance.

## 10. TS-BEADS-036

Materialize `ts-beads-036-b-first-001` from a freshly observed `origin/main` as `EXPERIMENTAL / Product authority NONE`. Recover and publish the pending 036 report before new experiment work; do not repeat TS-BEADS-035.

Continue B-first with isolated Dolt. Alternative A remains an informational transition only. Never write the shared Product store, migrate Tecnotron, or create another Kernel, scheduler or storage layer. Persist result and receipts before returning control to `TS- BEADS`.

## 11. Cleanup gate

A task worktree may be removed only when all conditions are true:

- terminal result and effect state are known;
- durable evidence is persisted;
- no live or unverifiable terminals remain;
- Git is clean, or every local change is explicitly preserved;
- the task owner and next competent boundary are recorded.

Before removal, capture `worktree show`, `terminal list --include-visual-layouts`, `git status` and the final receipt. Root worktrees are not cleanup candidates.

## 12. Acceptance checklist

- YAML parses and contains only the exact ordered tab titles.
- Setup and tab commands are informational-only.
- No `.env` copy, dependency installation, `sharedDirectories`, automatic browser or automatic agent exists.
- A test worktree per repository reproduces the exact layout.
- Opening a worktree leaves Git clean and starts no application process.
- FitFlow demonstrates Orca URL discovery, visible headed browser, observable Playwright terminal, named session, recoverable trace and clean closure.
- Roots are pinned in `Done`; only bounded responsibilities remain active.
- Every meaningful effect has a reconstructable receipt and terminal correspondence.

This contract refines the developer surface only. It creates no Product authority and does not override any Product-local SOT, Upper LC source, TASK, DoD or acceptance boundary.
