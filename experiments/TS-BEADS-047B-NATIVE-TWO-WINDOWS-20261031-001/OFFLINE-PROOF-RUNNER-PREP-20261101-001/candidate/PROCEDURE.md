# Disposable offline privilege proof runner — procedure

Execution attempt: `TS-BEADS-047B-OFFLINE-PROOF-RUNNER-PREP-20261101-001`.

This preparation created no fixture, database, user, privilege, secret, listener, or SQL process. It ends at **REVIEW_REQUIRED**.

## Future conditioned use only

An independent review must first approve these exact immutable bytes. A distinct future execution attempt must provide an external frozen JSON grant containing exactly: `Authority: EXTERNAL_ONE_TIME_USER_GRANT`, subject `TS-BEADS-047B-OFFLINE-DISPOSABLE-PROOF`, `OneTime: true`, its exact `ExecutionAttempt`, this runner's SHA-256, and observed `ExpectedHost` and `ExpectedOwner`. The runner rejects the preparation attempt, any mismatch, stale/reparse/unsafe root, listener/Serve state, prior receipt/unknown state, incomplete observation, or non-matching fixed Dolt binary/hash/version.

Only after that independent authorization may a reviewer invoke `-Effect`. It derives (not accepts) a new disposable root under `LOCALAPPDATA`, writes an original receipt before its conditioned process calls, uses `ProcessStartInfo.ArgumentList` and SQL on redirected standard input, then requires a second CLI readback using the same canonical privilege-file path. A timeout or ambiguity preserves state without kill, retry, or cleanup. Unsupported grammar/auth semantics is `NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE`.

This is not a statement about real privileges, security, or independence. It is only an auditable empirical fixture design when separately granted.
