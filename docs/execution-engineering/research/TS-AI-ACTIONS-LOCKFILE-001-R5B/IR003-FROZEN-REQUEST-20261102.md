# IR003 — TS-AI-ACTIONS-LOCKFILE-001 R5B (frozen independent review)

```yaml
review_id: IR-TS-ACTIONS-LOCKFILE-001-IR003
status: REQUESTED_READ_ONLY
candidate: TS-AI-ACTIONS-LOCKFILE-001-R5B
scope: ISOLATED_EXECUTION_ENGINEERING_RESEARCH
product_authority: NONE
ir_acceptance: NOT_GRANTED
```

## Immutable candidate and previous attempts
- **R5B** is the new candidate; **R5** is an independent terminal failure, **not retried**. R1–R4 preserved.
- ZIP **exact binary GitHub**: `mauedgar/ts-execution-lab@49621bb543bc440f8e9fab0e472e6f72075a04b1:docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R5B/TS-AI-ACTIONS-LOCKFILE-001-R5B-CANDIDATE.zip`, size **11,056 bytes**, SHA-256 `b5864876299cf736e9c9b85e93fddcdc7523dd61242ec5a396499f1007e61ce7`, Git blob `f7ac9056c34ac28026eea3dd2c3e00a0e635abcf`.
- Independent restricted carrier copy: educational SharePoint `TS-TRANSPORT-BRIDGE-001/TS-AI-ACTIONS-LOCKFILE-001-R5B-CANDIDATE.zip`. Read only; no need for Commander or execution.
- Inside ZIP: `policy.py` SHA `86b348b41c01929c6172704221b6f0f576d2f530e5480079481611e21b5a8505`; `test_policy.py` SHA `7efb20a2f17e36c4c0c3a33b387202231867721b4602f611c44076519cbb0c2c`; `runner.ps1` SHA `43e162274b6bf4fa3578602f954eca1384a6e7e673c6dd0ec4f434814ff96f4e`; `fixture/.github/workflows/baseline.yml` SHA `377f7e61d06600b57d054acaea0bd6f5f2231d9200401c056dc08418691abd99`; `fixture/.github/workflows/actions.lock` SHA `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`.
- `MANIFEST.json` file hashes must match all included payloads. Exact file bytes, not merely extracted text, are authoritative.
- **R5 terminal receipt:** Git `mauedgar/ts-execution-lab@9e87031b0dad28367e014d734b9bc048e444e6a2:docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R5B/TS-AI-ACTIONS-LOCKFILE-001-R5-TERMINAL.json`; original OneDrive JSON **1,526 bytes**, SHA-256 `b55f337f0476d4fe8a3fdf0970d36120bc07047d5972e44a043e60c7a916d43d`. R5 terminal due cross-platform CRLF snapshot fixture checksum mismatch, no subsequent checks performed.
- **R5B terminal receipt:** Git `mauedgar/ts-execution-lab@d2207c7078836b681ac5fecfc9e6c379c8a990ef:docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R5B/TS-AI-ACTIONS-LOCKFILE-001-R5B-RECEIPT.json`; original OneDrive JSON **2,738 bytes**, SHA-256 `7bff16f88abd95a08d73d5945dd45fa8f3cc4687dba84918961813c182a06976`. Git JSON may normalize line endings; verify bytes from OneDrive if asserting this exact raw hash.
- CLI actual tool `github/gh-actions-lock v0.4.0`, Windows amd64 official SHA-256 `a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`. Runner preflight hashed installed executable. Reviewer does **not** have independent executable bytes and must not claim otherwise.
- Runtime `uv 0.13.1` with isolated Python **3.12.15**, `ruamel.yaml==0.18.17` dependency. Runner is an already-materialized PowerShell -File, no `-Command` nesting; Commander was only mechanical execution/result surface.

## Observed bounded R5B execution
- Notebook process `11612`, terminal **exit 0**.
- 38 Python unit tests via `uv run`: exit 0, expected stderr `Ran 38 tests`. **T01 ID mistakenly remains `...37_tests`**: do not mistake label for count.
- Policy scan of isolated `.github/workflows/baseline.yml`: exit 0, `status=PASS`.
- Official `gh-actions-lock --verify-local`: exit 0, coverage.
- Official `gh-actions-lock --verify`: exit 0, online provenance for this single synthetic baseline.
- Original YAML final SHA equals `377f7e61d06600b57d054acaea0bd6f5f2231d9200401c056dc08418691abd99`; lockfile SHA equals `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`.
- No Product writes, pushes or Actions dispatch in the runner contract. A receipt's hard-coded no-Product claims are not independent telemetry.

## What R5 policy claims / important limitations
The companion Python YAML scanner rejects unpinned external job-level reusable `jobs.<id>.uses`, unpinned `container`/`services`/`docker://`, unresolved expressions, untrusted local paths, and missing/tampered external workflow snapshots; recursively scans local reusable workflows and composite actions; uses strict `ruamel.yaml` safe YAML parsing with duplicate-key rejection. Synthetic tests include CRLF raw-byte regression and cyclic graph cases.

**Do NOT assume** the scanner is a complete supply chain gate:
- The `--workflow` input selects specific workflows; does it safely inventory **all** workflows in a repository, or can an omitted workflow bypass the policy?
- Its caller-supplied external snapshot catalog proves an exact local file's SHA-256, **not independently that these bytes came from GitHub repository/path at the pinned commit**. Require separate trusted provenance verification for transitive remote dependencies, including their edges and source immutability.
- External action `uses:` with mutable refs is delegated to a **separate** gh-actions-lock `--verify` stage. Does that stage cover every local/composite/external action and every file in a real repo?
- Inspect exact YAML 1.2 parsing and semantics: duplicate keys, aliases/merge, jobs mapping, exotic `uses` forms, symlinks and traversal, local `action.yaml` alternative, Docker-based local actions, runs with shell Docker invocations, service expressions/matrix and custom build commands. Fail closed; mark legitimate unsupported patterns as limitations.
- Check scanner graph recursion/cycles, stale catalogs, max size/depth, symlink components, unexpected YAML types, dynamic expressions, Unicode decoding and deliberately confusing image tags/digests.
- Validate runner tests actual invariants in same bounded process: file hash/manifest preconditions, zero unapproved effects, postconditions, no auto-retries or silent bypass. Identify any mismatch between runner output labels and actual test count.
- `--verify-local` is offline coverage only. `--verify` is online provenance for **supported action refs** only; R4 proved external reusable `@main` and unpinned `node:22` can still pass.
- The actual 38 tests PASS **synthetically**; no Product repository security policy was applied or enforced by CI.

## Original IR002 linkage / required independent disposition
Review original `/Independent-Reviews/IR-TS-ACTIONS-LOCKFILE-001-IR002-20261102.json` in Library (25,829 bytes, original SHA `811d36fdc5308dfb...`) to reconcile 4 findings F001–F004 and 8 advisories A001–A008 individually. R5B's compensating code may address F001/F002 conceptually but the upstream limitation remains. Do **not** claim all closed if full repo traversal/provenance or CI integration remains incomplete. Assess any new findings with severity, exact file:line witnesses and actionable next repair gate.

Produce **one original** `IR-TS-ACTIONS-LOCKFILE-001-IR003` verdict **PASS/PASS_WITH_LIMITATIONS/FAIL/BLOCKED** with candidate hashes, verified tests, F/A dispositions, new findings/advisories, decision boundary, and suggested next gate. Save original receipt in Library if available. Strict **READ_ONLY**, no Commander, no CLI execution, no package modifications, no Git writes, no Product, no acceptance or deployment. If exact bytes unavailable, report limitation instead of inventing verification.
