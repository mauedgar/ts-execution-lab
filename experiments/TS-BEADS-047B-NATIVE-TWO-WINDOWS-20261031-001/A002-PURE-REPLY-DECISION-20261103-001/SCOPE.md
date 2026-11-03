# TS-BEADS 047B A002 — PURE READ-ONLY ARCHITECTURAL ISOLATION

This is a materially distinct **non-mutating** experimental prototype, not a replay, alternate carrier or continuation of the tool-blocked source-publishing operation. It introduces only a standalone reply parser, a fail-closed terminal predicate and synthetic tests. It neither embeds nor modifies the historical effect runner.

Existing experiment: `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (Product NONE).
Source basis: `mauedgar/ts-execution-lab@9f174e505dfa0314f9dd4df89e9e7999b274d96f`; tree `a8721f6aec01ff2dd2290fb1e92e67a3db45135f`.
Independent original IR022 `libfile_64c2b54b61c08191af5444838c134e5e`, 6,569 bytes, SHA-256 `caafd111b388bcdfacd4b972f6ec602193dfdd3d5c0c8f15ecf111cc87d25936`.

- IR022 F022-01 claimed `-cne` meant equals, but in PowerShell `-cne` means case-sensitive **not equals**. Original condition `if($b -cne 'BETA_EXPLICIT_BEFOREOID_REJECTION'){throw ...}` fails closed for unknown/untyped results; reversing it would be unsafe. This is a Control correction, not a rewrite of the independent reviewer report.
- IR022 F022-02 remains **unfixed in the original runner**; this isolated pure proof-of-concept validates strict GraphQL reply structure and expected `clientMutationId` without network access. It is not imported into the original runner, so no integrated repair is claimed.
- F03-01 remains PARTIAL, F03-02 BLOCKED, F04 BLOCKED_TOOL_SECURITY. No mutating workflow was introduced. Historical BETA PROVIDER_UNKNOWN and notebook V6P2 ABANDONED_UNRECONCILED_UNKNOWN are protected from retry or cleanup.
- Test execution is synthetic and cannot prove real GitHub error taxonomy, CAS, cross-host Beads/Dolt continuity, global fencing, or any Product adoption.
- #34 CLOSED_PASS, #35 H6 separate, Kernel UNDECIDED.

**Next gated action:** Review source-only prototype independently. Only after a separately permitted, substantively safe integration path is established may a new bounded integration candidate be considered. The existing blocked CAS-capable runner publication must not be retried or repackaged.
