---
artifact_id: TS-EE-ACTIONS-ORIGINAL-RUN-IDENTITY-BINDING-v1
owner: TS_EXECUTION_ENGINEERING_TECHNICAL_METHOD
class: NONPRODUCT_EXPERIMENTAL_EXECUTION_CONTRACT
status: CANDIDATE_NOT_PRODUCT_ADOPTED
created: 2026-11-11
product_effect: NONE
---
# Actions original-execution identity — two-commit nonProduct bridge

## Evidence, authority and problem
PR20 IR002 was terminal **NO_RECOMMEND / FULL_SOURCE / 0F / 2A**. A01: GITHUB_RUN_ATTEMPT=1 prevents the retry of one native GitHub run but does NOT prevent a later push to the same branch/workflow having a new run with attempt 1. The existing A003 script does not require its workflow's own exact Git blob, source HEAD and tree. A workflow cannot embed its own final Git blob hash without a circular reference. The new method resolves that problem by freezing the original source **before** one marker-only dispatch commit, never by modifying or replaying terminal A003 or IR002.

Original PR20 subject HEAD b9263f8e20dad3b6c2060cff55b1abbc7bfdecd4, tree e8a53c9600a0c4f4933c39754f632b5b4f52f9b6; run 43037911945 SUCCESS; IR002 original mauedgar/ts-execution-transport@20ff6bace9255e54007a2b2f5c3f81ee357a17e7:results/TS-R3-A02-NATIVE-PG16-PR20-WEBINLINE-IR002-20261111-001/ORIGINAL.md is immutable. No Product authority is created.

## Five bounded transitions
1. **Freeze source parent**: create a new isolated nonProduct branch with all sources, an original Actions workflow triggered ONLY by creation of ONE known marker path under .github/ts-ee-original-dispatch/. Publishing source/workflow does not dispatch. Freeze source-parent Git commit SHA, tree SHA, workflow Git blob, branch and exact write-set.
2. **Publish external Control request BEFORE dispatch**: create exactly one immutable request in mauedgar/ts-execution-transport:requests/<identity>/REQUEST.md containing original responsibility, owner, Developer/experiment grant, ExecutionAttempt, source-parent SHA/tree, workflow SHA, exact trigger marker path, expected effect/result, stop conditions and evidence. No marker blob here: it would create a hash cycle because marker contains this external request's immutable commit SHA. Predeclare all other marker fields and verify them separately.
3. **Original marker-only dispatch**: create a single JSON file at that exact marker path containing version, original attempt, repo/ref, source-parent SHA/tree, workflow path/blob, marker path and immutable external Control request Git ref. Control checks all values against that original request, computes expected marker bytes/blob in memory, then commits the marker alone with its exact source-parent as sole parent. This single push dispatches GitHub Actions once.
4. **Before ANY effect** the job executes tools/ts_ee_original_actions_binding.py with repo root, exact marker path and attempt. It verifies GitHub native SHA/ref/repo/run ID and run_attempt=1; checked-out HEAD equals GITHUB_SHA; HEAD has ONE parent equal frozen parent; source parent tree matches frozen tree; original workflow SHA equals marker value in parent AND child; changed path/status is exactly A <marker>. No source, SQL, network, host or role effects before positive preflight. Failure BLOCKED_PRECONDITION without retry.
5. **Deferred durable join**: Control observes the original provider run_id/head once, verifies marker Git blob and external Control request, workflow SHA, actual receipts and result/effects. Terminal/UNKNOWN effects never replay. Any subsequent modified source/workflow requires a NEW request and ExecutionAttempt; never reuse A003 or this original identity.

## Assurance ceiling
The validator proves a bounded Git transition, not Developer grant, provider trust, permission ownership, Product source acceptance, complete PostgreSQL semantics or host-independent execution. The JSON marker is **data**; it cannot grant authority. The external immutable Control request and its pre/post marker checks supply independent competent ownership. The validator does not consume untrusted arbitrary code, construct shell commands, or execute data. A second branch or history rewrite cannot be admitted as the same terminal original under a competent immutable external receipt, even though a user with GitHub write permission could author a different experiment.

This is a nonProduct EE technical candidate, NOT a new Product scheduler/actor/TaskCycle gate or a retroactive repair of PR20. A synthetic test PASS does not qualify a Product binding. Production/Neon/notebook/A02 physical remain NO_GO; PR20 remains DRAFT and IR002 verdict unchanged.

## Qualification and negative test plan
One future original disposable GitHub Actions qualification: publish source, publish external request, create exactly one marker, observe original CI run/job/result, check both Git and transport IDs and original effect. One positive plus nine synthetic negative tests: second attempt; wrong HEAD, repository, ref, missing run ID; extra commit; changed frozen workflow SHA; extra file in marker commit; wrong source parent. Independent source review of candidate required before EE general adoption. A test script cannot infer run ownership or change an existing Product authority state.

## Separate A02 boundary
A02 from PR20 IR002 is NOT solved by identity binding. The synthetic lab and golden share the frozen schema source and one PG16 cluster. Actual physical golden/source/role/container/volume identity requires separate read-only evidence from an independently curated oracle and competent physical fixture. No physical writes or role/grant changes follow from this contract. Keep PA01–PA04 OPEN and A02 physical NO_GO until independently verified and authorized.
