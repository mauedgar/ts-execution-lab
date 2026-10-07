# TS-EXECUTION-RUNNER-V0.2-001 — Terminal Result

Authority: **NONE**  
Product authority: **NONE**  
Product effect: **NONE**

## Terminal disposition

```yaml
experiment: TS-EXECUTION-RUNNER-V0.2-001
status: PASS_RECONCILED_TERMINAL
qualified_execution_subject: 07c0c2a383fc31ae2d46c4e4d7a71caab4d7e456
qualified_execution_tree: 65fa021d23f9ca166f87aaba668bd951352dd92b
branch: devlab/execution-runner-v0-2-001
DoD_01_through_14: PASS
Product_effect: NONE
TC_Core_reopened: false
Upper_LC_changed: false
```

## Adopted execution shape inside the experiment

```text
already-decided mechanical operation
  -> ExecutionRequest JSON
  -> Zod trust-boundary validation
  -> registered TypeScript profile
  -> qualified local/remote binding
  -> validated ExecutionResult JSON
  -> validated ExecutionReceipt JSON
```

Markdown remains human-facing. JSON is the portable machine carrier. TypeScript/Node owns deterministic execution mechanics. YAML is provider glue only. The runner does not own Product semantics, retries, acceptance, review, lifecycle, or generic orchestration.

## Runtime contracts

Qualified portable contracts:
- `ts-execution-request/v0.2`
- `ts-execution-context-manifest/v0.2`
- `ts-execution-result/v0.2`
- `ts-execution-receipt/v0.2`

Zod is used at serialized/trust boundaries only. Internal trusted implementation remains ordinary TypeScript. Unsupported/malformed contracts fail closed before effectful profile execution when identity is recoverable.

Result status and effect state remain separate:

```text
PASS | PARTIAL | FAIL | BLOCKED | UNAVAILABLE
!=
NONE | CONFIRMED | UNKNOWN
```

## Qualified profiles

### canonical-sha256/v0
Bounded read-only JSON profile.

Terminal semantic digest:

`sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728`

### git-exact-subject/v0
Read-only Git identity profile using only predetermined Git operations. No transported arbitrary Git argument list is accepted.

v0.2 qualifies **READ_ONLY profiles only**.

## Windows/local qualification

Environment:
- Windows
- Node 22.23.3
- exact implementation subject `07c0c2a3...`

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
  -> validated result.json + receipt.json
```

Observed:
- request_identity: `sha256:fb0a82c235ba8f17e81e139754e3bb6970ce6eb18ee06bc48c8dff813e92c474`
- semantic_digest: `sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728`
- result_status: PASS
- effect_state: NONE
- binding: local-commander
- subprocess_count: 0
- internal total: 5.094 ms
- observed wall-clock: 857 ms

Normal steady-state execution requires no generated PowerShell, no .cmd, no separate parser process, no OpenCode and no Orca.

## Remote qualification — GitHub Actions / Ubuntu

The exact implementation subject was checked out by SHA through the reusable public workflow.

### Local/remote equivalence

Run: **37699334066**

Verified in durable GitHub logs:
- reusable workflow ref: `07c0c2a383fc31ae2d46c4e4d7a71caab4d7e456`
- checkout exact SHA: `07c0c2a383fc31ae2d46c4e4d7a71caab4d7e456`
- Ubuntu runner
- Node 22.23.3
- PASS / NONE
- selected_binding_ref: github-actions
- subprocess_count: 0
- request_identity: `sha256:fb0a82c235ba8f17e81e139754e3bb6970ce6eb18ee06bc48c8dff813e92c474`
- semantic_digest: `sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728`
- internal runner total: 4.957 ms
- elapsed: 14 s
- artifact: 11516742025
- artifact digest: `sha256:a86b52d9c61c2b27de0bf5386118bb1bb2db0bdd274212e68c3e0fcfd7fee786`

The same stable request identity and semantic digest were preserved across local and remote bindings while ExecutionAttempt metadata differed.

### Private caller correlation

Run: **37699344269**

Verified:
- exact lab subject: `07c0c2a383fc31ae2d46c4e4d7a71caab4d7e456`
- PASS / NONE
- selected_binding_ref: github-actions
- exact caller subject: `git:mauedgar/ts-execution-private-consumer@f5aeba43b4168b0040f44f353082e055dba8e152`
- elapsed: 19 s
- internal runner total: 4.564 ms
- artifact: 11516871482
- artifact digest: `sha256:f3eb6e06d7b1f3df93e1bcc8931df4c579157d7b7156cbf0024835777062808f`

No PAT, GitHub App or additional secret was introduced.

## Context / transport

The runner preserves context identity without becoming a context runtime or packager.

Qualified context manifest modes:
- REF_ONLY
- INLINE_SMALL
- FROZEN_BUNDLE

The context contract is portable JSON/Zod. Context acquisition/materialization remains outside the runner. Previous private concurrent transport evidence remains reusable, and the v0.2 namespace preserves Product / Product_operation / ExecutionAttempt isolation.

No universal ContextPackager or shared mutable context slot was created.

## Fallback

Stable request identity excludes ExecutionAttempt identity.

Attempt A:
- same logical operation/profile/request identity;
- local binding launch failure before runner load;
- request validation had already produced the stable identity;
- result_status: BLOCKED;
- effect_state: NONE;
- profile_executed: false.

Attempt B:
- NEW ExecutionAttempt;
- github-actions;
- run 37699334066;
- PASS / NONE;
- same request_identity;
- same semantic digest.

`EFFECT_UNKNOWN` remains fallback-blocking until competent reconciliation. The runner never autonomously retries.

## Wait / observation

Async wait remains outside `ts-exec`.

Terminal remote qualification used GitHub provider state/logs/artifacts:
- no Commander polling of remote Actions;
- no fixed max-poll count;
- adaptive observation based on the observed ~11–20 s range;
- equivalence: terminal at the first ~10 s observation;
- private caller: RUNNING_EXPECTED at ~10 s, terminal by ~18 s;
- no no-information observations in the final qualification.

Commander was used only for bounded dispatch/local execution and explicit local-worker diagnosis, not as the remote result surface.

## Efficiency

DOD-12 passed with measured improvements.

Local steady-state:

```text
v0.1:
materialize shell -> parser process -> execution process

v0.2:
one bounded Node runner invocation
```

Measured/evidenced reductions:
- generated shell artifacts: 1 -> 0
- parser calls: 1 -> 0
- minimum external process launches: >=2 -> 1
- minimum ChatGPT/Commander execution calls: >=2 -> 1

Remote sample:
- v0.1 canonical: ~17 s
- v0.2 terminal canonical: ~14 s

Private caller sample:
- v0.1: ~20 s and 4 Product-local mechanical workflow steps
- v0.2: ~19 s and one reusable-workflow call

Timing samples are observational, not latency guarantees.

## Development worker routing

Parallel bounded implementation used OpenCode with explicit OpenAI models:
- Core: GPT-5.6 Sol
- Actions binding: GPT-5.6 Luna
- Qualification: GPT-5.6 Luna

Those workers produced isolated sibling candidates; Web reconciled and composed them by exact commit. OpenCode is not required in the steady-state execution path.

## Friction adjudication

Observed execution-engineering friction:
- Orca branch aliases diverged from intended remote branch names;
- long inline terminal sends were fragile under layered quoting;
- candidate-only workflow_dispatch depended on default-branch workflow discovery;
- initial reusable adapter omitted request-directory creation;
- one historical OpenCode permission denial occurred on transport work.

These remained binding/development observations. They did not require Product policy, a permission project, TC Core reopening, broad permission weakening, or a new orchestration platform.

## Reuse-before-build outcome

Harness/provider-native ownership remains native:
- OpenCode/Orca: worker/session/worktree/runtime mechanics;
- GitHub Actions: queue/run/artifact mechanics;
- Git/GitHub: exact object and forge identities;
- other competent harnesses: their own tool/session/sandbox/event models.

`ts-exec` owns only the narrow deterministic portable execution core.

## Residual limits

- v0.2 qualifies READ_ONLY profiles only.
- Direct workflow_dispatch of a candidate-only workflow is not the preferred pre-adoption route; exact-SHA reusable workflow callers are qualified.
- The runner reports effect state but does not resolve Product-level UNKNOWN.
- No automatic retry/fallback policy was added.
- No Product/Tecnotron adoption is performed by this experiment.

## Terminal state

```yaml
Execution_Runner_v0_2:
  status: PASS_RECONCILED_TERMINAL
  qualified_for_execution_lab_core_adoption: true
  qualified_execution_subject: 07c0c2a383fc31ae2d46c4e4d7a71caab4d7e456
  Product_authority_created: false
  Product_effect: NONE

next_eligible_effect:
  target: mauedgar/ts-execution-lab:main
  meaning: ADOPT_EXECUTION_LAB_CORE
  Product_effect: NONE

Product_boundary:
  Tecnotron_adoption: NOT_PERFORMED
  FitFlow_adoption: NOT_PERFORMED
  Upper_LC_Product_adoption: NOT_PERFORMED
```
