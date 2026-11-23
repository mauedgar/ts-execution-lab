# TS EE 004 — IR006 F01 trusted caller identity repair (NONPRODUCT)
status: EXPERIMENTAL_NOT_INTEGRATED
source_base: mauedgar/ts-execution-lab@8eb4e4d16b8ca0aea956c1e8d8e15be012470b01 (PR73)
new_branch: experiment/ts-ee004-ir006-external-identity-20261123
review_origin: Developer-provided IR006 METHOD_NO_RECOMMEND / 1F5A (reviewer-original not in Git Transport)
Product_authority: NONE
Product_effect: NONE

The strict v0.1 evaluator accepts caller-supplied **external** expected engine, subject kind and evidence profile; they are never obtained from the producer JSON. For real browser=PASS claims, all are REQUIRED. The Q5B map is required if and only if the trusted caller selected the Q5B profile; mutating runner.engine, source.subject_kind or original.reference does not turn it off. Q5B also requires expected HEAD/tree/run parameters. Caller must pin all arguments from trusted, versioned workflow and the independent native provider readback; no claim that command-line flags alone authenticate GitHub.

Strict CLI receives --expected-engine, --expected-subject-kind and --expected-evidence-profile, with established --expected-commit/tree/run-id. Missing or inconsistent flags fail closed. TEST_VECTOR remains diagnostic-only, never accepted by strict consumer; generic Playwright synthetic with GENERIC_BROWSER_V01 does not inherit Q5B checks. Contract version remains v0.1 experimental only; stable v0 validator unchanged.

The new CI is SOURCE-ONLY: reuse previous independently reconciled ChromeDriver original run 45229561752 / artifact 14847471289 and the four browser sessions, DO NOT replay browser actions as an artificial requirement for an identity-check change. New Actions native job proves source tests only; it is not a re-attestation of Q5B ChromeDriver output.

Explicit exclusions: caller could still deliberately select an incorrect profile, so caller integrity and source profile provenance must be anchored by independently inspected workflow and original GitHub actions; no blanket provenance or network/process assurance. Descriptor, network, Windows and Product limitations remain untouched. Independent review required on this new delta before any method integration or Aware consumption.
