# TS-BEADS-045 — Native Dolt SQL server boundary prerequisite (prospective DoD)

Authority: EXPERIMENTAL_CONTROL_ONLY; Product effects NONE. User authorization: 2026-10-31 TS-BEADS evaluate next dependency and adapt remote-Dolt recommendation. This is a NEW distinct experimental identity, not a retry or resurrection of 043/044 or 042.

Operation: TS-BEADS-045-SERVER-BOUNDARY-20261031-001
ExecutionAttempt: TS-BEADS-045-ATTEMPT-001
Branch: experiment/beads-045-server-boundary-20261031-001
Entry source: native045.py Git blob SHA pinned by workflow after publication.
Environment: single disposable GitHub-hosted Ubuntu runner, two separate native Beads client processes, Dolt SQL server bound exclusively to loopback; no other host, no Product, no shared Git refs.
Binaries: Beads 1.3.1 tar SHA256 3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c; Dolt 2.2.0 tar SHA256 1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6.
Remote Git: forbidden. Existing repo refs/dolt/data observed and MUST NOT be overwritten.
Expected durable receipt: GitHub Actions single original run from push of workflow ts-beads045-server-boundary.yml; artifact ts-beads045-original-<run_id>/RESULT045.json and ORIGINAL045.log, manifest SHA256. One execution only; no automatic retry.

Prerequisites and checks:
1. Fresh isolated no-remote workspace; exact pinned binaries and script blob; no State Kernel imported/copied.
2. SQL-server listener on 127.0.0.1 only; root authentication hardened with random secret not logged; reader SELECT allowed, direct SQL UPDATE forbidden.
3. Native Beads in server mode using external SQL backing, no embedded local work database; preflight -> alpha,beta -> join -> parent dependency sequence and readiness verified.
4. Two separate native Beads client subprocesses write distinct child issues through server; independently verify in_progress, then close and observe dependency readiness and native history.
5. Restricted SQL client cannot mutate by native bd CLI; restart SQL-server and recover all states from server's durable store, with ready=[].
6. Preserve factual limits: this does NOT prove real remote second host, durable hosted endpoint, recovery from total machine loss, writer bypass elimination, full Product audit equivalence, real remote OpenCode agents or an UNKNOWN provider effect.

Decision:
- PASS_SINGLE_HOST_DOLT_SQL_SERVER_BOUNDARY_WITH_RESTART only if all checks pass, with explicit NEXT_DEPENDENCY=INDEPENDENT_HOST_REMOTE_SQL_ENDPOINT_AND_CREDENTIALS.
- FAIL_CLOSED_ORIGINAL if any required precondition/check fails; preserve evidence without blind rerun. BLOCKED if provider/auth/network prerequisites fail before execution and record exact evidence.
- No new Kernel, scheduler, ledger or Product write. Reuse Beads/Dolt and GitHub native receipts. Any cross-host experiment is separately identified and never inferred from this one.
