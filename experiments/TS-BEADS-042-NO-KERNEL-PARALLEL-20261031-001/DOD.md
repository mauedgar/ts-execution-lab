# Beads 042 — Decisive no-State-Kernel parallel workflow qualification

**Authority:** EXPERIMENTAL_CONTROL_ONLY; Product NONE. Original TaskCycles, canonical #35, acceptance, integration and Kernel retirement remain exclusively with Beta Control. Does not alter Product SOT or grant permission to migrate.

**Operation** `TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001`, one `ExecutionAttempt=TS-BEADS-042-ATTEMPT-001`, a frozen source and exactly one push-triggered GitHub Actions run. Only disposable local Git and embedded native Beads/Dolt. No old 028–041 effect rerun. Native Beads 1.3.1 and Dolt 2.2.0 binaries are SHA256 pinned. Source blob `native042.py@ba518e866b644378610e730574a3df840f75ecea`.

## Experimental architecture

Product-like synthetic **PARENT** → **JOIN** → **CHILD ALPHA + CHILD BETA** → **PREFLIGHT**, all five actual native Beads issues with blocking native dependencies and native readiness/close/history. No State Kernel library, no replacement state service, no new workflow journal. One trusted **coordinator** selects based on Beads `bd ready`, starts two distinct Python child processes concurrently, authenticates receipt identity/hash and closes the native Beads tasks. Disjoint worker-owned output directories. This is *real parallel subprocess execution*, but **synthetic work**, not two OpenCode/LLM provider executions or two Product TaskCycles. `trusted coordinator` is required to enforce authority and verify receipts; no claim Beads itself implements Developer approvals or provider idempotency.

## Prospectively frozen DoD

1. Fresh local Git without remotes, Beads version pinned; only preflight ready, then exactly two child issues ready and join/parent blocked.
2. Two **distinct OS subprocesses** running independent disjoint jobs concurrently, each writes its own deterministic effect and immutable identity-bound receipt. Prove actual execution overlap **>=100 ms** via monotonic clock.
3. Validate owner/attempt/workset and original SHA256 receipts; neither worker may touch the other output folder. No State Kernel imports and no separate homegrown durable task state.
4. Trusted coordinator records both verified receipts in native Beads issues, closes one child and proves join remains blocked, closes second then join ready, closes join then parent ready, closes parent; final `bd ready=[]` and all five native issues closed. Native history for both children has at least two entries.
5. Verify original result JSON, checks PASS, exact ExecutionAttempt/authority/source, original result SHA256; archive original logs/receipts and optional native store within one finite-retention artifact; no Product writes or provider effect.
6. Truthfully qualify limitations: native Beads 028 privileged bypass remains, original Kernel global hash-chain parity not demonstrated, providers without authoritative status cannot safely retry UNKNOWN, Developer/IR acceptance remains external, local synthetic subprocesses do not validate remote OpenCode/worktree actors.

**Decisive decision rule:**
- If all DoD pass, `GO_EXPERIMENTAL_WORK_GRAPH_PARALLEL_WITHOUT_KERNEL`, **not** product-ready to retire Kernel.
- If any test fails, `FAIL_CLOSED`; preserve original; no automatic rerun. The design should not be accepted as qualified for the user's requested purpose merely on paper.
- Product **NO-GO** if attempting to substitute *all* State Kernel and authority guarantees without an explicit Product revision of those invariants and a real writer boundary.
- Avoid inventing a new Kernel/scheduler; Beads handles work readiness, dependencies and task state; a narrow coordinator retains external authority and receipt checking.

**Stop:** This is the last bounded experimental qualification of parallelism/no Kernel unless a specific terminal finding requires a new distinct authorized repair candidate. Publication ≠ adoption. No Product issue/TaskCycle effects.
