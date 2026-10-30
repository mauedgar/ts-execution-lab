# TS-EE LLM × Beads 040 — Empirical qualification of a native workgraph

- Evidence class: NONPRODUCT_EXECUTION_ENGINEERING_EXPERIMENT
- Authority: EXPERIMENTAL_CONTROL_ONLY; Product NONE.
- Exact frozen source / run head: `2164ca608bf8b2061ce963a5130d68385efaf9b1`.
- Experiment: `TS-EE-LLM-BEADS-040-20261030-001`.
- Attempt: `TS-EE-LLM-BEADS-040-ATTEMPT-001` — executed exactly once.
- Native GitHub Actions run: https://github.com/mauedgar/ts-execution-lab/actions/runs/41030172418 ; job `123977773276`, attempt 1, completed SUCCESS.
- Original native result artifact: https://github.com/mauedgar/ts-execution-lab/actions/runs/41030172418/artifacts/12964898068
- Artifact ZIP SHA-256 (provider metadata): `597e469b1fba7edcbc797a9f6abd141cbf34ba5df4cf119bfb52ceda50b6c775`.
- Original `ORIGINAL_RESULT040.json` SHA-256 (native job log): `719c3780162e73dfccbe99e95286fdbddf9f87a0973dd944db474a814e30d2b3`.
- Source script blob: `experiments/TS-EE-LLM-BEADS-040-20261030-001/native040.py@eaeb5233ed7271053c3365d775cd2d239fd6fcb0`.
- Runtime: pinned Beads v1.3.1 + Dolt v2.2.0 archives with SHA checks; disposable Git repository, no remote.

## Observed native outcome

`PASS_NATIVE_BFIRST_MODEL_QUALIFICATION_WORKGRAPH_READY`; 8/8 assertions PASS, job completed success.

Actual graph:
1. `llm040-preflight` is the only initially ready synthetic task.
2. Closing only this synthetic preflight exposes **two distinct ready tasks**:
   - `llm040-deepseek` for `opencode/deepseek-v4.1-flash-free`.
   - `llm040-mimo` for `opencode/mimo-v2.6-flash-free`.
3. `llm040-compare` depends on **both** and is not ready.
4. Native CLI fresh-process readback recovered the same ready set, and Git remained without remotes.

The runner printed:
```text
TS_EE_LLM_BEADS040=PASS_NATIVE_BFIRST_MODEL_QUALIFICATION_WORKGRAPH_READY;checks=8;ready=llm040-deepseek,llm040-mimo;Product=NONE;provider=NONE
TS_EE_LLM_BEADS040_RECEIPT_SHA256=719c3780162e73dfccbe99e95286fdbddf9f87a0973dd944db474a814e30d2b3
```

## Strict limits

This was **real Beads-native execution** but only a synthetic workgraph. No model was invoked; there is no LLM read/deny PASS, no competing writer race within this run, no multi-host concurrency, no live worker execution, no model comparison, no TaskCycle, Product acceptance, migration, shared Dolt write, or canonical adoption. Earlier independent Beads 035/038/039 evidence can support limited guarded-concurrency behavior, not universal write confinement; privileged bypass shown in 028 remains unresolved. GitHub Actions artifact retention is finite (provider listed expiry 2026-11-29). Native result bytes remain in the named original artifact; this Markdown is an indexed interpretation, **not** a replacement native receipt.

## Next independent gates

- Freeze a disposable synthetic read/deny fixture and effective OpenCode v2 tool permissions.
- One source-bound unique attempt for DeepSeek, one for MiMo, with real native read+deny traces and zero Product writes.
- Preserve actual model/provider session, original receipts, costs, errors, timestamps and versions.
- Only after both original qualifying results are reconciled should a separately authorized comparison proceed.
- Keep evidence in ChatGPT Library; Product incorporation only at the final reconciled Upper LC #34/#35 DoD, or earlier upon a specific competent Product consumer/authorization.

No changes to `mauedgar/tecnotron-ai`; no authorization to start #35.
