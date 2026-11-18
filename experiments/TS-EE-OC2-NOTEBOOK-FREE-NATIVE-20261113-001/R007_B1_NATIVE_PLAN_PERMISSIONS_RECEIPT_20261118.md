# R007 B1 native plan permission observation — 2026-11-18

Responsibility: `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`. Non-Product experimental mechanics only; `Product_effect=NONE`.

## Exact source and native execution identity

- Source: `mauedgar/ts-execution-lab@33714ba7c250e45c544642c75dfffe61d2d9b561:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_B1_NATIVE_PLAN_PERMISSIONS_V3.ps1`; Git blob `df9c22f8efa40b88d16e25710637e68d1ce19e64`.
- New isolated Orca worktree: `C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-oc2-r007-b1-file-config-20261118-001`, frozen checked-out Git HEAD `2c58013476d09eb63839f8ebb604c1954473f695`. No checkout transition or Product effect.
- Native visible Orca Experiment terminal: `term_c763c655-b52b-4c6a-ab04-de5cd2538e05`, incarnation `3128fc7e-f5ee-4f52-a6da-6bc0ac523f1c`, notebook `DESKTOP-DJLBEQH`.
- Create-once native Orca terminal send request ID `38fbda0d-73bc-4daa-a12b-4c26c49d7b47`, accepted=true, replayed=false. Delivery support is unavailable in Orca; follow-up exact terminal screen read confirmed execution markers and result without re-sending.
- Exact observed output, no semantic model inference:

```text
R007_B1_PLAN_V3_START
R007_B1_PLAN_V3_SHAPE;COUNT=7;KEYS=id,name,request,description,mode,hidden,permissions;PLAN_FOUND=True
R007_B1_PLAN_V3_RULES;COUNT=11;SHAPE=action,resource,effect;LAST_DENY_ALL_INDEX=8;ALLOW_OR_ASK_AFTER=0
R007_B1_PLAN_V3_MODEL;MODEL=@{id=deepseek-v4.1-flash-free; providerID=opencode}
R007_B1_PLAN_V3_PERMISSION_DENY_PASS_SOURCE_ONLY_NO_INFERENCE
```

Earlier same-root native `models --standalone` preflight reported `OPENCODE=12;OTHER_PROVIDER=0;PINNED=1`; source/control evidence previously preserved at `mauedgar/ts-execution-lab@51e8f12d06d522914c0f5592e47dcbc3ed74b48f:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_B1_FILE_NATIVE_PROVIDER_OBSERVATION_20261118.md`.

## Qualification boundary

**PASS at B1 native admission observation:** isolated source and provider model binding; `plan` resolved permission array has an explicit wildcard deny-all and no later `allow` or `ask`; selected model is `opencode/deepseek-v4.1-flash-free`. This directly corrects earlier mistaken assumptions from `debug config` (source listing, not effective policy), which remain historically inconclusive rather than an effective-enforcement failure.

**Not demonstrated by this source-only no-inference observation:** a hostile denied-tool canary, permanent zero invoice/account billing attestation, full binary-package SHA, host-wide atomic attempt ledger, new complete runner with separate JSONL/stderr and UNKNOWN-preserving terminal receipts, grouped IR of the final source batch, or three semantic cases. Do not infer any of those PASS states.

**Effect:** `NATIVE_DEBUG_PREFLIGHT_CONFIRMED / NEW_SEMANTIC_INFERENCE=NONE / PRODUCT_EFFECT=NONE`. Historical A001 was not retried. No global credentials/settings changed. OpenCode2 remains optional and not qualified as reviewer.
