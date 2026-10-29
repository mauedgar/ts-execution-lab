# Beads 034 — B-first deferred durable join of existing real provider effect

Authority: EXPERIMENTAL_CONTROL_ONLY. Operate a disposable Beads v1.3.1/Dolt v2.2.0 instance, no remotes, no Product writes, no shared Dolt ref writes. The previously executed 033 external provider attempt is terminal and **MUST NOT** be dispatched or repeated.

Provider execution to observe only:
- repo mauedgar/ts-execution-lab
- run 40930288498, attempt 1, job 123646594227, source eebf8e72b83df5aed61416ffc0fa81e84fdf55ea
- artifact 12921817863, name ts-beads-033-provider-attempt-001, SHA-256 ZIP 329d05a218ea04dd740ab1579aed31d00a3f110700670e4d380993a0bde98dc6
- request SHA-256 350fb2c516c5ae94cf34cac7c38f5ea10ef11e3d715bf35826dadbce25dfdfe2
- original ExecutionAttempt TS-BEADS-033-PROVIDER-20261029-001/ATTEMPT-001.

Run steps: start with an UNKNOWN/reconciliation_required Beads issue; refuse a would-be second attempt; terminate initial command process; fresh process independently read provider run/jobs/artifact and download ZIP receipt, fail closed on corrupted/incorrect native evidence; only then mutate native issue to CONFIRMED with exact external identity; independent fresh process verify current state, as-of UNKNOWN and history. Publish original result via established qualified TXT carrier format.

Constraints: A second experiment workflow run is permitted only for a mechanical/harness repair with a distinct source SHA; it must not create new provider artifacts or replay 033. Avoid claiming actual ACK-loss: 033 was a client-ACK-discard scenario. No Kernel equivalence, no global version claim, no Product adoption/migration. Explicitly record negative guards as caller policy rather than native Beads enforced security.

Source pins: Product tools@d4154bd43f26515c39a41be974e462a0c7406a2d, tree cbfb71ad8632047e8e64fe2665d8614d835a2c8b. Shared Dolt ref 1f72d68797114170a97fee27641858f2e55a4571. Parent 033 f888e594c205efc04a9fb6a6dd255c411675e0d7.
