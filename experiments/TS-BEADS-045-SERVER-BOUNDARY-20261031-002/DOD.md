# TS-BEADS-045-002 — corrected distinct candidate, prospective DoD

Operation: TS-BEADS-045-SERVER-BOUNDARY-20261031-002
ExecutionAttempt: TS-BEADS-045-ATTEMPT-002
Authority: EXPERIMENTAL_CONTROL_ONLY; Product NONE. Original experiment 042 and Beta/#35 unchanged.
Branch: experiment/beads-045-server-boundary-20261031-002
Source: experiments/TS-BEADS-045-SERVER-BOUNDARY-20261031-002/native045.py, Git blob f4515102d7e2c16357f90f50e8b7c5d35e7a37cf.
Original 001: GitHub Actions 41176871863, attempt 1, completed/failure. FAILED ORIGINAL preserved. Its SQL server ran, Beads initialized, then PyMySQL rejected the unescaped literal % in SQL username host. The artifact path also contained a malformed bash variable, causing no artifact. These are confirmed bounded fixture errors, NOT server/host-independence conclusions.
Repair: fresh candidate file escapes literal % in PyMySQL CREATE USER SQL; new unique operation/attempt; corrected workflow scratch path uses $GITHUB_RUN_ID. Original 001 never rerun or rewritten.
Native pins: Beads 1.3.1 sha256 3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c; Dolt 2.2.0 sha256 1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6.
Execution: one fresh isolated GitHub Actions Ubuntu runner, bounded 12 minutes, one push-triggered run, no auto retry; source and this DoD Git blobs pinned before dispatch.
No git remote inside test worktree; DO NOT touch shared repo refs/dolt/data. No Product, #35, Workstation or Kernel effects.
Expected original receipt: GitHub Actions run on 002 workflow push, artifact ts-beads045-002-original-<run_id> containing RESULT045.json ORIGINAL045.log DOD.md ORIGINAL_SHA256.txt.

Required tests:
1. Prove fresh isolated state, exact binary pins and no remote/synced Kernel.
2. Start Dolt server bound to 127.0.0.1, enforce root password; create read-only SQL principal that can SELECT but cannot UPDATE native issues.
3. Initialize native Beads against SQL server (not embedded work DB); prove all five synthetic preflight/alpha/beta/join/parent issues and dependent readiness.
4. Use two independent native Beads CLI subprocesses to update distinct child issues; reject read-only CLI update, close in native dependency order, verify history and final ready=[].
5. Restart server process and recover all native status/history on same runner. No Product equivalence or host failover asserted.
6. Preserve limitations and original results without secrets. If any test fails, record FAIL_CLOSED_ORIGINAL and stop; no automatic retry.

Acceptance ceiling: PASS_SINGLE_HOST_DOLT_SQL_SERVER_BOUNDARY_WITH_RESTART proves ONLY a prerequisite for future real interhost experiments; remote SQL endpoint and two separate hosts remain separately blocked/unproven.
