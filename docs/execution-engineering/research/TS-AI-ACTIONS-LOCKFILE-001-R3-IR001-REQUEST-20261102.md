# IR001 request — TS-AI-ACTIONS-LOCKFILE-001 R3

## Status
`PENDING_INDEPENDENT_REVIEW` — no reviewer verdict asserted, no Product acceptance, no upstream workflow changes.

## Review subject
A frozen isolated candidate for actual `gh-actions-lock v0.4.0` tests on the Windows notebook. Three attempt identities and outcomes must remain distinct:
- **R1**: CLI generated a lockfile but runner failed constructing receipt; original root retained; recovered lock SHA `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`.
- **R2**: complete receipt, but a fixture bug restored `actions/checkout@v4` after pinning had normalized `v4.4.0`; tests T06–T09 contaminated. Frozen R2 review: `docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R2-REVIEW-20261102.md`.
- **R3**: fresh identity and isolated root, normalized baseline restored, 11 CLI cases completed, restored positive verifications exit 0. Frozen structured evidence: `docs/execution-engineering/research/TS-AI-ACTIONS-LOCKFILE-001-R3-QUALIFICATION-20261102.json`.

## Frozen source and integrity
- Official binary version v0.4.0, SHA-256: `a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`.
- R3 frozen candidate package `TS-AI-ACTIONS-LOCKFILE-001-R3.zip`, SHA-256 `3c4a8d01f971d7eefe2002c1b3c37b0f92d7b5d597672b28728949e8bc5901ea`, 3884 bytes.
- R3 `runner.ps1` SHA-256 `008a624c8ac9ab4abf159c9e6d6ffd9bd721fd220b0e12f3377747d17831c511`.
- Cloud carrier (educational tenant, restricted access):
  `TS-TRANSPORT-BRIDGE-001/TS-AI-ACTIONS-LOCKFILE-001-R3.zip`; use connected educational SharePoint if authorized, do not share public file URL or copy user data.
- R3 original receipt: `TS-TRANSPORT-BRIDGE-001/ACTIONS-LOCKFILE-001-R3-RECEIPT.json`, SHA-256 `f965f8ac0da258f4039f40532d4e1b8acbeccb83b064592f15113c3b8dbc0a42`, 11 test entries.
- Generated lockfile SHA-256 `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc`, 438 bytes; exact R1 artifact recovered independently through SharePoint and verified.

## Reviewer checklist
1. Recompute hashes of frozen R3 candidate and receipt, verify runner scope and static syntax; do not execute payload unless separately authorized.
2. Distinguish the tool CLI's real `--verify-local` (offline *coverage only*) from real `--verify` (online provenance) and accept only the claims actually supported by traces.
3. Confirm T01/T02/T03/T04/T05/T06/T10/T11 expected results, proper isolation, no external effects. Check stdout/stderr excerpts for signs of corrupted or incomplete CLI capture.
4. Treat T07 as **INCOMPLETE external reusable workflow qualification**: failure was due to new workflow missing lockfile entry, not an isolated proof that external jobs are independently locked or enforced.
5. Treat T08 as **INCOMPLETE offline container-warning isolation**; T09 `--no-fix` explicitly warns `node:22` has no digest, while its nonzero exit also reflects a not-pinned new workflow.
6. Check R3 runner's effect isolation. If findings/advisories are material, request a separate R4 with fresh identity. Never rerun R1/R2/R3.
7. Review public/private evidence boundaries, especially no stored tokens, no publication of educational account IDs, and no Product authority.
8. Return an explicit `PASS`, `PASS_WITH_LIMITATIONS`, `BLOCKED`, or `FAILED` with numbered findings/advisories, source hashes and their dispositions. A review submission does not itself grant integration.

## Mandatory authority statement
Research-only. No git push, repository Actions dispatch, Product workflow lockfile insertion, branch protection/ruleset changes, new CI runner effects, or paid model consumption. Commander may observe terminal results and execute already-prepared bounded commands only; GitHub/SharePoint or supplied carrier is the semantic review surface.

## Suggested research disposition until independent review
`GO_RESTRICTED_FOR_RESEARCH_ONLY` for the actual CLI candidate; `NO_GO_FOR_PRODUCT_ROLLOUT`. No claim of a zero-advisory full feature proof.
