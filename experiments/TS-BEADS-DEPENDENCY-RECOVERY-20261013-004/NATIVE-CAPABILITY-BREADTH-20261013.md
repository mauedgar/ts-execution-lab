# Beads v1.3.1 — native capability breadth beyond the handoff inbox

Classification: research inventory, NONE_PRODUCT. Date: 2026-10-13.
Status: DOCUMENTED_UPSTREAM for features below unless explicitly marked OBSERVED in a synthetic pilot.
Decision: **NO_ADOPTION_DECISION**; user authorized empirical evaluation and reuse-before-build, not Product integration.

## Directly relevant to the continuity problem

| Beads mechanism | Potential Tecnotron responsibility to absorb | Evidence/status | Boundary |
|---|---|---|---|
| `discovered-from` typed nonblocking provenance | durable discovered obligations and linking source work | **OBSERVED** synthetic Pilot 004 creation; full native graph semantics DOCUMENTED | exact SOT/receipt references still must come from Product/Transport |
| `blocks`, `bd ready` | blocked/resumable continuations and independent ready work | **OBSERVED** Pilot 004: A continuation hidden until B closed, C still ready | ready != authorized Product gate |
| Dolt persistent database | cross-process continuity without chat memory | **OBSERVED** Pilot 001, 002 and 004 | host-local embedded, not remote wake |
| `bd update --claim`, `bd ready --claim` | one agent claims pending item instead of duplicate work selection | DOCUMENTED, **UNTESTED multiwriter** | claim != Product selection/grant; requires shared qualified write binding |
| `bd dep cycles` and typed dependency validation | safe work graph and prevention of invalid cycles | DOCUMENTED; not observed in Pilot 004 | graph topology alone does not encode lifecycle semantics |

## More substantial opportunities not assumed in initial handoff proposal

| Native Beads feature | Could displace custom code if empirically qualified | Caveat |
|---|---|---|
| **Molecules** (persistent epic with ordered/parallel children) | non-authoritative workflow progress/dependency traversal and perhaps some custom operational queue | Could **overlap Upper LC/TaskCycle Core**, so no migration or Product pipeline rewrite without competent architecture/equivalence decision |
| **Formulas** (`bd cook`, `bd mol pour`) | reusing declarative DAG templates, variable substitutions and fan-out/fan-in without writing a new TS scheduler | A workflow template does not authorize its instantiation or prove exact candidate receipts/IR/acceptance |
| **Wisps** (ephemeral molecules) | short-lived operational experiments, release checks, health loops with optional digest | Ephemeral/purge **not suitable for indispensable audit**, unknown effects or immutable Product evidence |
| **Gates** (human/CI/PR/timer) | waiting on external conditions from a graph without custom polling framework | Native gate resolution does not substitute Developer grant, Product preconditions or qualified Web deferred join |
| **`merge-slot`** | serialized write/merge coordination between independent agents | Native lock != Product merge authority or proof of Git commit/tree/combined validations |
| **`bd assign`, comments, messaging** | agent-targeted operational inbox and handoffs without chat prompt injection | An assignee is a text label, not a qualified autonomous ChatGPT Web agent registry, and messaging does not automatically wake completed chats |
| **Dolt remotes, federation, backup** | cross-machine operational state, recovery of working obligations | Distinguish full Dolt history backup from JSONL export; cannot silently retire Git-based Product SOT/Transport |
| **Native GitHub Issue/PR integrations** | reduce duplicate issue synchronization glue | Must evaluate exact fields/Projects alignment and prevent two writable canonical authorities |

## Adoption hypothesis matrix — minimize custom system rather than wrap it

- **NARROW/REPLACE_CANDIDATE:** non-authoritative operational obligation list, dependencies, `ready` work index, a cross-process checkpoint pointer store, manual handoff index and simple agent claim coordination.
- **EXPLORE_AS_REPLACEMENT:** operational workflow/DAG traversal now done by bespoke runner glue (molecules/formulas/gates), only after consumer inventory and equivalence proof. Do not hard-code Beads as an Upper LC Product lifecycle oracle.
- **KEEP_UNLESS_PROVEN_EQUIVALENT:** Product SOT, canonical decisions, TaskCycle identity/state and grant root, exact Git candidate/receipt transport, Independent Review input/frozen semantics, Developer acceptance, Phase 2 and merge authority, `UNKNOWN` effect reconciliation.
- **DO_NOT_DEFAULT:** new scheduler, agent registry, Beads remote service, GitHub Projects two-way syncing, or tracking every shell subprocess as Product issues.

## Current empirical ceiling / next tests

Pilot 004 is `PASS_SYNTHETIC_CONTINUITY` with exact fresh-process before/resume/readback; original attempt `BEADS-DEPENDENCY-RECOVERY-20261013-001`, `mauedgar/ts-execution-lab@f154204574fe24e0ea75cfcf3f9b6d994528f817:experiments/TS-BEADS-DEPENDENCY-RECOVERY-20261013-004/PILOT-RESULT-20261013-004.md`. It does NOT prove parallel agents, multiwriter atomic claims or automatic cross-chat recovery.

Dolt server binding is a separate experimental line; until qualified it remains `HOST_BINDING_PENDING` on the user's device. Concurrent write trial requires server-mode preflight, not embedded-mode race on one database.

## Version-pinned sources

- https://github.com/gastownhall/beads/blob/v1.3.1/docs/core-concepts/dependencies.md
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/multi-agent/coordination.md
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/formulas.md
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/molecules.md
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/wisps.md
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/architecture/dolt.md

**Warning:** documentation is vendor/source evidence, not a successful qualification of every version-specific feature. This is a decision input, not new canonical documentation.
