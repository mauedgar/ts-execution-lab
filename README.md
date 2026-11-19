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

## Current execution routing (non-Product)

- **Operating authority:** [`TS Execution Engineering Autonomous Operating Contract v1`](docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md); it controls execution mechanics only. Product selection, TaskCycle transitions, Developer acceptance and integration stay with competent Product Control.
- **Local OpenCode2 semantic execution:** launch only from a **visible Orca-owned terminal** (Windows or WSL) on the previously authorized host/worktree, following [`ORCA Developer UX v1`, §7.1](docs/execution-engineering/ORCA-DEVELOPER-UX-v1.md). Commander is restricted to bounded mechanical execution/transport/result handling; it is **not** an OpenCode2 semantic launcher, repository reviewer or source-editing surface.
- **GitHub Actions OAuth pilot:** optional, task-specifically admitted, through [`opencode-ci-oauth-pilot.yml`](.github/workflows/opencode-ci-oauth-pilot.yml), with per-run model selection and required Environment approval; historical pilot success is **not** present authorization or credential freshness proof.
- **Risk-adaptive delivery:** [`method v1`](docs/execution-engineering/TS-EE-RISK-ADAPTIVE-DELIVERY-v1.md) is a bounded FitFlow experiment, not automatic policy for Aware, Attendance, Tecnotron or TS Remote State.

## OpenCode CI OAuth pilot (historical, non-Product)
- **Technical scope:** `COMPLETE — OBJECTIVE_ACHIEVED`, two independent ChatGPT OAuth inference/secret-refresh runs without a conventional OpenAI API key. PAT lifetime configured to 90 days; renew manually when needed. Other providers and Product integrations remain out of scope.
- **Operational detail:** [notebook station profile, §9](docs/stations/TS-DEV-UX-NOTEBOOK-PROVISIONAL-20261015.md#9-opencode-ci-chatgpt-oauth--cierre-de-piloto-2026-10-16). **Exact evidence:** [cross-run technical return](https://github.com/mauedgar/ts-execution-transport/blob/c35e3a2b62b1f2ca679d863b8713d0af6c8d69db/results/TS-DEVUX-OPENCODE-CI-OAUTH-CROSS-RUN-QUALIFICATION-20261016-001/TECHNICAL_RETURN.md). This pilot is not a Product SOT, acceptance, or authorization to dispatch Product work.

## Frontend Browser QA common method (non-Product)

- [TS Frontend QA Common v0](docs/execution-engineering/TS-FRONTEND-QA-COMMON-v0.md) is the stable TS EE lab method entrypoint. It links the bounded Playwright/receipt source, safe-by-default CLI, actual CI, independent review, native artifact readback and explicit Product authority limits. Aware is the intended first consumer but remains NOT_ADOPTED.
- Optional private skills-only [TS Frontend QA plugin](https://chatgpt.com/plugins/plugins_6aff5120ae14819190a85f34e7b57d1f) routes requests; no Product or merge authority.
