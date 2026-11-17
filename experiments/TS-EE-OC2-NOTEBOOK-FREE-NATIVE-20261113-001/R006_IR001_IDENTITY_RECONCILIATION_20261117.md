# TS EE — R006 IR001 identity discrepancy and Control disposition (2026-11-17)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`. Experimental TS Developer Lab only, `Product_authority=NONE`, `Product_effect=NONE`.
**Frozen historical Review_ID:** `TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116-001`, `ExecutionAttempt=TS-EE-ORCA-JSONL-V6-CRLF-IR001-A001`.
**Native automation:** `Automation_c6a4a9afcf2481919b2ede351883ff2c`, run `a3f38e05-ae60-832b-a200-933b6d3462bb`, completed 2026-11-16T19:54:33.938698Z, without retry.
**Immutable IR verdict:** `BLOCKED_SOURCE / 1F / 5A`. Do not rewrite or retroactively change the reviewer original.
**Control disposition:** `F01_IDENTITY_ASSERTION_UNSUPPORTED_BY_FROZEN_INPUT / SOURCE_REVIEW_NOT_ACCEPTED / IR002_NEW_IDENTITY_REQUIRED`.

## Original custody

IR001 uploaded ORIGINAL to Library `libfile_64179c1a8390819198c527486674c099` with raw backing file `file_00000000a8b481f58554c2d2cf214390`. Control materialized exact `9320` UTF-8 bytes, SHA-256 `089779aeb41dbe6ba79cfba8672f2e8caca40e04e015bdeb97b8b97f70d78238`, Git blob `5b225b450f82f71c8481a2a72d444ca3337f7bf2`. Published create-only and verified matching bytes/blob at `mauedgar/ts-execution-transport@0ccc88a7076a2808750fd4217c6a7a123f8834cc:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116-001/ORIGINAL.md`. No duplicate publication.

## Direct independent Git identity checks by Control

- Frozen IR input (unchanged): `mauedgar/ts-execution-lab@396a24709471cbbb68a07786ebdd73c2d9354e87:reviews/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR001-20261116/FROZEN_INPUT.md` blob `acb9b802a9b77c52768ef26dd68cbb35a7f233e1`.
- Its **line 7** explicitly declares subject `8b4dbd49832367d8690fe3f79ba9c607856537ca` (**40** hex characters) and tree `9494f7f7d78cd369280de247bfaa6e78408f1cb6`.
- Native GitHub `GET /git/commits/8b4dbd49832367d8690fe3f79ba9c607856537ca` returned that exact commit and exact tree. **PASS**.
- Input line 8 source commit `dfdaae3a2f3d6adcd183514b2761e7d1c2d5ca2e` (40 hex) and tree `fe307a78ff55ca4bffc482a1f5875d44a064400d`, both verified via native GitHub commit. **PASS**.
- Request publication commit `396a24709471cbbb68a07786ebdd73c2d9354e87` has a distinct legitimate tree `77a22c5d80256d6df84010c75763635c34b0c61b`. Do not conflate request-publication tree with frozen *subject* tree.
- In its ORIGINAL, IR001 instead identifies a different 42-hex string `8b4dbd49832367d8690fe3f79ba9c607856537ca2e`, claims that this unresolvable string appears in the frozen input, and flags F01 on that basis. The frozen input does **not** contain that 42-hex string.
- Thus F01 is a reviewer **transcription/evidence-fidelity finding**, not a defect supported by the frozen request or R006 source. The IR's `BLOCKED_SOURCE` remains the original review disposition **as published**, but it cannot be used as affirmative independent source acceptance or as valid evidence of a code finding.

## Scope unchanged and next competent gate

- R006 source remains immutable at `dfdaae3a2f3d6adcd183514b2761e7d1c2d5ca2e`; blobs `tools/ts_ee_orca_jsonl_receipt_v6.py = 08fa4d3d5b829129adeaa39bf3182c8143507408`, `test/ts_ee_orca_jsonl_receipt_v6_test.py = d4dd738cb5243cdf55c45a101a4fbbe683d59826`.
- R006 POSIX synthetic test execution `60/60 PASS` and private historical A001 structural validation remain as previously verified. The 399,890-byte private original and 1,138-byte private receipt were **not** inspected by IR001.
- Historical OpenCode2 semantic A001 remains terminal failed/nonconformant. Full Commander→Orca reviewer runtime bridge remains `NO_RECOMMEND / 4F / 5A`.
- Historical IR001 still carries 5 advisories requiring independent disposition. Do not erase them on the strength of identity reconciliation.
- The next gate, if within the existing Developer grant, is **new independent WEB_INLINE source-only IR002**, separately frozen and dispatched under a NEW Review_ID/ExecutionAttempt. It should independently verify the 40-char subject and actual Git trees and inspect full R006 source and tests, taking IR001's transcription mistake as a reproducibility caution; it must NOT replay IR001 or A001 and must not claim full-runtime acceptance. Reviewer binding is per-responsibility, not canonical.
- `MODEL_CALLS=0` new OpenCode2, `ACTIONS_RUNS=0`, `PRODUCT_EFFECT=NONE`.

**Current:** `IR001_ORIGINAL_DURABLE / F01_INVALID_REFERENT / R006_SOURCE_ACCEPTANCE_PENDING_NEW_IR / RUNTIME_BRIDGE_NO_RECOMMEND`.
