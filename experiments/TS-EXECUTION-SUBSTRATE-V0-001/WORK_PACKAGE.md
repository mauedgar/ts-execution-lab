# TS Execution Surface Engineering — Experiment 001

## Status and authority

```yaml
experiment_id: TS-EXECUTION-SUBSTRATE-V0-001
authority: NONE
Product_authority: NONE
Product_effect: NONE
Product_repository_effect: NONE
implementation_authorized: true
experimental_repository_effect: AUTHORIZED
```

This work is limited to the execution laboratory and dedicated synthetic/transport repositories.
Do NOT modify Tecnotron, FitFlow, Attendance, Proof/Order Evidence, devBrain, or any Product repository.

## Responsibility

`QUALIFY_MULTI_PRODUCT_LOCAL_REMOTE_EXECUTION_CONTEXT_TRANSPORT_WAIT_AND_FALLBACK_V0`

The goal is empirical qualification, not a generic orchestrator and not a new lifecycle.

## Existing exact baseline

Repository: `mauedgar/ts-execution-lab`

Baseline main:
`0ad95a9891030efb3a73ff7194f3c499b1b45f4c`

Existing successful remote smoke:
- operation_id: `BOOTSTRAP-SMOKE-001`
- run_id: `37621354100`
- dispatched subject: `dc1a5f59799908e71773e38703bb0d3443e00547`
- conclusion: success
- receipt artifact id: `11482032449`
- artifact digest: `sha256:334f0158012cb3717809aec9fb46d39f124370bbfadd75aa798970e5559e2b63`

Work on branch:
`devlab/execution-substrate-v0-001`

## Governing boundaries

- ChatGPT Web owns semantic determination, wait/observation and result adjudication.
- Commander is a bounded local execution surface, not a semantic repository reader.
- GitHub Actions is a remote deterministic execution binding.
- GitHub repositories/artifacts/refs are durable transport/result surfaces.
- Product semantics remain Product-local.
- Execution lab creates no Product authority.
- No arbitrary remote shell command input.
- No generic AgentRuntime/orchestrator.
- No new lifecycle/state machine.
- No hidden dependency on chat transcript.
- Context is manifest/ref first; bytes only when a concrete binding needs them.
- Same Product operation may have multiple ExecutionAttempts.
- A fallback is always a NEW ExecutionAttempt.
- UNKNOWN/ambiguous prior effects forbid blind fallback/retry.

## Visibility decision under experiment

Make `mauedgar/ts-execution-lab` PUBLIC before further remote qualification.

Public means every byte in this repository must be safe to remain public permanently.
Do not put Product-private context, secrets, private source excerpts, tokens, credentials, or private transport payloads in it.

Create/reuse one PRIVATE repository:

`mauedgar/ts-execution-transport`

Its role is only transient/durable transport of immutable request/context/result carriers.
It is NOT Product SOT, lifecycle state, knowledge SOT or Product authority.

Do not create additional repositories unless a concrete DoD proof below cannot be performed without one.
If a synthetic Product-like source is needed, prefer harmless fixtures inside the public lab first.
A private synthetic fixture may be created only for the private-consumer topology proof.

## Definition of Done

The experiment is PASS only if all mandatory proofs are satisfied or explicitly adjudicated as a qualified negative result where stated.

### DOD-01 — Public remote substrate
- execution-lab visibility = PUBLIC
- bootstrap smoke behavior still works on `ubuntu-latest`
- exact run/head/receipt correlation is captured
- no sensitive/private payload was published

### DOD-02 — Portable execution contracts
Implement minimal JSON schemas and examples for:
- `ExecutionProfile/v0`
- `ExecutionRequest/v0`
- `ExecutionReceipt/v0` (adapt existing schema, do not fork semantics unnecessarily)
- `ExecutionContextManifest/v0`
- `TransportSlot/v0`

Required identity separation:
- Product_ref
- Product_operation_ref
- ExecutionAttempt_ref
- execution_profile_ref
- exact subject refs
- context_id
- request identity
- provider/native run identity
- result/receipt identity

The context manifest must support:
- baseline_refs
- delta_refs
- cutoff
- unknowns
- REF_ONLY
- INLINE_SMALL
- FROZEN_BUNDLE materialization classes

No full repo dump by default.

### DOD-03 — Known-profile runner, not arbitrary shell
Implement one intentionally small profile:
`canonical-sha256/v0`

Input: bounded UTF-8/JSON payload.
Output: canonical semantic digest plus structured receipt.

It must be runnable:
- locally with Node 22
- remotely on GitHub Actions Ubuntu/Node 22

No workflow input may accept an arbitrary command string.

### DOD-04 — Dual-binding equivalence
For the SAME exact profile and SAME exact input:
- local execution result is recorded
- remote Actions execution result is recorded
- semantic digest/result must correspond exactly
- provider/native receipts remain distinct

If results differ, STOP and report the mismatch. Do not redefine equivalence to pass.

### DOD-05 — Parser/execution maturity evidence
For nontrivial local PowerShell launch mechanics:
- materialize script first
- parse separately
- execute only after parser PASS
- record parser failure separately from execution failure

Do not merge parser+execution yet.
Record enough evidence to decide later when merging is safe.

### DOD-06 — Concurrent transport isolation
In `ts-execution-transport`, prove at least two independent concurrent transport slots representing two different synthetic Product refs.

Required namespace:
`<Product_ref>/<Product_operation_ref>/<ExecutionAttempt_ref>`

Each slot must have immutable request/context/result/receipt identity.
No shared mutable `current`, `RESULT.yaml`, or global request file.
No cross-slot overwrite.
Both results must be independently retrievable and correlated.

The transport repo remains PRIVATE.

### DOD-07 — Context transport strategy
Prove:
1. REF_ONLY context where the executor can resolve the source directly.
2. INLINE_SMALL for bounded metadata/delta.
3. FROZEN_BUNDLE only for a bounded unavailable source.

Record when materialization was actually required and its byte size.
Do not create a universal ContextPackager.

### DOD-08 — Private Product topology
Empirically compare:

A. Product-owned execution:
private synthetic consumer repo -> its own Actions workflow -> consumes public execution-lab contract/runner logic -> private checkout remains private.

B. Central public runner -> private synthetic source using only default `GITHUB_TOKEN`.

B is allowed to result in a QUALIFIED_NEGATIVE if default GitHub permissions do not allow safe cross-repo private checkout.
Do NOT add PATs, GitHub App credentials or repository secrets in this experiment merely to force B to pass.

Record which topology is simpler and safer for future private Products.

### DOD-09 — Fallback proof
Using `canonical-sha256/v0` only:
- represent one logical operation
- attempt A uses one binding and ends EFFECT_NONE with a deliberately induced binding-level/preflight failure
- attempt B uses the other already-qualified binding
- attempt B is a NEW ExecutionAttempt
- profile/input identity is preserved
- result is successful and corresponds

Also document that EFFECT_UNKNOWN would block fallback pending reconciliation.
Do not induce an ambiguous external effect merely for the test.

### DOD-10 — Wait/observation evidence
For remote runs record:
- estimated_duration_ms before observation
- queue/start time when available
- actual terminal elapsed
- observation timestamps
- whether each observation yielded information
- transition among RUNNING_EXPECTED / RUNNING_OVERTIME / SUSPECTED_STALL / DIAGNOSIS / TERMINAL where applicable

No fixed max-poll count.
Do not poll Commander.
Use GitHub/provider durable observation.

This experiment need not implement automatic learned p50/p90 routing yet; it must produce enough structured timing evidence for the next iteration.

### DOD-11 — Multi-Product readiness conclusion
Produce one terminal report:
`experiments/TS-EXECUTION-SUBSTRATE-V0-001/RESULT.md`

It must classify:
- Commander/local capabilities proven
- GitHub Actions capabilities proven
- overlapping capabilities proven
- fallback-qualified profiles
- context transport findings
- concurrency findings
- public/private topology findings
- wait findings
- parser findings
- unresolved blockers
- candidate routing defaults for multiple Products

The report is DevLab evidence only:
`authority: NONE`
`Product_effect: NONE`

## Execution method

You may use GitHub CLI/API, Node, PowerShell, and GitHub Actions.
Prefer Node built-ins.
Keep dependencies at zero unless a DoD proof truly requires one.

Use exact Git identities and non-force pushes.

For public/private repository visibility or repository creation:
- reconcile whether the effect already occurred before retrying
- no blind retries

For Actions:
- dispatch once per intended attempt
- resolve exact run_id/head_sha
- do not treat provider success alone as semantic success
- produce/read structured receipts

For concurrency tests:
- use independent refs/branches/slots
- never use a shared mutable branch as the slot identity

## Local worker result and publication

Commit experimental implementation/evidence to:
`devlab/execution-substrate-v0-001`

Push non-force.

Do NOT merge to main.

When the work reaches a coherent candidate or a blocker, write:
`experiments/TS-EXECUTION-SUBSTRATE-V0-001/WORKER_RESULT.yaml`

Return only a compact terminal summary containing:
- candidate commit/tree
- public/private repo effects performed
- remote run_ids
- mandatory DoD status
- blockers
- result artifact paths

Do not semantically approve your own result.
