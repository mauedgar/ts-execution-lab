# R3 portability experiment — credential-free host preflight

**Owner:** TS_EXECUTION_ENGINEERING. **Product authority/effect:** NONE.
This is a bounded *read-only* mechanic, not another Upper LC actor/gate, a scheduler, or a Product-approved recovery path.

## What is portable

`r3-portable-host-preflight.cjs` uses only built-in Node.js 22 modules and repository-relative paths. It checks each filesystem ancestor with lstat and compares canonical realpaths; the leaf is opened via a file descriptor and fstat (with O_NOFOLLOW where available). An attacker able to replace parent path components concurrently still creates a possible TOCTOU race; only use it in a provider-enforced immutable checkout. Windows reparse-point behavior and actual Node runtime on Windows require independent native verification. It does not bind to a device name, Commander, Orca, ChatGPT or a cloud provider. It can be run in a separately qualified checkout on Windows, Linux, a notebook, desktop, or ephemeral compute. It verifies the four *existing* R3 client/test Git blobs, the locked `r2-node/package.json` and `package-lock.json` Git blobs, and the installed `pg` package **name/version metadata** at the expected location.

Expected input layout is the frozen `experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/` root, with sibling `r2-node/` and `r3-client/` directories. Command from `r3-client/`:

```text
node r3-portable-host-preflight.cjs
```

Run without arguments, without `TS_R3_DATABASE_URL` in the environment, from an immutable qualified checkout. A matching `pg` package metadata file is necessary; it is **not** proof that a package was fetched with the lockfile integrity or that the module is safe to load. Do not run `npm install` automatically as a side effect of preflight. Do not run with privileged secrets.

## Precise read-only result

- Success means native Node22, pinned file blobs, pinned `package-lock.json` declaration with integrity metadata, and installed `pg@8.23.1` *package metadata* match. Output contains `installed=PACKAGE_METADATA_ONLY`, `tls=NOT_TESTED`, `physical=NOT_TESTED`.
- Missing file/package, wrong Node, changed source or lock, unexpected arguments, a detected `TS_R3_DATABASE_URL`, source or ancestor path symlinks/junctions, or unsupported metadata fail closed with one bounded `BLOCKED|...` line, exit 2. No credentials, DB URL, file paths, host identifiers or stack traces in the intended terminal receipt.
- No database connection, no network, no PostgreSQL DML/DDL, no credential creation, no physical host attendance, no GitHub Actions or Product action. The script itself does not enforce an OS network sandbox; execute only in an appropriately constrained provider.
- Synthetic native suite: `node --test r3-portable-host-preflight.test.cjs` — **21 tests** including parent redirect/junction and leaf symlink negatives, pinned lock/package tampering, malformed metadata, a deliberately unverified installed module and native CLI redaction. The suite creates disposable temp fixture files locally; it never connects to Neon.

## Relationship to host agnosticism

This is the **environment-sufficiency** predicate only. It makes the same preflight executable across authorized host types. A future notebook-off criterion additionally requires:

1. Provider-native immutable `ExecutionRequest`/`ExecutionReceipt` with authorization and `ExecutionAttempt` correlation, not just a console line.
2. Independently qualified ephemeral remote executor with appropriate secure secret injection, Node22/pg installation, real TLS and separate credentials.
3. Persisted authoritative state and receipts (currently experimental Neon + GitHub Transport), without relying on a machine-local folder or active ChatGPT session.
4. Successful unique A→B or A→remote test with A proved unavailable, B read-only recovery, no duplicate mutation; real uncertain-ACK reconciliation; independent review.
5. A read-only status surface usable from ChatGPT Web/mobile when notebook and desktop are offline.

**Do not confuse** this standalone preflight, R3 IR003 code-preflight PASS, or a possible new review PASS with actual physical continuity, automated unattended operation, kernel retirement or Product acceptance. In particular, the earlier GitHub Actions workflow-creation denial remains denied; this adapter is not a workaround and does not dispatch any workflow.

**Frozen existing effects:** Neon synthetic schema and historical P02 were confirmed once; current existing-table ACL and future-object default ACL were narrowed and independently confirmed. Neither is replayed here. Preserve `UNKNOWN` stop conditions and independent Product authority.

**Review disposition:** IR001 of the predecessor candidate was NO_RECOMMEND (F001 parent symlinks, A001–A003). This repair validates source and ancestor paths, adds native negatives, and keeps package integrity and host/provenance acceptance as external qualified gates. Neither the code nor the tests claim to remove all adversarial TOCTOU races.
