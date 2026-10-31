# TS EE LLM048 — Fail-closed boundary for a non-idempotent provider

**Authority:** TS_EXECUTION_ENGINEERING / EXPERIMENTAL_CONTROL_ONLY; Tecnotron Product, Upper LC #34/#35, Beads adoption, reviewer acceptance, Phase 2, and canonical schedulers NONE. No real external effects.

## Frozen original source and owner

- Operation: `TS-EE-LLM-048-NONIDEMPOTENT-20261030-001`
- Unique ExecutionAttempt: `TS-EE-LLM-048-ATTEMPT-001`, writer only disposable Actions `RUNNER_TEMP/ts-ee-llm048-$GITHUB_RUN_ID`, original receipt `RESULT048.json` and original provider/consumer SQLite databases and logs, expected hash emitted by runner.
- `provider048.py@331e3f84993a120d355273d16a2f37aa3ebdbebc`
- `consumer048.py@aa08297e4e9f6cd4ac02821222c242135293b493`
- `test048.py@d7e1233f3223c77efa23ce87757b455fdb2b2b5b`
- Every source blob/DoD frozen before original one-shot GitHub Actions dispatch. Run attempt must be exactly 1; no replay or automatic repair.

## Negative capability and invariant

Provider: separate Python HTTP process bound to 127.0.0.1, non-idempotent by deliberate construction. Provider table uses auto-increment event ID, **not a UNIQUE attempt ID**; submitting same attempt twice directly produces **two durable effects and two different receipts**. Provider GET status returns HTTP 405; no authoritative effects query is exposed. For transport faults, it can close the HTTP connection after effect commit or before commit, or exit after commit before ACK.

Consumer: distinct Python process with its own SQLite `attempts` primary key, durable `SEND_STARTED` record committed in a `BEGIN IMMEDIATE` transaction **before first HTTP send**. Every subsequent request for the same attempt ID is blocked or returns its already-durable ACK locally; no second POST. Mismatched subject/owner is BLOCK_IDENTITY before network. ACK loss yields persistent UNKNOWN. No provider probing, transport retry or forced replay. A synthetic direct bypass is used solely for the adversarial test.

## Prospective nine-case DoD

1. Provider commits then drops TCP ACK. Client records UNKNOWN; new client process **blocks** repeat and cannot consult provider (GET=405), effect count remains one when observed by test-only DB inspector.
2. Provider drops connection **before commit**. Client sees indistinguishable UNKNOWN and still blocks repeat. Effect count zero; deliberate false negative prevents unsafe automatic retry.
3. Provider process actually crashes after commit, before ACK. New provider and consumer processes preserve UNKNOWN and block same attempt, one effect.
4. Successful ACK committed by client: repeat gives local NO_RETRY_CONFIRMED without new POST, one effect.
5. Client receives ACK but discards it deliberately: UNKNOWN persists, no repeat, one effect.
6. Attempt ID with changed owner fails BLOCK_IDENTITY locally, no extra HTTP effect.
7. Consumer reserves attempt and exits **before any POST**: later run cannot infer no effect, blocks repeat, provider has zero effect.
8. Two concurrent consumer processes use the same journal/attempt: only one is allowed to submit, one provider effect; no duplicate even under lock competition.
9. Bypass client and deliberately POST same attempt twice directly to provider: **two distinct persisted effects and distinct receipts**, establishing that the provider offers no native idempotency. Test-only bypass, never claimed as safe Product retry.

Each case has a separate DB/HTTP provider and independent consumer processes; test-only SQLite inspection verifies effect counts, provider and consumer PRAGMA integrity checks. No repeated execution of the original attempt. Native test runner must return 9/9 success, no ERROR/FAIL, exact original result SHA-256, raw SQLite and logs artifact (including test-only duplication case). Distinguish test-authorized direct duplicate from a forbidden autonomous retry.

## Limits / stop

This experiment qualifies **a fail-closed local policy**, not exactly-once against a real provider. It deliberately trades liveness for safety when the ACK is ambiguous. SQLite WAL/synchronous FULL does not establish power-cut durability. No external network partition, remote LLM API, authenticated TLS, multi-host consensus, privileged writer containment, or Product binding. If the provider lacks both native idempotency and status/receipt lookup, reconciliation of UNKNOWN is **not automatically solvable**; require external competent evidence/decision, never assume absence means safe retry.

Final semantic disposition `PASS_BOUNDED_FAIL_CLOSED_UNKNOWN / COMPLETE_WITH_LIMITATIONS` only if every assertion passes; otherwise FAIL_CLOSED with original receipts. Publication does not authorize Product adoption.
