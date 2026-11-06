# TS R3 — offline execution-attempt receipt mechanic v1

**Owner:** TS_EXECUTION_ENGINEERING. **Class:** experimental, isolated mechanical execution binding. **Product authority/effect:** NONE. **Neon/physical host effect:** NONE. This is neither a new Upper LC actor/gate nor an authorization or scheduler. No integration into `mauedgar/tecnotron-ai:tools`.

## Subject and narrow purpose

Frozen source subject `mauedgar/ts-execution-lab@981e06ede3fa6e1b0a1ceeee04b786a9e51b3c17`, tree `74faee8d375d6e4271c5255aed4931c71da61ebd`, preflight file `r3-portable-host-preflight.cjs` Git blob `044c517c631f225e2c476046b163f53ad6b11a21`. Its separate independent review IR002 was `PORTABLE_PREFLIGHT_CODE_PASS`, **0 blocking findings / two unresolved external advisories A001 (real package integrity) and A003 (authenticated provider/attempt)**. This wrapper does not change or replace that source.

`r3-offline-attempt-v1.cjs` is a credential-free, bounded, one-shot invocation/receipt wrapper for the **existing** read-only R3 portable host metadata preflight. The wrapper's `request.json` identity and provider subject are **self-declared and hash-bound, not authenticated**. The provider must independently authenticate request, immutable checkout and execution provenance before trusting it.

It does not connect to a database, call GitHub, query Neon, install packages, inject credentials, create a server, mutate Product, or issue network requests. It invokes only the pinned local `.cjs` preflight with native `process.execPath` in a sanitized subprocess environment. It does not assert the process cannot access networking at the OS level; that remains an external sandbox requirement.

## Exact invocation and input layout

Caller must *already have* a qualified and provider-enforced immutable checkout with the pinned preflight source and installed pinned dependencies, plus one isolated existing attempt directory on a filesystem whose containing directory supports acknowledged fsync. This is qualified on the ChatGPT-local Linux container only; no native Windows durability claim. Directory ownership and ACLs, provider-origin proof and machine trust are **external preconditions**. The directory must initially contain exactly request.json and must NOT contain claim.json or receipt.json. This is a new two-file mechanical write-set, not a Product state transition. No workspace or attempt directory is created by the script.

```text
node <immutable-checkout>/r3-client/r3-offline-attempt-v1.cjs <isolated-existing-attempt-dir>
```

Example `request.json` (UTF-8, at most 32KiB; exactly these five top-level properties):

```json
{
  "schema": "TS_R3_OFFLINE_ATTEMPT_V1",
  "operation": "CREDENTIAL_FREE_METADATA_PREFLIGHT",
  "operation_id": "TS_R3_OP_20261105_001",
  "execution_attempt_id": "TS_R3_ATTEMPT_20261105_001",
  "subject": {
    "repository": "mauedgar/ts-execution-lab",
    "commit": "981e06ede3fa6e1b0a1ceeee04b786a9e51b3c17",
    "tree": "74faee8d375d6e4271c5255aed4931c71da61ebd",
    "preflight_blob": "044c517c631f225e2c476046b163f53ad6b11a21"
  }
}
```

The wrapper checks argument count, request shape/IDs, exact subject, request file and ancestor path safety, pinned preflight Git blob and Node22, and rejects **any prior claim.json or receipt.json before dispatch**. It validates directory fsync support before effect; then creates claim.json with exclusive O_EXCL, writes every byte in a checked loop, fsyncs file, checks close, fsyncs the containing directory and verifies content **before it dispatches any child**. Any surviving claim, even without a terminal receipt, blocks repeat dispatch under the same attempt. The subprocess uses spawnSync with a strict preflight PASS line, 30s bound, 16KiB stdout/stderr limits, no inherited database credentials and no shell. The terminal JSON receipt.json is also created O_EXCL, fully written, file-fsynced, close-checked, directory-fsynced and verified. Both artifacts are permission 0600 where supported. Only claim.json and receipt.json are allowed in the mechanic write-set. All other files are read only.

`claim.json` contains request and subject SHA256 correlation and a NONREPLAYABLE_ATTEMPT_RESERVATION marker. `receipt.json` includes schema, operation/attempt IDs, raw request SHA256, the exact claim SHA256, frozen subject, local Node version, PASS_METADATA_ONLY/BLOCKED, child exit/failure class, and explicit `network_proof: NONE`, `package_integrity_proof: NONE`, `device_attestation: NONE`, `product_effect: NONE`. No raw stdout/stderr, environment values, hostname, paths or credentials appear in receipt. The returned digest is for exact artifact reconciliation, not a cryptographic signature.

**Fail closed:** invalid or missing input/manifest, ancestor redirect, source hash mismatch or existing receipt exits 2 *without executing child*. A failing child creates one terminal BLOCKED receipt; no retry within the same attempt directory. Any crash after durable claim and before terminal receipt leaves a claim-only **UNKNOWN** to be independently reconciled; no execution restart. A short write, file fsync/close failure, directory fsync failure, or readback mismatch leaves the attempted claim/receipt untouched and fails closed. On platforms where directory fsync is unavailable (for example the unqualified Windows filesystem case), the wrapper BLOCKS rather than simulating durable publication. The fsync guarantee remains subject to honest provider/filesystem behavior and is not equivalent to a provider-signed receipt. A provider failure after a successful child but before receipt still requires original-provider observation. The script must not be used to adjudicate an ambiguous physical database effect.

## Qualification ceiling and separate future gates

1. Native Node22 unit suite `r3-offline-attempt-v1.test.cjs`: 29 tests cover durable claim-before-dispatch, simulated and real subprocess exit after durable claim, fail-closed no-replay, short/progressive writes, file+directory fsync and close failures, receipt UNKNOWN, strict PASS grammar, request/source integrity, path links, no args/secrets, child errors and collisions. The suite uses **mocked subprocess results** for positive cases and a real isolated negative CLI, so it does **not** prove installed `pg`, power-loss filesystem persistence, a real physical host or TLS.
2. Independent code review required for this *new wrapper* before recommending use. No claim of previous IR002 covering this new code.
3. **A001** qualified locked clean installation: provider-enforced immutable checkout, Node22, `npm ci --ignore-scripts --no-audit --no-fund` against verified package/lock and isolated directory; verify actual native `pg` package and transitive graph and original provider result. **This wrapper does not perform installation** and `npm ci` is not yet executed on the physical hosts. A tarball SRI in lock alone cannot prove installed bytes after-the-fact.
4. **A003** provider-native identity: independent provider-signed run/attempt/device receipt, immutable checkout provenance, OS user, resource isolation and protected secrets. Self-declared Git refs and hashes alone are not attestation; this wrapper's receipt does **not** close A003.
5. Windows/Linux native qualification, TLS CA/hostname positive and negatives, host-specific protected credentials, A offline / B independent recovery, genuine lost-COMMIT-ACK and P01–P10 require separate competent grants and original receipts. No reuse of denied GitHub Actions workflow or alternative provider to bypass that specific denial.
6. For laptop-free execution, ChatGPT Web/mobile may read GitHub/Neon evidence but **unattended remote provider execution with both local hosts off is still unproven**. This mechanic makes receipt transport independent of a specific host, not autonomous cloud capacity.

**No completed effect is replayed:** original Neon P02 and both ACL grants/revokes, previous IR003, portable IR001, portable IR002 and earlier denied workflow creation all retain their native dispositions. New request/attempt must have distinct identity, qualified provider and explicit write-set.
