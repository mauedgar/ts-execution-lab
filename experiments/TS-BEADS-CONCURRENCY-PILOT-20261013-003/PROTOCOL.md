# TS — Beads Pilot 003 | Concurrent ingress qualification
Date: 2026-10-13
Status: EXPERIMENT_PROTOCOL_FROZEN; NOT_EXECUTED
Authority: NONE_PRODUCT
Experiment: TS-BEADS-CONCURRENCY-PILOT-20261013-003
Planned attempt: BEADS-CONCURRENCY-LOCAL-20261013-001
Owner: TS experimental Beads evaluation
Parent DoD: mauedgar/ts-execution-lab@e6a48ba7a4f39c4870f6bb4a4bbdd3984e348ca9:experiments/TS-BEADS-EVALUATION-CHARTER-20261013-001/EXPERIMENTAL-CHARTER-AND-DOD.md

## Exact boundary
Work only with synthetic records in a **new, unique** local Beads database under `%LOCALAPPDATA%/TS-Experiments/TS-BEADS-CONCURRENCY-PILOT-20261013-003` on `DESKTOP-3LJ0E54`. Reuse separately pinned local Beads v1.3.1 only after confirming its SHA-256 against preserved Pilot 001 receipt. Keep Pilot 001 and 002 data intact. No Product writes, active TaskCycles, GitHub Issues/Projects changes, MCP, new transport publisher or global binary installation. Any existing local attempt/result requires identity/effect reconciliation before a new run; no blind retry.

## Test cases
1. Precondition: verify host, previous installed binary identity, Pilot 001 PASS and Pilot 002 read-only PASS, a fresh experiment data directory, declared pinned Git script/manifest hashes and free disk above 1 GiB. Fail closed before any Beads write on mismatch.
2. Initialize a new isolated store. Create two different synthetic pipeline responsibilities A and B. Assign separate stable task identities. Two **independent OS processes** update only their own responsibility to `in_progress`.
3. Force the two workers to reach a rendezvous **after each independently observes that source S has no existing entry**. Release both at the same logical gate. Each attempts to create the same `SOURCE_REF=S` obligation. Record precheck counts, actual UTC start/end for both write intervals, process PIDs, CLI exit codes, created IDs and any DB lock errors. The barrier alone does not prove the two CLI writes overlapped; overlapping timestamps must be checked.
4. A distinct third process reads all records and exact source references, ensuring each unrelated responsibility remains in its expected state, collecting cardinality and issue identities. Do not infer readback from the writing processes' local variables.
5. Preserve the original execution receipt even if it reports duplicates, an error or `UNKNOWN`; do not repair by repeated create or destructive cleanup. Classify:
   - `PASS_ATOMIC_DEDUP`: real overlap, both operations accounted for, one source record, no corrupted state and proof that the single result is not just a failed/absent write.
   - `OBSERVED_DUPLICATES`: real overlap, two distinct records for one source; dedup safety not demonstrated.
   - `CONTENTION_OR_WRITE_FAILURE`: one or both writers fail; record whether state persisted without claiming atomic dedup.
   - `INCONCLUSIVE`: overlap not shown or independent readback incomplete.
   - `BLOCKED_PRECONDITION` / `UNKNOWN`: fail-closed before execution or uncertain effects.
6. Distinct source with same title is a separate control, covered by Pilot 002. It may be repeated here only if it adds evidence and must not be confused with the racing identical-origin case.

## Execution design (not yet materialized)
Use a single complete, reviewed, pinned PowerShell runner plus manifest in this experiment branch. Runner validates parser and identities, launches two isolated worker processes with a bounded test-specific rendezvous, records their raw outcomes, runs the read-only third process and writes a compact terminal receipt. No new generic scheduler, daemon, background wakeup or Product gate. Transport the already-built artifacts by the established Git/file mechanism; **Commander must not construct or upload scripts** and may only execute the already-materialized bounded command. Do not dispatch until the complete runner/manifest and local file binding are verified.

## Acceptance for this pilot
A reconciled, immutable original terminal receipt, demonstrable process independence, actual write interval overlap (or explicit inconclusive classification), separate responsibilities, exact source cardinality, reliable independent readback, and clear attribution of what Beads itself guarantees versus what consumer policy must enforce. **Duplicates or contention are valid research findings**, not a reason to repeat Product work. Evidence must be portable and explicitly state whether host-native Git Transport publication has been qualified (not established in pilots 001/002).

## Result interpretation
This tests a storage-race edge case, not two full AI agents and not safe multi-TaskCycle Product coordination. Findings inform a later synthetic interrupted-pipeline scenario and the capability/subsystem replacement assessment. Product adoption, State Kernel replacement and removal of existing code remain separately conditioned decisions.
