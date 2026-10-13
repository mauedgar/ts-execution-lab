# TS-BEADS-CONTINUITY-PILOT-20261013-001

Experimental Windows-local Beads continuity pilot (not Product, no TaskCycle, no GitHub Projects effects).

**Owner:** Experimental evaluation, not Product Control. **ExecutionAttempt:** `BEADS-LOCAL-TRIAL-20261013-001`.

Purpose: create synthetic active responsibility, register nonblocking incoming handoff while active, finish active, verify pending handoff from a *fresh process*. No production handoffs or real issue IDs are imported.

Transport: this frozen branch is a deployment carrier only. Files are read from an exact Git commit in `mauedgar/ts-execution-lab`; no code is fetched from main at runtime. For terminal results, `result.json` and `fresh-process-readback.json` are left in the isolated local directory. Git Transport publication is *not assumed*: existing native publisher only has offline qualification, and the current host binding must be qualified separately before any remote write.

Local workspace: `%LOCALAPPDATA%/TS-Experiments/TS-BEADS-CONTINUITY-PILOT-20261013-001`. Fail closed if present. Download vendor archive only from `gastownhall/beads` stable v1.3.1, validated by upstream-published SHA-256 (`48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`). No system-wide npm/global PATH, Git hooks, Docker, MCP, GitHub Projects or Product changes. Only files under the isolated workspace are modified by the pilot runner.

Manifest: `manifest.json` pins both scripts' SHA-256, release/checksum, attempt and output; `runner.ps1` verifies them before effect. Repeated execution is **not** a retry: workspace-exists guard blocks. On FAIL/UNKNOWN reconcile local result first, do not blind retry.

Dispatch as two bounded mechanical operations: once to acquire frozen source into a new local carrier checkout, once to execute a fully predetermined `pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <checkout>\\experiments\\...\\runner.ps1`. Commander has no semantic role or polling. Acquire final output from native durable result via existing Transport binding *if qualified*, or one terminal result retrieval / file export, rather than reading local files granularly.

**Acceptance**: verified install hash; no Product effects; one active and one handoff; handoff is ready while active; after active close, fresh PowerShell process sees active closed and handoff still open and ready; no duplicate created; receipt readable with exact attempt/ids/host. **Limitations**: Beads does not automatically know that a ChatGPT Web TaskCycle finished; selection and Product decisions remain separate; real duplicate-hand-off behavior and cross-host transport are not yet qualified; no MCP phase in scope.
