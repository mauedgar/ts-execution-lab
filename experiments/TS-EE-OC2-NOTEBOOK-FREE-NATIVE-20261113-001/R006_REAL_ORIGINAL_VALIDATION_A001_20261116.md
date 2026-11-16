# TS EE — R006 private validation against historical A001 ORIGINAL (2026-11-16)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.  
**Validation Operation:** `TS-EE-R006-REAL-ORIGINAL-VALIDATION-OP001`.  
**Validation ExecutionAttempt:** `TS-EE-R006-REAL-ORIGINAL-VALIDATION-A001` — one dispatch, terminal `RECEIPT_PUBLISHED_AT_OBSERVATION`; no replay.  
**Historical OpenCode2 ExecutionAttempt:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001`, preserved terminal `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`; no new inference.  
**Authority:** TS Developer Lab experimental source-only, Product authority/effect NONE. No canonical reviewer or runtime integration.

## Bound source, regression proof and native execution

- R006 exact source-and-test commit: `mauedgar/ts-execution-lab@dfdaae3a2f3d6adcd183514b2761e7d1c2d5ca2e`, branch `experiment/ts-ee-oc2-notebook-free-native-20261113-001`. The file's original Git blobs were fetched directly and reverified by `git hash-object` in the existing isolated Orca worktree after a clean `--ff-only` fast-forward: `tools/ts_ee_orca_jsonl_receipt_v6.py` blob `08fa4d3d5b829129adeaa39bf3182c8143507408`, `test/ts_ee_orca_jsonl_receipt_v6_test.py` blob `d4dd738cb5243cdf55c45a101a4fbbe683d59826`.
- Synthetic deterministic gate `TS-EE-R006-POSIX-TEST-A001` in notebook `DESKTOP-DJLBEQH`, Ubuntu 24.04 WSL and Python 3.12.3; native mechanical PID `13100`, exit 0, **60/60 PASS / 0 FAIL**, unittest-reported duration `0.633 s`. Exact original test output (not a provider model original) was read back and preserved in GitHub Transport at `mauedgar/ts-execution-transport@4029bf20cc3b04ea337b1f97d14c704364f86c5e:results/TS-EE-R006-POSIX-TEST-A001/TERMINAL_OBSERVATION.txt`, blob `cc79d6cd36b9c4be67f78876ef2de5ad950a2d8c`; 60 lines of test `ok`.
- R006 supports **uniform LF or uniform CRLF**, rejects mixed line endings and missing final newline, and records `source_line_ending` without modifying the ORIGINAL or its SHA-256. The v5 source and historical R005 55/55 test proof remain unchanged.

## Private source preservation and one-run native result

- Historical model ORIGINAL remains on the original notebook Orca workspace, `399,890` bytes, SHA-256 `ea873a99533684f3ee2ab9d7f39fb634031969c689bff7a95919f5ba53085ae9`. No original bytes are uploaded here.
- Bounded work copy in **private** WSL ext4 directory `/tmp/ts-ee-r005-a001-private-20261116-001` (mode `0700`, owner UID `1000`), staged `results/ORIGINAL.jsonl` (mode `0600`, same 399,890 bytes and SHA-256). This is retained privately for custody reconciliation and is not GitHub/Library material.
- The preceding **distinct** R005 validation `TS-EE-R005-REAL-ORIGINAL-VALIDATION-A001` terminated `BLOCKED_PRECONDITION / ORIGINAL_NOT_LF_TERMINATED`, with no receipt effect. Native last four raw bytes `7d 7d 0d 0a` confirm CRLF; original and staging bytes are unmodified. Historical checkpoint `mauedgar/ts-execution-lab@ae4f7bda3fcd3a24df2cdf4273c88af730c1db49:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R005_REAL_ORIGINAL_A001_BLOCKED_CRLF_20261116.md`.
- R006 executed **once** via the existing isolated Orca terminal `term_481dfbce-9351-4968-a32d-828f1d58a53a`, native send request `fbd092be-1708-4a2c-9bec-b9e8aa8c326f`, incarnation `4b9735b6-0890-4f1b-8054-a4f63d25f4bc`. It invoked the already-frozen Python v6 checker with `python3 -B`; **not OpenCode2**.
- Deterministic native stdout: `RECEIPT_PUBLISHED_AT_OBSERVATION`, `original_event_count=63`, `source_line_ending=CRLF`, `original_sha256=ea873...85ae9`, `semantic_verdict=NOT_ASSESSED`, observed receipt size `1138` bytes and SHA-256 `0cdc1354404739b193536b87ac3ca569a78e1a139994b2600a2452f582153c5d`; native device `2096`, inode `12257`. This is a point-in-time observation, **not** perpetual immutability.
- Private receipt `/tmp/ts-ee-r005-a001-private-20261116-001/receipts/R006_A001_VALIDATION.json` remained on notebook ext4, exactly `1138` bytes, mode `0600`, UID `1000`; SHA reverified with native `sha256sum` PID `6176`, metadata verified with native `stat` PID `2000`. Its bounded JSON was parsed outside Commander and checked for expected fields and no raw-prompt/secret field names. **The private receipt itself is not published to GitHub**.

## Validated whitelisted counters and uncertainty

- `schema=ts-ee-orca-jsonl-v6-posix-source-only`, `source_line_ending=CRLF`, `event_count=63`: `step_start=14`, `step_finish=14`, `text=1`, `tool_use=34`.
- `read_only_tool_events=34`, `other_tool_events=0`, `reported_tool_errors=2`.
- `provider_reported_total_cost=0` (**provider-reported**, not independent invoice or account billing proof).
- `provider_signature_verified=false`, `independent_billing_verified=false`, `native_terminal_verified=false` **as claimed by the checker**, `semantic_review_verdict=NOT_ASSESSED`, `result=BOUNDED_JSONL_PARSED_UNVERIFIED_PROVIDER_SEMANTICS`. Control additionally witnessed the one native Orca terminal invocation and private receipt hash, but does not promote these observations to provider-authenticated provenance.
- **Important:** Structural read-only tool names and reported zero model cost do NOT establish compliance with the bounded review instructions. Original historical OpenCode2 A001 remains semantically `NO_RECOMMEND`; the full Commander→Orca runtime bridge remains `NO_RECOMMEND / 4F / 5A`.

## Disposition, independent gate, privacy

This validates R006's **compatibility and structural parsing of the actual historical source** under a bounded private trust model, plus 60/60 synthetic tests. No external provider/model was called, no historical inferential effect repeated, no Product code touched or accepted, and no Actions run.

**R006 source has NOT yet received a fresh independent WEB_INLINE IR**. Next competent experimental gate: freeze source commit/tree/blobs plus the present **sanitized** real-original observation and request a fresh `WEB_INLINE / STRICT_READ_ONLY / SOURCE_ONLY` Independent Review of uniform CRLF handling, test oracles and preservation of raw digest; do not provide the 399,890-byte ORIGINAL or private 1,138-byte receipt publicly. Even 0F/0A source approval must not imply bridge runtime qualification or a reviewer default. Reviewer selection (WEB_INLINE, OpenCode2 or other) stays a per-responsibility competent choice.

`MODEL_CALLS=0 · ACTIONS_RUNS=0 · PRODUCT_EFFECT=NONE`.

**Current checkpoint:** `R006_TESTS_60_60_PASS / REAL_ORIGINAL_STRUCTURE_PASS / PRIVATE_RECEIPT_HASH_VERIFIED / SOURCE_IR_PENDING / FULL_BRIDGE_NOT_QUALIFIED`.
