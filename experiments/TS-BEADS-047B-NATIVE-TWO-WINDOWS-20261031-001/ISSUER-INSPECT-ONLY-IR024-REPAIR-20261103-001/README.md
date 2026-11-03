# TS-BEADS 047B — IR024 repair: issuer INSPECT ONLY

**Authority:** existing EXPERIMENTAL_CONTROL_ONLY responsibility TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001, no Product authority. **Source-only status:** not a key provisioning or signing runner, no SQL grant, no CAS effect, no host-independent Beads proof.

## Independent IR024 consumption

Original independent IR024 `ISSUER_SOURCE_FAIL` is preserved in Library as `libfile_6267c97566d4819183321dd8738c2534` (7,709 bytes, SHA256 `b55db9ef9153c541523185b97c8f2f46f896810113172cd438616d18f03252c3`). Its frozen subject `mauedgar/ts-execution-lab@79e2a5cef5711307c9b359de6d9dd5e0a0af579e`, tree `ad7ca9b3241713c96cf3eff4eaadd9e6becef2c5`, has an effectful `-Provision -SecurityChangeApproved` route reachable using caller-provided switches. **That old branch is not accepted, not dispatched and must not be run or repackaged as an effectful script.**

F01 blocker: caller-switch effect bypass. F02 high: check-then-act certificate race and ambiguous partial key writes. F03 high: environment hostname and current-user cert-store identity do not establish authorized signer identity. F04 medium: provider/export policy/private-use unverified. F05 medium: source text/AST tests are synthetic and incomplete. Three advisories preserve separate issuer appointment, exact future owner/attempt and original evidence limitations.

## New isolated source-only candidate

Created from **pre-IR024 V6P1 qualified baseline** `mauedgar/ts-execution-lab@7184ea0461f3fd4c25b4e9a4b6f157e40c92a754`, deliberately **not** from the rejected effect-capable commit. Exactly this isolated directory and a read-only CI workflow are new; the old effect-capable issuer script is not in this branch.

`Inspect-047B-IssuerEvidence.ps1 -Inspect` is observational. It lists only the Windows current-user certificate store on the intended notebook and, if a unique subject-matched certificate is present, describes its **public** RSA key fingerprint, thumbprint, expiry and a self-reported `HasPrivateKey` claim. If none or more than one match are observed, it returns distinct untrusted statuses. It has **no provision/sign/delete/cleanup modes** and never grants authority; all outcomes keep `competentIssuerBound=false`, `oneTimeSqlGrantPresent=false`. The notebook hostname check is a weak hint, NOT cryptographic host/device/SID attestation.

`Test-047B-IssuerInspectOnly.ps1` uses PowerShell AST parser plus exact command allowlist, checks only one `Inspect` parameter, rejects both former provisioning switches, and tests wrong-host fail-closed on GitHub Windows runner. It does NOT prove positive notebook inspection, user SID custody, cert ACL, private use prohibition, concurrency, actual key generation or signature validation.

**No local certificate should be created under this source subject.** No action on notebook is selected by publication or CI. If a real separate key-custody generator is later needed, its approved immutable source, trusted issuer appointment, Windows SID/device owner, once-only durable original attempt and crash/UNKNOWN reconciliation must be independently designed and reviewed; not pulled from rejected IR024 code.

## Product and provider boundaries

Original V6P1 manifest `mauedgar/ts-execution-lab@0118028c2508c2ce274fd42240f847adf7ff2187`, blob `401e5e11fb88f537ed0b0bd6b25b346afa1e3d96`, remains `notDispatchable=true` and trust pin all zeros. BETA `PROVIDER_UNKNOWN`, V6P2 `ABANDONED_UNRECONCILED_UNKNOWN`, F03-02 and F04 `BLOCKED_TOOL_SECURITY` remain. No retries, CAS edits, grant simulation, SQL/Dolt/Beads/Tailscale Serve/backup or Product effects.

#34 remains CLOSED_PASS, #35 H6 independent, State Kernel UNDECIDED. The original 047B DoD is `mauedgar/ts-execution-lab@e02c611dec74ce5d2ddcd5c169f407543ef2e3c4:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.

**Disposition target:** `ISSUER_INSPECT_ONLY_SOURCE_PASS_LIMITED` or `SOURCE_FAIL` after independent review. Even PASS would not authorize provisioning/SQL or prove host independence.
