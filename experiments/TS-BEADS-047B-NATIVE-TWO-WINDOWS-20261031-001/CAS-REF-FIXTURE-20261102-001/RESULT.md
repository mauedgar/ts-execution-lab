# TS-BEADS 047B — original one-time GitHub ref/CAS synthetic result

**Class:** EXPERIMENTAL_PROVIDER_MECHANICS_EVIDENCE_ONLY, not Product or SQL grant, not independent review. **Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`. **ExecutionAttempt:** `TS-BEADS-047B-GITHUB-CAS-FIXTURE-20261102-001`.

**Frozen pre-effect plan:** `mauedgar/ts-execution-lab@15550221eb3ee2a39191ce59a1c1f5cabe8b6a49:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/CAS-REF-FIXTURE-20261102-001/PLAN.md`.

**Original provider observations (each effect launched exactly once):**
1. `search_branches` found 0 matching exact branch before creation.
2. `create_branch` on `mauedgar/ts-execution-lab` returned branch `experiment/ts-beads-047b-cas-fixture-20261102-001` when anchored to frozen `b2bb1f26206000abe61e971f51be0a7c9d4051f3`. Original result reported the branch name only; do not infer commit from that response alone.
3. Subsequent exact branch fetch returned SHA `b2bb1f26206000abe61e971f51be0a7c9d4051f3`, matching the expected anchor.
4. `update_ref` invoked ONCE with `force=true`, `expected_sha=b2bb1f26206000abe61e971f51be0a7c9d4051f3`, target `ee5efa31cf9674c4f148e5ef51b710899df5c359`; original result `success=true`.
5. Exact branch fetch after B returned SHA `ee5efa31cf9674c4f148e5ef51b710899df5c359`. Identity/effect reconciled. No retry or timeout, no prior UNKNOWN.

**Verdict:** `PASS_POSITIVE_GITHUB_REF_CREATE_AND_GUARDED_UPDATE / EXPERIMENTAL_SYNTHETIC_ONLY`. This establishes that the selected connector/API path could perform an authenticated branch create followed by a positive force-with-lease update and exact readback under the observed single-actor case. It does **not** establish concurrent contender rejection, a true atomic external claim issued by competent Control, exclusive ownership for a live SQL attempt, signature verification, no original 047B effect, Windows host or Beads durability. **No adversarial duplicate attempt was launched**.

**Boundary:** The synthetic disposable branch is deliberately left pointing to `ee5efa31cf9674c4f148e5ef51b710899df5c359`. Do not delete/reset it automatically. Product `tecnotron-ai`, #34, #35, State Kernel, SQL, Tailscale, Beads and native notebook were not changed by this fixture. No credentials, accounts, server or grant were created.

**Next genuinely necessary dependency:** qualify a competent Control-authorized **real** off-host exclusive claim tied to an exact immutable attempt and reconcile original provider receipts/PIDs, before considering a source/issuer/host grant. A synthetic positive API response is insufficient to close IR009 F001/F002/F006 or establish `HOST_INDEPENDENCE_GO`.
