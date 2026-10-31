# TS Beads 039 — Conservative race semantic parity, terminal experimental result

**Authority:** `EXPERIMENTAL_CONTROL_ONLY`; Tecnotron Product none. Canonical issue #35 belongs to Beta Control. **Disposition:** `PASS_BOUNDED_CONSERVATIVE_UNKNOWN_PARITY_OVER_NATIVE_BEADS_WITH_GLOBAL_GAPS / COMPLETE_WITH_LIMITATIONS`.

- Original source Git `mauedgar/ts-execution-lab@4d32a170f6f8aa2cabb9c0d0915b6cd1a7798d10`, one independent `TS-BEADS-039-ATTEMPT-001`.
- [Original GitHub Actions 41173329767](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173329767), job `124455684541`, attempt 1, completed SUCCESS.
- [Original artifact 13031552292](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173329767/artifacts/13031552292), ZIP `sha256:96839db7c20212930ccb80a4147bb3c69f35d23ef70a65d909b58f8fff41593c`, expiry 2026-11-30T05:37:55Z. Contains A/B native original JSON/log, comparison JSON and original SHA manifests.
- Original `COMPARE039.json` SHA-256 `565b3038840ce00ccb976955599344a4193f90f55be606b589a9c145eb50e161`.
- Native original A State Kernel fixture PASS (10 checks); native B Dolt/Beads fixture PASS (32 checks); independent `compare039.py` 13/13 PASS. Both execute the exact same unmodified original Product Recipe `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js`, Git blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc` (same historical and current `tools` blob at observation). Neither installed Product nor prior 030 changed.

**The original divergence is preserved, not overwritten:** Kernel A observed a concurrent `UNKNOWN` and returned `UNKNOWN/UNKNOWN`; original Beads-backed Recipe B returned `FAIL/NONE` when its causal guarded write was rejected. The new experimental B **post-batch** read inspected the native Beads gate's persisted `UNKNOWN` and returned a separately constructed conservative `UNKNOWN/UNKNOWN` assessment, with `provider_redispatch_count=0`. The new layer is an example of **consumer-side reconciliation**; it is **not** an intrinsic Beads guarantee or a Product source patch.

Positive five-obligation completion/closing, partial ACK-loss classification, authority-reference fixtures and independent native CLI terminal readback remain passing. Historical provider bypass 028 still open; Beads per-issue revisions/Dolt history are not Product global revision + event hash chain. A real remote provider may not support status/idempotency. No real TaskCycle #35, no Beads adoption or cancellation of current Kernel.

**Next qualified experimental frontier:** native end-to-end Beads dependency readiness, issue lifecycle and Dolt audit snapshots in a single isolated workload, plus direct audit comparison with existing Kernel source invariants. Stop claiming B=Product READY until ownership boundary + global audit acceptance are competent.
