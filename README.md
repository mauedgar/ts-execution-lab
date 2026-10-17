# ts-execution-lab

Execution/binding lab for deterministic command-execution experiments. Authority: NONE. Product effect: NONE.

Not Product SOT, lifecycle authority, knowledge SOT, or an orchestrator.

## Layout

- docs/execution-surface-v0.md — initial routing rules
- schemas/execution-receipt-v0.schema.json — receipt schema
- scripts/emit-receipt.mjs — receipt emitter (Node built-ins only)
- .github/workflows/remote-smoke.yml — remote smoke workflow
- bootstrap/dispatch-receipt.yaml — workflow dispatch receipt
- docs/stations/TS-DEV-UX-NOTEBOOK-PROVISIONAL-20261015.md — **provisional, non-Product** notebook/workspace execution map; Beads and Upper LC still pending

## Notebook toolchain check (non-Product)

- `scripts/station/Assert-Node22Npm10.ps1` checks the **exact** Windows `fnm` Node 22.23.3 + bundled npm 10.9.9 pair without changing system `PATH`, running npm scripts, or installing dependencies. It is a technical assertion, not a bootstrap or Product acceptance.
- Refer to `docs/stations/TS-DEV-UX-NOTEBOOK-PROVISIONAL-20261015.md` for the provisional Windows/WSL workspace mapping. Beads and Upper LC decisions remain deferred.

## OpenCode CI OAuth pilot (non-Product)

- **Primary execution:** notebook via Orca/OpenCode2 and Commander. **Secondary option:** manual protected GitHub Actions through [`opencode-ci-oauth-pilot.yml`](.github/workflows/opencode-ci-oauth-pilot.yml), with per-run model selection and human Environment approval.
- **Technical scope:** `COMPLETE — OBJECTIVE_ACHIEVED`, two independent ChatGPT OAuth inference/secret-refresh runs without a conventional OpenAI API key. PAT lifetime configured to 90 days; renew manually when needed. Other providers and Product integrations remain out of scope.
- **Operational detail:** [notebook station profile, §9](docs/stations/TS-DEV-UX-NOTEBOOK-PROVISIONAL-20261015.md#9-opencode-ci-chatgpt-oauth--cierre-de-piloto-2026-10-16). **Exact evidence:** [cross-run technical return](https://github.com/mauedgar/ts-execution-transport/blob/c35e3a2b62b1f2ca679d863b8713d0af6c8d69db/results/TS-DEVUX-OPENCODE-CI-OAUTH-CROSS-RUN-QUALIFICATION-20261016-001/TECHNICAL_RETURN.md). This pilot is not a Product SOT, acceptance, or authorization to dispatch Product work.
