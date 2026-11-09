# A11 — IR002 local repair: exact collision and proven PG16 lock overlap

Owner TS_EXECUTION_ENGINEERING / TS Remote State 002, **NONPRODUCT**. Previous A11 original reviewer IR002 execution run 42ed2470-6d14-8325-8f98-c453b7c608ec; verdict LOCAL_QUALIFIED_WITH_ADVISORIES, **0 blocking findings, 2 local advisories**. Prior candidate mauedgar/ts-execution-lab@63dfaf14021b480122ccaad92eba18286d79c096, original native GHA42552751718 attempt1 SUCCESS. This is a NEW isolated candidate, not retry of the original terminal run.

## Repairs
IR002-A01: Worker distinguishes the deterministic StorageRejected(MUTATION_COLLISION) in the actual bridge.apply call, emitting exactly {disposition:REJECTED_MUTATION_COLLISION,reason_code:MUTATION_COLLISION,effect:NONE_FOR_THIS_REQUEST}. The original receipt on the previously confirmed same ID is NOT declared NONE or removed. The test asserts this exact code and unchanged head/event/receipt counts. Unknown transport errors are still conservatively classified as POSSIBLE_DISPATCH and never retried.

IR002-A02: Actual PostgreSQL16 deterministic lock contender under an isolated synthetic role/DB:
- Original frozen Product JS on disposable shadow produces TWO different proposals for SAME global revision5/head and last hash, identities A10-PG16-LOCK-WRITER-A/B.
- Python opens independent backend A (writer), B (contender) and C (read-only observer). A starts a transaction and locks the real global head with SELECT ... FOR UPDATE; B calls pre-existing real bridge.apply() and waits on the same row; C verifies via pg_blocking_pids(B) contains A and pg_stat_activity(B).wait_event_type == Lock during positive contention.
- A applies its original JS proposal through bridge.apply inside its outer transaction and commits once; B then is rejected by original bridge with STALE_REVISION, no replay or mutation effect.
- Result after this test HEAD1/events6/receipts6/revision6, original JS new milestone A present, contender B absent. Every backend is on ONE GitHub Actions host, so **two physical hosts and remote Neon concurrency remain NOT_RUN**.
- Strict 5s readiness and 3.5s lock-overlap observation limits, max10s B completion, fail-closed errors. Test-only fixed synthetic PostgreSQL16 URI/user; no Neon Environment, no secrets and no Product effect.

Preserve prior IR001 seven local negatives, IPC classification and guarded SQL foreign-object inventory, and then guarded RESTRICT cleanup after six exact events and receipts. All old workflows were archived before this branch and native effects never replayed. One new push workflow is admitted exclusively for this isolated candidate and later archived. Future Independent Review IR003 must check evidence independently without forcing zero. Upper LC and TaskCycle Core semantics remain original JS, not rewritten in SQL. Product cutover NO_GO, remote A02 OPEN.
