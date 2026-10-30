TS EE LLM045 frozen execution request — EXPERIMENTAL ONLY
Original Git subject: mauedgar/ts-execution-lab@93838b18e9e04ee814e261e7fee409b9f12da547
Baseline original GitHub Actions run: 41115875432, first attempt, PASS_EXPECTED_RED.
Model host: DESKTOP-DJLBEQH / Orca native OpenCode v2, no paid fallback.
Case A recovery: native write only cases/recovery/src/recover.mjs in the respective worktree.
Case B ready: native write only cases/ready/src/ready.mjs in the respective worktree.
All four independent worker attempts start from exactly the same Git tree but separate worktrees:
LLM045-D-A-001 -> llm045-d-a-001 -> recovery -> opencode/deepseek-v4.1-flash-free
LLM045-M-A-001 -> llm045-m-a-001 -> recovery -> opencode/mimo-v2.6-flash-free
LLM045-D-B-001 -> llm045-d-b-001 -> ready -> opencode/deepseek-v4.1-flash-free
LLM045-M-B-001 -> llm045-m-b-001 -> ready -> opencode/mimo-v2.6-flash-free
Exact role-local prompt for all: "Perform the bounded synthetic task in WORK_PACKAGE.md. Read WORK_PACKAGE.md, src module, visible tests only; edit only the role-owned src module via native edit. Do not use shell, tests, git, web, delegation or any ungranted tool, do not modify test/config. Report actual edit or BLOCKED, never claim independent tests passed."
Invocation: opencode2 run --standalone --format json --agent bench-implementer --model <id> --title <attempt> '<prompt>' | Tee-Object -FilePath C:/TS/station/<attempt>.jsonl
Unique original JSONL outside all Git worktrees, absence checked before launch.
At completion: independent mechanical node --test tests/visible.test.mjs, git status/diff/commit only owned file, original native hash/session, original tests + prospectively frozen 8 hidden tests per case in GitHub Actions on exact original candidates. Never replay terminal or UNKNOWN attempt; preserve actual failures.
Effect class: synthetic code changes in separate experimental repo, no Product, no real partial external side effect, no Beads integration.
