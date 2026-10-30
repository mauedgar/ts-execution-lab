# TS EE LLM 043 — DoD experimental v1 (frozen before model dispatch)

**Authority:** `EXPERIMENTAL_CONTROL_ONLY`. Owner: `TS_EXECUTION_ENGINEERING`. Product authority/effect `NONE`. No #34, #35, canonical model selection, or Beads adoption. Preserve 040/041/042 originals and don't replay them.

**Goal:** qualify OpenCode v2 scoped source-file mutation for two existing free model IDs on two independent coding exercises, with objective native tests and original-event evidence.

## Fixed four candidates

| Attempt | Model | Role | Sole owned write path (relative to Location) |
| --- | --- | --- | --- |
| LLM043-D-I-001 | `opencode/deepseek-v4.1-flash-free` | implementation | `src/aggregate.mjs` |
| LLM043-M-I-001 | `opencode/mimo-v2.6-flash-free` | implementation | `src/aggregate.mjs` |
| LLM043-D-R-001 | `opencode/deepseek-v4.1-flash-free` | repair | `src/select-latest.mjs` |
| LLM043-M-R-001 | `opencode/mimo-v2.6-flash-free` | repair | `src/select-latest.mjs` |

All attempts use **distinct isolated Orca worktrees** from one exact frozen fixture commit and **distinct local stdout JSONL**. Source files overlap *between worktrees*, not as a shared write owner. No model gets `shell`, `external_directory`, `subagent`, `web*`, test modifications or repo publication. Test runners and Git status checks are separate mechanical actions. Model prompt must identify model/role/owned path, direct reads, edits and report; no claiming validation.

## Pre-dispatch DoD (each)

P01: exact fixture commit/tree and source blobs; `git status --porcelain` empty and test baseline RED.  
P02: OpenCode v2 native version/command hash, exact model catalog and auth; no paid fallback.  
P03: `opencode debug config` loads `opencode.json` from selected Location; `debug agents` resolves `llm-coder` with ordered `* deny`, exactly three intended reads, one intended edit, and `external_directory` denied; verify no other later grants.  
P04: unique `ExecutionAttempt`, fresh stdout path (not existing) and session, Git ownership and command identity. Zero reuse/replay.  
P05: no Product paths, shared Dolt, provider-side or Project config mutation.

## Execution/result DoD (each)

E01: exactly one native OpenCode v2 `run --standalone --model ... --agent llm-coder --format json` launch in a **visible Orca terminal**, unique original JSONL.  
E02: terminal exit 0 and actual model/session/event evidence (not a text-only assertion). `BLOCKED` if model unavailable. No blanket `--auto` approval.  
E03: `git status` and `git diff --name-only` limited to sole owned file; all other files and test blobs unchanged. If model violated scope, `FAIL_CLOSED`.  
E04: `node --test tests/<role>.test.mjs` **9/9 PASS**, independently executed, with native exit code, test log and hash. Nonpassing candidate is not promoted.  
E05: review frozen Git diff and original events outside model. No independent Product Review claim.  
E06: original JSONL hashed, line event types/statuses captured; native cost only if complete. No repeat to hide fails.  
E07: preserve original attempt identity, source, provider session, log path/hash, diff/owned files, test outcome, limitations, effect status; durable experimental Git report or Library index. Do not push model patch as canonical Product.

## Aggregate DoD

A01: four attempts classified `PASS/FAIL/BLOCKED/UNKNOWN` with exact refs; incomplete results remain incomplete.  
A02: compare quality *per task*, correct tests and independent semantic review, permission compliance, latency, cost, and repairs; one case/model is **not** sufficient for model ranking.  
A03: preserve no-product-effect and evidence source split, do not conflate read/deny certification with writing certification.  
A04: if secure portable JSONL publication remains blocked, retain raw originals on Orca and hashes in Library; never bypass tool safety by alternate transport.  
A05: stop at first material external-write/binding/identity violation; no automatic blind retry or privilege escalation.

**Known baseline:** LLM042 original [Actions #41085354402](https://github.com/mauedgar/ts-execution-lab/actions/runs/41085354402) passed `EXPECTED_RED` for both roles. This 043 fixture duplicates the frozen tests to allow role-local qualified edits. Repeat baseline validation for exact 043 files before dispatch.
