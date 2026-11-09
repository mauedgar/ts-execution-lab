# A11 — Original Product JS semantics through asynchronous real PostgreSQL16 bridge

NONPRODUCT / TS_EXECUTION_ENGINEERING. This is an isolated experiment; no Product code changes, no Developer acceptance, no Neon credential-bearing effects, no replacement of canonical Kernel.

Exact chain: frozen original Product JS V0 calls -> A10 reviewed disposable shadow proposal -> Node22 async port -> bounded stdin JSON IPC -> Python 3.15.2 psycopg[binary]3.3.8 worker -> preexisting TS R3 real PG16 bridge with one global CAS, append-only event/receipt, exact JS bytes. Read and reconciliation use new independent connections; Mutation authority_fingerprint is a fixed synthetic test marker and is NOT a Developer grant.

Strict exposure: Docker PG16 with fixed synthetic user/database and 5432 loopback in ephemeral GitHub Actions worker; no Environment, no Neon, no secrets. One workflow-native attempt. schema_guard.py creates exactly one known schema only if absent, and drops after verifying one expected scope and final 1 head/4 events/4 receipts. Worker input max6MiB, stdout small JSON with no credentials, stdin one-shot. No Product authority or semantic transition implementation in Python/SQL; Python bridge only validates historical JS encoding and CAS invariant.

DoD: original JS genesis with exact bytes; original JS TaskCycle create/transition/satisfy/pending with exact 4 canonical events and raw original reader restore at revision 4; stale proposal returns NONE without persistent event; real Postgres commit followed by **synthetic IPC response loss** must result in UNKNOWN until same mutation receipt is reconciled without retransmitting, original bytes/hashes verified and schema cleaned. This does **not** prove real network TCP lost ACK (D8 separate local), a distributed epoch, real Neon TLS/auth, two hosts, Product CLI consumer migration or production integration.

Important design limitation: A10 shadow currently computes semantics by reconstructing a temporary filesystem generation; it is qualification oracle, not a production-quality pure JS proposal engine. One Node IPC worker per request is a bounded experimental mechanism, not an accepted Product runtime architecture or performance decision. A separately reviewed future Product storage port must address process overhead and TypeScript/JS async API safely; no spawnSync runtime shortcut.

Security constraints: previous credential-bearing A001 IR003/D3 and E2 publication security denials remain terminal; this isolated synthetic PG16 test is independently non-secret and not a substitute for or replay of those effects. User confirms the existing Neon Environment secret, but an actual authenticated client has NOT been tested; no PAT, DSN or token retrieval.

Any failure => original attempt reconciled from native provider logs; never blind rerun same attempt. Follow-up independent STRICT_READ_ONLY review of exact candidate. Product cutover remains NO_GO.
