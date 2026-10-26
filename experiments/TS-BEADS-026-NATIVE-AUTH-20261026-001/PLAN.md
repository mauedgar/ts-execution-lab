# TS — Beads 026 | Control experimental — native auth and writer boundary

**Authority:** EXPERIMENTAL_CONTROL_ONLY, Product NONE. No TaskCycle, Phase 2, Independent Review Product or Developer grant.

**Source Product read-only:** mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56, tree 8caa56d36f3efeba359bbbf65b158ffb01a19da6; SOT blob dd8d34a7e3ef3094805d014f9e59741d2c553957; current-state blob 0d8a6426f51020d51d74bfb50dc8702a07f02837. Lab main@b30241201d07a9590e1e845abe767cdcf9921479, shared Dolt ref 1f72d68797114170a97fee27641858f2e55a4571 unchanged.

**Evidence from 025:** isolated Ubuntu UID-based SQL/OS network policy worked in the tested scope, but does not protect a same-UID implementer, another privileged native endpoint, or compromised credentials. 025 verdict at mauedgar/ts-execution-lab@c57f8594ad3f4b349c1146e800cd46b10051123a.

**New native Beads capability:** v1.3.1 exposes --auth-token-file (cmd/bd/serve.go; internal/httpapi/auth.go and server.go). Loopback auth optional; bearer token protects all routes except healthz, including context. It grants the entire surface, no identity or scoped permission. Token file is reloaded during requests; invalid/unavailable reload retains last-good credentials. A same-UID actor might read the 0600 file. Direct privileged CLI to Dolt can bypass server auth.

**Bounded native experiment:** isolated Linux Git/Dolt directory and Beads server, pinned release binaries, no Product or shared remote effects. Qualify six endpoints with missing/invalid token; valid token; a second process with exactly the same UID but no root SQL password; a direct CLI dependency mutation; token rotation/revocation; missing token file during service and during fresh startup; recovery after restart; atomic guarded writer vs stale CAS. Do not leak tokens into logs or TXT.

**Qualification criteria:** PASS_AUTH_BOUNDARY_WITH_SAME_UID_AND_TOKEN_LOSS_GAPS means observed native behavior is correctly classified, NOT safe Product writer exclusivity. If the native behavior differs, preserve failures and analyze rather than manufacturing success. Do not create new global mutable ledger, scheduler, or role.

**Carrier:** reuse Product scripts/review_txt_carrier.py blob 96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4; generate/verify/extract IR-TXT-CARRIER/1 with exact original JSON result and PLAN; Git branch create-only publication. No ZIP as consumer format.
