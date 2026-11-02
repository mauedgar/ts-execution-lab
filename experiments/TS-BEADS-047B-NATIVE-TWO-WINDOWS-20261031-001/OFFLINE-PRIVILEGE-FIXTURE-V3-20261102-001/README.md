# TS-BEADS 047B — V3 bounded source repair (NOT DISPATCHABLE)
Operation: `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, experimental control only. Frozen predecessor V2: `ee5efa31cf9674c4f148e5ef51b710899df5c359`. Independent IR008 FAIL: Transport `bb0017d59fa14b7343be7de5d3a98b8903e01ce9`, IR blob `d346a22bc313acf7bd6444cb98ef7e0e0f3ff91f`.

This V3 is a **genuine proposed executable code path, not SQL authority**. Signing key still deliberately unprovisioned; direct effect invocation must stop. No SQL, grants, real users, Tailscale Serve, Beads, backup or Product changes were executed by publishing it. No native Windows tests are claimed.

V3 targeted changes:
- F004: Win32 `CreateFileW(CREATE_NEW)` with an initially protected owner-only DACL for receipt instead of create-then-ACL; for Dolt-created `privileges.db`, verify a protected, trusted parent plus restricted permitted ACE identities without incorrectly demanding the child's DACL inheritance be disabled.
- F007: preserve single-row JSON arrays using `ConvertFrom-Json -NoEnumerate`; still needs empirical pinned Dolt schema readback.
- F010: distinguish confirmed child exit with potential SQL partial effect from unknown child lifecycle, retaining no-retry. Manifest generated from fetched raw bytes, not a claimed size estimate; original V2 README 7,981-byte erratum is preserved in IR008 and is not silently edited.
- Added static source-only assertions of atomic private receipt API, JSON handling, inherited file ACL policy, and result taxonomy.
- F001-F002/F005-F006/F009 still require **external** competent issuer key, authoritative off-host atomic claim and original-effect join, pinned Windows Tailscale and native parser/ACL evidence. The code does not invent these. F003 and F008 also need native negative harness and redaction checks before any effect. File-descriptor races remain a security review issue.
- No changes to Upper LC/TC, #34 CLOSED_PASS, #35 H6, State Kernel UNDECIDED; complete 047B DoD is still HOST_INDEPENDENCE_INCOMPLETE.

Source verification: this V3 manifest records the exact Git blobs, independently calculated UTF-8 byte counts and SHA-256 for newly added files. All files are new in V3, old V1/V2 and original IR007/IR008 unchanged. **No equivalent Product Kernel or authenticated network privilege proof.**

Next: independent source review on a **frozen V3 commit**, validate actual Windows PowerShell parser / ACL / native Dolt 2.2.0 with separately bounded read-only host test and original receipts, provision a competent trust anchor and off-host CAS/claim via Control; only after that consider a separate conditioned one-time SQL fixture grant. Do not declare zero findings from static checks.
