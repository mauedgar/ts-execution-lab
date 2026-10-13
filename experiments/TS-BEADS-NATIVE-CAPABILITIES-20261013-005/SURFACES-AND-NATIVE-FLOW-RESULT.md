# TS Beads Native Workflow / Execution Surface Qualification 005

Date 2026-10-13. Classification: experimental evidence, **NONE_PRODUCT**, no TaskCycle lifecycle or authority effect.
Product repo SOT was read only at `mauedgar/tecnotron-ai:tools:docs/SOURCE_OF_TRUTH.md`, as was TS Execution Engineering autonomous operating contract on `mauedgar/ts-execution-lab:main`.

## Durable original execution references

| Experimental subject | GitHub Actions original run/job | State | Exact observation |
|---|---|---|---|
| Native atomically claimed operational issue, separate actors | Run [38453388657](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453388657), job `115489756045`, commit `08d16f65a8683fbb7be1a89a662df5f27d29c566` | **PASS** | Process A won; process B rejected explicitly; final independent `bd show` owner A |
| Early matrix YAML typo | Run [38453633081](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453633081), commit `580f64d464ce3cdcdc9d7f9e6a57c515a6e498e7` | **FAIL** | Wrong matrix expression; not a Beads product claim |
| Broken PowerShell runner syntax attempts | Runs [38453659054](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453659054), [38453773956](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453773956), [38453841045](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453841045) | **FAIL**, independent original provider attempts | Runner parse-stage failures; no Beads issue creation |
| Formula cook / dry run / pour | Run [38453976567](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453976567), **formula job** `115491801764`, commit `3f724cea99ce395c5535f7502b8c2b530e376535` | **PASS job** despite overall run FAIL (graph companion FAIL) | `TS_NATIVE_FORMULA_COMPILE=PASS`, `TS_NATIVE_FORMULA_POUR_DRYRUN=PASS`, `TS_NATIVE_FORMULA_POUR=SUCCEEDED`, `TS_NATIVE_FORMULA_RECORDS=4`, `TS_NATIVE_FORMULA=PASS_COMPILE_DRYRUN_POUR` |
| Manually constructed epic graph with `bd ready --mol` | Same run [38453976567](https://github.com/mauedgar/ts-execution-lab/actions/runs/38453976567), graph job `115491801464` | **FAIL** on scoped frontier assertion | `bd ready --mol <ad-hoc-epic>` did not show expected children; `bd dep add` succeeded. This is NOT proof of globally blocked graph or that a poured native molecule behaves likewise. |
| Independent synthetic fanout/fanin with manual gate | Run [38454230027](https://github.com/mauedgar/ts-execution-lab/actions/runs/38454230027), source commit `472f364c340fb44f9d52e849123c2097bcd8d01d` | **PASS** graph job (workflow SUCCESS) | Global `bd ready` initially included root, two independent children and excluded dependent join. Closing children left join blocked by human gate. Synthetic `bd gate resolve` made join ready. `bd mol show` succeeded. The scoped `bd ready --mol` result remained empty for this ad-hoc epic. |

## Exact observed graph identities and qualification

From native Actions job logs of `38454230027`:

- Epic root `ts-execution-lab-0fw`, left `ts-execution-lab-0fw.1`, right `ts-execution-lab-0fw.2`, join `ts-execution-lab-0fw.3`, synthetic human gate `ts-execution-lab-t98`.
- `TS_MOL_SCOPED_BEFORE=` (empty).
- `TS_MOL_GLOBAL_BEFORE=ts-execution-lab-0fw,ts-execution-lab-0fw.1,ts-execution-lab-0fw.2`.
- `TS_NATIVE_GRAPH_GATE=PASS_FANOUT_FANIN_AND_SYNTHETIC_HUMAN_GATE`.
- Synthetic test gate represents *no Developer/Product grant*. This test only qualifies operational graph mechanics.

## Execution surface vs persistence

| Surface | Observed strengths | Unqualified or intrinsic caveats |
|---|---|---|
| **Local embedded Beads** | Prior pilots 001/002/004: persistent cross-process recovery and sequential exact source-ref dedup policy; no server installation | Embedded Dolt is single-writer; no simultaneous writes to same embedded store; owner host can be offline |
| **GitHub Actions + ephemeral local Dolt server** | Runs `38445929222`, `38446617378`, `38453388657`, `38453976567`, `38454230027`: fresh independent OS, pinned binary versions, concurrent writers, exact-ID collision prevention, atomic claims, formulas, graph/gate mechanics | The runner is ephemeral. **When a run ends, its Dolt database is not a durable shared inbox**. Logs prove what happened, not automatic state resumption; future runs require a durable external state store or verified export/restore. Provider availability and quotas are external. |
| **Actions client + durable independent Dolt backend (remote)** | Architecturally possible candidate: Action as stateless executor, remote datastore as authoritative operational continuity | NOT TESTED: remote credential, host/port/network, concurrent SQL, backup, access control, TCO and exact canonical source selection. No default service deployment authorized. |
| **Actions client + Git/Transport-backed serialized Beads snapshot** | Can be investigated with existing Git Transport contracts and full Dolt backup/export/recovery | NOT TESTED: serializable multiwriter updates, optimistic locking, snapshot application, durable idempotence. JSONL issue export is **not** a full Dolt history backup. Do not conflate publishing receipt with adopting/restoring operational state. |
| **Local Dolt server** | Technically viable with version-pinned Dolt 2.2.0; upstream documentation | Original local host `DESKTOP-3LJ0E54` has no qualified Dolt server installation. Host status and exact original Pilot 003 remain PENDING, not inferred from hosted Actions tests. |

**Decision framing:** choose execution per task binding and availability; keep durable operational continuity independently specified. For stateless CI, isolated trials, reviewers and bounded validation, Actions is already useful. For a shared long-lived Beads inbox, hosted Actions **alone** is not a persistence service. Local embedded suffices for proven sequential case; real distributed multiwriter requires a qualified durable backend and identity/effect rules.

## Adoption candidates, not decisions

Native claim/leases, dependency DAGs, `bd ready`, human/CI external gates, persisted formulas/molecules, and deterministic `--id` collisions are promising replacements for *bespoke non-Product* queue, dependency, checkpoint or claim mechanisms. Still NOT PROVEN: `bd ready --mol` behavior for poured molecules, lease expiry/reclaim under UNKNOWN, automatic chat wakeup, GitHub Projects parity, source-ref semantic idempotence on duplicate conflict, Product review/grant/TaskCycle semantics. Preserve `NONE/CONFIRMED/UNKNOWN` effect reconciliation outside ordinary ready/closed fields unless independently equivalent.

## Proposed next self-contained research boundaries (not new Product gates)

1. Prove cross-run continuity in Actions by a **durable backed-up Beads store**, read by a new independent workflow/job, using existing Transport or a provider artifact where appropriate. Exact backup identity and consumption must be verified; avoid a new scheduler or publisher.
2. Qualify poured native molecule scoped readiness and `--claim` lease expiry/ownership recovery without treating an expired lease as authorization for blind retry of unknown Product effects.
3. Compare true migration/removal opportunities with current Tecnotron consumer inventory at fresh repo ref. Use competent Product Control only for any canonical adoption.

Upstream version-pinned docs: https://github.com/gastownhall/beads/blob/v1.3.1/docs/multi-agent/coordination.md ; https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/formulas.md ; https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/molecules.md ; https://github.com/gastownhall/beads/blob/v1.3.1/docs/workflows/gates.md ; https://github.com/gastownhall/beads/blob/v1.3.1/docs/architecture/dolt.md .
