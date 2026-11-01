# Provider contract — future runner

`Ts047bHostProvider` is the typed boundary. `WindowsTs047bHostProvider` contains the real Windows API/process/DPAPI/MySqlConnector adapter; `MockTs047bHostProvider` is test-only.

* Preflight calls only observations: host/owner/version/peer, integrity, prior receipt, canonical path/reparse/ACL, listener/Serve/Funnel, secret capability, connector and grammar evidence.
* `Apply` cannot use this build attempt. It additionally requires a distinct future attempt plus a matching explicit effect grant and source digest.
* Effects are ordered: CSPRNG → DPAPI+ACL → no-secret loopback config → one SQL process → recovery-admin before root removal → scoped accounts/grants → negative auth/postconditions.
* `OpenSql` and `ExecuteSqlSecret` use an in-memory MySqlConnector session and parameter, never a shell SQL client or credential command-line/environment variable. The current real adapter intentionally returns `VerifiedPinnedDolt=$false`; it fails closed until native Dolt 2.2.0 `help`/grammar evidence is captured under a separate effect grant.
* Once SQL start is attempted, any exception returns `UNKNOWN_OR_PARTIAL_PRESERVE_STATE`; retry, rollback and cleanup are forbidden. Serve/Funnel are never an Apply action in this runner.

The protected directory limits ordinary local access. A user with filesystem access sufficient to invoke `dolt sql` can bypass SQL grants; this candidate makes no contrary claim.
