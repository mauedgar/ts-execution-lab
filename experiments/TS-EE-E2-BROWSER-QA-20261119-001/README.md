# TS EE E2 Browser QA adapter — experiment, not Product

Responsible: TS Execution Engineering. Product authority/effect NONE. 
Synthetic localhost-only app, no external access, uploads only test evidence.
Source fixture embedded in versioned runner e2_browser_qa.py.
QUALIFICATION: 4 viewports (320,375,768,1440), overflow, catalog product and hidden SKU, deep-link/back-forward, role/label, console errors, HTTP errors, outbound WhatsApp blocked by context.route, screen PNG and trace ZIP with SHA-256.
Two variants: expected GOOD 0 issues, BAD must flag OVERFLOW, LABEL, HIDDEN_SKU, CONSOLE, HTTP. This is a bounded seeded-detection test, not Product E2E or full axe/WCAG.
Read-only local browser may be blocked by administrator; any such failure is HOST_BLOCKED, not a QA PASS.
CI pinned to Playwright Python 1.57.0; GitHub Actions isolated branch. Run with python e2_browser_qa.py --output NEW_PATH. Each output is create-only, never overwrite.
