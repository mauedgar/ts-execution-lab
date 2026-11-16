# TS EE R005 — Exact POSIX test execution receipt A001

**Date:** 2026-11-16 (Argentina local).
**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`.
**Test Operation:** `TS-EE-R005-POSIX-TEST-OP001`.
**Test ExecutionAttempt:** `TS-EE-R005-POSIX-TEST-A001` — terminal PASS, one dispatch, no retries.
**Original A001 OpenCode inference attempt:** Historical and terminal; **NOT REPLAYED**.
**Authority:** TS Developer Lab experimental only, `Product_authority=NONE`, `Product_effect=NONE`.
**Disposition:** `EXACT_SOURCE_POSIX_TESTS_PASS_55_OF_55 / SOURCE_IR_0F5A / FULL_RUNTIME_BRIDGE_NO_RECOMMEND`.

## Immutable candidate and materialization

- R005 frozen Git source commit: `mauedgar/ts-execution-lab@74e98c436b62e199b5f109bad0eff947c7134a61`, source tree `17674f4abb8c0540b21f9ba664ba5a1399effd0f`.
- Python checker `tools/ts_ee_orca_jsonl_receipt_v5.py`: exact Git blob `9fd047bdb3c7ba1a9fdc4f160d8d281d1b0a0bf7`.
- Regression tests `test/ts_ee_orca_jsonl_receipt_v5_test.py`: exact Git blob `4cd97cefc425ceab76ce121b82007189ac8e8d24`.
- Notebook `DESKTOP-DJLBEQH` (authorized Orca host). One Git fetch of frozen experimental branch into existing TS EE git store; mechanical PID `6832` finished exit 0, updating origin/experiment to `38c86f80734c744eabf642d29dc2a309eb7c89f3`. No Product branch was touched.
- Orca native worktree create, mechanical PID `4620`, native receipt `5d0d22fa-e214-47e0-95c7-acfd034e971c`, `ok=true`, `warnings=[]`. New isolated worktree `de17644d-bbf9-4c3b-b6be-52b51954e854::C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-r005-posix-tests-20261116-001`, identity `wt2:local:4cfb9f54-4ce0-4715-9187-cb920a10ccce`, setup SKIP, no agent, parent NULL, not main worktree. Its checked-out HEAD `38c86f80734c744eabf642d29dc2a309eb7c89f3` is a descendant of the frozen candidate and **not** misrepresented as the frozen subject commit.
- Critically, the two actual files in that worktree were rehashed by native `git hash-object` (mechanical PID `14528`): exactly the two expected blob identities above **before tests ran**. Execution claims bind to these actual source bytes, not solely the descendant checkout HEAD.

## Exact native POSIX execution

- WSL distribution `Ubuntu-24.04`, Python `3.12.3`, test temp filesystem `/tmp` on `ext4` (`/dev/sdd`, verified with `df -T /tmp`, mechanical PID `14804`).
- Tests imported the checked-out, hash-verified source through WSL `/mnt/c/.../ts-ee-r005-posix-tests-20261116-001`; each `tempfile.TemporaryDirectory` fixture used Linux's default `/tmp` native ext4, not Windows NTFS. Python `-B` disabled bytecode writes in the checked-out tree.
- Single noninteractive bounded test command from the authorized device:
```text
wsl.exe -d Ubuntu-24.04 -- python3 -B -m unittest discover -s /mnt/c/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-r005-posix-tests-20261116-001/test -p ts_ee_orca_jsonl_receipt_v5_test.py -v
```
- Original mechanical PID `14640`, terminal native receipt `Process completed with exit code 0`; **55 of 55 tests PASS, 0 FAIL, 0 ERROR, 0 SKIP**, unittest-reported duration `0.660 s`.
- Provider-native Commander observation (original terminal output, not independent IR and not GitHub Actions) archived **byte-identically after readback**: `mauedgar/ts-execution-transport@97fb6c5c7fd6180bed071f36621507ca1e8edd0c:results/TS-EE-R005-POSIX-TEST-A001/TERMINAL_OBSERVATION.txt`, Git blob `b45f4625c4ce4d7b01d196a64dad73d7f9d785ed`; the observed text contains all 55 named test records plus `Ran 55 tests in 0.660s`, `OK` and exit-code-0. No fabricated success.
- The same isolated worktree was subsequently checked with native `git status --porcelain=v1 --untracked-files=all` (PID `14776`); exit success and empty output: **CLEAN**. Test fixtures were isolated in WSL ext4 temporary directories.

## Bounded qualification, no authority promotion

- An independent WEB_INLINE IR on the frozen R005 source had already concluded `RECOMMEND_SOURCE_ONLY / 0 blocking findings / 5 advisories`, Review_ID `TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001`. Its 9,074-byte ORIGINAL resides at `mauedgar/ts-execution-transport@2c7852dd458983300f769f89b4d68bc3fb9bab27:results/TS-EE-ORCA-JSONL-V5-POSIX-WEBINLINE-IR001-20261116-001/ORIGINAL.md`, blob `ced0461d5ed581163120da419e6fea728af9f487`, SHA256 `86d4d2debb46259948a56b9fe71d101e118e0de5f26c6b11d37b5b6db2306106`.
- A02's prior **test-not-executed evidence gap is now satisfied for these exact source blobs** by the concrete POSIX execution above. Other advisories A01/A03/A04/A05 and the constraints of actual provider provenance, sticky/race adversarial coverage, metadata privacy, same-UID/privileged actors and non-POSIX portability are NOT silently closed.
- This gate qualifies the R005 helper for **isolated experimental POSIX source/test use with recorded limitations**, not as a production or Product-level integration, nor as a complete semantic OpenCode2 reviewer or Orca runner qualification. **The full Commander→Orca bridge retains `NO_RECOMMEND / 4F / 5A`**. Historical OpenCode2 semantic A001 remains terminal `FAILED_NONCONFORMANT`; its private 399,890-byte ORIGINAL has not been independently published. A passing helper cannot close it.
- `MODEL_CALLS=0`; `OPENCODE2_LAUNCHES=0`; `ACTIONS_RUNS=0`; `PRODUCT_EFFECT=NONE`. Commander used solely to mechanically fetch/version a separate TS EE worktree, invoke the fixed pre-existing deterministic Python tests, and return compact native results. No Commander repository source inspection, Product modification, semantic analysis or script construction.
- Reviewer binding remains explicitly chosen by competent Control per responsibility: WEB_INLINE, OPENCODE_LOCAL or another qualified medium, never a canonical default.

**Terminal classification:** `R005_SOURCE_TEST_GATE_PASS_55_55 / EXPERIMENTAL_POSIX_QUALIFIED_WITH_ADVISORIES / FULL_BRIDGE_NOT_QUALIFIED`.
**Next possible separate gate:** decide whether to validate this helper against the historical A001 JSONL in trusted private custody with no public original exposure, including native terminal correlation and explicit privacy checks. Such work cannot be inferred as safe or authorized from this source-only test receipt alone.
