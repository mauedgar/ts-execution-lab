# TS Frontend Browser QA — Common Execution Contract v0
status: EXPERIMENTAL_CANDIDATE / NOT_CANONICAL_PRODUCT_POLICY
owner: TS_EXECUTION_ENGINEERING
authority: EE_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE
first_consumer: Aware Control 005, pending competent Product adoption

## Purpose and ownership

A single reusable **execution/evidence method**, not a UI architecture and not a new Independent Review rule. TS EE qualifies the runner, deterministic receipt format, isolation and supporting adapters. Each Product retains SOT, source writers, test cases, review and integration/acceptance authority. The Developer has assigned QA method work to this TS EE chat rather than parallel Aware implementation. Published handoff != consumed or Product grant.

Reuse-before-build: E2 original `ts-execution-lab@fb0867350410f7cb6b16c5d7cd83e965950f5441`, native GitHub Actions `44529617929` PASS BOUNDED SYNTHETIC, Playwright 1.57.0, 320/375/768/1440, 5/5 seeded defects, zero good-case false alarms, 17 CI artifacts; E3 source-context method remains separate. Aware ChromeDriver and CI preflight code are Product-owned and **not** qualified E2E because run 44527745230 stopped at TypeScript 7 API loader.

## Binding and lifecycle invariants

1. Freeze immutable `repo@commit:tree`, lockfile identity, execution attempt, environment, *test source*, expected artifact and write-set. Source identity must be checked by native checkout, not by a branch label alone. Do not dispatch if an original RUNNING, terminal or UNKNOWN effect would conflict.
2. Never install unapproved or billable dependencies on Product. In experimental CI use pinned versions, isolated ephemeral runner, read-only source checkout and no credentials. No server access outside loopback without separate authority.
3. Identity → dependencies → integration → build → browser → evidence/readback are distinct stages, each explicit PASS/FAIL/NOT_RUN/SKIPPED with exact source evidence. A previous FAIL freezes that original; no automatic rerun or fallback.
4. Test the expected 320/375/768/1440 viewport widths, horizontal overflow, routing, deep-link and refresh, back/forward history, hidden/foreign/duplicate SKU, basic accessibility label/heading, focus/Tab/Enter and browser console/local HTTP failures. Declare unsupported dimensions NOT_RUN, not PASS. Basic checks are not WCAG/axe certification.
5. Preventive egress when `network.enforcement=PREVENTIVE_BROWSER_ABORT`: intercept before request, disable Service Workers, allow **only** explicit loopback origin, abort everything else and log attempted/blocked/leaked counts. A ChromeDriver post-hoc performance log is `OBSERVE_ONLY`, not evidence of isolation; OS-level egress may need separately qualified enforcement.
6. Supply machine-readable JSON with checked terminal identity, runtime versions, individual scenario statuses and limitations, screenshot/trace or log hashes, and original/transport custody. Artifact listing and SHA assertions alone do not prove the bytes were independently read. Provider result != Product release.
7. Use deterministic `receipt_validator.py` to classify report **shape and internal consistency** only. It does NOT independently authenticate GitHub, rehash remote binaries, rerun UI or give Product acceptance.
8. Route engine selection is optional (`PLAYWRIGHT_PYTHON` or `CHROMEDRIVER_NODE`); neither is canonically mandatory. The same receipt contract can be produced by both once qualified.
9. Aware is first intended consumer: retain TS7.0.2 typecheck/build CLI. Its `tests/integration/demo-routing.test.mjs:12` uses removed `typescript/lib/typescript.js` and `transpileModule`. Product owner may select a tested standalone transformation (Vite/esbuild if exact export and JSX semantics confirmed), or `@typescript/typescript6` for the legacy Compiler API with competent lockfile changes. Do not broadly downgrade TypeScript, edit Product from EE, reopen PR47, or re-run terminal CI.
10. Keep Aware historical #46 IR001 `NO_RECOMMEND/2F2A`, #47 `CLOSED_NOT_MERGED`, Product main at its own SOT. A future Product QA candidate needs independent Product authorization and a new immutable attempt/review, never a continuation of failed run `44527745230`.

## Machine-readable interface

`qa_report_v0.example.json` is a purely fictional **TEST_VECTOR** for validator qualification, not a provider receipt. Mandatory fields:
- `schema=ts-ee/frontend-browser-qa/v0`, `source.subject_kind=SYNTHETIC|PRODUCT_PREVIEW`, exact source repository, commit and tree, `attempt`, `runner` engine/version/native run ID/head commit;
- `stages` with identity/dependencies/integration/build/browser;
- `scenarios`: one status per `viewport,routing,history,deep_link_refresh,sku_negative,keyboard_focus,a11y_basic,console_http`;
- `viewports` 320,375,768,1440 each with PASS/FAIL/NOT_RUN;
- `network` enforcement, service worker policy and counts;
- `artifacts`: screenshot at each tested viewport and a trace/log, with SHA256 and byte size;
- `original`: custody method, immutable identity/hash, bytes and native reference, limitations and effect states.
A report with `TEST_VECTOR` custody may pass only **schema test**, never provider qualification.

## Qualification / DoD

D0 reuse and authority reconciliation; D1 schema and validator code with negative fixtures; D2 one native GitHub Actions self-test on immutable experimental source; D3 read back exact native run/job/status/log and per-commit identity; D4 if Green, `CONTRACT_SHAPE_QUALIFIED_BOUNDED_NONPRODUCT`, with transfer to Aware; D5 consumer E2E **not** qualified until Aware's competent new candidate runs integration+build+browser against exact Product HEAD and a separate IR.

If D2 blocked or failed, preserve that terminal, diagnose exact cause, publish limitations. Do not create a generic new dispatcher, new Product runner, canonical Recipe/Primitive or automatically adopt TS EE method in Tecnotron.

## IR001 repair candidate — provenance and actual producer/consumer gate

Original independent method review `mauedgar/ts-execution-transport@3651e8784175e324a9a2cdb98fd40dff3e1f3ede:results/TS-EE-FEQA-COMMON-METHOD-WEBINLINE-IR001-20261119-001/ORIGINAL.md` reported `METHOD_NO_RECOMMEND / 4 findings / 4 advisories`. The ORIGINAL remains immutable; no semantic replay.

Repair requirements:
- F01: reject contradictory browser PASS, malformed lifecycle and invented network claims. Even structurally valid received evidence returns `VALID_SHAPE_UNATTESTED`; native provenance and Product acceptance remain separate. Optional local artifact-root checks hashes/size but cannot authenticate remote CI.
- F02: **remove the executable `pure-typescript-loader.mjs`**. Replace it with `pure-typescript-transform.mjs`: sha256-pinned and transform-only (no dynamic `import()`, no evaluation). It does NOT claim no imports/side effects in the resulting JS; callers must only evaluate independently authorized trusted source in an isolated Product test gate.
- F03: actual `e2_browser_qa.py` writes E2 original `RESULT.json`; bounded `adapters/e2_to_common.py` verifies 16 local screenshot/trace hashes and converts the real E2 receipt into `COMMON_RECEIPT.json`. CI immediately validates this actual report (with the current Git SHA/tree/run ID) and only then uploads evidence. Test vectors remain explicitly non-native.
- F04: capture label status at initial screen before navigation; bind seeded negative sensitivity to precisely five injected classes. Routes, keyboard and deep refresh are positive-check-only; screenshots are of initial catalog, while trace contains later interactions. Replace local HTTP 404 fixed-delay race with a Playwright response event. No unsupported universal sensitivity claim.
- A01/A02/A03/A04: network prevention is scoped to the Playwright context with blocked Service Workers; OS-level egress is not proven. Source runner artifacts verified locally, native artifact ZIP digest recorded separately, ZIP internals not independently read back here; retain provenance limitations. Extra tests validate negative report states and local artifact bytes. TypeScript 7 solution remains method-only until a distinct Aware Product run.

DoD: true E2→common producer/consumer interoperability on one *new* immutable nonProduct candidate, 16/16 existing + expanded tests, updated transform-only Node tests, full synthetic GOOD/BAD matrix, original native CI receipt and artifacts, then a distinct independent method IR. **Do not promote to Tecnotron or merge Aware** from these component-level results.

## IR002 B001 S1/S2 reconciled method repairs (nonProduct)

Two original independent reviewer results are immutable, byte-identical in GitHub Transport:
- S1 `mauedgar/ts-execution-transport@db21f3dcc88aa8d651b35e25f75693a439781fe8:results/TS-EE-FEQA-COMMON-B001-WEBINLINE-IR002-S1-20261119-001/ORIGINAL.md`: 2 findings / 3 advisories.
- S2 `mauedgar/ts-execution-transport@c9423de2926e53a8e830ba5f308e4e92e3164606:results/TS-EE-FEQA-COMMON-B001-WEBINLINE-IR002-S2-20261119-001/ORIGINAL.md`: 2 findings / 3 advisories.

Distinct experimental successor (not retry):
- S1 F01: both-direction browser/verdict checks; failed browser must show grounded failed scenario/viewport. S1 F02: external native run/tree/readback remains a separate Control qualification requirement; converter fields and CLI values are NOT native attestation. Shape validation alone never grants a provider PASS.
- S1 A01–A03: fail malformed nested receipt safely, contain local artifacts within non-symlink evidence roots, test negative cases and report strict local limitations.
- S2 F01: test keyboard Enter from `/about` and require a URL transition to `/catalog`; separate negative fixture that disables Enter must remain at `/about`; converter now checks both.
- S2 F02: explicitly bound network counts to observed browser route interceptions, require route abort navigation to fail; do not claim all system outbound blocked; no OS-level egress verification.
- S2 A01–A03: await native 404 event, preserve context-level route and Service Workers blocking, record provider artifact ZIP independently outside same job; OS/browser binary reproducibility not asserted.

Source-only CI PASS, local artifact checks and synthetic browser PASS remain **necessary but insufficient** for cross-product QA method adoption. Competent Control separately observes original provider-native run status, head/tree and artifact metadata; it does not infer identity from self-declared E2→common JSON. Aware QA still requires new Product grant, exact candidate integration+build+browser, separate IR.

## B002 IR003 repaired in distinct B003 experiment

Two independently terminal originals (both LOCAL_METHOD_NO_RECOMMEND) are immutable:
- S1 `ts-execution-transport@81e08cf095fc188e1a0e73483683732ca8a9a98c:results/TS-EE-FEQA-COMMON-B002-WEBINLINE-IR003-S1-20261119-001/ORIGINAL.md` (1F/3A): the blocking native provenance concerns **provider-level qualification**, not an observed false `VALID_SHAPE_UNATTESTED` acceptance.
- S2 `ts-execution-transport@8629a9f5a44e40299d8fc9f663871968d19295ce:results/TS-EE-FEQA-COMMON-B002-WEBINLINE-IR003-S2-20261119-001/ORIGINAL.md` (2F/4A): navigation timeout previously risked losing a complete negative receipt and outbound proof used a brittle Chromium error string.

B003 candidate repairs S2 independently: a failed Enter now adds `KEYBOARD_ACTIVATION` without losing the source `RESULT.json`; disabled-Enter negative fixture requires focused target AND exact unchanged /about URL; `route.abort` returns a typed structured source event, while external navigation must fail (timeout is not proof); per-row outbound observed counts equal source variant totals and converter rejects mismatches; malformed runtime/width fields fail closed. Method scope remains **only the browser context**, Service Workers blocked but no OS firewall claim. Always distinguish native GitHub run/artifact metadata from verified original nested ZIP data, neither of which the converter can attest independently.

D4 remains experimental/nonProduct, `VALID_SHAPE_UNATTESTED` cannot be promoted by any report without native external readback. B003 new native CI and independent review must be reconciled separately before first-consumer suggestion.

## B004 — Developer completeness requirement, limited zero-undisclosed-debt target

Developer ruled **no new consumer handoff until integral method completion and competent canonical adoption**. This specifically reopens IR004's nonblocking A01–A03 and A04 provenance as NEW bounded experimental requirements, not as an implicit replay of B003 original `44570872017` or IR004.

- A01 fail-closed runtime terminal: E2 source `TS_EE_E2_FAULT=runtime_exception` triggers a synthetic Playwright-stage runtime exception; source writes `TERMINAL_FAILURE.json` create-only and exits nonzero without inventing a successful `RESULT.json`. Failure-receipt fsync is best effort, not proof of atomic power-loss durability. No routine overwrite/retry.
- A02 live negative detector sensitivity: `keyboard_block_positive` disables positive Enter in a separate browser run; `external_fulfill_simulated` supplies a successful response **locally via Playwright `route.fulfill` without any external network call**, proving the detector flags absent external `route.abort`. Neither test claims malicious OS-level egress containment.
- A03 type checks before summing nested `blocked_external` values, typed viewport inventory/boolean fields, safe artifact source inode opens with `dir_fd` + `O_NOFOLLOW` + regular-file `fstat`, bounded bytes and SHA256. The parent workspace remains trusted, ephemeral and runner-owned. **NOT a general hostile filesystem isolation layer or OS directory-handle attestation**.
- A04 an independently read-back B003 GitHub ZIP was checked 712409 B / provider SHA256 `515405bbe075b58bbcd4ef118cb93d50f3f43bfbeb33534daa322e3f608fcb14` with 18 members, 16/16 matching screenshot/trace content hashes in both JSONs. See `mauedgar/ts-execution-transport@0b430a2920894d3379d379a77e27297ca4cc1bbd:results/TS-EE-FEQA-CANONICAL-ADOPTION-READINESS-20261119-001/DIAGNOSTIC.md`. Future B004 `runtime.chromium_executable_sha256` is the **Playwright-resolved distribution executable path**, not necessarily the actual headless child process executable; do not mislabel that digest as full runtime-binary attestation. Native provider reads remain Control-owned outside converter. Evidence ZIP readback must be independently repeated for each new candidate.
- B004 is still **NONPRODUCT**. Passing CI + new source IR cannot alone integrate this into `ts-execution-lab:main`, Tecnotron SOT or Aware Product. An explicit competent adoption disposition and a reviewed, collision-safe PR against current canonical main are required. No broader browser security, WCAG, Cloud authorization or Product release acceptance.

DoD for B004: new HEAD/tree and attempt; 50+ Python schema+bridge tests, 9 Node tests, E2 GOOD 0/BAD 5, 3 independent live-negative fault runs (Enter failure, simulated allowed external success, exceptional failure receipt), actual E2→common + 16 local hashes, correct native job and artifact; full independent delta IR; independent ZIP readback; no new Aware handoff pending canonical integration. This is a scope-bounded no-undisclosed-method-debt qualification, not universal zero risk.

## B005 — B004 IR005 findings and consumer mode repair

Independent B004 method IR005 originals were terminal: S1 `LOCAL_METHOD_RECOMMEND/0F3A` 5/5 FULL, S2 `LOCAL_METHOD_NO_RECOMMEND/1F4A` 5/5 FULL, both original Git/library preserved without semantic reruns. S2 F01 requires not merely a failing detector but evidence that the **actual browser observed a successful simulated external HTTP 200**.
Distinct B005 changes `e2_browser_qa.py` to report a structured exact-url `route.fulfill(status=200)` event after fulfillment returns, the returned navigation `response.status==200`, final exact URL, absence of timeout/PlaywrightError and no abort. In fault mode, `FAULT_INJECTION_UNPROVEN` is raised if any proof is absent; `EXTERNAL_NOT_BLOCKED` still indicates the deliberate escape. `test_e2_runtime_faults.py` asserts every variant and viewport contains actual 200/event/success and no unproven marker. All fulfilled traffic remains entirely local to Playwright interception with **zero real external egress**.
S1 A03 consumer ambiguity: `receipt_validator.py --require-local-bytes` enforces full local screenshot/trace byte verification before CLI 0 is usable for a **consumer-side evidence-shape gate**, while remaining `VALID_SHAPE_UNATTESTED` and `provider_native_verified:false` (native Control GitHub join remains separately required). Without that switch, default shape-only mode remains a diagnostic, not a Product QA acceptance.
Do not mistake `browser_binary_sha256` for true child-executable attestation: E2 hashes Playwright's resolved distribution executable, not necessarily a non-default E2_CHROMIUM_PATH override or Chrome headless child process. The verified B004 provider ZIP, source and IR originals remain historical immutable evidence. For hostile multi-writer roots the contract remains OUT_OF_SCOPE; CI evidence root must be isolated and trusted, and Product cannot infer OS egress security or WCAG coverage.
B005 requires new native CI with 54+ Python/9 Node/3 runtime-fault checks, independent source-only delta IR and independently verified ZIP. Only after method evidence disposition may an **exact, cleanup-reviewed** proposed adoption into TS EE main be considered. No new Aware handoff before these gates and competent canonical acceptance; Product authority NONE.
