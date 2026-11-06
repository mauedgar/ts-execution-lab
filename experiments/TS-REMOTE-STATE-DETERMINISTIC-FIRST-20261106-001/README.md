# TS Remote State 002 — Deterministic-First Python adapter v0 (NONPRODUCT)

Experimental candidate only. No Product mutation, no real Neon connection in this candidate's local tests, and no Developer acceptance/Phase2/Kernel retirement. Source of decision: `ts-execution-transport@12c59d575eccdd97b200fec46bb5608456e13c6c:decisions/TS-REMOTE-STATE-002-DETERMINISTIC-FIRST-20261106-001/DECISION.md`.

## Protocol boundary

- Python `==3.15.2`, `psycopg[binary]==3.3.8` pinned in `pyproject.toml`. **A full `uv.lock` is mandatory before physical deployment**; this repository does not claim dependency installation or Python 3.15.2 compatibility until native qualification.
- CLI (`python -m ts_detstate plan --command-file file.json`) is **offline and credential-free**, does not contain a write mode. Public API `apply_once(conn, command)` and `reconcile_readonly(conn, command)` must only be used by a future admitted hash-verified runner with distinct protected A/B credentials, real PostgreSQL `dict_row`, `autocommit=True`, verified TLS/role/schema and a single ExecutionAttempt. No direct Python import is permission to make Product or provider effects.
- Synthetic-only, fixed schema `ts_r3_synthetic_20261105_001`, fixed authority marker `AUTH-SYNTHETIC-R3`, `R3-DET-` identities. Not a Product grant or real TaskCycle. Transactions commit state + one event + one receipt atomically; `UNKNOWN` fences COMMIT ambiguity. No automatic retry, scheduler, DBOS or agent runtime.
- Canonical JSON v0 permits strings (NFC), integers within IEEE-754 safe range, booleans, null, lists and objects only. **Cross-language/JS JSON canonicality is NOT qualified**. Float, exotic keys, duplicate JSON keys, malformed Unicode and oversized input fail closed.
- Multi-revision append chain verified up to 1000 events; later revisions do not prevent reading a prior receipt. A unique mutation claim is transaction-scoped. Same-key changed authority/state/attempt fingerprint is collision; distinct-key stale revision refuses. Competing genesis can surface a precommit SQL failure; always reconcile first rather than rerun blind.
- Database constraints assumed from previous synthetic read-only verification: PK aggregate id, event id, unique event_hash, receipt mutation id; current A grants SELECT/INSERT and bounded UPDATE on aggregate/receipts, current B SELECT-only. SQL identifiers are static and values bind via `%s` parameters.
- The event hash includes synthetic authority/attempt/operation IDs and state. Event chain hash, revision, aggregate and receipt are independently checked in a read-only REPEATABLE READ transaction. No remote data, credentials or historical P02 rows are transferred.

## Validate locally

`PYTHONPATH=. python -m unittest discover -s tests -v`

The tests exercise Python-only fake PostgreSQL transactions; they do **not** prove real PostgreSQL isolation, TLS, external secret custody, two physical hosts, real lost COMMIT ACK, Python 3.15.2 wheels, Product aggregate equivalence, or backup/restore. These are separate mandatory empirical gates before migration.

## Execution boundary

Use ordinary trusted Git/source tools to acquire the frozen commit; Commander is a mechanical runner ONLY after the exact versioned runner, toolchain and allowlist are verified outside it. Do not use Commander to clone/edit source or scripts. `uv.lock` must be generated and independently reviewed using a real 3.15.2-compatible environment, never forged or copied from a different project. The future Host A physical write requires a new isolated identity because the old Node-frozen `TS-R3-PHYSICAL-NOTEBOOK-A-20261106-001-A01` remains reserved and not dispatched.
