# TS-BEADS-046 — Native Dolt backup remote handoff after host loss (prospective DoD)

Date: 2026-10-31. Authority: EXPERIMENTAL_CONTROL_ONLY. Product effect NONE.
Operation: TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001.
Producer ExecutionAttempt: TS-BEADS-046-A-ATTEMPT-001.
Consumer ExecutionAttempt: TS-BEADS-046-B-ATTEMPT-001.
Source Git subject: single push-triggered original run on branch experiment/beads-046-native-backup-failover-20261031-001, with frozen source and this DoD SHA checks before effects.
Writer owner A: GitHub-hosted ubuntu-24.04 producer isolated runner, own disposable embedded Beads/Dolt store.
Writer owner B: independent ubuntu-24.04 consumer runner, fresh workspace; never has original A workspace mounted.
Provider: GitHub Actions original immutable artifacts, native Beads 1.3.1, Dolt 2.2.0, hashes pinned from 042 and 045.
Dependencies: prior 045 PASS single-host SQL server (run 41177022889, exact commit aae4dabd9c2b6d37a24bba896d2eaa2199533287, original artifact 13032823741 sha256:07b70ea4902d4bfec9efdda08e939b3d753287a2d2b74c6a7e4fe93f38ee33f4), and DC044 distinct two-host remote READ_ONLY success run 41177310449. These are evidence only, not attempts to replay.
No new external SQL endpoint or secrets are available/authorized in this chat. This experiment qualifies a separately useful dependency: durable remote native backup and resumption from NONTERMINAL state across two distinct hosts. It is NOT a substitute for the proposed live shared remote SQL primary test.

## Bounded original execution
1. Host A freezes exact Git subject and binaries, initializes a synthetic five-issue Beads native graph on a disposable source worktree; no git remote; does not copy or load State Kernel.
2. Host A advances preflight and Alpha with a SHA256-anchored existing provider-original reference (045, READ-ONLY; not Alpha's effect), leaves Beta in_progress and Join/Parent blocked. No external provider dispatch.
3. Host A writes durable native Dolt backup via supported bd backup init/sync, packages only the backup and original manifest to GitHub Actions artifact. When A job ends, its local workspace/server is lost.
4. Host B is another independent runner. It verifies original producer SHA and manifest, creates fresh Beads store and restores native backup. It checks exact issue/dependency/history, verifies existing provider receipt with original GitHub run+artifact; no redispatch/no Product.
5. Host B completes synthetic Beta, then Join and Parent in native Beads dependency order; all five closed and ready empty; preserves final result/sha as another GitHub artifact.
6. Any failed precondition/test -> FAIL_CLOSED original. No auto retry of 001, no rewriting 042/045, no writes to any Git remote ref (especially refs/dolt/data).
7. No Product changes, no external costs or credentials. Review original FAILs separately. Cumulative evidence does not establish live remote SQL sharing, remote writer confinement, HA, true UNKNOWN effect reconciliation, migration, or Kernel Product deletion.

## Expected durable original receipts
A: ts-beads046-producer-<run_id> / BACKUP046.tar.gz, BACKUP_SHA256.txt, RESULT046_A.json, ORIGINAL_A_SHA256.txt.
B: ts-beads046-consumer-<run_id> / RESULT046_B.json, ORIGINAL_B_SHA256.txt.
Both jobs: one original GitHub Actions run, run_attempt=1, source original sha, unique attempt IDs.
Acceptance: PASS_REMOTE_NATIVE_BACKUP_NONTERMINAL_HOST_FAILOVER_WITH_LIMITATIONS only if all tests pass and B restored without A's local folder, with no new dispatch. Product effect NONE.
Separate next dependency for full goal: real stable remote SQL primary and 2 live host clients with TLS and scoped credential storage. Absent that, state remains LIVE_SQL_INTERHOST_BLOCKED, not GO.
