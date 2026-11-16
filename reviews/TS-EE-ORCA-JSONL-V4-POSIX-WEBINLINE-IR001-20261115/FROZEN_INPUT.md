# TS EE — WEB_INLINE IR001 | JSONL v4 POSIX, SOURCE_ONLY

**Review_ID:** `TS-EE-ORCA-JSONL-V4-POSIX-WEBINLINE-IR001-20261115-001`  
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V4-IR001-A001` (RESERVED, NOT_DISPATCHED)  
**Reviewer binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH INDEPENDENT CONTEXT / SOURCE_ONLY`.  
**Authority:** TS Developer Lab experimental only; `Product_authority=NONE`, `Product_effect=NONE`.  
**Exact subject:** `mauedgar/ts-execution-lab@539a88157610c5dac1cd871bbeb7191dab24eacc`; tree `a0302523ac91ec237d2d98d76b297c6c613a96d2` (native Git endpoint verified by Control).  
**Branch:** `experiment/ts-ee-oc2-notebook-free-native-20261113-001`, no merge/main acceptance.  
**Expected ORIGINAL target:** `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-V4-POSIX-WEBINLINE-IR001-20261115-001/ORIGINAL.md`, published later by Control only after verified Library custody.

## Immutable independent source reads

1. `tools/ts_ee_orca_jsonl_receipt_v4.py` — Git blob `6ab25af3f0d775d10d5857f9a4cb8f8813bd5004`; 15,918 UTF-8 bytes.
2. `test/ts_ee_orca_jsonl_receipt_v4_test.py` — Git blob `bb0661e929ebbd91378a04f73f8ce1d2ceca4a5f`; 14,174 UTF-8 bytes.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R004_SOURCE_REPAIR_DISPOSITION_20261115.md` — Git blob `a5512b1c4ff282fe4f5822a89a4b6419d8661180`.
4. Prior independent R003 IR ORIGINAL: `mauedgar/ts-execution-transport@ef956f26589c734ab4fb23450738134701af25b4:results/TS-EE-ORCA-JSONL-V3-POSIX-WEBINLINE-IR001-20261114-001/ORIGINAL.md`, blob `92775bce4d5e744d17a18134e87c164b8729eebe`, 10,804 bytes, SHA-256 `da1025f41094347034f9bff7e5c7b408a831750a6abe59162d334e7a5c125bc8`, prior `NO_RECOMMEND / 2F / 6A`.
5. Original experimental A001 remains terminal; no source here authorizes new OpenCode2 execution or Product effect.

## Independent review DoD, narrow truthful claims

- Verify actual subject commit/tree and EVERY Git blob independently. Read and inspect all R004 Python source and all 48 tests, not just Control's report.
- Evaluate R003 **F01 final-path inode substitution**: does `0700` exclusive UID directory ownership/permission check provide a clearly defined, operationally enforceable trust model? Is same-UID/privileged interference expressly excluded? Is the staged inode bound to readback fd/final inode at observation? Does the returned digest support downstream trusted custody? Never infer immutable future path.
- Evaluate R003 **F02 ambiguous link / cleanup**: is `link_attempted` set before syscall, and do *all* ambiguous interruptions—including syscall with effect then exception—preserve stage/final and classify `UNKNOWN_PUBLISH_POSTCONDITION`? Are prelink cleanup failures `UNKNOWN_STAGE_CLEANUP_POSTCONDITION`? Search for remaining unsafe cleanup, exceptions that may mask the original effect, or incorrect replay assumptions.
- Examine root ancestors (`O_NOFOLLOW` each component), directory traversal races, symlinks, source hardlink aliases, trust/ownership of parent directories, malicious concurrent same UID and privileged actors. Distinguish within and outside the explicit bounded trust model. Identify vulnerabilities inside the stated scope, not hypothetical broader guarantees.
- Analyze atomic publish, fsync/file+dir and final identity, returned observation-time inode/digest, bytes/encoding, JSON depth and duplicate keys, input limits, source fd ownership, model/provider billing/verdict fields intentionally unverified, logging privacy.
- Assess all 48 test cases for genuine fault injection, meaningful negative assertions, mistaken mocks, missing race and depth tests, platform compatibility, and false green tests. Control ran Python 3.13.5 `py_compile` PASS and **48/48 unittest PASS twice**, with different `PYTHONHASHSEED` values. IR **MUST NOT execute** code; report `tests_not_executed_by_IR=true`.
- Scope strictly source-only helper for POSIX/WSL. No live original A001, runtime Orca bridge F01/F03/F04, host lease, actual provider model/price, independent billing, Product acceptance, Windows-native support, reviewer route, Actions, merging, or automatic fallback are qualified by this review.
- Reviewer remains an explicit competent choice per responsibility: WEB_INLINE, OPENCODE_LOCAL or other; no global default via this experiment. Don't conflate IR verdict with Developer acceptance.
- Examine previous advisories A01–A06 and report `RESOLVED_BY_SOURCE`, `PARTIALLY_RESOLVED`, `OUT_OF_SCOPE_RUNTIME`, or `STILL_OPEN_SOURCE` as appropriate. Do not erase them without evidence.

## Required result

Produce **one** `IR001_ORIGINAL` with Review_ID/ExecutionAttempt, exact subject/trees/blobs, independent full-source assessment, `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, all findings Fxx and advisories Axx with file:line, mechanism, risk, bounded repair, previous IR 2F/6A reconciliation, remaining evidence gaps and precise next competent gate.

If source achieves 0F/0A, qualification remains `SOURCE_ONLY`, not Product adoption or runtime mechanism PASS. Reviewer MUST NOT execute Python/Orca/Commander/OpenCode2/Actions, alter files, create commits/PRs, or spend model provider quota. **Custody:** in a scheduled task, inline the full Library handoff template with exact SHA/bytes/readback clauses; this frozen input alone is insufficient for Library publication.

**State:** `FROZEN / NOT_DISPATCHED / ORIGINAL_ABSENT`.
