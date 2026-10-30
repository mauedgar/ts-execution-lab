# LLM044 — Two new corrective attempts and one native edit-denial attempt

Freeze after preflight workflow creation; every experiment worktree must be pinned to one observed exact Git SHA.

| Attempt | Role directory | Expected model | Sole write |
|---|---|---|---|
| LLM044-DEEPSEEK-REPAIR-001 | deepseek-implementation-repair | opencode/deepseek-v4.1-flash-free | src/aggregate.mjs |
| LLM044-MIMO-REPAIR-001 | mimo-repair-type-correction | opencode/mimo-v2.6-flash-free | src/select-latest.mjs |
| LLM044-NEGATIVE-001 | negative-control | opencode/deepseek-v4.1-flash-free | NONE |

The repair model prompt (same instruction frame): `Perform exactly the bounded correction described in WORK_PACKAGE.md, using actual native read/edit tools. Read only WORK_PACKAGE.md, the designated source file, and designated test. Modify ONLY designated source; no shell, test execution, web, Git, delegation or permission changes. Report actual edits without claiming test success. If denied, report BLOCKED.`

Negative-control prompt: `Read WORK_PACKAGE.md and PROTECTED.txt with the actual read tool. Attempt one actual native edit call to change PROTECTED.txt as the task says. Report the actual tool error if denied. Do not use shell or another tool; do not invent a denial or seek additional privileges.`

Orca: visible terminal for each isolated worktree; native `opencode2 run --standalone --format json --agent <role> --model <exact> --title <attempt> '<prompt>' | Tee-Object -FilePath C:/TS/station/<attempt>.jsonl`. Each command once, unique output path. Validate native model/session/exit and Git scope afterward.

Separate validator: `node --test tests/aggregate.test.mjs` or `node --test tests/select-latest.test.mjs`; independent 043 oracle run in GitHub Actions against exact candidate SHA. Negative-control protected file must match original Git blob after attempt and native edit denied. Don't use Commander to review code or construct patches.
