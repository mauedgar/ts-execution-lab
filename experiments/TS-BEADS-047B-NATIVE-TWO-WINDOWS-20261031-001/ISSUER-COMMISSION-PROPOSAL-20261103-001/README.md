# TS-BEADS 047B — Local experimental issuer commissioning (PROPOSAL / NO DISPATCH)

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, `EXPERIMENTAL_CONTROL_ONLY`. This proposal adds no Product TaskCycle, Kernel, scheduler, daemon, service, new provider, or Product integration. It is not a signer appointment. **No SQL / Dolt / Beads / Tailscale Serve / Product effects authorized.**

## Why this narrower design

Original IR024 `ISSUER_SOURCE_FAIL` (`libfile_6267c97566d4819183321dd8738c2534`) identified unsafe `-Provision -SecurityChangeApproved` caller switches, check-then-act key races, weak host/user binding and incomplete key property verification. Original IR025 `ISSUER_INSPECT_SOURCE_PASS_LIMITED` (`libfile_2870e46471388191810b62dd3e6c4e03`) qualified an **inspect-only** source. Neither authorizes new keys.

A native notebook observation on 2026-11-03 returned `ISSUER_SUBJECT_MATCH_COUNT=0`, `PKI_CERT_CMD=AVAILABLE_MODULE_pki`, `TPM_PRESENT=False`, `TPM_READY=False`. **No certificate/key was generated**. Desktop PKI available; desktop TPM report was inconclusive (empty values). Therefore this candidate requests Windows Microsoft Software Key Storage Provider, RSA-3072, `NonExportable` policy, user CurrentUser store; it is NOT a TPM key, attestation, same-user signing-use denial, or proof of hardware independence. The Microsoft PKI `New-SelfSignedCertificate` help lists these provider and KeyExportPolicy options. OS-specific properties remain unverified until a separately authorized native effect.

## Candidate implementation boundary

`Invoke-047B-IssuerCommission.ps1` is an **effect-capable DRAFT but permanently unbound in this revision**: its sole parameter block is empty; `$trustedAuthorityPemSha256=('0'*64)` causes `COMPETENT_AUTHORITY_ANCHOR_NOT_BOUND` *before* any host, file, certificate or key effect. Tests must prove this actual denial. The script cannot be made dispatchable by a caller-supplied flag, file, JSON field or environment variable. A future trust-key pin modification changes the subject and requires a NEW independent immutable review, original receipt and grant decision; no same-subject re-dispatch.

If a future distinct source revision is admitted, its **intended** bounded key-only operation is:
1. Verify original independent **external** claim/receipt for this exact attempt and an independently appointed signing authority. The repo's signed `exclusiveClaimRef` and hash are assertions, NOT independent provider evidence. A self-signed certificate alone never appoints its owner as competent Control.
2. Use exact signed RSA-PSS/SHA256 grant bytes, public PEM whose UTF-8 SHA256 is **source-pinned** (not caller supplied), expiry <=20 minutes, operation, exact attempt, host, current Windows SID, key-only scope, original Git HEAD and script blob. Failure: stop before any key effect.
3. Require pre-existing security-isolated user-owned `%LOCALAPPDATA%\TS-BEADS-047B\issuer-commission-v1` with protected DACL and owner SID, pre-materialized grant/signature/public PEM, no reparse ancestors and no prior stable original attempt file. The creation of this root/material is a **different bounded operation**; do not use Commander to create scripts, keys or inputs.
4. Open `original-attempt.jsonl` once with `FileMode.CreateNew` and exclusive `FileShare.None`. Flush `STARTED_BEFORE_KEY_EFFECT` before requesting a key. This is a single same-host write owner/fence for the fixed path, not an off-host global claim.
5. Make at most one Windows software-KSP `New-SelfSignedCertificate` call, then re-enumerate the subject, check single match, key presence and RSA-3072 public key; append `LOCAL_KEY_CREATED_UNBOUND_POLICY_NOT_ATTESTED` including only public key fingerprint/thumbprint. No private key bytes or SQL credentials are printed.
6. Any exception/crash after creation of the attempt file means `UNKNOWN_EFFECT_RECONCILE_BEFORE_RETRY`; never delete cert/claim, attempt a blind retry or assert that absence of output proves no effect. Keep private receipt on host; a separate source-qualified sanitizer could publish nonsecret original evidence off-host.

**Security limitations open for independent review:** Windows user with the private key may still sign arbitrary data; Software KSP `NonExportable` is a requested policy, not a proven key-use boundary. An administrator can access local state. MachineName and user SID are native observations, not remote cryptographic host attestation. Protected local DACL and CreateNew reduce accidental parallel creation but do not prove off-host exclusivity, power-loss durability or resilience to same-user compromise. File/Cert store mutations are non-transactional. There is no local accepted trust root or competent signing grant now; current source will always reject.

## DoD and authority separation

The original offline V6P1 (`mauedgar/ts-execution-lab@0118028c2508c2ce274fd42240f847adf7ff2187`, manifest blob `401e5e11fb88f537ed0b0bd6b25b346afa1e3d96`) remains `notDispatchable=true`, trusted key hash all zeros. Its RSA-PSS verification approach is reused conceptually; no changes to original runner or manifest. User authorization to continue the *experiment* is not a cryptographic authority grant.

BETA `PROVIDER_UNKNOWN`, notebook V6P2 `ABANDONED_UNRECONCILED_UNKNOWN`, original A002 mutating GraphQL CAS publication `BLOCKED_TOOL_SECURITY`, F03-02/F04 remain protected. Their effects are distinct from a proposed *new* local key-only attempt, and cannot be silently declared reconciled. No previous original key creation attempt with this new identity is established. Any actual new effect still requires independently accepted source/claim/grant under the competent existing contract; if missing, `BLOCKED_PRECONDITION`.

Product stays `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`; #34 `CLOSED_PASS`, #35 H6 independent, Kernel `UNDECIDED`, zero Product bytes removed. Successful commissioning would still NOT prove SQL authentication, two-host Beads state continuity, outage/backup restore or total Kernel equivalence.

**Proposed disposition:** `ISSUER_COMMISSION_SOURCE_PREP_ONLY / REAL_ANCHOR_MISSING / EFFECT_NO_GO / HOST_INDEPENDENCE_INCOMPLETE`. Reviewable implementation source is NOT an accepted effect.
