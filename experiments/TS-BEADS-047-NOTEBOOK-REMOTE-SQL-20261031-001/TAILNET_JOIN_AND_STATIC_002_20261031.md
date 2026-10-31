# TS-BEADS 047 — Notebook tailnet join / corrected static candidate 002

Date: 2026-10-31. Authority: EXPERIMENTAL_CONTROL_ONLY. Product effects NONE. No live 047 SQL attempt dispatched or initialized.

## Observations and original identities
- Authorized notebook Windows device Tailscale 1.104.4 status returned `BackendState=Running` and `Online=True`. Device identifier and IP deliberately omitted from portable report. This resolves host-side tailnet login dependency only.
- Native Windows Dolt verified `dolt version 2.2.0`. Native Windows Beads verified `bd version 1.3.1`; both were installed previously through hash-checked WinGet.
- Preflight: no Dolt process/listener observed on TCP 3307. Tailscale Serve TCP is not yet configured. No SQL database or writer/reader credentials provisioned.
- GitHub CLI query `gh secret list --repo mauedgar/ts-execution-lab --json name` returned successfully with empty secret-name output at observation. The planned five secret names were not confirmed configured; **never infer credentials or launch**.
- Product SOT `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remained unchanged at last source observation.
- Prior terminal 045 Actions run `41177022889`, 046 `41210661485`, DC044 `41177310449`, and original 047 static candidate 001 `41214259307` all preserved; none re-dispatched.

## Corrected 047 002 candidate
- Repository `mauedgar/ts-execution-lab`, experiment branch `experiment/beads-047-notebook-remote-sql-20261031-001`.
- Corrected native source: `experiments/TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001/native047.py`, Git blob `f8713242d37f9ebdef5ff12baa10d0336b65bb29`.
- Original DoD blob `85e3bbe1b0e795ce46b3a517ef2e930a434faf07`; original native toolchain action blob `c45410c64eb63d80215549ed2688075d52c79c06`.
- Main SQL workflow `.github/workflows/ts-beads047-notebook-live-sql.yml`, blob `2c44df5ca73faa6a396757191fd10f084d061a4a`. It is gated by an exact **absent** one-shot sentinel, never triggered by code/report modifications.
- Separate static validation **candidate 002**: GitHub Actions original run `https://github.com/mauedgar/ts-execution-lab/actions/runs/41215865528`, source commit `3d37d99152a4126dfbff81db788684f5235c8abd`, `run_attempt=1`, `completed/success`, job `124580132130`, artifact ID `13048301209`, ZIP provider digest `sha256:ec8e486eca44f83b4656f8d61b827a1070b974efe391a287c25a07c268fed7a1`. This proves only static syntax, code-hash freeze and expected workflow/job structure, not live SQL.
- C001 fixed: private endpoint attestation now keyed HMAC, not SHA of a small IP address.
- C002 guarded: refuse publishing portable metadata if bytes include runtime private host or SQL credentials; does not prove the metadata will pass with actual Beads. Fails closed if it does not; no silent leak.
- C003 fixed: record remote-write intent before native mutation; classify errors after a possible write as `UNKNOWN_REMOTE_WRITE_OUTCOME_REQUIRES_RECONCILIATION`, not definitive FAIL or automatic retry.
- C004 expanded: attempt native Beads CLI write with restricted SQL reader and require denial in addition to direct SQL denial. These are lab negative tests only.
- Explicit tailnet-only endpoint check and no local embedded/shadow Dolt store, as well as original provider receipt identities.
- C005 remains LIVE_SQL_UNQUALIFIED; static checks do not establish functional SQL/Windows interoperability. Negative revocation, forced A crash, actual provider UNKNOWN reconciliation and off-host backup still require empirical gates.

## Next exact independent prerequisites and deferred join
1. On Tailscale admin console, create `tag:ts047-ci` and grant only TCP/3307 to the authenticated notebook. Create an OAuth client scoped to `auth_keys` and that tag. Use OAuth only in GitHub encrypted Secrets; never in chat/repo/Commander logs.
2. In `mauedgar/ts-execution-lab` GitHub repository Actions Secrets, configure `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TS047_SQL_HOST`, `TS047_SQL_PASSWORD`, `TS047_RO_PASSWORD`. Private SQL host must be 100.64.0.0/10 Tailscale address or a specific `.ts.net` hostname.
3. On notebook, independently isolate Dolt SQL at `127.0.0.1:3307` in a fresh lab-only storage root and database `ts047beads`, harden root and provision restricted writer `ts047_writer` and read-only `ts047_reader`, confirm failed empty/wrong SQL password and deny public ingress. Only after ACL and credentials, enable private Tailscale Serve TCP forwarding. No auto-start scheduler/gateway/new kernel.
4. When host and secrets meet all exact checks, create the single frozen GitHub sentinel once (NOT done). Start a single provider run `TS-BEADS-047-ACTIONS-ATTEMPT-001`; join original producer/worker receipts, preserve failure/UNKNOWN without retry, accept only exact DoD.
5. Exceptional notebook loss: pause/no dual writer; 046 proved native cold backup transfer in a separate test but 047 does NOT yet have off-host durable backup. Select separate isolated GitHub remote and prove native Dolt backup + restore and RPO/RTO before claiming operational disaster recovery.

Current verdict `HOST_INDEPENDENCE_INCOMPLETE`. Current experiment gate `READY_WITH_PRECONDITIONS / BLOCKED_HOST_SQL_AND_GITHUB_OAUTH_SECRETS`. No Product adoption and zero bytes Product deleted.
