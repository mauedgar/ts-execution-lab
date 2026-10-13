# TS — Beads | Experimental evaluation charter and Definition of Done
Date: 2026-10-13
Classification: EXPERIMENTAL_RESEARCH_ONLY
Product authority: NONE
Scope: evaluation and synthetic pilots only; no Product TaskCycle start, adoption, refactor, migration or integration
Owner of Product authority: existing Tecnotron competent Control/Developer
Working principle: REUSE / ADOPT BEFORE BUILD

## Purpose and decision question
Determine which existing Tecnotron operational responsibilities Beads can **own natively** (not merely mirror), including responsibilities we have not yet anticipated, and whether using it reduces total implementation and maintenance cost without losing Product invariants. The decision is **not** to assume Beads must be adopted. Compare Beads to current Tecnotron capabilities, GitHub Issues/Projects, and existing Git/Transport mechanics, and explicitly keep the option **no adoption**.

Primary user pain: a pipeline/TaskCycle exposes cross-module dependencies, attention shifts, and the original responsibility becomes hard to recover. In parallel pipelines, the same origin may generate duplicate obligations, repeated effort or interference. Need durable discoverable obligations with exact provenance, correct dependencies, and safe return to original responsibility.

## Authority and containment
- Product truth, scope, TaskCycle/Upper LC gates, grants, independent review, acceptance and effect reconciliation stay with competent Tecnotron authorities and repository SOT.
- Beads is an **experimental operational candidate**, not a Product state machine, new source of authority, automatic TaskCycle initializer, scheduler or second canonical ledger.
- Do not modify Tecnotron Product repos, active TaskCycles, GitHub Projects or existing State Kernel consumers in this research. Any physical replacement requires separate competent Product decision, fresh consumer and equivalence evidence, and the normal authorized lifecycle.
- Synthetic responsibilities may resemble TaskCycles for a realistic scenario but have no Product effects or authority.
- Local isolated Beads v1.3.1 on DESKTOP-3LJ0E54 is an observed test binding, not a mandatory architecture. Commander only executes a pre-determined bounded mechanical invocation and returns compact results; never explores or constructs patches. Use existing transport or exported file for richer evidence; do not create another publisher. MCP/remote connection and automatic Git Transport publication remain separate qualifications, not requirements for local evaluation.
- Every observation records exact repository/commit or source reference, test identity, attempts, host/binary when relevant, terminal status, effect/receipt provenance and limitations. Preserve failed attempts without blind rerun.

## Capability exploration — not only known use cases
Assess native capabilities and whether each truly helps Tecnotron:
1. **Continuity/inbox:** capture a discovered obligation without diverting the active pipeline, trace back to the exact source and checkpoint, recover from a new process/chat, and query pending work at a meaningful handoff or closure.
2. **Graph/work selection:** origin relationships, depends-on/blocks, readiness, ordering, cross-module references, ownership/claim and priority, including ability to keep independent work moving while a dependency is unresolved.
3. **Parallelism/conflict:** independent pipelines on shared state; simultaneous ingestion of the same source; same title from different sources; write collisions and safe retries after uncertain outcomes.
4. **Portability/operations:** data export, backup/recovery, Git/GitHub interaction, cross-machine availability, access from ChatGPT Web through existing local transport; maintenance/upgrades and operational complexity. Do not assume native GitHub Projects field sync or native multi-agent coordination without evidence.
5. **Absorption opportunities:** operational obligation list, dependency/indexing, ready queue, continuation breadcrumbs, ownership assignment, duplicate suppression and other native features discovered in research. Examine whether one external capability can **replace**, **narrow**, or **leave untouched** each current subsystem; do not retrofit unrelated Product semantics into Beads.

For each capability, distinguish: DOCUMENTED / OBSERVED_PASS / OBSERVED_FAIL / UNTESTED / INCOMPATIBLE, with source and exact evidence. A product claim or a synthetic demonstration is not Product equivalence.

## Evidence already available (fixed, non-repeatable history)
- Pilot 001: `PASS_LOCAL_SYNTHETIC_WITH_LIMITATIONS`; one handoff persisted and recovered after checkpoint. No Product or automatic end-of-chat detection. Report: `mauedgar/ts-execution-lab@603fa23657a656852784ed034f188647dcb6c089:experiments/TS-BEADS-CONTINUITY-PILOT-20261013-001/PILOT-RESULT-20261013-001.md`.
- Pilot 002: `PASS_SEQUENTIAL_DEDUP_WITH_RECOVERED_READBACK_AND_LIMITATIONS`; repeated same source mapped to one obligation, different sources with same title stayed distinct; 12/12 recovered read-only checks. Dedup was consumer policy, not Beads-native or concurrent guarantee. Report: `mauedgar/ts-execution-lab@2c98305af8ae72b02f571d0ec13be62c8635df15:experiments/TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/PILOT-RESULT-20261013-002.md`.
- Previous FAIL/BLOCKED attempts and their mechanical receipts retain original dispositions. Web-side reports do **not** prove host-native Git Transport publication.

## Next bounded experiments (research sequence, not Product gates)
A. **Pilot 003 — concurrent ingestion and non-interference:** two independent synchronized local processes; record a demonstrated overlap in critical operation intervals, verify each can advance its separate responsibility, race identical source ref, and distinguish other source with identical title. Independent third-process readback verifies cardinality, links, data and statuses. Report duplicates, lock/contention errors or ambiguous outcomes as actual findings; do not hide behind sequential pre-check. If no native atomic uniqueness exists, evaluate the minimum safe single-writer/locking strategy and its cost **without claiming it is already qualified**.
B. **Representative continuity scenario:** synthetic pipeline A discovers a dependency belonging to module B, records exact origin/checkpoint, remains on permitted work or stops at a specified dependency, and resumes from its original point only after a competent *simulated* dependency disposition. Prove no invented authority, no lost obligations, no unauthorized duplicate execution, and that independent pipeline C can proceed. Recovery must work in a fresh process and from exported evidence.
C. **Breadth and replacement study:** verify native features against documented behavior, then produce an ownership/equivalence matrix across current Tecnotron mechanisms and GitHub Projects/Transport. Classify KEEP / NARROW / REPLACE_CANDIDATE / NOT_APPLICABLE, with consumer list, exact missing semantics, TCO/maintenance and portability risk. State Kernel replacement cannot be recommended without independently proving `NONE / CONFIRMED / UNKNOWN`, effect reconciliation, blocked retry under UNKNOWN, receipt integrity and auditability. No physical change here.

## Experimental Definition of Done
The evaluation is ready **for a Product adoption decision**, not adopted, only when:
- [ ] A capability inventory covers both known needs and at least one deliberate search for unanticipated useful native features; feature claims are sourced and labeled by evidence class.
- [ ] Pilot 003 has a terminal, reconciled result and independent readback. A failure is documented, not rebranded PASS; any mitigation is tested separately if proposed.
- [ ] The cross-module interruption/resumption scenario demonstrates correct provenance, dependency links and recovery with no repeated effect, or records a concrete limitation.
- [ ] A comparison table identifies which **current** components Beads could absorb and what exact semantic guarantees must remain outside it, informed by current consumers at a specified repo ref.
- [ ] Risks are assessed: concurrency, durability, portability, GitHub synchronization, operational ownership, failure modes, future maintenance and multi-host/Web access.
- [ ] We can estimate **net** simplification: code/components likely removable vs new adapters/operations; unsupported quantities are marked UNKNOWN rather than invented.
- [ ] A concluding recommendation selects one of `ADOPT_CANDIDATE_WITH_BOUNDED_SCOPE`, `CONTINUE_RESEARCH`, or `DO_NOT_ADOPT`, with exact evidence and an explicit list of unresolved blockers.
- [ ] Results are recoverable via immutable Git reference or verified exported artifact; no need for chat Memory or replaying a completed effect.

## Success / stop rules
- Research can succeed by proving Beads is *not* a good replacement; finding a failure is valid evidence.
- Stop any execution when original attempt status/effects are UNKNOWN until exact reconciliation; don't retry blindly.
- If an experiment would change Product authority, active TaskCycles, existing Product files or canonical component ownership, stop the Product effect and transfer findings to competent Control for separate selection/authorization.
- No MCP deployment, GitHub Issues two-way sync, new orchestration layer, calendar/scheduler, adoption or actual module deletion is implicit in this charter.

## Immediate next action
Prepare and execute Pilot 003 as a **new isolated bounded mechanical experiment** after pinning runner, manifest, source identities and expected receipts through normal repository reasoning and Git Transport. Do not restart pilots 001/002. Independently research feature breadth and maintain a capability/ownership assessment. Neither activity blocks independent ongoing Product work.
