# TS EE LLM047 — Terminal experimental network ACK-loss result

**Date:** 2026-10-30. **Execution authority:** `EXPERIMENTAL_CONTROL_ONLY` / TS_EXECUTION_ENGINEERING. **Disposition:** `PASS_BOUNDED_REAL_TCP_ACK_DROP_RECOVERY / COMPLETE_WITH_LIMITATIONS`. Product authority/effects NONE, no Upper LC #34/#35 intervention, no Beads Product adoption, no model routing adoption.

## Original attempt / frozen provenance

- Operation: `TS-EE-LLM-047-NETWORK-ACK-LOSS-20261030-001`.
- Original ExecutionAttempt: `TS-EE-LLM-047-ATTEMPT-001`, writer: disposable GitHub Actions runner's `RUNNER_TEMP`. **One original push-triggered execution; no retry.**
- Executed exact subject: `mauedgar/ts-execution-lab@a62581ce33992511543567dead34b21b1d141b6f` on `experiment/llm-047-network-ack-loss-20261030-001`.
- Native source blob pins verified by the workflow:
  - `provider047.py@e1f71a57fc9ca31daecfca259262805ae6e31fcc`;
  - `client047.py@69681f595675f21af2f999696dfe4c3aa65f33b2`;
  - `test047.py@4b721e20bab7e402fe2d015cf72b55c67fc3e2aa`.
- Experiment DoD: `experiments/TS-EE-LLM-047-NETWORK-ACK-LOSS-20261030-001/DOD.md`, frozen before workflow dispatch.
- [Original Actions run 41142339467](https://github.com/mauedgar/ts-execution-lab/actions/runs/41142339467), job `124359340987`, run_attempt 1, terminal `completed/success`.
- [Original artifact 13019855824](https://github.com/mauedgar/ts-execution-lab/actions/runs/41142339467/artifacts/13019855824), `ts-ee-llm047-original-41142339467`, 21,352-byte ZIP, `sha256:9e33be76d253be8b876e1013de8f0ff581de2d28120d7000a05c89b73222fedb`; provider expiration 2026-11-29 23:05:54 UTC. Artifact contains `RESULT047.json`, original run log, native provider/client logs, SQLite databases for all seven cases, checksum manifest `ORIGINAL_FILE_SHA256.txt`. An indexed Markdown report is **not** a replacement for those bytes.
- Native `RESULT047.json` SHA-256: `c68a18c47e73d1bec3c078dd80b1c9f7a5846e124a415e30d62095a26870b700`, printed by original runner.

## Actual empirically verified results

**7/7 independent tests PASS**, 0 FAIL, 0 ERROR; each used separate SQLite DBs and client/server processes, with integrity checks after execution. The HTTP provider was listening on `127.0.0.1` using real TCP connections (not mock function calls). The consumer is a distinct Python CLI process; both used SQLite WAL, `synchronous=FULL` and an append-only consumer journal.

| Test | Actual injected behavior | Observed reconciliation |
| --- | --- | --- |
| 01 | HTTP provider commits effect then forcibly closes TCP socket without sending HTTP ACK; provider remains alive | Distinct client observes `ACK_UNKNOWN`, new client process queries durable provider receipt and records `NO_RETRY_CONFIRMED`, one effect |
| 02 | Provider process `os._exit(73)` after DB commit but before HTTP ACK; original transport drops | New provider process opens same SQLite DB; new consumer GET obtains original receipt, one effect |
| 03 | Provider `os._exit(74)` before DB commit, drops transport | Consumer retains `RECONCILE_UNKNOWN` while provider unavailable; after restart, authoritative GET returns absence and `ABSENT_REQUIRES_AUTHORITY`, **no automatic retry** |
| 04 | Consumer receives a real ACK then intentionally discards it before durable ACK journal | New consumer process GET recovers matching receipt; one original effect |
| 05 | Same attempt ID with changed owner | Provider returns HTTP 409 `BLOCK_IDENTITY`; original effect remains untouched |
| 06 | Explicitly injected duplicate HTTP request for test purposes | Second returns `ALREADY_CONFIRMED`, same receipt, exactly one effect. Not an authorized Product retry |
| 07 | Two concurrent independent HTTP client subprocesses submit same attempt | One `APPLIED_ACK`, another `ALREADY_CONFIRMED`, same receipt, exactly one SQLite effect |

The original Actions log reported `TS_EE_LLM047=PASS_BOUNDED_REAL_TCP_ACK_DROP_RECOVERY;tests=7;Product=NONE;provider=LOCAL_SQLITE_HTTP_MOCK`; total native tests completed in approximately 1.820 seconds (excluding queue/build).

## Evidence boundaries / remaining debt

- This is a **real localhost network socket and separate processes**, but the provider is an explicitly synthetic SQLite HTTP server, not an external LLM/model provider. Localhost test cannot demonstrate distributed durability, real network partitions, multi-machine coordination, TLS, authentication, provider contracts or failover.
- `synchronous=FULL` configured; physical power-cut crash, storage controller failure, arbitrary race/interleaving or privileged-writer bypass were not qualified. Separate host/network fault injection remains future work if technically relevant.
- The "one effect" invariant here follows the synthetic provider's `attempt` primary key and transaction. A real provider **without** an idempotent native operation or authoritative receipt cannot be assumed equivalent.
- No OpenCode inference was dispatched in 047; no global model comparison; earlier native model JSONL portable transport limitation remains unresolved.
- Original artifact expires in 30 days. Retain original raw evidence before 2026-11-29 if ongoing audit needs it; Git/Library summaries alone are insufficient.
- No Product changes. The Tecnotron `tools` branch was observed at `bc9e60b9cad79037b40c298d5c9a84f17a33d909` before the experiment; re-observe competent SOT for any future Product gate.
- Next optional experimental frontier: provider **without** native idempotency or authoritative status, plus external network partition simulation, to find the fail-closed boundary and prevent false exactly-once claims, rather than adding a new kernel/scheduler by default.
