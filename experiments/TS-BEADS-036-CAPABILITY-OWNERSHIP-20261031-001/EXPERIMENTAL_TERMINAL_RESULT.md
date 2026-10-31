# TS Beads 036 — Terminal experimental capability ownership result

**Date:** 2026-10-31. **Authority:** `EXPERIMENTAL_CONTROL_ONLY`. **Disposition:** `PASS_SOURCE_BOUNDED_OWNERSHIP_AUDIT_WITH_AUTHORITATIVE_GAPS_OPEN / COMPLETE_WITH_LIMITATIONS`. **Product:** `NONE`. The canonical issue **#35 remains exclusively under Tecnotron Beta Control**; this Beads branch cannot choose, implement, accept, integrate or close any of its responsibilities. Attendance is not reclassified here.

## Original frozen execution and durable receipt

- Original source subject: `mauedgar/ts-execution-lab@8f876c8a5eb0054aa85c818fa84bcb8cfce862c8`, branch `experiment/beads-036-capability-ownership-20261031-001`.
- Original `ExecutionAttempt=TS-BEADS-036-ATTEMPT-001`, one push-triggered [GitHub Actions run 41172317720](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172317720), run attempt 1, job `124452700858`, `completed/success`.
- [Original artifact 13032085095](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172317720/artifacts/13032085095): `ts-beads036-original-41172317720`; compressed bytes 6,717, ZIP `sha256:7bc6b3bca551464e20e9623517317e130e86462bfa4705eb24756319050b29f1`, retention expiry **2026-11-30T05:22:14Z**. Contents: `RESULT036.json`, original frozen manifest, DoD, original audit log and SHA manifest.
- Original `RESULT036.json` `sha256:b2472db3466bd63fcbfc3f0c8bd8bfedbddada488ca11c26db14140bdb3d5a2b`.
- Frozen `INPUT_FROZEN.json` blob `9fdcbd7ba296d3ec85f89f6adcca955b6eb1b240`; mechanical source `audit036.py` blob `89f5692222122ebeab46f3bef0269b68e85714aa`. DoD at `experiments/TS-BEADS-036-CAPABILITY-OWNERSHIP-20261031-001/DOD.md`.
- Original runner line: `TS_BEADS036=PASS_SOURCE_BOUNDED_OWNERSHIP_AUDIT_WITH_AUTHORITATIVE_GAPS_OPEN;kernel_bytes=36715;adapter_bytes=12020;recipe_bytes=36279;Product=NONE`.
- **This was a consistency check of the frozen, previously GitHub-observed source inventory and original historical receipts.** It did **not** re-fetch the Product source on the Actions runner, re-run Beads, bypass sandbox permissions, run models or perform Product effects.

## Technical capability disposition

| Capability/claim | Owner/proof | 036 disposition |
|---|---|---|
| Native dependencies/`ready` | Beads experiments 040–041, synthetic, native readback | `QUALIFIED_BOUNDED` as optional **read projection**, not authority or scheduler |
| Beads historical commit/as-of snapshots | 032, 18/18 native | `QUALIFIED_BOUNDED` but not equivalent to Product global event-count/hash-chain history |
| Native guarded causal batch under one server | 035, four races/29 checks, one 200 + one 409 | `QUALIFIED_SELECTED_PATH`; no general privileged writer exclusivity |
| Total causal writer exclusion | 028, `bd dep add`/alternate `bd serve` bypass | **`BLOCKED_PRIVILEGED_BYPASS`**. Existing selected launcher does not fence all privileged mutation paths |
| Global revision and audit replay | Product `state-kernel-v0/store.js`; 030 comparison | **`NOT_EQUIVALENT`**. Original Product expects global revisions, event count, hash chain, snapshot/HEAD correspondence |
| UNKNOWN/retry/effect reconciliation | Product original Kernel and adapter; 030 A=`UNKNOWN/UNKNOWN` vs Beads B=`FAIL/NONE` on test race | **`BLOCKED_SEMANTIC_PARITY`**. Difference proven in synthetic fixture, **not** actual Product incident |
| Per-actor write authority | Current Product authority/role constraints; Beads native bearer grants API surface | **`NOT_QUALIFIED`** for Product roles; don't confuse HTTP auth with Developer grant |
| GitHub receipts and transport originals | 033–034, Product original OP03, 046–048 provider-failure lessons | Provider and Git/Transport remain authoritative; Beads only stores references, no automatic re-dispatch after UNKNOWN |

**Frozen code footprint:** 4 State Kernel files 36,715 bytes; State Kernel adapter 12,020 bytes; original close Recipe 36,279 bytes; **85,014 measured bytes in these three classes**. Exact source blobs recorded in `INPUT_FROZEN.json` against `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`. This is *source footprint*, not proof all bytes can be removed; actual removed bytes from Product by Beads 036 **0**, and net maintenance savings **not established**.

## Architecture alternatives, without authority promotion

- **A — Beads read-only informative projection:** may be experimented with without replacing Product Kernel/TaskCycle ownership, but brings another store/service, synchronization and lifecycle. It is **optional**, not a precondition to execute canonical #35 and not an integration approval.
- **B — Beads-first authoritative causal store:** **NOT READY**. Requires explicit competent Product approval **after** closing actual exclusive-writer boundary, global audit semantics or an adopted replacement invariant, sticky UNKNOWN classification and per-actor authority. The Beads 035 selected-path PASS does not solve the 028 privileged bypass or 030 divergence.

**Critical correction to older chat wording:** canonical **#35 is the Upper LC issue**, managed by Beta Control; this experimental chat does **not** classify Attendance's canonical status or advance any #35 TaskCycle. "Prior to #35" denotes a possible future decision point in Beta Control, not an execution dependency invented by Beads research.

## Recommended next bounded Beads research

**`037 — privileged-writer exclusion / authority boundary feasibility`** (not initiated here). Compare an isolated writer identity with read-only agents and all native Beads CLI/HTTP/Dolt mutation entrypoints, identifying whether existing OS credential boundaries can actually prevent bypass without adding a new Kernel/daemon. If no complete, measured boundary is feasible, preserve B=BLOCKED and stop; do not proceed by convention-only root revision. Afterwards compare event/UNKNOWN semantics only with a Product-authorized invariant contract. Do not bypass security safeguards, repeat historical attempt, write Product, or delay #35 by default.

**Source disposition:** `EXPERIMENTAL_036_TERMINAL_PASS_BOUNDED_WITH_B_ADOPTION_BLOCKED`; no Beta transfer, Product issue comment, SOT change or intake claim has been made.
