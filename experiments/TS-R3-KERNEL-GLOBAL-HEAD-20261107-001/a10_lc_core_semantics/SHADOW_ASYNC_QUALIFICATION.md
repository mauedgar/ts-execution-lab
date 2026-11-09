# A10 — Experimental shadow async adapter qualification

Authority: NONE Product. Owner: TS_EXECUTION_ENGINEERING. Only isolated lab, no Neon credentials/SQL and no Product code write.

## Purpose and non-goals
Address local A10 IR001 advisories A01 (missing Milestone positive/negative and bytewise no-effect proof) and A02 (untested async proposal/CAS/UNKNOWN/old-writer fence). This DOES NOT qualify a production storage driver, real PostgreSQL lost ACK or Product integration.

A01 source canary now tests all four original Product kinds and verifies exact HEAD.json, state.json and events.ndjson bytes plus global revision stay unchanged after EVERY rejected original JS mutation. The test still uses the exact original JS fixtures contracts.js/index.js/store.js and Zod4.6.7 from Product HEAD 26509b74d50207bb247dcc9bdb929a63f5451e88.

A02 shadow adapter module shadow_async_adapter.cjs performs:
- stage observed state/events into a unique isolated disposable filesystem generation with exact SHA256 HEAD fields; the real original Product FilesystemStateStore.read/verify validates and the unmodified original Product index.js executes the proposed synchronous domain operation;
- capture exactly one new canonical JS event line, state bytes and original event hash; no domain transition rule is implemented in the fake port or adapter;
- expose a promise-based boundary with explicit observed revision and single writer epoch; fake in-memory CAS test support rejects stale revision and old epoch with NONE without any persistent mutation;
- a synthetic *postcommit response loss* throws after fake commit, adapter fences UNKNOWN and blocks further proposals/writes; read-only receipt reconciliation of SAME mutation ID recovers CONFIRMED without reapplying;
- explicit rejection of a stale writer after changing epoch followed by one successful new-epoch mutation; zero transient duplicates and one receipt per committed mutation.

## Unqualified critical parts
- The fake in-memory port is not PostgreSQL, has no real transactions/locks, no durability, crash/restart persistence, bytea/psycopg protocol, Neon TLS/auth or physical hosts.
- Disposable FS is a qualification oracle, not proposed runtime architecture. Its synchronous filesystem staging is NOT a production migration plan; a future Product candidate must extract a pure original-JS proposal engine at an intentional async caller boundary and independently prove byte/semantic equivalence against frozen original JS and PostgreSQL real driver.
- Backend authority fingerprint remains an untrusted claim. No automatic Product Developer/Control decisions or TC Core rule migration.
- The epoch fence in this prototype is in-memory only, not a distributed ownership or cutover fencing token. It does not authorize cutover and cannot replace a SQL-backed owner change contract.
- We reuse D7/E2 and D8/D9 terminal results for real local SQL/ACK evidence instead of replaying them. Global remote A02 authenticated Neon, physical two-host contention, prolonged remote recovery, full Product caller inventory and reversible cutover remain OPEN.

## Admission
Run qualification once on an isolated GitHub Actions branch without DB credentials; Node22.16/Zod4.6.7, exact Product JS blobs; expected six original canary scenarios with Milestone included and 14 exact negative rejections (12 original + 2 Milestone) and one shadow async scenario covering seven cases. Archive workflow after terminal outcome. Independent IR must label local vs remote coverage accurately. Product: NO_GO.
