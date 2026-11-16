# TS EE — JSONL POSIX R005 source repair disposition (2026-11-16)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`, experimental DevLab only.
**Scope:** evidence checker SOURCE_ONLY, **not** the runtime bridge, OpenCode2 reviewer or Product.
**Status:** `R005_SOURCE_PUBLISHED / 55_TEST_CASES_DEFINED_NOT_EXECUTED / INDEPENDENT_IR_REQUIRED`.
**Historical A001:** terminal `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`, no replay.
**Full runtime bridge:** `NO_RECOMMEND / 4F / 5A`, unchanged, NOT_QUALIFIED.
**Reviewer choice:** per-responsibility WEB_INLINE/OPENCODE_LOCAL/other, no canonical default.

## Exact source and verified immutable refs

- Prior independent R004 IR `TS-EE-ORCA-JSONL-V4-POSIX-WEBINLINE-IR001-20261115-001`: `NO_RECOMMEND / 2F / 5A`, run completed 2026-11-15 Argentina local date.
- The prior IR ORIGINAL: `mauedgar/ts-execution-transport@4b5d52473e00a3c2d660b1b51125b04c4d534d26:results/TS-EE-ORCA-JSONL-V4-POSIX-WEBINLINE-IR001-20261115-001/ORIGINAL.md`, Git blob `53451987e0283c28d2c9aba7bf49b95d6ad1bd52`, 10,063 UTF-8 bytes, SHA-256 `78364a62ec1c669a18066c63b0826d1e391b5803a39401dc7c9b29c8bad432ac`. Library `libfile_304ca34fa7448191a458451ec2a8dc5f`, exact copy recovered and GitHub readback identical.
- Frozen R004 source commit `539a88157610c5dac1cd871bbeb7191dab24eacc`, tree `a0302523ac91ec237d2d98d76b297c6c613a96d2`. Historical R004 source and ORIGINAL left intact.
- R005 source-and-tests commit `dcc439b2622ef58253d7253da54ccfef8712a9d7`, tree `74bf812de3a257892dd4eb6ecce2fdf8ac6d7dc4`.
- `tools/ts_ee_orca_jsonl_receipt_v5.py` blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`.
- `test/ts_ee_orca_jsonl_receipt_v5_test.py` blob `4cd97cefc425ceab76ce121b82007189ac8e8d24`.
- Created additively via GitHub and immediately read back byte-identically. No source or tests were executed in this gate.

## R004 F01 treatment — ancestry trust, bounded threat model

New `verify_trusted_ancestry_edge` binds each POSIX directory edge to actual opened `dir_fd` descriptors and `fstat`. It requires parent and child owners to be the effective UID or root, and prevents group/other-writable parent entries unless their sticky bit protects a trusted-owned child entry. This allows conventional `/tmp` sticky ancestry while rejecting untrusted writable non-sticky ancestors. `O_NOFOLLOW` remains on all traversed components. Tests now include a 0777 mutable ancestor rejection, a 01777 sticky ancestor acceptance, and a symlinked higher ancestor rejection.

**Limits:** same-UID and privileged writers are deliberately trusted/excluded; root-owned sticky parent protection depends on POSIX directory-entry semantics. No persistent file-name identity beyond observation is asserted. The checked path's metadata is a point-in-time observation, not a security boundary against out-of-model actors.

## R004 F02 treatment — cleanup and close uncertainty

New `close_owned_fd` preserves an already classified `UNKNOWN_*` when a second descriptor-close error occurs, and reports `UNKNOWN_PUBLISH_POSTCONDITION` if folder/root descriptor close fails after publication could have occurred. The root-level `run` marks `publication_possible=True` before entering `publish`, conservatively fencing all subsequent effects. The previous post-link `link_attempted` boundary and create-only hardlink publication remain unchanged.

Tests add fault injection for receipt-directory close after final link, root descriptor close after final link, simultaneous link-created-then-raise plus root close fault, and source-mode ancestry checks. Existing 48 tests are preserved as methods in the new v5 test module.

## Source verification and exact limitations

The current R005 module and test source were independently re-fetched from GitHub by Control: exact Git blobs verified, native Git commit/tree observed, key precondition and UNKNOWN logic present, 55 methods named `test_*` counted. This is **static inspection**, not Python execution. Do not report `55/55 PASS`. The current workspace in this chat did not receive a mount of repository source for execution; no localhost, notebook, Github Actions, Docker or outside model was used to run it.

The repaired R005 test file adjusts its sibling `tools` import path, addressing prior R004 advisory A02. Other advisories stay open unless an independent source review explicitly disposes them. Full parser behavior, real close/failure injection, shell portability and code compilation remain to be validated by an execution surface outside Commander semantic use; an independent IR must label its tests unexecuted.

## Next gate, no authority expansion

Freeze exact R005 source commit/tree/blobs in a separate **WEB_INLINE / STRICT_READ_ONLY / SOURCE_ONLY** Independent Review, independent of Control and prior reviewer. Request independent findings/advisories and explicit check that R004 F01/F02 are closed in source. Do not claim R005 operational/0F0A before this review and a competent disposition. Any full bridge runtime qualification remains separate and cannot be inferred from this helper.

No Product commits, PR, Actions execution, OpenCode2 model call, launch retry, adoption of reviewer default, or changes to the previous A001 terminal effect.

**Disposition:** `SOURCE_R005_REPAIR_PREPARED / TEST_EXECUTION_NOT_VERIFIED / RUNTIME_BRIDGE_NOT_QUALIFIED`.
