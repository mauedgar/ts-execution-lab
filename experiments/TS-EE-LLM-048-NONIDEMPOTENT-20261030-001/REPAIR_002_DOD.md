# TS EE LLM048 — Separate correction candidate 002 (bounded DB bootstrap only)

**Parent frozen original:** `mauedgar/ts-execution-lab@b04f2f1b4039fb954a5aa610c8990bcfd87f02c6`. Original `TS-EE-LLM-048-ATTEMPT-001` / [Actions 41156598760](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156598760) **terminal FAIL, 8/9**. Original artifact `13024229934` SHA-256 ZIP `fd9ca536823f4b82a160501e528bf6648e8817f390324273a70968754fdd44b5`, preserved. Failure case 08: concurrent first-open consumer attempts caused `sqlite3.OperationalError: database is locked` during `PRAGMA journal_mode=WAL`. No duplicate provider effect was demonstrated by the failing assertion; case 08 did not reach its intended end-to-end verification.

**New independent candidate:** branch `experiment/llm-048-db-bootstrap-002-20261030`, proposed ExecutionAttempt `TS-EE-LLM-048-ATTEMPT-002`; allowed only because terminal FAIL was observed and root cause was isolated. It is a distinct source commit/run/receipt, **not an automatic retry of 001 or an effect replay**. Model/Product authority NONE.

- `provider048.py` exact unchanged original blob `331e3f84993a120d355273d16a2f37aa3ebdbebc`.
- `test048.py` exact unchanged original nine-case blob `d7e1233f3223c77efa23ce87757b455fdb2b2b5b`. Acceptance not weakened; still tests cold-start concurrent consumers.
- `consumer048.py` changed solely in local journal-mode initialization, new blob `811942dae3560c795477b9dfd0c98c80dd67cc6f`, from original `aa08297e4e9f6cd4ac02821222c242135293b493`.
- New bounded retry applies **only to local SQLite WAL metadata initialization**, up to 100 attempts with 25 ms spacing on an explicit `database is locked` error. It does not execute provider HTTP, modify the effect intent after error, retry UNKNOWN, create Product effects, or alter provider idempotency. All other schema and contract behavior unchanged.

**DoD:** A new unique one-shot GitHub Actions run pinned to these three blobs; the original nine tests execute without modifications, must return 9/9 and preserve original SQLite DBs, run logs, journal, SHA256 manifest and `RESULT048.json`. The new result is independently classified and does not overwrite the original failure. A PASS still qualifies only a localhost non-idempotent synthetic provider/SQLite consumer, with deliberate liveness loss at UNKNOWN. No new scheduler/kernel or Beads/Product adoption.

**Stop:** Any other FAIL, ambiguous identity, changed test blob, unexpected file or source mismatch => preserve original and fail closed; no blind replay.
