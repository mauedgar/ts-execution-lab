# TS EE LLM 043 — Immutable four-attempt experimental dispatch request

**Source Git freeze:** `mauedgar/ts-execution-lab@8d565454ada52e873ab57d19cd5c9e036ebf41ca`. The Git branch may move later; do not silently update source worktrees or compare unequal baselines. Owner: `TS_EXECUTION_ENGINEERING`; Product authority NONE.
**Device:** DESKTOP-DJLBEQH, Orca project `github:mauedgar/ts-execution-lab`, OpenCode v2.1.0. Frozen DoD: `experiments/TS-EE-LLM-043-NATIVE-CODING-20261030-001/DOD.md`.
**Binding:** location `experiments/TS-EE-LLM-043-NATIVE-CODING-20261030-001/<role>` within each respective worktree; native `llm-coder` effective permissions must be checked separately in each. All four worktrees are separate and start on frozen Git subject. No automatic or silent fallback to a paid model, other model, v1, or different workspace. Model has NO `shell`; validator acts separately after the model.

**Prompt shared verbatim for each role:** `Perform the bounded synthetic task defined in WORK_PACKAGE.md. Read only WORK_PACKAGE.md, the designated src file, and the designated test file. Change only the designated src file using native edit/write. Do not run shell, tools outside permissions, tests, web or git. Do not claim tests passed; describe actual edit or BLOCKED.`

| Attempt | Orca worktree name | Role location | Model | Sole allowed source |
| --- | --- | --- | --- | --- |
| `LLM043-D-I-001` | `llm043-d-i-001` | implementation | `opencode/deepseek-v4.1-flash-free` | `src/aggregate.mjs` |
| `LLM043-M-I-001` | `llm043-m-i-001` | implementation | `opencode/mimo-v2.6-flash-free` | `src/aggregate.mjs` |
| `LLM043-D-R-001` | `llm043-d-r-001` | repair | `opencode/deepseek-v4.1-flash-free` | `src/select-latest.mjs` |
| `LLM043-M-R-001` | `llm043-m-r-001` | repair | `opencode/mimo-v2.6-flash-free` | `src/select-latest.mjs` |

**Invocation shape:** `opencode2 run --standalone --format json --agent llm-coder --model <exact> --title <attempt> '<prompt-above>' | Tee-Object -FilePath C:/TS/station/<attempt>.jsonl`. No `--auto`; no `--continue`. Only one Orca terminal dispatch per exact Attempt.

**Independent validation after terminal:** `node --test tests/aggregate.test.mjs` for implementation, `node --test tests/select-latest.test.mjs` for repair. Take `git status --porcelain` and `git diff --name-only`, must show exactly one bounded target (or none on FAIL). Hash original JSONL and tests; store session ID, tool event types and exit. Never run tests from agent itself.

If any attempt is already RUNNING, do not dispatch again. Missing final `step_finish` without other effects is completeness limitation, not automatic model fail; missing terminal evidence yields `UNKNOWN`. Do not change owner, source or write grant in response to a model request. Preserve exact original JSONL host paths. No Git publication of raw logs while private transport block remains unresolved.
