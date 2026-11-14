# TS EE — WEB_INLINE Independent SOURCE_ONLY Review IR001 | JSONL v3 POSIX

**Review_ID:** `TS-EE-ORCA-JSONL-V3-POSIX-WEBINLINE-IR001-20261114-001`  
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V3-IR001-A001` — RESERVED, NOT_DISPATCHED  
**Reviewer binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH INDEPENDENT CONTEXT / SOURCE_ONLY`  
**Authority:** TS Developer Lab experimental only, `Product_authority=NONE`, `Product_effect=NONE`.  
**Subject commit:** `mauedgar/ts-execution-lab@8bec3aa449f82b05326177ef847b73b39cd9bde2`  
**Subject tree (native Git endpoint verified by Control):** `dde0ef9560705dfca8b299ae9a2255721101a609`  
**Branch:** `experiment/ts-ee-oc2-notebook-free-native-20261113-001`, not main.  
**Expected independent ORIGINAL custody:** Library personal, with byte-length/hash/upload/readback verifiable; subsequent GitHub Transport publication by Control alone to `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-V3-POSIX-WEBINLINE-IR001-20261114-001/ORIGINAL.md`.

## Exact frozen source inventory

1. `tools/ts_ee_orca_jsonl_receipt_v3.py` — Git blob `55aa5026584a4bed5f01c6ea616d8c09171cfd6a`, 12,001 UTF-8 bytes.
2. `test/ts_ee_orca_jsonl_receipt_v3_test.py` — Git blob `7db16511e8b21861996071bd76d5541b9478e90a`, 8,361 UTF-8 bytes.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R003_SOURCE_REPAIR_DISPOSITION_20261114.md` — Git blob `4ab725e8fad4b630a2235d2732ff1636fac6271c`.
4. Independent previous source-only IR ORIGINAL `mauedgar/ts-execution-transport@58a1cd48e1a70ee292925ca776968e6cfc745742:results/TS-EE-ORCA-JSONL-RECEIPT-V2-WEBINLINE-IR001-20261114-001/ORIGINAL.md` — blob `6031f6a5954a2437ecd4ccb19eebc77a81917ba3`, 9,909 bytes, SHA-256 `b0ec8e773b546bcb8682d92126f31f3acda86c13a6af9547223a466445a4ff7d`, prior `NO_RECOMMEND / 3F / 5A`.

The previous v2 IR had a request commit/tree mismatch: `deaf909cf7632b3e7f88c7a9c7a7f2d04c56c14b` tree `39c624a95ff3a299db3774a1069894d2fab52f8d`, while its request publication commit `d90414af016101125221d741971370253c932c36` has tree `9aa2821804e265d13e32a19b6d1b1ca9bb93fd9a`. Distinguish these; use the **exact v3 subject** listed above, do not repeat a tree mismatch.

## SOURCE_ONLY DoD: independent scrutiny

- Verify commit, tree, ALL source blobs directly through GitHub. Read all Python code and tests, not just the disposition.
- Evaluate prior F01 (terminal grammar), F02 (file identity/TOCTOU/symlink) and F03 (atomic create-only, interrupted writes) individually. Classify `RESOLVED_BY_SOURCE`, `PARTIALLY_RESOLVED`, `STILL_BLOCKING_SOURCE`, or `RUNTIME_OUT_OF_SCOPE`. Preserve findings/advisories separately.
- Assess the new parser's explicitly constrained, versioned event grammar. Does `part.type` match actual defined kinds in its own source contract? Is sequence coherent across multiple steps, text/tool events, unknown/error events, nonstandard JSON numbers, multiple sessions and terminal closure? Are provider-signature and semantic verdict **correctly NOT claimed**?
- Assess POSIX-only `dir_fd` traversal, `O_NOFOLLOW`, source regular file and fstat metadata, digest, root boundary, TOCTOU races including directory symlink swaps, platform fail-closed on Windows, open file races and potential external hardlink aliasing.
- Assess the publish path: write+fsync of unique staged file, POSIX hard link/create-only final, directory fsync, exact readback, stage cleanup, collision and power-loss semantics, failures **before** and **after** link, preserved `UNKNOWN_PUBLISH_POSTCONDITION`, no retry/overwrites. Evaluate whether atomic publication is factually supported. Do not claim Windows portable.
- Inspect all 34 tests for false positives, meaningful negative cases and omissions: injected pre-link failure, post-link fsync failure preserving final, symlink and traversal cases, grammar, nonstandard JSON, cost, model claims, collisions and source mutation. Control ran the exact Git blobs with local isolated Python 3.13.5: `py_compile` PASS and 34/34 `unittest` PASS; the independent IR must report `tests_not_executed_by_IR=true` unless it actually runs them, which this review MUST NOT do.
- Review sanitized receipt shape: no raw JSONL or prompt copied into public result; model, cost, provider terminal, native semantic outcome clearly `unverified`; hidden sensitive metadata in receipt should be explicitly considered.
- Scope is **one source-only helper**. Even 0F/0A does not qualify live OpenCode reviewer, billing, actual tool-denial, Windows support, automatic fallback, full runtime bridge, developer adoption or Product effects. The old bridge IR `NO_RECOMMEND/4F/5A` and semantic A001 `NO_RECOMMEND` remain terminal and independent.
- Reviewer binding remains a choice: WEB_INLINE, OpenCode2, or another competent medium, never hardcoded as canonical. No Product PR, merge, actions execution, code alteration, runtime effect, or model calls.

## Required one-original output

Return `IR001_ORIGINAL` with Review_ID, ExecutionAttempt, frozen commit/tree/blobs verified, actual coverage, independent fresh-context observations, `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, all blocking Fxx and advisory Axx with exact file:line, severity, reproducibility and bounded repair; source-only regression disposition against prior 3F/5A; unverified runtime dependencies, Product_effect NONE, tests_not_executed_by_IR true. If source admits vulnerabilities, provide no automatic follow-up run/repair: Control owns the disposition.

**Custody:** When run by a scheduled WEB_INLINE task, the *actual scheduled prompt* MUST inline the full `docs/execution-engineering/TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` upload, readback, SHA, byte-length and fail-closed requirements, not merely link here. GitHub original publication requires a separate Control operation after verification.

**State:** `FROZEN_REQUEST / NOT_DISPATCHED / ORIGINAL_ABSENT`.
