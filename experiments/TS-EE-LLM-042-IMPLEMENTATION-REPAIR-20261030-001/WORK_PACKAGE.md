# TS EE LLM 042 — Two synthetic coding benchmarks

Authority: EXPERIMENTAL_CONTROL_ONLY. No Product/TaskCycle effect or Beads Product adoption. Do not re-run prior DeepSeek/MiMo 040 attempts.
Frozen source: this experiment branch/HEAD after all files and validation checks are published.

## Benchmark I — implementation
Owned implementation file only: `src/aggregate.mjs`. Export `aggregateResults(events)`.

- Input: array of ordinary event objects with `id` (nonempty string), `status` exactly PASS/FAIL/BLOCKED, `durationMs` finite nonnegative integer, and optional `costUsd` finite nonnegative number (default 0).
- Reject non-array and invalid events with `TypeError` or `RangeError`. Do not mutate inputs.
- Duplicate `id` is case sensitive; **first valid occurrence wins**. Validate **all** entries before aggregating, including duplicates.
- Return `{total,counts:{PASS,FAIL,BLOCKED},durationMs,totalCostUsd,ids}`. IDs sort ascending by UTF-16 code-unit order. Sum costs in floating-point, round final sum to six decimal places.
- Empty input yields zeroed structure; no disk, network, time, randomness, or dependencies.
- Before implementation the supplied file throws `NOT_IMPLEMENTED`; initial tests must be RED.

## Benchmark R — repair
Owned implementation file only: `src/select-latest.mjs`. Export `selectLatest(records)`.

- Input array of objects with `jobId` nonempty string, `sequence` nonnegative safe integer, `status` exactly PENDING/PASS/FAIL/UNKNOWN. Reject malformed records with TypeError/RangeError.
- Group by exact case-sensitive jobId; select greatest sequence. A tie on sequence preserves the **first** encountered record, regardless of later status. Sort returned array by jobId UTF-16 ascending.
- Return `[{jobId,sequence,status}]` without modifying inputs.
- Current supplied implementation incorrectly selects last appearance rather than maximum sequence and admits invalid records. Repair without broadening authority.

## Comparability and constraints

Each model receives a separate identical clean source Git tree per role, own worktree, exact model ID and exact permitted write path. Task instructions and max tokens/time must be frozen before dispatch; no auto-approved write outside allowlist; no paid model fallback. The source files for the two roles are disjoint and can be tested independently. Review the native event log, requested patch, tests, Git diff and cost. No tool use or model execution is implied by this document.

Deterministic validation:
- `node --test tests/aggregate.test.mjs`
- `node --test tests/select-latest.test.mjs`

Baseline DoD: tests RED on supplied stubs/bug, while scripts parse, and CI retains original output; no algorithmic PASS until model candidates exist and separately pass validation/review.

## Research limitations
One fixture is not representative of broad software engineering. The tests are visible; model performance and independent review are not qualified yet. Read-only E-002/E-003 does not grant write authority. Keep all effects within synthetic worktrees and experimental repository.
