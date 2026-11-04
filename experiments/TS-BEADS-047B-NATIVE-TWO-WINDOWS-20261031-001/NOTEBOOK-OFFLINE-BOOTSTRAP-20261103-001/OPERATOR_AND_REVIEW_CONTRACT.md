# TS-BEADS 047B — IR003-A001 fixture-only path probe isolation

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, experimental; not a new TaskCycle or SQL ExecutionAttempt. **Disposition requested:** `SOURCE_ONLY / NO_GO_EFFECT`. No Product, DPAPI, ACL, SQL, Tailscale or original-attempt effects. No implementation or review authority follows from this document.

## Exact baseline, frozen evidence and predecessor

- Parent source-only IR003 candidate `mauedgar/ts-execution-lab@bd60495be30fef40577f07da16f49a5cecfb8a16`, tree `d9e30c434f84d3c86796f827cfb6891f407f77a7`, passed CI `41748241517` attempt 1, 13/13 tests.
- Independent IR003 `mauedgar/ts-execution-transport@94b05a9a30a2f15295bfaa7386ab053a39d01f74:reviews/TS-BEADS-047B-NOTEBOOK-OFFLINE-BOOTSTRAP-20261103-001/WEB_INLINE_IR003_SECURITY.md`, Git blob `a060b6609578ef91cb21e0d73f50e5b53813302e`, 0 source-blocking findings and 2 LOW advisories, `GO_SOURCE_LIMITED / NO_GO_EFFECT`.
- Original DoD Git blob `26388665fc0782fd10b24adca96a7dfa47c6a952` unchanged.
- The original source-only runner was **once** executed on the notebook under a separate immutable identity with exit 0 and `READONLY_OS_OBSERVATION_PARTIAL`. Preserve this terminal evidence, do not rerun to improve status: `mauedgar/ts-execution-transport@a60aad99143f89981442a00f3f22f9056485de9e:results/TS-BEADS-047B-IR003-SHAREPOINT-NOTEBOOK-READONLY-20261103-001/CONTROL_RECEIPT.md`.

## IR003-A001 repair (source only)

- Production `Invoke-047B-NotebookOfflineBootstrap.ps1` now permits only `-Mode Inspect` and `-Mode Execute`. `-Mode Execute` still always fails with exit 41 **before any host reads**. `-Mode ProbePath` and caller-supplied `-ProbePath` are completely deleted from production script. No externally callable arbitrary filesystem metadata probe remains.
- The same `Assert-NoReparseAncestor` source function is extracted by the CI-only Python test into a **disposable, isolated PowerShell fixture** on ephemeral hosted Windows runner. Only that fixture accepts a path; it probes normal, missing, relative and NTFS junction directories. Temporary files/fixture junctions are created on hosted CI only, not on actual notebook or Product hosts.
- Behavioral negative tests preserve unconditional `Execute` denial, forged host environment, and wrong-host `Inspect`. Tests assert no `ProbePath` presence or `PATH_PROBE_OK_NOT_HOST_QUALIFIED` in production runner.
- Production `Inspect` logic and its return code/status strings are otherwise intentionally unchanged; this source-only repair does not grant extra runtime assurance or justify rerunning completed notebook preflight.

## IR003-A002 residual native obligations

No exact Windows SID pin or ACL ownership/effective inheritance proof on the future SQL data tree, no audited Tailscale peer/Serve/Funnel identity, no alternate SQL service exhaustion, no atomic ancestor protection, no immutable original provider receipt/replay fence, no Dolt SQL root/anonymous/writer/reader negatives, no DPAPI/backup recovery or two-host continuity. A positive `Inspect` output remains explicitly partial. **Native proof/SQL effect admission remain blocked pending a separate trusted effectful design, grant and independent review**. Do not conflate script test fixtures with actual two-host experiment.

## Independent validation request

A distinct independent IR004 reviewer must consume exact Git subject, four file blobs, CI logs and this reconciliation, focusing on whether production `ProbePath` really disappeared and CI fixture safely exercises the same guard logic without covert host effects or new trust bypass. Its receipt, if requested, must be a new single frozen subject at Transport `reviews/TS-BEADS-047B-NOTEBOOK-OFFLINE-BOOTSTRAP-20261103-001/WEB_INLINE_IR004_SECURITY.md`. This artifact is only a reviewer request boundary, not self-approval.

**Invariant:** Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remains untouched, #34 `CLOSED_PASS`, #35 H6 independent, Kernel `UNDECIDED`. No live SQL or remote Tailscale changes.
