# Execution Runner v0.2 — Zod Boundary Addendum

Authority: NONE  
Product authority: NONE  
Product effect: NONE

Continuation of: `TS-EXECUTION-RUNNER-V0.2-001`

## Governing refinement

Use Zod only at untrusted/serialized portable runtime boundaries.

```text
serialized JSON
  -> Zod parse/safeParse
  -> trusted typed TypeScript
  -> mechanical execution
  -> construct portable output
  -> Zod validate
  -> publish JSON
```

### Required portable schemas

- `ExecutionRequestSchema`: REQUIRED
- `ExecutionResultSchema`: REQUIRED
- `ExecutionReceiptSchema`: REQUIRED when receipt is emitted as a distinct portable artifact

Additional schemas are allowed only when a real serialized external boundary exists.

Do NOT create schemas for internal trusted helper objects.

Prefer:

```ts
const ExecutionRequestSchema = z.object({...});
type ExecutionRequest = z.infer<typeof ExecutionRequestSchema>;
```

Avoid manually duplicating TypeScript interfaces and Zod schemas unless a concrete reason exists.

## Contract versions

Portable request/result/receipt artifacts must carry explicit contract versions.

Unknown incompatible versions fail closed with effect state NONE when failure occurs before any effectful execution.

No generic schema registry, migration framework, speculative compatibility matrix, or schema platform.

## Request boundary

Validation must complete before:
- provider launch;
- worktree mutation;
- effectful command invocation;
- Actions dispatch;
- Orca/OpenCode dispatch;
- conditioned external effect.

Normalize request parse outcomes:
- PASS -> execution may continue
- INVALID -> BLOCKED / effect NONE
- UNSUPPORTED_VERSION -> BLOCKED / effect NONE

Do not silently coerce materially incorrect semantics.

## Result boundary

Validate portable result before publication.

Minimum result statuses:
- PASS
- PARTIAL
- FAIL
- BLOCKED
- UNAVAILABLE

Effect state is a separate dimension:
- NONE
- CONFIRMED
- UNKNOWN

Invariant:
`result_status != effect_state`

Failure must never imply NONE automatically.

## Receipt boundary

A receipt records correlation/evidence only. It never creates Product authority, Developer acceptance, Independent Review PASS, or next-work selection.

Minimum correlation where applicable:
- contract_version
- Product_operation_ref
- ExecutionAttempt_ref
- request_identity
- selected_binding_ref
- started_at
- completed_at
- result_status
- effect_state
- exact_subject_ref optional
- provider_native_refs
- evidence_refs
- result_ref

## Retry boundary

Product_operation is stable across attempts. ExecutionAttempt is new per attempt.

- prior NONE -> retry may be possible
- prior UNKNOWN -> retry forbidden until reconciled
- prior CONFIRMED -> duplicate same-effect retry forbidden

Runner may expose retry-relevant facts but must not make Product-semantic retry decisions.

## Execution binding boundaries

Commander: bounded execution/result surface only; no semantic repo inspection or architectural reasoning.

GitHub Actions: deterministic execution/validation binding; Actions PASS is not review PASS, Developer acceptance, or Product authority.

Orca/OpenCode: runtime/worktree/implementation bindings only; provider-native state is provenance/liveness evidence, not Product truth.

## Scope

This addendum permits only execution-request/result/receipt contracts, Zod boundary validation, version checks, structured errors, correlation, mechanical preconditions, binding normalization, execution metrics, deterministic result materialization, and reduction of redundant shell/tool calls.

It does not authorize Product responsibility selection, Product lifecycle ownership, Independent Review adjudication, Developer acceptance, TC Core reopening, semantic composition, automatic retries, generic UNKNOWN reconciliation, provider scheduling, or a new state ledger.

## Governing principle

`The Execution Runner owns mechanical execution fidelity. It does not own Product meaning.`
