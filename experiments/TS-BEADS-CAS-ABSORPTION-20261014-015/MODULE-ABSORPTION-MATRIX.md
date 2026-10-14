# TS Beads 015 — Broader Tecnotron module absorption assessment

**Scope:** experimental candidate assessment only, no Product grant, integration, migration or new authority. Cutoff: 2026-10-14. Beads release **v1.3.1** (GitHub latest release at observation). Comparison against current Product branch `mauedgar/tecnotron-ai:tools@1ecce07708a5760c99d7faf55f2344f2eabbc119`, tree `025ce7524d1b8bf1753cfc4af964ee554d3b0977`. Product `docs/SOURCE_OF_TRUTH.md`, `docs/architecture-knowledge-ownership-baseline.md`, `docs/capability-map.md`, `docs/operational-architecture.md` and direct referenced source files observed. This is a current experimental view, not a canonical consumer inventory or Product decision.

Evidence labels: `NATIVE_PREVIOUS` = qualified by 005–014 bounded pilots only, not necessarily live Product; `NATIVE_015` = qualified in 015 only if terminal receipts support it; `SOURCE_V1.3.1` = native feature identified in Beads release docs/source, not Product conformance. `PROPOSED` has no grant.

| Tecnotron module/capability | Beads facility | Fit and ownership decision *candidate* | Boundary/gap |
|---|---|---|---|
| State Kernel V0 persistence and lifecycle adapter | Native issue identities, Dolt history/metadata, events, HTTP `MetadataCAS`, transactional role and expected-version lifecycle | **HIGH: replace persistence after semantics parity; not yet physically retired** | Authority, legal transition rules, exact TaskCycle/Operation/ExecutionAttempt identities, `NONE/CONFIRMED/UNKNOWN` + reconciliation, immutable receipts, multi-aggregate atomicity stay Product-specific until proven |
| Operational task index / queues / discovery and cross-module inbox | `bd ready`, `bd blocked`, dependency DAG, `discovered-from`, claims, cross-repo routing | **HIGH: native work index; consolidate duplicate planning/progress queues** | A Beads-ready task is not Product-granted; a discovered candidate is not initialized TaskCycle; GitHub planning projection and Product Control retain ownership |
| Coordinator's dependency frontier and worker allocation | Native ready frontier; `bd update --claim`, `bd ready --claim`, deps, molecules/formulas, gates and wisps | **MEDIUM-HIGH: absorb generic graph/claims, narrow Coordinator** | Beads does not run bounded Recipes or reconcile external provider effects merely by holding a claim; cannot add new scheduler/gates by default |
| RunStore / SQLite projection and duplicate operational state summaries | Dolt issue history, event/audit stream, issue queries and `bd kv` | **HIGH for redundant operational bookkeeping; direct deletion candidate only after real consumer check** | Existing RunStore `src/core/run-store.js` stores typed run events and snapshot files, with SQLite projection; 2026-10-04 consumer inventory found no active caller, but this is not current deletion authority. Beads event semantics vs RunEvent must be compared before assuming drop-in |
| Continuation snapshot & cross-session operational work | Issue metadata, notes, links, history, source refs, `bd memories`, work handoffs | **MEDIUM-HIGH for operational recovery pointers; use links instead of a second task store** | Portable `manifest.json`/hash, context sufficiency, provenance and semantic handoff still require exact external Git/evidence contract. `bd mail` delegates to *another* provider; it does NOT itself supply Web wakeup/inbox |
| GitHub Issues/Projects operational projection | Beads native tasks and metadata external refs; configurable integrations, Git remote Dolt | **MEDIUM: use either as operational index, avoid dual mutable masters** | GitHub owns its Issues/Projects IDs and planning projection. No automatic sync/adoption; Project `Ready` not inferred from `bd ready` |
| ExecutionRecordStore / lightweight counters and observed events | Dolt history, events journal (ordered replayable mutation feed, with configurable retention), typed metadata | **MEDIUM: consolidate operational event projection conditionally** | GitHub Actions provider run/job ID, original attempt receipts and external ACK are not native Beads event facts; no double write or new audit SOT |
| ContextPackager, repo-packager and knowledge retrieval | Beads memories, `bd prime`/context hints, task-linked notes | **LOW for wholesale replacement; useful index pointers only** | Actual repository/file search, evidence packaging, deterministic coverage/budget, action sufficiency and source hashes retain current owners |
| AgentRuntime / Router / ModelResolver / FinOps | Assignees, agent-work hints in namespaced metadata, multi-repo routing | **LOW for replacement; possible narrower hints** | Agent/provider/model policy, context/token pricing and actor execution do not become Beads-native semantic capabilities |
| Recipes, transport, executable workspaces, Git qualification | Workflow molecules, formulas, gates and claims can *describe* mechanics | **LOW wholesale; reuse preflight/graph primitives** | Native molecule status neither executes selected Recipe nor verifies Git candidate tree and receipts; original deterministic Recipes still own bounded mechanics |
| IR, Developer acceptance, Product Control | Beads gate/dependency can represent an external checkpoint | **NOT ABSORBABLE AS AUTHORITY** | Reviewer independence, Developer grants, Phase 2, terminal close and productive `UNKNOWN` reconciliation remain competent Product decisions; Beads may store pointers, never grant them |
| SOT, permanent architectural decisions, accepted evidence | Beads metadata can link canonical refs | **NOT REPLACEABLE** | Git repository SOT, exact commit/tree/blob evidence, accepted ADRs and branch protection continue under their existing authority |

## Existing native evidence reused, without replay

- `TS-BEADS-NATIVE-GRAPH-FORMULA-005`: native DAG, ready frontier and formula proof within separate synthetic Dolt lab; no Product effects.
- `TS-BEADS-UNKNOWN-HANDOFF-20261013-010`: fresh native GitHub remote readback, exactly-one synthetic origin, no duplicate replay, synthetic handoff claim/close, independent fresh consumer audit; no Product authority.
- `TS-BEADS-CONSUMER-SHADOW-012`: 15/15 deterministic Product/Beads index comparison, **model-only**.
- `TS-BEADS-NATIVE-CONSUMER-SHADOW-013`: native fresh consumer successfully bootstrapped shared immutable Dolt ref, read 4 issues and 3 ready, Product unchanged.
- `TS-BEADS-LIFECYCLE-PARITY-014`: 21/21 native plus synthetic adapter checks; ordinary unguarded `bd update --metadata` accepts a stale writer and bare `bd close` accepts a close without Product grant, **not proof native Beads lacks CAS**.
- `015`: current native MetadataCAS experiment, evaluated in separate `RESULT.md` with exact terminal run or explicit limitation. Do not infer its result from this assessment.

## Source feature references (pinned v1.3.1)

- https://github.com/gastownhall/beads/blob/v1.3.1/issueops/metadatacas.go — one-key transactional CAS and `Current`/non-winner semantics; not Product authorization.
- https://github.com/gastownhall/beads/blob/v1.3.1/internal/httpapi/metadata_cas.go — `POST /v0/beads/issues/{id}:casMetadata`.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/multi-agent/index.md — native ready/claim, agent assignment, cross-repo dependencies.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/molecules.md — dependency-ordered molecules.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/formulas.md — formula templates and gates.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/reference/events-journal.md — ordered event feed, retention, cursor and limitations.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/cli-reference/mail.md — **delegated**, not built-in mail.
- https://github.com/gastownhall/beads/blob/v1.3.1/docs/cli-reference/kv.md — operational key-value store.

## Recommended simplification order (research, not authorization)

1. **Index-first:** use Beads as read-only operational ready/blocked/claims/discovered-from projection for Control; quantify whether a distinct task queue/inbox actually disappears, avoid a parallel master.
2. **Transactional state parity:** certify native CAS, lifecycle version guards, independent external receipt reconciliation, concurrency, atomic close, crash and shared-remote recovery before replacing State Kernel persistence.
3. **Consolidate duplicate operational storage:** compare RunStore's current live consumers and event schemas to Beads event journal and Dolt; delete only truly redundant code after separate Product authorization.
4. **Narrow coordinator/continuation:** reuse Beads dependency/claim/molecule metadata instead of inventing another scheduler, but preserve semantic authorization, portable manifests and selected deterministic Recipe execution.

**Optimization hypothesis**: maximum native Beads for agent work tracking, task graph, claims, historic state and notifications *of changed Beads data*; minimal Product-specific policy for identity, authorization, semantic sufficiency, external effect receipt reconciliation and independent review. No additional Product layers, orchestrator, duplicated mutable ledgers or new gates are justified by this assessment.
