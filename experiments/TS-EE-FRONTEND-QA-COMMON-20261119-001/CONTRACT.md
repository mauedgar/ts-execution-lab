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
