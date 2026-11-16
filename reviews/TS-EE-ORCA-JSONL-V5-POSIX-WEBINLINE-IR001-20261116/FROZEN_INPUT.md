# TS EE — Independent WEB_INLINE IR001 | JSONL R005 POSIX SOURCE_ONLY

**Review_ID:** `TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001`.
**ExecutionAttempt:** `TS-EE-ORCA-JSONL-V5-IR001-A001`, RESERVED_NOT_DISPATCHED.
**Reviewer binding:** `WEB_INLINE / STRICT_READ_ONLY / FRESH_INDEPENDENT_CONTEXT / SOURCE_ONLY`.
**Authority:** TS Developer Lab experimental ONLY; `Product_authority=NONE`, `Product_effect=NONE`.
**Subject:** `mauedgar/ts-execution-lab@74e98c436b62e199b5f109bad0eff947c7134a61`, native tree `17674f4abb8c0540b21f9ba664ba5a1399effd0f`. This subject is **not** the later publication commit of this request.
**Original target:** `mauedgar/ts-execution-transport:results/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001/ORIGINAL.md` (publication by Control after verified Library copy only).

## Direct independent reads — freeze exact files

1. `tools/ts_ee_orca_jsonl_receipt_v5.py`, Git blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`, ~18k chars.
2. `test/ts_ee_orca_jsonl_receipt_v5_test.py`, Git blob `4cd97cefc425ceab76ce121b82007189ac8e8d24`; 55 defined `test_*` methods.
3. `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R005_SOURCE_REPAIR_DISPOSITION_20261116.md`, Git blob `4a99aa97a2844214da742c5163b5f1d31fe6e79b`.
4. Independent prior R004 IR001 ORIGINAL `mauedgar/ts-execution-transport@4b5d52473e00a3c2d660b1b51125b04c4d534d26:results/TS-EE-ORCA-JSONL-V4-POSIX-WEBINLINE-IR001-20261115-001/ORIGINAL.md`, Git blob `53451987e0283c28d2c9aba7bf49b95d6ad1bd52`, exactly 10,063 bytes, SHA-256 `78364a62ec1c669a18066c63b0826d1e391b5803a39401dc7c9b29c8bad432ac`.
5. Previous R004 source frozen at `mauedgar/ts-execution-lab@539a88157610c5dac1cd871bbeb7191dab24eacc` tree `a0302523ac91ec237d2d98d76b297c6c613a96d2`, parser blob `6ab25af3f0d775d10d5857f9a4cb8f8813bd5004`; R004 IR `NO_RECOMMEND / 2F / 5A`.

## Scope / required independent analysis

Read every R005 source and test line from GitHub at the frozen ref and compare against the R004 findings, without assuming the implementer's disposition is right.

- **F01 ancestor integrity:** verify `verify_trusted_ancestry_edge`'s parent and child UID/mode checks under actual POSIX sticky directory entry rules. Could untrusted UID with writable non-sticky ancestor replace the receipt path despite descriptor checks? Is sticky bit sufficient when parent ownership is unexpected, parent mode changes, child owner differs or ancestor is renamed? Confirm source `O_NOFOLLOW` behavior and root trust; distinguish same-UID/root actors excluded by stated threat model from in-scope other UIDs. Check that file path identity claims remain observation-only.
- **F02 post-link descriptor-close classification:** inspect `close_owned_fd` and `publish`/ `run` finally blocks; does any close after a possible link or an already classified UNKNOWN return `BLOCKED_PRECONDITION`, hide UNKNOWN or trigger unsafe cleanup/retry? Audit OS-error paths, nested exceptions, double-close/leaks and proper stage preservation. A model that merely claims "fail-closed" is not enough: cite exact control flow and risks.
- **Testing:** identify whether 55 test methods are meaningful or contain faulty or incomplete injections; verify direct sibling-tools import, ancestry rejection, sticky allow, higher symlink ancestry, post-publication folder/root close faults and preservation of UNKNOWN under simultaneous failures. **Control did not execute R005 tests**, so do NOT claim 55/55 PASS or independent execution. Review may recommend tests to be run outside Commander; `tests_not_executed_by_IR=true`.
- Review prior A01–A05 advisories, parser grammar/event identity, reported billing disclaimers, provider attestation, metadata privacy, POSIX/WSL-only portability, root-owned directory trust. Distinguish source vulnerabilities from full runtime dependencies.
- The entire helper is deterministic and non-model. Do not launch Python/Orca/OpenCode2, Commander, Github Actions, or modify repos; no Product effect, no use of OpenAI provider quota. **Full Orca bridge IR remains `NO_RECOMMEND / 4F / 5A` and A001 semantically failed.**
- Developer ruling: reviewer selection is always explicit and per responsibility; this selected WEB_INLINE source-only IR does not make WEB_INLINE or OpenCode2 canonical.

## Independent original contract

Return exactly one `IR001_ORIGINAL` with Review_ID, attempt, exact subject commit/tree and blob verification, genuine independent source analysis, verdict `RECOMMEND_SOURCE_ONLY | NO_RECOMMEND | BLOCKED_SOURCE`, numbered Fxx and Axx with file:line, severity, evidence, bounded repairs and regressions, exact disposition of prior 2F/5A, unexecuted test limitation, runtime exclusion, `Product_effect=NONE`. Do not sign off 0F/0A without source evidence. Do not transfer acceptance authority or silently qualify native runtime.

The actual scheduled-task prompt **MUST inline in full** the verified `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` custody instructions (upload status, file IDs, byte count, SHA, readback, UNKNOWN/BLOCKED), not merely reference them here. Reviewer does not write GitHub Transport; only Control may publish a verified ORIGINAL.

**Status:** `FROZEN / NOT_DISPATCHED / ORIGINAL_ABSENT`. No new OpenCode model attempt is granted.
