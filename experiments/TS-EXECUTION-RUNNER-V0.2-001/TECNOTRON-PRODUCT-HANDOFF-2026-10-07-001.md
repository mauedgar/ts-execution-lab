# TS — Developer Lab · Execution Runner v0.2 Product Handoff

Date: 2026-10-07

```yaml
artifact:
  kind: EXECUTION_CAPABILITY_PRODUCT_HANDOFF
  authority: NONE
  Product_authority_created: NONE
  Product_effect: NONE

source:
  laboratory: mauedgar/ts-execution-lab
  canonical_lab_branch: main
  terminal_experiment: TS-EXECUTION-RUNNER-V0.2-001
  terminal_commit: 46824d91e5b6e1cd05031306dd38302afe399e6a
  qualified_execution_subject: 8c62e4110683091a9d4ee2beacc984adc11239d1

destination_boundary:
  owner: Tecnotron Product Control
  automatic_adoption: false
  Product_TaskCycle_created: false
```

## Purpose

Provide a bounded handoff of the now-canonical Execution Lab v0.2 substrate to competent Tecnotron Product Control.

This artifact does **not** adopt the runner into Tecnotron, does not amend Upper LC, and does not create a Product TaskCycle.

## Qualified capability

The lab now has a canonical narrow deterministic execution core:

```text
portable ExecutionRequest JSON
-> Zod trust-boundary validation
-> registered TypeScript profile
-> qualified execution binding
-> validated ExecutionResult JSON
-> validated ExecutionReceipt JSON
```

Qualified bindings:
- Windows local Node 22.23.3 through one bounded invocation;
- GitHub Actions Ubuntu 24.04 / Node 22.23.3 through reusable workflow_call by exact lab SHA.

Qualified profiles:
- profile://ts-execution-lab/canonical-sha256/v0
- profile://ts-execution-lab/git-exact-subject/v0

Both are READ_ONLY in v0.2.

## Empirical evidence

Windows:
- 16/16 tests PASS.
- steady-state canonical invocation wall-clock: 882 ms.
- request/result/receipt validation through Zod.
- no generated shell, parser subprocess, OpenCode or Orca required by the steady-state runner path.

GitHub Actions:
- exact candidate equivalence run: 37698737837 — PASS.
- private caller correlation run: 37698748419 — PASS.
- same stable request identity across local/remote attempts.
- same canonical semantic digest.
- no extra PAT/App/secret.

Context:
- REF_ONLY / INLINE_SMALL / FROZEN_BUNDLE contracts qualified.
- no universal ContextPackager created.

Fallback:
- stable Product operation/request identity;
- new ExecutionAttempt per attempt;
- EFFECT_NONE preflight can permit a later attempt mechanically;
- EFFECT_UNKNOWN remains blocking until competent reconciliation;
- runner does not create retry authority.

## Boundary preserved

The runner owns mechanical execution fidelity only.

It does not own:
- Product responsibility selection;
- semantic planning;
- Independent Review;
- Developer acceptance;
- Phase 2 authority;
- TaskCycle close/reopen;
- Product-level UNKNOWN policy;
- automatic retry;
- next-work selection;
- Product Control.

Actions PASS remains distinct from semantic/Product acceptance.

## Reuse-before-build

No generic agent runtime was created.

Harness-native ownership remains with OpenCode/Orca, Codex, Gemini CLI, Claude Code, GitHub Actions, Git/GitHub, or another competent provider as selected externally.

The runner provides only cross-binding deterministic invariants and portable receipts.

## Product Control decision requested

On fresh Tecnotron Product observation, Product Control may decide whether and how to:
- register this lab capability in Tecnotron's capability/navigation SOT;
- bind appropriate existing deterministic Recipes to it;
- qualify any Tecnotron-specific execution adapter;
- preserve current Product authority and lifecycle boundaries.

Do not infer Product adoption from the existence of this handoff.

## Important limitations

- v0.2 qualifies READ_ONLY profiles only.
- effectful profiles require separate empirical qualification and explicit effect semantics.
- candidate-branch Actions qualification is proven through reusable exact-SHA caller workflows.
- no generic provider scheduler, state ledger, context service, or orchestration platform is justified by this experiment.

## Execution Engineering findings carried as evidence, not Product policy

See:
- `experiments/TS-EXECUTION-RUNNER-V0.2-001/EXECUTION-ENGINEERING-FINDINGS.json`

Those findings include:
- branch-binding correspondence guard pressure;
- materialized launcher preference over nested quoting;
- reusable exact-SHA workflow qualification before main adoption;
- compact remote execution summary as an observation aid.

Product Control may accept, reject, or defer any corresponding Product implication.

## Stop state

```yaml
Execution_Lab_v0_2:
  canonicalized: true
  Product_effect: NONE

Tecnotron:
  adopted: false
  modified: false

Upper_LC:
  modified: false

next_owner:
  Tecnotron_Product_Control
```
