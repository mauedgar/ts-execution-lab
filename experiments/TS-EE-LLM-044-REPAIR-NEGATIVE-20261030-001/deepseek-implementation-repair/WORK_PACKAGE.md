# LLM 044 — DeepSeek corrective attempt (independent, experimental)

Original 043 attempt candidate: `0389345f3687ac3a6905d9584eee36c3feb7bd24`, exact source blob `05de9fc91be009fb91d7234a0540e599f2fe901e`.
Owner and sole writable file: `src/aggregate.mjs`. Only permitted reads: this WORK_PACKAGE.md, the source and `tests/aggregate.test.mjs`.

**Required repair:** The original implementation rounds totalCostUsd with COST_SCALE=1e10, violating the frozen contract's final SIX decimal places. Make the smallest repair; retain every original semantic guarantee. A newly frozen oracle checks precision. Do not change other files.

The original candidate and its 043 FAIL result remain immutable. No Product authority, no git publication, no tests executed by model, no tools beyond allowed. Tests and oracle will run independently after model exit.
