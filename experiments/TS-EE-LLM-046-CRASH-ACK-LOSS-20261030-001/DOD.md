# TS EE LLM046 — Crash/ACK-loss durable reconciliation DoD (frozen)

**Authority:** TS_EXECUTION_ENGINEERING / EXPERIMENTAL_CONTROL_ONLY; Tecnotron Product authority and effects NONE. Do not touch #34/#35, upper lifecycle, canonical model routing, or Beads adoption. This is not a model inference benchmark.

**Exact source blobs before native execution:**
- fixture046.py Git blob 6c1f267ed4f2e92e377456ffd3263643af2bc689
- test046.py Git blob 1f5688e378d8239147b5f5d6d4c95c946835cd97

**Operation:** TS-EE-LLM-046-CRASH-ACK-LOSS-20261030-001
**ExecutionAttempt:** TS-EE-LLM-046-ATTEMPT-001; owner TS_EXECUTION_ENGINEERING; writer only disposable GitHub runner's RUNNER_TEMP/llm046-<run-id>, unique receipt expected RESULT046.json and unmodified SQLite DBs. Exactly one push-triggered Actions run; no retries on UNKNOWN.

**Mechanism:** separate Python subprocesses with SQLite WAL, synchronous FULL and BEGIN IMMEDIATE. Effect represented only by one row per attemptId, UNIQUE constraint. Client intent/journal in a different SQLite file, append-only rows. Provider crash is real subprocess os._exit(73) after commit and before ACK, or os._exit(74) before commit. No production provider, network, Beads or OpenCode involved. A request has attempt+subject+owner identity and a deterministic synthetic receipt.

## Six frozen acceptance scenarios

1. **Crash after commit / before ACK:** child returns code 73 with empty stdout, durable provider row survives new-process open, authoritative probe returns matching receipt, consumer observes UNKNOWN then NO_RETRY_CONFIRMED; one effect.
2. **Crash before commit:** child exits 74, row rolls back; provider unavailable yields UNKNOWN, authoritative absence yields ABSENT_REQUIRES_AUTHORITY, never automatic retry.
3. **Consumer loses ACK:** provider returned ACK but consumer intentionally discards it; later process reconciles exactly one effect without re-submitting.
4. **Attempt identity collision:** same attemptId with changed owner returns BLOCK_IDENTITY; no overwritten or duplicate effects.
5. **Explicit adversarial duplicate:** a test deliberately submits same provider request twice to check idempotency; second result ALREADY_CONFIRMED, same receipt and one effect. **This is not a Product retry after UNKNOWN.**
6. **Concurrent competing writers:** two provider subprocesses simultaneously submit the same identity; one applies and one returns ALREADY_CONFIRMED; exactly one row.

Every scenario verifies SQLite PRAGMA integrity_check for provider and consumer. Preflight code is syntactically valid; original result JSON and synthetic SQLite files must be retained as one artifact. CI must verify source Git blobs before launch, single attempt identity and exact run head. Runtime decision under failure is fail-closed, without automatic retries, elevated privileges or branch integration.

**Success:** six independent cases PASS, zero failures, stored SQLite + journal original artifacts, GitHub provider run completed/success with first attempt, exact receipt hash and content. **Limitations:** local mock provider, synthetic transactional row, not real remote provider ACK loss, no process power failure, no disk fsync durability proven beyond SQLite settings, no distributed quorum, no privileged bypass, no Product effect. Status must remain COMPLETE_WITH_LIMITATIONS despite a bounded PASS.

**Preflight provenance:** the author's first local execution of six scenarios timed out at concurrent case 06, while its first five scenarios reported PASS. An isolated execution of case 06 then passed; a later full local preflight passed six of six. These are local design preflights, not the GitHub Actions attempt/receipt. Do not hide the first timeout or interpret it as an original hosted run.

**Evidence preservation:** source in experimental Git, original CI artifact (SQLite and RESULT046.json), Library index; any raw model JSONL from earlier experiments remains separate, with transport limitations unchanged.
