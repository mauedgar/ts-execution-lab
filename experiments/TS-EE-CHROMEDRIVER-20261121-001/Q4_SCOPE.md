# TS EE 003 — Q4 ChromeDriver real synthetic browser (NONPRODUCT)

status: EXPERIMENTAL_CANDIDATE__NOT_INTEGRATED
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE
source_base: mauedgar/ts-execution-lab@2df415398dd90d9b8cc5fae04483cab9c38575af
prior_Q0_Q3: mauedgar/ts-execution-transport@a38223e1840071f5c26d0f57e7b36b2cb2272959:results/TS-EE-003-CHROMEDRIVER-B003-NATIVE-20261121-001/TECHNICAL_RETURN.md
branch: experiment/ts-ee003-chromedriver-q4-20261121

This candidate performs **one** ChromeDriver W3C POST /session per isolated native GitHub Actions matrix job across four declared viewport widths (320,375,768,1440). Chrome's mobileEmulation deviceMetrics is fixed at session creation, avoiding unstated runtime viewport overrides; each job reports actual innerWidth and compares it to its requested width.

The browser navigates to only a newly created synthetic loopback HTTP server. It tests a simple catalog h1, no horizontal overflow, keyboard Tab/Enter on an actual button, direct product deep link and native browser Back, controlled local HTTP 404 and 500 route visits (as reported by the fixture server), one deliberately seeded JS error observed by fixture-owned in-page error handler, and a real PNG screenshot of the synthetic catalog. The script never opens Aware or any external Product URL; the page contains no user content or credentials.

Evidence is an allowlisted Q4_REPORT.json with one screenshot PNG for the requested width. `q4_receipt_gate.mjs` rehashes locally read screenshot bytes and asserts 11 real scenario statuses, source viewports, cleanup outcomes, network policy and seven corrupted receipt fixtures; upload steps preserve one JSON and one synthetic PNG per job. Native CI original HEAD/tree/jobs, ZIP and all nested member hashes must be independently joined; a local self-report does not authenticate GitHub run identity or Product acceptance.

The script must fail closed when ChromeDriver cannot start, a route assertion fails, screenshot is invalid, session DELETE fails, direct driver exit cannot be observed, local server close fails, or profile directory cannot be removed. It reports `descendant_termination=NOT_ATTESTED`: direct ChromeDriver exit != all Chrome descendants complete. Also port reservation is TOCTOU and port owner is not independently native-attested. `--no-sandbox` is CI-only exception.

Network is `OBSERVE_ONLY`: loopback origin and Chrome flags `--disable-background-networking` **do not prove preventive egress isolation** or OS-wide network denial. HTTP 404/500 checks read the local server's own counters, not full native browser CDP network performance events. JS error detection is on a seeded fixture and is not generic global console surveillance, and simple semantic h1/focus checks are not WCAG/axe certification.

This is a bounded real synthetic ChromeDriver functional qualification, not a new generic QA platform, Product test implementation, all viewport WCAG, full process custody, Common v0/v0.1 producer, or Product release. Existing Common v0 strict validator still requires PREVENTIVE_BROWSER_ABORT on browser PASS; Q4’s `PASS_BOUNDED_Q4` cannot be represented as `Common v0 browser PASS` without violating that guarantee. The compatible v0.1 source proposal is still unqualified. Q5 schema+producer/native artifact binding and Q6 genuine external Independent Review remain separate gates.

No historical B001/B002/B003 workflow rerun. The new Q4 workflow, committed after source and test files, creates the only Q4 original run. Any terminal failure is preserved; no hidden retry, no fallback or automatic Product integration.
