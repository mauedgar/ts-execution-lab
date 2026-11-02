# TS-BEADS 047B — A002 controlled controller-loss / durable identity experiment

**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, EXPERIMENTAL_CONTROL_ONLY. This document is a lab evidence map, NOT Product state/authority, a new TaskCycle, a retry, a grant, or a new scheduler.

## Current development stage (2026-11-02)

- F001 previous-child PID attribution fixed in the **partial** V6P3R2 runner blob `c483edd310756097027c2f6c17e483eac69c9fb7`, independent IR016 `F001_PATCH_SOURCE_PASS_LIMITED`, five advisories. Provider synthetic attempts `41502588386`, `41502911941` PASS; post-Start benign `whoami.exe` case `41506347473` PASS source-only after IR016. No new complete executable candidate, no launcher/manifest; a tool security restriction previously blocked effect-capable launcher publication and must not be bypassed.
- This **A002 experiment is independent** of that blocked live SQL launcher. Work on a fresh branch `experiment/ts-beads-047b-a002-controller-exit-20261102-001`; own scoped source `A002-CONTROLLER-LOSS-20261102-001/Test-A002-ControllerLoss.ps1`, frozen Git blob `54ee953e99470df1e89b871c471718d17ab09799`, commit `c7845af599d0b9152d71c3e363cedeb8b6646371`.
- Source-only hosted Windows run `41528367706` attempt 1; trigger commit `42b4d611eeb2002380faf96bcd6f7c280f0ca48c`, workflow `.github/workflows/ts-beads047b-a002-controller-exit.yml`; checkout exact frozen source. Provider terminal result must be separately observed and joined; no PASS inferred from dispatch.

## Controlled cases / safety fence

- `Recorded`: dedicated ephemeral controller writes a new `SPAWN_INTENT`, then starts a benign local `pwsh` child (the same script's `Child` role). Child independently flushes a new `CHILD_SELF_ATTESTED` file recording its own PID/start UTC and a fresh nonce. Controller records `CHILD_STARTED` with PID/start UTC and flushes both stream + FS before deliberately exiting through `[Environment]::Exit(73)` (bypasses caller's finally).
- `MissingPid`: controller writes and flushes `SPAWN_INTENT`, starts the same benign child, then exits immediately **without a durable PID record**. Child separately persists its witness. Original journal remains insufficient for declaring no process. A separate observer matches the nonce but returns `ORIGINAL_PID_ABSENT_EXTERNAL_JOIN_REQUIRED_NO_RETRY`, never interprets no PID as no effect.
- The observer is a new distinct pwsh process after controller exit. It validates flush-persisted JSONL, nonce, PID and process start time for the recorded case; no PID-only equivalence or assumed no effects. `[Environment]::Exit(73)` stops only its own disposable test producer, **not** the user's old notebook PID 18796 or any unrelated process. Hosted Actions scratch requires fresh `RUNNER_TEMP` path per case; no access to Product paths, Dolt, SQL, Beads or Tailnet.
- **Evidence scope if tests PASS:** limited `SAME_HOST_FLUSHED_FILE_ONLY`, with actual independent process exit and benign subprocess. This is NOT off-host durability, actual host power loss, atomic cross-host external CAS, exactly-once SQL, signed issuer, terminal join of V6P2, backup/restore, or a demonstration that remote Beads state survives notebook loss. Do not upgrade DoD or Product.

## Explicit remaining 047B phases

1. **Source/fencing preflight (current):** F001 patch and A002 same-host controller-loss evidence; independent reviews/advisories; no active live effect authority. V6P2 original notebook process `18796→11384→20888→23184` still `ABANDONED_UNRECONCILED_UNKNOWN` and may not be killed/retried blindly.
2. **Secure native provisioning (not started):** competent bounded grants, correct authenticating issuer, fresh independent off-host CAS and original receipts, private listener only and authorization negatives. Blocked until product-independent owner and old effects are reconciled.
3. **Live two-host Beads state and failure exercise (not started):** native notebook server plus desktop peer, 5-issue graph, concurrent dependency transitions, service vs CLI outage differentiation, no local Kernel fallback, exact identity/effect reconciliation.
4. **Restore/backup and adoption decision (not started):** independent backup cut, restore test, security/owner checks, measure cost/reliability, compare feature coverage vs custom Kernel; require separate Product authority before integration/removal. No new TaskCycle created by this plan.

**Overall verdict:** `HOST_INDEPENDENCE_INCOMPLETE`; `NO_GO_EFFECT`; Product #34 `CLOSED_PASS`, #35 H6 Attendance separate and no Beads dependency; State Kernel architectural disposition `UNDECIDED`.
