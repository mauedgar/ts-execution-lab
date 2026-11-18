# R007 B1 — Existing synthetic attempt ledger reconciled (2026-11-18)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`; Product authority/effect NONE.
**Mode:** read-only reconciliation of exact existing synthetic files; **no new model call**, no Product effect, no replay, no cleanup.
**Source:** `R007_B1_CREATE_ONLY_ATTEMPT_LEDGER_V1.ps1`, Git blob `a987ab797b069d2c9db616c2c5798efbba6add1d` and `R007_B1_LEDGER_SYNTHETIC_SELFTEST_V1.ps1`, blob `14e43bb2ab8a66833a95d1f31de03f60fd611c64`, at `mauedgar/ts-execution-lab@cd2c90bff3ea049fbd64e6626bb6443dfac91c23`.

## Exact observation and no-replay disposition

The one-time attempt to submit these previously built scripts via the isolated Orca experiment terminal `term_c763c655-b52b-4c6a-ab04-de5cd2538e05`, process incarnation `3128fc7e-f5ee-4f52-a6da-6bc0ac523f1c`, was accepted once (`requestId=efd432b5-8da7-4c36-b03f-9bac7a5b11b3`, `replayed=false`), but its native screen returned `R007_LEDGER_TEST_BEGIN` followed by `BLOCKED_SYNTHETIC_TEST_PREVIOUS_EFFECT`. Therefore this newly submitted synthetic test **did not run** and must **not be retried** to manufacture a fresh PASS.

A separate bounded **read-only observation** of the original reserved synthetic root `%TEMP%/TS-EE-R007-LEDGER-SYNTHETIC-001` found five existing files. Exact names/record fields:

| File | Observed native effect | SHA256 |
|---|---|---|
| A001 claim | UNKNOWN_UNTIL_TERMINAL | `C1DA55665DA301E3E2ADE0A4AD803A0AF80AF7BDE06D9A397D5E506D57155B1A` |
| A001 terminal | NONE | `2377E6E1EF5067BAF724615ECE7D35A166FB4E16D7896783044D2739BE222561` |
| A002 claim | UNKNOWN_UNTIL_TERMINAL | `F6A0068812520DA2914B4531292DE8EB306D65D7580663140AAE09CD6D769B63` |
| A002 terminal | CONFIRMED | `5BED6E55FBACC49F858F124E12B0075E5C4D342DBE4262EB5AB8FC37908DF5AE` |
| A003 claim | UNKNOWN_UNTIL_TERMINAL | `B88763327E2B9E5D2AF47C269D82EBE8E93236AE870F370A7CE667827868C314` |

Additional native checks: `A003.terminal.json=ABSENT`, `A004.claim.json=ABSENT`. All observed schema identifiers were `ts-ee-r007-attempt-claim/v1` or `ts-ee-r007-attempt-terminal/v1`. The five files' sizes were respectively 305, 290, 305, 295, 305 bytes.

**Interpretation:** the existing file states are **consistent** with the four-case synthetic oracle: create-only A001 NONE, duplicate excluded, A002 CONFIRMED, A003 intentionally left UNKNOWN and A004 blocked by the UNKNOWN fence. However this does not establish the entire previous native test script reached its final 4/4 PASS marker: the prior original Orca dispatch identity and terminal completion marker were not recovered here. Consequently verdict is `EXISTING_SYNTHETIC_RECEIPTS_RECONCILED / COMPLETE_SELFTEST_VERDICT_UNVERIFIED`, rather than asserting a newly executed 4/4.

The preserved A003 `UNKNOWN` belongs to the synthetic test namespace only; it does not prove an unresolved **provider model** effect. Do not delete or overwrite it. Non-synthetic runner admission must use the separately prescribed host-owned ledger root, an exact new attempt and independent qualifications. This observed synthetic path is not a standing model-dispatch authorization.

**Next:** reuse ledger source, harden/test full transport original/stderr/durable terminal candidate, source review of coherent B1 batch. Native free-provider availability, billing and original provider custody remain independent preconditions before B2.
