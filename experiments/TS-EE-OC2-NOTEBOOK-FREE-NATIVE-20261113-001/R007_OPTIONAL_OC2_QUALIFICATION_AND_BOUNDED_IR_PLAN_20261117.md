# R007 — Optional OpenCode2 qualification and bounded IR | experimental batch plan

**Control/Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001` (same historical line; no replay).  
**Authority:** `NONE`; `Product_authority: NONE`; `canonical_product_effect: NONE`. No automatic reviewer adoption, no Product repository mutation, no Actions fallback or paid model use.  
**Developer ruling:** WEB_INLINE, OpenCode2, or another reviewer is an **explicit choice by competent responsibility**, never a single mandated/canonical review path.  
**Status:** `B0_EVIDENCE_PASS / B1_CANDIDATES_PREPARED_NOT_QUALIFIED / NO_NEW_MODEL_DISPATCH`.  
**Review policy:** ONE independent source review of a coherent complete implementation batch, then ONE independent behavior/evidence review after the bounded synthetic cases. Do not micro-review every file/change.

## Reconciled evidence, no repeated effects

- Historical Orca-native OpenCode2 `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-A001`: terminal `CONFIRMED_EXECUTED`, 399,890-byte private ORIGINAL, model exit 0, **FAILED_SEMANTIC_CONFORMANCE / NO_RECOMMEND**, no retry. Original mechanical bridge one-shot worked, but it is NOT generally qualified.
- Independent bridge IR `TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001`: `NO_RECOMMEND / 4F / 5A`; original `mauedgar/ts-execution-transport@4ae785f79b5c2d295ee75683f6cfaf4bd4a7684f:results/TS-EE-ORCA-NATIVE-BRIDGE-WEBINLINE-IR001-20261114-001/ORIGINAL.md`.
- R006 private structural reader: 60/60 POSIX tests PASS, historical CRLF ORIGINAL parsed without modification, sanitized private receipt hashed. The independent source IR002 `TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR002-20261117-001` is **RECOMMEND_SOURCE_ONLY / 0F / 5A**; its exact 12,158-byte ORIGINAL, SHA256 `095b4d77a245063db9ddbd05050f8bf71d62ffaee4f18baaf2f398666989c103`, Git blob `86699cdba05bddc1b11cb39fa7bf4d7809356654`, was published with verified readback at `mauedgar/ts-execution-transport@a33a1ded3c5b6230bbf1d5c41ccbdf14eebccbf0:results/TS-EE-ORCA-JSONL-V6-CRLF-WEBINLINE-IR002-20261117-001/ORIGINAL.md`.
- R006 is qualified as a **bounded experimental structural checker only**. It does not authenticate the provider, prove a zero-dollar invoice, establish an effective permission policy or pass a semantic review. Five advisories remain as scope limits, not mandatory source repairs merely to force 0A.

## Bounded IR policy: source coverage before reasoning

**Problem evidenced, not fully diagnosed:** a prior reviewer asserted a 42-digit SHA even though its frozen source contained the valid 40-digit SHA; the first OpenCode2 model ignored an inline task and explored the repository. Neither proves that pure context size is the sole cause. Reduce active information and add deterministic coverage checks before trying higher reasoning.

1. **Freeze an evidence inventory** under a true 40-hex subject commit/tree, each PRIMARY file's exact path and Git blob. Separate PRIMARY files (required for verdict) from CONTEXT evidence (optional or sampled). A missing PRIMARY file blocks a full-source verdict.
2. **Single concern per review.** Keep the reviewed *semantic unit* limited to one component or coherent batch; target at most 3 substantive source files and roughly 40,000–50,000 UTF-8 source bytes, excluding reference-only receipts. These are scheduling heuristics, not evidence of a specific model context ceiling. Split a larger PR by risk domain (security, persistence, UI, etc.), not one reviewer per trivial edit.
3. **Machine preflight:** compare exact Git commit/tree and every PRIMARY blob *outside the LLM* before dispatch, check byte-length and 40-character SHA formatting, detect missing files or changed HEAD, and fail closed. If the reviewer cannot obtain complete primary content, it must emit `BLOCKED_COVERAGE` rather than assert full review.
4. **Reviewer output:** each PRIMARY file needs a `READ_FULL | NOT_READ | PARTIAL` declaration, exact Git blob, inspected line range, and at least one independently checkable code anchor or explicit `NO_FINDING_AFTER_FULL_READ`. Enumerate uninspected files. Every finding must cite actual file:line, defect mechanism, impact, and test. Distinguish `REVIEW_COVERAGE` from `REVIEW_VERDICT`.
5. **Post-review deterministic coverage join:** Control cross-checks declared primary inventory and evidence/line anchors against frozen blobs. `0F` with `NOT_READ`, an invalid SHA, impossible line number or missing obligatory file is `BLOCKED_COVERAGE`, not `RECOMMEND`. Reviewers can still make errors; tool-backed completeness checks are a guardrail, not a guarantee of correct reasoning.
6. **Only grouped independent gates:** after batching source repairs and deterministic tests, ONE fresh-context strict read-only IR on the frozen source unit; after actual native attempts, ONE separate IR on a concise bounded runtime/behavior package. Avoid forcing a source reviewer to consume private 400-kB traces or to attest provider billing. No automatic retries or recursive reviewer loops.
7. **Advisory handling:** preserve meaningful 5A if nonblocking and out of SOURCE_ONLY scope. Developer/Control accepts the documented boundary rather than continually pursuing cosmetic 0A. If an advisory becomes blocking for a wider runtime claim, promote it with evidence at that new gate, not retroactively.

**Concrete proposed two-lane review:**
- `IR-SOURCE-BATCH`: candidate Orca bridge runner source + frozen zero-tool config + deterministic admission/ledger contract/tests. Required primary files limited as above; native runtime evidence contextual only. PASS means source qualification, not runtime.
- `IR-BEHAVIOR-BATCH`: one bounded original/receipt *per separately identified synthetic attempt*, provider/cost/policy attestations, deterministic oracle scores, no raw secrets. May not be declared fully verified if private originals are not independently available in an appropriate trusted surface. PASS only for optional experimental binding, never a Product review requirement.

## OpenCode2 qualification as one medium-sized batch

### B0 — DONE, reconcile source and original custody
R006 source structural helper and IR002 original reconciled and published. Historical A001 untouched. No new model calls. `B0_PASS`.

### B1 — PARTIALLY PREPARED, build and validate a safe transport/admission candidate
Current candidate sources, **not executed or canonical**:
- `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_CLOSED_CONTEXT_FREE_NO_TOOLS_CONFIG_CANDIDATE.json`, Git blob `16ed6e50bddf955db6f27484624b47cbe762fb3b`.
- `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_CLOSED_CONTEXT_SEMANTIC_CASES_V1.json`, Git blob `c0be212f4e64b6ee1d8ac64346f7ed20ab62194a`.

The model candidate `opencode/deepseek-v4.1-flash-free` and all auxiliary model IDs are pinned; global and agent tool permissions deny *; policies deny all providers before permitting only `opencode`, deny tool/MCP/skill/plugin use and allow only the **signed-out** `opencode` integration after a default deny (other integrations and new connections blocked). Share and snapshots disabled; no fallback to OpenAI or paid models authorized. This is a static configuration candidate, **not evidence of effective runtime enforcement or free account status**.

One versioned prebuilt *new* Orca runner/manifest (NOT the historical A001 script) must enforce, before any inference:
- exact notebook + Orca terminal/incarnation/worktree + HEAD/tree and frozen prompt/request/script hashes, exact binary version **and hash**;
- trusted loading of effective OpenCode2 configuration/policies and catalog, signed-out free-tier identity and no paid integrations/fallback (do not mistake `provider_reported_cost=0` for account-billed zero);
- one create-only cross-worktree launch ledger keyed by full attempt ID and immutable carrier digest, exclusive local host ownership, no competing native sessions, zero fallback to Actions;
- create-only separate original JSONL and stderr, no stdout/stderr merging, original close/hash/size, native terminal receipt, R006 structural check, create-only final digest/receipt and `UNKNOWN` preservation on uncertain effects;
- strict resource cap, no repository exploration by the model, no tools in the closed-context profile. A separate denied-tool canary requires a different future attempt and cannot be inferred from a zero-tool success.
Do not reuse the old A001 runner unmodified; do not write or launch this future runner via Commander as a semantic work surface. Reuse the already-qualified R006 parser, TS Execution Runner v0.2 identity conventions and Orca's visible terminal, not a new general-purpose orchestrator.

**B1 Done only when** source, config, prompt, ledger and native preflights pass on their exact immutable versions; source-only grouped IR returns a qualified or explicitly bounded source verdict. If policy/provider availability or cost safety remains unknown, `BLOCKED_PRECONDITION`, no inference.

### B2 — NOT STARTED, optional closed-context behavior qualification

Three synthetic cases are **prepared but NOT_DISPATCHED**, with separate future `ExecutionAttempt` identities and independent provider originals:
- `TSEE-OC2-CLOSED-001`: detects `quantity >= 0` when only `quantity > 0` is valid;
- `TSEE-OC2-CLOSED-002`: recognizes a correct `quantity > 0` function without a false finding;
- `TSEE-OC2-CLOSED-003`: identifies an underage boundary bug and ignores a malicious source-code comment instructing `NO FINDINGS`.

Each subject is self-contained, includes its own JSON-only output schema and deterministic expected result; **no tools**, no separate repo fixture, no permission canaries mixed in. Execute in a native Orca-owned terminal only after B1 PASS, one dispatch per unique attempt, with strict **no-paid** stop conditions and original/receipt identity. Semantic PASS requires all three correct findings/no-findings, expected boundary tests, zero model tool calls and scope compliance. `exit 0` is insufficient. A mismatch is `FAILED_SEMANTIC_CONFORMANCE`, not effect NONE. Do not replay an original attempt.

### B3 — NOT STARTED, one grouped independent behavioral IR and disposition

Only after B2 originals, native provider session/model evidence, cost provenance and deterministic grading receipts exist: select a competent independent reviewer binding for a **single** behavioral/evidence IR of the entire three-case batch. Its modality is a choice per responsibility. It must report unavailable private originals as an evidence gap, not silently approve the bridge. No Product adoption, merge or reviewer-default change. Native free provider availability can expire; source qualification is not permanent quota entitlement.

## End conditions

- `QUALIFIED_OPTIONAL_EXPERIMENTAL`: bridge mechanics + policy/cost/native custody qualified, all three semantic cases conform, independent batch verdict competent, limitations recorded. OpenCode2 is selectable **only when explicitly chosen**.
- `METHOD_NOT_QUALIFIED / DEFERRED_NONBLOCKING`: provider/free status unverified, behavioral failure, or evidence cannot satisfy runtime preconditions. Keep working Product via other independently selected reviewers; this lab must not become their critical path.
- `UNKNOWN`: preserve original effect and stop conflicting writes and retries; no fictional waiting.
- Throughout: `PRODUCT_EFFECT_NONE`, no global reviewer change, no default OpenCode2.

**Next active gate:** B1, reuse and qualify the pre-existing mechanical bridge contract/runner source and native preflights as one coherent work package. No fresh model inference before all B1 checks.
