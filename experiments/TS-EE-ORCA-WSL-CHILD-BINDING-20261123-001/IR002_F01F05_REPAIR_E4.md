# TS EE 004 — E4 fresh bounded-source repair of Independent Review IR002
status: NONPRODUCT_SOURCE_ONLY__INDEPENDENT_IR_REQUIRED
authority: TS_EXECUTION_ENGINEERING_METHOD_ONLY
Product_authority: NONE
Product_effect: NONE
new_ExecutionAttempt: TS-EE-004-ORCA-WSL-E4-ATOMIC-RECEIPT-20261123-001-A001
base_original: mauedgar/ts-execution-lab@3a5914e619f361254787ce77c98bc6fb3458d3b3 (PR78)
original_ir: mauedgar/ts-execution-transport@01f9db835ff242709a3540e432107b23584afb28:results/TS-EE-004-ORCA-WSL-PR78-WEBINLINE-IR002-20261123-001/ORIGINAL.md
original_ir_blob: 803e54507e57d8b4e876a01c35817925b3070f91
original_ir_sha256: 98a7c885e141fc3019a4314bc32cf8613b48c151ce85423616c3459d8161bcee
original_ir_disposition: SOURCE_NO_RECOMMEND_5F_4A

E4 source uses a **new** frozen request ID and exact create-only output root `C:\TS\station\ts-ee004-wsl-leaf-e4-20261123-001`; previous E1, E2 and E3 effects are preserved. This is neither an E3 retry nor re-admission of rejected PR77 or PR78.

- IR002-F01 HIGH: strict RESULT.json v0.3 has 28 required typed fields, no unknown/missing/duplicate names, exact identity request/attempt/source SHA and externally supplied Orca runtime+handle+incarnation+host. Any FAILURE.json, INCOMPLETE, or RESULT.tmp dominates success. Inconsistent source IDs, original bytes, marker content or output hash result in INVALID, regardless of exit0. No contradictory SUCCESS+FAILURE admissible. Source-only tests include positive strict reader, counterfeit partial, contradictory failure and tampered original bytes.
- IR002-F02 HIGH: bounded ORIGINAL stdout and stderr bytes (4096/2048 max) are retained as base64 inside the **single** atomic RESULT.json, with exact size and SHA256. Consumer recomputes SHA and checks original stdout typed marker. No invented reconstruction of process output. No second independent output side-effect.
- IR002-F03 MED: synchronous unbounded CIM removed entirely from runner critical path. Windows parent/PID observation remains a separate bounded native Orca/Windows provider join, `NOT_ATTESTED_BY_RUNNER_SEPARATE_PROVIDER_JOIN`. The 16s ReadAsync+WaitForExitAsync and 2s kill/wait remain qualified only source-side; actual WSL descendant termination not proven on timeout.
- IR002-F04 MED: C# System.Text.Json JsonDocument parser with exact ordinal match of 8 keys, JSON primitive kinds (Number vs String), integer-only lexemes, no duplicate keys or extra lines, literal expected marker names. Positive and mutated negative cases added, including string UID, fraction, case drift and duplicate UID. Native JSON remains an **untrusted Linux stdout self-report**.
- IR002-F05 MED: before fixed Win32 CreateDirectoryW atomic exclusive reservation, check exact Windows `C:\TS` and `C:\TS\station` ACLs: owner current user/Administrators/System and no Allow write/delete/change-permission to other principals; fail closed on unresolved trustee. Reparse attributes checked. Still does NOT prove safety against hostile privileged concurrent ACL/parent rename, and requires real native host preflight evidence after independent review. No change to Product directory or system ACLs.

The independent source review must assess the correctness of these repairs and state precise limits, especially strict consumer tests and Windows ACL assumptions. The planned physical attempt is **not authorized by this code or CI**: requires the exact reviewed LF/CRLF byte SHA, verified non-Commander source ingress (or preinstalled qualified MAT-XFORM), new Orca provider native terminal+exit receipt, exact child identity as self-reported vs externally observed and owned terminal close. Existing OneDrive carrier/sync path is a possible separately qualified transport, not assumed delivered here. No ad-hoc script construction or arbitrary file writes via Commander; no `pwsh -Command`, Product, SQL/Kernel/Beta Run or costed providers.