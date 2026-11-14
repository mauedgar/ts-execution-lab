# TS EE — Orca Bridge IR001 4F/5A: bounded source repair R002

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.  
**Date:** 2026-11-14. **Authority:** TS Developer Lab experimental, Product NONE.  
**Original A001:** terminal `CONFIRMED_EXECUTED / FAILED_SEMANTIC_CONFORMANCE`; NEVER replay.  
**Bridge IR001:** `NO_RECOMMEND / 4F / 5A`, Review_ID `TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001`, independently reviewed commit `3f9db9086cc11e0ca01affff92738c89d28f4bf8` (tree `ffb70e4f3945f260e22b3d22af1c57e6d596b52d`).  
**IR ORIGINAL custody:** `mauedgar/ts-execution-transport@4ae785f79b5c2d295ee75683f6cfaf4bd4a7684f:results/TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001/ORIGINAL.md`, 12,512 UTF-8 bytes, SHA256 `996afe049e456428aef6bb8cecc668220eda0d38a57634b749c04733234f997e`, verified exact after create-only publication.

## Reuse and bounded implementation

Preserved original `ORCA_NATIVE_BRIDGE_A001_RUNNER.ps1` as an immutable historical effect. No destructive rewriting or retry of A001.

Created **source-only** repair artifacts in this isolated lab branch:

1. `tools/ts_ee_orca_jsonl_receipt_v2.py` at Git blob `982745211cf2ed5e8b805a4a527bdfab691b6749`. A deterministic postprocessing-only checker: validates bounded UTF-8 JSONL, duplicate object keys, final event, exact session identity, complete LF, create-only receipt, original size/digest, tool names and reported cost. Never launches a model or judges semantics. Its cost and model fields are explicitly **claimed/provider-reported**, never independently billed/verified.
2. `test/ts_ee_orca_jsonl_receipt_v2_test.py` at Git blob `a2286a636d89587e4f15766438c7b1646b184618`, 16 bounded synthetic tests for valid completion, unexpected edit tool, digest mismatch, malformed JSON, duplicate keys, mixed sessions, missing terminal event, nonfinite/oversized cost, truncated LF, provider nonzero, OpenAI ID rejection, receipt collision, path traversal, nonexistent receipt parent and unknown-event preservation.

**Actual deterministic test execution** in an isolated local container with Python 3.13.5 and Git 2.47.3. The copied test subjects were verified byte-for-byte against the exact Git blob hashes above using `git hash-object` **before execution**. `python -m py_compile` on the parser PASS. `PYTHONPATH=/tmp/ts_ee_orca_verify/tools python -m unittest discover -s /tmp/ts_ee_orca_verify/test -p '*test.py' -v` returned **16 tests / 16 PASS / 0 FAIL**. This is a synthetic deterministic test, **NOT** a notebook OpenCode2/Orca run or Product gate.

## Finding-specific disposition

| Finding from independent IR001 | Current bounded status | Remaining gate |
| --- | --- | --- |
| F01 effective provider/tool policy not attested in runner | `OPEN_RUNTIME`; source config already has prior static/native inspection, but no independent empirical denial matrix | Separate explicit native negative permission test under new authority, actual model-free + model-side calls distinguished |
| F02 original JSONL/terminal evidence incomplete | `PARTIAL_SOURCE_REPAIR`; staged parser & create-only evidence receipt, 16/16 tests; **not integrated** in a qualified V2 runner | Verify terminal/exit/receipt correlation, stderr separation, parser on bounded real original in private custody and independently reviewed runtime |
| F03 replay/immutable carrier not guaranteed | `OPEN_RUNTIME`; old runner remains frozen, no new run; Git blob/version and A001 receipt preserved | Independent create-only launch ledger with native terminal incarnation, exact request/prompt/script hashes, anti-replay and cross-worktree exclusion |
| F04 session/provider billing and isolation uncertain | `OPEN_RUNTIME`; no paid fallback authorized, but zero provider-reported cost is not bank/account reconciliation | Native host lease, exact provider/auxiliary effective routing, account-level free/price evidence; do not spend paid quota |

**A01–A05** are preserved as advisories, not silently erased. The 399,890-byte A001 ORIGINAL remains private on notebook and was NOT copied to public GitHub; IR001 therefore classified full runtime as `BLOCKED_EVIDENCE`.

## Reviewer modality is a competent CHOICE, never a default

This repair does not select OpenCode2, WEB_INLINE, Actions or any other harness for future Product reviews. The per-responsibility competent Control chooses a binding if review is required, under the Product SOT and actual independence/cost constraints. The optional profile `OPTIONAL_PRELIMINARY_REVIEWER_CANDIDATE.md` remains `PREPARED_NOT_QUALIFIED / NOT_DISPATCHED`, not an A002 authority.

## Stop boundary and next possible gates

- **No semantic rerun, no Actions activation, no Product write, no integration into main**. The F02 checker is a source-level tool candidate, not yet a reusable runtime Recipe/Primitive.
- The next safe gate is a separate **WEB_INLINE source-only code IR** of just the checker/test and this bounded disposition. Do not ask it to assess the missing private A001 ORIGINAL or declare the full bridge 0F/0A. On 0F/0A source-only, evidence may be curated as an experimental helper while F01/F03/F04 remain open.
- Any new notebook synthetic reviewer or native live denial canary requires its own competent Developer ruling, attempt identity and frozen subject. Do not infer retry authority from source repair.
- A runtime bridge qualification stays `NO_RECOMMEND` until all four F are actually closed with appropriate evidence. Preserve the IR001 source and result exactly.

**Current state:** `R002_SOURCE_F02_PARTIAL_16_16_PASS / BRIDGE_RUNTIME_4F5A_NO_RECOMMEND / PRODUCT_EFFECT_NONE`.
