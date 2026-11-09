# TS-EE Neon Actions 001 — G5 qualification dossier (candidate, not Independent Review)

Responsibility: TS_EXECUTION_ENGINEERING; OPERATIONAL / NONPRODUCT.
Authority: [issue #9](https://github.com/mauedgar/ts-execution-lab/issues/9).
Product source of truth: mauedgar/tecnotron-ai:tools/docs/SOURCE_OF_TRUTH.md; Kernel remains UNDECIDED.
No Product acceptance/integration, no TS Remote State / Attendance project mutations.

## Qualified experiment gates

| Gate | Exact execution | Candidate outcome | Limit |
|---|---|---|---|
| G1 | GitHub Actions run 42549487422 (read-only) | PASS / CONFIRMED | Scope initially further examined in G2 |
| G2 | Run 42551306634 | FAIL_PRECONDITION / NONE | GET /projects returned 404, no Neon writes |
| G2 | Run 42551461126, head 2d26c6df7a013729377da1c7fa881caea89452fb | PASS / CONFIRMED | disposable branch created, synthetic SQL test, delete & GET404 |
| G3 | Run 42552326983, head 802f23b8d7ba6fc26aee8370635210f799a918be | Function deployment PASS | Neon g3pulse Node24 Function, disposable branch |
| G3 | Neon trigger trigger-2e5a241a-2d8c-41bd-b8f1-3181b3c0ba10 | E2E PASS | scheduled 02:43:00Z; persisted 02:43:19.039Z; SQL elapsed 45ms; trigger disabled afterwards |
| G4 | Run 42552680334, head 85ea170f1e1f5605f674de2346d4f794342b6753 | two parallel candidate jobs PASS | CAS/UNIQUE/rollback/recovery; both attempt-owned branches destroyed |
| G5 lock | Run 42553077453 | FAIL_PRECONDITION / NONE | lock was generated; wrong working-tree existence guard prevented push |
| G5 lock | Run 42553181797 (head c8de1c3b00ab8f5caee7c12e1caa0fa7298cdc42) | PASS | exactly one file added in commit eb0cfdf3ea519ea03018812313bae47c57168790 |

G3 artifact's lock is SHA256 2147dd49d99a3fd9d22b6cc7c146f076f334de89f9df80726af4f5243ca846aa, 90,220 bytes, lockfile v3 / 201 packages, exact direct deps neon@9.2.0, @neon/config@1.10.0, @neondatabase/serverless@1.2.0. G5 run regenerated **the same hash**, ran npm ci successfully on Ubuntu 24.04 / Node 22.23.0 and published package-lock.json to GitHub. GitHub compare verified one addition only.

## Resource and cost matrix

As of Nov 2026, Neon Free reference: [official October 2 2026](https://neon.com/blog/neon-free-plan-1-gb-per-project).
- 100 Free projects, with separate per-project compute quotas; target one existing Free project in compatible region aws-us-east-1.
- For this project: 100 CU-hours monthly; 1 GB Postgres storage; 10 branches; 6-hour instant restore window.
- Functions: 1M invocations, 10 active capacity-hours and 400 waiting capacity-hours per month.
- No paid service, plan upgrade or purchase was performed. These are quota limits, not measured actual consumption.
- Peak observed branch count <=4: Neon main, G3 TTL branch, and G4 candidates while concurrent; below 10-branch cap.
- G2 + G4 candidate branches deleted with ownership verification. G3 temporary branch expires 2026-11-09T03:32:00Z, not yet confirmed absent when dossier authored. G3 trigger disabled with next_run_at=null.
- SQL synthetic, short-lived; one confirmed cron event; low consumption expected but exact metered CU-hours and function capacity-hours **unavailable** from Free API. No unverified $0 bill claims.

## Security and replay controls

- Scoped project key available only as NEON_API_KEY in protected environment ts-ee-neon-ci on exact trusted branch. No key in source, receipt, logs or artifacts. HTTP body of scoped-auth checks discarded.
- Positive-own GET200 + negative-other-project GET403/404 before any G2/G3/G4 Neon write. This is a capability canary; it is not comprehensive proof of RBAC for every API verb.
- Workflows use exact Github repo/ref guards, push paths limited to own workflow file, permissions contents:read in Neon-touching jobs, concurrency cancel-in-progress:false, exact SHA-pinned external actions.
- G5 lock publishing workflow alone requires contents:write, has no Neon environment/secret, only commits one SHA-checked allowed lockfile and checks exact head; its effect confirmed in Git compare.
- Unique run-bound Neon branch names + action created=true, no shared Product database; cleanup only after exact ID/name/parent, one DELETE + GET404. G3 trigger was disabled after the first proven execution; TTL used rather than manual deletion.
- Function handler's x-neon-trigger-invocation-id header gate is not cryptographic authentication: **never adopt this synthetic public URL as a Product security design**.
- Historical G2/G3/G4 action pins to Node20-target actions emitted a Node20 deprecation warning on GitHub-hosted runner (forced Node24). G5 lock publisher uses v6 actions with Node24 support; full migration of historical experiments not necessary for frozen run identity.
- No force-push/retry of terminal or uncertain remote effects; separate candidate commits were created only after each original FAIL_PRECONDITION terminal reconciliation.

## Qualification caveats / review targets

1. Cancellation after remote branch creation with UNKNOWN state and full crash/stop recovery **not empirically tested**. G4 covered parallel CAS, transaction abort and recovery but not GitHub cancellation.
2. G3 negative HTTP error path and recovery after Function failure **not independently exercised**, despite proof of successful actual scheduled delivery, SQL write, telemetry and trigger shutdown.
3. Credential rotation and explicit revocation protocol needs documented procedure; secret contents are never to be copied to evidence.
4. G3 TTL branch deletion final provider observation pending its expiry; avoid asserting cleanup finished before checked.
5. Node20 runtime deprecation warning from older action pins remains a future portability maintenance item.
6. Independent Review strict read-only with 0 findings and 0 advisories is **not yet done**. No QUALIFIED claim from self-review.

G5 candidate state before IR: TECHNICAL_EVIDENCE_COLLECTED; **NOT_QUALIFIED_YET**.
Evidence in ts-execution-transport/results/TS-EE-NEON-ACTIONS-001-G{2,3,4}-20261109-001/RESULT.md.
