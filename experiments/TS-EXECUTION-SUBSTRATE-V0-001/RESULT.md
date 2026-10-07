# TS-EXECUTION-SUBSTRATE-V0-001 — Terminal Result

authority: NONE
Product_effect: NONE
branch: devlab/execution-substrate-v0-001

## Commander/local capabilities proven
- Local canonical-sha256/v0 execution corresponds exactly to remote (DOD-04): sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728.
- Local preflight failure with EFFECT_NONE (DOD-09 attempt A) recorded; parser/launcher maturity evidence (DOD-05) materialized script → separate parse → execute.

## GitHub Actions capabilities proven
- Remote deterministic execution of canonical-sha256/v0 with structured receipts (DOD-03/04), public smoke run 37621354100, CANON-SHA256-REMOTE-0001 run 37655975430, transport slot runs 37661477555 + 37661622747, DOD-08A run 37663582852, DOD-09B run 37664046391, DOD-08B run 37663798724 (expected failure).

## Overlapping capabilities proven
- Same profile + same bounded input → same semantic digest on local and remote; distinct provider/native receipts.

## Fallback-qualified profiles
- canonical-sha256/v0: attempt A (local-commander) EFFECT_NONE preflight failure; attempt B (NEW ExecutionAttempt, github-actions) succeeded and corresponded — digest sha256:32b76998... matches local. EFFECT_UNKNOWN documented as fallback-blocking.

## Context transport findings
- REF_ONLY / INLINE_SMALL / FROZEN_BUNDLE classes demonstrated (DOD-07): REF_ONLY via direct source resolution, INLINE_SMALL for bounded metadata, FROZEN_BUNDLE only for the bounded unavailable fixture; materialization required only where stated, byte sizes recorded in evidence/dod07-context-transport.json.

## Concurrency findings
- Two independent concurrent transport slots on PRIVATE mauedgar/ts-execution-transport branches: transport/product-alpha/op-001/attempt-001 (run 37661477555, 18s, digest sha256:9fa4f08...) and transport/product-beta/op-002/attempt-001 (run 37661622747, 16s, digest sha256:6b7f3bd...); each slot independently retrievable, no shared mutable current/RESULT.yaml.

## Public/private topology findings
- topology A proven: private mauedgar/ts-execution-private-consumer workflow checked itself out privately and consumed the exact public lab runner/profile logic (run 37663582852, success, digest sha256:9da28dc8...).
- topology B QUALIFIED_NEGATIVE: public lab runner could not check out the private consumer with default GITHUB_TOKEN only (run 37663798724, "Repository not found", exit 128). No PAT/App/secrets added. Topology A is simpler and safer.

## Wait findings
- Runs: 37655572280 (13s), 37655975430 (17s), 37661477555 (18s), 37661622747 (16s), 37663582852 (20s), 37663798724 (46s, expected checkout failure), 37664046391 (11s). Queue_time not separately exposed; estimated 60s before observation; ChatGPT used adaptive remote observation on the GitHub Actions API with no Commander polling for remote-run observation and no fixed max-poll count. Commander terminal state was consulted only after explicit transition to local worker DIAGNOSIS. Transitions: RUNNING_EXPECTED → TERMINAL in the recorded remote runs.

## Parser findings
- Parser failure (evidence/parser-failure-demo.json) and successful materialize→parse→execute (evidence/parser-launch-worker.json) recorded; parser and execution failures recorded separately.

## Unresolved blockers
- Central public runner cannot consume private sources with default token (structural; topology A is the supported path).
- GitHub write surface had intermittent guards earlier; no blind retries used.

## Candidate routing defaults for multiple Products
- Remote deterministic receipt-producing execution for bounded known profiles (canonical-sha256/v0 qualified).
- Private Products use topology A: Product-owned workflow consuming public lab runner/profile.
- Fallback only after EFFECT_NONE preflight/binding failure; EFFECT_UNKNOWN blocks fallback pending reconciliation.
- No arbitrary command strings; no generic orchestrator; no fixed poll budgets.

Result: all mandatory DoD satisfied; DOD-08B adjudicated QUALIFIED_NEGATIVE as permitted.
