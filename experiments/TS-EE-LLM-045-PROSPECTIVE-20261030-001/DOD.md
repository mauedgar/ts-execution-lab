TS EE LLM045: Prospectively frozen two-case x two-model benchmark
Authority: EXPERIMENTAL_CONTROL_ONLY; Product NONE, #34/#35 untouched.
Case A recoverAttempt: adversarial partial effect / UNKNOWN; Case B selectReady: dependency DAG.
Source and independent oracle must be committed to Git before model inference.
Each model gets its own clean worktree and a single allowed edit to one case source, reads only WORK_PACKAGE.md, source and visible tests. No shell, web, git, delegation or other path.
Four independent ExecutionAttempts, exactly one launch each, unique native event JSONL. Validate tests independently in GitHub Actions on exact candidate commits, preserve both PASS and FAIL.
Benchmark DoD: frozen original+hidden test blobs, baseline RED, native session, strictly owned diff, Git clean on candidate, independent 7+8 tests for each case, original logs hashes, no automatic retry UNKNOWN. This is a pure synthetic experiment and not a Product scheduler or an authority promotion.
