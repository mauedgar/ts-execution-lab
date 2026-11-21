# TS EE 003 — ChromeDriver Q0/Q1 candidate B001

authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
product_authority: NONE
product_effect: NONE
status: EXPERIMENTAL_NOT_QUALIFIED
source_base: mauedgar/ts-execution-lab@b451fe41b789a02e56cb5896b9db669467c52bfa
branch: experiment/ts-ee003-chromedriver-b001-20261121

## Scope

One real ChromeDriver lifecycle trial per isolated GitHub Actions matrix job (two jobs). Each job creates one ephemeral Chrome profile and measures GET /status separately from one native W3C POST /session. DELETE /session and process/profile teardown are mandatory. Synthetic protocol tests independently test W3C success, invalid response, timeout and redaction, without external origins.

No historical Aware CI, Product source, model inference, secrets or external URLs are used. Browser route and viewport scenarios remain NOT_RUN. network=OBSERVE_ONLY does not prove interception or OS-level egress prevention. No raw driver verbose logs, WebDriver session IDs, screenshots, cookies or bearer tokens are exported. The JSON is a producer self-report, not independent native provider attestation.

GitHub ubuntu-24.04 runner is NOT an immutable Chrome/ChromeDriver pin. Each job must read actual versions, resolved executable paths, file hashes, image version and source commit/tree; missing tools fail closed. Two trials do not establish robust latency percentiles, guaranteed ETA, or grounds to raise historical 12/15-second timeouts.

## Expected gates and exclusions

B001 is a bounded Q0 real session/teardown observation plus Q1 synthetic protocol checks. It does NOT qualify generic ChromeDriver Node Common v0 end-to-end, native child PID custody, browser route QA, network enforcement, independent review or Product use. Next qualified gates: deterministic native process-exit and cleanup-failure fixtures; loopback GOOD/BAD routes and four viewports; negative privacy tests on ZIP+logs; compatible versioned Common receipt and full strict validator; independent Q6 review of exact code, native CI/jobs/HEAD/tree, ZIP/inner hashes.

Current Common v0 requires PREVENTIVE_BROWSER_ABORT whenever browser=PASS. A truthful ChromeDriver OBSERVE_ONLY browser PASS must not weaken this invariant. A compatible, versioned extension must distinguish functional test PASS from independently proven network safety. Aware A01 disposition remains separately BLOCKED_SCHEMA_REQUIREMENT until such method contract is qualified and Product-owner adopts it.

No unconditional retries, no automatic fallback to another engine, no Product merge/deploy/adoption.
