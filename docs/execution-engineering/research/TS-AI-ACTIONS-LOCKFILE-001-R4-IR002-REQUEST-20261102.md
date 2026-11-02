# TS-AI-ACTIONS-LOCKFILE-001 R4 — Frozen IR002 independent review request

**Disposition before review:** `R4_COMPLETED_PENDING_IR002`. **No Product acceptance or workflow rollout.**

## Identity and authority
- Gate: `TS-AI-ACTIONS-LOCKFILE-001-R4`, fresh synthetic-only execution, no retries of R1/R2/R3.
- Authorized basis: user accepted R3 independent review recommendation to run the next bounded isolated gate.
- Repository: `mauedgar/ts-execution-lab`. Canonical Product repositories FitFlow and Tecnotron untouched.
- No release, push, Actions dispatch, ruleset/branch-protection change, model API request, or approval to integrate.
- Commander is a mechanical execution/results surface, **not** a semantic review surface.

## Frozen evidence
- Original R4 carrier: `TS-AI-ACTIONS-LOCKFILE-001-R4-CANDIDATE.zip`, educational OneDrive folder `TS-TRANSPORT-BRIDGE-001` on connected FRC UTN SharePoint; 4,404 bytes, SHA-256 `881a7fe844e84863eadaf7babe84322be4594221a5cfe627ee93f337b247443d`.
- Contained `runner.ps1` SHA-256 `5a4435d8c3fad6f07c4cf66613a22f18ac6b8b1e30ee1e20706f7f2ff1cc41f9`. `MANIFEST.json` and baseline fixture hashes in ZIP, verify against bytes.
- Official tool: `github/gh-actions-lock v0.4.0` Windows amd64, official SHA-256 `a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`.
- Local terminal process PID `5008`, **terminal exit 0**, 13 cases reported `semantic_pass=13`.
- Original R4 receipt stored in same restricted OneDrive folder: `ACTIONS-LOCKFILE-001-R4-RECEIPT.json`, **8,609 bytes**, SHA-256 `4c961ea7d5263211889137ff67ae5171e3c7829f1a56340092eb3d6898030951`. Independently re-fetched raw bytes in originating chat and recomputed hash. Normalized text mirror at `mauedgar/ts-execution-lab@5a47808d15d37ae92fa26f28e572c7bace0854f8:docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R4-ORIGINAL-RECEIPT-20261102.json`; **do not** mistake normalized Git text for identical raw byte stream.
- Generated `actions.lock` 438 bytes; terminal SHA-256 `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`, matching R1/R2/R3 (R4 original output file not yet independently re-fetched).
- Source of real public reusable workflow: `actions/reusable-workflows@d468c63c53c1184242904d1a3ac74fd1081f36c8:.github/workflows/basic-validation.yml`, Git blob `d2e5e0ce44e51e9dec1ac8584fc0756e851e0241`, with verified `on.workflow_call`. Mutable control `@main`.

## Observed real CLI cases (R4)
1. T01 initial missing lock: exit 1, explicitly `not-pinned`.
2. T02 generation: exit 0, normalized checkout v4→v4.4.0.
3. T03 baseline offline: exit 0, complete coverage.
4. T04 baseline online: exit 0, one workflow valid.
5. T05 **external reusable @main** added inside **already locked** YAML: `--verify-local` exit 0, full coverage.
6. T06 same @main: `--verify` exit 0, one workflow valid. **SECURITY GAP**: tool does not reject mutable external reusable ref.
7. T07 same external reusable job pinned full commit SHA: `--verify-local` exit 0. A compensating **independent** check must require SHA; CLI does not establish consumer policy.
8. T08 restore baseline: offline exit 0.
9. T09 add `container: node:22` to **already locked** baseline: `--no-fix` exit 0 and emitted `not pinned by digest` warning.
10. T10 same unpinned image: `--verify-local` exit 0, complete coverage.
11. T11 same unpinned image: **`--verify` exit 0** with explicit digest warning. **SECURITY GAP**: this warning does not enforce digest.
12. T12 restore baseline: offline exit 0.
13. T13 restore baseline: online exit 0.

These 13 assertions PASS because the runner correctly *observed and classified the tool behavior*, not because all dependencies are secure. The actual mode `--verify-local` checks coverage, not provenance. Only `--verify` checks online action provenance, and not external jobs or container digests.

## IR002 independent review tasks
- Independently read, hash and examine the **original ZIP** and receipt using connected SharePoint (educational) read-only, plus normalized mirror and public official upstream sources. If inaccessible, mark incomplete, do not invent evidence.
- Examine actual `runner.ps1` for proper isolation, per-case semantic assertions, stdout/stderr behavior, secret/data disclosures, manifest and PowerShell control flow. Determine if all cases truly reached required states and whether source files were fully restored. Prefer raw bytes and exact line witnesses.
- Reconsider IR001 3 findings + 5 advisories **individually**. F001/F002 cannot be closed merely because upstream limitation was confirmed; recommend compensating policy and adoption boundary. F003 runner assertions may be resolved subject to verification.
- Evaluate two independent compensating gates for any future Product: static ban on mutable `jobs.*.uses` (require full commit SHA) and on unpinned image references for container/services/`docker://` (require immutable `@sha256`); test drift, expressions, matrix and transitive refs separately. This policy is a **proposal**, not already implemented.
- Disentangle `IR_PASS` from `RESEARCH_GRADE_PASS`; classify remaining advisories and bounded follow-up.
- Return ORIGINAL written receipt `IR-TS-ACTIONS-LOCKFILE-001-IR002` with findings, advisories, evidence hashes, exact disposition `PASS/PASS_WITH_LIMITATIONS/FAIL/BLOCKED`; save in Library when available. **No Git writes, no CLI reexecution, no Commander and no Product changes or acceptance**.

## State invariants
The initial issue no longer concerns a broken receipt: R4 runner completed, and its exact SHA-256 validated. The **real observed security gap** is that GH v0.4.0 accepts with exit 0:
- a mutable external reusable workflow dependency;
- an unpinned container image with warning.

Until separate compensating checks are qualified, `NO_GO_PRODUCT_ROLLOUT` remains mandatory. R4 may justify a restricted research decision only.
