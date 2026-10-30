# LLM 043 — REPAIR synthetic bounded coding experiment

**Authority:** EXPERIMENTAL_CONTROL_ONLY; no Product effects, no external repository modification.
**Allowed source write:** `src/select-latest.mjs` only.
**Available read:** `WORK_PACKAGE.md`, `src/select-latest.mjs`, `tests/select-latest.test.mjs` only.
**Required API:** `selectLatest` exported from the source module.
**Acceptance criteria:** inherit exactly the frozen functional contract from `TS-EE-LLM-042-IMPLEMENTATION-REPAIR-20261030-001/WORK_PACKAGE.md` and the adjacent frozen test suite. The local test suite is a complete working copy of the validated red baseline. Implement the smallest correct solution, including input validation, deterministic order and non-mutation. Do not modify tests.
**No shell** from the model, no npm installs, git push, web, delegation or access to other files. A separate mechanical runner will perform `node --test tests/select-latest.test.mjs` after the model returns. No self-approval, no Product authority.
