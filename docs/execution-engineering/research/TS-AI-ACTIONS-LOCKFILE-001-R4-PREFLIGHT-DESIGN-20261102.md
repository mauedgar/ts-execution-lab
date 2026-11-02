# TS-AI-ACTIONS-LOCKFILE-001 — R4 preflight design (NOT EXECUTED)

State: `DESIGN_ONLY / AWAIT_IR001`. This document is not an execution grant, retry, or Product acceptance.

## Frozen identity
- R3 carrier SHA-256: `3c4a8d01f971d7eefe2002c1b3c37b0f92d7b5d597672b28728949e8bc5901ea`
- R3 runner SHA-256: `008a624c8ac9ab4abf159c9e6d6ffd9bd721fd220b0e12f3377747d17831c511`
- R3 lockfile SHA-256: `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`
- Official gh-actions-lock v0.4.0 Windows AMD64 SHA-256: `a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`

## Why R4 may be necessary
R3's T07 and T08 did not isolate the intended negative condition: the new workflow lacked its own lockfile entry, independently producing a nonzero exit code. T09 `--no-fix` directly emitted the no-digest warning, but its exit code also reflected missing workflow coverage. A failed command is not evidence that the specific expected check fired. R3's T10/T11 restored positive verification both PASS.

## Distinct isolated scenarios (proposed, not run)
1. **Remote reusable jobs (T07 repair):** create a standalone synthetic `jobs.<id>.uses` external workflow fixture with NO direct steps. Record actual CLI onboarding, lockfile and `--verify-local`/`--verify` outcomes. Compare a mutable `@main` reference with a verified full SHA reference. If fictional repository cannot resolve, stop as INVALID_FIXTURE and use a legitimate public immutable workflow with its real provenance; never claim PASS from an artificial missing entry. Regardless of result, GitHub's documented upstream limitation is that external reusable job-level workflows are NOT protected by gh-actions-lock; pin them directly to full commit SHAs in YAML and review the dependency.
2. **Container digest (T08/T09 repair):** isolate a workflow that is already correctly onboarded with complete action coverage; add `container: node:22`. Run `--verify-local`, `--no-fix` and `--verify` while recording warnings AND whether missing lockfile entries contribute to exit status. Compare with the same workflow using a legitimately sourced immutable digest; never invent a sha256. A warning is a warning, not evidence the container image was safely pinned.
3. **Coverage versus provenance:** in a fresh synthetic fixture, tamper the locked commit to a syntactically valid but incorrect value; contrast offline coverage with online provenance. A local coverage PASS must not be interpreted as proof of trusted provenance.
4. **Restore and seal:** remove only the new negative fixture mutations; run final positive checks on the fresh R4 root, preserve per-case NDJSON, raw output excerpts, canonical SHA-256 manifests and a separate terminal receipt. No reuse of R1/R2/R3 IDs or roots. Stop for any UNKNOWN effect.

## Controls
All code/materialization is performed on normal semantic surfaces, NOT via Commander. Commander is limited to bounded, already-prepared mechanical execution and compact result observation. No git push, Actions dispatch, Product repositories, secrets, SQL, paid tool execution, acceptance, or auto-retries. An independent reviewer must first dispose of IR001 and approve the bounded follow-up scope before any R4 execution.

Sources:
- https://github.com/github/gh-actions-lock/blob/v0.4.0/README.md
- https://github.com/github/gh-actions-lock/issues/179
- https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies
