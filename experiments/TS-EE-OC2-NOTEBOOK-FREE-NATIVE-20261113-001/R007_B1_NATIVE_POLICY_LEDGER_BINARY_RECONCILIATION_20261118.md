# TS EE R007 — B1 provider, effective agent, ledger and executable reconciliation

**Control:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`; source-only experimental evidence, `Product_authority=NONE`, `Product_effect=NONE`.
**Date (Argentina):** 2026-11-18. **Disposition:** `B1_NATIVE_PROVIDER_FENCE_PASS / B1_NATIVE_AGENT_DENY_PASS / B1_LEDGER_SYNTHETIC_4_4_PASS / B1_FULL_BRIDGE_AND_GROUPED_IR_PENDING`.
**Zero new semantic provider inference. No A001 replay. No credential or Product writes.**

## Native admission and identity evidence

Native notebook: `DESKTOP-DJLBEQH`. Isolated NEW Orca worktree `ts-ee-oc2-r007-b1-file-config-20261118-001`, frozen checkout HEAD `2c58013476d09eb63839f8ebb604c1954473f695`; Orca Experiment terminal `term_c763c655-b52b-4c6a-ab04-de5cd2538e05`, incarnation `3128fc7e-f5ee-4f52-a6da-6bc0ac523f1c`.

1. Exact config-file blob `16ed6e50bddf955db6f27484624b47cbe762fb3b`; native `models --standalone` from its directory yielded `OPENCODE=12;OTHER_PROVIDER=0;PINNED=1` for `opencode/deepseek-v4.1-flash-free`. The historical `OPENCODE_CONFIG_CONTENT` `debug config` literal comparator was an invalid effective-policy oracle; it must not be claimed as demonstrated native insecurity.
2. Native `debug agents --standalone`, frozen source `R007_B1_NATIVE_PLAN_PERMISSIONS_V3.ps1` blob `df9c22f8efa40b88d16e25710637e68d1ce19e64`, one send request `38fbda0d-73bc-4daa-a12b-4c26c49d7b47`, original terminal readback:
   `R007_B1_PLAN_V3_SHAPE;COUNT=7;KEYS=id,name,request,description,mode,hidden,permissions;PLAN_FOUND=True`
   `R007_B1_PLAN_V3_RULES;COUNT=11;SHAPE=action,resource,effect;LAST_DENY_ALL_INDEX=8;ALLOW_OR_ASK_AFTER=0`
   `R007_B1_PLAN_V3_MODEL;MODEL=@{id=deepseek-v4.1-flash-free; providerID=opencode}`
   `R007_B1_PLAN_V3_PERMISSION_DENY_PASS_SOURCE_ONLY_NO_INFERENCE`.
   Previous immutable publication: `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_B1_NATIVE_PLAN_PERMISSIONS_RECEIPT_20261118.md`, Git blob `bd1a431a9f356cae7cc7455550af19a47b8be4ac`.
3. Native `opencode2 auth list --format json` showed eight existing non-OpenCode credential integrations, **no authenticated OpenCode integration**; none changed. The offer for the selected model is published as free but time-limited, not a permanent zero-invoice attestation.
4. One bounded read-only process observation of the running `opencode.exe` binary (PID `12948`), `SHA256=17531635C255D2DD70057B8D50564B829349EAE8C2946590CE355F003CB251E6`, `BYTES=259169160`. This is a process executable identity at that observation, **not yet proof that future private standalone starts from the same exact binary**. The separate CMD shim SHA remains `4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49`.

## New minimal create-only ledger: 4/4 native synthetic tests

Reused TS Execution Runner v0.2 request/result/receipt identity conventions. Its historical local launcher `devlab/execution-runner-v0-2-001:scripts/bounded-launch.cmd` (Git blob `824f52cee44aaa8545ec4621d6ed2996bd84cbcb`) only wraps a parse check and no-op worker; it does not provide cross-worktree single-attempt fencing.

Added source-only experimental helper `R007_B1_CREATE_ONLY_ATTEMPT_LEDGER_V1.ps1`, Git blob `a987ab797b069d2c9db616c2c5798efbba6add1d`. Its test `R007_B1_LEDGER_SYNTHETIC_SELFTEST_V1.ps1`, Git blob `14e43bb2ab8a66833a95d1f31de03f60fd611c64`, was delivered once as a fully built carrier to the same Orca Experiment terminal. Native send `2be7a869-f661-47ad-8a61-0443371df510`, `accepted=true / replayed=false`, was independently joined via exact native terminal screen.

Observed native terminal markers:
```text
R007_LEDGER_TEST_BEGIN
R007_LEDGER_TEST_FIRST_PASS
R007_LEDGER_TEST_DUPLICATE_BLOCKED_PASS
R007_LEDGER_TEST_SECOND_PASS
R007_LEDGER_TEST_UNKNOWN_FENCE_PASS
R007_LEDGER_TEST_TERMINAL_4_OF_4_PASS_NO_MODEL
```
The separate one-off **synthetic** ledger root is `%TEMP%/TS-EE-R007-LEDGER-SYNTHETIC-001`. It intentionally retains the third simulated `UNKNOWN` claim without a terminal, and the fourth attempt was not claimed. **Do not retry** this synthetic attempt or clean its evidence merely to rerun. This is not the production ledger root; no model was invoked. The helper uses a single-host same-user named mutex while the bounded operation runs, cross-worktree exact create-only claim identity and durable terminal receipt. It has NOT undergone independent security/source IR, hostile-user ACL testing or actual provider-model launch.

## Remaining qualified boundary

The original policy/provider uncertainty is substantially resolved by real native preflights, without paid-provider usage. **B1 overall remains incomplete** because (a) the final new Orca-native full runner/manifest with exact source/hash, separate immutable raw JSONL and stderr capture, R006 POSIX raw checker and native receipts has not yet been built/tested; (b) cross-process/provider-wide conflict exclusion, filesystem trust/ACL and full binary binding during private standalone launch need an exact final gate; (c) grouped `IR-SOURCE-BATCH` is not performed. The new ledger test PASS is not a general security claim. B2 three semantic attempts and B3 behavioral IR remain NOT_DISPATCHED/NOT_STARTED.

**Stop condition:** no model inference, no paid fallbacks and no Product use until complete B1 and competent single grouped source review. OpenCode2 remains an optional, unqualified reviewer method. Do not reactivate historical A001.
