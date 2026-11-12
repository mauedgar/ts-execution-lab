---
artifact_id: TS-EE-GITHUB-NATIVE-ACQUISITION-CONTRACT-v1
owner: TS_EXECUTION_ENGINEERING_NONPRODUCT
kind: EXPERIMENTAL_READONLY_PROVIDER_PROVENANCE_CONTRACT
status: SOURCE_CANDIDATE_NOT_PRODUCT_QUALIFIED
date: 2026-11-11
product_effect: NONE
---
# GitHub native Control evidence adapter — bounded original execution acquisition

## Authority, historical originals and selected gap

Product SOT mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e, docs/SOURCE_OF_TRUTH.md, filesystem Kernel, Upper LC and TaskCycle Core remain authoritative. This experimental TS Execution Engineering utility does not create a Product actor, gate, scheduler, Control authority, reviewer acceptance or Kernel replacement.

Earlier PR25 remains DRAFT at exact frozen HEAD 34ed8e6c28c338e454889f9dfcf51f3cf1af899b, original GitHub Actions 43071422341 completed/success and original IR TS-EE-CONTROL-JOIN-PR25-WEBINLINE-IR001-20261111-001 terminal NO_RECOMMEND/FULL_SOURCE/0F/2A. Immutable original review at mauedgar/ts-execution-transport@22523dad730c55cd19b8a9c5f29bf23b2f0de1ed:results/TS-EE-CONTROL-JOIN-PR25-WEBINLINE-IR001-20261111-001/ORIGINAL.md. Never retry these original attempts. This repair is NEW source, new branch and one separately identified original qualification, not retroactive IR acceptance.

A01 HIGH: legacy source reconcile(external,native,guard,run) accepts mutually consistent caller-supplied evidence, and unit tests alone cannot prove authenticated GitHub provenance. A02 MEDIUM: caller-supplied run listing and Git delta summary lacks full native paginated proof. This candidate acquires facts from authenticated GET requests to the literal api.github.com host, pinned immutable external Control request and historical original terminal GitHub provider run. The target is historical run 43071422341, READ ONLY and NEVER replayed. A02 independent physical golden is a different advisory and remains BLOCKED.

## Native acquisition, mandatory boundaries and proof

Source tools/ts_ee_github_native_acquisition.py:
- A separate immutable external Control request, create-only in mauedgar/ts-execution-transport, pins qualification original ExecutionAttempt, source parent/tree/workflow SHA and exact historical original run/commit/tree/marker/workflow/request blobs. JSON block has strict framing in immutable Markdown. Own Git blob and bytes are verified. No marker or request grants Developer authority: Control must independently preapprove, publish, verify and reconcile them.
- Original marker/guard runs FIRST, before GitHub token or native reads, with exact original source parent/tree, workflow blob, attempt, immutable Control request ref and one-marker-only delta, run_attempt=1. No SQL/host/secrets before original guard.
- The adapter uses GitHub Actions token with **contents:read and actions:read** on a disposable runner. All provider observations are native authenticated TLS GET, pinned source blobs/IDs and exact historical run. Redirects, API failures and oversized payloads are blocked without retries. Token never printed.
- Two full recursively enumerated Git trees must be NONTRUNCATED and differ by exactly one newly added ordinary blob marker. Every tree/blob/submodule mode and full path hierarchy are structurally checked; duplicate tree paths, malformed ancestor trees, blob-directory collisions, missing parent nodes and orphan directories block. Canonical Git ancestor directory SHA changes are expected; all non-tree leaves are compared by path/type/mode/blob. No hidden add/modify/rename/delete/copy, unexpected marker mode, invalid tree, missing blob or changed workflow may pass.
- **Single-run-per-isolated-branch ONLY:** requires native total_count=1, exactly one run record, exact branch, no Link pagination header and a second identical complete native page read. Any second run or even the presence of a next/last Link BLOCKS. Multi-page GitHub run histories are deliberately UNSUPPORTED by this binding, instead of pretending 101+ pagination is qualified. Each new original operation MUST use a distinct isolated branch/ExecutionAttempt.
- Fixture selftest in tools/selftest_ts_ee_github_native_acquisition.py uses provider-shaped fake responses and explicit negative codes, NOT live API; a separate GitHub Actions step MUST perform authenticated real provider reads for an already terminal historical run. Unit mocks must never be reported as independently trustworthy provider output.
- Competent Control performs deferred join on the actual qualifying attempt native run/job/logs/commit and frozen external request. No unqualified provider fallback (TinyFish, arbitrary browser or Commander), and no external source writes from the adapter.

## New bounded repair candidate after terminal PR26 IR001

Original PR26 source IR001 at frozen HEAD b9e8481205ccef37e4d9e50d0e17c744e73ab745 ended **NO_RECOMMEND/FULL_SOURCE/0F/2A**, immutable original mauedgar/ts-execution-transport@8fafc070f42fd596c9e5b588fed485fafb9f12fd:results/TS-EE-GITHUB-NATIVE-PR26-WEBINLINE-IR001-20261111-001/ORIGINAL.md. The actual historical native provider qualification run 43119529214 stays terminal PASS and IS NOT repeated or reinterpreted as independent source acceptance. A01 MEDIUM concerned real 101+ run pagination; because this method explicitly requires exactly ONE run on a dedicated branch, we **remove general pagination rather than simulate 101 new runs**. A02 LOW/MEDIUM required complete Git tree structure before comparing non-tree leaf hashes and evidence of collision/rename/symlink/submodule blocking; the successor source and expanded exact-code negative tests address that at the declared bound. This successor requires a NEW original CI attempt, actual native single-run read, and a NEW independent source review before general EE adoption. It does not retroactively close PR26's terminal A01/A02 or inherited PR23 A03.

## Assurance ceiling and stop conditions

These preconditions rely on authenticated GitHub TLS/API origin and independently authorized Control request. A fully forged network/API origin defeats content-only checks; no source selftest can prove an independently authenticated Developer grant. The legacy Control join may accept a coherently fabricated dict if invoked outside the adapter; this method only accepts authenticated, bounded native response construction. It does not cryptographically authenticate Developer intent or physical PG16 identity.

Use distinct branch, frozen source parent commit/tree/workflow Git blob, external request before marker, one marker-only dispatch, one ExecutionAttempt, one original provider run/job and create-only original result. If FAILED/BLOCKED/UNKNOWN, do not rerun the attempt; separately reconcile and repair only within competent existing authority. Independent STRICT_READ_ONLY source review and competent EE disposition are required before general adoption.

No Product, Neon, notebook, PostgreSQL role/DDL/genesis, two physical hosts, LAN writer locks, lost COMMIT ACK, restore or Beta Run008 effects. Original physical A02 golden P0 BLOCKED, PA01–PA04 OPEN and Product Kernel replacement NO_GO. Source-only provenance PASS cannot change them.

## Current qualifying run — separately authenticated native proof (candidate successor)

PR27 independent IR001 terminal **NO_RECOMMEND/FULL_SOURCE/0F/1A** identified a remaining A01 MEDIUM gap: adapter qualify() could accept a locally forged current --original-guard even though the original pinned private workflow had performed a separate guard first. The new successor source candidate requires qualify(fetch, request_ref, guard, runtime) to authenticate the **CURRENT**, not merely historical target, original Actions run via GitHub native HTTPS REST before returning PASS. The original PR27 reviewer and provider run are immutable and NOT rerun.

In the new isolated private Transport original workflow the caller's native GITHUB_ACTIONS, GITHUB_REPOSITORY, GITHUB_REF, GITHUB_SHA, GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT and GITHUB_EVENT_NAME are compared to all relevant original guard fields and the frozen external Control request. Guard status TS_EE_ORIGINAL_GIT_TRANSITION_PASS and version TS-EE-ACTIONS-ORIGINAL-BINDING-v1 are required, not self-asserted by a marker.

The adapter performs separate authenticated GitHub GET calls using read-only contents/actions token for the **current run** (it must be in_progress or queued, attempt 1, exact repo/ref/head/workflow), current Git head and parent commits/tree, the current exact commit file-list consisting of only one newly added marker Git blob, original marker bytes and full frozen workflow blob at current head, and the current branch's sole run list with second-page consistency check. It rejects any mismatch before reading the old historical terminal source target. This authenticates original current-provider identity under the bounded provider/TLS trust model; it does not give itself Developer authority, sign GitHub or prove arbitrary web clients' environment integrity.

Negative fixtures must exercise the real adapter with false status, current run ID, repository, ref, HEAD, tree, marker blob, current native provider run, marker response and duplicate current branch runs; each is a distinct exact reason. Fixture tests are synthetic and separate from live read-only GitHub GET on both current original and historical completed run. The new original qualifying workflow must freeze a source HEAD/tree/workflow blob, external private Control request before a marker-only dispatch, and confirm exactly one provider-native run with no CI reruns. Reviewers then assess source and logs independently. A native PASS alone is NOT method acceptance.

The inherited original guard subprocess Git environment/PIPE A03 remains OPEN, outside this current-run A01 repair. Source-only or native GitHub success does not affect physical A02 independent golden P0 BLOCKED/P1 NO_RECOMMEND/PA01–PA04 OPEN, Product Kernel replacement NO_GO.
