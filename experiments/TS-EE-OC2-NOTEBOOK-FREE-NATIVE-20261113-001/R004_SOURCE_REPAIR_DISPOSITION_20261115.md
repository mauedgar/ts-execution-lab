# TS EE — JSONL v4 POSIX source hardening R004 (2026-11-15)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`, experimental Developer Lab.
**Authority:** no Product effects, no canonical harness or reviewer adoption, no Actions activation, no OpenCode2 inference.
**Status:** `R004_SOURCE_CANDIDATE / 48_OF_48_OFFLINE_TESTS_PASS / INDEPENDENT_SOURCE_IR_PENDING`.
**Historical A001:** `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`, immutable, never retry.
**Full Orca bridge:** `NO_RECOMMEND / 4F / 5A`, NOT qualified or adopted.

## Direct evidence and previous IR

- R003 independent IR `TS-EE-ORCA-JSONL-V3-POSIX-WEBINLINE-IR001-20261114-001`: `NO_RECOMMEND / 2F / 6A`.
- R003 ORIGINAL: `mauedgar/ts-execution-transport@ef956f26589c734ab4fb23450738134701af25b4:results/TS-EE-ORCA-JSONL-V3-POSIX-WEBINLINE-IR001-20261114-001/ORIGINAL.md`; Git blob `92775bce4d5e744d17a18134e87c164b8729eebe`, exact 10,804 UTF-8 bytes, SHA-256 `da1025f41094347034f9bff7e5c7b408a831750a6abe59162d334e7a5c125bc8`.
- R003 source commit `8bec3aa449f82b05326177ef847b73b39cd9bde2`, tree `dde0ef9560705dfca8b299ae9a2255721101a609`. Historical source is UNCHANGED.
- R004 code-only commit `ff5b9af7bd6a8921d28fd16d9716b828c7721f1f`, **actual tree** `2cfc278d828492044d22d06297a87629fb1da2a6`. Source `tools/ts_ee_orca_jsonl_receipt_v4.py` blob `6ab25af3f0d775d10d5857f9a4cb8f8813bd5004` (15,918 bytes). Tests `test/ts_ee_orca_jsonl_receipt_v4_test.py` blob `bb0661e929ebbd91378a04f73f8ce1d2ceca4a5f` (14,174 bytes). GitHub readbacks match the original local file bytes.

## F01 source treatment — directory and receipt identity

- A 0700 **same-UID-exclusive trusted receipts directory** is mandatory and checked at runtime by owner uid and exact mode; rejects group and other access. This does NOT protect against malicious same-UID processes or privileged adversaries. Consumers must also be within that trusted boundary.
- Opened root's absolute path is traversed from `/` via `O_DIRECTORY | O_NOFOLLOW` at every component, preventing symlinked ancestors; sources/receipt parent and source file are opened relative to descriptor-bound directories and hashed over the same opened descriptor.
- Publisher keeps `fstat` of staged inode, then checks `(st_dev,st_ino)` of final readback FD against staged inode and compares exact bytes. After stage cleanup and parent fsync, rechecks the final entry's dev/ino, owner and 0600 mode **at observation time**.
- Returns `receipt_sha256`, byte length and observed dev/ino to allow binding a downstream independently durable custody manifest. This is **not** an immutable later path guarantee; no stronger claims against same-UID writers or future modification are made.
- Test includes regular-file substitution of final after link, not just symlink collision.

## F02 source treatment — ambiguous effect classification

- `link_attempted=True` is set **before** the syscall and never depends on a successful return. Any exception after that transition is `UNKNOWN_PUBLISH_POSTCONDITION`, preserves any staged/final artifacts, and prevents blind retries.
- Prelink failure triggers stage cleanup; **cleanup failure** is instead `UNKNOWN_STAGE_CLEANUP_POSTCONDITION`. No cleanup attempted when link could have effected final creation, even if `os.link` raised.
- Final readback, stage cleanup, directory fsync, and post-cleanup identity check all remain inside the post-link ambiguity boundary. Status `RECEIPT_PUBLISHED_AT_OBSERVATION` is not an indefinite path-integrity or provider-verdict guarantee.
- Fault tests simulate `link()` creating final then raising, link failure without effect, prelink fsync and cleanup errors, postlink unlink and fsync errors, and concurrent regular-file replacement.

## Additional advisories

- Bounded JSON recursion nesting scanner (max depth 128) and `RecursionError` catch convert too-deep input to an ordinary fail-closed result. Limits event bytes to 1 MiB and stream to 16 MiB.
- Only narrow `step_start/text/tool_use/step_finish` grammar is accepted. Provider schema identity, stream authenticity, message step IDs and native terminal receipts are **not** attested. It does not copy prompts or original JSONL into published receipt.
- POSIX `dir_fd`, hardlink and fsync behavior only. Windows native unsupported. Source hardlink aliases and privileged/same-UID writers are outside the assumed threat boundary, not proven impossible. An actor controlling these is not safely mitigated by this candidate.
- A claimed zero-cost `opencode/deepseek-v4.1-flash-free` model and `exit_claim=0` do **not** attest provider routing or invoices. All independent verification booleans stay false.
- No provider, model, Orca, Commander, Actions or Product process was launched.

## Test evidence

Isolated local Linux/POSIX container, Python 3.13.5; `py_compile` PASS.
`python -m unittest -q test_ts_ee_orca_jsonl_receipt_v4.py` PASS **48/48** with `PYTHONHASHSEED=1`, and repeated **48/48** with `PYTHONHASHSEED=42`, no failures. Includes ordinary receipt, multi-step, invalid JSON, duplicate keys, depth, NaN, mixed sessions, symlink ancestors, strict directory ownership/mode, atomic publication collision, final regular-file swap, ambiguous `link` effect, stage cleanup errors, directory fsync failure, cost/metadata disclaimers, sensitive prompt nonpublication, source hash/exit/model claims and no-repeat effect. These are Control-run synthetic tests; **not independently executed by an IR**.

## Exact scope and next gate

R004 is a fresh *source-only* experimental candidate. A fresh `WEB_INLINE / STRICT_READ_ONLY` IR must verify full source/test files, actual code commit/tree, F01/F02 repairs, threat model and any new defects. Do not call SOURCE PASS until that IR reaches competent 0F/0A; such PASS still does not qualify the runtime bridge or mandate OpenCode2 as reviewer.

Selection of WEB_INLINE, OPENCODE_LOCAL or another reviewer remains explicit and per-responsibility. No Product effect; no GitHub Actions run; no model calls; no commit to main.
