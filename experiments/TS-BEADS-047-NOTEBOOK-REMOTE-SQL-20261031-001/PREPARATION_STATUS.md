# TS-BEADS-047 — Prepared native Windows notebook; live remote SQL not dispatched

Date: 2026-10-31. Authority: EXPERIMENTAL_CONTROL_ONLY. Product effect NONE.
Responsibility TS-BEADS / TS Execution Engineering. Product SOT unchanged `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`.

## Verified local notebook preflight and bounded package installations
- Identified one online Windows notebook device via authorized Remote Desktop Commander, with an HP laptop hardware model, about 8 GiB physical memory and 100,526,727,168 available bytes on drive C. Exact hostname, tailnet IP and user details deliberately omitted from public report.
- WSL Ubuntu-24.04 exists but WSL2 failed to start, `HCS_E_HYPERV_NOT_INSTALLED` / virtualization unavailable. **No BIOS changes or WSL repair**. Use native Windows binaries.
- Windows Tailscale installed from WinGet `Tailscale.Tailscale@1.104.4`. WinGet verified MSI SHA256 `1d12cd8b1d6dbb447da8579b1a5268ae2fc050967bebfaa02e32d2bb645ef6ee`; installer returned `Instalado correctamente`. Windows service `Tailscale` was Running/Automatic. Native Tailscale status backend `NeedsLogin`; **NOT authenticated and no tailnet exposure configured**.
- Windows native Dolt installed from WinGet `DoltHub.Dolt@2.2.0`; package hash verified by WinGet; exact installer returned `Instalado correctamente`. Native SQL server NOT started. No SQL user credentials or database yet provisioned.
- Windows native Beads installed from WinGet `GasTownHall.Beads@1.3.1`; hash verified by WinGet; installer returned `Instalado correctamente`, command alias `bd` and PATH update (new user shell may be needed). No native Beads Product or local experimental DB initialized.
- No Tailscale sign-in, SQL listener, firewall rule, port forwarding, paid cloud, credential creation or external provider command was attempted.

## Durable lab source and static qualification
- Branch `experiment/beads-047-notebook-remote-sql-20261031-001` in `mauedgar/ts-execution-lab`.
- Live SQL client `experiments/TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001/native047.py` blob `8ca873d5c1825c3e0ad6a1fbf6dff8cdd5d2b8b5` (provider-neutral SQL endpoint via environment).
- Exact DoD blob `85e3bbe1b0e795ce46b3a517ef2e930a434faf07` and independent native toolchain action blob `c45410c64eb63d80215549ed2688075d52c79c06`.
- Main execution workflow `.github/workflows/ts-beads047-notebook-live-sql.yml` is **push-sentinel gated** on exactly `EXECUTE_047_ONCE.txt` in this experiment folder. The sentinel has not been created. Pushes of sources, reports or workflow DO NOT launch live SQL. Run attempt `TS-BEADS-047-ACTIONS-ATTEMPT-001` remains NOT STARTED.
- One independent **STATIC ONLY** GitHub Actions run `41214259307` at Git commit `c3e2ef48410694686e057b5aaed2e3a5e32f8ed6`, run_attempt=1, `completed/success`, job `124575381053`, original artifact `13046578981`, ZIP SHA256 `0dadfcde2d342af3f806b81f2f17bb817bfd8d4f72907b04209b5f814c61fbab`. Python source compiled; YAML job edges/credential references/one-off sentinel were validated. No SQL attempt was launched.
- Nothing altered `mauedgar/ts-execution-lab` shared `refs/dolt/data` intentionally; no Git remotes push/retry in 047.

## External and host operational prerequisites (not inferred)
1. **Human-only**: sign in to Tailscale on the notebook, backend state must become Running. Use free Tailscale Personal for noncommercial lab use, check tailnet eligibility. The login must not be delegated to an unauthenticated remote CLI with exported tokens.
2. Configure Tailscale Serve TCP on the host with `tailscale serve --bg --tcp=3307 tcp://127.0.0.1:3307`, only after verifying private access policy for `tag:ts047-ci`; **never Funnel/public router forward**.
3. Using already installed native Dolt, initialize isolated `ts047beads` SQL DB and start the Dolt server on loopback only. Harden SQL root; create dedicated `ts047_writer` (scope ts047beads) and `ts047_reader` (SELECT-only) with independent random credentials, deny invalid auth and SQL writes from reader.
4. In Tailscale admin console create/restrict `tag:ts047-ci` and OAuth client with `auth_keys` scope and tag. In **GitHub encrypted repository secrets**, configure `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TS047_SQL_HOST`, `TS047_SQL_PASSWORD`, `TS047_RO_PASSWORD`. No secret values should enter this report/chat.
5. Verify exact network reachability and host+DB identity and no previous unknown/partial 047 effect. **Only then** create the predesigned GitHub dispatch sentinel once to run 047; never rerun an ambiguous attempt.
6. Backup exception: 046 proved original cross-host cold recovery; 047 needs separate off-host native backup destination (prefer dedicated isolated GitHub repo with native Dolt refs, no existing `refs/dolt/data`), integrity and restore test. Until that mechanism is qualified, notebook disconnection must FAIL CLOSED with no automatic second writer/failover.

## Current terminal observation
`READY_WITH_EXTERNAL_PREREQUISITES`, live SQL status `BLOCKED_EXTERNAL_TAILNET_IDENTITY_AND_SQL_CREDENTIALS`, not FAIL, not PASS, not a Product state. Next permitted independent task is to prepare secure native host runner plus backup transport, without starting 047 provider attempt before credentials. Next required human step is signing in Tailscale; afterward verify device authentication and create scoped credentials/secrets.
