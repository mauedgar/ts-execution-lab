# R007 B1 — Orca file-profile provider admission observation (2026-11-18)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001` (same line, Product authority NONE).
**Observation:** `B1_FILE_CONFIG_SOURCE_VERIFIED / NATIVE_MODEL_CATALOG_PROVIDER_FENCE_PASS / AGENT_EFFECTIVE_PERMISSIONS_UNRESOLVED / MODEL_INFERENCE_NONE`.
**Historical A001:** terminal semantic nonconformance, untouched and never replayed. All new commands below were model-free native preflights; no Actions/paid/model dispatch or Product effects.

## Actual cause and controlled repair

The 2026-11-18 read-only candidate `OPENCODE_CONFIG_CONTENT` debug-config comparison returned only two native policy entries and mismatched all model/role values. **It was not a valid effective-policy oracle**: V2 `debug config` lists sources, rather than a fully resolved effective configuration, and upstream V2 also reports ignored/misapplied inline configuration. Preserve that negative observation as inconclusive, not proof the provider was unsafe.

- The exact strict-free candidate was added to the **file-based** experimental runroot at `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_CLOSED_CONTEXT_RUNROOT/opencode.json`, Git blob `16ed6e50bddf955db6f27484624b47cbe762fb3b` (byte-for-byte equal to the original candidate).
- A versioned, source-only `R007_B1_FETCH_REF_A001.ps1` was frozen with corrected Git blob `f94a8fb26da156dac79aa22a3086c122cdec3d58`. One bounded delivery into the existing Orca **Control** terminal `term_652daa83-f247-48a8-ae5f-adfb4f771c93`, incarnation `ecb4f236-ccfd-4c48-b46e-f6505432702a`, input request `d0faf8bf-d707-4b1b-8a6d-63586a7ba62f`. Native screen showed `R007_B1_FETCH_A001_PASS`. Historical A001 checkout HEAD was asserted unchanged; fetched exact branch head `2c58013476d09eb63839f8ebb604c1954473f695`. No new inference.
- Native Orca create-only materialization succeeded with receipt `0442e99b-a35a-4834-9c0b-cf3dd0d7b9f8`, warnings `[]`, and exact new worktree `de17644d-bbf9-4c3b-b6be-52b51954e854::C:/Users/Mauri/orca/workspaces/ts-ee-llm040-source-20261030-001/ts-ee-oc2-r007-b1-file-config-20261118-001`; verified HEAD `2c58013476d09eb63839f8ebb604c1954473f695`. No setup or agent launch.
- Native Experiment terminal for this NEW worktree: `term_c763c655-b52b-4c6a-ab04-de5cd2538e05`, incarnation `3128fc7e-f5ee-4f52-a6da-6bc0ac523f1c`.

## Distinct native file preflights

1. An isolated file source/effective-comparison candidate `R007_B1_FILE_POLICY_PREFLIGHT_V1.ps1`, Git blob `5ef35dfecc4ea86dd368019a036ef933c18f6b65`, was sent once (request `16e3d355-53e5-4552-99a3-426aa7943adc`) and returned `POLICIES=False;GLOBAL_DENY=False;MODELS=False;ROLES=False` and `BLOCKED_NATIVE_EFFECTIVE_POLICY_MISMATCH`. This compared a V2 **source enumeration** to a literal candidate object and is **NOT a valid runtime deny-policy oracle**. It did prove the exact worktree, exact Git config blob, installed shim SHA and v2.2.5 version gates passed before reaching debug config.
2. Corrected *read-only* native inspection `R007_B1_NATIVE_SOURCE_AGENTS_MODELS_V2.ps1`, Git blob `1f1bd7420e917c14febf778bd3ebd7d58554842d`, was sent once from Orca Experiment (request `62e6bfed-7c99-41e2-a0f0-8f8b39699555`, same incarnation). Native screen reported:
   - `R007_B1_NATIVE_V2_CONFIG;JSON=True` — the returned JSON is array-shaped, not a resolved effective model/policy document.
   - `R007_B1_NATIVE_V2_AGENTS;JSON=True;PLAN_MENTION=True;MODEL_MENTION=False;DENY_MENTION=True;COUNT=481` — agent data are available, but the simple text oracle does not certify the resolved plan-agent deny matrix.
   - **`R007_B1_NATIVE_V2_MODELS;OPENCODE=12;OTHER_PROVIDER=0;PINNED=1`** — the standalone catalog from the isolated file-profile root exposes only `opencode/` models; specifically the pinned `opencode/deepseek-v4.1-flash-free` exists, while all other provider namespaces are absent.
   - `R007_B1_NATIVE_V2_TERMINAL_NO_INFERENCE`. The script checked exact HEAD and config Git blob before catalog calls.

Separate native `opencode2 auth list --format json` returned 8 credential-bearing non-OpenCode integrations and **no connected `opencode` account**. No credentials were changed. Official model pricing currently lists DeepSeek V4.1 Flash Free at FREE but time-limited, not a perpetual billing guarantee.

## Disposition

**PASS:** isolated worktree/source binding, file config Git identity, native provider catalog fence (12 `opencode/`, zero outside), candidate model presence. This is not a model call or an invoice attestation.

**Still BLOCKED:** full native `plan` deny-all resolved permission/policy matrix, full real OpenCode binary identity, create-only cross-worktree attempt ledger, original/stderr separation and durable native terminal receipt, grouped source IR before B2. No model dispatch until these requirements are met.

**Product effect:** NONE. No default reviewer binding, no A001 retry, no credential or global-installation mutation.
