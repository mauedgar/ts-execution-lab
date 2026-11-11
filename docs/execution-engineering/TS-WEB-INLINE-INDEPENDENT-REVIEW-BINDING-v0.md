# WEB_INLINE — ChatGPT Web Independent Review binding v0

```yaml
id: TS-WEB-INLINE-INDEPENDENT-REVIEW-BINDING-v0
owner: TS_EXECUTION_ENGINEERING
artifact_class: EXECUTION_BINDING_PROFILE_CANDIDATE
status: EXPERIMENTAL_SYNTHETIC_PASS_PENDING_PRODUCT_QUALIFICATION
Product_authority: NONE
Product_effect: NONE
canonical_Tecnotron_adoption: NOT_GRANTED
```

## Modalities and selection

The established Independent Review contract and lifecycle remain unchanged. These are **alternative, separately qualified harness bindings**, not different Reviewer responsibilities:

| Binding | Scope of this profile | Existing status |
| --- | --- | --- |
| `WEB_INLINE` | ChatGPT Web semantic Independent Review; optional scheduled invocation and temporary Library return | This experimental profile candidate only |
| `OPENCODE_LOCAL` | Native OpenCode-local reviewer | Unchanged; keep existing native isolation, authentication, credentials, preflight and receipts |
| `ACTIONS_REMOTE` | Remote reviewer execution via Actions | Unchanged; keep provider-specific dispatch, isolation and receipts |

**Control alone selects a binding** within actual competent Product authority and the current review contract. Neither `WEB_INLINE` success nor a failure/blocker in another modality selects, replaces, retries or authorizes any modality automatically. If changing surface, Control must preserve or competently re-freeze the **same exact authorized subject** and correlate all review/attempt identities and review preconditions; a distinct necessary review has its own identity and authority. No modifying an active TaskCycle or bypassing a blocking gate.

Every modality returns its original verdict `PASS` / `FAIL` / `BLOCKED` and full findings/evidence to the **same competent Product reconciliation path**. Publication != consumption; review `PASS` != Developer acceptance; neither means Phase 2, integration or close.

## WEB_INLINE execution arrangement (optional; not a new Recipe)

1. Control selects a competent already-authorized review, freezes the exact Git subject and applicable authority/scope/criteria/evidence inventory under the **existing** `materialize_frozen_review_interface@v0` Recipe and portable handoff. An open issue, READY preflight or frozen package is **not** a dispatch or grant.
2. Create exactly one `ExecutionAttempt` with expected result, target and status. Reconcile old terminal/UNKNOWN attempts first. Bind `WEB_INLINE` explicitly. **For a Scheduled launch, the exact task prompt MUST explicitly demand saving the one ORIGINAL to personal ChatGPT Library**, not merely say "consume the handoff and execute IR". Instantiate `TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md` with frozen Git handoff, Review_ID, ExecutionAttempt and expected Git result target. The entire mandatory Library upload/receipt/failure clause must be in `automations.create.prompt`; referencing a frozen handoff alone is insufficient.
3. The ChatGPT Web reviewer must acquire **only** declared frozen inputs from Git and verify identity; use a fresh separate context, read-only semantic assessment, no prior implementation discussions or unlisted memory, and report actual isolation evidence/limits. Scheduled invocation is an empirical separate task but does **not** itself attest provider-internal isolation, model identity, GPT Sol version or reasoning effort.
4. The reviewer emits **one complete ORIGINAL** result with review ID, `ExecutionAttempt`, subject commit/tree/parents, interface hash, verdict, all findings and limitations, actual validations, independence evidence and `Product_effect: NONE`. Do not modify the candidate, self-accept or publish Product SOT.
5. The scheduled task **MUST attempt** to upload its one complete ORIGINAL to personal ChatGPT Library as temporary transport, using an actual available Library file-management operation and confirming `status=succeeded`. The response must include exact returned `library_file_id`/`file_id`, original UTF-8 byte length, SHA-256 and verification evidence; a file at `/mnt/data` or downloadable sandbox link is **not** Library persistence. Prefer independent readback/materialization to compare bytes. If upload cannot be performed/confirmed, keep the **review result terminal** but return explicit `BLOCKED_TRANSPORT` (or `UNKNOWN_EFFECT` if write outcome ambiguous), preserve the original and a recovery pointer and never claim Library success. No direct Scheduled GitHub write is required by this binding.
6. At the real ChatGPT Web continuation, acquire that exact Library file/bytes and verify checksum, length, `ExecutionAttempt`, review ID and immutable subject. Reconcile whether the intended GitHub result already exists; if `UNKNOWN`, do not repeat a mutation. Publish **identical original bytes** to GitHub Transport under authorized target, verify exact Git commit/blob and readback. Preserve a separate bridge receipt if needed; do not rewrite the Reviewer verdict or mistake a bridge receipt for original review evidence.
7. Deliver exact result Git ref to competent Control for the **existing** review-result consumption and TaskCycle reconciliation. The intermediate Library hop is not Product SOT, a new lifecycle state, scheduler, Recipe, or automatic gate; this bridge currently needs an **interactive Web continuation** and is not fully unattended end-to-end.

### Scheduled launch hard gate — original artifact custody (2026-11-11)

The operative [WEB_INLINE scheduled dispatch template](TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1.md) is **mandatory** for new scheduled WEB_INLINE Independent Reviews. Before scheduling, Control verifies that the **actual task prompt** contains the four frozen identifiers and an explicit Library upload/receipt/verification and fail-closed clause. Do not create a task with only the previous shortened handoff-only prompt. If the selected scheduled environment's Library-write capability is not known, record `UNKNOWN_PRE_DISPATCH_CAPABILITY`; do not pretend a task inherits the tools of the active conversation. The task must handle missing tooling as `BLOCKED_TRANSPORT`, never by falsely reporting success. This is a transport reporting requirement, not a new Product review gate.

On original provider terminal result, distinguish `REVIEW_TERMINAL` from `LIBRARY_VERIFIED`, `LIBRARY_UPLOADED_UNVERIFIED`, `BLOCKED_TRANSPORT`, or `UNKNOWN_EFFECT`. A successful automation **schedule** does not satisfy either reviewer completion or artifact custody. Control checks exact `library_file_id`/`file_id`, byte count and SHA-256 before publishing the identical original to GitHub Transport create-only; reconcile a prior/uncertain Git result before any write. If Library failed but the original is available by reviewer download/user attachment, interactively recover **those exact bytes** rather than repeat the semantic review. Never synthesize the reviewer ORIGINAL from an automation summary, never promote an attachment to an independent test and never claim Product acceptance from a bridge receipt.

**Regression reference:** Attendance PR21 IR002-A001 review finished in a separate scheduled context with `NO_RECOMMEND / 0F / 5A` but its actual task prompt omitted explicit Library upload. It produced only a sandbox artifact. The same original was later verified as 7,374 UTF-8 bytes, SHA-256 `fefd09b618f8e89d56dfce87a64e373259bc717e1188a91a1191c4566f0d04b2`, recovered into Library `libfile_24278c95b154819197167c45d83d86d8`, and published byte-identically as Git blob `20918b2d33db875773383497dea93ab183d74b8e` in `mauedgar/ts-execution-transport@00cf96b0c787e6fdba12cd5d7dc441d333abe53e`. This validates interactive recovery; it does **not** verify scheduled Library tool availability or qualify the Product binding.

## Reviewer completeness diagnosis (EE reporting clarification, 2026-11-09)

In the ORIGINAL result of a WEB_INLINE review, supply `review_completeness` as specified by `TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md` §14: `expected_files`, `fetched_and_verified_files`, `semantically_reviewed_files`, per-path `omitted_files[path,reason]`, `incomplete_reason[category,observed_error,evidence,recovery_precondition]`, and `test_execution[executed_by_reviewer,existing_CI_verified,missing_validation]`. Use actual Git blob reads and tool errors, not just a changed-path table or reviewer intent. An incomplete review must explain which paths or cross-file/security consumers remain unevaluated, why, and what competent dependency would make review completion possible. Missing source coverage => `PARTIAL` or `BLOCKED`, not a full PASS, even if all observed CI is green. Provider-internal model/effort limits, tool quotas and security filtering are `UNKNOWN` unless actually observed; a negative 404 is not automatically a security denial.

Record test execution, verification of pre-existing CI receipts and NOT_RUN work as separate categories. This is a reporting requirement in the **existing** review artifact; it introduces no reviewer executor, TaskCycle, Product DoD, new Recipe, or independent security approval. The bound input for a Product review must still freeze the subject and source scope and must not reuse a security-denied IR input.

**Evidence ceiling:** [synthetic source qualification](https://github.com/mauedgar/ts-execution-transport/blob/63c901874038a0699ad1b0c941dd744e8b7c5446/requests/TS-EE-REVIEW-COMPLETENESS-QUAL-20261109-001/INPUT.md) and [original terminal result](https://github.com/mauedgar/ts-execution-transport/blob/fca0d44ab34dd146a31034e169968f1479022649/results/TS-EE-REVIEW-COMPLETENESS-QUAL-20261109-001/ORIGINAL_RESULT.md), both read-back verified, tested FULL 1/1 and PARTIAL 1/2. This qualifies only small synthetic omission diagnostics. `EXPERIMENTAL_SYNTHETIC_PASS_PENDING_PRODUCT_QUALIFICATION` remains unchanged.

## Qualification / fail-closed

- The Product `QUALIFIED_INDEPENDENT_REVIEW_BINDING` ceiling still comes from `mauedgar/tecnotron-ai:tools:docs/architecture-knowledge-ownership-baseline.md` §16.4, WP003 REVIEW and current competent Product authority. Candidate profile existence and synthetic `PASS` do **not** qualify a Product-independent reviewer. Confirm full frozen inventory/correspondence, actual separate-context limits, semantic evidence, result provenance and exact Product subject before claiming qualification.
- Model/provider configuration is not inferred from ChatGPT Web task naming; capability to dispatch Scheduled does not attest explicit GPT Sol/model/effort. Each profile has separate qualification evidence.
- No implicit fallback from `OPENCODE_LOCAL` or `ACTIONS_REMOTE`; a blocked modality remains blocked for its specific attempt until Control authorizes a properly reconciled alternative.
- Do not replay a reviewer when only Library/GitHub publication failed. In any uncertain write effect, observe exact target before a competent retry; no blind retries.
- If ChatGPT safety checks deny GitHub writes, report the actual denial, respect it, and use only authorized operations when available. Do not treat changing extension, encoding, role wording, or tool as a safety bypass.
- Existing OpenCode v2 reviewer preflight/isolated-host constraints are **unchanged** and remain applicable to `OPENCODE_LOCAL`, not falsely imposed on `WEB_INLINE`. Existing `ACTIONS_REMOTE` constraints are likewise unchanged.

## Exact experimental evidence (not Product adoption)

- `WEB_INLINE` handoff-only reviewer synthetic 006: frozen/handoff evidence `mauedgar/ts-execution-transport@8106b64b0a5aafd3ddb6b512892afa154a254612:requests/TS-REVIEWER-HARNESS-AGNOSTIC-MVP-20261012-006/HANDOFF.md`. Original task returned `FAIL`; scheduled GitHub write refused; separate EE user-return reconciliation at `9d6608c3a5dff732bd967dad99af5ae4e6dcc9d0:results/TS-REVIEWER-HARNESS-AGNOSTIC-MVP-20261012-006/EE_OBSERVATION_FROM_USER_RETURN.json`.
- Temporary Library bridge synthetic 008: `libfile_8a2c907f617c8191be135646b78df667`; byte-identical Git publication `mauedgar/ts-execution-transport@370fdc1e0658b7c2472ebad07685db646adc17e6:results/TS-SCHEDULED-LIBRARY-BRIDGE-20261012-008/LIBRARY_ARTIFACT.json` (213 bytes).
- Full original synthetic Independent Review 009: handoff `mauedgar/ts-execution-transport@4de6fa0ad39e26f994a1da8687d0accadde0a199:requests/TS-REVIEWER-LIBRARY-MVP-20261012-009/HANDOFF.md`; original result Library `libfile_352f2e1337088191b34bee161acc0e6f`, 4718 bytes, SHA-256 `d8cdf53e14d02d48d709db84b6a3e48e59591e20fe2cd7030e088a4756ec71d7`; exact Git result `mauedgar/ts-execution-transport@4b81a008db0ae07d61cd89dc671a1d841ecfacfc:results/TS-REVIEWER-LIBRARY-MVP-20261012-009/REVIEW_RESULT.json`, blob `0e051619c57fde8fc963008ee0046069163acacf`; `FAIL` with two original findings. Publication in Git was completed by an interactive ChatGPT Web continuation without a second review.
- Limits: synthetic only; actual Product IR and provider-internal isolation/model binding not independently attested; one end-to-end original-review experiment is not a reliability guarantee. No Product authority or canonical Tecnotron effects.

## Promotion boundary

Execution Engineering may qualify **this technical binding**, but Product adoption requires competent Control selection, actual applicable independent-context evidence, original IR as needed on a real authorized exact subject, distinct Developer acceptance where the TaskCycle requires it, and separately authorized integration/reconciliation. **Do not integrate into `mauedgar/tecnotron-ai:tools` merely because this profile exists.**

The operative SOT is the Tecnotron repository, not this document, a chat, Library, or the transport repository.
