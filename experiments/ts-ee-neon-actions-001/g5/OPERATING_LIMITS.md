# TS EE Neon Actions 001 — bounded operating policy / G5 A001–A003

## Scope and authority

- Owner: TS Execution Engineering; [lab issue #9](https://github.com/mauedgar/ts-execution-lab/issues/9), NONPRODUCT / OPERATIONAL.
- This is an engineering qualification experiment, not a Product migration or replacement of Kernel. Never access or modify projects jolly-dew-53200016 (TS Remote State) or little-lake-14158600 (Attendance).
- Only Neon project odd-pond-18952360, main branch br-cool-sea-bc75qsj1 as read-only parent. Do not change main schema, delete main, promote experiment resources or accept Product.
- Experiment branches uniquely prefixed with gate and original GH run ID. Never reuse, overwrite or delete branches based on names alone. Verify exact project, ID, parent, name, created ownership, non-primary and postcondition.
- Cancellation or crash can leave an owned branch. If original effect status is UNKNOWN, observe GitHub run and Neon branch by exact identity before any new action. Do not create a retry attempt or manually delete it; TTL-only recovery on this experiment.

## Bounded Free budget / A001

- Current Neon project subscription is free_v3 (provider project record), region aws-us-east-1, PostgreSQL 18, default max 0.25 CU, retention 6 h, project branch limit 10.
- Reference Free quota in 2026: 100 CU-hour/project/month, 1 GB Postgres storage/project, 10 branches, function invocations and capacity-hour caps per Neon Free plan. These values are ceilings, not measured consumption.
- Direct read-only call to Neon get_project_consumption on 2026-11-09 returned HTTP 403: "This endpoint is not available. It is included with Launch plans and above." **Observed provider limitation**, not a valid 0-cost metered receipt.
- Do not upgrade plan for metrics, buy credits, create paid integrations, remove defaults or increase compute size. Billing conclusions: NO_CHARGE_OBSERVED_FROM_REPO_ACTIONS but ACTUAL_BILLING_UNVERIFIED; cannot claim $0 spent based on metadata counters.
- Hard operating envelope for next test candidates: <= 4 concurrently present branches including main, <= 8 minutes automatic TTL for intentionally abandoned branches, <= 10 minutes per GH job, <= 2 confirmed cron occurrences before disabling, <= 4 synthetic SQL connections per independent candidate. Stop when branch count, branch ownership, quota or billing evidence is ambiguous. Never spin open-ended scheduled workflows or indefinite Neon cron.
- Stop immediately if Neon reports quota exhaustion, paid upgrade prompt, create failure due to resource ceilings, unknown effects, missing secret, unexpected HTTP statuses, failed identity guard, or unknown project ownership. No automatic scaling/retry/plan upgrade. Escalate project to controller with exact refs and provider response codes only.
- Allow periodic read-only observation on original attempt and project branch list; do not create active polling or duplicate runs. A provider Free-plan 403 for usage metering is tracked explicitly as a limitation, not hidden.

## Credential source, scope and rotation / A002

- Credential route: manually provisioned **Neon project-specific API key**, supplied to GitHub Actions protected environment `ts-ee-neon-ci` as `NEON_API_KEY`. The repository uses the environment variable `NEON_PROJECT_ID=odd-pond-18952360`. Do not embed credentials in source, artefacts, CLI args, action output, commits or review receipts.
- G2/G3/G4 verified own project GET200 and other project GET403/404 using only HTTP status, response discarded; this is an **empirical negative scope canary**, not a complete proof that every API verb is least-privileged.
- GitHub environment requires the branch policy to admit only `exp/ts-ee-neon-actions-001-g1`; Neon jobs run on push affecting own exact workflow and guard exact GitHub repo/ref/event, never forks with secrets.
- Keep runner token `permissions: contents: read` for Neon-touching jobs. The separate G5 lock publication needed `contents: write` and did not load Neon environment/secret. G4 controlled self-cancellation is an exceptional job limited to `actions:write` to cancel **its original exact run** only.
- **Rotation:** (1) identify and freeze existing secret's responsible owner and active run references without reading its value; (2) create a new project-scoped Neon key restricted to odd-pond-18952360; (3) replace the GitHub environment secret with new key in approved `ts-ee-neon-ci` store; (4) run a **new, separately authorized read-only scoped canary** (not replay an old run), ensure own GET200 and foreign GET403/404; (5) revoke only the old key via Neon after verifying its identity and no active dependent attempt; (6) record new key metadata, date, owner, observed result and revocation receipt without secret values; (7) if old-key ownership or dependency is uncertain, STOP and seek competent authority rather than revoke.
- **Compromise:** block workflow dispatch/disable experiment trigger, revoke implicated key using Neon UI after identifying exact key and dependent effects, rotate to fresh project-only key, inspect original runs and branches without replays, and escalate any Product scope concern.
- No new integration installation required; the official Neon GitHub Integration may be considered later but is not a requirement for this verified manual key path.

## Node action compatibility / A003

- Original G2–G4 runs are frozen evidence. The SHA-pinned `actions/checkout@v4`, `setup-python@v5` and `upload-artifact@v4` binaries emitted Node20-target warnings even though GH coerced Node24. **Never replay or rewrite terminal runs simply to silence historical warnings.**
- For all new candidate workflows use reviewed exact SHA-pinned Node24-compatible generations, e.g. checkout v6 `d23441a48e516b6c34aea4fa41551a30e30af803`, setup-node v6 `249970729cb0ef3589644e2896645e5dc5ba9c38`, setup-python v6 `ece7cb06caefa5fff74198d8649806c4678c61a1`, upload-artifact v6 `b7c566a772e6b6bfb58ed0dc250532a479d7789f`; verify action source and version each next candidate.
- Do not change the pinned G2/G3/G4 workflow files until there is a distinct authorized successor, since their `on.push.paths` self-trigger may initiate unapproved new remote effects.

## Limits and review

- Native Neon Functions strip caller-supplied `X-Neon-*` headers; the dedicated G5 external header-forgery E2E at run 42554308425 proved HTTP403 for GET, POST without header and POST with fake header. G3 persisted synthetic row count stayed two. Not a general authentication pattern outside Neon's native edge.
- Two cron events were confirmed despite shutdown after first was observed. Disable prevents future schedule, does not prove cancellation of already-dispatched deliveries; function idempotency uses scheduled_at PRIMARY KEY and ON CONFLICT.
- G4 two-candidate CAS/rollback tested synthetic transaction recovery. G4 cancellation E2E (separate run) and Neon TTL disappearance require original run/branch receipts and their own join.
- Independent IR001 NO_RECOMMEND preserved; any repair proof informs new independent IR002, not retroactive alteration of original verdict.
