# TS EE Neon Actions 001 — IR001 finding/advisory repair candidate for IR002

## Provenance

- Controller: TS Execution Engineering, NONPRODUCT OPERATIONAL; GH lab [issue #9](https://github.com/mauedgar/ts-execution-lab/issues/9).
- Prior independent IR001: [transport report](https://github.com/mauedgar/ts-execution-transport/blob/759b746b0b85f17fa9a1611ad74c9ce7f35c6479/results/TS-EE-NEON-ACTIONS-001-IR001-20261109-001/REVIEW.md), verdict NO_RECOMMEND 3F/4A, review expressly focalized (not full-tree).
- Product SOT exact `mauedgar/tecnotron-ai@26509b74d50207bb247dcc9bdb929a63f5451e88`, tree `eecf5c4e52b8ca511d45ecebd9495ffb051997ac`; `docs/SOURCE_OF_TRUTH.md` explicitly preserves developer-only Product authority and Kernel undecided.
- GitHub comparison from original G1 source `f4cb27f5a5dd71c1198d4cc1a92bacde0d6a48ca` through new candidate checked: 20 files changed, **all** under `experiments/ts-ee-neon-actions-001/**` or `.github/workflows/ts-ee-neon-actions-001*.yml`; no `tecnotron-ai` modifications, no Product integration.

## Finding dispositions (not independently accepted)

| IR001 | Repair/evidence | Controller status |
|---|---|---|
| F001 actual cancellation/UNKNOWN | New original run [42554516435](https://github.com/mauedgar/ts-execution-lab/actions/runs/42554516435) deliberately cancelled after provider branch `br-super-resonance-bcvr5y4n` created & exact ownership verified; independently observed residual branch after cancellation; provider TTL at 03:14:31Z, then `list_branches` absence and exact `get_branch` HTTP404; no retry or manual cleanup. Receipt `ts-execution-transport@6ad2113751d7a52b21290562ab3a35d4924a22b8:results/TS-EE-NEON-ACTIONS-001-G4-20261109-003/CANCEL-TTL-CONFIRMED.md`. | candidate RESOLVED for TTL-scoped Neon branches; does NOT qualify all remote effects with no TTL |
| F002 purported spoofing `x-neon-trigger-invocation-id` | Official Neon native Functions edge strips client-supplied `X-Neon-*` headers. New GH [42554308425](https://github.com/mauedgar/ts-execution-lab/actions/runs/42554308425) exact no-secret native endpoint negative GET, POST no header, POST with forged header: **all HTTP403**, DB row count unchanged=2. Receipt `ts-execution-transport@0d7bf8e1f986e5f2a4221d226d18d802dd5154e2:results/TS-EE-NEON-ACTIONS-001-G5-20261109-001/HEADER-FORGERY-E2E.md`. | candidate REFUTED as native-edge exploit; header check is NOT a generic security pattern for other proxies |
| F003 lifecycle closure | G3 cron two events 02:43 and 02:44 UTC committed, trigger disabled `enabled=false,next_run_at=null`. G3 branch `br-holy-bird-bctkk4ym` expires at 03:32:00Z on 2026-11-09. The original controller will observe expiration; the independent IR002 MUST query provider after this time, including branch exact 404, and distinguish queued deliveries from future schedule. | PENDING provider TTL / never infer cleanup until exact read |

## Advisory dispositions

| IR001 | Repair/evidence | Controller status |
|---|---|---|
| A001 quotas Free | `g5/OPERATING_LIMITS.md` defines <=4 branches including main, expire TTL <= 12min for synthetic runs (G5 intentional failure candidate), bounded time/compute/stops and no plan upgrades. Neon metering `get_project_consumption` returned explicit HTTP403 "Launch plans and above"; this cannot be claimed as exact usage=0 or paid verification. | documented provider limitation + fail-closed cost envelope; request reviewer classify whether this suffices within no-pay Free |
| A002 rotation | `g5/OPERATING_LIMITS.md`: project-specific key, env scoped branch, owned GET200/foreign GET403-or-404 preflights, independent credential rotation/revocation 7-step SOP, compromised key path. No secret values persisted or requested. | candidate repaired by documented bounded runbook; metadata from GitHub env management API not independently readable (not an invitation to bypass access controls) |
| A003 Node20 warnings | Historical G2/G3/G4 unaffected and not rerun. G5 [42555017053](https://github.com/mauedgar/ts-execution-lab/actions/runs/42555017053) uses Node24 generation checkout/setup-node/setup-python/upload-artifact, log has NO `Node.js 20 is deprecated` warning. External Neon action emits upstream `url.parse()` deprecation warning, not silently ignored. | candidate repaired for future actions; vendor upstream maintenance caveat |
| A004 negative Function recovery | New G5 original run 42555017053 deployed `g5failure` on disposable branch `br-ancient-flower-bclbshuj`, expires 03:23:55Z. Single scheduled_at `2026-11-09T03:14:00Z`; 03:14:39Z native delivery returned HTTP503 deliberately and recorded attempts=1/state=failed_once; 03:15:46Z platform redelivered SAME occurrence, SQL row attempts=2/state=recovered, log `TS_EE_G5_RECOVERY_IDEMPOTENT`. Trigger disabled after first failure, `next_run_at=null`. Receipt `ts-execution-transport@9e853cda1285e8993ac590e76102a318f1c797fb:results/TS-EE-NEON-ACTIONS-001-G5-20261109-003/FUNCTION-RETRY-RECOVERED.md`. | candidate RESOLVED for native retry and idempotency; TTL postcondition separate |

## G5 qualification boundaries

- G1–G4 original test runs and G5 exact lock reproducibility remain as frozen; do not re-execute.
- G5 current source remains lab branch; no Product/Kernel/H6/Beta Run/Remote State integration permitted by this experiment.
- No candidate can claim `QUALIFIED` until a new **Independent Review** of frozen exact source/evidence obtains 0 findings & 0 advisories within accepted Free-plan limits; the original IR001 NO_RECOMMEND remains immutable.
- Reviewer should independently check all 20 changed files and GH original runs, exact Neon present branches, former branches' absence after TTL, actual G5 503/retry/logs, platform-native header spoof negative, maintainer permissions and SOT.
