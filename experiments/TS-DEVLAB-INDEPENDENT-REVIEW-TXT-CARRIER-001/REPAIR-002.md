# Independent Review TXT Carrier — Repair 002

Preserve current recursive candidate f0d48e89520ec4bd27dac2b2cc72ffa904adb2bd.

Apply only portable-path/readability hardening.

1. Portable path safety for BOTH exact and readable modes:
   - reject case-insensitive duplicate paths within one TAR/archive.
   - reject Windows reserved device segments: CON, PRN, AUX, NUL, COM1-9, LPT1-9 (including extensions).
   - reject segments ending in dot or space.
   - reject characters invalid for portable Windows filename segments: < > : " | ? *
   - preserve existing absolute/traversal/backslash rejection.
   - verification must also reject ambiguous/case-insensitive duplicate member/leaf provenance.

2. Reviewer-readable leaf definition:
   - for project-readable, decode UTF-8 AND require every character to be printable or TAB/CR/LF.
   - NUL or other control characters in a non-TAR leaf fail closed.
   - nested TAR containers continue to recurse before this leaf check.

3. Tests:
   - case-insensitive duplicate exact mode blocked.
   - case-insensitive duplicate readable leaf blocked.
   - reserved Windows path blocked.
   - trailing dot/space path blocked.
   - readable NUL/control leaf blocked.
   - all existing tests remain PASS.

Do not alter Product semantics.
Do not claim canonical TAR replacement.
Do not merge.
Commit/push this branch and stop.
