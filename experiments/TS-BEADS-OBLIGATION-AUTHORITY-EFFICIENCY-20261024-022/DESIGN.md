# TS — Beads 022 | Design and bounded authority/effect qualification

**Status:** EXPERIMENTAL TEST PLAN, not Product decision. **Scope:** original `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`. SOT blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.

**Parent empirical facts:** 019 found native per-issue revision is not global Product revision; 020 qualified an async native read-set with atomic Beads batch under synthetic authority; 021 executed original `reconcile-and-close-taskcycle.js` preflight/execute after strictly anchored in-memory async adaptation for **already satisfied** obligations, with a possible Product original developer REJECTED gap under pre-satisfied synthetic fixture.

## 022 hypothesis

With Product's real verification/reconciliation methods retained, a **new** async scoped contract may execute the original consumer from five pending obligations through competent synthetic evidence into native Beads TaskCycle closure. It should block missing/REJECTED evidence when obligations are pending; reject unreconciled synthetic `UNKNOWN`; preserve partial effects and receipt correspondence after a malformed acknowledgment; and reject a genuine relevant-issue concurrency race atomically.

Investigate `REJECTED` independently of native Beads by running Product's **unmodified** original recipe preflight with two read-only synchronous snapshots:
1. Developer obligation **PENDING**, evidence REJECTED — expected BLOCKED;
2. Developer obligation already **SATISFIED**, developer authority previously attached, fresh reconciled evidence REJECTED — expected behavior to be measured; prior 021 had READY.

It is important to distinguish a verified `REJECTED` *fact being reconciled* from the separate permission *to use it as Developer acceptance*. The latter is not automatic Product authority. No real Product TaskCycle has this synthetic fixture, and there is no evidence of a real historical unauthorized close.

## Mechanism and limits

- In-memory source adaptation compiles the **original** pinned Product `reconcile-and-close-taskcycle.js` with `async/await` call-site substitutions, importing original Zod, reconciliation and receipt semantics.
- Native Beads v1.3.1 and local Dolt 2.2.0 are disposable; no remote Beads Git, no Product workspace write, no TaskCycles, no provider external effect.
- Two-item causal native `batchApply`: TaskCycle root aggregate metadata and its related attempt guard; native expected_version of each and no independent mutable coordination ledger. Each satisfaction changes TaskCycle metadata epoch and aggregate revision by one, with synthetic event ids for correspondence. The final closure additionally uses native issue close in the same native batch.
- Fresh HTTP GET plus same-value metadata CAS batch used for native `expected_version` tokens; instrument GET response shape, native calls, token reads, batch items to quantify amplification. Do **not** claim optimized read-only native CAS until a token can be acquired and race-protected without updates and verified.
- Cases: full five-pending obligations and closed terminal; separate malformed ACK after first pending satisfaction producing CONFIRMED partial effect without reexecution; third synthetic presatisfied fixture for original Product REJECTED comparison.
- Findings about native guarded batches vs external receipt identities are *different*: no external provider lost-ACK or GitHub effect is attempted.
- No Product authority/Independent Review, no source-native TaskCycle integration, no remote store changes, no acceptance. A PASS qualifies only this bounded fixture.

**Defer** multirunner concurrency, actual dynamic dependency discovery, arbitrary source-native installed consumers, production security and net total code reduction. A subsequent proposal may choose to redesign Product contracts based on these findings, with competent independent review and lifecycle selection; current canonical implementation is not permanent design law but remains operational authority until superseded.

**Execution attempt:** GitHub Actions workflow `.github/workflows/ts-beads-022-obligation-authority-efficiency.yml`, source commit `7a0f3450b82f74d3762a601f90e8414331536d2e`, run [40101479718](https://github.com/mauedgar/ts-execution-lab/actions/runs/40101479718). Terminal result lives in `RESULT.md` after deferred durable join, not inferred from the existence of this design.
