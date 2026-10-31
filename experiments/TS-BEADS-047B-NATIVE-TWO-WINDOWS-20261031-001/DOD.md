# TS-BEADS 047B — Two native Windows hosts, one notebook Dolt SQL service

**Date** 2026-10-31. **Authority** `EXPERIMENTAL_CONTROL_ONLY`; **Product effects** `NONE`.
**Status** `PREPARE_NONCONFLICTING_VARIANT / NO_LIVE_SQL_EXECUTION_STARTED`.
**Operation candidate** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, NOT a retry of the terminal 045/046 or original 047 static runs.
**Source branch** `mauedgar/ts-execution-lab:experiment/beads-047b-native-two-windows-20261031-001`, from exact 047A preparation commit `b9be864a498355d4d7d03e7fd6c65cb01b66081e`.

## State reobserved
- Notebook: authorized desktop commander device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2`, Windows hardware distinct from desktop; Tailscale backend `Running`, online `True`, installed Dolt 2.2.0 and Beads 1.3.1. Notebook is the intended SQL primary; no SQL listener at 3307 and no Tailscale Serve proxy observed in 047A.
- Desktop: authorized commander device `777b57a0-70df-4bd6-b9ed-f6a4998e6022`, distinct Windows host, Tailscale backend `Running`, online `True`. Native Beads 1.3.1 installed via WinGet with package integrity verification in original terminal installer result.
- Both devices observe the other online and each original bounded Tailscale peer ping yielded `PING_OK`. No private IP or tailnet name serialized to this public repository.
- Original 047A source and static PASS run `41215865528` remain frozen and DO NOT dispatch live SQL. Original one-off GitHub Actions sentinel absent. We deliberately do not alter that original operation.
- Product SOT `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remains separate; existing lab `refs/dolt/data=1f72d68797114170a97fee27641858f2e55a4571` untouched.
- 042, 045 original run `41177022889`, 046 original run `41210661485` and DC044 original run `41177310449` preserved as terminals. Reusing their methods is not rerunning their effects.

## Architecture adaptation
- Endpoint abstraction remains `server_host` (tailnet private address), `server_port=3307`, `database=ts047b_beads`, `writer user`, `reader user`, credentials from protected native host secret store; no hardcoded private IP, password, automatic local fallback or new Product Kernel.
- **Notebook:** native Dolt SQL v2.2.0, loopback `127.0.0.1:3307` only, isolated native directory under current user's local application data; Tailscale Serve TCP forwards private tailnet TCP/3307 to loopback; NEVER Funnel, raw public SQL port, router forwarding, or 0.0.0.0 binding.
- **Desktop:** native Beads v1.3.1 connects to notebook via tailnet DNS/IP using `BEADS_DOLT_SERVER_MODE=1`, `BEADS_DOLT_SERVER_HOST`, `BEADS_DOLT_SERVER_PORT=3307`, `BEADS_DOLT_SERVER_USER`, `BEADS_DOLT_PASSWORD`; use `bd init --server --database ts047b_beads` with fresh isolated workspace, no copies of notebook workspace or Kernel. Confirm Beads project identity is adopted from existing server DB; if mismatch, fail closed.
- **Authentication:** SQL service must have nonblank root administrator password before tailnet proxy is enabled. Dedicated `ts047b_writer` scoped to the lab database only and separate SELECT-only reader. No secret values in Git, ChatGPT, Commander command arguments/results, logs or original portable receipts; do not use anonymous SQL, even on tailnet. Existing same-tailnet peer connection is NOT a bypass for SQL authorization.
- **No OAuth needed** for two computers already members of the same tailnet. This adaptation is independent of TinyFish browser availability, GitHub Actions ephemeral runner tags, OAuth and five GitHub repository secrets. A third ephemeral GitHub runner remains future/incremental and not presumed available.
- **Boundary:** Commander is only the bounded execution/result surface, not for semantic discovery, interactive file edits or script/payload materialization. Scripts and frozen subject materialized through GitHub/normal repo surfaces, parse/integrity checked BEFORE any Commander launch. Never use `start_process` to write/create scripts or transport an encoded payload.

## Preflight stop conditions
1. Freeze Git subject/DoD/native source and static validation. Confirm exact host identity and both peers still `Running/Online`, independent tailnet pings and installed native version outputs.
2. No existing port 3307 occupant, lab DB/dir or uncertain previous 047B write; no Product DB paths; no previous `ExecutionAttempt` with same identity.
3. Only after atomic secure root-password provisioning, scoped SQL users and positive/negative SQL auth confirmation while bound to loopback: activate Tailscale Serve private forwarding. Verify desktop can reach only the specific notebook TCP service. Test denial of invalid credentials and read-only native mutations.
4. Maintain one operation identity, original host receipts with exact native issue graph, provider and mutable checkpoint; no duplicate write owners or auto retries.

## Empirical DoD, separate from 047A
1. Notebook creates synthetic 5-issue graph `preflight→alpha/beta→join→parent` using native Beads; SQL state on notebook remains the only store.
2. Desktop from fresh workspace and no copied `.beads` metadata/Kernel uses native `bd init --server --database`, validates project identity, graph/ready/history, closes Alpha; notebook closes Beta; both roles and native histories corroborated. Distinct host identities verified without public host identifiers.
3. Disconnect notebook CLI (not SQL service), verify desktop still independently reads/writes authoritative SQL. Then simulate SQL-primary disconnection separately: desktop detects unavailable state and fails closed without embedded fallback, no attempt to close Join or replay uncertain provider effects.
4. Restore notebook service with original native SQL data and verify desktop reconnects to same project identity and closes Join/Parent only once, with original role receipts and no shadow write.
5. Negative authorization: wrong password, read-only SQL user via direct SQL and native Beads CLI, unexpected public listener, stale project identity and concurrent update conflict fail closed. No override by alternate Dolt CLI/privileged writer.
6. Exceptional off-host backup (separate finite operation): native Dolt backup archived to **desktop or another isolated GitHub backup ref** with actual hash, cutoff and restore test on third fresh directory; do not copy live `.dolt` storage. No HA claim or automatic promotion; fence original primary before any restoration as writer. Measure RPO/RTO only after empirical runs.
7. Original provider UNKNOWN: provenance from real external provider action, exact immutable receipt and observed effect, no blind re-dispatch. Synthetic loss of a CLI response alone cannot prove complete provider UNKNOWN reconciliation; classify limitations honestly.
8. Source/code absorption: inventory candidate ownership with 045 85,014-byte footprint as hypothesis only; run lab deletion/measurement if justified. Product bytes removed remain **0** unless separately authorized Product change.

## Final verdict contract
`HOST_INDEPENDENCE_GO` only if full interhost outage, receipt reconciliation and recovery/backup/permissions are empirically proven. Otherwise `HOST_INDEPENDENCE_INCOMPLETE` or `NO_GO`, specifying exact original evidence and missing tests. A passing dual-client SQL fixture alone is **NOT** the full verdict.

## No launch
No 047B SQL service, credentials, Tailscale Serve, live Beads graph or backup has been started by creating this document. Both users' Tailscale logins and native Beads install can be reused without an OAuth panel. No Product authority, TaskCycle, #35, FitFlow, old attempts, Kernel deletion, or paid service.
