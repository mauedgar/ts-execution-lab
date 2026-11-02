# TS-AI-ACTIONS-LOCKFILE-001 — R2 review and R3 decision

Status: **R2_TERMINAL_WITH_FIXTURE_DEFECT / NO_PRODUCT_ADOPTION / NO_RETRY_R2**.

The new R2 runner did produce its full receipt (9 cases), preserving the prior R1 root and receipt failure. Official binary v0.4.0 SHA-256 `a64179817d7605d705e805475a09b5ef0be12a3469477d8607350f1f3cc26d8b`. Carrier SHA `1dcddd39b7b9ddd46ebbe7758a6b0978a2011eefedfdb465c9c8d1b3c5bb805f`. Receipt SHA `c739d60f70be066a5f6000d45ba629ccf6d97838886601559343f9d51b52c756`. The recovered/generate lockfile SHA was `bad92b372467c06dc8de4d1339caec4a1557a9d7d6eaf723dc047d759f94d9bc` in both R1 and R2.

Observed R2 results:

| Case | Exit | Disposition |
|---|---:|---|
| T01 missing lock, offline | 1 | Expected missing pin |
| T02 generate lock | 0 | Generated valid lockfile |
| T03 verify-local on generated state | 0 | Correct coverage of normalized ref |
| T04 verify online | 0 | Online verified |
| T05 new `uses:` with old lockfile | 1 | Expected stale/not-pinned, BUT baseline restoration then reused wrong content |
| T06 local action | 1 | Local-action finding **and** unexpected ref-changed/stale |
| T07 external reusable | 1 | **Inconclusive** due inherited ref-changed/stale |
| T08 unpinned container | 1 | **Inconclusive** due inherited ref-changed/stale |
| T09 restored verify-local | 1 | **Fixture repair required**, not CLI failure |

**Root cause:** the CLI normalizes `actions/checkout@v4` to `actions/checkout@v4.4.0` during pinning. R2 runner captured `$original` prior to CLI generation, then restored obsolete `v4` after T05 while lockfile pinned `v4.4.0`. This contaminated later negative/positive cases.

**Narrow R3 candidate:** separate run identity and fresh root, persist `RESULTS.ndjson` and final `RECEIPT.json`, snapshot the **normalized generated baseline after T02**, use that snapshot for T05 mutation and restoration. Then test T06/T07/T08 without ref-drift, and T09 clean restored state; use `--no-fix` as an extra read-only path for container warnings. Preserve R1 and R2 and ensure hash/parser/preconditions before executing R3. Do not invoke R2 again.

**Authority:** only previously authorized isolated experiment/recovery; no Product, push, Actions dispatch, automated adoption, model charges or implicit repeat of ambiguous effects. Independent review of frozen R3 is required before recommendation.
