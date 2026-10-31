# TECNOTRON-DISTRIBUTED-CONTROL-001 — Disposición arquitectónica experimental concreta

**Cutoff:** 2026-10-31 UTC. **Class:** RESEARCH / EXPERIMENTAL_CONTROL_ONLY. **Product authority/effect:** NONE. **Subject:** `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, tree `e6be65e0c3d9aca074218b2fff92e6d42fc76141`, read-only. No Product TaskCycle initialization, #35 execution, State Kernel migration, or Phase2.

## I. Concrete experimental selection

**SELECT:** `BEADS_FIRST_GITHUB_NATIVE_DOLT_REMOTE_SINGLE_TRUSTED_WRITER` for **distributed work state only** (task graph, dependencies, ready, status and native work history), with interchangeable clients/worktrees/Actions and no canonical local Kernel folder. Writer publishes natively to a **dedicated, isolated** GitHub repository/ref; clients consume under `contents:read`. A single trusted writer/OS principal/service account owns mutations and no other agent, reviewer or operator receives DB/CLI write privileges. Do not build a parallel task ledger, new scheduler or clone of Kernel.

**SELECT for Product semantics:** Keep competent Developer authority, SOT, Upper LC/TC Core, immutable Git subjects, IR, acceptance, Phase2 and effect reconciliation *outside Beads*. `bd ready` signifies dependency readiness, never authorization. External verified GitHub/Transport receipts preserve original `ExecutionAttempt` identities and drive `NONE/UNKNOWN/CONFIRMED` and no-retry; a tiny stateless policy/Recipe adapter MAY translate native Beads operations only after consumer qualification, not another persistent store.

**DO NOT SELECT:** a permanent SQL Dolt server as default, direct multiwriter Beads authority, new custom ledger, artifact ZIPs as long-term SOT, Product Kernel shutdown or adoption before Product control. Server mode is a contingent future option if same-remote concurrency requires it and security/downtime/backup evidence warrants it; Beads 045 only proved same-host restart and two client processes.

**Verdicts:**
- `WORK_STATE_HOST_INDEPENDENCE_GO_EXPERIMENTAL`: native GitHub Dolt storage, fresh independent clients and recovery are empirically demonstrated.
- `LIVE_MULTIWRITER_AND_PRODUCT_AUDIT_EQUIVALENCE_INCOMPLETE`: no interhost write isolation plus complete canonical receipt/authority/audit parity yet.
- `PRODUCT_KERNEL_FULL_REPLACEMENT_NO_GO_NOW`: not authorized, not safe to claim with present evidence. This is NOT a permanent ban on later Product migration.
- `EXPERIMENTAL_ARCHITECTURE_DISPOSITION_COMPLETE_WITH_LIMITATIONS`: selected topology and explicit blockers, not a Product ADR.

## II. Original durable evidence reconciled

| Evidence | Original run/ref | Confirmed scope |
| --- | --- | --- |
| Beads 009 | `mauedgar/ts-execution-lab@80845c3c2ac326acbf39b9008905097c23d20077:experiments/TS-BEADS-NATIVE-GITHUB-REMOTE-20261013-009/RESULT-20261013.md` | Native GitHub `refs/dolt/data` push; fresh runner restore; concurrent stale writer non-fast-forward rejection; independent reconciliation. Limit: not real Product UNKNOWN. |
| Beads 029 | `@6c03915493594a38cbb21c80235e7ac81e0e26af:experiments/TS-BEADS-029-ARCHITECTURE-COMPARISON-20261028-001/CONTROL_EXPERIMENTAL_VERDICT.md` | State Kernel source 36,715 bytes; adapter 12,020; source removal **0**, net savings unmeasured; privileged 028 bypass. |
| Beads 030 | `@5cd88a9ce63aadbe08385f63ac11588192f31f6d:experiments/TS-BEADS-030-PARITY-20261029-001/CONTROL_EXPERIMENTAL_VERDICT.md` | A/B original Recipe synthetic parity mostly PASS, but concurrency effect-state differs: Kernel UNKNOWN/UNKNOWN vs Beads FAIL/NONE. Single positive cold timing A 32.555ms vs B 739.650ms; **not** production performance ranking. |
| Beads 041 | `@293a58de63341f51f6b2dbf05710f488392e4754:experiments/TS-BEADS-041-PORTABLE-NATIVE-STORE-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md` | Fresh runner recovered full native archive/graph/history; archive != live remote. |
| Beads 042 | `@7b0fb033e9aa9a1e3d140622209ed427d77b1f12:experiments/TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md` | Two synthetic concurrent subprocess workers, native join/Parent, no Kernel; one host. |
| DC043 | [Actions 41176626803](https://github.com/mauedgar/ts-execution-lab/actions/runs/41176626803), terminal report `@4025b8a93f2c15e62d42594eda76e2405075eb26:experiments/TS-DISTRIBUTED-CONTROL-001-HOST-FAILOVER-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md` | Different runners; native store and effect external artifacts survive injected lost ACK. B recovers original UNKNOWN→CONFIRMED, `redispatch=0`. Workflow failure intentional on producer; consumer success. Artifacts expire. |
| Beads 045-002 | [Actions 41177022889](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177022889), source `aae4dabd9c2b6d37a24bba896d2eaa2199533287` | Dolt SQL server and two native clients; reader SQL ACL denied writes; server restart recovered native graph/history. **One** physical host, not interhost HA. |
| DC044-001 | [Actions 41177181291](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177181291), source `e67c8bfa2d1e9059dd90fabf52ed549dbc721dcf` | FAIL due overstrict fixture count=3. Real pinned remote had 4 issues. No push; remote unchanged. Original preserved, no replay. |
| **DC044-002** | [Actions 41177310449](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177310449), source `3850a1f249d438d933012a5f223ec78e62ab4650`, attempt 1 | **SUCCESS**. Two independent Ubuntu runners Alpha/Beta and third join job all PASS. Both native `bd bootstrap` recovered exactly same 4 issues with original source refs from remote `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`. No local Kernel, no push, no external provider dispatch. Remote live ref unchanged after join. |

DC044-002 original verified receipts:
- Alpha job `124467423404`, artifact [13033382303](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177310449/artifacts/13033382303), ZIP SHA256 `d212d4da0b75d3a2597dba0ada83dd0b51f94b8a62ed703fe45981d12ea4c76b`, original RESULT sha256 `dbfb11b6e9b521ae757360c17cf9dcd8bc1d39bae01997648c83e44eb7fdacaf`.
- Beta job `124467423482`, artifact [13032824244](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177310449/artifacts/13032824244), ZIP SHA256 `f24436e2602dd73f3235fad7f381a92659fdf97e29dbb35cf1dd904eb39af4d0`, original RESULT sha256 `0b9f992e267ee926a0f90a9d74d936e05b84dfb34e4a9cbf7b7d1f8ba3c49597`.
- Join job `124467463666`, artifact [13033292304](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177310449/artifacts/13033292304), ZIP SHA256 `ce1a883036902a6dcc658beb5c5bf5e14b9aabbf1fcb225e5962fa36b52d0500`, `RESULT044.json` sha256 `797092197820819250593a96552097343287681cabfa6ff024ab1998673ef9f6`. Original log `TS_DC044_JOIN=PASS_TWO_INDEPENDENT_HOSTS_NATIVE_GITHUB_REMOTE_READ_ONLY;hosts=2;pushes=0;Product=NONE`.
- Artifact retention ~2026-11-30T06:36Z. Original .beads store is hosted in native Git ref, not reconstructed by artifact in DC044. Provider artifacts are temporary evidence; commit exact result pointers in versioned transport if permanent receipts are needed.

## III. Ownership map (do not fork current Product implementation)

| Owner | Responsibility | What may be eliminated after separate Product evidence |
| --- | --- | --- |
| Git + dedicated GitHub repo | Commit/ref identities; remote Beads/Dolt Git storage; worktrees; immutable source; CI runners | Local host as durable owner, bespoke Git-state cache |
| Beads native + Dolt | Work-graph/child dependencies, `ready`, status, native work history and snapshot/backup | Duplicate kernel-like work tracking, custom scheduler/RunStore, duplicate graph persistence **only where no active consumer remains** |
| GitHub Actions/Transport/provider | Original effect/ExecutionAttempt receipts and external status with verifiable identity | Custom ephemeral result inbox/state store where provider-native receipt suffices |
| Developer + SOT + Product control | Product authorization/TaskCycle Core; IR, acceptance, Phase2; canonical knowledge and semantics | Nothing by inference from `bd ready` |
| Existing stateless Recipe/Coordinator qualification | Verify exact grant, subject, attempt, provider receipt, no-retry and fail-closed UNKNOWN; publish authorized Beads mutations via trusted writer | Existing filesystem Kernel effect storage ONLY after proven equivalent source-native, not this experiment |
| Interchangeable local/remote hosts | OpenCode/Orca/worktrees/Actions implement bounded tasks; return code commits/receipts; no Beads write credential | Host-specific continuity dependence |

## IV. Candidate alternatives and net cost

**Preferred near-term B-first constrained topology:** native GitHub Dolt remote + single trusted writer in a dedicated experimental repository; read-only Beads clients can be many. Workers can execute independently in parallel, but workgraph mutation ownership serializes through one writer to avoid multiwriter bypass. GitHub/Transport receipts and Product SOT remain distinct. No always-on service.

**Alternative server:** externally reachable Dolt SQL server when real concurrent graph writes are needed. Adds service uptime, authenticated network endpoint, account lifecycle, backup/restore and ACL operations. Beads 045-002 demonstrates the local prerequisite only, not distributed uptime. No necessity demonstrated for baseline, so **DEFER**.

**Alternative GitHub Issues/Actions only:** could avoid Dolt, but native Beads already demonstrated graph/ready/history and direct issue equivalence/cost not measured; implementation of composite dependencies and work status may increase custom code. **NOT SELECTED** without measured migration benefit.

**Alternative custom ledger/Kernel clone:** rejects objective (new maintenance + host persistence). **NO_GO experimental design**.

**Measured net:** `Product bytes removed=0`; `new Product adapter/backup/credentials/ops cost=UNKNOWN`. Neither 36,715+12,020 bytes is automatically removable. Original close Recipe 36,279 bytes is mostly Product policy and must survive; prior 030 native adaptation was +90 bytes in one in-memory fixture, not deployed. Thus this is an architecture topology selection, not a demonstrated net maintenance win.

## V. Conditions before real Product choice

1. Product Control must select a **bounded consumer** and explicit authority, without using this experimental result to initialize #35 or migrate ongoing TCs. H6 Attendance remains independent.
2. Dedicated remote repository, protected `refs/dolt/data` lifecycle, one trusted writer with tightly scoped credentials and authenticated, read-only worker principals. Do not give agents privileged CLI/SQL or broad GitHub push rights. Beads 028 privileged-native bypass persists inside the writer's trusted computing base.
3. Portable Git/Transport receipts with exact source/attempt/effect IDs; archival retention independent from expiring Actions artifacts; identity reconciliation and `UNKNOWN` no-retry must be tested with opaque external providers.
4. Explicit Product equivalence matrix for current State Kernel `revision/event_count/hash-chain/snapshot HEAD`, effect classification race, Developer REJECTED authority reachability, IR/acceptance/Phase2, and active consumer/Recipe interfaces. **No weakening invariants to make replacement pass.**
5. One real authorized consumer-fit with two children, separate immutable write-sets, negative unauthorized-close and lost-ACK cases, net source/ops/backup measurements and rollback verified. If replacement requires a second ledger/scheduler or no measurable advantage, abandon full substitution and retain only Beads work tracking.
6. Rollback is to leave current Kernel/TC Core untouched and turn off experimental Beads consumer path. Never move an active TaskCycle to another store without separate Product migration authority and matched identities/receipts.

## VI. Final experimental ruling

`ARCHITECTURE_CANDIDATE_SELECTED_B_FIRST_GITHUB_REMOTE_SINGLE_WRITER`
`HOST_INDEPENDENCE_GO_EXPERIMENTAL_FOR_WORK_STATE`
`PRODUCT_KERNEL_FULL_REPLACEMENT_NOT_YET_QUALIFIED`
`EXPERIMENTAL_RESEARCH_CLOSE_WITH_LIMITATIONS`

This closes the **architecture selection** within the experimental line. It does not authorize Product implementation or label Beta/#35 READY. The next Product act is a **separate** competent Beta Control decision if/when it elects to consume the candidate. The experiment itself needs no more tests to select a topology; detailed Product conformance and cost remain explicit deferred acceptance criteria.
