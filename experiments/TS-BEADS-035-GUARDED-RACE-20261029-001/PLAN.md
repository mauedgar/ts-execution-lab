# TS Beads 035 — bounded real concurrent guarded causal mutation

Authority: EXPERIMENTAL_CONTROL_ONLY. The user authorizes priority 035, not Product migration or privileged-writer bypass.

## Immutable baseline
- Product SOT: `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`, SOT blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`.
- Shared Dolt: `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.
- Parent experiment 034 terminal `1c8509b4fa47d36609f0047c3ceaf8240e3732fb`. DO NOT REPLAY 033/034.
- 028 terminal `9e8016004ef5d3ca74abd67914d8e1a03ffcd851` already demonstrated privileged alternate writer bypass with direct `bd dep add` and direct `bd serve`. Do NOT repeat or evade existing safety controls.
- 018 established stale sequential `expected_version` batch rollback, but **not a genuine simultaneous cross-process race**.

## Distinct 035 question
Under a single disposable Beads service and two cooperating unprivileged caller processes, does native `batchApply` with the **same observed root revision** admit at most one competing `update root(expected_version)+dep_add` transaction? Is rejected writer's edge absent? Repeat bounded races, check exact identities, single winning edge, root version change and historical persistence. No attempt to qualify universal exclusivity, OS privilege boundaries, native ACL security or full Kernel invariants.

## Mechanics and success criterion
- Beads `v1.3.1` / Dolt `v2.2.0`, pinned archives and SHA-256.
- Isolated disposable Git lab with **no remote**, Beads embedded Dolt, auto-push off. Run one loopback Beads server with generated local bearer token.
- Create one native root and two unique native child issues per round. Both independently forked worker processes receive the exact same server-minted root revision and wait on a release barrier; send native HTTP batchApply in parallel with distinct targets, no direct Dolt/CLI writes from workers.
- PASS only if exactly one worker commits, the other is rejected; root metadata identifies winner, exactly winner's graph edge exists, losing edge absent; a later fresh guarded request with stale token is rejected, and end-of-experiment CLI reload confirms the exact graph without any remote.
- Every check is original runner evidence; publish only after PASS through existing `IR-TXT-CARRIER/1` project/verify/extract.
- If both commit or no one commits, preserve FAIL and investigate; never relaunch same workflow attempt, only distinct source/attempt if safe and justified.
- **Limit:** same native server, clients authorized to submit guarded batches, no arbitrary privileged direct CLI access; 028's universal bypass remains open, no Product authority, adoption or migration.
