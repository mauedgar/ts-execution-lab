# TS-BEADS 047B — Repair instructions after WEB_INLINE IR001 FAIL (existing security gate)

**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`.
**Authority:** User experimental secure-provisioning authorization and subsequent correction/continuation authorization. `EXPERIMENTAL_CONTROL_ONLY`, no Product authority or TaskCycle initiation.
**Original candidate:** `mauedgar/ts-execution-transport@dce961f2e99950e7cf59f414320be29ed3530477:handoffs/TS-BEADS-047B-ARTIFACT-ACQUISITION-20261101-001/original/SecureProvisioningRunner-047B.ps1`, Git blob `ab7233a0bad92f46283874e4cf7936c2866d227f`, original attempt `TS-BEADS-047B-SECURE-PROVISIONING-PREP-20261101-002`. Preserve immutable original; do not re-run or repurpose its ExecutionAttempt.
**Independent verdict:** `mauedgar/ts-execution-transport@1e0ae1dd68ed6cf493c8340c19be24b3f01e2beb:handoffs/TS-BEADS-047B-SECURE-HOST-PROVISIONING-PREP-20261101-002/WEB_INLINE_IR001-SECURITY-20261101.md`, blob `e9b75c38d8ebd6c7dedd777a5455746b93cda6b5`. `IR001_FAIL_SECURITY_PROMOTION`, F001–F004 blockers, F005–F006 advisories.
**Provenance path addendum:** `mauedgar/ts-execution-transport@60743e0ca21143a972a3699f3dc4eaf04f3df9d6:handoffs/TS-BEADS-047B-ARTIFACT-ACQUISITION-20261101-001/PROVENANCE-CORRECTION-20261101.md`.
**Frozen DoD:** `mauedgar/ts-execution-lab@e02c611dec74ce5d2ddcd5c169f407543ef2e3c4:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.
**Frozen security contract:** `mauedgar/ts-execution-lab@f88e30cdce5a092b4a84c7a75987dba47063f00d:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/SECURE_HOST_PROVISIONING_REQUEST_20261101.md`, blob `7ebec00133736a74431516171deee614f3dbaed1`.

## Repair scope: same 047B dependency, no new Product gate

Produce a **new** reviewable candidate for a bounded *effectful* native Windows Dolt SQL bootstrap, plus test harness, input schema, secret-handling procedure and immutable source provenance. Do NOT call the former 002 script an effectful runner; it is only a static environment preflight.

### Mandatory design and implementation

1. Explicit operation, host `DESKTOP-DJLBEQH`, authorized owner/device identity, unique new `ExecutionAttempt` for any future conditioned effect, no duplicate/UNKNOWN historical provider effect and no second writer. Never run a new SQL process while constructing or statically validating the candidate.
2. Separate a safe **preflight-only mode** (no writes) from a strictly conditioned effect mode, and enforce exact allowlisted data root `%LOCALAPPDATA%\TS-BEADS-047B`; reject path traversal, symlink/reparse points, non-directory collisions, unprotected ACLs, unexpected preexisting state and non-Windows host.
3. Use OS CSPRNG for independent root/writer/reader secrets locally; user/host-scoped DPAPI or Credential Manager and restricted ACLs. No secret values in command args, env dumps, repository contents, transcript, process invocation, stdout/stderr or error messages. Secrets must not be accidentally echoed through SQL commands or provider exceptions.
4. Bind Dolt 2.2.0 to **127.0.0.1:3307** only, with explicit isolated `data_dir`, `cfg_dir`, `privilege_file`, no public listener. Default uninitialized `root@localhost` has no password: ensure passwordless/anonymous root is not left valid before any tailnet ingress, configure protected writer scoped to `ts047b_beads` and SELECT-only reader; independently test wrong-password, reader mutation denial and SQL principals via local loopback. The local `dolt sql` superuser bypass means OS ACL isolation is mandatory; no claim that grants protect a privileged local filesystem owner.
5. Verify exact Dolt 2.2.0 syntax and SQL user operations from the pinned **local native executable** in **no-effect** help/version/syntax preflight or provider-pinned source before SQL deployment. Do not assume `dolt sql-server --user/--password` exists (removed as of Dolt 1.49), nor silently assume `ALTER USER`/optional MySQL features work; unsupported grammar must `BLOCKED_PRECONDITION` before effect.
6. Before effect: verify unique prior attempts/receipts and absence of SQL/Serve side effects at provider, host identity, native version + binary hash, peer tailnet ACL, occupied 3307, existing lab root, stale provider process and startup permissions. A missing directory alone is not sufficient proof of absence of a prior effect.
7. Once-only runner: parser/hash verification → all local/provider preconditions → conditioned loopback SQL bootstrap and *immediate safe hardening* → local positive/negative auth/permission tests → compact sanitized receipt. On partial effect or UNKNOWN preserve state/identity, do NOT delete/mutate/retry automatically. Only after **independent PASS and explicit conditioned effect invocation** may any SQL server run; Serve/Funnel remain disabled until all local tests pass.
8. Tailscale Serve TCP can forward to loopback using `tailscale serve --tcp=<port> tcp://localhost:<local-port>`, but must NOT activate during candidate construction or pre-SQL hardening; never use Funnel, WAN exposure, 0.0.0.0 listeners, or implicit fallback to embedded/local DB.
9. Test cases must assert exact expected failure reason for wrong host, effect identity, stale directory/reparse point, mismatched binary hash, ACL, secret store, unexpected Serve, occupied port, partial provider effect, auth setup failure, privilege/anonymous access and duplicate attempt. Include positive fixture without live SQL, negative source bypass fixtures, provider-mocked SQL and idempotency behavior. No unconditional `PASS` booleans as proof of provider non-effects.
10. All new files remain isolated to the existing experimental lab/Transport area, with exact commit/tree/sha and sanitized test receipt. No Product/Kernel migration, FitFlow paths or TaskCycles. Avoid slow semantic repo exploration; consume the pinned files directly by GitHub URL and work only in the experiment directory.

### Stage boundary / return

**This repair request authorizes static candidate construction/review preparation only**; it is not a SQL start command. The first delivery is frozen source, parser + negative fixture transcript and a claim of *STATIC_* status; independent ChatGPT Web review must then PASS before effectful SQL invocation and real host preconditions. If secure provisioning with protected secrets or pinned SQL syntax cannot be implemented or tested, report `BLOCKED_PRECONDITION` with exact missing capability, not a false PASS.

**Authoritative contemporary references (must confirm 2.2.0 behavior):**
- https://www.dolthub.com/docs/sql-reference/server/access-management/
- https://www.dolthub.com/blog/2025-02-05-sql-server-removes-user-pass-args/
- https://www.dolthub.com/docs/sql-reference/server/configuration/
- https://tailscale.com/docs/reference/tailscale-cli/serve
