# TS-EXECUTION-RUNNER-V0.2-001 — Terminal Result

Authority: **NONE**  
Product authority: **NONE**  
Product effect: **NONE**

## Terminal disposition

```yaml
experiment: TS-EXECUTION-RUNNER-V0.2-001
status: PASS_RECONCILED_TERMINAL
qualified_execution_subject: 8c62e4110683091a9d4ee2beacc984adc11239d1
branch: devlab/execution-runner-v0-2-001
DoD_01_through_14: PASS
Product_effect: NONE
Product_adoption: false
TC_Core_reopened: false
Upper_LC_changed: false
```

## What was adopted inside the experiment

The steady-state execution path is now data-driven:

```text
already-decided mechanical operation
  -> ExecutionRequest JSON
  -> Zod boundary validation
  -> registered TypeScript profile
  -> local or remote qualified binding
  -> validated ExecutionResult JSON
  -> validated ExecutionReceipt JSON
```

Human/architecture artifacts remain Markdown. GitHub Actions YAML remains provider glue only.

The runner is intentionally narrow:
- no arbitrary command transport;
- no generic orchestration runtime;
- no Product responsibility selection;
- no automatic Product retry;
- no semantic acceptance/review authority;
- no context runtime or universal ContextPackager.

## Runtime boundary

Zod is used only at serialized/trust boundaries:
- ExecutionRequest;
- ExecutionContextManifest;
- ExecutionResult;
- ExecutionReceipt.

Internal implementation remains ordinary TypeScript.

Malformed or unsupported requests fail closed before profile execution when identity is recoverable.

## Registered profiles

### canonical-sha256/v0

Bounded, pure JSON profile.

Terminal digest for the qualification fixture:

`sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728`

### git-exact-subject/v0

Read-only Git identity profile using only predetermined Git operations. No transported arbitrary Git argument list is accepted.

v0.2 profiles are explicitly **READ_ONLY**. No effectful profile is qualified by this experiment.

## Local qualification — Windows

Environment:
- Node 22.23.3 portable
- Windows local binding
- candidate exact source includes the qualified runner

Final focused suite:

```text
16 tests
16 PASS
0 FAIL
```

Steady-state canonical execution:

```text
Commander
  -> one bounded Node invocation
  -> result.json + receipt.json
```

Observed wall-clock: **882 ms**.

Portable result:
- result_status: PASS
- effect_state: NONE
- binding: local-commander
- subprocess_count: 0
- internal total: 5.094 ms
- request_identity: sha256:fb0a82c235ba8f17e81e139754e3bb6970ce6eb18ee06bc48c8dff813e92c474

No generated PowerShell, no .cmd, no parser process, no OpenCode and no Orca are required by the steady-state runner path.

## Remote qualification — GitHub Actions / Ubuntu

The exact qualified execution subject was invoked through a reusable public workflow from the synthetic private caller.

### Local/remote equivalence

Run: **37698737837**

- Ubuntu 24.04
- Node 22.23.3
- PASS / NONE
- selected_binding_ref: github-actions
- subprocess_count: 0
- request_identity: sha256:fb0a82c235ba8f17e81e139754e3bb6970ce6eb18ee06bc48c8dff813e92c474
- semantic_digest: sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728
- elapsed: ~14 s
- internal runner total: 10.81 ms
- artifact: 11516228100
- artifact digest: sha256:a00b5b74f3b6343f2f1cc8e05413b8d32a6af448e1ac89c31ae51abeefeb9039

Local and remote preserved the same stable request identity and semantic digest while using different ExecutionAttempt/binding metadata.

### Private caller correlation

Run: **37698748419**

- PASS / NONE
- selected_binding_ref: github-actions
- exact caller subject: git:mauedgar/ts-execution-private-consumer@9a21cde2717c3fd6f7f4722db2ca79da05710beb
- elapsed: ~19 s
- internal runner total: 3.426 ms
- artifact: 11517240237
- artifact digest: sha256:22a5300c96bb2cf15d7a5aab4b2ff2ca0627b7bc82794e70f4d12007f8268317

No PAT, GitHub App or additional secret was introduced.

## Private Product topology

Qualified topology:

```text
private caller
  -> reusable public workflow by exact lab SHA
  -> caller checkout remains private
  -> public runner checkout
  -> same TypeScript runner
  -> portable result/receipt
```

This supersedes the need for a public central runner to acquire private Product sources with its own default token.

## Context / transport

The runner preserves context identity/ref without becoming a context packager.

Qualified portable context manifest classes:
- REF_ONLY
- INLINE_SMALL
- FROZEN_BUNDLE

No standalone context service or universal ContextPackager was created.

Two synthetic Products used the same runner without shared mutable execution state or observed context crossing.

## Fallback semantics

Stable request identity excludes ExecutionAttempt identity.

Attempt A:
- same logical operation/profile/request identity;
- local binding preflight failure;
- BLOCKED / NONE;
- profile not executed.

Attempt B:
- new ExecutionAttempt;
- github-actions;
- run 37698737837;
- PASS / NONE;
- same request_identity;
- same semantic digest.

EFFECT_UNKNOWN remains fallback-blocking until competently reconciled.

The runner does not autonomously retry.

## Wait / observation

Async wait remains outside ts-exec.

Final qualification used GitHub/provider state as the remote observation surface:
- no Commander polling of remote Actions;
- no fixed max poll count;
- adaptive follow-up only while progress remained plausible;
- no-information observations in final qualification: 0.

No generic polling loop was added to the runner.

## Efficiency result

The optimization requirement passed.

For the local steady-state path, v0.1 required at minimum:

```text
materialize shell
-> parser process
-> execution process
```

v0.2 requires:

```text
one Node runner invocation
```

Measured/implied reductions from direct execution evidence:
- generated shell artifacts: 1 -> 0
- parser calls: 1 -> 0
- minimum external process launches: >=2 -> 1
- minimum ChatGPT/Commander execution calls: >=2 -> 1

Remote sample wall time:
- v0.1 canonical: ~17 s
- v0.2 canonical: ~14 s

Private caller sample:
- v0.1: ~20 s, Product-local workflow mechanics in 4 steps
- v0.2: ~19 s, one reusable workflow call in the private repo

Timing samples are evidence, not latency guarantees.

## Friction adjudication

Development friction observed:
- Orca local branch naming could diverge from the intended remote carrier name;
- long inline terminal commands were fragile under layered quoting;
- workflow_dispatch discovery on a candidate-only workflow depended on default-branch availability;
- the first reusable adapter omitted creation of the remote request directory.

All were mechanically reconciled without widening Product semantics.

Normal steady-state execution does not depend on OpenCode permission approval.

No broad permission weakening was introduced.

## Reuse-before-build outcome

The experiment did **not** rebuild harness/runtime capabilities already competently owned elsewhere.

Harness/provider-native ownership remains:
- OpenCode/Orca: worker/session/worktree/runtime mechanics;
- GitHub Actions: queue/run/artifact mechanics;
- Git/GitHub: exact object/forge identity;
- other competent harnesses: their own sessions, tools, sandbox and event models.

ts-exec owns only the narrow deterministic portable core.

## Residual limitations

- v0.2 only qualifies READ_ONLY execution profiles.
- Candidate-branch direct workflow_dispatch is not the preferred pre-adoption qualification route; reusable exact-SHA caller workflows are qualified.
- The runner reports effect state; it does not resolve Product-level UNKNOWN.
- No automatic fallback/retry policy was added.
- No Product/Tecnotron adoption occurs here.

## Terminal state

```yaml
Execution_Runner_v0_2:
  status: PASS_RECONCILED_TERMINAL
  qualified_for_execution_lab_core_adoption: true
  Product_authority_created: false
  Product_effect: NONE

next_possible_effect:
  target: mauedgar/ts-execution-lab:main
  meaning: adopt_execution_lab_core
  Product_effect: NONE

Product_boundary:
  Tecnotron_adoption: NOT_PERFORMED
  Upper_LC_Product_adoption: NOT_PERFORMED
```
