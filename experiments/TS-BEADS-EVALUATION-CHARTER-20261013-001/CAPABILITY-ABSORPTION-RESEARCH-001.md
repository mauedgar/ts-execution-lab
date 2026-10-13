# TS — Beads adoption research | Initial capability and absorption map
Date: 2026-10-13
Classification: RESEARCH_FINDING / NONE_PRODUCT
Cutoff: Beads v1.3.1 docs; Tecnotron SOT observed on 2026-10-13 without Product write
Evidence boundaries: software documentation ≠ local qualification; synthetic pilot PASS ≠ Product semantics equivalence.

## Observed locally
- Pilot 001: persistent synthetic handoff recovered from fresh process after checkpoint; no automatic ChatGPT closure detection.
- Pilot 002: consumer-defined exact SOURCE_REF policy deduplicated sequential ingress and preserved different origins with identical titles; 12/12 checks recovered independently. Neither proves native dedup or racing writer guarantees.
- Pilot 003: protocol/runner/manifest created; **NOT EXECUTED**. v1.3.1 embedded mode is documented single-writer. The initial candidate runner is fail-closed pending an isolated qualified server-mode binding.

## Capability comparison (hypotheses until qualified)
| Beads native candidate | Tecnotron need | Potential adoption disposition | Limits / proof still required |
|---|---|---|---|
| Typed dependency graph; `blocks`, `related`, `discovered-from` | Cross-module obligation attribution and dependency recovery | REPLACE_CANDIDATE for custom non-authoritative obligation indexing | A graph relationship is not Product acceptance, selection, or authorized phase transition. Verify typed dependency behavior in v1.3.1 local pilot. |
| `bd ready` and atomic `bd update --claim` | Discover actionable pending work without losing a prior responsibility | REPLACE_CANDIDATE for a separate ready-inbox/claim queue | Readiness is not proof of Product authorization; multi-agent claiming on qualified server needed. |
| Durable issue records and `bd show` | Restart same responsibility and recover discovered obligations | NARROW custom operational notes/handoff index | Explicit exact git/receipt refs, uncertainty, last terminal result and authoritative checkpoint still must be preserved. |
| Embedded Dolt local mode | Low-footprint single-writer agent workflow | REUSE for controlled sequential local scenarios | Unsupported concurrent writes; cannot extrapolate to parallel agents. |
| Server-mode Dolt concurrent writers | Parallel pipelines registering work | INVESTIGATE; not yet selected | Separate service dependency, binding, persistence/security/backup and contention qualification; exact v1.3.1 behavior. |
| Dolt history, backup and remote synchronization | Recoverability and multi-host transport | INVESTIGATE if existing Git Transport becomes unnecessary for operational state | Git Transport receipts, Git subject identity and Product SOT remain distinct; JSONL export not full backup. |
| Hash IDs and cross-repo references | Separate tasks across independent modules | REUSE POSSIBLE | Hash uniqueness does not equal semantic source-ref dedup. Need source-key uniqueness and cross-module retrieval test. |
| Messages, threading, comments, memory/compaction | Agent coordination and reduced context overhead | EXPLORE_UNEXPECTED_VALUE | Evaluate exact semantics and version, retention/audit constraints, and whether this saves code rather than adding another store. |
| GitHub Issues/Projects interoperability | Current human and Product planning | CONSIDER ONLY AFTER COVERAGE TEST | Do not assume synchronization of Projects fields or authority. Two mutable sources of same obligation are not acceptable without owner/reconciliation rules. |
| Native Product effect journal / `NONE-CONFIRMED-UNKNOWN` | Retry safety and exact effect reconciliation | KEEP TECNOTRON ownership | No verified equivalence. State Kernel final disposition remains UNDECIDED and physical migration is not authorized. |

## Priority research order
1. Avoid an accidental unsafe concurrent embedded writer test. Determine and qualify supported multi-writer Dolt server binding **before** releasing Pilot 003.
2. Independently model the representative **interrupted synthetic pipeline** in a sequential isolated store using `discovered-from`, blocking/dependency links, a source checkpoint and readback. This is closer to the user pain than a storage-race microbenchmark and need not wait for a concurrent server.
3. Test server-mode parallel writes, independent ownership, atomic `--claim`, and source-ref dedup with explicit outcome receipts.
4. Use fresh Tecnotron consumer inventory at a future competent Product evaluation gate to estimate components truly removable versus integration and maintenance obligations; recommend retain/narrow/absorb only after evidence.

## Decision boundary
Evidence can recommend adoption, limited-scope adoption or no adoption. This research does **not** change Upper LC, TaskCycle Core, existing State Kernel or GitHub Projects, and does not grant Product Phase 2. Existing authorization permits only independent synthetic experiments and capability assessment.

## Sources
- Upstream Beads v1.3.1: https://github.com/gastownhall/beads/blob/v1.3.1/docs/reference/faq.md
- Upstream release: https://github.com/gastownhall/beads/releases/tag/v1.3.1
- Pilot 001: `mauedgar/ts-execution-lab@603fa23657a656852784ed034f188647dcb6c089:experiments/TS-BEADS-CONTINUITY-PILOT-20261013-001/PILOT-RESULT-20261013-001.md`
- Pilot 002: `mauedgar/ts-execution-lab@2c98305af8ae72b02f571d0ec13be62c8635df15:experiments/TS-BEADS-INBOX-DEDUP-PILOT-20261013-002/PILOT-RESULT-20261013-002.md`
- Tecnotron Product SOT: `mauedgar/tecnotron-ai:tools:docs/SOURCE_OF_TRUTH.md`, `docs/architecture-knowledge-ownership-baseline.md` and `docs/current-state.md`. Current branch must be reobserved before any Product change.
