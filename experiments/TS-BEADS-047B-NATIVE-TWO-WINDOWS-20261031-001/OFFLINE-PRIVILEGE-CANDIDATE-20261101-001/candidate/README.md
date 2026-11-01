# Offline privilege bootstrap candidate

ExecutionAttempt: `TS-BEADS-047B-OFFLINE-PRIVILEGE-CANDIDATE-20261101-001`.

This is a future-only adapter. It is not a validation that Dolt 2.2.0 accepts the proposed global flags, performs `init`/offline `sql` against the same privilege store, or supports the SQL postconditions. No native executable is called by the included harness.

`OfflinePrivilegeBootstrap.psm1` uses .NET `ProcessStartInfo.ArgumentList` and redirected stdin in its production-native helper. The password is never placed in an argument, file, or environment variable. It uses CSPRNG plus DPAPI `CurrentUser`, requires precheck delegates with individual results, rejects native output containing protected input, applies a process timeout and process-tree kill, and stops before a server invocation.

`MockNativeHarness.ps1` is deterministic and uses only injected mock delegates. It emits a parser/mock receipt and verifies that it never requests `sql-server`.

## Security and feasibility status

**BLOCKED_OFFLINE_PRIVILEGE_FEASIBILITY / NO_GO for SQL_GO.** Native 2.2.0 behavior remains unverified: exact placement/support of the global flags for `dolt init` and `dolt sql`; whether offline CLI writes the supplied privilege file; actual root-account state; ACL/owner semantics; and whether CLI output can be proven not to disclose stdin SQL. The mock does not establish any of those facts. A future independent reviewer must execute native evidence separately before this code can be promoted.

No `dolt init`, `dolt sql`, `dolt sql-server`, authentication, passwords, network service, Beads, Serve, Funnel, Product, or repository publication was executed in this attempt.
