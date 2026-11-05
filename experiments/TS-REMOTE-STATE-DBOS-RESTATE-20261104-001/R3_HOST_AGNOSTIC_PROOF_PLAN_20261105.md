# TS-REMOTE-STATE — R3 physical-host-independent proof plan

**Disposition:** `DESIGN_ONLY / NOT_STARTED / NO_EXTERNAL_PROVIDER_CONNECTION / NO_PRODUCT_AUTHORITY`.
**Owner:** Tecnotron TS Execution Engineering, experimental responsibility, not FitFlow, not Product Beta Run.
**Prepared against:** `mauedgar/ts-execution-lab@7e0dab4a055e3948b90b70c62cabd65dee1be3f8` (tree `ede59d9cb55b90090b332e55a0bacbc1beaee604`); Product oracle `mauedgar/tecnotron-ai@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84` tree `25d1a151d651bb41936c69334fb0b0772ef22519`; current Product branch `tools@ac18fc398c52b2ebb9636d93dcdbdddf75f87fb1` and `docs/SOURCE_OF_TRUTH.md` blob `498d338eb98e54e294db697c5574296febf77e6f`.

## Product boundary

The SOT baseline states `State_Kernel: NARROW / final_disposition: UNDECIDED`, migration and removal NOT authorized. Kernel provides lifecycle semantics, 4 aggregates, original reducers, UNKNOWN/effect classification, monotonic revision, authority/provenance, hash-chain, late obligations, frozen receipts and CAS. DBOS is an execution/workflow durability library, not a replacement for all Product semantics. GitHub/Transport owns code, request IDs, reviews and portable evidence; a remote database would own only the admitted persisted state/effect records. Do not duplicate Upper LC, TaskCycle Core, Recipe or invent a new Product scheduler/contract.

The active Recipe compatibility binding and `FilesystemInvocationArtifactStore` have **separate** consumers. State persistence equivalence must not be called a complete filesystem/kernel removal. No existing Product input, state snapshot, event or historical UNKNOWN may be uploaded into R3.

## Operational decision

- **Primary candidate:** one independently hosted, managed PostgreSQL endpoint (PostgreSQL 16 or a provider-supported compatible version) with TLS, two different physical client hosts, and pinned isolated DBOS + Python 3.15.2 / Node22 dependencies from R2. Exact provider selection is deferred until actual access, acceptable cost, features and credentials are verified. Do not create unrequested cloud accounts, databases, users or subscriptions.
- **No notebook as permanent state server:** it would leave persistence coupled to the notebook's power, Tailnet and disk. A notebook-hosted PostgreSQL test can be a separate *transport rehearsal* but cannot satisfy independent hosted persistence.
- **No automatic DBOS or Restate adoption:** current R2 verifies only a bounded DBOS two-process replay and PostgreSQL transaction checks. Use existing Postgres + DBOS mechanics first; assess Restate only if a specific verified gap remains.
- **No provider binding before the independent R1/R2 IR002 is resolved**, even though R3 preparation may advance independently at document/fixture-design level.

## Concrete R3 proof (synthetic-only; not yet authorized to execute)

| Test | Two-host observation / stop condition | Expected evidence |
| --- | --- | --- |
| R3-P01 environment | Host A and Host B independently connect over verified TLS to a single explicit provider endpoint and database identity, using separately scoped credentials, with client/provider versions and host fingerprints recorded | No secrets in logs; exact endpoint fingerprint; both hosts independently qualified |
| R3-P02 write-read | Host A commits a synthetic aggregate-shaped state and hash-chained event at a globally expected revision, with an immutable request fingerprint | Host B, in a new process without any data copied from A, reads identical aggregate, events, hash and global revision |
| R3-P03 durability | Host A exits, disconnects or is powered off after a confirmed commit | Host B independently reopens and retrieves the same committed state; no A local storage or process required |
| R3-P04 duplicate/ACK | Host A performs a new synthetic keyed mutation then loses ACK; Host B repeats exact identity/fingerprint | One effect; one original receipt; mismatched payload/authority/revision with same key rejected |
| R3-P05 concurrency | Two separate hosts contend on same expected revision (different IDs) and same idempotency key (same request) | One winner + stale revision, or one winner + reconciled receipt; no duplicate, no forged authority, no unique-violation leak |
| R3-P06 UNKNOWN | Synthetic stored UNKNOWN attempt observed from Host B | Host B does not issue a new attempt or infer success; explicit safe reconciliation only |
| R3-P07 restart | Restart client processes (not historical Product), optionally rotate independent client connections | Same state/receipts; no new effect on resume; DBOS same synthetic workflow ID safely resumes |
| R3-P08 backup/restore | Restore a *separate synthetic database copy* from an explicit provider-supported backup or dump | Consistent state/events/receipts and hash-chain, with documented recovery point. Never overwrite source database |
| R3-P09 security | Simulate failed TLS and rejected or wrong-scoped credentials | Fail closed, no sensitive output, no privilege escalation or write to a different tenant |
| R3-P10 cleanup | Destroy only test-owned artifacts under exact returned provider IDs after proof and receipt | Ownership bound; no deletion by guessed name; report cleanup failure separately |

### Minimum evidence contract

A single distinct synthetic test namespace and generated, unique run IDs; exact Code Git commit and tree, Python `uv.lock` and Node `package-lock.json` blobs; R2 tool/runtime versions and DBOS version; controlled host A/B fingerprints (avoid personal machine details in public receipts); provider identity as safely redacted hash/fingerprint; TLS mode; normalized read/write outputs; statement of no Product writes; test and cleanup outcomes separately. Each client process produces its own signed or SHA-256 hashed receipt; Transport combines only after an identity/digest reconciliation. Never claim `exactly-once` for arbitrary external provider side effects.

Minimum meaningful independent proof: **P01-P07** from *two distinct physical hosts against hosted persistence*. P08-P10 are required before recommending a production adoption/cutover, not necessary for preliminary connectivity proof. Distinguish `R3_CONNECTIVITY_ONLY`, `R3_DURABILITY_PROOF` and `R3_REVIEWED` as descriptive experiment result labels, **not** Product lifecycle states.

## Isolation and activation order

1. **Current authorized work:** preserve existing R1 source `76814d5fa5c2bd5f2a19887823d5881cafd81c77`; no more runner patch iterations without a new terminal failure. Prepared runner v3 `7e0dab4a055e3948b90b70c62cabd65dee1be3f8` blob `0655ebcc74a5a57a8b9557146351e36ec56b9839` has no new full Docker PASS. A prior local attempt `TS_REMOTE_R1_LOCAL_20261104_001` had test PASS but process exit 1 on cleanup. Previous Commander probes to check Docker readiness and free attempt ID were denied, so preserve `BLOCKED_PRECONDITION` and **do not route denied probes through another tool**.
2. **Independent IR002 request already frozen:** `mauedgar/ts-execution-transport@5228b6b85ac3f5cffcc36953a731810fb3ea6352:reviews/TS-REMOTE-STATE-R1-R2-IR002-LOCAL-20261105-001/REQUEST.md`. It activates only after a distinct fully terminal R1 local result with valid cleanup and verified unchanged R2 evidence. Old IR002 request depended on GitHub Actions `41877732907` completed/success, which instead was terminal failure. Do not fabricate or reuse it.
3. **If IR002 findings/advisories:** Execution Engineering repairs real issues on a **new frozen candidate**, performs independently qualified validation, and requests an independent IR003 over that exact identity. Keep original review receipts immutable. A reviewer does not self-patch or accept the candidate. Developer authorization to repair does not grant Product integration.
4. **Only after R1/R2 qualified and separate experimental provider scope confirmed:** provision or select hosted PostgreSQL as a one-shot explicit provider operation with least-privilege credentials and no Product data. Validate P01-P07, then independently evaluate recovery, security and cleanup P08-P10. No automatic background poll, retry or hidden external action.
5. **Product adoption separate:** if and only if R3 evidence and independent review support the solution, propose a distinct Product consumer migration decision to competent Control, with actual authorization and guarded Phase 2. Legacy Kernel stays intact and readable until accepted cutover; artifact-store migration and historical records are separate decisions.

## Readiness/deferral matrix

- **Available:** local Docker Engine both hosts (per observed receipts), WSL Ubuntu, Git objects, Node22, Python R2 locks, isolated R1 synthetic PASS logs, remote Git/Transport evidence. These establish neither an authorized fresh host preflight nor real provider credentials.
- **Missing:** full new R1 runner terminal PASS, independent IR002 PASS, hosted Postgres endpoint and confirmed TLS/auth, credentials for each physical client, justified provider budget/availability, two-host proof. Do not infer them from installed software or user's earlier intent.
- **Stop and report:** any tool safety denial, unknown previously launched operation, missing exact Git subject, unexpected provider effects, secrets in a log, Product write conflict, DBOS/R2 lock drift, uncertain recovery identity or unverified cleanup.

**Current result:** `R3_PLAN_READY / R3_EXECUTION_NOT_STARTED` — an executable acceptance specification, not implementation or Product decision.
