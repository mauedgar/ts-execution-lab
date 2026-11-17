# TS EE — Independent WEB_INLINE IR002 | R006 LF/CRLF source checker

**Review_ID:** `TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR002-20261117-001`.
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V6-CRLF-IR002-A001`, RESERVED / NOT_DISPATCHED.
**Reviewer:** WEB_INLINE, STRICT_READ_ONLY, FRESH SEPARATE CONTEXT, SOURCE_ONLY.
**Authority:** TS Developer Lab experimental. Product_authority=NONE, Product_effect=NONE. This reviewer binding is a one-time choice, not canonical.
**Original target:** `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR002-20261117-001/ORIGINAL.md`, for Control's create-only publication after independent Library upload/readback.

## Exact frozen Git inventory (verify native commits and trees independently)

Subject commit: `mauedgar/ts-execution-lab@8b4dbd49832367d8690fe3f79ba9c607856537ca`, **exactly 40 hexadecimal characters**. Expected subject tree `9494f7f7d78cd369280de247bfaa6e78408f1cb6`.
Source commit: `mauedgar/ts-execution-lab@dfdaae3a2f3d6adcd183514b2761e7d1c2d5ca2e`, **exactly 40 hexadecimal characters**. Expected source tree `fe307a78ff55ca4bffc482a1f5875d44a064400d`.

Direct reads:
1. `tools/ts_ee_orca_jsonl_receipt_v6.py`, expected blob `08fa4d3d5b829129adeaa39bf3182c8143507408`; complete source (~447 lines).
2. `test/ts_ee_orca_jsonl_receipt_v6_test.py`, expected blob `d4dd738cb5243cdf55c45a101a4fbbe683d59826`; complete 60 tests.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R006_REAL_ORIGINAL_VALIDATION_A001_20261116.md`, blob `0f53f5393b58f27cad3088b1d4a3fdeb11612362` at the subject commit, sanitized runtime evidence only.
4. Native deterministic WSL/POSIX 60/60-test output: `mauedgar/ts-execution-transport@4029bf20cc3b04ea337b1f97d14c704364f86c5e:results/TS-EE-R006-POSIX-TEST-A001/TERMINAL_OBSERVATION.txt`, blob `cc79d6cd36b9c4be67f78876ef2de5ad950a2d8c`.
5. Previous R005 independent source IR (0F/5A, source-only) `mauedgar/ts-execution-transport@2c7852dd458983300f769f89b4d68bc3fb9bab27:results/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001/ORIGINAL.md`, blob `ced0461d5ed581163120da419e6fea728af9f487`.
6. Prior R006 IR001 historical ORIGINAL, `mauedgar/ts-execution-transport@0ccc88a7076a2808750fd4217c6a7a123f8834cc:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116-001/ORIGINAL.md`, blob `5b225b450f82f71c8481a2a72d444ca3337f7bf2`, historical `BLOCKED_SOURCE / 1F / 5A`.
7. Control reconciliation of the prior finding at `mauedgar/ts-execution-lab@e8f2636587f0107e1079bed2d1a2266ba6e29230:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R006_IR001_IDENTITY_RECONCILIATION_20261117.md`, blob `86709b7fdd911625ce59906ce67ace6cc7a01989`.

## Why IR002 is a new review, not an IR001 retry

IR001 completed with a preserved ORIGINAL and reported a 42-character purported subject SHA, while its FROZEN_INPUT actually contained the valid 40-character subject SHA printed above. Control independently verified both exact commits and tree objects through GitHub's native Git commits endpoints. That evidence inconsistency means IR001 cannot certify a source verdict; it remains immutable. IR002 has a **new Review_ID, ExecutionAttempt, request, ORIGINAL destination and fresh independent reviewer context**. It is not a retry under the IR001 identity.

**Mandatory:** Before judging source, count each frozen SHA's characters, resolve the exact 40-character commits through native GitHub, check subject/source trees and file Git blobs. Do not append, truncate, infer or substitute a ref. If the actual input is invalid, cite the exact contents and stop; if it is valid, do not reproduce the prior transcription error. Independently evaluate Control's reconciliation, rather than adopting it as authority.

## Independent DoD (source only)

- Audit uniform LF and CRLF interpretation, rejection of mixed/CR-only/unclosed lines, parser limits and raw SHA preservation. Inspect all 60 tests for real oracles, false positives, missing cases and direct import behavior. Verify no source bytes are normalized before digest.
- Audit POSIX dir_fd/O_NOFOLLOW ancestry, owner/mode and sticky-bit semantics, create-only hardlink publication, pre/post link UNKNOWN handling, path privacy and claimed vs independently verified receipt fields. Distinguish theoretical out-of-model same-UID/privileged attacks from in-scope other UID.
- Prior IR001 advisories A01–A05: provenance, test-oracle weaknesses, hostile-UID race evidence, metadata confidentiality, downstream schema/runtime portability. Reconcile each as OPEN/PARTIAL/RESOLVED_IN_SOURCE/OUT_OF_SCOPE, not silently cleared.
- Control's exact-Python tests returned 60/60 PASS and a separate native private structure-check of the historical 399,890-byte A001 original resulted in a private 1,138-byte receipt; neither original nor private receipt is available directly to reviewer. Report `tests_not_executed_by_IR=true`, `RUNTIME_EVIDENCE=PARTIAL_NOT_VERIFIED` or `BLOCKED_EVIDENCE`; do not claim independent invoice/provider auth or runtime qualification.
- Historical OpenCode2 semantic A001 is terminal nonconformant. Full Commander→Orca bridge `NO_RECOMMEND / 4F / 5A` remains separate; source approval cannot close it. No Product authority/effect, OpenCode2 or Actions launches, commits or PRs, any retry of model A001, or reviewer default change.
- This is an independent assessment: don't treat the previous review, its advisories, or Control's analysis as binding. Return `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, Fxx/Axx with actual path:line and mechanism, a candid DoD, limits, and next competent gate.

## Original and custody

Produce exactly one `IR002_ORIGINAL` with all identities and evidence, verdict, findings/advisories, independent source-specific verdict separate from bridge runtime, no modifications. The actual scheduled task MUST inline the full exact `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` contract with Library upload/readback and byte count/SHA-256, fail closed on UNKNOWN or partial upload. Reviewer must NOT publish to GitHub; Control will reconcile and publish a verified ORIGINAL later.

**State:** FROZEN / NOT_DISPATCHED / EXPECTED_ORIGINAL_ABSENT.
