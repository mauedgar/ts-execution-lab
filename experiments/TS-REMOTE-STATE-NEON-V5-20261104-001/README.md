# TS-REMOTE-STATE-NEON-V5-20261104-001 — staged cross-runner pilot

**Status:** SOURCE_ONLY / NOT_DISPATCHED / EXTERNAL_PROVIDER_NOT_CONNECTED / PRODUCT_NONE.
**Authority:** User authorized conditional Neon Free adoption as an experimental candidate; no Product Kernel migration, Customer SQL, historical replay or Phase2. Lab is not Product SOT.
**Base:** lab `mauedgar/ts-execution-lab@77f6201ef9122ce682dc405b7afb9a6378701fd4`; V4 original run `41862024848` attempt 1 must be reconciled independently; this source-only V5 does NOT retry it.
**Product cutoff:** `mauedgar/tecnotron-ai:tools@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`, SOT and State Kernel decision `NARROW/UNDECIDED`.
**Independent inventory:** lab `a6d02908a4a428e5f004d7ba712a35e42cc4d8d2`, file `TS-REMOTE-STATE-CONSUMER-AND-CUTOVER-MATRIX-20261104-001.md`.

## Why Neon Free
Neon maintains PostgreSQL outside the GitHub Actions machine, eliminating ephemeral PostgreSQL as the experiment's system-of-record. Official 2026 Free limits include 1 GB storage/project, 100 CU-hours/project/month, 5 GB public transfer, automatic compute scale-to-zero after five idle minutes, and six-hour instant restore (limited). Consumption caps can suspend compute; backup and restore must be exported independently. Product authority and secret custody are *not* provided by Neon/DBOS.

## Strict preconditions before launch
1. User connects Neon provider in ChatGPT or provisions a separate project `ts-remote-state-lab`; ChatGPT connection alone does **not** create the GitHub Actions secret. User controls the Neon account, region, free plan, retention and any billing action. No credentials in chat, Git, PRs, logs or shared files.
2. Provision an entirely empty, isolated *synthetic only* PostgreSQL project/database. Confirm DB credentials have no access to any Product/Customer database. Require TLS in the DB URL (`sslmode=require` or stronger).
3. With appropriate repo rights, user or a qualified secrets-API surface stores the URL exclusively as GitHub Actions secret `TS_NEON_LAB_DATABASE_URL` in `mauedgar/ts-execution-lab`. No secret was created or read in this source-only publication.
4. The workflow `workflow_dispatch` may not be manually runnable until an independently reviewed copy is present on the lab default branch. That promotion is a separate, narrow lab disposition and is **not** Product adoption.
5. A later launch must freeze Git commit/tree, one original GitHub run/attempt, expected native jobs and their receipts; only one dispatch. Any `UNKNOWN` provider effect requires exact identity reconciliation before another launch.

## Test intent and ceiling
- Job `seed` and job `recover` are separate GitHub-hosted runner VMs with no shared workspace. Both access the same managed Neon PostgreSQL and use the exact same DBOS workflow ID derived from one GitHub run ID.
- `seed` creates synthetic-only table and increments one synthetic step; `recover` on the next runner must return the original completion with the table count remaining 1.
- With a persistent remote database, data must survive the first runner's teardown. Verify native run/job/step receipts and SQL count from the second runner.
- GitHub job independence does not prove portability to another provider or full disaster recovery. No assertion of external exactly-once: an interrupted side effect before DBOS step completion remains potentially re-executable.
- This does NOT replace the State Kernel's aggregate Product reducer, authority validation, obligations, global CAS, immutable audit, replay, UNKNOWN guards or artifact store. V4 experiments independently test limited PostgreSQL mechanics.

## Security and cost gates
- Use least privilege and separate schema or dedicated database; no Product data, passwords in source, or paid upgrade.
- Neon Free limits, downtime/quota, short instant restore window and free-tier conditions make it a feasibility target, **not** a production durability SLA.
- No auto-retries, no `workflow_run` chaining, and no cleanup that could delete evidence or accidentally mutate real state.
- DBOS 3.4.0 has been verified on Python 3.15.2 with ephemeral PostgreSQL in run `41859696607` attempt 1; this pilot adds an unproven external Neon endpoint.

**Current disposition:** GO_FOR_SOURCE_STAGING, NOT YET HOSTED_NEON_PASS, NOT PRODUCT_KERNEL_RETIRED.
