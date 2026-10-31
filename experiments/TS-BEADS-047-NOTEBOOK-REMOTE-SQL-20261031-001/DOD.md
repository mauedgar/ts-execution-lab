# TS-BEADS-047 — Notebook-hosted live SQL / provider-neutral endpoint

**Date:** 2026-10-31. **Authority:** EXPERIMENTAL_CONTROL_ONLY. **Product effects:** NONE.
**Responsibility:** TS-BEADS (not Beta Control). **Current gate:** PREPARED / BLOCKED_EXTERNAL_TAILNET_IDENTITY; **no live 047 ExecutionAttempt dispatched**.
**Operation candidate:** `TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001`.
**Expected provider ExecutionAttempt when prerequisites pass:** `TS-BEADS-047-ACTIONS-ATTEMPT-001` on ONE manually dispatched GitHub Actions run, run_attempt=1; unique client role identities bootstrap, alpha, beta, join. Do NOT create this Attempt while missing credentials or endpoint; never replay if UNKNOWN.
**Branch:** `experiment/beads-047-notebook-remote-sql-20261031-001` in `mauedgar/ts-execution-lab`. Freeze exact commit/tree and native script blobs before execution. **Do not run simply on source push**.

## Frozen authority/evidence
- SOT Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, tree `e6be65e0c3d9aca074218b2fff92e6d42fc76141`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`. Product Kernel disposition remains UNDECIDED; no Product TaskCycle or #35 change.
- Native server-mode prerequisite 045 `41177022889` PASS single host, real host-independence NOT_TESTED.
- 046 `41210661485` PASS cold restore across two independent GitHub-hosted hosts with original native Dolt backup artifacts; real live SQL NOT_TESTED.
- DC044 `41177310449` PASS read-only two-host native Git remote.
- Existing lab `refs/dolt/data=1f72d68797114170a97fee27641858f2e55a4571` must never be mutated by 047.
- Notebook preflight observation 2026-10-31: Windows host accessible through authorized Commander, 8 GiB physical RAM, ~93.6 GiB disk free, WSL2 unavailable due disabled virtualization; Tailscale 1.104.4 installed through official WinGet with verified package hash, service Running/Automatic, auth BackendState=NeedsLogin. No Dolt/Beads present on Windows PATH when observed. Laptop user identity and IP addresses are NOT portable public artifacts.

## Boundary and configuration
- **Host:** Windows native Dolt SQL 2.2.0, single process listening ONLY on loopback 127.0.0.1:3307, isolated laboratory database `ts047beads`; do not alter any Product DB, host Git workspace, global Beads config, Kernel, or external Dolt ref.
- **Private transport:** Tailscale Serve TCP forwarding from the notebook's private tailnet IP:3307 to localhost:3307; no Tailscale Funnel, public router port forwarding, or 0.0.0.0 listener.
- **Client:** Beads native 1.3.1, `BEADS_DOLT_SERVER_MODE=1`, `BEADS_DOLT_SERVER_HOST=<runtime endpoint>`, `BEADS_DOLT_SERVER_PORT=3307`, `BEADS_DOLT_SERVER_USER=<scoped lab account>`, `BEADS_DOLT_PASSWORD=<secret>`, `BD_NO_PUSH=1`; no fallback to embedded store or hidden local server. All native binaries pinned by version; checksums verified before effects.
- **GitHub secrets:** `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TS047_SQL_HOST`, `TS047_SQL_PASSWORD`. SQL username can be a hardcoded dedicated non-root `ts047_writer`; no secret in source or log. OAuth tag `tag:ts047-ci` must be pre-created and authorized in Tailscale ACL/grants for TCP 3307 to exactly the notebook.
- Native bootstrapping has one exclusive coordinator owner; its clean `.beads` metadata (without data DB or credentials) is copied via original GitHub artifact only to independent runner workspaces. The actual SQL DB must remain ONLY on notebook.
- GitHub Actions access: `contents:read`, `actions:read`; ephemeral Tailscale node via official `tailscale/github-action@v4`. No GitHub write token, no provider external task dispatched.

## Prerequisite gate — fail closed
1. Human authenticates laptop to Tailscale. Verify `BackendState=Running` (do not publish node IP/tailnet/private keys).
2. Host installs pinned official native Dolt 2.2.0 and Beads 1.3.1, initializes ONLY an empty isolated SQL server/DB, changes unauthenticated default SQL root to strong credentials, provisions least-privileged `ts047_writer` account for `ts047beads` only, validates wrong passwords rejected.
3. Host runs `tailscale serve --bg --tcp=3307 tcp://127.0.0.1:3307` after private-ACL and Serve prerequisites; verify service reachable only from tagged CI nodes and not a public port.
4. The user configures GitHub encrypted secrets/ Tailscale OAuth client with restricted tag. Never ask for secrets in chat.
5. Before any GitHub dispatch, validate no conflicting existing `ts047beads` data and no prior unknown 047 run, exact host identity and frozen source, auth and grant. Otherwise `BLOCKED_PRECONDITION` and zero effects.

## Live interhost DoD (NOT YET EXECUTED)
1. One bootstrap job independently connects to notebook Dolt over Tailscale and creates exactly five synthetic native issues with graph `preflight→alpha/beta→join→parent`, closes only preflight. No local `.beads/dolt` or embedded engine, verify server-hosted SQL state.
2. Two GitHub runners in **separate parallel jobs** download only the frozen metadata; each independently updates its disjoint child, preserves original provider identity and returns an original artifact. Both write to the same notebook SQL primary; cannot create a shadow DB or trigger remote remotes.
3. Third fresh runner joins original A/B receipts and SQL host identity, checks both children closed, then closes Join and Parent in native Beads readiness order; after host A and B job completion validate all closed and nonempty history.
4. Host failure case: if notebook unreachable, fail closed and preserve last original receipts. Do not switch to embedded/local writer or re-dispatch UNKNOWN. No automatic promotion of stale backup.
5. Security check: authenticated read-only SQL account cannot update native issues; denied writers and wrong SQL credentials fail closed. Runners never receive root admin credentials.
6. Preserve original role JSON and join JSON with exact Git subject, endpoint fingerprint *without leaking URL*, runner IDs and observed state. Prove at least two independent runner hosts from independent provider jobs, not just two processes.
7. PASS only with all original checks, no shadow storage, no Product effects, no UNKNOWN. FAILED/BLOCKED not a grant for retry.

## Exceptional off-host backup and disconnection policy
A connection loss is a **pause/fail-closed event**, not authority to recover on stale data. Keep the notebook as sole writer until explicitly fenced/confirmed offline; detect actual SQL loss separately from GitHub heartbeat. A local backup protects against local Dolt corruption, not against physical loss of the notebook. An OFF-HOST backup must be a native Dolt backup or separately isolated `bd dolt push` remote, with hash, cutoff/epoch and restore test; 046 proves a native backup can be moved to independent hosts but does not establish continuous or permanent off-host publication for 047.
- Before a meaningful irreversible effect and after bounded checkpoints, request a native Dolt backup, then export verified bytes to external storage. Never hot-copy `.dolt` files.
- If notebook goes offline: no automatic failover/no second writer; preserve receipts, recover latest checkpoint, identify RPO gap, reconcile pending provider effects, fence original, only then authorize isolated restore and continue.
- Default permanent backup provider: a distinct isolated GitHub backup repository/ref with no existing `refs/dolt/data`, using native Beads/Dolt push or transport; **not** `ts-execution-lab` existing `refs/dolt/data` and not a finite 30-day artifact as sole permanent backup.
- Disaster recovery/HA/automatic promotion remains NOT QUALIFIED; off-host credential and backup destination provisioning is a distinct precondition before claiming this DoD's backup-dependent acceptance.

## Stop
No notebook identity/secret login in model-owned code; no hosting bills, no public listener, no WSL/virtualization BIOS change, no Product writes, no kernel deletion. In absence of Tailscale login/OAuth secrets/secure SQL user, leave `BLOCKED_EXTERNAL_TAILNET_IDENTITY` and report exact next user action, do not pretend 047 PASS.
