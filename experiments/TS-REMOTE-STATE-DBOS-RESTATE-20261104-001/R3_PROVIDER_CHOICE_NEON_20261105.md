# TS-REMOTE-STATE R3 — managed PostgreSQL provider candidate selection

**Status:** `NEON_FREE_PROVISIONAL_CHOICE / NO_PROVIDER_BINDING / NO_CREDENTIALS / NO_EXECUTION`. TS Execution Engineering experiment only, not Product, not a new TaskCycle, not a migration or cutover. This decision does **not** supersede `R3_HOST_AGNOSTIC_PROOF_PLAN_20261105.md` or modify earlier frozen requests.

## Why this candidate

Prefer **Neon Free managed PostgreSQL** for the first independent two-host physical proof, contingent on connected account and actual project/endpoint capabilities. As of 2026-11-05 published provider material:

- Official Neon release 2026-10-02 states Free tier **1GB PostgreSQL per project, 100 projects, 100 CU-hours/project/month, 10 branches/project, six-hour instant restore history**, automatic scale-to-zero. This is suitable for an **ephemeral synthetic R3 proof**, not an SLA or permanence guarantee. Source: https://neon.com/blog/neon-free-plan-1-gb-per-project
- Neon documents serverless scale-to-zero after 5 min idle and persistence of storage independent of the client compute. Source: https://github.com/neondatabase/website/blob/main/content/faqs/free-plan-limits-and-quotas.md and https://neon.com/blog/postgres-needs-better-connection-security-defaults. Compute quota exhaustion can interrupt connections and is a test failure condition, not erased history.
- Prefer **TLS certificate/host authentication** with the driver-verified equivalent of `sslmode=verify-full`; Neon also recommends channel binding in supported libpq clients, rather than interpreting `sslmode=require` alone as full server identity verification. Source: https://neon.com/blog/avoid-mitm-attacks-with-psql-postgres-16 and https://neon.com/blog/postgres-needs-better-connection-security-defaults
- Supabase Free remains a fallback, but official documentation says Free projects can pause after seven days of low activity, which can confound a long-idle recovery test. Source: https://supabase.com/docs/guides/platform/free-project-pausing
- **No service account or project exists in TS evidence yet.** Plugin discovery showed a Neon integration available but not installed/connected at this time. Its setup is the next external dependency. Do not infer account entitlements, project credits, or secret custody from a listing.

## Least-privilege physical test contract

1. Provider connection required and user chooses exact synthetic Neon project/branch (prefer dedicated project, not an existing real app). Never inspect or copy production secrets or historical Product state into the experiment.
2. Record public endpoint hostname fingerprint, region, provider PG version, TLS identity verification, two separate client credentials and host fingerprints; no full connection URLs or passwords in GitHub/Transport.
3. Test-only schema/namespace `ts_remote_r3_<random unique attempt>`; grant only create/use within this namespace and no global destructive DDL. Confirm provider allows DBOS system schema if DBOS is tested; otherwise keep basic Postgres effects isolated and report DBOS limitation.
4. Two **different physical hosts** notebook `DESKTOP-DJLBEQH` and desktop `DESKTOP-3LJ0E54`, original host A commits synthetic state/event and exits; B reads independent of A power, performs idempotent lost-ACK replay, negative authority/revision collision and conflicts. Use exactly one qualified attempt per effect and stored durable receipts.
5. P01-P07 minimum independent durability proof as frozen in `R3_HOST_AGNOSTIC_PROOF_PLAN_20261105.md`; P08-P10 backup/restore, TLS failure and owned-resource cleanup **before any recommendation to adopt**. Do not claim replacing `FilesystemInvocationArtifactStore` through a PostgreSQL-only proof.
6. No production data or automatic Product consumer migration. Kernel remains unchanged until competent Control/Developer Product decision and independent review.

## Stop conditions and evidence

Stop before provisioning if provider integration remains unconnected, credentials are missing, actual trial/billing terms are unacceptable, or TLS verification cannot be established. The **next authorized action** is to connect the Neon integration, confirm actual account/project access and a scoped provider boundary, then prepare a new exact R3 implementation candidate and preflight. No unattended provider creation or resource deletion based on this document alone.

**Decision:** `NEON_FREE_FIRST_CANDIDATE`, `R3_IMPLEMENTATION_AND_TWO_HOST_PROOF_PENDING_EXTERNAL_BINDING`, and `NO_PRODUCT_EFFECT`. R1/R2 local evidence and new A001 IR004 are separate.
