# DC043 — Prospective experimental DoD

Identity: `TS-DISTRIBUTED-CONTROL-001-HOST-FAILOVER-20261031-001`; authority `EXPERIMENTAL_CONTROL_ONLY`.
Scope: lab only; `Product NONE`, `#35 NONE`, `TC_INIT NONE`; no shared `refs/dolt/data` mutation.
Frozen source: `host_failover043.py` blob `a77f845fc545c7b729508a4508010f4ff6613870`.
Source baseline: `ts-execution-lab@7b0fb033e9aa9a1e3d140622209ed427d77b1f12`.
Product SOT read-only cutoff `tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`.

## Original attempt and expected behavior

One workflow push, run_attempt 1, on the isolated branch. A runs on an Ubuntu GitHub Actions runner, opens a native Beads 1.3.1 / Dolt 2.2.0 workgraph (preflight→effect→join→parent), captures effect as UNKNOWN under stable `TS-DC043-EXTERNAL-EFFECT-ATTEMPT-001` and publishes its native store as an immutable 30-day GitHub Actions artifact. Then A publishes **exactly one** synthetic external effect as a second GitHub Actions artifact, and deliberately fails **after publication** to simulate lost acknowledgement. Its job failure is required and not to be re-run.

B runs in a separate clean runner despite A's failure, downloads both remote originals, validates hashes/identity, checks GitHub artifact IDs and uniqueness independently, opens native Beads/Dolt history from the store, observes original UNKNOWN, and then marks CONFIRMED from the external provider receipt. It closes effect→join→parent, proves zero new dispatches, and publishes RESULT043.json plus the terminal native store with hashes.

## Pass criteria

1. `producer` job failed at the explicit ACK-loss injection, *after* both artifact publication steps succeeded.
2. `consumer` job completed/success on different GitHub runner; original run_attempt=1 and exact source/code blob verified.
3. Two remote artifact names are unique; native store checksum and exact effect payload SHA-256 verified; provider artifact numeric ID present.
4. Original Beads effect not closed and its description contains original identity and UNKNOWN before B reconciliation.
5. Parent/join initially blocked, then graph closes in sequence after confirmation with native history preserved and `ready=[]`.
6. `provider_redispatch_count=0`, one synthetic external publication; no new attempt; no State Kernel or Product writes.

Fail closed for any other producer failure, missing/duplicate artifact, inconclusive provider identity, hash mismatch, incompatible Beads version, or incorrect graph state. No automatic retry.

## Qualification ceiling

PASS here proves bounded **independent remote-artifact recovery**, not native live Dolt Git remote replication, production HA, real host power loss, multiple trustworthy writers, long-term backup, privileged-writer confinement, or canonical Product Kernel/TC Core equivalence. It deliberately uses immutable GitHub Actions artifacts (retention) as the recovery substrate, not a new custom ledger. A separate exact remote-native Dolt test would still be needed before `HOST_INDEPENDENCE_GO` for the target live architecture.

No Product repo changes, no experiment branch merge, no #35 start.