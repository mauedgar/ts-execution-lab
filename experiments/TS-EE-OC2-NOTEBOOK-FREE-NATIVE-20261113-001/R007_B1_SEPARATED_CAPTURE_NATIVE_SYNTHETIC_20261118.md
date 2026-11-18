# R007 B1 — Native Orca separated capture synthetic PASS (2026-11-18)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.
**Authority:** TS Developer Lab / Execution Engineering experimental only. `Product_authority=NONE / Product_effect=NONE`.
**Disposition:** `R007_B1_SEPARATED_CAPTURE_SYNTHETIC_3_OF_3_PASS / NO_MODEL_CALLS`.
**Does not certify:** OpenCode2 semantic reviewer, native provider/authenticated original, invoices, other users' local filesystem races or complete general-purpose runtime bridge.

## Frozen source

- `R007_B1_SEPARATED_CAPTURE_V1.ps1`, Git blob `bde1aeb9caf0819f0bc294e72786ce1c47ff7ca8`, first published at `a6b201e44128fb6e69b540b95961ed0a6d712e50`.
- Original selftest `R007_B1_SEPARATED_CAPTURE_SYNTHETIC_TEST_V1.ps1`, blob `878f31e95c1765ef0d11d006a51a0f84e2b4401c`, used a WindowsApps `pwsh.exe` alias with non-readable file: native V1 test stopped **before any capture directory was created**. Preserve V1 as an actual failed preflight, no replay.
- V2 corrected selftest `R007_B1_SEPARATED_CAPTURE_SYNTHETIC_TEST_V2.ps1`, blob `cb66566f159d4cc94009b47098c0b85296849082`, uses the true `$PSHOME/pwsh.exe` binary instead of the WindowsApps execution alias. Published at `5d816eb26e524b7d35b5c87ce1fc8b6bc3039de9`. Binary hash is checked at native run time.

## Exact native Orca delivery and terminal

- Notebook `DESKTOP-DJLBEQH`; isolated non-Product Orca worktree `ts-ee-oc2-r007-b1-file-config-20261118-001` (separate from historical A001).
- Visible Orca `02 · TS · Experiment` terminal: `term_c763c655-b52b-4c6a-ab04-de5cd2538e05`; incarnation `3128fc7e-f5ee-4f52-a6da-6bc0ac523f1c`.
- V2 single send request `1926b0bb-2084-4328-8da7-e03944f7a0da`; `accepted=true`, `replayed=false`. Provider reported delivery-observation unsupported; native terminal screen later confirmed actual markers. No second send for that attempt.
- Native PowerShell 7.7.0 present; test launched only local `pwsh.exe` synthetic subprocesses, no OpenCode2 or any model.
- Exact observed native markers:
```text
R007_CAPTURE_TEST_BEGIN
R007_CAPTURE_TEST_A001_PASS;STDOUT_BYTES=23;STDERR_BYTES=18
R007_CAPTURE_TEST_A002_NONZERO_EXIT_PASS
R007_CAPTURE_TEST_DUPLICATE_BLOCKED_PASS
R007_CAPTURE_TEST_TERMINAL_3_OF_3_PASS_NO_MODEL
```
- The source `Invoke-R007SeparatedCapture` creates exclusive attempt paths, writes stdout/stderr as separate raw `.NET` streams, fsyncs both files, computes their SHA-256, and writes a create-only fsynced terminal JSON receipt. It does not emit a semantic verdict or authenticate provider billing.

## Independent native read-only postconditions

Root: `%TEMP%/TS-EE-R007-CAPTURE-SYNTHETIC-001`. Six existing artifacts at the exact synthetic identities:

| Attempt | File | Bytes | SHA-256 |
|---|---|---:|---|
| `R007-B1-CAPTURE-TEST-A001` | `ORIGINAL.stdout` | 23 | `83B6D66389A4F2EB26EAD759BDC90134C300A381BBAEC1C871CE533B87F9C974` |
| A001 | `ORIGINAL.stderr` | 18 | `AF731CC96C5FD5375475AC4EE3330113BCA43D85EC52B8A5A85AEB3B38CB1B1D` |
| A001 | `CAPTURE.terminal.json` | 612 | `55958AFD47F1B9A79A2E0F295BF62BEA56D1715052B8878245D6E1EE8A73B81F` |
| `R007-B1-CAPTURE-TEST-A002` | `ORIGINAL.stdout` | 21 | `3F27EC6F53436CDE60A73576C5BF7C70FCB1AB3AB9E3E3E34B8768DE7F9E6053` |
| A002 | `ORIGINAL.stderr` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| A002 | `CAPTURE.terminal.json` | 612 | `2EF12949CBD13E8E97041B6749DAF0D1813CF17042B0BB320D240B8C79CEA6C5` |

Native receipt fields verified: A001 `exit=0/effect_state=CONFIRMED_EXECUTED`; A002 `exit=7/effect_state=CONFIRMED_EXECUTED`. Nonzero exit is not effect NONE. Duplicate A001 was rejected before any additional capture, as directly evidenced by the terminal marker.

## Boundary and next gate

**Qualified narrowly:** byte-separated, create-only and fsynced *synthetic* capture on this one notebook and Orca terminal. Native original-byte preservation is established for these subprocess outputs, not for an actual OpenCode2 provider JSONL yet.

**Still unqualified for B1 complete:** integrate trusted executable/package identity, effective file-based free-model permission admission, host-wide no-duplicate ledger, full immutable prompt/carrier binding and a native OpenCode2 subprocess under one reviewed runner; then one grouped independent source IR. No semantic model attempt is permitted by this synthetic PASS alone.

Developer widened free-model choice but no model was invoked; free quota is treated as eligibility to evaluate models after verification, not authorization to use paid balances or pay-as-you-go accounts.
