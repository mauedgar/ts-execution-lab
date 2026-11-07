# TS R3 — experimental Global-Head PostgreSQL bridge (non-Product)

**Owner:** TS Execution Engineering / TS Remote State 002. **Authority:** experimental only. **Source oracle:** `mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88`, `src/state-kernel-v0/store.js` Git blob `f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a`, `src/state-kernel-v0/index.js` blob `0219b92e5f546407a6060a6dc449865c14c7f144`. **Architecture decision:** `mauedgar/ts-execution-transport@17ddae918a9ff4b3884b6291552e44c1815b192e:decisions/TS-REMOTE-STATE-002-KERNEL-REPLACEMENT-ADAPTATION-20261107-001/DECISION.md`.

## Selected scope

This is the **storage-only** bridge *candidate*: fixed PostgreSQL 16 schema with a global `head` revision, **raw bytea** Product JS snapshot and event strings, immutable append-only global event sequence, and per-mutation receipts in one atomic transaction. The Python bridge is stdlib-only until a caller passes a configured `psycopg` connection. It does **not** parse SQL credentials, access the network, create a schema on import, or run code when imported. `schema.sql` is a proposed isolated schema, **not executed or Product DDL**.

The Product JS/TS caller remains responsible for the four-kind lifecycle semantics, valid state transitions, TaskCycle obligations and late extension, bootstrap provenance, actual Developer-grant competence, closure decisions and `UNKNOWN` fencing. No generic `TaskCycle` actor, scheduler or authority source is added. `scope` isolates experiments but is **not** a new TaskCycle ID/authority. `authority_fingerprint` stores an *external admission claim*, never proves its competence.

- `initialize(conn, scope, state_bytes)` creates only a virgin revision-0 empty Product-shaped snapshot, once. A lost commit ACK is `UNKNOWN`, requiring `read` before any further attempt, never duplicate genesis.
- `read(conn, scope)` takes an explicit **repeatable-read READ ONLY** transaction and verifies the full event chain, exact snapshot/state SHA-256, bytes and event replay. A tampered `bytea` or field must fail closed.
- `apply(conn, Mutation(...))` requires `conn.autocommit=True` and `conn.info.transaction_status.name=='IDLE'` for a dedicated top-level psycopg3 transaction. It checks the original bytes, validates exact global revision and event predecessor, acquires the **single global head row `FOR UPDATE`**, then updates it via conditional global CAS and inserts event+receipt in one transaction. Failure after dispatch means `EffectUnknown` even if the backend probably rolled back. **No automatic retry.** In the case of a verified prior mutation receipt, it returns the existing receipt without another effect; changed fingerprints fail.
- `reconcile(conn, original_mutation)` reads the same original attempt's receipt and verified event chain under a consistent read-only transaction. Absence after uncertainty is **UNKNOWN**, not proof of `NONE`; a conflicting fingerprint is a fail-closed condition.

### Read-only Product V0 contract guard

The new `ts_global/legacy_v0.py` is a **fail-closed read mirror** pinned to frozen `contracts.js`/`store.js` blobs. It checks kind-specific exact fields, aggregate state vocabularies, references, obligation shape, timestamps, `UNKNOWN` reconciliation, `BOOTSTRAP_IMPORT` provenance, authority/evidence correspondence, cutover timestamps, and the nonterminal bootstrap invariant. It does **not** issue grants, choose legal transitions or replace the real Product JS/Zod validator. Python additionally enforces JS snapshot field order, two-space serialization and original event-history reconstruction, including numeric object-key ordering and Unicode bytes. Full Product runtime parity remains an independent acceptance gate.

### Exact JS bytes

The canonical Product store hashes **`JSON.stringify(payload)` insertion-order bytes** and writes `JSON.stringify({...payload,hash}) + '\n'` into its `events.ndjson`; it uses `JSON.stringify(state,null,2)+'\n'` for snapshots. **Never parse JSONB and reserialize** to reproduce those hashes. `oracle/generate.cjs` creates a deterministic **synthetic** 14-event four-kind fixture with exactly these JS byte rules, including TaskCycle obligation, nonterminal bootstrap import, `UNKNOWN` and explicit reconciliation. `oracle/golden.json` is the frozen fixture. The Python bridge tests verify byte-for-byte replay. This synthetic fixture **does not execute the real Product Zod contract engine or replace the E1 acceptance oracle**; full equivalence and historical migration remain deferred gates.

### Native limits (do not overclaim)

- **Tested locally** in isolated ChatGPT container: Python 3.13.5 stdlib fake-transaction tests, plus Node 22.16.0 fixture generator. `FakeConn` simulates rollbacks/ack-loss; it is **not a PostgreSQL execution**.
- **Not yet qualified:** native Python 3.15.2/psycopg3 real transaction, SQL permissions/DDL/rollback in a fresh native Neon sandbox, external TLS/credential issuer and truly independent host A/B, lost network COMMIT ACK, high-volume performance, historical Kernel migration, safe Product integration.
- **Size limit:** 4 MiB for individual snapshot/payload/line. The full event history is read/replayed on each mutation (O(n)) — deliberately simple for experiment; archival, performance and unbounded Product operation still open.
- External creator of `Mutation` must be the **trusted existing Product JS state machine**; these Python shape guards are an extra defense, not a replacement for `validateState`, transition legality or Developer acceptance. A malicious database principal capable of rewriting both event bytes and hashes is outside this experiment's tamper-security guarantee.
- Any historical byte incompatibility or mismatched Product fixture blocks cutover. A source-only review PASS **never** authorizes migration, execution on Product, or physical Kernel removal.

## Local verification (non-production)

```sh
# No installation required for offline tests; tested with Python 3.13.5
node oracle/generate.cjs     # deterministic synthetic JS fixture; rehash against tracked file
PYTHONPATH=.:tests python -m unittest discover -s tests -v
python -m compileall -q ts_global tests
```

**Native 3.15 reference** for any future admitted isolated runner: `psycopg[binary]==3.3.8`, Python 3.15.2 and a frozen `uv.lock` created only after independent IR and qualified notebook source-materialization. The bridge never installs dependencies.

**Product authority:** no changes to `mauedgar/tecnotron-ai` or its SOT. The global-head storage protocol is an experiment, not a canonical replacement or acceptance.
