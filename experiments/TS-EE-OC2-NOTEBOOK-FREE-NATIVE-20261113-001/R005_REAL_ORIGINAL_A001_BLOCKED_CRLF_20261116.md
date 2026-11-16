# TS EE — R005 checker on historical A001 ORIGINAL: blocked CRLF, not rerun

**Date:** 2026-11-16 (Argentina local).  
**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.  
**ValidationAttempt:** `TS-EE-R005-REAL-ORIGINAL-VALIDATION-A001`; terminal `BLOCKED_PRECONDITION`; NEVER replay it.  
**Historical model ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001`; terminal `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`, no new model call.  
**Authority:** TS Developer Lab experimental only. Product authority/effect NONE. No canonical reviewer selection or Actions fallback.

## Exact original and private staging

- Historical notebook `DESKTOP-DJLBEQH` and original path `C:\Users\Mauri\orca\workspaces\ts-ee-llm040-source-20261030-001\ts-ee-oc2-notebook-free-native-20261113-001\results\TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001\ORIGINAL.jsonl`.
- Original native file measured **399,890 bytes**, SHA-256 `EA873A99533684F3EE2AB9D7F39FB634031969C689BFF7A95919F5BA53085AE9` and LastWriteTimeUTC `2026-11-14T02:56:51.3675409Z`, matching historical custody. No original bytes modified or exposed.
- Bound Orca TS experiment terminal `term_481dfbce-9351-4968-a32d-828f1d58a53a` in isolated R005 worktree `ts-ee-r005-posix-tests-20261116-001`, no OpenCode agent launched.
- Create-only private WSL stage `/tmp/ts-ee-r005-a001-private-20261116-001` with owner UID `1000`, mode `0700`; its `results/` and `receipts/` directories were created under it. Staged exact copy `results/ORIGINAL.jsonl` mode `0600`, 399,890 bytes, SHA-256 `ea873a99533684f3ee2ab9d7f39fb634031969c689bff7a95919f5ba53085ae9`, verified natively before running R005.
- R005 source immutable at `mauedgar/ts-execution-lab@74e98c436b62e199b5f109bad0eff947c7134a61:tools/ts_ee_orca_jsonl_receipt_v5.py`, blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`; isolated POSIX tests `55/55 PASS` earlier at `mauedgar/ts-execution-lab@ed52aa22e414c77eaad1c709191c8e1404b3e935:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R005_POSIX_TEST_A001_EXECUTION_RECEIPT_20261116.md`.

## The one actual validation effect

Orca native terminal accepted one bounded WSL invocation of the pre-existing R005 Python checker, native send request `bc495cd3-6cf7-4489-9859-f01e91bd6b0d`, terminal incarnation `4b9735b6-0890-4f1b-8054-a4f63d25f4bc`. This was **not** a new OpenCode2 inference or rerun of the historic A001.

- Inputs: original raw SHA above; `--root /tmp/ts-ee-r005-a001-private-20261116-001`, `--original results/ORIGINAL.jsonl`, `--receipt receipts/R005_A001_VALIDATION.json`, `--attempt TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001`, `--session ses_e280576f5ffeFHjktQ8Q7GveAg`, `--model opencode/deepseek-v4.1-flash-free`, `--provider-exit-claim 0`.
- Provider-native result: `{"model_calls_started":0,"reason_code":"ORIGINAL_NOT_LF_TERMINATED","status":"BLOCKED_PRECONDITION"}`. This is an input-format admission failure, **not** evidence of corrupted source or failed historical model effect.
- Independent native file-tail read using fixed-position `od` returned `7d 7d 0d 0a`; the original bytes end with **CRLF**, whereas v5 explicitly rejects `raw.endswith(b"\\r\\n")`. The historical original remains byte-for-byte unmodified.
- The private `receipts/` directory was observed with `ls -la` containing only `.` and `..` (mode 0700, owner tsops); no R005 receipt was created. Effect `NONE` for v5 publish, not `UNKNOWN`. The staging copy is retained privately for bounded analysis, not uploaded to public GitHub.

## Disposition / next isolated dependency

- The 55/55 synthetic R005 source test result and independent `RECOMMEND_SOURCE_ONLY / 0F / 5A` remain historically valid **for the v5 contract**, but real native JSONL compatibility is **BLOCKED_INPUT_FORMAT**. Do not reinterpret R005's source PASS as runtime PASS.
- Source next step **proposal, not yet acceptance**: prepare additive R006 that recognizes uniformly LF-terminated or uniformly CRLF-terminated JSONL, rejects mixed line endings and missing newline, keeps the SHA-256 and content of the ORIGINAL unchanged, and exposes an explicit `source_line_ending` in the sanitized receipt. Validate R006 via real negative tests and a fresh source-only IR before a **new** private historical validation with distinct validation identity.
- Do not rerun R005 validation A001; no change to historical OpenCode2 A001; no raw original in GitHub or Library, no Product modification, no default reviewer.
- `MODEL_CALLS=0`, `ACTIONS_RUNS=0`, `PRODUCT_EFFECT=NONE`.

**Terminal state:** `R005_REAL_ORIGINAL_A001_BLOCKED_CRLF / R005_RECEIPT_EFFECT_NONE / R006_COMPATIBILITY_CANDIDATE_REQUIRED`.
