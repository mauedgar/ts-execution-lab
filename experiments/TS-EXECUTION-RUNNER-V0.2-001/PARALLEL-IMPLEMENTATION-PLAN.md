# TS Execution Runner v0.2 — Parallel Implementation Plan

Experiment: TS-EXECUTION-RUNNER-V0.2-001
Authority: NONE
Product effect: NONE

Exact integration baseline:
- repository: mauedgar/ts-execution-lab
- branch: devlab/execution-runner-v0-2-001
- commit: 303e875ce54e53b29c4f662ca0e1e878283abed7
- tree: e9fd2c06dd904a833954e98ed14405ac5c1b074b

This is one experiment with parallel bounded implementers, not multiple architecture waves.

## Frozen portable interface for parallel work

Normal request is binding-agnostic.

ExecutionRequest v0.2 carries:
- contract_version = ts-execution-request/v0.2
- request_id
- Product_ref
- Product_operation_ref
- ExecutionAttempt_ref
- execution_profile_ref
- subject_ref
- context_id
- optional context_manifest_ref
- input object

Selected binding is execution metadata, NOT request semantics.

Result:
- contract_version = ts-execution-result/v0.2
- request/Product operation/attempt/profile/subject/context identities
- request_identity sha256
- result_status: PASS | PARTIAL | FAIL | BLOCKED | UNAVAILABLE
- effect_state: NONE | CONFIRMED | UNKNOWN
- optional semantic_digest
- optional profile_output/errors
- observation

Receipt:
- contract_version = ts-execution-receipt/v0.2
- Product_operation_ref
- ExecutionAttempt_ref
- request_identity
- selected_binding_ref
- started_at/completed_at
- result_status/effect_state
- optional exact_subject_ref
- provider_native_refs[]
- evidence_refs[]
- result_ref
- authority_created=false
- Product_effect_created=false
- observation

Zod at serialized boundaries only.
TypeScript internally.
Unknown contract versions fail closed before effects.
result_status != effect_state.
No arbitrary command strings.
No generic orchestrator.

## Worker A — CORE

Branch:
devlab/execution-runner-v0-2-core-001

Owned paths:
- package.json
- package-lock.json if npm creates it
- src/**
- schemas/** (v0.2 request/result/receipt updates/additions)
- test/core-*.test.ts
- test/profile-*.test.ts
- examples/requests/** if needed

Responsibilities:
- implement minimal ts-exec CLI: validate, run, profiles
- Zod ExecutionRequest/Result/Receipt schemas
- known profiles canonical-sha256/v0 and git-exact-subject/v0
- result/receipt validation before publish
- structured failure result/receipt for pre-effect invalid/unsupported request when identity is safely recoverable
- timings/subprocess_count
- Node 22 native TypeScript qualification locally via tests
- no Actions YAML edits
- no private consumer edits
- no experiment terminal RESULT/EFFICIENCY docs
- commit/push branch, stop

## Worker B — REMOTE BINDING

Branch:
devlab/execution-runner-v0-2-actions-001

Owned paths:
- .github/workflows/ts-exec-runner.yml
- .github/workflows/ts-exec-reusable.yml
- .github/workflows/* only when strictly needed by this experiment
- experiments/TS-EXECUTION-RUNNER-V0.2-001/remote/**
- synthetic private consumer workflow/files only in mauedgar/ts-execution-private-consumer

Responsibilities:
- implement minimal Actions adapter around the frozen interface above
- prepare workflow_dispatch runner and reusable workflow_call variant
- Product/private caller should retain private checkout where possible
- no PAT/App/secrets
- no duplicate profile semantics in YAML
- provider adapter calls node src/cli.ts run
- may create fixtures/request JSON under remote/ only
- do not edit src/** or package.json
- if dependency on missing core bytes prevents actual dispatch, prepare mechanically complete binding and stop with exact dependency
- commit/push branch, stop

## Worker C — QUALIFICATION / EFFICIENCY

Branch:
devlab/execution-runner-v0-2-qualification-001

Owned paths:
- experiments/TS-EXECUTION-RUNNER-V0.2-001/qualification/**
- experiments/TS-EXECUTION-RUNNER-V0.2-001/EFFICIENCY-DRAFT.json
- experiments/TS-EXECUTION-RUNNER-V0.2-001/QUALIFICATION-DRAFT.md
- test/qualification-*.test.ts only

Responsibilities:
- derive exact qualification matrix from WORK_PACKAGE + REUSE + ZOD
- prepare local/remote equivalence fixtures and expected identities
- prepare fallback proof fixture where Attempt A = safe EFFECT_NONE binding/preflight failure and Attempt B = new ExecutionAttempt
- prepare before/after efficiency measurement template using v0.1 evidence
- do NOT claim PASS for unexecuted proofs
- do NOT edit src/** or workflows
- commit/push branch, stop

## Integration rule

No worker merges.
No worker modifies devlab/execution-runner-v0-2-001 directly.
No worker semantically approves another worker.
Web Execution Engineering will reconcile all three siblings and compose the exact candidate.
