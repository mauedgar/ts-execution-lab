# TS-BEADS 047B — issuer key custody candidate (source-only)

**Existing responsibility:** TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001, experimental control only. This source is NOT a Product decision, signer appointment, SQL grant, or real CAS claim. It was built over `mauedgar/ts-execution-lab@7184ea0461f3fd4c25b4e9a4b6f157e40c92a754` and preserves the original V6P1 source, tests and manifest byte for byte. No Product files or existing attempts are modified.

## Selected bounded adaptation

Keep the existing 047B V6P1 RSA-PSS verification design and isolate **only the prospective custodian key**. Do not add another ledger, Kernel, scheduler, state service or provider adapter. There are two explicitly distinct script modes:

- `-Inspect`: read-only Windows CurrentUser certificate store query on the pinned notebook. The output never contains a private key, and reports `competentIssuerBound=false` even if a certificate already exists. No SQL, file writes or network calls.
- `-Provision -SecurityChangeApproved`: a **future local security mutation**, not run by source creation/CI. Intended to create at most one user-scoped, nonexportable RSA-3072 certificate using the Windows Microsoft Software Key Storage Provider. Reports only public PEM SHA256 and certificate thumbprint. If the key is already present, duplicates exist, the owner is wrong, or a prior result is ambiguous: stop without cleanup or retry.

The exact private-key owner is the Windows account, not the remote chat or CI. Nonexportable does NOT protect against programs running under the same user or administrators. This is **not** a hardware security module, independently appointed issuer or proof of non-use. Initial physical and source review must precede any local key provisioning.

**No invocation of Provision is selected or authorized by this candidate.** All source tests are synthetic/parser-only plus a wrong-host fail-closed check. Even a future successful local key would be `LOCAL_KEY_CREATED_NOT_BOUND`, not a competent grant.

## Competent sequence still required

1. Independent reviewer checks the exact new source, native read-only CI, no-effect boundary, host owner, Windows certificate compatibility, nonexportability and recovery ambiguities. A CI PASS alone does not approve key changes.
2. If source accepted, select one *new original* bounded key-custody attempt with exact immutable commit, hash, notebook owner, OS principal and durable original receipt. Materialize code via normal repository/Orca surfaces, never Commander. The execution attempt must have a separately competent security-change authorization. Do not start it from a chat command or a key request alone.
3. Locally export only the **public** SPKI PEM from the pinned Windows user certificate using an independently reviewed procedure. Independently authenticate the actual custodian/issuer provenance, confirm exact UTF-8 PEM bytes and SHA-256, then publish a distinct reviewed revision of V6P1 to replace its all-zero trust pin. Publishing a public key is not, by itself, appointing its owner as competent Developer/Control.
4. A future grant and reconciliation must be signed using the approved private key with RSA-PSS/SHA256, bound to operation, attempt, host, source, owner/write-set, expiry, expected receipt and verified exclusive claim. Real external provider evidence and original UNKNOWN reconciliation must independently pass **before any SQL effect**. Never synthesize those fields as true from local flags.
5. Only then a separately reviewed secure notebook Dolt 2.2.0 offline/loopback bootstrap may be evaluated. Initially no Tailscale Serve. Authenticated root/writer/reader denial must be proven before private TCP forwarding, and the two-Windows-host Beads graph/outage/backup/restore DoD still remains.

## Immutable historical boundaries

- Original V6P1 source: `mauedgar/ts-execution-lab@0118028c2508c2ce274fd42240f847adf7ff2187`, manifest blob `401e5e11fb88f537ed0b0bd6b25b346afa1e3d96`, `notDispatchable=true`, `grantPresent=false`, trusted key pin 64 zeroes.
- Windows source CI `41575236247` PASS only for V6P1 parser, source and no-issuer negative tests.
- Original mutating GraphQL CAS publication remains `BLOCKED_TOOL_SECURITY`. Do not retry or repackage those write-capable blobs.
- Historical BETA `PROVIDER_UNKNOWN` and notebook V6P2 `ABANDONED_UNRECONCILED_UNKNOWN` remain; missing processes or files do not prove no effect.
- Original 047B DoD: `mauedgar/ts-execution-lab@e02c611dec74ce5d2ddcd5c169f407543ef2e3c4:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.
- Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` unchanged: #34 CLOSED_PASS, #35 H6 independent, State Kernel UNDECIDED.

## Provider compatibility to validate later

Dolt access-management docs describe default passwordless `root@localhost` until privileges.db is initialized and a local `dolt sql` superuser escape; never confuse SQL SELECT grants with restrictions on the Windows account owning Dolt storage. Documentation also lists some MySQL ALTER USER features as unsupported, so do not design the actual Dolt 2.2.0 bootstrap from generic MySQL assumptions. Tailscale Serve TCP and access controls are private-tailnet considerations, not a reason to enable Funnel.

**Control classification:** SOURCE_ONLY_CANDIDATE_NOT_REVIEWED / LOCAL_ISSUER_NOT_APPOINTED / NO_SQL_EFFECT / HOST_INDEPENDENCE_INCOMPLETE.
