# G1 — GitHub Actions ↔ Neon project-scoped access

Responsibility: \`TS-EE-NEON-ACTIONS-QUALIFICATION-001\` (NONPRODUCT).
Owner: \`TS_EXECUTION_ENGINEERING\`, issue \`mauedgar/ts-execution-lab#9\`.
State: \`ACCESS_DESIGN_QUALIFIED / SECRET_PENDING_USER_AUTH / NO_WORKFLOW_DISPATCH\`.
Created in isolated candidate branch: \`exp/ts-ee-neon-actions-001-g1\`, not merged.
Scope: G1 only. This document is not a Product grant, TaskCycle, acceptance or workflow execution.

## Confirmed destination

- Repository: \`mauedgar/ts-execution-lab\` (public, admin connection observed).
- Neon organization: Free; project \`odd-pond-18952360\`, \`ts-ee-neon-actions-qualification-001\`.
- Region: \`aws-us-east-1\`; PostgreSQL 18; branch \`br-cool-sea-bc75qsj1\` (\`main\`); database \`ts_ee_neon_ci\`.
- Functions/trigger listing: successful, currently empty. No mutation to this database or Functions.
- No access or effects on Neon projects \`jolly-dew-53200016\` (Remote State) or \`little-lake-14158600\` (Attendance).
- Product SOT: \`mauedgar/tecnotron-ai:tools:docs/SOURCE_OF_TRUTH.md\`; Kernel final disposition UNDECIDED.

## Selected credential and GitHub setup

**Manual authentication required:** Neon does not expose project-scoped management API-key creation through this chat's connected Neon actions. Do not call Neon branch \`create_credential\`: those are customer runtime credentials with \`storage/functions/ai_gateway\` scopes, not the management API credential required by the branch action. GitHub connector does not expose Actions secret writes. Never create a management API key that is printed into ChatGPT, a GitHub comment, a file, a test output, a runner command argument or an artifact.

Use a **project-scoped organization API key**, named \`ts-ee-neon-actions-001-github-ci\`, restricted to **\`odd-pond-18952360\`** (Editor on one project; no access to other projects). Neon Console → Organization → Settings → API keys → Create new → Project-scoped → choose project; token appears only once.

Use GitHub **environment**, not a repository/organization-wide secret:

1. \`https://github.com/mauedgar/ts-execution-lab/settings/environments\` → New environment → \`ts-ee-neon-ci\`.
2. Add \`NEON_API_KEY\` under **Environment secrets**, pasting the one-time key **directly into GitHub**, never into a chat message or downloadable handoff.
3. Restrict environment deployment branches to trusted candidate branch patterns; ensure untrusted fork PR workflows cannot obtain the secret. Any required trusted approvals must be satisfied through GitHub native controls.
4. \`NEON_PROJECT_ID\` is public metadata, value \`odd-pond-18952360\`. No secret is needed for this ID; workflow may use an explicitly pinned value or a GitHub environment variable.
5. Do not install Neon GitHub App merely to complete this gate. It is a viable later alternative but may change repository/OAuth permissions and is not a prerequisite for official \`neondatabase/create-branch-action\`.

**Secret provenance:** Neon key name/project and GitHub environment/secret metadata are the evidence. Never request or record the secret's value. After user native sign-in+deposit, verify **existence metadata only** and run a controlled **read-only** API access smoke from a trusted \`workflow_dispatch\` workflow with \`environment: ts-ee-neon-ci\`. This must authenticate and confirm exact project ID, return only success/fail and receipt without printing headers, token or DB URLs. G1 = CONFIRMED only if this read-only smoke and original provider receipt succeed.

## Required action hardening before smoke

- Dedicated workflow in \`.github/workflows/ts-ee-neon-actions-001-g1*.yml\` on isolated trusted candidate, no default \`push\` / \`pull_request_target\` trigger, avoid \`pull_request\` secret exposure.
- \`permissions: contents: read\`; no broad \`write-all\` or privileged runner.
- \`environment: ts-ee-neon-ci\` on the dedicated job (environment secrets inaccessible until environment is used).
- Pin third-party GitHub Actions to an exact reviewed commit SHA, not mutable version tag. Qualify exact source before enabling.
- No \`set -x\`, no secret in shell command arguments/echo/logs; Neon API \`GET /api/v2/projects/odd-pond-18952360\` for read-only canary.
- No branch creation, DB migration, Neon Function deployment, workflow dispatch or project/branch cleanup as part of this access-design receipt.
- On \`401\` or \`403\`, treat G1 as BLOCKED and preserve original attempt ID; do not blindly regenerate/retry keys.
- Rotate by making a fresh project-scoped key, updating only this GitHub environment secret, validating original new attempt and revoking the old one; revocation is a separate authorized effect.

## Closure / next boundary

**G1 status now: BLOCKED_EXTERNAL_SECRET_DEPOSIT.** Existing evidence verifies account, role, scope, project, region, repo and chosen access model. Remaining user authentication action is **Neon project-scoped token → GitHub environment secret**; waiting for native metadata confirmation. No tool in this session can verify secret value or create it safely on both sides. Once confirmed and read-only access smoke passes, issue #9 can advance G2 within its write-set, and prepare \`@Rotación\` **OPERATIONAL**, not STRICT. Never claim rotation occurred merely because a handoff was published.

Reference sources (current as of 2026-11-08):
- Neon scoped keys: https://github.com/neondatabase/website/blob/main/content/faqs/find-or-generate-neon-api-keys.md
- Neon action: https://github.com/marketplace/actions/neon-create-branch-github-action
- GitHub environments: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- GitHub encrypted secrets: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
