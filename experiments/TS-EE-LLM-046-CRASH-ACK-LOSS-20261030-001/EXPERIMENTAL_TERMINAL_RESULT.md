# TS EE LLM046 — Experimental terminal crash/ACK-loss reconciliation

**Date:** 2026-10-30. **Authority:** EXPERIMENTAL_CONTROL_ONLY / TS_EXECUTION_ENGINEERING. **Disposition:** `PASS_BOUNDED_NATIVE_CRASH_RECONCILIATION / COMPLETE_WITH_LIMITATIONS`. No Tecnotron Product authority, effects, #34/#35, Upper LC, canonical Beads integration, OpenCode model routing or TaskCycle initiation.

## Frozen source, owner, single native attempt

- Operation `TS-EE-LLM-046-CRASH-ACK-LOSS-20261030-001`
- ExecutionAttempt `TS-EE-LLM-046-ATTEMPT-001`, owner `TS_EXECUTION_ENGINEERING`, exactly one GitHub Actions push-triggered run.
- Exact original Git subject `mauedgar/ts-execution-lab@4192396f2363b5df53fe0a441281ff1372ceaa05`; branch `experiment/llm-046-crash-ack-loss-20261030-001`, original source and DoD frozen before workflow dispatch.
- Fixture source Git blob `6c1f267ed4f2e92e377456ffd3263643af2bc689`; independent six-case test Git blob `1f5688e378d8239147b5f5d6d4c95c946835cd97`; workflow validates both before execution.
- [Original GitHub Actions #41140406488](https://github.com/mauedgar/ts-execution-lab/actions/runs/41140406488), job `124353018460`, run attempt 1, `completed/success`.
- [Original artifact #13018597729](https://github.com/mauedgar/ts-execution-lab/actions/runs/41140406488/artifacts/13018597729): `ts-ee-llm046-original-41140406488`, ZIP `sha256:13781643da9171d3a2413d5a07bff98fa2fd3118bcf473c965c9ecf7fc47d165`, 9,911 bytes. Provider expiration **2026-11-29T22:47:32Z**.
- Original `RESULT046.json` SHA-256 `96e68324c37ee85ed42fb9a4f456b120576bad36db5b68b83a6f4a786c77843b` emitted by native run. Artifact retains six scenario directories each with provider SQLite and consumer SQLite DB, original run log and `SQLITE_ORIGINAL_SHA256.txt` manifest.
- Native output: `TS_EE_LLM046=PASS_BOUNDED_NATIVE_CRASH_RECONCILIATION;tests=6;Product=NONE;provider=SQLITE_MOCK`. Six separate tests succeeded; no runtime assertions or DB integrity failures.

## What was actually demonstrated

All scenarios run against synthetic transactional state in SQLite configured with WAL, `synchronous=FULL`, `BEGIN IMMEDIATE` and one attempt-ID primary key:

| Scenario | Injected failure / challenge | Original observed outcome |
|---|---|---|
| 01 | Real provider subprocess crash `os._exit(73)` after `COMMIT`, before ACK | No ACK, effect row survives new interpreter, authoritative probe finds same receipt and exactly one effect; consumer journal `INTENT → RECONCILE_UNKNOWN → NO_RETRY_CONFIRMED` |
| 02 | Real crash `os._exit(74)` before `COMMIT` | Rollback; unavailable provider stays UNKNOWN, later verified absence only yields `ABSENT_REQUIRES_AUTHORITY`, no blind retry |
| 03 | Consumer deliberately discards provider ACK | Fresh consumer process reconciles original provider receipt; one effect, no repeated operation |
| 04 | Reuse attempt ID with mismatched owner | `BLOCK_IDENTITY` and no overwrite or second effect |
| 05 | Explicit *test-injected* identical duplicate submission | `ALREADY_CONFIRMED` and same receipt; unique effect remains one. This is **not** a Product retry after UNKNOWN |
| 06 | Two simultaneous provider subprocesses submit same identity | Exactly one `APPLIED_ACK`, the other `ALREADY_CONFIRMED`; provider primary-key uniqueness and transaction prevent duplicate |

Both databases passed `PRAGMA integrity_check` in all six cases. Each test starts a fresh provider/client DB pair, all effects remain inside GitHub runner's disposable `RUNNER_TEMP`. No external provider or real financial effect called.

## Local development preflight provenance

Before freezing and dispatching GitHub run 41140406488, the *first local developer preflight* passed scenarios 01–05 and exceeded its allotted window in 06. A separately executed isolated case 06 then passed; a full fresh local preflight subsequently reported 6/6 PASS. These local design tests are **not** GitHub `ExecutionAttempt-001` and cannot overwrite the first timeout. The GitHub original attempt was dispatched once and returned 6/6 PASS.

## Scope and residual qualification debt

- This is empirical recovery of a **mock, locally persisted transactional effect** across a real provider process exit, not evidence that a real OpenCode/LLM provider guarantees idempotency, offers authoritative receipts, or withstands a crash at any arbitrary instruction.
- `PRAGMA synchronous=FULL` is configured, but physical power-cut durability, multi-host partitions, remote ACK-loss, provider outages and crash-fault injection after external transactions are **not measured**. An authoritative negative probe is not a Product retry grant.
- The preserved artifact's 30-day retention means raw SQLite originals are **not permanently archived** merely by storing this report in Git or Library. Portable transport of original model JSONLs from experiments 040–045 remains separately blocked/unqualified.
- No canonical Scheduler, Kernel, external worker or Beads authority added. No real TaskCycle transition, reviewer acceptance, merge or Product configuration change.
- Next independent experimental option: a two-endpoint mock provider with explicit network ACK drop and provider restart in separate processes/containers, evidence-preserving publisher and durable remote join, with strict no-retry UNKNOWN and identity controls. Not a Product authorization.
