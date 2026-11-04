# TS-BEADS 047B — IR001 source repair candidate (non-effectful)

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, experimental only. **Decision:** `SOURCE_ONLY_REPAIR / NO_GO_EFFECT`. This document does not create a Product TaskCycle, grant, original ExecutionAttempt, SQL authority, host-independence PASS, or new owner. Original DoD blob `26388665fc0782fd10b24adca96a7dfa47c6a952` is frozen.

**IR001:** `mauedgar/ts-execution-transport@5d3c324c58c1d3a965723dc695882ef0cbd61654:reviews/TS-BEADS-047B-NOTEBOOK-OFFLINE-BOOTSTRAP-20261103-001/WEB_INLINE_IR001_SECURITY.md`, blob `51d04d171ec64e31b91c0f3f701248cb27e5227e`: 6 blocking findings + 5 advisories; `GO_SOURCE_LIMITED / NO_GO_EFFECT`. Original candidate `mauedgar/ts-execution-lab@404c358cb9717dd5446deae154afd576ede543ba` and its original successful CI `41743600975` remain immutable. Never reclassify their receipt.

## Actual source repair boundary

The original `Invoke-047B-NotebookOfflineBootstrap.ps1` contained an unsafe, callable `Execute` branch using self-asserted JSON. This repaired **source-only variant** removes the entire effectful bootstrap implementation and **unconditionally rejects `-Mode Execute` before any host query or filesystem operation, exit 41**. It no longer accepts caller-provided grant paths or digest parameters. An external grant or forged checksum cannot activate an effect. There is no SQL, DPAPI credential creation, Windows ACL mutation, Tailscale forwarding, Beads graph mutation, launch of native SQL subprocess, rollback or retry.

The remaining `Inspect` is read-only and **only** observes: exact notebook hostname; Windows identity SID *format, not exact SID pin*; pinned Dolt/Beads binary digests and versions; Dolt process absence; known likely SQL listener ports; Tailscale daemon self-online and JSON Serve/Funnel state; canonical `LOCALAPPDATA` ancestor reparse flags; absence of the exact local attempt root. Its output is sanitized. A positive read-only output explicitly labels original receipt, exact SID/peer and SQL/ACL/DPAPI/restore checks **UNVERIFIED**; it is not native or effect qualification. Concurrent host changes, other port aliases/processes, deeper filesystem attacks and Windows admin power remain outside this inspect probe.

## IR001 item-by-item dispositions for the next independent reviewer

| ID | Source-only change | Honest residual / admission status |
| --- | --- | --- |
| F001 | Forged grant acceptance path deleted; Execute hard-denied irrespective of args | Original external immutable grant and native provider receipt **not available**; effect NO_GO |
| F002 | Removed unverified root/anonymous account provisioning and `privileges.db` success claim | Dolt 2.6.2 root/anonymous inventory, scoped writer/reader and second-process persistence **not tested**; effect NO_GO |
| F003 | No ACL writes; read-only canonical ancestor/reparse check added | Final file/ancestor SID ACLs, TOCTOU and distinct nonprivileged user denial **not tested**; effect NO_GO |
| F004 | All local preparation/SQL effects removed; no partial local writes can occur through this runner | Future externally started original attempt, PARTIAL_LOCAL_EFFECT and UNKNOWN_SQL_EFFECT handling require a **distinct** admitted runner/review; no replay |
| F005 | No DPAPI secret, mutable plaintext, SQL stdin or logging of SQL in this runner | Future DPAPI round-trip, exact SID, OS logging policy and encrypted off-host recovery **not tested**; effect NO_GO |
| F006 | Read-only probe checks more native signals and sanitizes outputs | Actual notebook exact SID, peer identity, all alternate services and provider/Transport original receipt **not qualified**; no host-effect admission |
| A001 | Native SQL subprocess and SQL dialect removed from runnable source | Dolt 2.6.2 CLI/dialect still requires separately authorized disposable validation; none executed now |
| A002 | Blocking standard-input/write/read/WaitForExit removed entirely | Future effect runner must have bounded I/O, child handle ownership and UNKNOWN reconciliation |
| A003 | Removed DPAPI generation; no unsupported portable-backup claim | Off-host encrypted secret recovery + independent restore still absent |
| A004 | Actual Windows negative subprocess tests: unconditional denial, caller-forged grant, host spoof and wrong-host Inspect; source API bans | SID mismatch on actual notebook, ACL/reparse adversarial tests and SQL auth negatives still required |
| A005 | Workflow trigger expanded to runner, tests and contract changes on new branch; exact-head parent/scope and DoD are pinned | Each future candidate must have its *own* exact CI/IR; this run cannot qualify the original effectful file |

## Reconciliation and future effect dependency

No new native `ExecutionAttempt` was started. The *old* attempt identity `TS047B_NOTEBOOK_OFFLINE_BOOTSTRAP_20261103_001` remains historical reference, not a new attempt. Original IR001 and CI are terminal; do not replay either. No SQL listener, Tailscale Serve/Funnel, credential store, interhost issue graph, host outage test or encrypted remote backup is claimed.

Before any newly designed effectful stage: independent immutable authorizing control and provider receipt bound to subject/hash, principal/host, one original attempt and non-replay fence; target notebook read-only qualification; offline tested Dolt privilege/auth and negative cases; ACL/SID tests including reparse/TOCTOU and nonprivileged principal; DPAPI and recoverability/logging; child-process lifecycle and persistent partial/UNKNOWN reconciliation; independent security IR. **A new source candidate and separately competent grant are required**; no adjustment of a command-line flag can unlock this candidate.

## Requested IR002

An independent reviewer must inspect the **new immutable Git commit/tree/blobs**, exact CI results and this F001–F006/A001–A005 ledger. Reviewer must decide **source-only safety and whether residual requirements remain correctly classified** without scoring deferred native proof as complete. `GO_SOURCE_LIMITED` is possible; `GO_EFFECT` and `HOST_INDEPENDENCE_GO` are NOT requested and cannot be supported by these artifacts. `STRICT_READ_ONLY`, no re-use of IR001 reviewer as code author, and one durable receipt under a distinct IR002 identity.

**Product:** `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remains untouched, #34 closed, #35 independent, Kernel UNDECIDED. No customer data or secrets enter Git/CI/Transport.
