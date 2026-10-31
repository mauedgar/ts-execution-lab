# TS Beads 037 — Terminal native OS principal and guarded writer result

**Authority:** EXPERIMENTAL_CONTROL_ONLY / Product NONE. **Status:** `PASS_BOUNDED_SCOPED_UNPRIVILEGED_DENIAL_WITH_PRIVILEGED_BYPASS_OPEN / COMPLETE_WITH_LIMITATIONS`. Canonical Product issue #35 belongs solely to Beta Control. No attendance, TaskCycle, Phase2, Product integration.

## Original attempts, never replayed

1. `TS-BEADS-037-ATTEMPT-001`, source `0e0c0b86fa6342515de18f6cddc5284a08298660`, [Actions run 41172687235](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172687235), attempt 1, terminal FAILURE before Beads graph initialization: Dolt SQL child exited code 2. Failure artifact `13031681326`, ZIP `sha256:e2d550bb29ace2881f0cba4d682bec8e7c12e1c2daa7e961891d85afe776d9b6`. No writer/security verdict from 001. Suspected inaccessible scratch parent on runner, not conclusively identified from its redacted transcript.
2. `TS-BEADS-037-ATTEMPT-002`, new source `6ace605b344ec11e53c232b896eed0895a079063`, [Actions run 41172852201](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172852201), attempt 1, terminal SUCCESS; source `native037_002.py` `sha256` tracked by Git blob `7ac9471d434f0396f8baa4296abfba9d3c51cdfe`. Directory moved to unique 0755 `/tmp` scratch while private writer store/credential file retained 0700/0600.
3. [Original 002 artifact 13031456953](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172852201/artifacts/13031456953), ZIP `sha256:8cda5db5224055abe689a60cfd654a4a20792cc8ffa3b9b18f5494e6f166c7b1`, expiry `2026-11-30T05:30:36Z`; original `RESULT037.json` SHA-256 `f0f0a2206c1202a2a5adb713922c0604db4a310851d8841fdab49a73a229b28e`.

## Native findings

**27/27 checks PASS** using Beads v1.3.1 and Dolt v2.2.0 original pinned releases. Unique Unix UIDs for writer and reader, private writer directory, bearer token, authenticated Dolt SQL. Reader cannot read protected path or secret, cannot mutate via native direct `bd dep add`, independently start a `bd serve` against protected store, invoke privileged launcher, or access unauthenticated native HTTP read/write. The authorized writer applied real native `batchApply` with root expected revision, created the matching edge, rejected stale revision and a fresh Beads CLI `show`/ `ready` retrieved persistent state.

**Material boundary that remains:** the writer UID retains native `bd` and Dolt write capability outside `batchApply`. Prior 028 showed same-UID native CLI bypass; 035 guarded-path PASS did not remove it. The OS boundary is protective **only against separate unprivileged identities**. Never call it universal exclusive-writer or unconditionally READY for authoritative Product Beads.

No Product, shared Dolt, external provider effect, Beads adoption, new Kernel, privileged OS escape or real remote provider operation occurred.

**Next bounded work:** 038 native Beads UNKNOWN + external receipt and 039 original Product Recipe race semantic comparison. Independent of Beta Control, no blocking #35 by experimental status.
