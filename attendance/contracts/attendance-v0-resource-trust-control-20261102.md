# H6 Attendance V0 — Control resource and trust boundary disposition 2026-11-02

Evidence class: COMPETENT_CONTROL_CONTRACT_REFREEZE_ADDENDUM
Authority: Developer explicitly authorized Control to re-freeze materially changed Attendance V0 semantics during TECNOTRON_BETA_RUN_001 and authorized the next recommended dispositions on 2026-11-02. Binding only after Control records the exact commit/blob in issue #35; this document alone is not Product adoption.
Owner: TECNOTRON_BETA_RUN_001 Control
Scope: H6 standalone pilot, Domain/Operator/Parent shared interface
Predecessor: `attendance/contracts/attendance-v0.md` blob `2e939672a8401154289ea94aab83194f689247f0`
Predecessor exceptional rule: `attendance/contracts/attendance-v0-legacy-idempotency-control-20261102.md` blob `5ccb84f7642eb25fc2b3fb98bb7f93cab0ecd917`
Motivation: original independent Domain IR007 FAIL, `mauedgar/ts-execution-transport@a88d0f702917769a6d846152fe53cb73ebce5ce6:results/TECNOTRON-H6-IR007-DOMAIN-20261102-001/ORIGINAL_REVIEW_RESULT.json`, F003, A001, A002, A003 and A005.

## 1. Private SQLite trust model

For this **experimental single-process/single-file standalone pilot**, the SQLite file is an application-owned, private file protected by the OS. Arbitrary direct writes to the file by another principal, SQL editing of both a request and its provenance ledger, malicious administrator, corrupted block storage and hostile user-supplied SQLite files are outside the V0 application-security model. The file path is provided by the authorized operator, not an untrusted network user.

The application MUST still fail closed on an unrecognized v1/v2 schema, data invalidity detected on application read, malformed persisted responses, spoofed payload-only legacy markers, missing migration provenance ledger, violated uniqueness/integrity and inconsistent history. A ledger persisted in the **same mutable file** establishes migration origin only **under this OS-trusted file assumption**; it is NOT a cryptographic receipt, a tamper-proof attestation or protection against someone with arbitrary write access to the same file. No claim of tamper evidence. If shared/untrusted or real-person deployment is selected later, a separate security/storage authority decision is mandatory. No authentication/PII/real attendance deployment in V0.

## 2. Timestamp precision/CPU budget — scoped material exception

RFC3339 timestamps have a maximum of **8192 digits after the fractional decimal point** and maximum **8218 ASCII characters total**, including date/time and UTC-offset (maximum length calculation: 10+1+8+1+8192+6). Empty/malformed/oversize inputs MUST fail with typed `INVALID_ARGUMENT` **before expensive regex/datetime parsing**. Within the bound, retain **all** significant fractional precision; **no rounding/truncation**. Original 5000-digit precision regression remains valid. Both `occurred_at` and `from/to` use the same admission rule; no silent precision loss.

The V0 interface is explicitly re-frozen to include this admission ceiling. Operators must not infer that larger syntactically RFC3339 timestamps are supported. This bounded resource policy supersedes solely the formerly unrestricted input length; other V0 semantics remain as frozen.

## 3. listSessions result budget — scoped material exception

`listSessions` remains an **atomic, fully materialized, ordered `Session[]`** in its original V0 shape. It does not paginate or truncate. For at most **10,000 matching Sessions**, return all. At **10,001 or more**, fail deterministically with typed `INVALID_ARGUMENT` and a reason requiring a narrower `from/to` range; do not return partial data. Enforce using a SQL `LIMIT 10001` guard **before constructing all result objects** and preserve the original sorted order. Not a new API/gate/scheduler, no implicit pagination.

This controlled query-output policy supersedes V0's previously unbounded result size; operator and Parent E2E consumer must be re-bound to this exact addendum as a shared Control disposition.

## 4. Validation and declared limitations

- V1->V2 migration: strict original-schema and object-inventory admission, transactional migration and persisted replay; v2 restart must verify schema and indexes. Negative examples: extra UNIQUE, RAISE(IGNORE) trigger, fake partial index v1/v2, corrupted replay marker, unknown v0 schema, overlap, orphan, read corruption.
- Negative budgets: 8192 digits accepted without precision loss, 8193 rejected; list 10,000 inclusive accepted and 10,001 rejected atomically. Additional separate smoke/fault simulations for ENOSPC/IOERR where available without touching real user DB.
- **Durability limitations:** SQLite transactions + logical fault tests are expected. No claim of full physical power-loss safety or cryptographic crash/fault tolerance from CI; classify that as a declared out-of-scope limitation for pilot only, NOT an unproven PASS. Real deployments require separate non-Phase1 acceptance and environmental qualification.
- **Parent evidence** (real Operator+Domain integrated E2E) belongs to Parent and is NOT satisfied by Domain-only native validation or an IR PASS.
- Preserve original V0/addendum immutable history, all prior IR FAIL receipts and Product SOT. This Control ruling changes only the scoped resource/trust interpretation for future H6 Phase1 review; does not accept code candidate, grant Phase2, integrate Product, change Kernel/Beads or touch FitFlow.

If this new addendum is referenced in a new reviewer interface, its SHA/blob and issue #35 Control qualification MUST be exact. Neither child modifies `attendance/contracts/**`.