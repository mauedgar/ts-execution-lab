# TS EE LLM048 — Original candidate 001 terminal FAIL

**Original ExecutionAttempt:** `TS-EE-LLM-048-ATTEMPT-001`; **authority:** `EXPERIMENTAL_CONTROL_ONLY`, Product NONE.

- Frozen Git subject: `mauedgar/ts-execution-lab@b04f2f1b4039fb954a5aa610c8990bcfd87f02c6`.
- [Original GitHub Actions run #41156598760](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156598760), attempt 1, terminal `completed/failure`. Failed step: `One bounded original non-idempotent provider test`.
- [Original failure artifact #13024229934](https://github.com/mauedgar/ts-execution-lab/actions/runs/41156598760/artifacts/13024229934), ZIP `sha256:fd9ca536823f4b82a160501e528bf6648e8817f390324273a70968754fdd44b5`, 22,676 bytes; expiry `2026-11-30T01:42:07Z`.
- **8/9 tests PASS**: cases 01–07 and 09 succeeded; case 08 (simultaneous cold-start consumers) failed before end-to-end verification.
- Native error: second consumer Python process exited code 1 during `consumer048.py:db()`, `sqlite3.OperationalError: database is locked` while executing `PRAGMA journal_mode=WAL`. The test expected exit 0 or 77, and therefore correctly flagged failure.
- Case 09 **demonstrated two effects** and different receipts when two POST requests bypassed the consumer entirely. Case 01/02 supported persistent UNKNOWN blocking with and without an underlying provider effect.
- This failure does **not** establish duplicate consumer dispatch in case 08. No other assertions from that case are promoted to PASS; original remains terminal FAIL.

**Disposition:** `FAIL_CLOSED_CONCURRENT_SQLITE_BOOTSTRAP`. No blind re-execution. A distinct corrected candidate `experiment/llm-048-db-bootstrap-002-20261030` was prepared only after terminal result and root cause reconciliation; it retains original provider and test blobs. Product untouched.
