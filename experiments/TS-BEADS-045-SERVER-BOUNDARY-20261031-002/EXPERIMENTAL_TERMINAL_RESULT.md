# TS-BEADS-045 — Terminal original result, server boundary prerequisite

Date: 2026-10-31. Responsibility: TS-BEADS / TS Execution Engineering. Authority: EXPERIMENTAL_CONTROL_ONLY. Product effect: NONE.
Final bounded verdict: PASS_SINGLE_HOST_DOLT_SQL_SERVER_BOUNDARY_WITH_RESTART / COMPLETE_WITH_LIMITATIONS.
Real interhost independence verdict: INCOMPLETE / NOT_TESTED. Do not equate server mode with a remote server on a second host.

## Original identity and reconciliation
Original corrected operation: TS-BEADS-045-SERVER-BOUNDARY-20261031-002.
ExecutionAttempt: TS-BEADS-045-ATTEMPT-002.
Frozen execution Git subject: mauedgar/ts-execution-lab@aae4dabd9c2b6d37a24bba896d2eaa2199533287; branch experiment/beads-045-server-boundary-20261031-002.
Frozen code: experiments/TS-BEADS-045-SERVER-BOUNDARY-20261031-002/native045.py blob f4515102d7e2c16357f90f50e8b7c5d35e7a37cf.
Frozen DoD: experiments/TS-BEADS-045-SERVER-BOUNDARY-20261031-002/DOD.md blob dc51f96fe5af2a202d42ab96797c35dd885c19de.
Original GitHub Actions run: https://github.com/mauedgar/ts-execution-lab/actions/runs/41177022889; run_attempt 1, completed/success, job 124466565610 completed/success.
Original native artifact: https://github.com/mauedgar/ts-execution-lab/actions/runs/41177022889/artifacts/13032823741; original ZIP SHA256 07b70ea4902d4bfec9efdda08e939b3d753287a2d2b74c6a7e4fe93f38ee33f4; provider retention to 2026-11-30T06:32:36Z.
RESULT045.json SHA256 b66710d11cb978306c5668b5819851d6a6a4462ef8d88cdf380df2b2a9d018c9. Verified the original ZIP directly: the ORIGINAL_SHA256.txt manifest matches all entries (RESULT045.json, ORIGINAL045.log, DOD.md). Native original result shows 24/24 checks PASS, 2 separate Beads CLI subprocesses, one GitHub runner, external hosts 0, 2 server starts, 5 native Beads issues, Kernel unused. No re-dispatch.

Historical original 001 PRESERVED: execution subject bc909b4a868b0927944ec6684319fb0d219ec109, ExecutionAttempt TS-BEADS-045-ATTEMPT-001, original run https://github.com/mauedgar/ts-execution-lab/actions/runs/41176871863, run_attempt 1 completed/failure, job 124466136294. The initial server/bootstrap proceeded until PyMySQL SQL CREATE USER with unescaped % triggered ValueError; malformed workflow scratch path prevented artifact collection. Independently corrected 002 source/DoD/workflow produced the PASS above; neither effect nor ID of 001 was retried. Historical 028–042 remain untouched.

## Verified scope, not inferred
1. Fresh no-remote disposable worktree; Beads 1.3.1 and Dolt 2.2.0 original SHA256 pins, no state-kernel directory or embedded work DB.
2. Real Dolt SQL server bound to loopback, root password hardened. A restricted SQL user reads issues but cannot mutate via SQL or native Beads CLI.
3. Native five-issue graph: preflight -> alpha/beta -> join -> parent, correctly gated by Beads ready, with two distinct native CLI processes mutating disjoint child issues.
4. Native history survived server shutdown/restart with final ready=[] and all issues closed. Credentials not published in artifact.
5. No write to Git remote, and in particular no effect on the pre-existing shared lab refs/dolt/data (Git object 1f72d68797114170a97fee27641858f2e55a4571 observed). No Product writes or tests.

This is an actual **server-mode prerequisite** with 24/24 PASS, NOT proof of two machines, remotely hosted persistence, host A loss recovery, SQL multi-host networking/TLS, service HA or real provider UNKNOWN reconciliation. It cannot authorize Product migration.

## Product capability absorption matrix, read-only
Product SOT reobserved: mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909, tree e6be65e0c3d9aca074218b2fff92e6d42fc76141; docs/SOURCE_OF_TRUTH.md blob dd8d34a7e3ef3094805d014f9e59741d2c553957 and docs/architecture-knowledge-ownership-baseline.md blob 330fdc82f75e1126939cd718c1facb28abe00c62. Its State Kernel final disposition remains UNDECIDED; implementation refactor, migration and deletion are not authorized by this line.

| Existing Product code | Footprint | Work that Beads/provider could absorb | What stays blocked |
| --- | --- | --- | --- |
| src/state-kernel-v0/* (four files) | 36,715 bytes | Some issue/work-state CRUD and dependency readiness | Stable Product authority, semantic states and global event hash-chain/revision/HEAD replay not proven equivalent |
| src/operational-spine-v0/state-kernel-adapter.js | 12,020 bytes | Potential simplification of work-state and readiness binding | Active consumer for Operation/ExecutionAttempt/UNKNOWN and authority, must retain equivalent behavior |
| src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js | 36,279 bytes | Native Beads dependency join can replace a portion of mechanical readiness checks | Product independent review/Developer acceptance/Phase2/canonical close remain independently authorized |
| src/operational-spine-v0/execution-record-store.js | 3,510 bytes, outside the prior 85,014 | Immutable plans/receipts potentially hosted via GitHub Actions/Transport instead of workstation-local files | Must verify exact identity, no-replay, retention and consumer compatibility |
| src/operational-spine-v0/recipes/render-current-state.js | 1,964 bytes, outside the prior 85,014 | Derived read-only status projection from Beads/remote state | Recipe receipt and authority/read model retained until consumer test |

36,715 + 12,020 + 36,279 = 85,014 bytes already measured in 036. These bytes are the currently present source footprint, NOT eliminable bytes. Product bytes actually deleted = 0. Distinguish work-status duplication from essential Product state and policy. Do not add a new Kernel, scheduler, ledger or redundant tracker.

## Remote-host continuation dependency (NOT YET EXECUTED)
Select topology A: one durable remote Dolt SQL **primary** on a host independent of two ephemeral runners, with private networking/TLS and distinct least-privileged credentials. This requires an explicitly configured external endpoint and a secret provisioning mechanism; neither is evidenced by this run. Do not infer that an ephemeral loopback SQL server has solved host independence.

Next exact bounded DoD:
1. Freeze external remote endpoint identity/TLS certificate and scoped credentials (secret in provider storage, never commit), two independent runner IDs and no Kernel folder, and immutable Git subject.
2. Host A creates Beads parent, 2 children and provider receipt reference; Host B starts from clean workspace and reads same live SQL database without a copied Dolt store or original workstation.
3. Simulate loss of A: B joins using original provider status+receipt, never re-dispatches UNKNOWN blindly; run a truly distinct host with no A filesystem mount.
4. Restrict native alternate write paths and SQL accounts, fail closed on stale reads/network partition/revoked credentials; capture backup/restore to third environment with verifiable SHA and finite RPO/RTO.
5. Quantify Product code elimination only by a separately authorized exact candidate and IR/acceptance path; zero Product writes in LAB.

Decision: GO for native SQL-server mode as a **technical prerequisite**, INCOMPLETE for remote host-independence, NO-GO for automatic Kernel retirement. Stop this attempt; never rerun 001 or 002. #35/Beta Control not affected.
