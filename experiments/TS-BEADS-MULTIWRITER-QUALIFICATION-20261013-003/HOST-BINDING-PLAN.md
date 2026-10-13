# TS — Beads multiwriter qualification | Host-bound technical plan

Date: 2026-10-13
Classification: NONPRODUCT_EXPERIMENT; HOST_BINDING_PENDING
Owner: experimental Beads evaluation; no TaskCycle or Product authority
Active host: DESKTOP-3LJ0E54; device 777b57a0-70df-4bd6-b9ed-f6a4998e6022
Parent: mauedgar/ts-execution-lab@e6a48ba7a4f39c4870f6bb4a4bbdd3984e348ca9:experiments/TS-BEADS-EVALUATION-CHARTER-20261013-001/EXPERIMENTAL-CHARTER-AND-DOD.md
Related: experiment/beads-concurrency-20261013-003@42af3c08e7f6d303563548871f38dbb3d62d335b
Existing Pilot 003 attempt BEADS-CONCURRENCY-LOCAL-20261013-001: NOT_EXECUTED; runner and manifest are frozen fail-closed with dispatch_authorized=false. Do not unlock by editing Boolean alone.

## Current evidence and compatibility

- The fixed mechanical host check `dolt version` returned PowerShell CommandNotFound on 2026-10-13. This means **not available on PATH**, not necessarily absent anywhere on the host. No installation attempted.
- Beads v1.3.1 upstream documentation: embedded storage uses in-process **single-writer**, intended for solo use; for genuinely concurrent clients, run a standalone Dolt SQL server and initialize Beads in server mode.
- The version-specific standalone Dolt CLI pin is **v2.2.0**. The upstream docs warn of empirical hard-reset regressions in v2.3.0/v2.3.1; do not install `latest` or automatically upgrade.
- GitHub release Windows x64 archive: `https://github.com/dolthub/dolt/releases/download/v2.2.0/dolt-windows-amd64.zip`, size `40057960` bytes, official GitHub release API SHA256 `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`.
- Existing local Beads 1.3.1 original isolated binary is already verified against Pilot 001 receipt; no need to reinstall Beads. As a reference only, upstream Beads Windows archive SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`.
- Sources: https://github.com/gastownhall/beads/blob/v1.3.1/docs/architecture/dolt.md, https://github.com/gastownhall/beads/blob/v1.3.1/docs/reference/faq.md, https://github.com/dolthub/dolt/releases/tag/v2.2.0 and https://github.com/gastownhall/beads/releases/tag/v1.3.1 .

## Isolated qualification (authorized experimental scope, not yet performed)

1. Use the existing approved **Git/file transfer** mechanism or a separately delivered archive to place the exact Dolt 2.2.0 release in an experiment-only folder; **do not use Commander as a ZIP/script/manifest materializer**, do not add global PATH, do not modify repository Product files. Hash-verify source archive before extraction or execution. If qualified file transfer is unavailable, report `HOST_BINDING_PENDING` and keep advancing independent work.
2. Freeze a bound manifest containing exact host/device, binary SHA, path, process owner, loopback-only port, data directory, attempt ID, deterministic bounded runner Git blob, expected start/stop result receipts, and no-replay guard.
3. Use an ephemeral Dolt server on `127.0.0.1` with **separate isolated data** and a verified unused port, not any existing user's Dolt database. Start only once after preflight. Confirm version `2.2.0`, server readiness, authentication/access constraints and a single-writer control. Record server PID and own start receipt.
4. Explicitly `bd init --server` / `BEADS_DOLT_SERVER_MODE=1` with matching host/port; observe read/write smoke and shutdown/liveness independent of other experiments. No upstream Gas Town `gt` dependency is required for this bounded test if native `dolt sql-server` is already available.
5. Run **supported multiwriter** test: two simultaneous independent clients on separate synthetic responsibilities, exact UTC operation intervals and barrier, readback by a third process, error/lock preservation, no collisions of **issue IDs**. Next test **semantic source-ref identity**; Beads hash IDs are **not** a native proof that same SOURCE_REF creates one issue.
6. Classify and reconcile separately: `SERVER_BINDING_PASS/FAIL/BLOCKED/UNKNOWN`; `CONCURRENT_DISJOINT_WRITE_PASS/FAIL`; `SEMANTIC_SOURCE_DUPLICATES_OBSERVED` or `SINGLE_SOURCE_RECORD_PROVEN`; and `INDEPENDENT_READBACK_PASS/FAIL`. For unknown effect, do not terminate, delete or blindly replay attempt.
7. Before a Product adoption proposal, compare operational burden of hosting a service versus single-writer embedded plus ordered ingestion. A server should **not** become a default TS Product dependency merely because this experiment supports it.

## Work already independent of server

The separate Pilot 004 has a terminal local `PASS_SYNTHETIC_CONTINUITY`: dependency B was registered while A was in progress, independent C remained ready, and a new process resumed A only after B was synthetically closed, with independent third-process readback. See `mauedgar/ts-execution-lab@f154204574fe24e0ea75cfcf3f9b6d994528f817:experiments/TS-BEADS-DEPENDENCY-RECOVERY-20261013-004/PILOT-RESULT-20261013-004.md`.

No version on PATH or GitHub release metadata proves an installed local server. No attempt or receipt for concurrent multiwriter execution was created in this qualification.
