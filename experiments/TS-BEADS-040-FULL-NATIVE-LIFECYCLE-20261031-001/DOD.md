# Beads 040 — Full native lifecycle and provider-referenced dependency join

**Authority:** EXPERIMENTAL_CONTROL_ONLY. Product NONE, canonical #35 remains in Beta Control. Objective: **use actual Beads dependency graph, ready, create/update/close, native history and independent client readback** as work-state substrate in a disposable complete workflow. No new Kernel/scheduler or Product acceptance.

New ExecutionAttempt `TS-BEADS-040-ATTEMPT-001`, one original GitHub Actions source. Native Beads v1.3.1 archive `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`, Dolt embedded storage v2.2.0 environment; new worktree with no remote, no Product mutation, no model provider dispatch.

Frozen source `native040_full.py@a4e6038882922501303f3f6c6992fd89adfb77ed`. Extends prior original `TS-EE-LLM-BEADS-040` **as a new experiment** (does not reexecute that old attempt or carrier), preserving its original early ready checks and adding full lifecycle.

Provider reference: verified **read-only**, native GitHub Actions 039 run `41173329767`, head `4d32a170f6f8aa2cabb9c0d0915b6cd1a7798d10`, artifact `13031552292`, digest `sha256:96839db7c20212930ccb80a4147bb3c69f35d23ef70a65d909b58f8fff41593c`. `bd update` records this provider original reference in issue description, no provider effect repeated.

**DoD:** (1) fresh native `bd init`/three dependency edges: initial only preflight ready; (2) closing preflight unlocks two independent children, not join; (3) after one child closed join stays blocked; after both, join becomes sole ready; closing join ends `ready=[]`; (4) original verified provider receipt referenced and no redispatch; (5) `bd history` grows across native update/close, fresh `bd show` shows terminal state; (6) independent original Actions run and raw JSON/log/checksum artifact; (7) no Product authority/role acceptance inferred.

Success: `PASS_NATIVE_BEADS_END_TO_END_READY_HISTORY_AND_PROVIDER_REFERENCE` but **B-authoritative Product substitution is not qualified**: direct privileged writers can bypass guarded API (#028), native history differs from Kernel global event hash-chain, no intrinsic no-retry/Developer acceptance. Product #35 can proceed separately in Beta Control. All failures preserved; no blind rerun.
