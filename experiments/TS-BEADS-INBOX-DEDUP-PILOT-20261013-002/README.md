# TS — Beads Inbox/Dedup Pilot 002 (experimental)
Status: MATERIALIZED_SOURCE_PENDING_EXECUTION. Product authority: NONE.
Owner: experimental Beads continuity qualification. No Product TaskCycle or issue writes.
Exact attempt: BEADS-INBOX-LOCAL-20261013-001 (one shot, no blind retry).
Host: DESKTOP-3LJ0E54. Reuses prior pilot 001 native Beads 1.3.1 binary and verifies hash against its original retained receipt.
New data workspace: %LOCALAPPDATA%/TS-Experiments/TS-BEADS-INBOX-DEDUP-PILOT-20261013-002. Never touches original pilot data or Product repositories.
Sequence: guard fresh workspace and prior PASS -> init independent Beads store -> create synthetic active task -> ingest synthetic source-ref A three times, assert same id -> ingest source-ref B with same title, assert distinct id -> check pending while active is in_progress -> close active checkpoint -> independent PowerShell readback of both handoffs, still open, ready, and source unique.
Source identity is an explicit experiment-owned policy encoded as an exact SOURCE_REF marker in description, NOT an assertion about built-in Beads dedup.
Failure leaves original receipt and partial state for reconciliation; do not replay the attempt. No MCP, Docker, global PATH, GitHub Issues/Projects or Product effects. No host-native Git Transport publisher qualification here.
Transport: frozen Git branch/commit for sources; result written to local result.json and readback.json, terminal summary only via Commander. Automatic Git Transport publication remains HOST_BINDING_PENDING and belongs to its existing qualification responsibility.
