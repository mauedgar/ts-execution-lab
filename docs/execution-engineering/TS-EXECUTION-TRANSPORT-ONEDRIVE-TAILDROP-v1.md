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

## Canonical flow / producer-consumer contract

1. **Authority and artifact identity first**: determine existing responsibility, grant, unique artifact/attempt identity, destination, allowed size/type, expected SHA-256, and intended recipient. A transport grant never grants execution.
2. **Prepare a one-time isolated slot in notebook educational OneDrive** under a dedicated transport folder, with an exact permitted name. Observe/create only with a separately authorized bounded mechanical operation. Verify zero bytes / no previously committed content; pre-existing or ambiguous files are **not** safe to overwrite.
3. **Read/resolve the exact educational cloud target** with explicit educational account, do not use the default personal OneDrive connection. Target identity must match approved slot and drive.
4. **Cloud write with `Microsoft_SharePoint.update_file_exact`** using exact target, `link_id` explicitly selecting educational account, trusted file reference, and bounded MIME/type. Never use account-unbound `upload_drive_item_content` as the canonical cloud writer; it yielded HTTP 400 `ObjectHandle is Invalid`.
5. **Verify receipt**: cloud readback against expected bytes/hash where available, then independent notebook readback of synced bytes/size/SHA-256. A provider success response alone is not an end-to-end PASS.
6. **Optionally send notebook -> desktop via Taildrop** only when an explicit destination and artifact are authorized. Verify receiver file identity, size, and SHA-256. The reverse **desktop -> notebook file-transfer** direction is not yet qualified (bidirectional Tailscale pings are not equivalent to receipt verification).
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
| Taildrop desktop -> notebook, file receipt | UNQUALIFIED |
| OneDrive general direct upload/create from cloud | BLOCKED_CONNECTOR_ACCOUNT_BINDING |
| Large/binary artifacts, concurrency, cancellation, interruption, idempotent repair | NOT_TESTED |
| Auto-ingestion of all inbound bytes, Product effect execution | NOT_AUTHORIZED |

## Handoff and future updates

- This policy supersedes the earlier **transport evaluation-only** handoff solely in the tested transport scope; other evaluations and experiment isolation continue unchanged.
- A new transport implementation, bridge, or broader input envelope needs a new bounded EE qualification and any necessary approvals. Do not silently widen v1.
- On drift or violation: fail closed, preserve the original receipt and identity, report reason. Fall back to GitHub Transport + Commander if separately authorized and technically compatible; never treat a fallback as license to bypass a security denial.

Canonical baseline: `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`.
