# TS-BEADS — Host independence: research disposition 001

Date: 2026-10-31. Authority: EXPERIMENTAL_CONTROL_ONLY. Product effects: NONE.
Origin: ts-execution-transport@e5ad75510a5ed49a30c0d21a05e68fa8a60d1dd6:handoffs/TS-BEADS-HOST-INDEPENDENCE-20261031-001/HANDOFF.md
Prior terminal: ts-execution-lab@7b0fb033e9aa9a1e3d140622209ed427d77b1f12:experiments/TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md
Classification: RESEARCH_ONLY / INTERHOST_EMPIRICAL_INCOMPLETE. No 043/044 receipts verified; no repeat or retry.

## Goal
Reconstruct and continue work from an unrelated host without the original workstation or any copied State Kernel directory. Temporary worktrees are execution surfaces, never the only operational SOT. Absorb custom modules, not create a replacement kernel, tracker, ledger or scheduler.

## External technology evidence
- Beads documentation (steveyegge/beads docs/DOLT.md, docs/FAQ.md): Dolt embedded and server modes; remote push/pull; bootstrap from git remote refs/dolt/data; native Dolt backup/restore. Verify CLI/version against pinned executable before executing a test. Documentation references found: https://github.com/steveyegge/beads/blob/main/docs/DOLT.md and https://github.com/steveyegge/beads/blob/main/docs/FAQ.md
- Dolt docs: remotes and versioned snapshots https://www.dolthub.com/docs/sql-reference/version-control/remotes/ ; replication https://www.dolthub.com/docs/sql-reference/server/replication/ ; backups https://www.dolthub.com/docs/sql-reference/server/backups/
- Dolt documents no general OLTP multi-primary solution; remote replication and SQL-server concurrency are distinct. Hosted backup is automatic; self-hosted backup and restore must be operated and tested.

## Option ranking (NOT experimental pass)
A. One managed/remote Dolt SQL primary; Beads clients on two independent runners; strict writer principal and read-only actor principals; provider-native immutable receipts. Best candidate for shared live state, but requires server lifecycle, auth/network, backups and recovery tests. Product adoption not granted.
B. Beads embedded local per runner + Dolt remote push/pull/ref synchronization; best low-ops remote persistence and cold bootstrap; NOT automatically a single serializable shared scheduler or live concurrent writer state. Avoid multi-primary assumptions.
C. Self-hosted Dolt primary plus backups/replicas; greater operations/credential burden, potentially needed only if A unsuitable.
D. GitHub/Transport-only receipts plus a Beads state projection: durable evidence but not proven as a single native shared write-state; NOT equivalent to A.

## Proposed empirical interhost DoD; NOT executed
1. Freeze exact Beads/Dolt CLI versions, Git subject, two independent hosted runner identities, policy and output hashes. Original host A creates parent, 2 children, dependencies. No Kernel files copied.
2. Remote database authoritative; host B starts from fresh workspace and independently obtains correct issue graph/history/ready; writes disjoint child as restricted principal, with control-only parent/join. Distinguish remote live SQL from pull-based bootstrap.
3. Kill host A after a provider dispatch; host B reopens original remote state, retrieves provider run and exact receipt, safely classifies UNKNOWN without a replay, joins and closes.
4. Negative tests: unauthorized writer cannot mutate via CLI, direct SQL or alternative server; expected-revision conflict fails closed; credential revocation, network partition and stale reads fail conservatively.
5. Point-in-time backup/restore on a third clean environment; verify issue history/HEAD, receipt references, hash consistency. Quantify RPO/RTO experimentally (not assume zero).
6. Compare concrete custom Product modules by ownership and invariant: graph/status/ready/parent/join are candidates to absorb; receipt storage remains native external GitHub; authority/Developer/IR/retry rules remain outside Beads; hash-chain/global revision and trusted writer cannot be removed without competent Product equivalence decision. Measure actual deleted bytes only after a scoped candidate, not theoretical savings.

## Capability status
Work graph/dependencies/ready/parent/join: GO_EXPERIMENTAL from 042, within one runner.
Portable native store to another runner: GO limited from 041 via artifact transport; not live remote interhost coordination.
Remote DB host independence: INCOMPLETE; technology supports plausible route, no original two-host failure/recovery receipt here.
Eliminate Product Kernel or audit modules: NO-GO automatically; 0 Product bytes removed.
Eliminate custom work-state kernel in an isolated Beads-first flow: GO_EXPERIMENTAL from 042.

## Next dependency
A fresh, bounded, separately identified interhost experiment must select A or B with two real independent execution environments, server/remotes, isolated credentials, deadline and immutable receipts before dispatch. This research note DOES NOT start an ExecutionAttempt, does not change Beta Control, #35, Tecnotron Product or FitFlow. Historical 028–042 effects remain untouched.
