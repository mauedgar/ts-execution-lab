# TS EE 003 — Frontend QA Common v0.1 compatibility (candidate B001, NONPRODUCT)

status: EXPERIMENTAL_NOT_CANONICAL_NOT_ADOPTED
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE
date: 2026-11-21
source_base: mauedgar/ts-execution-lab@0cea5c2c923bc264a01750cbcc1f3306ff096467
branch: experiment/ts-ee003-feqa-v01-20261121
stable_v0_validator_sha: 36c207326fff0da2231b731422323af186511a49
versioned_new_validator: experiments/TS-EE-FRONTEND-QA-COMMON-20261119-001/receipt_validator_v01.py

## Why this is a separate version

Existing `ts-ee/frontend-browser-qa/v0` requires PREVENTIVE_BROWSER_ABORT for all browser=PASS. ChromeDriver observed network mode OBSERVE_ONLY cannot satisfy that assertion without falsifying evidence. B003 and Q4 genuine ChromeDriver experimental trials already showed real sessions, native fault fixtures and synthetic browser tests; those do NOT establish preventive browser/OS network blocking or actual Aware Product QA. Native Q4 source/result at `mauedgar/ts-execution-transport@9a2d6f73ca729db2805705f982e70d7cfa1f8a8d:results/TS-EE-003-CHROMEDRIVER-Q4-NATIVE-20261121-001/TECHNICAL_RETURN.md`.

This B001 Q5A is a **separate validator source and synthetic fixture qualification only**, not yet a ChromeDriver receipt producer or Product consumer. The stable v0 file and its qualified tests remain byte-identical. No schema mutates any Product or OS.

## New v0.1 required fields

Keep all v0 source/HEAD/tree, attempt, native run identity, expected 8 scenarios and 4 viewports, screenshot and TRACE/LOG artifact sizes/hashes, original custody, strict TEST_VECTOR rejection, local artifact root safety and external provider join. New required fields:

- `schema=ts-ee/frontend-browser-qa/v0.1`
- `functional_browser_status=PASS|FAIL|NOT_RUN`
- `network_assurance_status=PREVENTIVE_BROWSER_ABORT|OBSERVE_ONLY_UNATTESTED|NOT_RUN`
- `terminal_result=PASS_WITH_BROWSER_ABORT|PASS_FUNCTIONAL_ONLY|FAIL|NOT_RUN`
- `provider_native_verified=false`, `Product_accepted=false` mandatory in producer receipt. Neither field is writeable to true under this method.
- Browser PASS still requires all 8 specified scenario statuses PASS and 4 viewports PASS, four screenshot bytes and at least one actual TRACE or sanitized LOG. ChromeDriver browser PASS also requires browser version and file SHA256/size, driver version and file SHA256/size; these are **producer metadata**, not independent attestation of running executable.

If `stages.browser=PASS` but `network.enforcement=OBSERVE_ONLY`, only `functional_browser_status=PASS`, `network_assurance_status=OBSERVE_ONLY_UNATTESTED`, `terminal_result=PASS_FUNCTIONAL_ONLY`, `reported_verdict=PARTIAL` are permitted. Service workers MUST be NOT_VERIFIED and blocked traffic count zero, to avoid falsely claiming prevention. Such a report may pass strict internal shape + actual local byte validation, but **must never** imply security policy satisfied, native provider verified or Product accepted. `VALID_SHAPE_UNATTESTED` does NOT equal Product acceptance. The consuming Product must explicitly decide if OBSERVE_ONLY is allowed; no TS EE authority to waive network requirements.

With independently proven `PREVENTIVE_BROWSER_ABORT` the policy may carry `network_assurance_status=PREVENTIVE_BROWSER_ABORT`, `terminal_result=PASS_WITH_BROWSER_ABORT`, `reported_verdict=PASS`, service workers blocked and outbound_escaped=0. Even then Product_accepted remains false; browser-context prevention is not OS-wide prevention.

Nonexecuted browser stages must not claim functional PASS or network assurance. Failures must be clearly FAIL; missing scenario coverage is not silently promoted to PASS.

## Scope of native B001 tests

- Diagnostic-only synthetic ChromeDriver OBSERVE_ONLY fixture, clearly `TEST_VECTOR` and fictitious native IDs/hashes; strict CLI MUST reject it with nonzero exit.
- Ten mutations should fail closed: false Product/provider attestation, success verdict when security is unproven, preventive policy overclaim, serviceWorker/block claims, missing browser/driver hash and missing trace/log.
- A synthetic preventive-policy vector checks distinct schema semantics without claiming a real security test.
- Local bytes test rehashes actual temporary files and classifies only VALID_SHAPE_UNATTESTED, then corrupts one file and requires rejection.
- Original v0 validator is untouched and still rejects observe-only browser PASS; old v0 tests included in candidate CI.

## Remaining qualification gates

Q5B: build a REAL native ChromeDriver four-viewport producer that binds exact source/runner/action jobs and screenshots/LOG to actual bytes and v0.1 schema, with new immutable attempt; strict consumer gates cannot use this diagnostic-only TEST_VECTOR. Distinguish host self-reports and external GitHub original job/artifact ZIP+inner hash checks. No schema change to Product before competent Aware/Method adoption.

Q6: full source read and genuinely independent review of versioned validator+producer+runtime artifacts in a separate reviewer context, not an automation inheriting this implementation conversation. Only then can TS EE method owner consider NONPRODUCT integration; Aware Product separately decides/implements its A01 consumer under its SOT, new head/tree, native QA and Independent Review.

No automatic rollback, retry, Product integration, Kernel/Beta Run effect or Orca config change. This is an isolated method candidate.
