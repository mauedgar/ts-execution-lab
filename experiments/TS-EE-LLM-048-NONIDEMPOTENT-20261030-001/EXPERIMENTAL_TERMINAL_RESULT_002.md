# TS EE LLM048 — Non-idempotent provider boundary: terminal reconciliation

**Date/time:** 2026-10-30 Argentina / 2026-10-31 UTC. **Authority:** `TS_EXECUTION_ENGINEERING / EXPERIMENTAL_CONTROL_ONLY`. **Product effect/authority:** `NONE`. **Final experimental disposition:** `PASS_BOUNDED_FAIL_CLOSED_UNKNOWN / COMPLETE_WITH_LIMITATIONS` for **candidate 002**, preserving candidate 001's terminal FAIL separately. No Upper LC #34/#35, Product TaskCycle, canonical Beads adoption or acceptance.

## Exact original attempts (never conflated)

### 001: FAIL preserved
- `ExecutionAttempt=TS-EE-LLM-048-ATTEMPT-001`, Git subject `b04f2f1b4039fb954a5aa610c8990bcfd87f02c6`.
- [Original GitHub Actions #41156598760](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156598760) run attempt 1 `completed/failure`, **8/9 PASS; case 08 FAIL**, process exited at `PRAGMA journal_mode=WAL` under concurrent first-open with `sqlite3.OperationalError: database is locked`. Original test was not weakened.
- [Original artifact 13024229934](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156598760/artifacts/13024229934), ZIP `sha256:fd9ca536823f4b82a160501e528bf6648e8817f390324273a70968754fdd44b5` (22,676 bytes; expires 2026-11-30 01:42 UTC). Report `ORIGINAL_001_TERMINAL_FAILURE.md` indexed on source branch.

### 002: new, independently qualified correction
- `ExecutionAttempt=TS-EE-LLM-048-ATTEMPT-002`; **new source subject** `mauedgar/ts-execution-lab@08a3043c6476662cc05f3977e6132c70c05885e6` on `experiment/llm-048-db-bootstrap-002-20261030`.
- [Original GitHub Actions #41156746080](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156746080), run_attempt 1, `completed/success`, job `124405105749`.
- **Nine of nine** original test cases PASS, 0 FAIL/ERROR, run logs `TS_EE_LLM048_CANDIDATE_002=PASS_BOUNDED_FAIL_CLOSED_UNKNOWN;tests=9;Product=NONE`.
- [Original artifact 13025461214](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156746080/artifacts/13025461214), original ZIP `sha256:270e82a193dcb2fe555ddfc765977bf68c7cc3c70f32f27321cf0ba640e2d71a` (24,607 bytes; expires 2026-11-30 01:44 UTC).
- Original fixture `RESULT048.json` `sha256:bea6c110de10b5718b8390313a8c71139fcb8248b34096aed3565b474939ee77`; artifact also contains the original SQLite DBs, logs and original-file SHA256 manifest.
- Pre-execution frozen source blob pins: `provider048.py@331e3f84993a120d355273d16a2f37aa3ebdbebc` **unchanged**; `test048.py@d7e1233f3223c77efa23ce87757b455fdb2b2b5b` **unchanged** (same nine original tests); `consumer048.py@811942dae3560c795477b9dfd0c98c80dd67cc6f`, changed only to handle **local SQLite WAL bootstrap lock** with bounded metadata retries, *never a provider HTTP retry*. See `REPAIR_002_DOD.md` for exact grant and scope.

**Receipt identity advisory I001:** the frozen `test048.py` itself embeds the original literal `execution_attempt=TS-EE-LLM-048-ATTEMPT-001` in its inner `RESULT048.json`, including when run by candidate 002. That **inner field is inherited fixture metadata, not the reliable external ExecutionAttempt-002 identity**. The canonical native identity for this bounded *experimental run* is GitHub Actions run `41156746080`, its exact run_attempt, Git subject, job and artifact `13025461214`. This index reconciles the distinction; it does not modify the original result bytes or claim perfect provider-native 002 receipt binding. As a limitation, E2E self-identifying original JSON for 002 is **not qualified**. Do not feed the inherited 001 label into any Product TaskCycle or automatic transport consumer.

## Nine verified technical outcomes (candidate 002)

| Test | Bounded observed outcome |
|---|---|
| 01 | Provider applies effect, drops TCP ACK: client persists UNKNOWN and blocks same-attempt repeat; underlying effect one |
| 02 | Provider drops ACK **before** effect: client UNKNOWN also blocks repeat despite actual zero effects |
| 03 | Provider crashes after commit: restarted provider; client still does **not** retry UNKNOWN, underlying effect one |
| 04 | ACK explicitly journaled: subsequent attempt resolves locally to NO_RETRY_CONFIRMED, no second POST |
| 05 | Client receives then discards ACK: UNKNOWN remains blocked, one underlying effect |
| 06 | Same ID, different owner: BLOCK_IDENTITY before network, one original effect |
| 07 | Process stops after journal reservation but **before POST**: even though provider effect zero, the consumer refuses blind retry |
| 08 | Two concurrent consumers with the same SQLite journal: only one POST reserved/authorized, one provider effect; WAL first-open precondition resolved |
| 09 | Two deliberate POSTs that **bypass the consumer**: non-idempotent provider creates **two distinct durable effects/receipts** |

These are tests of real separate localhost processes/SQLite transactions, no remote model API. The apparent one-effect invariant applies **only to dispatches through this synthetic consumer**. It trades progress/liveness for duplication safety; no automatic recovery of UNKNOWN is possible when provider exposes neither idempotency nor authoritative status. A real provider without these capabilities cannot inherit the guarantees from experiments 046/047.

## Evidence and remaining debt

- Raw provider/consumer DBs and logs in Actions artifact, not durable in Library merely by listing refs; provider retention expires in ~30 days.
- No real cloud-provider ACK, physical power fault, TLS, distributed network partition, multi-machine race, privileged writer enforcement, or native model event-log transport qualified.
- Original 001 FAIL preserved. Original 002 PASS applies only to **nine bounded tests**; self-identification of `RESULT048.json` remains an advisory. Product branch `tools` last observed `bc9e60b9cad79037b40c298d5c9a84f17a33d909`, reobserve before any Product action.
- **Next recommendation:** stop extending synthetic cases by default; consolidate 040–048 into a concise experimental capability matrix showing qualified behavior, known hard limits, and exact adoption blockers for a future competent Product consumer after the Upper LC #34/#35 DoD. Do not add a scheduler, Kernel, lifecycle, or model router without a demonstrated need and Product authority.
