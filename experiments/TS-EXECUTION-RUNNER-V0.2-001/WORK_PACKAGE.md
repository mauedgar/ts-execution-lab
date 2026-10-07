# TS Execution Runner v0.2 — Work Package

## Authority

```json
{
  "experiment_id": "TS-EXECUTION-RUNNER-V0.2-001",
  "authority": "NONE",
  "Product_authority": "NONE",
  "Product_effect": "NONE",
  "implementation_authorized": true,
  "merge_to_main_authorized": false
}
```

Repository: `mauedgar/ts-execution-lab`
Branch: `devlab/execution-runner-v0-2-001`
Research base: `1e1323e7510465f97eab39612b5d11a4a5b5ef25`

Do not modify Tecnotron, FitFlow, devBrain, Attendance, Proof/Order Evidence, or any real Product repository.

Synthetic supporting repos that may be reused:
- PRIVATE `mauedgar/ts-execution-transport`
- PRIVATE `mauedgar/ts-execution-private-consumer`

## Responsibility

`ADOPT_DATA_DRIVEN_TYPESCRIPT_EXECUTION_RUNNER_V0_2`

Replace generated shell as the normal execution mechanism with a small known-profile TypeScript/Node runner.

The architecture target is:

```text
Human semantics       -> Markdown
Machine carriers      -> JSON
Runtime contracts     -> JSON Schema + TypeScript types/runtime validation
Execution mechanics   -> TypeScript/Node
GitHub provider glue  -> minimal YAML
Windows shell         -> adapter/bootstrap only
.cmd                   -> bootstrap/emergency only
```

The runner is NOT:
- a generic shell;
- an orchestrator;
- Product authority;
- lifecycle state;
- a context runtime;
- a retry engine;
- an autonomous worker system.

## Questions resolved before implementation

1. Permission friction is feedback, not a separate responsibility. Do not broadly change OpenCode/Orca/GitHub permission policy. The steady-state runner path should avoid needing OpenCode entirely.
2. Dispatch/routing/wait remain provider/control concerns in this iteration. Do not absorb them into a central orchestrator.
3. No arbitrary command input. Profiles are registered known code.
4. Prefer zero runtime dependencies. First empirically qualify Node 22 native TypeScript execution on local Windows and GitHub Ubuntu. If it is not competent on both, use the smallest pinned build/runtime alternative and record the added cost.
5. Existing Upper LC/TC Core identities and authority semantics remain unchanged.

# Definition of Done

## DOD-01 — Native TypeScript execution qualification

Prove the chosen TypeScript execution method on:
- local Windows Node 22.x;
- GitHub Actions `ubuntu-latest` Node 22.x.

Preferred:
`node src/cli.ts ...`

If native TS execution is not competent on either binding, record the negative evidence and adopt the minimum explicit alternative.

No generated PowerShell is allowed for the normal runner invocation.

## DOD-02 — Machine contracts are JSON-first

The following operational carriers must be JSON:
- ExecutionProfile
- ExecutionRequest
- ExecutionContextManifest
- ExecutionResult
- ExecutionReceipt
- ExecutionObservation/metrics where materialized

Keep/update JSON Schemas.
Provide TypeScript types and runtime validation that reject malformed requests before profile execution.

YAML is allowed only for provider configuration such as GitHub Actions.
Markdown remains for human documentation.

## DOD-03 — Small TypeScript runner

Implement a bounded CLI with the smallest useful surface, preferably:

```text
ts-exec run <request.json> [--out <dir>]
ts-exec validate <request.json>
ts-exec profiles
```

`run` MUST validate internally; external `validate` is diagnostic only.

A normal successful run must emit:
- `result.json`
- `receipt.json`

A deterministic rejected request should emit a structured failure receipt when enough identity is available.

Do not implement generic command execution.

## DOD-04 — Known profile registry

Implement/port at least:

1. `canonical-sha256/v0`
   - pure bounded JSON profile
   - preserve semantic equivalence with v0.1

2. `git-exact-subject/v0`
   - bounded Git identity profile
   - input names a repository working directory and expected/ref subject
   - output includes exact commit/tree correspondence
   - invokes only predetermined git operations
   - no arbitrary git argument array supplied by the request

Profiles are code-owned registrations, not shell strings transported in JSON.

## DOD-05 — Local steady-state path reduction

For an already-materialized valid request, prove:

```text
Commander
  -> one bounded Node runner invocation
  -> immediate structured result/receipt
```

Requirements:
- no generated .ps1
- no generated .cmd
- no separate parser process
- no OpenCode
- no Orca requirement for the execution itself
- request schema validation occurs inside the runner

Compare against v0.1 materialize-script -> parse -> execute path.

## DOD-06 — Remote steady-state path uses SAME runner

Create/adapt a minimal GitHub Actions adapter that runs the exact same TypeScript runner/profile code on Ubuntu.

Provider YAML may:
- checkout;
- setup Node;
- materialize/acquire a bounded JSON request;
- call the runner;
- upload result/receipt.

It may not duplicate profile semantics in YAML/bash.

Prove local and remote semantic correspondence for the same exact request.

## DOD-07 — Private Product reusable workflow topology

Improve the previously proven private Product topology.

Prefer a reusable public workflow in `ts-execution-lab` that a private synthetic Product repo can call by exact lab commit/ref.

Target:
- private caller retains private checkout;
- public lab supplies generic runner/workflow mechanics;
- no PAT, GitHub App, or extra secret;
- Product-specific request stays in the private repo or caller-controlled input;
- result/receipt correlate to caller exact subject and ExecutionAttempt.

If GitHub reusable-workflow semantics prevent this exact shape, record the qualified negative and keep the previously proven Product-owned workflow + public lab checkout pattern.

Do not force success with new credentials.

## DOD-08 — Context/transport compatibility

Runner must consume request/context identities without becoming a context packager.

Preserve:
- REF_ONLY
- INLINE_SMALL
- FROZEN_BUNDLE

Preserve namespace:
`Product_ref / Product_operation_ref / ExecutionAttempt_ref`

Prove two synthetic Products can invoke the same runner without shared mutable state or context crossing.

## DOD-09 — Fallback semantics preserved

Prove at least one runner-based fallback:
- same logical Product operation;
- same exact request/profile identity;
- attempt A binding failure with EFFECT_NONE;
- attempt B NEW ExecutionAttempt on the other qualified binding;
- successful corresponding semantic result.

EFFECT_UNKNOWN must remain fallback-blocking.

Do not implement automatic fallback policy in the CLI.

## DOD-10 — Feedback instrumentation without telemetry backend

Every run receipt or adjacent observation must retain, where available:

```json
{
  "binding": "...",
  "profile": "...",
  "result_class": "...",
  "effect_state": "...",
  "timings": {
    "validation_ms": 0,
    "profile_ms": 0,
    "total_ms": 0
  },
  "subprocess_count": 0
}
```

Experiment-level evidence must additionally compare:
- orchestration/tool-call count;
- generated shell artifact count;
- parser process count;
- no-information observations;
- remote wait observations;
- permission/harness friction;
- Developer intervention/manual follow-up;
- elapsed time.

Do not create a dedicated telemetry store.
Do not infer Product state from feedback.

## DOD-11 — Wait strategy remains external but measurable

Do NOT put a generic polling loop into `ts-exec`.

ChatGPT/provider observation remains responsible for async wait.

For remote experiment runs record:
- estimated duration before observation;
- actual elapsed;
- observation timestamps or intervals;
- information gain;
- transition to DIAGNOSIS only when duration/progress becomes abnormal.

No fixed max poll count.
No Commander polling of remote Actions.
Commander state inspection is allowed only after an explicit local-worker DIAGNOSIS transition.

## DOD-12 — Quantified efficiency improvement

Produce a before/after table for at least:
- one local canonical run;
- one remote canonical run;
- one private Product run.

The v0.2 normal path must improve at least TWO of:
- generated shell artifacts;
- external process launches;
- ChatGPT/Commander execution calls;
- parser calls;
- repeated permission prompts;
- prompt bytes/instructions needed for steady-state execution.

A claimed improvement must be evidenced, not inferred.

If no meaningful improvement is achieved, disposition is FAIL_FOR_OPTIMIZATION even if functionality works.

## DOD-13 — Permission-friction adjudication

Record observed permission friction.

PASS does NOT require eliminating all permission prompts during development.

PASS requires:
- normal steady-state execution does not depend on OpenCode permission approval;
- no broad permission weakening was introduced;
- any remaining prompt is classified by binding/stage;
- repeated friction is left as feedback candidate unless it blocks the runner objective.

## DOD-14 — Terminal convergence

Write:
- `experiments/TS-EXECUTION-RUNNER-V0.2-001/RESULT.md`
- `experiments/TS-EXECUTION-RUNNER-V0.2-001/WORKER_RESULT.json`
- `experiments/TS-EXECUTION-RUNNER-V0.2-001/EFFICIENCY.json`

Terminal result must classify every DoD item PASS/FAIL/QUALIFIED_NEGATIVE.

No merge to main.
No Product adoption.
No TC Core or Upper LC mutation.

# Implementation guidance

Prefer:
- Node built-ins
- TypeScript source
- Node built-in test runner
- deterministic JSON serialization where identity/hash matters
- one profile registry
- one request validation path
- one receipt/result path shared by local and Actions

Avoid:
- frameworks
- generic DI containers
- queue systems
- databases
- arbitrary subprocess descriptions in requests
- general-purpose plugin systems
- new lifecycle state machines
- secrets

# Candidate and validation

Use exact Git identities and non-force push.

Before terminal result:
- run focused/unit tests;
- run the same runner on Windows and GitHub Ubuntu;
- prove exact local/remote semantic result correspondence;
- reobserve public/private repo visibility and default branch;
- leave `main` untouched.

OpenCode may implement this bounded experiment in the isolated worktree. It does not semantically approve its own result.
