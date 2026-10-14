# TS — Beads lifecycle parity 014 | Native experimental evidence and disposition

Date: 2026-10-14, Argentina. Responsibility: same NONPRODUCT experimental Beads–Tecnotron investigation. **No Product selection, grant, TaskCycle creation, code change, acceptance, integration, migration, or State Kernel retirement.**

## Identity and terminal result

- Exact Product observation: `mauedgar/tecnotron-ai:tools@2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89`, tree `04e57337ac129bd40774d48cf2cfee041f904cfa`. `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `cac3955f1040e743248f015c974bbc397edb9650`. Its closed historical case `TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001` is only a reference; the 014 lab creates distinctly named *synthetic* identities, not that actual TaskCycle.
- Original shared Beads remote `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`. Observed unchanged before and after terminal run.
- Experimental branch: `experiment/beads-lifecycle-parity-20261014-014`. Script: `experiments/TS-BEADS-LIFECYCLE-PARITY-20261014-014/parity014.mjs`, initial source commit `82db7e897259d5b09a24aea48e9d5b3eb2af364b`. Workflow: `.github/workflows/ts-beads-014-lifecycle-parity.yml`, frozen execution source `e0eeed9a5c29c12be102010fdb6581436052c901`.
- **GitHub Actions terminal run** [38527908888](https://github.com/mauedgar/ts-execution-lab/actions/runs/38527908888), job `115732536686`: `completed / success`; pinned `bd` v1.3.1 with archive SHA-256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`. Windows runner, short disposable embedded Dolt working directory, isolated Git repository with **no Git remote**.
- Log receipt: `TS_BEADS014_RESULT=PARTIAL_NATIVE_PASS_PARITY_NOT_ESTABLISHED;pass=21;fail=0;native_cas=NOT_QUALIFIED;Product_effect=NONE` and `TS_BEADS014_PRODUCT_AND_DOLT_UNCHANGED=PASS;product=2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89;dolt=1f72d68797114170a97fee27641858f2e55a4571`.
- Native Actions receipt artifact ID `11876219664`, digest `sha256:25a97969eb4bc939855c15f8ea698db78cfccc3d6667eafeb79c7ca692d04b0d`, expires `2026-10-21T07:23:19Z`. Original script and this Git report are longer-lived durable evidence. No blind retry; one workflow run succeeded.

## Verified 21/21 experimental assertions (including intentionally negative controls)

**Native positive:** isolated Dolt/Beads initialization, stable issue identity and metadata, native deterministic ID duplicate rejection, persisted preparation, operational metadata readbacks, UNKNOWN state surviving re-instantiation of adapter and fresh `bd` CLI calls, presence of native history, closed issue excluded from `bd ready`.

**Thin synthetic test-double rules, NOT inherent Beads Product semantics:** `observeOperation`, `observeAttemptPresence`, `prepareAttempt`, `confirmDispatchStart`, `recordExecutionOutcome`, `snapshot`, `hasUnreconciledExecution`, `satisfyObligation` and `closeTaskCycle` implement a selected subset of Tecnotron's existing interfaces over native Beads issue metadata. They detect duplicate attempts and block subsequent work when `UNKNOWN` persists, reject an unqualified synthetic receipt, refuse premature TaskCycle closure and stale *sequential* revisions, and persist a synthetic satisfied obligation/closure. The external receipt was an *injected synthetic observation*; this **does not qualify actual provider reconciliation**.

**Native negative counterexamples, deliberately PASS as tests:** (1) ordinary `bd update --metadata` without conditional revision permits an obsolete second writer to overwrite the first's metadata; this tests that *specific unguarded CLI path*, **not every Beads API**. (2) bare `bd close` accepts a synthetic issue without Developer/Product grant; external semantic authorization remains necessary. The test-double's guarded logical close consisted of two native Beads commands (`bd update` plus `bd close`), **not an atomic lifecycle close**.

No metrics about real multi-writer latency, storage cost or Product recovery time are claimed. The result is `PARTIAL_NATIVE_PASS_PARITY_NOT_ESTABLISHED`, not `STATE_KERNEL_REPLACEMENT_QUALIFIED`.

## Critical new opportunity — use built-in Beads CAS instead of rebuilding it

Further source inspection of the **same released v1.3.1** found a native `issueops.MetadataCAS.CompareAndSetKey` contract designed for transactional compare-and-set of one metadata key, with `Swapped` and `Current`, and its HTTP endpoint **`POST /v0/beads/issues/{id}:casMetadata`**. The public Beads contract explicitly distinguishes the native `Lifecycle.ExpectedVersion` CAS, `Lifecycle.ExpectedStatus`, native claim semantics and unguarded generic `Lifecycle.Update`. It also emphasizes that CAS is atomicity, **not authority**, and one key's value is not a global fence. Sources at release v1.3.1: `https://github.com/gastownhall/beads/blob/v1.3.1/issueops/metadatacas.go`, `https://github.com/gastownhall/beads/blob/v1.3.1/internal/httpapi/metadata_cas.go`, `https://github.com/gastownhall/beads/blob/v1.3.1/cmd/bd/update_input.go`. These capabilities were **source-inspected, NOT runtime qualified by 014**, and their version/transport compatibility must be proven before production use. Do not extrapolate 014's unguarded write counterexample into a claim that Beads lacks any CAS.

## Disposition and next experiment candidate

Keep Upper LC / TC Core semantic authority, Developer grants, independent review, immutable Git candidates/receipts and reconciliation of actual external effects under Product ownership. Treat Beads as a strong candidate for the ONE operational/persistence backend through existing `ExecutionLifecycleCapability` and `TaskCycleLifecycleCapability`, not as automatic grant/acceptance/closure. The State Kernel physical disposition remains **UNDECIDED / no Product migration authorized**.

**Recommend 015 — native Beads CAS + metadata event/receipt correspondence parity** in disposable Dolt, using the shipped `MetadataCAS` HTTP/role and native version guards. Verify one-winner concurrency, stale expected rejection with no write, restart/readback and audit, exact authority/attempt/receipt linkage, unavailable provider/UNKNOWN and atomic close boundary. Map what can be safely absorbed into native Beads vs minimal *Product-owned semantic policy*, avoid any new ledger/queue/orchestrator. Only after this conformance can the competent Product Control consider a physical replacement/retirement decision; no Product change is selected now.

Final effect inventory: `Product_effect: NONE; shared_refs_dolt_data: UNCHANGED; experimental_LOCAL_ONLY: COMPLETED; previous pilots: PRESERVED; actual Product TaskCycles: UNTOUCHED`.
