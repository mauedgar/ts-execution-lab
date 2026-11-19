# TS Execution Engineering — Frontend Browser QA Common v0

status: LAB_MAIN_METHOD_BASELINE / QUALIFIED_BOUNDED_SYNTHETIC
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE
method_owner: TS Execution Engineering
first_intended_consumer: Aware Commerce, NOT_ADOPTED
canonical_lab_integration: mauedgar/ts-execution-lab@a67b364c6a5291b32bdeccce91ed3cd8fa1ca06c
method_source_commit: 5c7d4a3d78d37f948ac9cdd37b919761ec4562ee
method_source_tree: 03925a7d6d7f05cc3a405a656877f10f3b527dda

## How to invoke this contract

This is the stable TS EE **method entrypoint** for frontend Browser QA requests. Read the exact source and the current Product SOT before applying. It is not a new orchestrator, an automatic CI dispatcher, a Tecnotron canonical Product Recipe, or a Product acceptance mechanism.

1. Read the detailed method at `experiments/TS-EE-FRONTEND-QA-COMMON-20261119-001/CONTRACT.md`, and the consumer instructions at `experiments/TS-EE-FRONTEND-QA-COMMON-20261119-001/CONSUMER_GUIDE.md`.
2. Preserve Product owner/SOT and exact Product source commit/tree/lockfile, intended QA scope, qualified browser runtime and explicit action grant. Existing attempts are observed and reconciled FIRST; no duplicate terminal or UNKNOWN dispatch.
3. Choose an engine only if supported: Python Playwright has bounded synthetic evidence; ChromeDriver Node is an optional adapter interface **not yet independently qualified for Aware's Product source**.
4. Use the common report schema with 320/375/768/1440 widths and declared scenario statuses, actual screenshot/trace bytes, source+native IDs, limitations, and exact preserved original effect. A missing test is NOT_RUN; no invented coverage.
5. Execute consumer validation with `receipt_validator.py COMMON_RECEIPT.json --artifact-root ISOLATED_EVIDENCE_ROOT --expected-commit HASH --expected-tree TREE --expected-run-id RUN`. The **default is strict and fail closed**: any `TEST_VECTOR`, even with matching local artifacts, is not evidence and returns nonzero. With true locally read bytes, a real report can return `VALID_SHAPE_UNATTESTED` and exit 0. This still does NOT mean provider authenticated, Product approved or merge allowed.
6. Only `--diagnostic-only` allows schema-only vectors to exit 0. It is forbidden in Product consumer acceptance wrappers. Consumer command should allowlist exact `VALID_SHAPE_UNATTESTED` **and** require a competent external provider-native join of original GitHub run/job/head/tree/artifact identities, ZIP SHA-256 and nested byte hashes.
7. Return an auditable result to Product Control. Review scope, findings, acceptance and merge remain in that Product's lifecycle; TS EE only supplies the execution/evidence method.

## Verified bounded evidence and immutable reviews

- Distinct original GitHub Actions `44600037548`, attempt 1, source `5c7d4a3d78d37f948ac9cdd37b919761ec4562ee`: **61/61 Python**, **9/9 Node**, **3/3 live synthetic browser fault-injection checks**. GOOD 0 detected defects, BAD five seeded categories detected. E2 actual result is converted and locally validated as `VALID_SHAPE_UNATTESTED`.
- Native artifact `14567713255`: 2155499 bytes, `sha256:6003eebbedb04a6d98790cf973ba0274cea08c11ec5d6a84540f5c91cba6ab0b`, independently downloaded and 16/16 healthy screenshot/trace member hashes checked. Reference: `mauedgar/ts-execution-transport@9da8d64339a53069f7a646c7320b7b2116f3fe7e:results/TS-EE-FEQA-B007-STRICTDEFAULT-NATIVE-READBACK-20261119-001/TECHNICAL_RETURN.md`.
- Independent IR008 exact source, **LOCAL_METHOD_RECOMMEND / 0F4A / 5/5 FULL_READ**, single execution; Library and Git Transport original byte-identical `mauedgar/ts-execution-transport@907c1f6be370c5551607e6c91afc2f84443bb8cc:results/TS-EE-FEQA-B007-STRICTDEFAULT-WEBINLINE-IR008-20261119-001/ORIGINAL.md`.
- GitHub PR #66 merged into **TS EE LAB main** commit `a67b364c6a5291b32bdeccce91ed3cd8fa1ca06c`; source blob for validator matches reviewed `36c207326fff0da2231b731422323af186511a49`. Historical B006 sibling `bba92133a4a74feb422687d63eae14e5a9e778a3` IR007/CI is preserved, not separately integrated.
- Original B007 candidate run `44599888316` terminal FAILURE is preserved (stale historical test expectation). Corrected successor is separate, not retry.

## Explicitly excluded qualifications and debt boundary

The method has **four nonblocking IR008 advisories**, not an absolute zero-debt release: diagnostic-only is broad and MUST be unavailable to consumer acceptance wrappers; evidence path checks rely on a trusted isolated CI workspace and are not safe for hostile multi-writer roots; converter/validator cannot independently attest provider run, exact launched Chromium binary, native ZIP upload or OS-wide egress; actual Aware frontend build, TS7 test loader repair, ChromeDriver QA, WCAG/axe certification and Product release all require distinct competent gates.

Treat these as explicit preconditions/exclusions, not claims of universal support. A consumer requiring adversarial workspace support or OS-wide network proof must qualify that capability separately. No Product source write, PR, Independent Review, merge, production deployment or Tecnotron adoption is granted by this lab integration.

## Optional @ entrypoint

Private, skills-only `TS Frontend QA` plugin version 0.1.0, `https://chatgpt.com/plugins/plugins_6aff5120ae14819190a85f34e7b57d1f`. It routes method preparation and native QA result reconciliation; it is not a browser engine, scheduler, Product executor or alternative SOT. Installation/activation requires user action, and plugin invocation must retrieve the current stable TS EE method and Product SOT. This optional convenience interface cannot authorize execution or Product adoption.
