# TS EE LLM 043 — Bounded native coding qualification: terminal experimental disposition

**Date:** 2026-10-30. **Execution owner:** TS_EXECUTION_ENGINEERING. **Authority:** EXPERIMENTAL_CONTROL_ONLY, Product NONE. **Disposition:** `COMPLETE_WITH_LIMITATIONS`; four original model attempts terminal, four source commits preserved, independent tests reconciled. No Product TaskCycle, Phase 2, Beads adoption or model-routing promotion.

## Source, DoD, and isolation

- Frozen starting Git subject: `mauedgar/ts-execution-lab@8d565454ada52e873ab57d19cd5c9e036ebf41ca`; source branch `experiment/llm-043-native-code-qual-20261030-001`.
- Experimental DoD and exact task-scoped model permissions: `experiments/TS-EE-LLM-043-NATIVE-CODING-20261030-001/DOD.md` and `EXECUTION_REQUEST.md`. The role-specific `opencode.json` and `llm-coder` agent restrict reads to three selected files and allow exactly one source-file `edit`; all other tools/actions deny by default. Effective agent permissions were observed in native OpenCode v2.1.0 through Orca on DESKTOP-DJLBEQH. Shell, external directory, Git push, test-file modification, web, delegation and Product were not authorized for agents.
- Four isolated Orca worktrees `llm043-d-i-001`, `llm043-m-i-001`, `llm043-d-r-001`, `llm043-m-r-001`, each anchored at the same source commit, each distinct write owner. No automatic agent launch; exactly one OpenCode invocation per ID with original JSONL captured outside worktree.
- Source baseline [GitHub Actions #41087579731](https://github.com/mauedgar/ts-execution-lab/actions/runs/41087579731) PASS_EXPECTED_RED: both role fixtures initially fail known tests, and permissions were inspected, native artifact `12992652080` SHA-256 ZIP `50795615b51474e8ba80fc609e86713f3debe55b8ad720043556b7952ba3ec15`.
- No silent switch to a paid model or v1. No previous 040/041/042 model attempt replay.

## Exact four original source candidates and postflight

| ExecutionAttempt | Role/model | Immutable candidate commit | Code blob | Original 9 tests | Independent 4 tests | Terminal scoped interpretation |
|---|---|---|---|---:|---:|---|
| `LLM043-D-I-001` | DeepSeek implementation | `0389345f3687ac3a6905d9584eee36c3feb7bd24` | `05de9fc91be009fb91d7234a0540e599f2fe901e` | 9/9 | **2/4** | `FAIL_SEMANTIC_CONTRACT` |
| `LLM043-M-I-001` | MiMo implementation | `1b25bff7ecd211691b2d634d17d6d3c463ded4b2` | `9b2cc6c85fe2bfdb1552f5d2c03eef3f711ef219` | 9/9 | **4/4** | `PASS_BOUNDED_FUNCTIONAL_AND_ORACLE` |
| `LLM043-D-R-001` | DeepSeek repair | `e8242f27eaa680d0fd265ab9d296a1e35a16eb1b` | `2ebdf9412f1f5a387198ad1627854274fc5e7367` | 9/9 | **4/4** | `PASS_BOUNDED_FUNCTIONAL_AND_ORACLE` |
| `LLM043-M-R-001` | MiMo repair | `ae0b3e03ad0eca1180ddf6802039b9052507c084` | `bbd38f2b4f1b6b2d931f60efc3eba5d8b115033a` | 9/9 | **1/4** | `FAIL_SEMANTIC_CONTRACT` |

Before commit, each `git status --porcelain` showed exactly its one role-owned source file; after a single-file `git commit --only` and separate experimental branch push, all four worktrees were clean. No merge or canonization.

**Observed semantic findings:**
- `D-I`: `COST_SCALE = 1e10` / rounding to ten decimals instead of six. Violates the frozen `aggregateResults` contract; two independent oracle cases fail.
- `M-R`: generic `Error` on invalid records instead of `TypeError`/`RangeError`, violating the frozen `selectLatest` contract; three independent oracle cases fail.
- `M-I` and `D-R` passed all current original and independent tests, with no defect observed in targeted GitHub inline code review. This is not a universal correctness proof or independent Product Review.

## Independent validator and native evidence

- Separate validator branch `experiment/llm-043-independent-oracle-20261030-001@1f25e7b02b6e7f01865f02ea1cd41dbe4a2f0f46`; four candidate commit hashes and four code blob hashes frozen inside its Action.
- [GitHub Actions #41090151478](https://github.com/mauedgar/ts-execution-lab/actions/runs/41090151478), job `124181615519`, original run attempt 1, completed/success **for execution of the four test comparisons**; oracle failures recorded rather than discarded. **36/36 original tests passed; 11/16 oracle tests passed, 5 failed.**
- Independent logs artifact `12992952790`, ZIP SHA-256 `4cb7346351837bfc9723431c3487fc9f241acdbb38cce000f9d9a02eb0e28e63`. Results JSONL artifact `12993267159`, ZIP SHA-256 `3f779b0afc3bcd4a11da2200a273730469446c43959b2442977377cf21bbbd95`. Original result JSONL SHA-256 `05524e2c1c9ee6aae30b4987583142af81053b313b76438fe42af6c9e3a89cbf`. GitHub original artifact retention ~30 days; use exact run and artifact IDs to recover before expiration.
- Independent oracle is retrospective: authored after two initial candidates were inspected, derived from previously frozen contracts, and unavailable to the model's read allowlists. **Do not claim prospective blind benchmarking.**
- All four native OpenCode result JSONL files remain **host-local** at `C:/TS/station/<ExecutionAttempt>.jsonl`. Observed SHA-256 hashes, in attempt order:
  - D-I `EEF1B5152D10F5E0C55F89810FA64931EC208F23DFD8E85C2EDE9A726726976E`.
  - M-I `C8E98302DD3E316E3E572D1F53742BC13EA2C401E013A441EB8B2F05E511875E`.
  - D-R `08163D673B0E3A3C02771922997D468AB125084484CA25BCD781F5836ABD259C`.
  - M-R `B32A4C1667332B364596081608A66D413324DE637796B5B0262F06C2919FDF51`.
- The private GitHub Transport branch creation for 040 evidence was previously blocked by tool safety and not circumvented. **No raw 043 JSONL byte-for-byte cloud archival has been verified.** GitHub evidence is original source commits, test outputs, and result records, not a replacement for model event logs.

## Qualified scope and residual limitations

**Empirically qualified:** two free native OpenCode v2 model IDs can produce bounded source-file changes in distinct Orca worktrees with role-local permissions and tests; Beads was previously proven for synthetic coordination (040/041), not used as an authoritative scheduler for these four model attempts. Two model candidates satisfy both available code test suites.

**Not qualified:** general model skill rankings, benchmark sample repeatability, statistically robust costs/latency, raw event-log cloud transport, universal permission/write confinement, unauthorized write negative-control, full native event/cost accounting, independent Product Review, actual parallel task consumption by canonical Tecnotron, or any Product acceptance. The model requests ran in two overlapping cohorts, but no measured sustained throughput/performance inference follows.

**DoD settlement:** aggregate `COMPLETE_WITH_LIMITATIONS`; P01/P03/P04 and source/functional postflight evidenced, E04/A01-A03 independently validated. E02/E06/E07 raw event durability remains limited to host-original logs/hashes; cross-provider comparison and Product adoption are deferred. Failed semantic candidates remain FAILED as original results; no hidden retry or retroactive repair.

**Next experimental priority:** a distinct, frozen repair-cycle experiment with unique attempts addressing D-I six-decimal rounding and M-R error type, and a permission negative-control. Or qualify an approved raw-event carrier first if durable provider traces are needed before new executions. Neither option creates Product authority. Product HEAD last observed `mauedgar/tecnotron-ai:tools@6db3f02549a6ee0fce41e85b26f4c0898490d1ea`, no change by this line.
