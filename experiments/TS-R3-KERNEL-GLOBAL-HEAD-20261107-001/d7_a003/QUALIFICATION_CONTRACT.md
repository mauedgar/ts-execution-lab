# TS-R3 D7/A003 — Disposable qualification contract (NONPRODUCT)

Status: CANDIDATE_SPEC_ONLY / NOT_EXECUTED
Owner: TS_EXECUTION_ENGINEERING
Parent: mauedgar/ts-execution-lab@88a7a703e6a85bdded7a2445f01a5913afbd2a90
Product oracle: mauedgar/tecnotron-ai@26509b74d50207bb247dcc9bdb929a63f5451e88
Scope: isolated PostgreSQL 16 service; no Neon DSN, no Product writes, no existing schema reuse.
Frozen source: E2 Product JS 20 generations / 19 events; E2 original GHA run 42424099166.
Prior independent evidence IR001: RECOMMEND_LIMITED / 0 findings / 1 global advisory A02.
Forbidden: replay historical runs, security-denied publication, Product cutover, live migration, credential materialization.

## D7 — Historical reversibility

1. Reproduce the original E2 JS fixture using the existing frozen capture workflow; verify exact source blobs and generation hashes before SQL.
2. In a *new* disposable schema and scope, initialize genesis and apply exactly the 19 historical commands, each once, using bridge.apply; compare state bytes, event stream bytes, SHA-256, revisions and receipts after every generation.
3. Export a read-only, deterministic legacy-V0-compatible snapshot and newline-delimited event stream from bridge.read. Validate with the original JS Product oracle (not solely the Python mirror); compare byte-for-byte with the original filesystem fixture. Do not label this a Product migration API.
4. Restore those exported bytes to an independently created, disposable filesystem destination through a create-only, preflighted test adapter. Run the original JS Product read/verification against the restored copy, with all event hashes and revisions equal.
5. Negative rollback: inject a controlled failure *before commit* during a new disposable SQL mutation; verify unchanged head, events and receipts via a second connection. A failure after SQL dispatch is UNKNOWN until read-only reconciliation; never replay.
6. Negative import: corrupt one historical event byte or hash; verify rejection before any persistent mutation and unchanged destination.
7. Ensure all disposable destinations are unique, have explicit owner and bounded cleanup, and are never Product paths.

D7 PASS requires the original JS oracle and PostgreSQL agree on all 20 states and 19 events, reversible restore exact bytes, negative rollback NONE, and no unresolved UNKNOWN.

## A003 — Capacity and negative contracts

1. Measure bounded 0/1/19-event reads and increasing event-stream sizes under PostgreSQL 16; record elapsed times and resource ceilings. Measurements are descriptive, not a production SLO.
2. Reject payload/state above bridge.MAX_BYTES (4 MiB), malformed UTF-8, duplicate JSON keys, unsafe integer, invalid hash, mismatched event line, stale revision and mutation-ID collision; verify no new event, receipt or head change.
3. Verify non-idle psycopg connection is rejected before dispatch; verify replay of a confirmed receipt is read-only.
4. Verify concurrent CAS at the same revision with independent connections: one CONFIRMED, one STALE/NONE, with observer readback. Reuse D4 evidence if identical subject/conditions; do not repeat D4 merely to inflate coverage.
5. Capture SQL row counts, state/event hashes, original runner identity, environment versions, commit/tree, run ID and terminal result.

A003 PASS requires negative effects NONE and a recorded bounded capacity envelope. No extrapolation to Neon Free or two physical hosts.

## Execution admission

Before dispatch: freeze exact candidate commit/tree, review changed paths, establish one ExecutionAttempt, one disposable database/schema namespace, preconditions and expected provider-native receipt. Run once. On UNKNOWN stop conflicting writes. Review result independently. Never create a substitute for the previously denied E2 publication.

## Remaining global gap

A02 remains OPEN: real Neon TLS, independent hosts, genuine network ACK loss, extended disconnect/restart, and reversible historical Product cutover. Even D7/A003 PASS does not authorize Product adoption; cutover remains NO_GO.
