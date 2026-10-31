# TS-BEADS-047 — Native Windows host and private network onboarding (no secrets)

Date 2026-10-31. Intended for the experimentally identified Windows notebook host. This is a **manual identity and credential prerequisite**, not an automatically executed installer or Product runbook.

## A. One essential human-only step
Open the Tailscale application on the notebook, choose Sign in and authenticate with the intended user account. If a personal account is needed, create it from https://login.tailscale.com/start . Confirm that the desktop Tailscale app says connected. Its Windows service and WinGet package `Tailscale.Tailscale@1.104.4` are already installed; do not reinstall. We observed `BackendState=NeedsLogin`. Do not paste a login/auth key, tailnet password or credentials into ChatGPT.

Once signed in, Tailscale can display a private node address; keep it out of public repository documentation. It is an endpoint runtime configuration only.

## B. Private trust boundary
In the Tailscale admin console:
- Create `tag:ts047-ci` and authorize CI ephemeral nodes to access TCP port 3307 on exactly this notebook. Deny unrelated peers where practical.
- Prepare an OAuth client authorized only for writable `auth_keys` associated with that tag; GitHub secret names `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`. Prefer storing them via the GitHub repository Secrets UI or `gh secret set`; do not commit values.
- Tailscale Serve is private to the tailnet, NOT Funnel. After SQL auth is hardened and server is listening on loopback only, enable:
  `tailscale serve --bg --tcp=3307 tcp://127.0.0.1:3307`
- Verify Tailscale ACL controls and `tailscale serve status`; Windows public firewall/router port 3307 remains CLOSED. No public DNS or raw internet SQL port.

Official references:
- https://tailscale.com/docs/integrations/github/github-action
- https://tailscale.com/docs/reference/tailscale-cli/serve
- https://tailscale.com/docs/features/oauth-clients

## C. Native Dolt/Beads database
Pinned packages already installed through authenticated verified WinGet on the notebook:
- `DoltHub.Dolt@2.2.0` (Dolt SQL server).
- `GasTownHall.Beads@1.3.1` (Beads CLI); a new shell may be required to refresh PATH.

After sign-in, use only an isolated directory such as `$env:LOCALAPPDATA\TS-BEADS-047\sql` and database `ts047beads`, not Product or user's existing workspaces. A dedicated host bootstrap must:
1. Check the directory and DB are empty, not an existing/unknown attempt; check Dolt/Beads version and no local port 3307 collision.
2. Initialize a native Dolt database and launch `dolt sql-server --host 127.0.0.1 --port 3307` using that isolated data dir, not a public listener.
3. While network is still closed, require a non-empty root SQL password; create `ts047_writer` with only the lab schema privileges needed by native Beads and `ts047_reader` with SELECT only. Deny empty/wrong credentials and writes from the reader.
4. Store any generated password only in credential storage and GitHub encrypted secrets `TS047_SQL_PASSWORD`, `TS047_RO_PASSWORD`; store the private node address in `TS047_SQL_HOST`. Never print passwords in command traces or GitHub logs.
5. Test native `bd init --server --database ts047beads` only from the one exclusive initializer job; do not initialize a new local embedded database on runners.

This host bootstrap has NOT been executed. Do not use a temporary unsecured root account exposed to Tailscale; authenticate SQL clients independently even though transport is encrypted.

## D. Explicit one-shot dispatch once all five secrets and host gates pass
Workflow: `.github/workflows/ts-beads047-notebook-live-sql.yml`; the workflow deliberately has **no broad push trigger**. GitHub executes it only on an explicit push creating the exact file:
`experiments/TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001/EXECUTE_047_ONCE.txt`
with content `TS-BEADS-047-ACTIONS-ATTEMPT-001`. This sentinel is NOT published until the host is verified. No automatic retry of the resulting run.

Frozen code/config hashes are in DOD.md. The branch remains experimental and cannot authorize Product migration, #35 TaskCycle or Kernel deletion.

## E. Exceptional loss and native off-host backup
- Disconnected notebook: stop SQL clients fail closed; DO NOT auto-promote a backup to live writer or replay provider UNKNOWN.
- Durable backup goal: native `bd backup init/sync` or `bd dolt push` to an **independent dedicated repository/remote** with verified original hash, completed before declaring disaster recovery safe.
- Never push to the existing `mauedgar/ts-execution-lab` `refs/dolt/data` (its existing ref is the frozen earlier experimental `1f72d68797114170a97fee27641858f2e55a4571`). Do not hot-copy `.dolt` while writes are active.
- Preserve original provider receipts in GitHub Transport, reconcile possible in-flight UNKNOWN and fence the original SQL primary before any isolated restore. Recovery from physical notebook loss requires verified off-host bytes; merely having a backup on the notebook is insufficient.
- The 046 original artifact already proved cold native Dolt restore across two independent hosts but is not the new 047 database's off-host backup.

Next action to unlock 047: **sign in Tailscale on the notebook** and verify connected state. Keep GitHub execution sentinel absent until all SQL and credential gates pass.
