# TS-BEADS 047B — privacy-first keyless proof (experimental, not Product SOT)

**Scope:** Existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`. This is an **experimental design decision / source qualification**, not a new Product TaskCycle, permission for SQL, integration or accepted Tecnotron architecture. Product SOT stays `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`. Preserve #34 `CLOSED_PASS`, #35 H6 independent, Kernel `UNDECIDED`; original BETA/V6P2 `UNKNOWN` and CAS F03-02/F04 unchanged.

## Data classes and permitted surfaces

| Class | Examples | Experimental allowed destination | Forbidden destinations |
|---|---|---|---|
| `PUBLIC_SYNTHETIC` | Fixed test vector, public repository/workflow name, public code commit | Public lab Git, GitHub Actions, public Sigstore Fulcio/Rekor | Must never be confused with a real signed execution grant |
| `PRIVATE_OPERATIONAL` | Opaque original attempt references, internal dependency state, non-identifying receipts | Access-controlled private Transport with minimized retention after risk review | Public Git, Sigstore public bundle or transparency payload, CI logs |
| `CONFIDENTIAL_PERSONAL` | Identifiable user/customer records, bookings, emails, phone, health, finances, private correspondence | Approved isolated application data stores with purpose/tenant-specific access and encrypted backups | Public/private Git as convenience storage, general-purpose public sign/attestation services, LLM prompts by default |
| `SECRET` | SQL/root passwords, private keys, JWT, API tokens, tailnet/pairing credentials | Dedicated secret manager or OS-protected local store; short-lived tokens when possible | Git/Transport, ChatGPT, logs, command arguments, public artifacts, analytics, tlogs |
| `RESTRICTED_SENSITIVE` | Special-category regulated personal data, medical records, confidential client documents | Only after separate legal/privacy/security review and explicit purpose/jurisdiction/retention authorization | All experiment surfaces by default |

**Metadata can itself be sensitive.** Names, path segments, UUIDs, Git refs, timestamps, email/domain, customer/project IDs, location and hashes of low-entropy personal data can enable reidentification. No customer-derived plaintext, JSON, URL, direct hash or reversible token may be placed into public evidence. If operational correlation is necessary, use a cryptographically random opaque reference scoped to a private system; no mapping or secret salt is exposed. `PRIVATE_OPERATIONAL` is not automatically permitted for cloud publication: minimize and classify first.

## Keyless signing public-boundary admission

This experiment signs ONLY `PUBLIC_SYNTHETIC_PROBE.json`, an immutable fixed test document with `mode=TEST_ONLY`, `authority=NONE`, `allowEffects=false`, `dataClass=PUBLIC_SYNTHETIC`. It has no personal or operational fields and cannot authorize an action; the exact file bytes and Git blob are verified before requesting OIDC.

GitHub Actions OIDC (`permissions: id-token: write`) identifies a **workflow execution**, not a Developer/Product grant. Sigstore Fulcio can issue a short-lived signer certificate and Rekor records **public and potentially non-erasable identity/timing/evidence metadata**. Even the workflow path, repository owner and branch may be visible; therefore keep these public and generic. Never sign customer data, secret bytes, customer-derived hashes, original execution receipts with private IDs or internal URLs through public Rekor, even when the public log stores only a hash/proof. Never put OIDC JWT or GitHub secret in stdout, uploaded bundle, chat or Transport. Neither Sigstore nor GitHub is declared a private production secrets vault.

The signer uses exact expected `https://token.actions.githubusercontent.com` OIDC issuer and pinned GitHub Actions certificate identity; the verifier must check the original **document bytes + bundle + exact certificate identity and OIDC issuer**, not only the signature. No dynamically supplied audience, branch wildcard, untrusted pull-request context or caller-controlled identity. Identity validity and software integrity do NOT establish Product authority. A future grant may **reference** a vetted nonsecret digest and private authorization decision, but no new live effect follows from this proof.

## Future private-control architecture candidate — NOT IMPLEMENTED

- **Product authority:** Competent Developer/Control in canonical repository establishes a bounded decision; this experiment does not.
- **Artifact identity:** Public code and immutable build provenance may be signed in public keyless workflows only if metadata is acceptable for publication. Actual confidential grant contents stay private with independent authenticated access; for truly sensitive grant metadata, use private signing or a suitable internal KMS/PKI rather than public Rekor.
- **Execution exclusivity:** Only a future explicitly reviewed isolated transactional registry (e.g. SQLite-backed Durable Object) with authenticated per-actor access, opaque random attempt IDs, atomic compare-and-set, original owner and receipt verification. Do NOT use Cloudflare as a customer database. A registry reservation is not exactly-once external effect; `UNKNOWN` requires original provider reconciliation before retry.
- **Secrets/customer data:** Stay in application-controlled isolated stores and dedicated secret management, not CI, GitHub artifacts, Transport or public tlogs. Enforce least privilege, tenant boundaries, access audits, encryption in transit/at rest, protected backups, retention/deletion and incident response. Evaluate supplier terms, lawful basis, international transfers, and required data residency before customer onboarding. Cloudflare Durable Object jurisdiction only covers where DO runs/stores; its ID may be logged outside the requested jurisdiction.
- **User devices:** Notebook/desktop receive only authorized ephemeral execution parameters from a vetted channel; never SQL credentials in Commander arguments, Orca transcripts or model output. Commander remains execution/result-only. Do not auto-launch local SQL or open Tailscale Serve because of a signing proof.

## Security constraints of the one-off public test

1. The repository is **public**. The source fixture is intentionally already public and has exactly fixed bytes; the workflow denies changes via Git content hash, tests and explicit path allowlist. No customer file, arbitrary `workflow_dispatch` input, dynamic downloadable signing payload, real auth grant or production secret allowed.
2. No workflow or job secrets are passed; `permissions: contents: read, id-token: write` only for this public synthetic exercise. Job uses GitHub-hosted Windows, pinned action digests, nonpersisted checkout credentials. The signer deliberately generates a **public transparency event** for this dummy probe; it is not a production private signature.
3. Post-signature verifier checks exact workflow identity and OIDC issuer. A changed test blob must fail verification; the signed public bundle may be uploaded as a short-retention **non-authorizing** demo artifact. GitHub Action output is evidence of tests, not original Product or provider effect receipt.
4. No duplicate sign dispatch, retry or cron. If Sigstore/Rekor returns an ambiguous result classify `UNKNOWN_PUBLIC_PROBE` and reconcile provider evidence before any same-subject retry; a missing artifact is not proof no transparency event.
5. Do **not** infer compliance, deletion guarantees or free-tier durability. Separate privacy impact assessment, threat model, data processing agreement and jurisdiction decision precede any real user/customer/sensitive data.

## Next evaluation

If the public synthetic keyless sign + Windows verification succeeds, compare its developer cost, provider dependency and identity precision against the bespoke V6 signer proposal (IR026 only SOURCE_PASS_LIMITED / NO_GO_EFFECT). Decide whether source evidence is reusable; no Product adoption or live grant without competent decision. If it fails, preserve exact attempt/output, avoid blind reruns, and keep 047B host independence `INCOMPLETE`.
