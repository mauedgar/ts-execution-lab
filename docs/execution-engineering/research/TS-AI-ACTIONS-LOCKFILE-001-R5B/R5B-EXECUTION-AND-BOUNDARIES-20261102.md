# TS-AI-ACTIONS-LOCKFILE-001 — R5B evidence and research disposition (2026-11-02)

**Current status:** `R5B_EXECUTION_PASS / IR003_PENDING / NO_GO_PRODUCT_ROLLOUT`.

## Attempts
- R5 original: isolated runner stopped at T01 on Windows, SHA mismatch for YAML snapshot fixture due to CRLF actual bytes vs LF string hash. Receipt SHA-256 `b55f337f0476d4fe8a3fdf0970d36120bc07047d5972e44a043e60c7a916d43d`, 1,526 bytes. No subsequent gate executed. No retry.
- R5B: new identity, fresh run root, checksum computed from **actual** snapshot bytes; adds CRLF regression. Runner terminal exit 0, no Product dispatch/push.
- ZIP original 11,056 bytes, SHA-256 `b5864876299cf736e9c9b85e93fddcdc7523dd61242ec5a396499f1007e61ce7`. Recoverable directly from GitHub **binary** `docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R5B/TS-AI-ACTIONS-LOCKFILE-001-R5B-CANDIDATE.zip`, commit `49621bb543bc440f8e9fab0e472e6f72075a04b1`. Git blob `f7ac9056c34ac28026eea3dd2c3e00a0e635abcf`.
- Runner SHA-256 `43e162274b6bf4fa3578602f954eca1384a6e7e673c6dd0ec4f434814ff96f4e`. All `MANIFEST.json` file SHA-256 values verified against ZIP bytes.
- Original terminal receipt SHA-256 `7bff16f88abd95a08d73d5945dd45fa8f3cc4687dba84918961813c182a06976`, 2,738 bytes; original OneDrive educational source and text-normalized GitHub mirror exist.

## Validated R5B scope
1. Python 3.12.15 / `ruamel.yaml==0.18.17`, 38 unit tests in Windows via uv, exit 0, stderr assertion `Ran 38 tests`.
2. Static companion policy PASS on one synthetic baseline, CLI `gh-actions-lock v0.4.0 --verify-local` exit 0 and CLI `--verify` exit 0. These tests are separate **coverage** vs **online provenance** modes.
3. Baseline YAML and lockfile post-state hashes identical to package fixtures.
4. Cases cover immutable job-level workflow references, digest pinning of containers, services and `docker://`, missing/tampered nested snapshot catalogs, composites, unsafe paths, duplicate YAML keys, cycles, expressions/matrix, CRLF bytes. The *synthetic* tests do not demonstrate CI enforcement or production adoption.

## Important open limitations
- Scanner only analyzes explicitly supplied `--workflow` entries, not an independently enumerated complete workflow repository inventory; incomplete inputs can bypass its checks.
- Snapshot catalog hashes prove local file byte integrity, **not that external source bytes correspond to the specified GitHub repo/path/commit**. Require trusted immutable provenance evidence and transitive closure verification.
- External step actions still require `gh-actions-lock --verify`; the companion does not replace that independent gate.
- Some valid local action forms (`action.yaml`, Docker/Node local actions) are fail-closed unsupported; shell commands and nested install scripts are outside static scanner's guarantee.
- R5B runner test key still names `T01_python_policy_37_tests`, although actual assertion checks 38 tests; label is stale. Future candidate should fix without editing frozen R5B.
- The CLI's user-local logs and dependency tool caches are not fully isolated or independently audited; record real effects before making strict zero-side-effect claims.
- No Product repo workflows, CI integrations, model calls or deployments changed or accepted.
- The original IR002 (4 findings, 8 advisories) is not automatically closed by R5B PASS; an independent IR003 review was requested.

## Current decision
`GO_RESTRICTED_FOR_RESEARCH_ONLY`. Mandatory `NO_GO_PRODUCT_ROLLOUT` until compensating policy coverage and immutable remote-snapshot provenance are independently qualified, integration tests pass and a separate Product grant exists. No R5/R5B replay; preserve both original receipts and artifacts.
