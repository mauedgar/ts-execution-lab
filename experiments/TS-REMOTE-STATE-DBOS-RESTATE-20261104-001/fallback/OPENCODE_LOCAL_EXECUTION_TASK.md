# OpenCode v2 delegated mechanical local qualification — NONPRODUCT

**Profile:** Execution Engineering local synthetic R1 fallback only. This task is **not** permission to write to or dispatch GitHub Actions, modify Product, clone/repair a private repository, bypass safety restrictions, create a new TaskCycle, extend lifecycle, or retry prior effects. Keep the tool/provider and model independent of the fixed candidate. Do not invoke OpenCode 1.

## Immutable inputs to verify independently before one execution

- Current exact lab checkout commit: must match the user-provided candidate `<EXACT_LAB_SHA>` and contain `experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r1_differential.cjs` with Git blob `617e9bd067bb44d43eede95ec079d019a63533b5`.
- Exact Product reference checkout: `mauedgar/tecnotron-ai@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`, tree `25d1a151d651bb41936c69334fb0b0772ef22519`; **read-only canonical source**.
- Real WSL/Ubuntu paths: `<LAB_PATH>`, `<PRODUCT_PATH>`; validated by external authorized control, not Commander semantic discovery.
- Pre-materialized runner: `<LAB_PATH>/experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/fallback/r1-docker-once.sh`.
- Unique new attempt ID `<ATTEMPT_ID>` and `<RESULT_ROOT>` selected before execution and proven never used. Confirm notebook host, Docker Linux container availability, network, Git and Bash. No real secrets, no live data.

## Single bounded action

After all prerequisites PASS, execute **once**:

```bash
bash "<LAB_PATH>/experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/fallback/r1-docker-once.sh" "<LAB_PATH>" "<PRODUCT_PATH>" "<EXACT_LAB_SHA>" "<RESULT_ROOT>" "<ATTEMPT_ID>"
```

This local operation creates disposable copies, ephemeral PostgreSQL16 and Node22 Docker containers and a single terminal local result. It neither publishes nor dispatches a GitHub workflow. Do not start another run if execution becomes UNKNOWN; recover only its actual result and reconcile.

## Required compact return

Provide the exact subject, tree, R1 blob, original Product reference, attempt ID, host/runtime/image digests, exit code, `terminal.txt` path, original Kernel pass count, and occurrence of `PASS|R1|bootstrap_forgery`, `PASS|R1|mutation_collision`, and `PASS|R1|concurrent_same_key`. Return classification `PASS_LOCAL_R1`, `BLOCKED_PRECONDITION`, `FAILED_LOCAL_R1`, or `UNKNOWN`, with evidence and no speculation. A PASS is a **local synthetic qualification**, not independent IR002, CI success, Product acceptance or Kernel retirement.

Do not claim anything about R2 Windows/DBOS beyond already frozen previous workflow `41877732907` (two successful jobs on an older SHA). Never rerun old workflow attempt 1. Do not interpret source or patch code while executing this delegated mechanical request; semantic review belongs to an independent WEB_INLINE reviewer after terminal evidence.
