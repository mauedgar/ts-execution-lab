# TS Execution Engineering — bounded execution fallbacks for R1/R2

**Classification:** NONPRODUCT, local experimental execution only. No Product authority, TaskCycle, Phase 2, canonical Kernel cutover, R3 provider or historic replay. Never use a fallback to publish the GitHub Actions workflow whose publication was denied. This file is an execution plan and an already-materialized *local test runner*, not evidence that the local fallback ran.

## Known identities and current provider state

- Baseline Product Oracle `mauedgar/tecnotron-ai@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`, tree `25d1a151d651bb41936c69334fb0b0772ef22519`.
- Previous R1/R2 candidate `d14c6e08ace37bff9f3fffc8a7c66209e6a0e08b`, GitHub Actions run `41877732907`, attempt 1, **terminal failure** at R1 negative-test fixture `EACCES`; R2 Linux/DBOS and Windows **terminal PASS** for that old candidate only.
- New isolated repair was committed `41c06133ca8e6684d8353d2b72264556bbf24299`, tree `b5e866a6f493cb4b9b51546937dc96b211a15240`. The current branch may have further documentation/runner commits. For any execution, freeze **the actual checked-out final lab commit** as `<LAB_SHA>`. Do not substitute a mutable branch for a subject.
- R1 script blob `617e9bd067bb44d43eede95ec079d019a63533b5`; Product `store.js` blob `f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a`.
- Original IR001 `NO_RECOMMEND 3 F/4 A`; IR002 not run and previous request is bound to a superseded exact subject.
- GitHub workflow creation attempt: **tool safety denial**, not an observed GitHub API `403` or temporary throttling. No retry/alternate publication without resolving the policy/permission boundary. GitHub workflows generally require explicit appropriate token permissions, and `workflow_dispatch` must be defined on the default branch.

## Fallback priority / readiness

| Surface | Allowed use | Prerequisite | Current disposition |
| --- | --- | --- | --- |
| Original GitHub Actions | Read-only evidence join of existing exact run IDs | Provider run already exists | Original `41877732907` finished FAIL; **NO RERUN** |
| **WSL Ubuntu + Docker Desktop** | Bounded synthetic **R1** test under Linux Node 22 and PostgreSQL 16 | Local checked-out repos at exact SHAs, Bash, Git, tar, Docker Linux daemon, registry/npm network, unique attempt ID | Runner materialized in this repository; **host preflight and full R1 unverified** |
| OpenCode v2 | Dedicated implementation/semantic analysis, or explicitly approved **local** execution of same pre-materialized test runner | Model/provider, WSL checkout, same exact identity and unique ExecutionAttempt, scoped permissions; no Product writes | Defined task contract; no OpenCode execution observed |
| Commander | **Execution/result surface** only: run an **already materialized**, prevalidated bounded invocation or read its result | Device identity and path, runner already resident, exact SHA and preconditions confirmed outside Commander | Two devices reported online but ownership/path/capabilities not established; **do not launch by discovery** |
| Existing `ts-exec-runner.yml` GitHub workflow | Execute its already-defined bounded `ExecutionRequest` contract | Inputs and Product authority, workflow `workflow_dispatch` permission | **NOT an R1 fallback**: existing job lacks PostgreSQL service and frozen R1 test setup |
| Human GitHub administration | Resolve root cause of workflow-file publication policy/permissions | Authorized GitHub repository administration and provider policy | Independent of local validation; no tool-based workaround of denied publication |

## Prepared reproducible local R1 runner

Source: [`r1-docker-once.sh`](r1-docker-once.sh). It is designed for WSL2 Ubuntu or native Linux, **not PowerShell source text**, and uses Docker Desktop with WSL integration. It accepts existing checked-out directories and an exact SHA; no source changes to Product. It reserves an attempt ID before any side effect, creates only temporary Git archive copies, verifies frozen Product SHA/tree and the repaired R1 blob, starts an isolated PostgreSQL container, installs locks in disposable Node 22 Linux container, runs the original Product Kernel tests and PostgreSQL differential tests, checks the exact F001/F002/F003 regression markers and writes one terminal receipt and log. It removes temporary containers/work files. Source and secrets are not sent to external GitHub.

This command is only an example to execute **after** the user's real checkout paths, commit identity, environment and request ID have been verified. Run once; do not blindly re-run an attempt:

```bash
bash /path/to/lab/experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/fallback/r1-docker-once.sh \
  /path/to/lab \
  /path/to/tecnotron-ai \
  <EXACT_LAB_SHA> \
  /home/<user>/ts-remote-results \
  TS_REMOTE_R1_LOCAL_001
```

The runner does **not** clone repos, checkout other branches, edit Product, publish workflows, modify tokens, write external DBs or use real data. It does **not** install Python 3.15.2 or qualify DBOS/Windows R2 anew. The existing R2 job PASS is evidence solely for unchanged exact R2 blobs, and must be revalidated if R2 changes. The Docker image tags resolve to runtime digests recorded in the receipt; they are not immutable image pins at authoring time.

A successful local terminal is `PASS|R1_LOCAL_DOCKER`, **not** GitHub CI PASS, independent IR PASS, or Product adoption. A failure produces one `FAIL_OR_BLOCKED` receipt at the unique attempt directory. Reconcile before any new attempt or change of binding; avoid retrying an unknown effect.

## OpenCode delegated task and Commander boundary

If a connected OpenCode instance and scope are explicitly established, use [`OPENCODE_LOCAL_EXECUTION_TASK.md`](OPENCODE_LOCAL_EXECUTION_TASK.md) for the *local test only*. OpenCode does not mint Developer authority and cannot override an OpenAI/GitHub workflow publication refusal. It must return compact logs and exact subject/attempt IDs. If the local runner and all inputs are already present, Commander may invoke one **short mechanical command** chosen outside Commander; it must not explore, construct scripts, perform Git semantic reads or open a new editing session.

## After evidence

1. If R1 local PASS, verify the returned original kernel test count and F001/F002/F003 markers against the log; verify committed blob identities and R2 evidence separately. Publish a **new distinct local-validation receipt** in Transport only after the actual execution and receipt exist. Do not mislabel it as Actions CI.
2. Obtain competent determination whether this local evidence is sufficient for **experimental** IR002 or whether exact candidate GitHub CI is required. If approved, freeze subject and create a **new independent IR002 request** that matches it; never recycle the superseded `d14c6e08...` IR002 request.
3. If blocked, preserve `PENDING_EXTERNAL_RESULT` or exact `BLOCKED_PRECONDITION` without Product change. If failed, prepare a new candidate under a separate identity only with actual terminal reason.

No R3 remote provider, secrets, historical records, or original Git CAS sibling B effects are touched.
