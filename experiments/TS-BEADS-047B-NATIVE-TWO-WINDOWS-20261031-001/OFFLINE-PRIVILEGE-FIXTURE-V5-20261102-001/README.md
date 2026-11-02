# TS-BEADS 047B — V5 source repair after independent IR010

**Operation unchanged:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (experimental). **Source status:** `SOURCE_READY_FOR_INDEPENDENT_REVIEW / NOT_DISPATCHABLE / NO_SQL_EFFECT`. No Product TaskCycle, migration, SQL grant, acceptance or adoption is implied.

## Frozen predecessor and control
- V4R frozen: `mauedgar/ts-execution-lab@0d262c2987bd4a306cde4ed4c7486ab8a4d77205`.
- Original independent IR010 FAIL: `mauedgar/ts-execution-transport@d2e2bac3e1d8d7e0afbeb28b1ec4cf007708c6e3:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V4R-20261102-001/WEB_INLINE_IR010-SECURITY-V4R-20261102.md` blob `0e2ab950e68f62b5038650553ae2bdd07ebd605e`.
- No edit to V1/V2/V3/V4/V4R or prior reviews. No original attempt retried. No Commander semantic work.

## IR010 N001–N005 targeted repairs, pending independent disposition
- N001 BLOCKER: runner now uses built-in if/throw for file existence and Git blob integrity BEFORE `Import-Module`; no unbound exported guard is called before import.
- N002 BLOCKER: exactly two PowerShell arguments (`$Privilege $true`) are passed to ACL checker; separate source tests verify call arity rather than a substring.
- N003 BLOCKER: signed grant's sourceCommit is compared to the actual Git checkout HEAD, in addition to signed runner blob and grant/reconciliation subject agreement; checkout must be a recognizable Git working tree. This **is not** independent GitHub verification of an approved grant or off-host claim; source-only XFORM materialization lacking Git will fail closed, not bypass identity.
- N004 ADVISORY: append CHILD_AMBIGUOUS only if exit was not confirmed; preserve actual nonzero CHILD_EXIT and distinct effect uncertainty without automatically retrying.
- N005 ADVISORY: restore negative test's module Git blob pin; add PowerShell AST-based argument checks and module-bootstrap order checks plus Python source regression tests. Tests are source artifacts, **not** claimed executed Windows/PowerShell receipts.
- Existing V4R repairs preserved: owner/SYSTEM inheritable DACL on data/config; protected receipt created atomically with Win32 CreateFileW; local WriteThrough result log; JSON `-NoEnumerate`; bounded I/O; no kill/cleanup; `UNKNOWN_EFFECT` when stage is in flight; exact source pins. Native verification missing.

## Unresolved dependencies (no fabricated PASS)
**No competent issuer public key has been provisioned.** The source deliberately pins SHA256 to 64 zeroes and blocks SQL. A signed JSON boolean claiming registry observation/original reconciliation is insufficient proof: Control must independently observe authoritative provider CAS + original attempt, PID, receipts and UNKNOWN state, bind exact claim subject, and supply signed authority. The positive synthetic GitHub ref/CAS result is not real authority.

A separate specifically authorized **non-SQL host validation** is still necessary on Windows: PowerShell parse, Add-Type compile, guarded ACL/reparse negative tests with throwaway scratch objects, source hash, Tailscale version/Serve/Funnel/port inventory, bounded pipes, redaction. Native Dolt v2.2.0 `privileges.db`, JSON output and separate-process readback remain untested; executing that SQL requires another explicit one-time grant **after** host and source qualification.

Even successful offline persistence would not prove authenticated SQL denial, 2-host Beads ready/history continuity, outage fail closed, backup/restore, RPO/RTO or equivalence with the State Kernel. Preserve Product `State_Kernel.final_disposition=UNDECIDED`, #34 CLOSED_PASS and #35 H6 independence.

## Independent review request
Review this V5 exact immutable commit, all candidate files, tests, README and manifest; contrast every IR010 N001–N005, IR009 F001–F010 and above external limitations. Recompute SHA256/Git blob/bytes and inspect code rather than trust assertions. Report PASS_SOURCE_LIMITED, PASS_WITH_ADVISORIES or FAIL with exact source findings and unclosed empirical blockers. Never conflate source-level correction with zero remaining Product adoption blockers, SQL readiness or grant.
