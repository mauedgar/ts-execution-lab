# TS-BEADS 047B — V6 final source candidate for independent review

**Responsibility:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (same OPERATIONAL experiment). **Class:** EXPERIMENTAL_SOURCE_ONLY / NOT_DISPATCHABLE / NO_SQL_EFFECT. **Product authority:** NONE.

Frozen predecessors: V5 `mauedgar/ts-execution-lab@16f4aab38ba99f97f492cf663a0a28e58e132c6e`; original IR011 `mauedgar/ts-execution-transport@765132242f65bb752c890752603d3ca38fb46ded:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V5-20261102-001/WEB_INLINE_IR011-SECURITY-V5-20261102.md`, blob `9aafa33e1149b694af141a7b6800a52074ff63ee` (**FAIL**). No existing 047B attempt was rerun or cleaned. No prior candidate/IR overwritten.

## Targeted IR011 repairs (NOT an independent verdict)
- S001: all child PID state now uses `$script:ChildProcessId` rather than constant PowerShell `$PID`. The result still returns `pid` as a field; it no longer writes the automatic variable.
- S002: user-profile path in `Get-V6Root` is `$userProfilePath` instead of read-only `$HOME`.
- Additional prophylactic fix: `$script:LastExitCode` replaced with `$script:ChildExitCode` to avoid shadowing PowerShell's automatic `$LASTEXITCODE`.
- `tests/test_source_contract.py` now includes a case-insensitive protected-variable assignment regression check; `tests/Test-V6-ParserAndAst.ps1` adds `AssignmentStatementAst` screening. A generated AST script was corrected **before this candidate was frozen**. These tests are **not claimed to have been executed on Windows**, even though their source can be inspected and independently tested.
- V5 N001–N005 source fixes retained: bootstrap guarded with built-in throw before import, correct ACL parameter arity, signed grant sourceCommit compared against checked-out Git HEAD, no duplicate ambiguity after confirmed child exit, pinned negative trust-anchor test and parser/AST checks.

## Safety contract and remaining dependencies
No issuer key is provisioned (trust-key SHA256 remains 64 zeros). No signed experimental one-time SQL grant, no remotely authoritative exclusive live claim, and no original-attempt provider/PID/receipt reconciliation have been established. The separate positive synthetic GitHub ref CAS fixture is *not* an authority fence for SQL. Even a source-level PASS cannot authorize an SQL effect.

Native Windows tests still require exact host/runner preconditions and their own receipts: PowerShell direct preflight, parser/AST, C# Add-Type compile, protected creation ACL/reparse, process pipes/timeout, full Tailscale Serve/Funnel/socket/version inventory and no-effect negative signer test. A pinned Dolt v2.2.0 SQL privilege file/readback test requires **separate explicit, one-time SQL authority** afterward. A successful offline fixture would not establish remote authenticated denial or Beads graph/ready/history across two independent hosts.

This V6 is a source candidate for IR012, **not** a final integral Beta Run acceptance, SQL grant, Beads adoption or Kernel removal. Preserve `#34 CLOSED_PASS`, `#35 H6` without Beads, and `State_Kernel.final_disposition=UNDECIDED`. Future implementation needs exact Git source, qualified authority/claim, original receipts and negative/failure scenarios before any Product decision.
