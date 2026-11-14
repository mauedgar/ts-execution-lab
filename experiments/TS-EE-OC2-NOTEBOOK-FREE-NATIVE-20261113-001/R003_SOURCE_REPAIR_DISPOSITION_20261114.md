# TS EE — JSONL v3 SOURCE_ONLY candidate, post-IR001 repair R003

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001` (experimental DevLab).
**Status:** `R003_SOURCE_PREPARED / 34_OF_34_OFFLINE_TESTS_PASS / FRESH_SOURCE_IR_REQUIRED`.
**Authority:** NONE Product; no semantic execution authority generated; no integration into `main`.
**Preserved original semantic A001:** `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`; no replay.
**Reviewer choice:** `WEB_INLINE`, `OPENCODE_LOCAL` or another competent binding always selected explicitly per responsibility; none is canonical by this experiment.

## Prior independent IR and custody

Review `TS-EE-ORCA-JSONL-RECEIPT-V2-WEBINLINE-IR001-20261114-001` returned `NO_RECOMMEND / 3F / 5A`, source-only, with `F01` incomplete terminal grammar, `F02` TOCTOU on source/result paths and `F03` non-atomic final-path receipt write. Its exact 9,909-byte ORIGINAL was recovered from `libfile_4b3fce7bf9bc819186e2928dc1ebf7ba`, SHA-256 `b0ec8e773b546bcb8682d92126f31f3acda86c13a6af9547223a466445a4ff7d` and Git blob `6031f6a5954a2437ecd4ccb19eebc77a81917ba3`; published byte-identically at `mauedgar/ts-execution-transport@58a1cd48e1a70ee292925ca776968e6cfc745742:results/TS-EE-ORCA-JSONL-RECEIPT-V2-WEBINLINE-IR001-20261114-001/ORIGINAL.md`, readback verified.

Tree discrepancy preserved: IR froze source candidate tree `39c624a95ff3a299db3774a1069894d2fab52f8d` at code commit `deaf909cf7632b3e7f88c7a9c7a7f2d04c56c14b`. The subsequent request publication commit `d90414af016101125221d741971370253c932c36` has a different actual tree `9aa2821804e265d13e32a19b6d1b1ca9bb93fd9a`. IR correctly declined to attest the latter. The parser/test blobs at the reviewed source commit were independently verified. Never rewrite the frozen source/request.

## Repaired v3 source — isolated, additive, POSIX-only

- `tools/ts_ee_orca_jsonl_receipt_v3.py`, exact Git blob `55aa5026584a4bed5f01c6ea616d8c09171cfd6a`.
- `test/ts_ee_orca_jsonl_receipt_v3_test.py`, exact Git blob `7db16511e8b21861996071bd76d5541b9478e90a`.
- Source commit `2306680013874022d770404239c282b3da0f7ad9`, tree `e3623df2651b9cafdaf5401300d29fb4f4a90788`, branch `experiment/ts-ee-oc2-notebook-free-native-20261113-001`.

**F01:** versioned, intentionally narrow event grammar for `step_start`, `text`, `tool_use`, `step_finish`; validates `part.type`, step balancing, final step_finish, no text/tools outside active step, no error/unknown event accepted as terminal. Semantic status downgraded to `BOUNDED_JSONL_PARSED_UNVERIFIED_PROVIDER_SEMANTICS` — NOT a provider terminal, reviewer verdict or Product PASS.

**F02:** uses POSIX/WSL `dir_fd` traversal with `O_DIRECTORY` and `O_NOFOLLOW` for root/parents and source, `fstat` on the same descriptor, size/mtime/ctime/inode/device check, bounded read and exact digest comparison. No path-following source reopen; receipt directory bound to a file descriptor. Expected digest is still **caller-supplied**, not independently attested; native custody remains a separate runtime gate. Windows native is deliberately `POSIX_DIRFD_PLATFORM_REQUIRED` fail-closed (not tested or supported).

**F03:** writes receipt to a create-only `0600` staging inode in the already-open receipts directory; flushes + fsyncs content; atomically publishes using same-directory POSIX hard link that fails closed on collision; fsyncs parent and reads back exact bytes; removes stage only after confirmed success. On a post-link failure reports `UNKNOWN_PUBLISH_POSTCONDITION` and preserves potentially materialized original. No overwrite, no implicit retry, no partial receipt at final path.

## Test evidence and limitations

Source and tests were constructed under `/mnt/data/ts_orca_r003/` in an isolated test container and executed with Python 3.13.5: `python -m py_compile` PASS, `python -m unittest -v test_ts_ee_orca_jsonl_receipt_v3.py` **34/34 PASS** (0 FAIL). The exact local files have Git blobs `55aa5026584a4bed5f01c6ea616d8c09171cfd6a` and `7db16511e8b21861996071bd76d5541b9478e90a`; GitHub create/readback verified those exact blob IDs and content bytes after publication.

Tests cover clean atomic receipt, multiple balanced steps, missing/duplicate/out-of-order finishes/starts, invalid part.type, error/unknown events, tool status, unexpected edit observation, incorrect SHA, malformed/duplicate JSON, NaN, mixed sessions, missing LF, CRLF, huge/nonfinite cost, exit/model claims, final collision, traversal, source/parent/final symlinks, injected prelink write failure and simulated postlink fsync failure (UNKNOWN preserves final/stage), top-level receipt collision, invalid UTF-8 and parent absence. No actual `A001` ORIGINAL was used. No model, OpenCode2, Orca, Actions, provider billing, Product or GitHub workflow was run.

**Source test PASS != source acceptance:** this R003 candidate has not yet received an independent fresh-context IR. Runtime contract remains `NO_RECOMMEND / 4F / 5A` from earlier bridge IR; F01/F03/F04 of that full runtime and the A001 missing private ORIGINAL are not magically closed.

## Precise next gate

Independent `WEB_INLINE / SOURCE_ONLY / STRICT_READ_ONLY` IR of R003 source/test and this disposition. Check race hardening, POSIX limits, event grammar, atomic create-only finalization, test oracles, safe logging and non-claim of provider attestation. On findings, repair R003 only in new source commit without modifying historical A001. No model inference, Product effects, merge or Actions activation. Further runtime qualification requires separate Developer ruling.

**Current:** `R003_SOURCE_IR_PENDING / BRIDGE_RUNTIME_NOT_QUALIFIED / NO_PRODUCT_EFFECT`.
