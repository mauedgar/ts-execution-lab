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
