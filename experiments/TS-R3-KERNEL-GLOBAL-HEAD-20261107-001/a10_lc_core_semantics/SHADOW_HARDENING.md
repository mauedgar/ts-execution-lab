# A10 — Local A03/A04 shadow-async hardening

NONPRODUCT experimental test support only. No Neon, SQL, credentials, Product integration, new Upper LC rules or TC Core state changes.

Prior A10 IR002 review ID TS-R3-A10-UPPER-LC-ASYNC-IR002-20261108-001, original run e7d4488c-4c90-832c-82be-984e98307198, 0 blocking findings/2 local advisories:
- A03: reconcile() previously released UNKNOWN based only on CONFIRMED and mutationId. Repair binds scope, mutationId, fingerprint of revision/epoch/previous-event/event hash/exact state/event bytes, expected revision +1, previous epoch, state and event SHA256. UNKNOWN remains fenced on any mismatch. The local test corrupts each of eight receipt dimensions independently, verifies no redispatch and only accepts original receipt after complete match.
- A04: commit() previously had no in-flight exclusion across awaited port.apply. Repair guards with a fail-closed per-adapter inflight token set synchronously before awaiting; second commit returns BLOCKED_INFLIGHT without reaching port, proposals and reconciliation cannot bypass the live operation. Finally releases token after outcome classified. Adversarial test holds the first async port call and overlaps a second call, requiring exactly one backend dispatch and no rejected mutation in committed state.

All transitions and event bytes continue to be computed by the original Product JS V0 code, isolated in disposable filesystem shadow under an exact observed revision; fake CAS port is storage test support only. Backend retains no Product authority. This is NOT a qualified production lock or distributed epoch, not actual PostgreSQL transaction/receipt durability, not remote ACK/TLS/physical-host proof and not Product caller integration. No new actor, state machine, scheduler or mandatory artifact.

This candidate is eligible only for secretless local native qualification and independent read-only code review. Previous A10 and D7/D8/D9 terminal effects are preserved and not replayed. Global A02 and Product cutover remain blocked.
