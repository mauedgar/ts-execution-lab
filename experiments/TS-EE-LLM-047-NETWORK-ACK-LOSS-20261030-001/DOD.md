# TS EE LLM047 — Native HTTP ACK-loss / durable reconciliation DoD (frozen)

**Authority**: TS_EXECUTION_ENGINEERING experimental; Product = NONE. Existing Tecnotron Upper LC, issue #34/#35, TaskCycle and canonical Beads/routing are **out of scope**.

**Experimental objective:** a real TCP/HTTP connection between two distinct Python processes (consumer/provider), with a durable SQLite journal on each side, network ACK loss **after provider commit**, restart-based reconciliation, no blind retries, correlated identities and one effect per attempt. No external provider request, no billing, no LLM inference.

## Frozen source before dispatch

- `provider047.py` Git blob `e1f71a57fc9ca31daecfca259262805ae6e31fcc`.
- `client047.py` Git blob `69681f595675f21af2f999696dfe4c3aa65f33b2`.
- `test047.py` Git blob `4b721e20bab7e402fe2d015cf72b55c67fc3e2aa`.
- Operation `TS-EE-LLM-047-NETWORK-ACK-LOSS-20261030-001`, exact `ExecutionAttempt=TS-EE-LLM-047-ATTEMPT-001`, owner `TS_EXECUTION_ENGINEERING`, runner-only writable scratch under `RUNNER_TEMP/ts-ee-llm047-$GITHUB_RUN_ID`.
- One GitHub Actions push-triggered dispatch after code/DoD frozen; receipt `RESULT047.json` and artifact with provider+consumer SQLite databases, logs and hashes. **No automatic retry**. Job may finish FAIL without changing authority.

## DoD acceptance (seven independently frozen tests)

1. **Network ACK loss after commit:** provider commits one SQLite effect, closes its real HTTP socket without sending an ACK, distinct client records ACK_UNKNOWN; independent restarted client GET retrieves matching authoritative receipt, records NO_RETRY_CONFIRMED. Provider remains alive, no duplicate effect.
2. **Provider crash after commit before ACK:** actual HTTP server process exits abruptly (code 73), client observes unknown transport outcome, provider restarts with same database and GET proves exactly one original effect and receipt.
3. **Provider crash before commit:** server process exits with code 74 during transaction; client and offline reconciliation preserve UNKNOWN; provider restarts, returns authoritative absence, consumer records ABSENT_REQUIRES_AUTHORITY. **No automatic retry**.
4. **Consumer loses received ACK:** independent consumer discards a real HTTP ACK before durable journaling, new consumer process retrieves matching provider receipt, no repeat.
5. **Identity collision:** same attemptId with different owner returns HTTP 409 BLOCK_IDENTITY and leaves one original effect.
6. **Explicit duplicate injection:** test sends same identity twice to qualify provider idempotency; second returns ALREADY_CONFIRMED with same receipt, one effect. **Not a permitted Product retry after UNKNOWN.**
7. **Concurrent HTTP requests:** two separate consumer subprocesses submit same identity to threaded provider; only one APPLIED_ACK and one ALREADY_CONFIRMED, identical receipts and one provider effect.

All scenarios require `PRAGMA integrity_check=ok` for original provider and main consumer databases. Provider uses SQLite WAL, `synchronous=FULL`, primary-key uniqueness and `BEGIN IMMEDIATE`. Every scenario gets its own pair of database files in a newly created scratch directory.

## Stop / result and evidence rules

- Real network boundary is **127.0.0.1 TCP HTTP**, not a remote internet provider, independent machine, TLS or network partition. Python child subprocess crash/restart is real but process-level; no physical power outage or hard durable storage fault injection proven.
- The fixture's deliberate concurrent writes and duplicate request are adversarial test injections, never an external Product retry.
- Bounded local startup readiness checks are part of the fixture, **not Commander polling**, and cannot be equated to provider-side ACK certainty.
- PASS only when all 7 tests PASS, result receipt identity and exact source/hash verified, 7 provider DBs + 7 consumer DBs retained, original logs/hash manifest saved, run attempt exactly 1. Partial, fail, or ambiguous evidence is **FAIL/BLOCKED/UNKNOWN**, not a historical PASS.
- Overall disposition is `COMPLETE_WITH_LIMITATIONS` even with bounded PASS. Product authority remains NONE; no model skill ranking, Beads adoption, canonical scheduler, or no-retry grant for real providers.
- Artifact retention limited by provider. Git/Library indexes do not replace original bytes.
