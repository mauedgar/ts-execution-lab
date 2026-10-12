# TS Execution Engineering — native-result Git Transport sidecar (experimental)

Status: `QUALIFIED_OFFLINE_WITH_LIMITATIONS`. Authority: `NONE_PRODUCT`.

## Why this is reuse, not a new execution platform

The 2026-10-05 FitFlow precedent at `mauedgar/devBrain`, `transport-temp@dc9532c63ecb2b1fc5d4b394a8544811cca639b9`, `transport/exchange/fitflow/FITFLOW-M5-A1-TERMINAL-PHASE1-VALIDATION-002/` already delivered `manifest.json`, `RESULT.md`, logs and hashes over Git, including a terminal validation with mixed PASS/FAIL results. Its 002 package identifies actual Attempt `A1-TERMINAL-PHASE1-VALIDATION-20261004-004` and reports `251752 ms`; its earlier 001 manifest records a false-positive argv propagation defect and is not a validity claim. This precedent does **not** by itself attest current host credentials, independent Product adoption or that every byte was automatically published by a generic provider.

The 2026-10-11 `TS_EVIDENCE_PUBLICATION_DISCOVERY_PILOT_001` proved native GitHub Actions publication of `result.json` and `receipt.json`, followed by exact Web readback/ACK. PR43 `GITHUB_RESULT_PUBLICATION_BOUNDARY.md` (`ts-execution-transport@69283b7d0e6d3e91c1a363d9b29a96ce231894ba`) independently identifies the remaining Commander/WSL side: Web had transcribed/published terminal output, not the native process.

This **sidecar** consumes `result.json`/`receipt.json` from the *existing* `ts-execution-result/v0.2` and `ts-execution-receipt/v0.2` generator (`src/cli.ts` in `ts-execution-lab`), plus an explicit optional artifact list. It does **not** execute arbitrary Product work, select Tasks, watch a process, schedule, review code or infer an effect from publication.

## Reusable deterministic operation

1. Prior control freezes operation, `ExecutionAttempt`, subject, output paths, publication destination, expected remote HEAD and allowed artifact names. The runner is already determined/materialized.
2. Existing native execution writes `result.json` and `receipt.json` for PASS/FAIL/BLOCKED; the nonblocking launcher invokes the sidecar **after** the runner becomes terminal, including when its exit code is nonzero. Do not use `&&` to skip publication on FAIL.
3. Sidecar reads the native envelopes, enforces cross-file identity, rejects source/destination symlinks and traversal, checks package size, clean dedicated transport checkout, `branch`, exact local HEAD, exact origin URL and exact remote HEAD **before** any write.
4. Sidecar writes only the exact `results/.../<ExecutionAttempt>/` package, computes SHA-256 and sizes, stages only that directory, creates one commit and pushes non-forced. It then checks the branch's native remote SHA and emits compact `PUBLISHED_VERIFIED` with commit, parent, package path, attempt and manifest SHA.
5. `git push`/readback ambiguity is `PUBLICATION_UNKNOWN`, returning exact *local* commit, parent, branch and path. It does not retry or clean up. ChatGPT Web reconciles the attempt by exact GitHub ref under DEC. A local-only publication failure must not be represented as a successful delivery.

**No auto-replay**: a blocked precondition, collision, ambiguous push, or remote competing writer requires reconciliation. Caller must not start another ExecutionAttempt merely to retrieve a missing result.

## Invocation (publisher only; already-completed output)

```sh
node scripts/publish-native-transport.mjs publication-request.json
```

`publication-request.json` is an already-determined per-attempt configuration outside the Product workspace, for example:

```json
{
  "contract": "ts-ee-native-transport-publication/v0-experimental",
  "transport_checkout": "/dedicated/clean/checkout/ts-execution-transport",
  "result_dir": "/separate/native/attempt/output",
  "expected_head": "<40-character-pinned-remote-HEAD>",
  "expected_remote_url": "git@github.com:mauedgar/ts-execution-transport.git",
  "branch": "<qualified-dedicated-publication-branch>",
  "package_path": "results/<bounded-operation>/<exact-ExecutionAttempt-ref>",
  "artifacts": ["logs/output.log"],
  "max_package_bytes": 20971520
}
```

The actual request **must** use real exact values, not this placeholder. For production integration, the destination branch and auth must be allowed explicitly by Execution Engineering's qualified writer binding, and the output must be independently read back from GitHub. `GIT_TERMINAL_PROMPT=0` prevents credential prompts. The script embeds no credentials, never runs `git push --force`, and caps a package at 50 MiB (20 MiB default). Beyond the cap use already-qualified Actions artifacts / an authorized durable artifact store, plus hash and exact Git refs; do not silently stuff arbitrary binaries into Git.

## Tests and qualification

```sh
node --test test-publish-native-transport.mjs
```

`10/10 PASS` on Node 22.16.0 / Git 2.47.3 against disposable local bare Git remotes:

- Terminal PASS, FAIL and BLOCKED each publish the original result/receipt/extra log + deterministic manifest; collision on identical second submission fails closed.
- Stale local parent, changed remote, dirty checkout, unsafe relative path, identity mismatch and package limit all block.
- Deliberately rejected push is `PUBLICATION_UNKNOWN` with local commit preserved and no automatic retry.

**Still unqualified**: credentialed local Commander/WSL-to-GitHub publish (exact host, allowlist, auth scope, remote permission), host-native PowerShell launcher consumption, binary/very large files beyond cap, meaningful end-to-end Product TaskCycle use, concurrency under multiple writers, crash recovery beyond fail-closed return. These must not be inferred from the offline tests or old FitFlow precedent. Preserve prior terminal experiments and every Product `UNKNOWN`.

No schema replacement, new scheduler, Product policy, TaskCycle gate, Primitive, Recipe, plugin, adoption or Product effect.
