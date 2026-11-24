# TS EE 004 — Orca WSL E3 bounded native leaf, PR77 IR001 repair candidate
source_baseline: mauedgar/ts-execution-lab@96487dbd6c4423c6beb57286b8768e09d149189b
new_attempt: TS-EE-004-ORCA-WSL-E3-BOUNDED-LEAF-20261123-001-A001
status: SOURCE_ONLY_EXPERIMENTAL_NOT_NATIVE_ADMITTED
Product_authority: NONE
Product_effect: NONE
historic_E1_E2: TERMINAL_PRESERVED_NOT_REPLAYED
host_materialization: NONE
Orca_terminal: NONE
WSL_process: NOT_RUN
review: INDEPENDENT_WEBINLINE_PENDING

## Evidence and policy disposition

PR77 external original IR001 `SOURCE_NO_RECOMMEND`, 6 source findings (F01/F02 HIGH, F03–F06 MEDIUM), and four advisories. This new source is an *independent new candidate*; never modify original PR77, its native Actions run or original independent reviewer bytes.

F01: calls Win32 `CreateDirectoryW` directly for an exact fixed new output leaf and rejects ERROR_ALREADY_EXISTS atomically rather than relying on racy `Directory.CreateDirectory` semantics. Fixed parent `C:\TS\station` and `C:\TS` are checked for current reparse attributes; cannot claim security against hostile admin concurrent parent replacement or NTFS reparse races.

F02: creates `INCOMPLETE.txt` exclusively before WSL launch, and flushes `RESULT.tmp` exclusively before deleting the incomplete sentinel and atomically moving to `RESULT.json` within one directory. Consumers require no sentinel or temp; any incomplete, stale or missing receipt is UNKNOWN, never PASS. Best-effort create-only FAILURE receipt preserves `effect_state=UNKNOWN` if a child ever started; no silent automatic retry. A transient no-marker/no-final gap is accepted only as UNKNOWN. No guarantee against sudden power loss or hostile writers.

F03: Windows launcher PID is captured from the actual .NET Process object; CIM parent sample is an optional bounded observation, and a missing sample does not misrepresent failure as Linux child identity. A positive observed CIM parent must match expected Windows runner PID. Linux marker remains **stdout self-report**, not signed/kernel cross-namespace attestation. Native Orca runtime, terminal handle/incarnation must be supplied from original external provider receipt and verified by the Control afterward. Those input fields are not self-authenticating.

F04: concurrently drains stdout and stderr with .NET `Stream.ReadAsync` bounded to 4096/2048 raw bytes, with 16-second CancellationToken deadline. Timeout/error leads to best-effort Kill(entireProcessTree), a bounded 2s wait, `UNKNOWN` effect and incomplete root retained. Does NOT prove WSL Linux descendants terminated, and no remote commands after UNKNOWN.

F05: requires exact one-line v0.2 typed JSON marker, exact schema/request/attempt, fixed UID, PID/PPID, namespace regex and intended_exit together with observed `wsl.exe` exit code 7; extra lines/keys fail. Still NOT cryptographically independently authenticated Linux PID/UID or WSL process ancestry.

F06: requires a fixed externally pinned runner SHA and the original native Orca runtimeId/handle/incarnation/hostId, while the actual provider join is separate. Checks exact Windows host, PowerShell 7, fixed source root, WSL signed binary and fixed Python argv. These are bounded local guardrails, **not** independent caller authority or original host attestation.

New attempt E3 path `C:\TS\station\ts-ee004-wsl-leaf-e3-20261123-001` MUST be independently proved absent, transport carrier extracted with exact reviewed source SHA, and original Orca provider lease/terminal validated before any physical `pwsh -File` call. The imported version-qualified **pre-existing** MAT-XFORM extractor path, hash, source contract and exact create-only destination are still REQUIRED. Do not execute an unfrozen PowerShell `-Command`, generate scripts on Commander, re-materialize rejected PR77 bytes, treat source-only CI as WSL, or modify Product.

DoD: independent full-source IR after fresh exact Windows Actions pass, source/host transport qualification, then one completely new bounded E3 native attempt with original terminal+WSL receipts and exact closure, while preserving truthful `self_reported` vs `independently_attested` axes. Final TS Remote State handoff only after competent method status, never partial or Product acceptance.
