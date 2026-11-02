# TS Execution Engineering — Transporte OneDrive educativo + Taildrop v1

```yaml
artifact:
  id: TS-EXECUTION-TRANSPORT-ONEDRIVE-TAILDROP-v1
  owner: TS_EXECUTION_ENGINEERING
  kind: CANONICAL_EXECUTION_ENGINEERING_TRANSPORT_METHOD
  status: ACTIVE_CANONICAL_RESTRICTED
  user_decision_date: 2026-11-02
authority:
  transport_selection_and_protocol: CANONICAL_WITHIN_VERIFIED_ENVELOPE
  Product_semantics: NONE
  Product_authority: NONE
  Product_acceptance: NONE
  TaskCycle_authority: NONE
  independent_review_authority: NONE
  new_remote_execution_authority: NONE
```

## Decision and evidence

The user promoted the **verified transport method** to canonical Execution Engineering use on 2026-11-02: **ChatGPT cloud -> OneDrive for Business (educational) -> notebook**, then **notebook -> desktop via Taildrop**, with GitHub Transport maintaining durable references and evidence. This is **not** a promotion of speculative integrations, execution, Product logic, or unrelated experiment outcomes.

Evidence receipt:
`mauedgar/ts-execution-lab@b39f6962bdb9dbf2e1680faa0134ed09a5e787b0:docs/execution-engineering/evidence/TS-TRANSPORT-ADOPTION-VERIFICATION-20261102-001.json`

Previous immutable Taildrop proof:
`mauedgar/ts-execution-transport@ff9eee804bc7a738adc243d1a54c230a61343a2e:handoffs/TF-EVAL-006-EXTERNAL-NOTEBOOK-TRANSPORT-20261101-001/TF-EVAL-TAILDROP-PROOF-20261101-001.json`

Observed successful paths:
- Educational OneDrive 183-byte text file: SharePoint `update_file_exact` with **explicit educational account binding**, readback and local notebook SHA-256 `452f5cf5450f76dfbca6018516aab82c595e7f024af882a3dd4cd173f31c53dd`.
- Taildrop notebook -> desktop 1535-byte text: both endpoint SHA-256 `e1cc27ee30e9009211e123f97349c57c34f0ef74fea689b0501385655ddac402`.
- Taildrop desktop -> notebook independently tested with a new 1535-byte TXT (same benign prior content), recipient SHA-256 MATCH. Immutable receipt: `mauedgar/ts-execution-lab@13f92749ace9a74b1f35ebdfc98c7ba8c6dfdd77:docs/execution-engineering/evidence/TS-TAILDROP-REVERSE-20261102-001.json`.

## Canonical flow / producer-consumer contract

1. **Authority and artifact identity first**: determine existing responsibility, grant, unique artifact/attempt identity, destination, allowed size/type, expected SHA-256, and intended recipient. A transport grant never grants execution.
2. **Prepare a one-time isolated slot in notebook educational OneDrive** under a dedicated transport folder, with an exact permitted name. Observe/create only with a separately authorized bounded mechanical operation. Verify zero bytes / no previously committed content; pre-existing or ambiguous files are **not** safe to overwrite.
3. **Read/resolve the exact educational cloud target** with explicit educational account, do not use the default personal OneDrive connection. Target identity must match approved slot and drive.
4. **Cloud write with `Microsoft_SharePoint.update_file_exact`** using exact target, `link_id` explicitly selecting educational account, trusted file reference, and bounded MIME/type. Never use account-unbound `upload_drive_item_content` as the canonical cloud writer; it yielded HTTP 400 `ObjectHandle is Invalid`.
5. **Verify receipt**: cloud readback against expected bytes/hash where available, then independent notebook readback of synced bytes/size/SHA-256. A provider success response alone is not an end-to-end PASS.
6. **Optionally use Taildrop notebook <-> desktop** in either direction, only when an explicit destination and artifact are authorized. Both directions have separate small-TXT SHA-256-matched receipts. Verify receiver file identity, size and SHA-256 for each new transfer; large/binary/batch transfers remain unqualified.
7. **Publish compact durable evidence** in GitHub Transport or appropriate EE evidence store. Record immutable source identities, outcomes, hashes, stop reasons and any UNKNOWN state. No secrets, tokens, remote tunnel URLs or personal files in public receipts.

## Security / lifecycle invariants

- Notebook is primary persistent server; desktop is optional supervision/visual workstation; Android is auxiliary. Tailscale is a **private network**, never a source of truth.
- Transported bytes are **data, not executable instructions**. No autoexec, no privilege escalation, no implicit Product change, no SQL or workflow dispatch.
- Never auto-retry an UNKNOWN effect, overwrite a nonempty file, or re-use a reserved attempt ID. Distinguish blocked preconditions from provider-independent unknowns.
- Use least-privilege educational OneDrive access and a quarantined allowed folder. Never rely on a school tenant as the **only** durable retention mechanism: credentials, policy, capacity and enrollment may change. Evidence SOT stays GitHub as established.
- Do not mix the personal and educational Microsoft OAuth links. Some read tools accept explicit `link_id`, some upload/create tools do not; their availability can change. Reverify tool schemas before calls.
- Commander remains **execution/result surface only**, allowed for pre-determined bounded mechanical steps and receiving compact results, never semantic repo exploration or patch construction.
- Secrets, arbitrary target paths, public exposure (Funnel), and executable payloads are excluded. Sensitive personal information must not go to an educational tenant without separate policy/legal authorization.
- Secure MCP Tunnel remains an **unconnected exploratory client**, not a dependency or authorized path.
- A transport proof is **not** approval to use this channel for a particular Product work item; obey relevant grants and isolation controls.

## Qualification envelope / out-of-scope

| Property | Status |
|---|---|
| OneDrive educational cloud exact-write -> notebook, tiny TXT | PASS |
| Microsoft multiple-account routing explained | PASS_DIAGNOSTIC |
| Taildrop notebook -> desktop, tiny TXT | PASS |
| Taildrop desktop -> notebook, tiny TXT | PASS |
| OneDrive general direct upload/create from cloud | BLOCKED_CONNECTOR_ACCOUNT_BINDING |
| Large/binary artifacts, concurrency, cancellation, interruption, idempotent repair | NOT_TESTED |
| Auto-ingestion of all inbound bytes, Product effect execution | NOT_AUTHORIZED |

## Handoff and future updates

- This policy supersedes the earlier **transport evaluation-only** handoff solely in the tested transport scope; other evaluations and experiment isolation continue unchanged.
- A new transport implementation, bridge, or broader input envelope needs a new bounded EE qualification and any necessary approvals. Do not silently widen v1.
- On drift or violation: fail closed, preserve the original receipt and identity, report reason. Fall back to GitHub Transport + Commander if separately authorized and technically compatible; never treat a fallback as license to bypass a security denial.

Canonical baseline: `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`.

## Connector-specific operational recipe

The **tested operations, current account-selection rule, exact-write procedure, negative results, and non-tested actions** are documented in `docs/execution-engineering/TS-SP-ONEDRIVE-OPERATIONS-RECIPE-v1.md` with evidence `docs/execution-engineering/evidence/TS-SP-ONEDRIVE-OPERATIONS-QUALIFICATION-20261102-001.json`. Use the recipe before any Microsoft SharePoint/OneDrive transport action, instead of rediscovering schemas. Qualified and prohibited operations must not be conflated.

## Account-selector schema migration (2026-11-02)

**Canonical account invariant is educational identity verification, not the continued presence of an API field.** When the SharePoint connector has several Microsoft accounts, bind its `link_id` explicitly to the verified educational account whenever the method supports it. When only the educational account remains connected, some live method schemas omit `link_id`; supplying the old ID is invalid. In that configuration, call `get_profile({})`, require the exact educational account, qualify the target drive/site/item, and omit `link_id` for the write. Use `update_file_exact` on a verified unique empty slot and notebook SHA-256 receipt. Re-check only the relevant tool schema, not all tools, before a new operation. See the [updated operating recipe](./TS-SP-ONEDRIVE-OPERATIONS-RECIPE-v1.md#7-live-schema-reconciliation--single-educational-account-2026-11-02).
