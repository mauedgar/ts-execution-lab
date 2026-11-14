# TS EE — WEB_INLINE IR001 | Deterministic JSONL Receipt V2 Source Only

**Review_ID:** `TS-EE-ORCA-JSONL-RECEIPT-V2-WEBINLINE-IR001-20261114-001`  
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V2-IR001-A001` — RESERVED, NOT_DISPATCHED  
**Binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH_SEPARATE_CONTEXT / SOURCE_ONLY`  
**Authority:** TS Developer Lab experimental, `Product_authority=NONE`, `Product_effect=NONE`.  
**Subject:** `mauedgar/ts-execution-lab@deaf909cf7632b3e7f88c7a9c7a7f2d04c56c14b`; tree `39c624a95ff3a299db3774a1069894d2fab52f8d`.  
**Original destination:** `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-RECEIPT-V2-WEBINLINE-IR001-20261114-001/ORIGINAL.md` (Control create-only, NOT reviewer).

## Frozen direct-source reads

1. `tools/ts_ee_orca_jsonl_receipt_v2.py` Git blob `982745211cf2ed5e8b805a4a527bdfab691b6749`.
2. `test/ts_ee_orca_jsonl_receipt_v2_test.py` Git blob `a2286a636d89587e4f15766438c7b1646b184618`.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R002_SOURCE_REPAIR_EVIDENCE_20261114.md` Git blob `f35988f6f7542df818893271942bd54a086c701b`.
4. Prior independent Orca bridge IR001 ORIGINAL (not the local OpenCode JSONL): `mauedgar/ts-execution-transport@4ae785f79b5c2d295ee75683f6cfaf4bd4a7684f:results/TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001/ORIGINAL.md`, SHA256 `996afe049e456428aef6bb8cecc668220eda0d38a57634b749c04733234f997e`.
5. Optional reviewer binding decision: `mauedgar/ts-execution-lab@3f9db9086cc11e0ca01affff92738c89d28f4bf8:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OPTIONAL_PRELIMINARY_REVIEWER_CANDIDATE.md`, blob `c1df2afc606d406068b7ec5492fbaf741af94c04`.

## Mandatory independent checks

- Verify the exact subject tree/blobs from GitHub, and inspect ALL parser/test source directly. No relying solely on Control's narrative.
- Scope strictly to **deterministic JSONL parsing and create-only source receipt**. It does NOT close the original bridge IR F01/F03/F04 and does not implement provider billing verification, host fencing, model inference, runtime policy canaries, Product acceptance or a default reviewer.
- Source-level security: limit on file size/events, UTF-8 framing, duplicate JSON keys, path traversal and symlink escaping, race between reading/stat, content hash and session ID, strict terminal sequence, cost numeric validation including NaN/inf/huge, out-of-policy tool attempts, proper classification of provider-reported cost vs actual billing, creation/atomicity/collision of evidence receipt and cleanup semantics.
- Audit the 16 deterministic tests: correct expectations, meaningful negative cases, false positives/tautological tests, missing tests and scope of what PASS proves. Control executed the **exact Git blobs** in isolated Python 3.13.5 container with 16/16 PASS; this is not an independent runtime execution by the reviewer.
- A completed checker or original event stream MUST NOT be misrepresented as a valid semantic reviewer verdict, host grant, provider bill attestation or Independent Review.
- Determine whether 0F/0A is justified **only for SOURCE_CHECKER**. If an implementation flaw is blocking in this limited source scope, emit Fxx. Gaps requiring a later runner integration may be tracked as advisories or explicit future runtime gates, not silently adopted.
- State whether parser source could reveal sensitive original payload; it must never copy raw JSONL into public GitHub. Identify any unsafe output/data exposure.
- Keep WEB_INLINE, OpenCode2 and other reviewer surfaces as explicit alternatives selected per competent responsibility. No canonical reviewer route from this IR.
- Do not execute Python, GitHub Actions, OpenCode2, Commander/Orca, upload Product artifacts, alter repositories or modify the frozen subject. A separate reviewer can reason through tests but must state `tests_not_executed_by_IR`.

## Required one-original result

Return `IR001_ORIGINAL` with Review_ID, ExecutionAttempt, verified commit/tree/blobs, coverage, reviewer independence, verdict `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, all findings Fxx/advisories Axx with exact file:line, risk, evidence and bounded repair, source-only DoD, unverified runtime gates, no Product actions, no changes or execution.

**Custody:** If scheduled, the actual scheduled prompt MUST embed complete exact `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` original upload/readback and fail-closed contract, not just reference it. Publishing the Original to GitHub is Control's responsibility after Library verification.

**Status:** `FROZEN_REQUEST_NOT_DISPATCHED / ORIGINAL_TARGET_ABSENT`. No new OpenCode2 semantic attempt is authorized by this source review.
