# H6 Attendance — Control planning interface V0 (frozen for H6 preparation)

Status: `CONTROL_PLANNING_INTERFACE_FROZEN_V0`, **not** an accepted Product implementation, TASK, initialized TaskCycle, Developer grant, independent review, or Phase 2.
Owner: TECNOTRON_BETA_RUN_001 Product Control, bounded to issue mauedgar/tecnotron-ai#35.
Responsibility: `ATTENDANCE_STANDALONE_B_FIRST_PILOT_001`.
Baseline provenance: greenfield relative to `mauedgar/ts-execution-lab:main@e6562d5d4289978c28623927877cc8e1d0c74530`, tree `e7802bdc4e12c2e41f11d6407a9be13082449260`. No Attendance source or original 043 receipt has been qualified as portable Product baseline.
This file is a read-only shared interface for the two prospective children. Changing it requires a separate Control disposition and re-freeze of both children; it is not editable in either child's write-set.

## Boundary and minimal runtime

- Standalone Tecnotron Attendance delivery pilot, **not FitFlow** and not a migration of FitFlow.
- Python 3.12 standard-library callable service interface + SQLite file database owned by the domain child. Operator child supplies a CLI consumer. No HTTP server, authentication service, tenancy, payroll, identity enrollment, external integration or background scheduler in V0.
- Domain records must never be stored in Beads/Dolt, a State Kernel, FitFlow PostgreSQL, Git, or the service contract file. Configurable database file path is provided by the caller; no committed runtime DB.
- A subject is an opaque identifier, not a person's name or proof of real identity. No PII is needed in tests. Future authentication, privacy and retention policies remain outside V0 and require a separate decision before real-world deployment.

## Types and operation names

`subject_id`: ASCII `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`.
`request_id`: optional opaque ASCII token with the same validation; scoped per subject.
`occurred_at`, `from`, `to`: timezone-aware RFC3339 timestamps, normalized to UTC. Naive timestamps, malformed times and empty IDs are invalid; no implicit wall-clock timestamps.
`session_id`: opaque server-issued unique stable string.

`Session` = `{session_id, subject_id, checked_in_at, checked_out_at}` (UTC RFC3339, `checked_out_at=null` iff open).
`State` = `{subject_id, active, active_session}` (`active_session` is `Session|null`).

Four logical operations with JSON-compatible input/output shapes (method binding not prescribed):
1. `checkIn({subject_id, occurred_at, request_id?}) -> Session`.
2. `checkOut({subject_id, occurred_at, request_id?}) -> Session`.
3. `getState({subject_id}) -> State`.
4. `listSessions({subject_id, from, to}) -> Session[]` sorted by `checked_in_at, session_id`, filter `from <= checked_in_at < to`; `from < to` required. Open sessions can appear.

Errors are typed and machine-testable: `INVALID_ARGUMENT`, `ALREADY_OPEN`, `NO_OPEN_SESSION`, `NON_MONOTONIC_TIME`, `REQUEST_CONFLICT`, `NOT_FOUND`, `STORAGE_ERROR`. No implicit success on an invalid transition. `getState`/`listSessions` for an unknown subject return `NOT_FOUND`; `checkOut` for a subject without an open interval returns `NO_OPEN_SESSION`.

## Persistence and transition invariants

- At most one open interval per subject; enforce in a real SQLite transaction with a database constraint, including concurrent connections/processes.
- `checkOut` requires one open interval and `occurred_at > checked_in_at`; duplicate/openless checkout fails. `checkIn` fails while open and its timestamp must be strictly later than the last completed checkout. A subject may have multiple nonoverlapping completed sessions.
- `request_id` is optional. When given, the same `(subject_id, request_id)` and identical operation+arguments must return the persisted prior response without duplicating effects; different payload for the key returns `REQUEST_CONFLICT`. Without a key, repeated state-changing calls are governed by transition errors, not automatic retry. On unknown execution outcome, use readback/reconciliation, never blindly rerun.
- Database setup/migrations are repeatable; persistence survives process restart. All SQL is parameterized. Concurrent creation of a second open interval must fail, not race to two successes.

## Ownership / disjoint write-sets

Prospective child `ATTENDANCE_DOMAIN_PERSISTENCE_001`: exclusive write-set `attendance/core/**`, `attendance/storage/**`, `attendance/tests/core/**`; owns the logical API implementation, schema/migrations, storage/concurrency and core tests.

Prospective child `ATTENDANCE_OPERATOR_CONSUMER_001`: exclusive write-set `attendance/operator/**`, `attendance/tests/operator/**`; owns CLI actions for in/out/state/list, display and negative/contract tests. Consumes the frozen service API via an adapter/mock before integration; no direct database/schema changes.

Parent Control owns `attendance/contracts/**` (including this file) and future `attendance/tests/e2e/**` integration verification. Both children read this contract, neither writes it. Final delivery requires tests across actual operator + domain implementation, not merely mock PASS. Separate Git candidate, validation, independent review, Developer acceptance, Phase 2, effect reconciliation and logical closure per child; Parent close only after corresponding original receipts.

## Minimum H6 evidence to qualify (not yet PASS)

- Domain: deterministic check-in/out, duplicate/invalid/out-of-order, distinct successive sessions, persisted restart, concurrent separate connections, migration repeat and query edges.
- Operator: usable CLI with four operations, unknown subject and error cases, contract/mock tests independent of domain implementation and real end-to-end tests on integrated candidate.
- Parent: actual disjoint changes and genuine independent child ownership/receipts; simultaneous work can be demonstrated without overlapping writes, but synthetic Beads graph or tasks alone do not qualify.
- Separate grants needed before TaskCycle initialization, worker dispatch, candidate acceptance and Phase 2; no Product effect is implied by this planning interface.
