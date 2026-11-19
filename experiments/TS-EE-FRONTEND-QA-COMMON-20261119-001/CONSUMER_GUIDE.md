# TS Frontend Browser QA — Common Consumer Guide v0

status: EXPERIMENTAL_NONPRODUCT / CANDIDATE_B006
authority: TS_EXECUTION_ENGINEERING_METHOD_ONLY
Product_authority: NONE
Product_effect: NONE
first_consumer_intent: Aware Commerce, only after competent Product adoption

## Single-source consumer contract

This is a method/evidence interface, not a new runner, scheduler, release approver, Product SOT or generic web deployment adapter. The qualified method source lives in ts-execution-lab; the frozen execution subject must be identified by exact commit/tree. No downstream control may silently assume that the synthetic CI PASS also proves its Product UI.

Required consumer request:
- exact Product repo, immutable HEAD/tree, test/build lockfile, QA owner and write-set;
- ExecutionAttempt identity and original result target, previous attempt/effect reconciliation;
- environment and browser/driver version, isolation/egress policy, allowed local origin;
- 320, 375, 768, 1440 px; routes/deep links, history, hidden SKU, keyboard Tab/Enter, label/heading basic accessibility, JS/HTTP errors, images and traces;
- independent Control source/CI and artifact readback and separate Product review;
- no repeat of terminal/UNKNOWN attempts, no Product merge or deployment without its SOT grant.

Available engines are optional Playwright Python or ChromeDriver Node. The experiment qualifies the Playwright synthetic adapter only. Aware's ChromeDriver QA has not run against its Product candidate because the original TypeScript 7 JavaScript Compiler API preflight failed. No automatic fallback.

## Validator commands: safe by default

Consumer invocation:
  python receipt_validator.py COMMON_RECEIPT.json --artifact-root ISOLATED_ROOT --expected-commit HEAD --expected-tree TREE --expected-run-id NATIVE_RUN_ID

A successful exit verifies internal consistency plus actual local evidence bytes. The report remains VALID_SHAPE_UNATTESTED and Product_accepted=false, provider_native_verified=false. The Control must separately verify GitHub native run/head/tree/job/conclusion and original artifact ZIP digest plus each nested file byte hash. Never promote CLI exit 0 directly to native Product PASS.

Diagnostic TEST_VECTOR shape only:
  python receipt_validator.py qa_report_v0.example.json --diagnostic-only

Only explicit diagnostic mode may return code 0 for VALID_TEST_VECTOR_SHAPE_ONLY. Default consumer mode and --require-local-bytes forbid TEST_VECTOR even if its synthetic images/traces match their self-declared hashes. A combined diagnostic+strict request fails closed. Any missing or malformed input yields nonzero. --require-local-bytes is retained as an explicit compatibility guard.

## Evidence semantics and stop conditions

Producer JSON is never an independently signed provider receipt. A host-only report is not proof of complete Product route coverage, OS-wide network denial, WCAG conformance, production readiness or Product acceptance. If a stage fails, preserve that original, label all downstream NOT_RUN and do not relaunch it automatically. If artifact readback or native identity is ambiguous, stop at UNKNOWN or BLOCKED.

Browser interception and ServiceWorker blocking apply only within the Playwright browser context. Hostile/multi-writer artifact roots and actual child Chromium executable provenance need separate qualification. Runtime failure receipts are create-only when an output directory exists; the native provider remains authoritative for failures before directory creation. Browser binary distribution SHA is local-run metadata, not independent host-process attestation.

## @ proposal — TS Frontend QA (thin router)

Expose a private skills-based @TS Frontend QA entrypoint that reads the frozen common contract and accepts requests like:
- "Prepare QA validation request for this Aware commit"
- "Reconcile native Browser QA original and evidence"
- "Which QA engine is qualified on this runtime?"
- "Audit missing coverage/attachments before an IR"

It must NOT implement another browser engine or independent orchestrator. It must NOT dispatch Product CI, change PRs, release, merge, or gain Product authority by being invoked. It returns a grounded plan and exact refs. A new producer invocation still needs its competent owner and explicit grant.

Plugin v0 should include: read-only method lookup, consumer request schema, engine-selection decision table and original-effect reconciliation checklist; optional GitHub connector when available. A plugin publish/installation is separate from Git source integration, and is not a Tecnotron canonical Product adoption.

## Qualification roadmap, evidence and adoption conditions

G0: preserve B001–B005 native/IR original results and review findings; no retry.
G1: B006 strict consumer F01 repair and real CLI negative tests.
G2: native CI: Python/Node, actual synthetic browser, fault-injection, real E2 conversion, byte-level artifact validation, B006 strict/default/diagnostic matrix.
G3: independent source delta IR and native artifact readback. No auto-adoption from CI alone.
G4: collison-safe nonProduct method integration in ts-execution-lab main, subject to its competent review and explicit Developer disposition.
G5: publish versioned, stable method reference and optionally a private thin @ plugin. No duplicate Product owner.
G6: Aware Product's owner tests a new exact candidate: TypeScript 7 loader repair, identity, npm ci, integration, Vite build, browser QA, native artifacts, independent Product review and acceptance. TS EE synthetic gate is not that proof.

Completion criteria: G1–G3 PASS at exact B006 subject; G4–G5 separate competent integration and publication. G6 requires Aware Product authority and may not be performed by this nonProduct Lab without transfer. Unqualified capabilities must be labeled excluded, not silently treated as resolved debt.
