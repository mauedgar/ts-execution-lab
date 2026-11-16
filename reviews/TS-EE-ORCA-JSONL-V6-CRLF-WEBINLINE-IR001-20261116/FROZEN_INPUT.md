# TS EE — WEB_INLINE Independent Review IR001 | JSONL R006 LF/CRLF (SOURCE_ONLY)

**Review_ID:** `TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116-001`  
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V6-CRLF-IR001-A001` — RESERVED, NOT_DISPATCHED.  
**Reviewer binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH INDEPENDENT CONTEXT / SOURCE_ONLY`, selected explicitly for this experimental helper.  
**Authority:** TS Developer Lab, `authority=NONE`, `Product_authority=NONE`, `Product_effect=NONE`. No canonical reviewer route, Product change, OpenCode2 execution or Actions fallback.  
**Exact subject:** `mauedgar/ts-execution-lab@8b4dbd49832367d8690fe3f79ba9c607856537ca`, Git tree `9494f7f7d78cd369280de247bfaa6e78408f1cb6`.  
**Frozen source code commit:** `dfdaae3a2f3d6adcd183514b2761e7d1c2d5ca2e`, tree `fe307a78ff55ca4bffc482a1f5875d44a064400d`.  
**Expected independent ORIGINAL:** Library-upload, with Control subsequent create-only GitHub Transport publication at `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116-001/ORIGINAL.md`.

## Mandatory independent source reads: exact Git refs, do not trust Control interpretation

1. `tools/ts_ee_orca_jsonl_receipt_v6.py`, blob `08fa4d3d5b829129adeaa39bf3182c8143507408`, read at frozen source or subject commit.
2. `test/ts_ee_orca_jsonl_receipt_v6_test.py`, blob `d4dd738cb5243cdf55c45a101a4fbbe683d59826`, **60** named cases.
3. Sanitized one-shot real-original validation evidence `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R006_REAL_ORIGINAL_VALIDATION_A001_20261116.md`, blob `0f53f5393b58f27cad3088b1d4a3fdeb11612362` at subject commit.
4. Original deterministic 60-test **terminal output**, not the private model ORIGINAL: `mauedgar/ts-execution-transport@4029bf20cc3b04ea337b1f97d14c704364f86c5e:results/TS-EE-R006-POSIX-TEST-A001/TERMINAL_OBSERVATION.txt`, blob `cc79d6cd36b9c4be67f78876ef2de5ad950a2d8c`.
5. Historical v5 source at `mauedgar/ts-execution-lab@74e98c436b62e199b5f109bad0eff947c7134a61:tools/ts_ee_orca_jsonl_receipt_v5.py` (blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`) and historical v5 independent source IR `RECOMMEND_SOURCE_ONLY / 0F / 5A` ORIGINAL at `mauedgar/ts-execution-transport@2c7852dd458983300f769f89b4d68bc3fb9bab27:results/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001/ORIGINAL.md` (blob `ced0461d5ed581163120da419e6fea728af9f487`).
6. Historical R005 real-source CRLF fail-closed checkpoint `mauedgar/ts-execution-lab@ae4f7bda3fcd3a24df2cdf4273c88af730c1db49:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R005_REAL_ORIGINAL_A001_BLOCKED_CRLF_20261116.md`, blob `26c4fc1ee4e2cf8f1bc80cbcecb996a89bb097aa`.

## Independent SOURCE_ONLY DoD

- Verify subject commit, source commit, trees and blob hashes through GitHub directly. Read the full checker and all tests, not only the sanitized Control account.
- Evaluate R006's exact delta to v5: LF-only restriction replaced with **uniform LF/CRLF acceptance**, mixed-endings and missing-final-newline rejected, no byte-level mutation to original, in-memory trimming only, hash over the untouched raw bytes. Is the classification of per-line CR and malformed trailing data robust? Check malformed JSON, wrong digest, line limits, nesting, duplicate keys, UTF-8, unsupported event types and terminal sequence; test negative cases for both newline families. Assess whether actual Windows CRLF output is handled without false PASS or silently normalizing original custody.
- Inspect R006 `schema` bump (prior v5 had stale v4 label); `source_line_ending` in sanitized receipt and terminal return. Audit security boundaries and regressions from earlier v5 source qualification: POSIX-only `dir_fd` and non-follow, ownership/0700 ancestry, symlinks, atomic create-only hard-link, pre- and post-link UNKNOWN preservation and receipt privacy. Do not infer indefinite path immutability under same-UID/privileged writers.
- Assess ALL 60 cases, particularly modified `test_22_crlf` and added `test_56`–`test_60`. Look for tautological or ineffective cases, untested mixed terminators, R005 regressions, platform assumptions and malformed test harness. A separate Control mechanical WSL/Python 3.12.3 execution of exact frozen Git blobs reported **60/60 PASS, 0 FAIL, 0 ERROR** and 0.633s. The independent IR **MUST NOT RUN CODE** and must explicitly mark `tests_not_executed_by_IR=true`.
- Distinguish source integrity from runtime provenance. Control observed one R006 checker run (not a model run) against a private staged copy of the historical A001 ORIGINAL, original raw `399,890` bytes SHA-256 `ea873a99533684f3ee2ab9d7f39fb634031969c689bff7a95919f5ba53085ae9`, CRLF, 63 events, 14 start/finish, 34 read-only tool calls, two tool errors and provider-reported cost zero. R006 private create-only receipt SHA-256 `0cdc1354404739b193536b87ac3ca569a78e1a139994b2600a2452f582153c5d`, 1,138 bytes, native mode 0600. **The full private 399,890-byte ORIGINAL and private 1,138-byte receipt are NOT given to you.** You cannot claim direct independent inspection of those bytes, provider authentication, real invoice or model compliance. Classify `RUNTIME_EVIDENCE=PARTIAL_NOT_VERIFIED | BLOCKED_EVIDENCE` as appropriate. This source-only review may recommend source independently while explicitly leaving full-runtime qualification blocked.
- Reconcile v5 prior advisories A01–A05 with honest dispositions: what source differences actually resolve vs what remains out of scope or operational. A provider-reported `cost=0`, `model_id` claim, event count and tool-name allowlist are not authoritative invoices, signed provenance or independent semantic acceptance. Historical OpenCode2 reviewer A001 remains `FAILED_SEMANTIC_CONFORMANCE / NO_RECOMMEND`; full Commander→Orca semantic bridge remains `NO_RECOMMEND / 4F / 5A`.
- Reviewer modality is a **competent choice for each responsibility**, not an adopted default: WEB_INLINE, OPENCODE_LOCAL or another qualified harness; no Product SOT modification or reviewer-policy adoption by this source review.
- Strict read-only. Do NOT execute Python, Orca, Commander, OpenCode2, GitHub Actions, hidden tools, Product operations, commits, PR, billing, reruns or any second IR under this identity. Do not expand scope from source checker to Product or runtime bridge.

## One independent ORIGINAL and custody

Produce one full `IR001_ORIGINAL` with Review_ID, ExecutionAttempt, checked commit/tree/blobs, independent coverage/limitations, verdict `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, source findings Fxx, advisories Axx with exact file:line and bounded repair, test evidence disposition, raw-event provenance limits, `RUNTIME_EVIDENCE` classification, status for remaining 5 advisories, reviewer-selection boundary, and `Product_effect=NONE`. Do not claim `0F/0A` unless independently justified for the **source-only** subject.

If scheduled, the actual task prompt MUST inline the complete published `docs/execution-engineering/TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` upload/readback/sha256/length/fail-closed contract. The frozen input alone does not guarantee a Library upload. GitHub Transport ORIGINAL publication is solely by Control after verifying Library bytes.

**State:** `FROZEN_REQUEST / NOT_DISPATCHED / EXPECTED_ORIGINAL_ABSENT`.
