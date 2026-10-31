# OpenCode task — TS-BEADS-047B XFORM (OPERATIONAL)

Scope: experimental 047B only. Product and existing terminal attempts MUST remain untouched.

Review and, only if necessary, correct the bundled `TS047B-XFORM-MATERIALIZER-v1.ps1` against the attached `TS047B-PREFLIGHT-MAT-XFORM-v1.txt`. It should validate `ts-mat-xform-request/v1` and the EXACT Git blob `af0969d7b42cff53f20cbbded376f99aa50dce8e`. Use native Windows PowerShell 7 and the built-in .NET cryptographic APIs. No XFORM daemon, scheduler, database, new contracts, or external dependencies.

Requirements:
1. First run PowerShell's parser API on the materializer; fail closed if parser errors exist.
2. Run in validation-only mode: no file writes, SQL listener, Tailscale proxy, or Beads mutation.
3. Test tampered JSON, wrong request/batch, modified `utf8_text`, and mismatched preexisting output; all must fail closed.
4. Test materialization only in a disposable *staging* folder outside `%LOCALAPPDATA%\TS-BEADS-047B`, without script execution; check output's Git blob SHA and SHA-256.
5. Produce compact PASS/FAIL evidence, including exact host, source hash, candidate hash, destination, and no Product effect. Do not expose IPs, tokens, or passwords.
6. Do not call Remote Desktop Commander for source browsing, editing, materialization, OpenCode prompting, or patch construction. Use OpenCode's normal file/repository surfaces.
7. Preserve 047B original terminal runs; do not start native SQL or a new ExecutionAttempt until independent host preconditions and original receipts are reconciled.

If any input or runtime prerequisite is missing, return `BLOCKED_PRECONDITION` instead of improvising a script or starting a live effect.
