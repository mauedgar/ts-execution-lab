# TS Remote State — consumer inventory and ordered cutover (2026-11-04)

**Class**: Execution Engineering experimental source-only analysis. **Product authority**: NONE. **Not a canonical ADR/TaskCycle or instruction to delete code.**
**Scope**: preserve Product Upper LC and TaskCycle Core, seek retirement of physical filesystem State Kernel without losing consumer-visible guarantees. Do not replay past effects.

## Read-only exact Product evidence

- Product repository `mauedgar/tecnotron-ai:tools@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`, tree `25d1a151d651bb41936c69334fb0b0772ef22519`.
- SOT navigation `docs/SOURCE_OF_TRUTH.md` blob `498d338eb98e54e294db697c5574296febf77e6f`.
- Architecture `docs/architecture-knowledge-ownership-baseline.md` blob `330fdc82f75e1126939cd718c1facb28abe00c62`: `State_Kernel.final_disposition=UNDECIDED`, `NEEDS_EQUIVALENCE_BEFORE_CHANGE`.
- Current-state `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`: recent Recipe/Kernel decoupling does not select a new persistence backend.
- Kernel `docs/state-kernel-v0/README.md` blob `1c1fc35ef510ac46f4ba84af4b8434adffb47fe1`: four aggregate transition schemas, global CAS, append hash chain, replay, late obligations, UNKNOWN fence.
- Product Python policy `docs/python-runtime-policy.md` blob `ba997668102151a9be26ba5d3ff31c03a11fc93f`: default 3.15.2 for new Product Python components only, no global legacy migration.

## Precise consumer boundaries

1. `src/operational-spine-v0/taskcycle-lifecycle-capability.js` blob `9458a4baab04046e3e49bc07ecf06aafb15f3719`: exposes portable `executionLifecycle` six-method contract and `taskcycleLifecycle` five-method contract. This is a ready-made substitution seam, not a new framework.
2. `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts` blob `2ab6e2655944fd98653d673d5a4dce69da3a06`: typed portable ports. Preserve caller-visible signatures and semantics.
3. `src/operational-spine-v0/state-kernel-adapter.js` blob `b8970d6e78b77878a8cb8ef0fbd3c2568954c82e`: still imports `FilesystemStateStore` and implements both portable ports by using Kernel APIs; requires verified revision on mutation.
4. `src/operational-spine-v0/recipe-invocation.js` blob `4a2852602ccb654ad0a74ba1c5ce5ea89e411d2`: default `createRecipeInvocationEntrypoint` still binds `createStateKernelCompatibilityBinding({home: environment.state_store.location}).executionLifecycle` when not explicitly supplied, and defaults `FilesystemInvocationArtifactStore`. Those are two **distinct physical state/result dependencies**.
5. `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js` blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc`: consumes portable `TaskCycleLifecycleCapability` and requires no unreconciled execution before closure. Preserve exact semantic checks, not the filesystem.
6. `src/state-kernel-v0/index.js` blob `0219b92e5f546407a6060a6dc449865c14c7f144` and `contracts.js` blob `5d2d3a8a24ebc17339675e0c801595956e0cd353`: still contain actual validation/transition functions and typed state vocabularies. Physical deletion before relocating any uniquely owned semantics would drop capabilities. Historical tests are not disposable proof.
7. `src/state-kernel-v0/store.js` blob `f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a`: filesystem HEAD/generation/write-lock mechanic is the physical owner to retire **after** verified replacement.
8. `src/state-kernel-v0/cli.js` blob `f2163eb79965ef22739f4a183c8a869a625e884f`: current CLI backwards compatibility and read commands need explicit disposition before removal.

This is a **bounded source-level inventory**, not universal installed-harness tracing. No assertion that weeks of GitHub/ChatGPT external work were performed through the Kernel. The fact that they were often performed *outside* its filesystem runtime does not prove full in-repo consumer deletion is safe.

## Experiment evidence and strict scope

- Hosted DBOS 3.4.0 + PostgreSQL16 + CPython 3.15.2: `mauedgar/ts-execution-lab@8457060682923e5e8fe6b14017f8d890a97acb3a`, Actions run `41859696607` attempt 1 **PASS**; two separate Python processes replay same workflow ID, side-effect counter remains 1. Same ephemeral Actions-hosted PostgreSQL instance, not permanent remotely hosted database.
- Git-backed synthetic ledger `experiment/ts-remote-state-git-cas-20261104-001`: A commit `c29fb2f990081a3ddaa27a270ceb7f83b29a6b59` was observed as branch head and persisted synthetic revision 1. B sibling commit `bed36d401266e6e2ecbd6872b4eef6c6bcb20427` update returned **GitHub provider GraphQL UNKNOWN**, not a proven concurrency/CAS denial; preserve its uncertainty, do not retry that branch and do not use it as semantic equivalence evidence.
- PostgreSQL mechanical conformance pilot V4: `mauedgar/ts-execution-lab@77f6201ef9122ce682dc405b7afb9a6378701fd4`, Actions `41862024848` attempt 1, **QUEUED at current observation**, not PASS. It tests four synthetic aggregate-shaped rows, global revision race, hash audit, UNKNOWN fence and replay — **not** canonical Product reducers.

## Future ownership (proposed, not adopted)

| Concern | Candidate owner | Boundary |
| --- | --- | --- |
| Product authority, obligations, transitions, TaskCycle and Operation decisions | Upper LC / TC Core / existing validated Product domain components | Do not copy semantics into DBOS steps |
| Globally consistent mutable aggregate state and append audit | PostgreSQL transactional adapter | Same expected global revision; no separate materialized mutable truth |
| Durable execution workflow identity, step checkpoint, recovery | DBOS | Steps may be retried before completion; fence external UNKNOWN by exact provider identity |
| Canonical source and adopted decisions | Git repository SOT | Do not turn DB state into new Product decision authority |
| Large execution artifacts/effect receipts | GitHub Transport or appropriately protected artifact store | Mutable state and secrets/PII MUST NOT be committed to Git |
| Notebook/local folder | Optional cache and dev fixture after cutover | Never authoritative after proven, separately authorized migration |

## Ordered independent decisions and tests — do not collapse gates

**E0 mechanics**: reconcile V4 exact Actions original result; if fail, publish independently reviewed repaired **new subject** only after evidence, no blind workflow rerun. Existing DBOS basic PASS remains separate.

**E1 semantic equivalence**: derive exhaustive vectors from frozen `src/state-kernel-v0` original test suite and portable lifecycle ports. Prove four aggregates, late obligations, rejection atomicity, authority references, global expected revision, audit/replay, restart and `UNKNOWN` fencing against the exact same fixtures. Reuse/adapt accepted reducers in the correct Product semantic owner; no second shadow Kernel.

**E2 remote provider and disaster recovery**: provision strictly synthetic namespace with owner-controlled managed PostgreSQL after an explicit provider connection/secret custody boundary. Two independently hosted clients and off-host verified backup/restore, permissions/quotas, fail-closed outage, provider-result reconciliation and no local fallback.

**E3 caller cutover**: one exact Product-selected responsibility to adapt portable lifecycle and artifact stores at Recipe binding; independent IR, Developer accepted candidate, separately authorized guarded Phase2 and receipts. Keep old Kernel available read-only for reference during rollout.

**E4 physical retire**: demonstrate no active/default consumers or missing capabilities, original historical evidence preserved, no unresolved effects rewritten, and a reversible cutover/rollback boundary. Only then separately adopt physical deletion and update Product SOT, not during experiment.

No new Product scheduler, TaskCycle, provider grant, historical replay, wholesale refactor, global Python migration, or secrets are created by this document.
