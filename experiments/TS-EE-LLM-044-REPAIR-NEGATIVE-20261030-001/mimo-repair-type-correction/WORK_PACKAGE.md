# LLM 044 — MiMo corrective attempt (independent, experimental)

Original 043 attempt candidate: `ae0b3e03ad0eca1180ddf6802039b9052507c084`, exact source blob `bbd38f2b4f1b6b2d931f60efc3eba5d8b115033a`.
Owner and sole writable file: `src/select-latest.mjs`. Only permitted reads: this WORK_PACKAGE.md, the source and `tests/select-latest.test.mjs`.

**Required repair:** The original repair uses generic Error for rejected input, but the frozen contract requires TypeError or RangeError. Make the smallest repair; preserve highest sequence, first tie, UNKNOWN, and validation of all records. Do not change other files.

The original candidate and its 043 FAIL result remain immutable. No Product authority, no git publication, no tests executed by model, no tools beyond allowed. Tests and oracle will run independently after model exit.
