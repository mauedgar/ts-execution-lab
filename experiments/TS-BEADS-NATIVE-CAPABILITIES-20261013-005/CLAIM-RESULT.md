# TS — Beads native claim qualification 005
Date: 2026-10-13
Status: OBSERVED_PASS_NATIVE_ATOMIC_CLAIM_ON_HOSTED_WINDOWS
Authority: NONE_PRODUCT / experiment only

## Subject and original outcome
- Test source: `mauedgar/ts-execution-lab@08d16f65a8683fbb7be1a89a662df5f27d29c566:.github/workflows/ts-beads-native-claim-race.yml`
- GitHub Actions run: https://github.com/mauedgar/ts-execution-lab/actions/runs/38453388657
- Run terminal: SUCCESS; job `115489756045`; not replayed.
- Environment: ephemeral Windows Server 2022 GitHub-hosted runner; Dolt 2.2.0 SQL server; Beads 1.3.1; both binaries' upstream release SHA256 checked.
- Runtime IDs: exact synthetic issue `ts-execution-lab-a9c31ab5`; no Product authority or TaskCycle effects.

Two independent Start-Job PowerShell processes with separate `BEADS_ACTOR` identities were released together against the same exact issue by `bd update <id> --claim --json`.

| Worker | PID | Actor | UTC start | UTC end | Exit | Observation |
|---|---:|---|---|---|---:|---|
| A | 5440 | claim-worker-A | 2026-10-13T19:15:40.6302216Z | 2026-10-13T19:15:40.9008066Z | 0 | Claim succeeded |
| B | 2212 | claim-worker-B | 2026-10-13T19:15:40.6510170Z | 2026-10-13T19:15:41.0027113Z | 1 | Explicit `issue already claimed by claim-worker-A` |

Both critical operation intervals overlapped. Independent third observer (same workflow; other actor identity) read back only one issue with `status=in_progress`, `assignee=claim-worker-A`. Provider trace `TS_NATIVE_CLAIM=PASS_ONE_WINNER_TWO_OVERLAPPING_PROCESSES`. The issue also reported `lease_expires_at=2026-10-13T19:20:41Z`, `heartbeat_at=2026-10-13T19:15:41Z`: liveness expiry, release and uncertain reclaims are **not** qualified here.

## Scope and candidate absorption
Native atomic claim is a candidate to **avoid implementing a bespoke work-item lease/claim mutex**, not to replace Product authority, selection, TaskCycle starting, exact effects or Git SOT. `claim` success on an operational issue does not authorize a Product lifecycle transition. This result is qualified only on the ephemeral hosted Actions Windows/Dolt binding, not the user's local server (not installed).

## Alternatives, important separation
GitHub Actions can execute bounded, portable clients while available. Hosted Actions storage is ephemeral: **a successful workflow run alone is not a durable continuously shared Beads inbox**. Operational cross-run state needs a verified Dolt backup/restore or remote durable store, plus exact identities and readback. Local embedded Beads is already qualified for sequential continuity and can remain a fallback; persistent remote Dolt server and a qualified single-writer ingress are possible alternatives. No default provider selection or Product installation follows.
