# B003 distinct repair / positive receipt cross-field gate (2026-11-21)

B002 original `mauedgar/ts-execution-lab@785ac7f23f6a69bfcea7154ea404517a33654453`, Actions run `44867532566` attempt 1, concluded CI SUCCESS but **SEMANTIC_NO_RECOMMEND**. Both B002 positive JSON reported contradictory `overall=PASS_BOUNDED_DIRECT_DRIVER` and `error_class=CLEANUP_OR_RUNTIME_FAILED`. B002 is terminal; do not repeat or rewrite its original run.

B003 freezes a new source candidate from B002, repairs only the stale error-class comparison in `real_session_probe.mjs` and adds `positive_receipt_gate.mjs`. This gate verifies the actual real-session JSON (not merely synthetic fixtures) requires success status and `error_class=NONE`, DELETE ACK, remote DELETED_CONFIRMED, direct driver exit observed, profile cleanup PASS, explicit descendants/port NOT_ATTESTED, browser scenarios NOT_RUN, network OBSERVE_ONLY and provider/Product acceptance both false. It deliberately mutates seven positive-receipt vectors and proves the gate rejects contradictions, overclaims and unexpected data. The native CI runs real session once per isolated job and then applies the consistency gate on its actual bytes.

B003 remains an **experimental session lifecycle and receipt consistency** qualification, not full ChromeDriver/Frontend QA Common or Product acceptance. B002 four negative process/timeout/cleanup fixtures are reused as source tests in a *distinct new execution* under B003; do not confuse this with rerunning B002. Strict Common v0 baseline unchanged; v0.1 still PROPOSED_NOT_ADOPTED. Original provider ZIP SHA and inner hashes must be joined before calling B003 terminal qualified. Independent Review must use a distinct reviewer surface with no implementation context; prior IR001 was BLOCKED_INDEPENDENCE.

# TS EE 003 — ChromeDriver B002 repair and negative-fault matrix

status: EXPERIMENTAL_NONPRODUCT_CANDIDATE_NOT_ADOPTED
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_effect: NONE
original_B001_head: 72a8e606b1dd3e75c38a55fa4ffe55e88a8eedaf
original_B001_run: 44866963011 (attempt 1, SUCCESS, preserved)
B001_review_task_terminal: BLOCKED_INDEPENDENCE (do not replay)
B002_branch: experiment/ts-ee003-chromedriver-b002-20261121

## Repair scope

This is a DISTINCT candidate, not a retry of B001. One new real ChromeDriver session per native CI job, plus four deliberately negative **nonProduct** harness fault scenarios using short-lived localhost Node stubs (DRIVER_EXIT, SESSION_TIMEOUT, POST_REJECT and DELETE_REJECT). Each negative fixture must terminate as FAIL and report all browser scenarios NOT_RUN. No Product source, credentials, production navigation, model inference or external origin.

The original direct ChromeDriver exit cannot attest all Chrome descendants. B002 explicitly reports `driver_termination=DIRECT_PROCESS_EXIT_OBSERVED|NO_CHILD_SPAWNED|UNVERIFIED` and `descendant_termination=NOT_ATTESTED`; profile_cleanup PASS only means isolated directory removal. An unresolved/timeout `POST /session` is `session_remote_state=UNKNOWN`, never falsely ACK. `DELETE /session` refusal remains terminal FAIL even if main driver exit and profile removal are observed.

Use `TS_EE_TEST_FAULTS=1` only in the isolated NONPRODUCT workflow to enable synthetic fixture paths, never Product. The real session path uses the same 12000ms request timeout and does not auto-retry. Native CI has no raw chromedriver verbose output or WebDriver sessionId in JSON/logs/ZIPs. Fake malicious session ID, token and screenshot markers are injected in test doubles; all report/stdout/stderr bytes must exclude them. Host network assurance remains OBSERVE_ONLY, with OS egress unattested; `--no-sandbox` is confined to isolated CI.

## Limits and residual advisories

- The ephemeral selected TCP port is released before spawn, so service-port binding is not independently traced (TOCTOU); original driver PID/descendant provenance still excluded.
- Ubuntu image and Chrome/driver versions are read by native job and hashed, but the hosted image remains mutable and file hashes are not process executable attestation.
- Negative-fixture direct-process exit is not a real Chrome crash/missing dependency. Two new real positive jobs and four deliberate failure cases still cannot establish reliability percentiles or a ChromeDriver timeout root cause.
- Current Common v0 strict validator requires PREVENTIVE_BROWSER_ABORT to declare browser=PASS, incompatible with truthful ChromeDriver OBSERVE_ONLY. A proposed v0.1 contract is not adopted. No browser route/viewport/screenshot E2E, no actual Product A01 adapter, no Q6 independent review.

Native CI must verify exact branch head/tree, source hash, both job statuses and artifact ZIP/inner hashes. The experimental repair remains DRAFT until independent full-source review by a reviewer with NO implementation-context inheritance, competent nonProduct disposition and later method integration grant.

Original B001 derivative evidence: `mauedgar/ts-execution-transport@15e642e293018ac6ca73744c5980fde585651d38:results/TS-EE-003-CHROMEDRIVER-B001-NATIVE-20261121-001/TECHNICAL_RETURN.md`.
Review independence audit: `mauedgar/ts-execution-transport@a76c0246379647e1b466f9c77a2495bad0207688:results/TS-EE-003-PR67-REVIEW-INDEPENDENCE-RECONCILIATION-20261121-001/CONTROL_RETURN.md`.
