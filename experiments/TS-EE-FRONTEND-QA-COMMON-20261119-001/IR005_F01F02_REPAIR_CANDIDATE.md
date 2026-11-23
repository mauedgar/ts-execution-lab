# TS EE 004 — IR005 F01/F02 repair, separate NONPRODUCT source candidate

status: EXPERIMENTAL_NOT_ADOPTED__INDEPENDENT_IR_REQUIRED
authority: NONPRODUCT_METHOD_ONLY
Product_authority: NONE
Product_effect: NONE
base_parent: mauedgar/ts-execution-lab@84100a1106e78dfc95513e043d04d9302868b8d7 (PR72)
new_branch: experiment/ts-ee004-ir005-f01-f02-20261123
attempt: TS-EE-004-IR005-F01F02-20261123-001-A001
source_reason: User-relayed IR005 METHOD_NO_RECOMMEND (2F/3A); report is not falsely labeled provider-original reviewer publication.

Finding IR005 F01: previous validator conditioned the mandatory eight-scenario Q5B evidence map on a single `original.reference` literal written by the producer. A consumer could change that literal, delete the map and still claim browser PASS. New strict rule applies to *all* synthetic ChromeDriver browser-PASS reports by typed engine/subject/stage, regardless of reference string. Diagnostic-only TEST_VECTOR gets an explicit eight-scenario mapping; strict CLI still rejects TEST_VECTOR as consumer. Independent producer provenance still requires external provider-native HEAD/tree/run/ZIP/inner file readback, not a self-reported JSON digest; data fields never create independent attestation.

Finding IR005 F02: producer now writes into a create-only output directory with an `INCOMPLETE_Q5B` sentinel. A successful fully written output removes the marker; failure preserves a quarantined partial directory (no auto-delete/reuse), and a `finally` always closes the original directory descriptor. Consumer rejects a directory with incomplete marker even if individual declared files appear correct. Injected ENOSPC and create-only collision negative tests demonstrate marker/quarantine and descriptor closure, without retrying or overwriting any historical data. This is a deliberate **retain-and-quarantine** policy, NOT a claim that partial files are automatically deleted. This is a local isolated Ubuntu CI contract only, NOT hostile shared-workspace race or platform parity attestation.

Out of scope advisories remain: intermediate parent rename races, full Chrome descendant/host binary process custody, preventive egress/Service Worker denial, Windows parity, Product QA/merge/acceptance. Stable v0 validator original blob `36c207326fff0da2231b731422323af186511a49` remains immutable. Reviewer must independently FULL_READ changed files and native ZIP; a CI PASS alone is not method acceptance.

This is a **new** source change and GitHub Actions execution, not rerun of original PR71/Q5B or PR72 run 45106754570, nor a replacement of their receipts. No Product writes, no Orca/Commander execution, no network guarantee.
