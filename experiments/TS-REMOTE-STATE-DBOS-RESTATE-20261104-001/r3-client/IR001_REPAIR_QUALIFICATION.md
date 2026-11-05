# R3 physical-host client — IR001 repair candidate (experimental only)

## Identity and evidence ceiling

Subject: `mauedgar/ts-execution-lab`, branch `ee/ts-remote-r3-client-ir001-repair-20261105-001`.
Repairs `TS-REMOTE-R3-CLIENT-PREFLIGHT-IR001` F001–F003 within the bounded synthetic P01–P04 code scope. No Product/Kernel writes. The reviewer must freeze the **commit+tree+blob containing this document**, not assume the moving branch is the subject.

The client is NOT a hardware/physical attestation mechanism. The host label, local hostname SHA-256 and pinned database role are necessary checks, not sufficient proof. External reviewer-controlled evidence must independently map two distinct device IDs, process/session identity, private credential custody, host A outage, and independently issued B read/query. Do not claim P01–P04 physical PASS on code-only preflight.

## Required private per-host inputs

- `TS_R3_DATABASE_URL`: secret URL from local private credential store, never CLI argument, GitHub, OneDrive, Commander log or receipt. SSL URL params allowed only `sslmode=verify-full`.
- `TS_R3_EXPECTED_HOST`: exact preapproved Neon endpoint hostname (not credential).
- `TS_R3_TEST_ID`: new globally unique `R3-HOST-...` synthetic ID, **never** reuse the provider-side prior P02 IDs.
- `TS_R3_HOST_LABEL`: `HOST_A` or `HOST_B`, compared to external device witness.
- `TS_R3_EXPECTED_DB_ROLE`: separately approved scoped SQL role, not database owner.
- `TS_R3_EXPECTED_DEVICE_DIGEST`: SHA-256 hex of local hostname independently captured on that physical machine. Self-attestation alone proves nothing; reviewer cross-checks external host receipts.

Dependencies: Node22 plus pinned `../r2-node/package-lock.json` (`npm ci` in that exact directory, isolated). Client deliberately imports the lock-resolved `../r2-node/node_modules/pg`; no global npm fallback.

## Scoped privileges before first network SQL

Host A role: CONNECT on the synthetic DB, USAGE on **only** `ts_r3_synthetic_20261105_001`, SELECT+INSERT on the three synthetic tables; never OWNER/SUPERUSER/CREATEDB/BYPASSRLS. Host B role: CONNECT + schema USAGE + SELECT on the same three tables. It must lack INSERT/UPDATE/DELETE/DDL. B `replay` and `collision` take advisory transaction locks and read existing receipts via the same `dispatch` handler in **existing-only** mode; no SELECT FOR UPDATE and no write. Validate actual `has_table_privilege` outcomes independently; not assumed from documentation.

Secrets must be installed through protected host-local stores by an authorized operation; do not use Commander to transmit secrets, build patches, or explore repositories. Treat missing credential custody or unqualified TLS as `BLOCKED_PRECONDITION`.

## Preflight and controlled run order

1. Freeze Git commit/tree/blob and dependency lock; independent source/code/negative static review first.
2. Establish external physical A/B identities, unique roles, host-local secret stores, and provider-scoped ACLs. Confirm external TLS `verify-full`; on each host run `tls-negative` (wrong servername must raise `ERR_TLS_CERT_ALTNAME_INVALID`). A different TLS failure is not PASS.
3. Host A: `probe` then **once only** `write-drop-ack` on a fresh unique test ID. This intentionally suppresses an already successful COMMIT ACK; it is a simulation, not a proven network loss. A's output `UNKNOWN_CLIENT_ACK` is **not** permission to replay. Actual failed/ambiguous COMMIT exits `UNKNOWN_COMMIT_ACK` (code 2) and blocks mutations.
4. From an independently witnessed new Host B process/connection, run `probe`, then read-only `recover` for the exact same ID. No receipt means `UNKNOWN_NO_RECEIPT`; **stop**, do not retry write.
5. With the same B role and verified original receipt, run `read`, `replay`, `collision`. These invoke the identical transactional dispatcher in existing-only mode. Assert persisted command fingerprint, original result and exactly one state, event and receipt before and after; a changed authority fingerprint is rejected by the handler.
6. Physically take A offline and collect independent evidence; start fresh B process to read the same record with no A local files. Physical offline, concurrency P05, stored UNKNOWN P06, restarts P07, restore P08, negative credentials P09 and cleanup P10 remain **separate gated test attempts**, not implied by this file.

## Explicit advisory dispositions

- A001: positive TLS config + negative `tls-negative` code path prepared; **not proven** until actual external client test.
- A002: genesis expected revision 0 and same-key advisory-lock serialisation, no generalized CAS, event-sequence append or P05 contention claim; **deferred to P05**.
- A003: sorted-key JSON integers-only hash labelled `TS-R3-JSON-SORTED-V1`, not RFC 8785 or Product canonical cross-runtime proof. Full SHA-256 stored and verified; output prefix display-only. Cross-runtime vectors remain a separate gate.
- A004: existing-only B does not require UPDATE privilege, no secrets embedded; roles/privileges and local secret custody **unverified** until qualified provider-side checks.
- A005: no code-only test can assert physical P01–P10 or DBOS consumer parity. Keep all external gates open and record the original provider-side P02 as a **separate** confirmed experiment.

The candidate may become preflight-reviewable without any claim of real-world test PASS, Product acceptance, Phase2, or Kernel retirement.