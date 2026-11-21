# TS EE 003 — Q5B real ChromeDriver Common v0.1 producer (NONPRODUCT only)

status: EXPERIMENTAL_NOT_INTEGRATED
owner: TS_EXECUTION_ENGINEERING_OP
authority: NONPRODUCT_METHOD_ONLY
Product_authority: NONE
Product_effect: NONE
date: 2026-11-21
source_base: mauedgar/ts-execution-lab@44f0d98b43b9882825043caeed054fb16e22a364
branch: experiment/ts-ee003-feqa-v01-q5b-20261121
prior_Q5A_native: mauedgar/ts-execution-transport@fab19600282c49c23277141c23ca999dcd3adb8d:results/TS-EE-003-FEQA-V01-Q5A-NATIVE-20261121-001/TECHNICAL_RETURN.md

## Reuse and execution plan

Reuse Q4's real bounded W3C ChromeDriver synthetic browser method and Q5A's separately versioned Common v0.1 validator. One new isolated Ubuntu 24.04 GitHub Actions source candidate, four *sequential* one-session real ChromeDriver trials at 320,375,768,1440 widths, no historical run replay, no remote Product source/credentials. Each trial gets its own ephemeral Chrome profile and local HTTP fixture server, one POST /session, screenshot PNG, explicit session DELETE and direct driver/profile cleanup receipt. Missing or failed check fails closed, no automatic retry.

Q5B adds 3 bounded synthetic assertions beyond Q4: accessible text label on test button, native route refresh after product deep link, denied synthetic SKU returns 404 and is observed. It yields 14 PASS checks per width if successful. `console_http` Common scenario is bounded by local fixture HTTP 404/500 and seeded in-page JS-error handler, **not generic Chrome console/CDP or OS network telemetry**.

Each actual Q5B_REPORT.json and PNG is locally byte-verified by q5b_receipt_gate. Isolated host-side Chrome and ChromeDriver CLI version/SHA256/size are captured in TOOLCHAIN.json by q5b_toolchain_capture.py; file hash is not proof of the spawned child process. `q5b_to_common_v01.py` reads exact four report/PNG pairs and toolchain bytes, verifies actual bytes before create-only writing screenshots + sanitized structured LOG and one Common v0.1 receipt to isolated output. Strict receipt_validator_v01.py checks same actual local screenshot/LOG bytes, exact repository HEAD/tree, actual native GH run ID and scenario statuses. No TEST_VECTOR or `--diagnostic-only` in consumer path.

## Truthful network/security classification

Because this experiment does NOT intercept Chrome requests preventively, version v0.1 MUST encode:
- `functional_browser_status=PASS` only for its actual 8 mapped synthetic scenarios each PASS
- `network_assurance_status=OBSERVE_ONLY_UNATTESTED`
- `terminal_result=PASS_FUNCTIONAL_ONLY`
- `reported_verdict=PARTIAL`, never blanket PASS
- `network.enforcement=OBSERVE_ONLY`, `service_workers=NOT_VERIFIED`, `measurement_scope=LOCAL_FIXTURE_SERVER_ONLY`, `outbound_attempted/outbound_blocked/outbound_escaped=null` (NOT MEASURED, not zero traffic)
- `provider_native_verified=false`, `Product_accepted=false`, Product effect NONE.

This explicitly extends v0.1 Q5A method for honest fixture-only telemetry, preserving original stable `ts-ee/frontend-browser-qa/v0` unchanged. Under this scope even a strict validator exit0 and local artifact hashes establish only VALID_SHAPE_UNATTESTED; competent independent Control must separately join GitHub original run/job/head/tree/ZIP bytes and all inner files. The local report producer is never its own signed provider attestation.

## Negative and release conditions

Prospective negative tests reject false prevented egress, non-null counts when unmeasured, serviceWorker overclaims, mismatched source/artifact bytes, missing actual browser checks, unresolved session cleanup, forged Product approval or TEST_VECTOR strict acceptance. The existing Q5A v0/v0.1 tests run alongside Q5B. Local-source hostile multiwriter workspaces, exact driver child PID/namespace/descendant custody, ServiceWorker egress, full WCAG, real Aware SKU/stock and Aware Product negative tests remain NOT_QUALIFIED.

This is not a new generic platform or second execution controller. It does not accept/merge PRs, integrate stable method, change Aware Product, overwrite v0 or invoke OpenCode/Orca/Kernel/Beta Run. A genuinely independent Q6 reviewer must read exact candidate source in a separate nonimplementer context; same-chat scheduled reviewer is not acceptable. Only after method acceptance can Aware Control decide a new Product-owned A01 adoption candidate and receive its own real native CI and IR.
