# TS-BEADS 047B V6P3R2 — F001 partial source-only review scope

**Existing operation:** TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001. **Authority:** EXPERIMENTAL_CONTROL_ONLY. **Product effects:** NONE.
**Exact repair intent:** IR015 blocker F001 in V6P3R1 (stale child PID reused when the next stage fails before a new PID is assigned).
**This is a PARTIAL SOURCE PATCH, NOT a complete V6P3R2 test candidate.**

## Frozen history and separation

- Original IR015 independent original FAIL_SOURCE: mauedgar/ts-execution-transport@849e47ac1d2c41e669799e24b044166d21aa536d:results/TS-BEADS-047B-V6P3R1-WEB_INLINE-IR015-20261102-001/ORIGINAL_REVIEW.md (blob d5ade5e903518fa2f8381f215e80f196ffdbd9f1). Original review found F001 and retained A001/A003 dynamic limitations and other runtime blockers.
- V6P3R1 frozen original: mauedgar/ts-execution-lab@fb9a010751d98790226e147e2b58b87d7f0851cb, tree 41386b66e3e1d2ed4b43cfbfe6785370bc332b17. Original Windows source-only run 41471315893 PASS, independent review FAIL_SOURCE.
- V6P3R2 partial branch experiment/ts-beads-047b-v6p3r2-pid-isolation-20261102-001. Module Security-047B-V6.psm1 retains blob 70f5bee86358cf48ac6cded50c619ce46fed8f42. Runner Invoke-047B-V6-Fixture.ps1 new blob c483edd310756097027c2f6c17e483eac69c9fb7, not a grant/issuer or runnable live candidate.
- The new runner separates historical Spawned from CurrentStageSpawned, CurrentStagePid, ChildStartAttempted, resets prior ChildProcessId at each stage, and uses stage PID only for CHILD_STARTED, CHILD_EXIT and CHILD_AMBIGUOUS. Start() is attempted after SPAWN_INTENT, no automatic Kill()/retry.
- GitHub's prior source publication tool blocked writing an updated effect-capable Start-047B-V6.ps1 launcher; **do not bypass/duplicate that rejected tool action**. The current candidate intentionally has NO launcher and NO effect manifest; it is not dispatchable for SQL, Beads, Product, or a full 047B native proof.

## Source-only negative validations

- Test-V6P3R2-StageIdentity-Synthetic.ps1: extract only three real function declarations via PowerShell AST; mock source IO and previous stage success with a synthetic PID, then force an OS Start() failure on a verified nonexistent path. Assert stage two PID null, historical spawned retained, stage count unchanged, start attempt marked, CHILD_AMBIGUOUS reconciled=false, no child/SQL effects.
- Test-V6P3R2-LoggerFailure-Synthetic.ps1: similar synthetic stage-one identity, and mock CHILD_AMBIGUOUS log failure; assert no inherited PID, StageInFlight and ChildEffectAmbiguous retained, no false reconciliation or test child.
- These tests are **synthetic source-level controls**, not real SQL or multi-host proof. They cannot establish durable external receipt recovery after actual host crash. Neither case authorizes a retry of original V6P2 PID 18796 or the native SQL fixture.
- Separate native hosted Windows runs have distinct frozen code subjects and original provider receipts. Their outcomes must be individually joined, not inferred from workflow dispatch.

## Reviewer acceptance boundary

A reviewer may conclude `F001_SOURCE_PATCH_PROVISIONALLY_QUALIFIED` ONLY for the isolated code path when both native negative tests PASS and independent code inspection finds no stale identity. **Do not claim `V6P3R2_ACCEPTED`, `PASS_FULL_CANDIDATE`, `NO_ADVISORIES`, `HOST_INDEPENDENCE_GO`, or acceptance of Live SQL/Beads**. The final code candidate requires a legitimate authorized source-development path to finish launcher, manifests, full source tests, an exact native no-effects proof and independent IR. No Product TaskCycle or Kernel adoption.

Original notebook V6P2 Commander PID tree 18796→11384→20888→23184 remains ABANDONED_UNRECONCILED_UNKNOWN. Kernel UNDECIDED; #34 CLOSED_PASS, #35 H6 separate; no SQL or Beads mutation, Tailscale Serve, backup/restore, acceptance or integration.
