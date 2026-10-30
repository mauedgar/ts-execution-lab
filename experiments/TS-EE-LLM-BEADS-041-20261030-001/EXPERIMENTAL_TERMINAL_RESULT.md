# TS-EE LLM × Beads 041 — Terminal experimental result

**Disposition:** `PASS_BOUNDED_NATIVE_BEADS_ATTESTATION_JOIN_WITH_RAW_PROVENANCE_LIMIT` / `COMPLETE_WITH_LIMITATIONS`.
**Authority:** `EXPERIMENTAL_CONTROL_ONLY`; no Tecnotron Product grant, acceptance, #34/#35 effect, or Beads Product adoption.

## Original execution / identities

- Experiment: `TS-EE-LLM-BEADS-041-20261030-001`.
- Attempt: `TS-EE-LLM-BEADS-041-ATTEMPT-001`; **exactly one** GitHub Actions invocation, no replay.
- Executed branch/head: `mauedgar/ts-execution-lab:experiment/llm-beads-041-evidence-join-20261030-001@74f1ff9d62ecc60053ee341e7b370cc411e52d5e`.
- GitHub Actions [run 41075728548](https://github.com/mauedgar/ts-execution-lab/actions/runs/41075728548), job `124131256990`, attempt 1: completed/success.
- Original native receipt [artifact 12986757967](https://github.com/mauedgar/ts-execution-lab/actions/runs/41075728548/artifacts/12986757967) (`ORIGINAL_RESULT041.json`), file SHA-256 `3b7c3e04e47cb16aa398d7d8eef7ded7396e9b24a551982fc2e60b935157b68a`; artifact ZIP digest `sha256:bd1ddb8ff8d51c052a0b2242c2a85e27f22c259d272203dec1e5d6faa859fb60`.
- Original provider artifact expiry per GitHub: 2026-11-29 14:54:18 UTC. This Markdown is a durable index and interpretation, **not original receipt bytes**.
- Native implementation Git blobs: `native041.py@2910f65435fb9915c2d010fd14bf15090a7c05fc`; `EVIDENCE_ATTESTATIONS.json@9cb5a38ca3e3b5078a98cb924ecd4a98d225e17a`. Both frozen and verified by Actions before execution.
- Beads release `v1.3.1` and Dolt `v2.2.0` archives downloaded with SHA-256 verification. Disposable Git/Dolt environment; no Git remote; no shared DB, no external LLM request.

## Empirical checks

Original runner returned **19/19 checks PASS**. Readiness was verified at each stage through separate native CLI processes.

1. A newly constructed synthetic Beads graph initially made only `llm041-preflight` READY.
2. Host-observed E-002/E-003 attestations passed constrained shape/identity/hash/ref guards. No raw JSONL was present on runner.
3. Closing `preflight` exposed `llm041-deepseek` and `llm041-mimo` as distinct READY items while comparison remained BLOCKED.
4. For DeepSeek, Beads stored the model, original attempt ID, provider-native session, JSONL SHA-256 and `original_bytes_on_runner=false`. A fresh native show recovered the evidence reference. After closing DeepSeek, exactly MiMo remained READY; comparison stayed blocked.
5. For MiMo, the distinct evidence reference was stored and recovered similarly. After closing MiMo, precisely `llm041-compare` became READY.
6. Deterministic comparison preserved DeepSeek's final `step_finish` and MiMo's absence of that event / reversed read order. Neither is promoted to universal winner, and missing raw bytes are not treated as verified.
7. The synthetic comparison was closed; a new Beads CLI readback returned an empty READY set.

## Original model sources (reference-only)

- DeepSeek `opencode/deepseek-v4.1-flash-free`: attempt `TS-EE-LLM-DEEPSEEK-V41-ORCA-READONLY-20261030-001`; session `ses_e72eb16e0ffeNqN9R3vfceO5xz`; host-local JSONL SHA-256 `520E2783B4F037FD3C0410617BB8458202BA0EE8222F53A81CDCAC5F50F87842`.
- MiMo `opencode/mimo-v2.6-flash-free`: attempt `TS-EE-LLM-MIMO-V26-ORCA-READONLY-20261030-001`; session `ses_e72e93b7effenu1qENWyffsy5Y`; host-local JSONL SHA-256 `2F59A7C89CAFBA45D2EBBDE69C493802B80F9F604DB1502B13A46A7DBAC2BDEF`.
- The original E-002/E-003 host observations are indexed in ChatGPT Library `/TS — Tecnotron/Experimental Model Qualification/TS_EE_LLM_040_NATIVE_DEEPSEEK_MIMO_RESULT_20261030.md`.
- 041 **did not reproduce 040's original Beads instance**: it constructed a separate new disposable graph with its own attempt. 040 remains terminal and was not replayed.

## Architectural interpretation

`PASS_BOUNDED_NATIVE_EVIDENCE_REFERENCE_CONSUMPTION_AND_DEPENDENCY_JOIN` is demonstrated: isolated Beads can retain distinct experimental model-result refs and enforce the selected sequential comparison dependency.

NOT demonstrated: byte-for-byte revalidation of original Orca JSONLs inside the runner; durable raw JSONL transport to GitHub/Library; multi-host live model parallelism; full provider ACK-loss recovery; privileged writer confinement (028 bypass still open); global Product revision/hash-chain equivalence; model quality beyond one allowed/denied read experiment; native Product acceptance, Upper LC #35, or Beads adoption.

**Next priority recommendation:** preserve raw original JSONL via a narrowly authorized, original-hash-checking carrier before retention loss; then create a separate synthetic implementation/repair benchmark that tests real code changes, without integrating into Product. Avoid a new Kernel, scheduler, or task lifecycle.
