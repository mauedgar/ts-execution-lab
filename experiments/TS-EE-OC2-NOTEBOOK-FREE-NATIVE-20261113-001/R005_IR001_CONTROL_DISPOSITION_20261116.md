# TS EE — R005 IR001 control reconciliation and qualification boundary

**Date:** 2026-11-16 (Argentina local).  
**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.  
**Developer grant:** Continue the next bounded experimental dependency; no Product authority or Product effects.  
**Original review identity:** `TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001`, `TS-EE-ORCA-JSONL-V5-IR001-A001`.  
**Original native Automation run:** `7206b112-2020-8333-98ea-a40acac9debe`, terminal `completed`, started `2026-11-16T03:39:52.241796Z`, completed `2026-11-16T03:41:15.380512Z`, no repeats.  
**Independent verdict:** `RECOMMEND_SOURCE_ONLY / 0 blocking findings / 5 advisories`.  
**Control disposition:** `R005_SOURCE_IR_RECOMMENDED_NOT_OPERATIONALLY_QUALIFIED / DETERMINISTIC_TEST_RECEIPT_PENDING / RUNTIME_BRIDGE_NO_RECOMMEND`.

## Exact immutable subject

- R005 source commit: `mauedgar/ts-execution-lab@74e98c436b62e199b5f109bad0eff947c7134a61`, Git tree `17674f4abb8c0540b21f9ba664ba5a1399effd0f`.
- Parser `tools/ts_ee_orca_jsonl_receipt_v5.py`, Git blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`.
- Test file `test/ts_ee_orca_jsonl_receipt_v5_test.py`, Git blob `4cd97cefc425ceab76ce121b82007189ac8e8d24`.
- Original frozen request: `mauedgar/ts-execution-lab@8d055780b88bbc5dc08c925dea0155164a715068:reviews/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116/FROZEN_INPUT.md`.
- **Actual independent ORIGINAL** preserved in verified Library `libfile_acdb0442049c8191a82d727caa3ac28c` and copied byte-identically to `mauedgar/ts-execution-transport@2c7852dd458983300f769f89b4d68bc3fb9bab27:results/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001/ORIGINAL.md`; Git blob `ced0461d5ed581163120da419e6fea728af9f487`, UTF-8 byte_length `9074`, SHA-256 `86d4d2debb46259948a56b9fe71d101e118e0de5f26c6b11d37b5b6db2306106`. Local mounted ORIGINAL was independently hashed with `sha256sum` and `wc -c`; GitHub readback matched the file content.

## Independent finding reconciliation

R004 F01 (parent/ancestor directory integrity) and F02 (ambiguous descriptor closes after potential publication) are **RESOLVED_BY_SOURCE** under the source's stated POSIX/WSL same-UID/privileged-writer trust assumptions, according to independent IR001. The result is `0F/5A` only for the isolated checker **source**, not a runtime acceptance.

IR001 advisories:
- A01 provider/event identity and provenance unverified;
- A02 55 tests are defined but NOT executed; specific test fault-injection and import weaknesses;
- A03 no adversarial multi-UID sticky/rename race evidence;
- A04 receipt metadata privacy before sharing across trust boundaries;
- A05 stale v4 schema label in v5 and platform/provider limitations.

The ORIGINAL reports `tests_not_executed_by_IR=true`. No reviewer configuration is made canonical: WEB_INLINE, OPENCODE_LOCAL or another qualified mechanism remains a competent per-responsibility selection.

## Test execution boundary and honest outcome

Control attempted to bring frozen R005 Git sources into the isolated local Python 3.13.5 environment by fetching immutable public raw GitHub URLs. The environment's network fetch failed. The exact R005 parser/test sources are not mounted as files in this execution container, so Control **DID NOT execute** the 55 tests. Unrelated Library code files were materialized but their Git blob hashes did not match R005, and they were not substituted.

There is no truthful `55/55 PASS` claim and no authorization to activate GitHub Actions as a shortcut. The only completed independent source gate is WEB_INLINE `RECOMMEND_SOURCE_ONLY / 0F / 5A`; runtime qualified status is unchanged. The proper next dependency is materialization of the exact two Git-blobs onto a competent isolated POSIX test surface and a bounded deterministic test receipt with source hash, Python version, command, exit code, pass/fail counts, no model calls and no Product effects. Do not use Commander to explore repositories, write scripts or launch models. Do not repeat R005 IR001 or historical OpenCode2 A001.

## Standing limits / next gate

- R005 **experimental source candidate recommended but not operationally accepted** pending exact-source 55-test receipt and competent advisory disposition.
- Full Orca Native Bridge remains `NO_RECOMMEND / 4F / 5A`, with missing original runtime independent custody/provenance. A source-only helper cannot close runtime F01/F03/F04.
- No Model, OpenCode2, Orca, Commander, Actions, Product, merge or main effects from this dependency.
- Preserve `UNKNOWN` and all prior terminal identities. No blind retry.
- No automatic reviewer binding: the choice remains explicit per responsibility.

**Checkpoint:** `R005_IR001_TERMINAL_0F5A / ORIGINAL_GITHUB_PUBLISHED_VERIFIED / TEST_EXECUTION_BLOCKED_SOURCE_MATERIALIZATION / PRODUCT_EFFECT_NONE`.
