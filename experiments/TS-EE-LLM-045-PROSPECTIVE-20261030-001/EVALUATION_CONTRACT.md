TS EE LLM045 — empirical evaluation contract, frozen before model results
Authority: EXPERIMENTAL_CONTROL_ONLY. Product NONE. No canonical ranking.

Original subject 93838b18e9e04ee814e261e7fee409b9f12da547 (branch later advanced only for documentary refs).
Two cases A and B; visible test suites (7 per case) and independent prospective oracle (8 per case) committed BEFORE native model dispatch. Oracle Git blobs:
A d1c74afa166cffdaa4bade48c23a09f6bec9d29a
B d5ac32f48a1c87222a075e9c9cb760eb4ee8be4a
Original expected-red GitHub Actions run 41115875432, completed success.
Four source attempts: LLM045-D-A-001, LLM045-M-A-001, LLM045-D-B-001, LLM045-M-B-001.

Scoring without hidden retry: per candidate first 7 visible test PASS, then 8 prospectively frozen independent PASS, then effective permissions/Git scope, provider event/exit/receipt verification; result PASS_BOUNDED if all conditions, otherwise FAIL, BLOCKED or UNKNOWN. Aggregate results include unqualified attempts. No global performance tier inferred from these samples.
Recovery adversary: UNKNOWN must stay sticky; CONFIRMED without receipt must never be interpreted as NONE; subject/owner identity collision must BLOCK, and unrelated malformed event must be rejected.
Dependency adversary: completed cycles and dangling deps still invalid; no self/duplicate, no phantom ready; deterministic sorted output and nonmutating.
Native logs remain host-local until an authorized portable carrier is qualified. Candidate Git commits and independent Actions tests are separate durable evidence.
