# Execution Engineering — Receta operativa SharePoint / OneDrive educativo v1

```yaml
artifact:
  id: TS-SP-ONEDRIVE-OPERATIONS-RECIPE-v1
  status: ACTIVE_CANONICAL_RESTRICTED
  owner: TS_EXECUTION_ENGINEERING
  date: 2026-11-02
scope:
  account: EDUCATIONAL_ONEDRIVE_BUSINESS_ONLY
  operation: BOUNDED_TRANSPORT_AND_VERIFICATION
authority:
  Product: NONE
  execution: NONE
  general_cloud_file_mutations: NONE
```

## 0. Why this recipe exists

Do **not** rediscover routing/parameters every turn. With both personal and educational Microsoft accounts installed in ChatGPT, account-unbound OneDrive methods routed to personal or returned HTTP 400 `ObjectHandle is Invalid`. Even after the personal connection was disconnected, some default-drive reads failed internally. Explicit educational `link_id` actions continued to work. **Never equate tool-level success with end-to-end sync.**

Primary receipt: `docs/execution-engineering/evidence/TS-SP-ONEDRIVE-OPERATIONS-QUALIFICATION-20261102-001.json`.
Transport policy: `docs/execution-engineering/TS-EXECUTION-TRANSPORT-ONEDRIVE-TAILDROP-v1.md`.

## 1. Binding (refresh only when needed)

1. At invocation time inspect `mcp__Microsoft_SharePoint__get_profile` or `list_drives` tool schema and select the `link_id` whose `link_name` is **FRC UTN** and whose authenticated profile is the educational account. Do **not** select `Secundary` or any personal Microsoft account.
2. Use `get_profile({link_id: EDU_LINK_ID})` and `list_drives({link_id: EDU_LINK_ID})`; assert `drive_type == business` and that the known OneDrive belongs to the verified educational tenant. Concrete IDs and URLs are recorded separately in the **private** execution-transport binding, not in this public recipe.
3. Do not use any no-`link_id` method to choose the default account for an effectful write. Some such methods can still work with exact SharePoint site/URL; classify individually.
4. The endpoint and `link_id` are **runtime locators**, not credentials and not permanent guarantees; fail closed on mismatch and rebind through the provider, not via guesswork or blind retries.

## 2. The tested exact-write workflow (preferred)

**Preconditions (no Product / no executable instructions):** known bounded file type and size, pre-authorized effect, unique attempt, isolated educational OneDrive sandbox, no preexisting nonempty file, declared expected SHA-256, approved notebook consumer, no unresolved previous effect.

**Producer/consumer protocol:**

1. Notebook: mechanically check the educational OneDrive account and that its sync root exists. Only under a permitted bounded operation, reserve a **unique zero-byte slot** in the dedicated sandbox. If name already exists or is not zero bytes: BLOCKED_PRECONDITION.
2. ChatGPT connector: read exact path with `fetch({url: EDUCATIONAL_SLOT_URL, link_id: EDU_LINK_ID})` for text; for binary, get metadata via known Graph item ID. Confirm the slot belongs to the educational drive and is empty; note `fetch` text extraction does **not** support `.bin` in its default mode.
3. ChatGPT cloud: call **once** `update_file_exact({target: {type:'item_url',item_url:EDUCATIONAL_SLOT_URL}, file_uri:EXACT_SANDBOX_FILE_URI, mime_type:EXPECTED_MIME, link_id:EDU_LINK_ID})`. No general-purpose `upload_drive_item_content`, no overwrite of existing non-test data.
4. Verify Graph response `name`, `drive_id`, `size` and successful educational `fetch` (text) or `get_drive_item` (binary). Use `fetch({...,download_raw_file:true,link_id:...})` for raw binary when needed.
5. Notebook: verify the **same unique slot** exists in the local educational sync folder, exact byte length and SHA-256. A cloud success alone is not PASS. Record provider item ID, attempt ID, hash, byte length, timestamps and terminal state.
6. Optionally Taildrop the verified artifact to desktop. Both small-TXT transfer directions are tested but every new transfer still requires a receiving SHA-256 check.

**Observed exact-write positives:** 183-byte TXT SHA-256 `452f5cf5450f76dfbca6018516aab82c595e7f024af882a3dd4cd173f31c53dd`; 32768-byte synthetic binary SHA-256 `316843070c0b9dcda0fc0f0d3587820125d733ff2f76a69143f9626f2bec614d`. In both, the notebook hash matched. These are synthetic receipts only, not reusable execution inputs.

## 3. Working commands / recipes, by task

| Goal | Exact tool(s) | Observed result | Use rule |
|---|---|---|---|
| Verify educational identity | `get_profile(link_id)` | PASS | Explicit educational link |
| List account drives | `list_drives(link_id)` | PASS | Require `business`, not `personal` |
| Inspect recent documents | `list_recent_documents(link_id)` | PASS | Legacy/deprecated; fallback only |
| Resolve personal SharePoint site | `get_site(hostname,site_path)` | PASS | Known educational site, not arbitrary |
| Discover site libraries | `list_site_drives(hostname,site_path)` | PASS | Prefer this over default account drives for site scope |
| Discover SharePoint lists | `list_site_lists(site_id,top)` | PASS first page | Unrelated to transport; respect pagination |
| List exact transport folder | `list_folder_items(hostname,site_path,folder_path,top)` | PASS | Use before any site-scoped mutation |
| Read metadata of known file | `get_drive_item(drive_id,item_id,link_id)` | PASS | Explicit educational link + exact ID |
| Read known TXT | `fetch(url,link_id)` | PASS | Readable text only |
| Download binary | `fetch(url,download_raw_file:true,link_id)` | PASS | File reference, not inline base64 |
| View file revisions | `list_item_versions(target,link_id)` | PASS | Read-only, may paginate |
| Inspect access permissions | `list_item_permissions(target,link_id)` | PASS | Read-only; do not create sharing links |
| Write cloud to precreated slot | `update_file_exact(target,file_uri,mime_type,link_id)` | PASS TXT + BIN | ONLY bounded exact target / verified account / new empty slot |
| Create test subfolder under educational site | `create_folder(hostname,site_path,parent_folder_path,folder_name,conflict_behavior:'fail')` | PASS | Only sandbox; no account selector; exact site path essential |
| Rename empty test file | `move_or_rename_item(target,new_name)` | PASS | Exact source URL / unique name; verify readback |
| Copy empty test file | `copy_item(source_target,destination_folder_target,new_name,link_id,conflict_behavior:'fail')` | 202 + PASS after readback | Async accept is NOT completion; verify destination |
| Broad search | `search(query,...)` | PASS but 0 new-file hits | Indexing is not delivery confirmation |
| List default OneDrive folder | `list_drive_item_children(...)` | ERROR_INTERNAL after account change | Avoid as canonical method |
| Search default OneDrive | `search_drive_items(...)` | ERROR_INTERNAL after account change | Avoid as canonical method |
| Generic create/upload in OneDrive | `upload_drive_item_content(...)` | Previously HTTP 400 with mixed accounts | No `link_id`; not qualified after connection change; do not retry old effect |

## 4. Complete tool-inventory disposition (all surfaced actions)

**Qualified on isolated synthetic data:**

- `copy_item`, `create_folder`, `fetch`, `get_drive_item`, `get_profile`, `get_site`, `list_drives`, `list_folder_items`, `list_item_permissions`, `list_item_versions`, `list_recent_documents`, `list_site_drives`, `list_site_lists` (first page), `move_or_rename_item`, `search` (tool succeeds but indexing not delivery proof), `update_file_exact`.

**Observed failures / do not use until provider binding is repaired:**

- `list_drive_item_children`, `search_drive_items` (internal errors after account switch).
- `upload_drive_item_content` (previous `ObjectHandle is Invalid` with personal-default routing; no safe reclassification yet).

**Schema reviewed only; no effectful trial / require separate explicit grant and controlled sandbox if ever needed:**

- `create_drive_folder`, `create_drive_folders_bulk`, `create_drive_item_link`, `create_folders_bulk`, `create_sharing_link`, `delete_drive_item`, `delete_item`, `get_list_item`, `get_sensitivity_labels`, `invite_item_recipients`, `list_list_items`, `move_drive_item`, `move_drive_items_bulk`, `move_items_bulk`, `restore_item_version`, `update_file`, `upload_file`, `upload_file_to_folder`.

Tool catalogue is per installed connector version; if an operation disappears or gains an account-binding field, revalidate only that changed operation. Unsupported or dangerous actions are **documented, not falsely declared tested**.

## 5. Hard stop conditions / negative tests

- Wrong account, personal `drive_id`, missing educational `link_id` on exact-write, unexpected Graph drive, unknown slot or unexpected name → `BLOCKED_PRECONDITION`.
- Existing nonempty or reused target name → do not overwrite, no silent retry.
- Provider timeout / ambiguous success → `UNKNOWN_NO_RETRY`; reconcile exact target and provider receipt before any further effect. A new chat is not retry authorization.
- Cloud receipt success + notebook file absent / wrong hash → `PENDING_SYNC` or `FAILED_HASH`, **not** `PASS`.
- SharePoint `ObjectHandle is Invalid` → likely account-binding mismatch; check explicit identity and exact URL on read-only path, do not repeat old upload blindly.
- Creating anyone-link, emailing invitations, deleting/restoring versions, bulk writes, or copying sensitive user data outside the sandbox are **not transport validation**.
- Microsoft educational account may be institution-managed/revoked. Durable EE evidence remains in GitHub as established; OneDrive is a carrier, not authoritative state.
- Transport method does not grant execution, auto-unpack, SQL, Product acceptance, authority or retries.

## 6. Publishing / reuse

- Record `attempt_id`, source SHA-256, requested MIME/bytes, selected educational account alias, Graph exact drive/item ID, notebook receiver bytes/hash, and stop reason. Do not publish OAuth secrets or user identity selectors in public repos.
- Keep concrete educational account link/drive/site binding, when needed for fast re-use, in **private** `mauedgar/ts-execution-transport` and treat it as a cache requiring validity verification.
- Before a new connector call: consult this recipe; inspect just the live schema for the selected action, not all apps or the repository.
- This document is an operational recipe under `TS-EXECUTION-TRANSPORT-ONEDRIVE-TAILDROP-v1`, not a new Product grant.
