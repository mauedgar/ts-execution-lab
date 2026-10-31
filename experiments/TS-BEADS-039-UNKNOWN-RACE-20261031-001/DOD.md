# TS Beads 039 — Conservative UNKNOWN parity when native Beads CAS refuses a stale attempt

**Authority:** EXPERIMENTAL_CONTROL_ONLY; Product authority/effects NONE. **Issue #35** canonical belongs exclusively to TECNOTRON_BETA_CONTROL. Product cannot consume these experimental outputs as automatically accepted code.

## Frozen source and exact question

- Original historical experiment 030 B fixture: `consumer030-B.mjs@3f36e2238efd827b5a498ff1ff28546092a70665`; product source `mauedgar/tecnotron-ai@d4154bd43f26515c39a41be974e462a0c7406a2d`; the original close Recipe blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc` is **identical** to the current observed `tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` Recipe blob.
- Product and original 030 remain immutable, no replay of 030 attempt/receipt. This **new isolated experiment** runs fresh A (actual Kernel fixture) and B (native Dolt/Beads adaptation) against that frozen original Recipe, on fresh local roots and distinct result IDs.
- Git source blobs frozen: `consumer039-A.mjs@eea40f792940cd0143a67cde7a2cfa98d52a50b5`, `consumer039-B.mjs@3aa4fc146f1d5e42271682b801049358adca06dc`, `compare039.py@784d400732fb1be556089e6a95f2cad90a526a90`.
- One new `ExecutionAttempt=TS-BEADS-039-ATTEMPT-001`, source Git freeze, native Beads v1.3.1/Dolt v2.2.0 pinned release SHA, separate initial A/B original JSON and independent compare JSON. Original failure not silently repaired.

## DoD (source and semantic)

1. The SAME original Product Recipe SHA256 must be reported by A (actual Kernel) and B (in-memory native Beads adaptation), with **zero** installed Product file changes.
2. In the original 030 race, A yielded `UNKNOWN/UNKNOWN` conservatively and B's original Recipe yielded `FAIL/NONE` after native guard refusal; **preserve that original B outcome**, do not rewrite its return values retroactively.
3. New **external experimental conservative join** must reread native Beads attempt issue immediately after CAS refusal. If `state=UNKNOWN` or `reconciliation_required`, externally classify `UNKNOWN/UNKNOWN` with `NO_RETRY`, without reopening or sending provider effects. This postread matches A on this exact race; it does NOT prove the original Recipe or Beads core enforces this rule.
4. Preserve positive A/B five obligations, closure, authority fixtures, partial ACK-loss and terminal independent native CLI readback, no regressions.
5. Original independent comparison asserts all checks, preserves A/B JSON original output and compare original JSON with hashes. A postread policy gap must remain explicit: Beads does not provide global Product revision/event/hash chain or native no-retry guarantee.
6. No new Kernel, scheduler, authority, Product TaskCycle, merge, #35, provider effect or Beads adoption. Stop on FAIL/BLOCKED. No automatic rerun, original logs and source subjects preserved.

**Expected bounded result** `PASS_BOUNDED_CONSERVATIVE_UNKNOWN_PARITY_OVER_NATIVE_BEADS_WITH_GLOBAL_GAPS` and overall `COMPLETE_WITH_LIMITATIONS`. Follow-up still requires privileged writer confinement and global audit compatibility or Product-approved replacement invariants.
