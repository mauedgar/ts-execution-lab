# H6 Attendance V0 — Control-frozen legacy v1 idempotency exception

Evidence class: CONTROL_COMPATIBILITY_REFREEZE_CANDIDATE
Status: FROZEN_FOR_BOUNDED_CONTROL_EVALUATION; NOT_PRODUCT_ACCEPTED
Owner: TECNOTRON_BETA_RUN_001 / issue #35
Date: 2026-11-02
No independent TaskCycle, no Phase2, no canonical Product effect.

## Original governing interface

Unmodified V0 at `mauedgar/ts-execution-lab@f6ea85050734bfd7f0fd2a8fa4c6d1f869f134bc:attendance/contracts/attendance-v0.md`, blob `2e939672a8401154289ea94aab83194f689247f0`; original Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`. This is a **narrow Control-ruling candidate**, not a silent edit of V0 or acceptance. Preserve all other V0 behavior and both original child write owners.

## Source of material exception

Original independent IR002 and IR003 original receipts:
- IR002 `mauedgar/ts-execution-transport@ee041e3ec459f3fe29a495654e6be8e882539b8b:results/TECNOTRON-H6-IR002-DOMAIN-OPERATOR-20261102-001/ORIGINAL_REVIEW_RESULT.json`.
- IR003 Domain `mauedgar/ts-execution-transport@e389023f9428ee9f273f90ff26d8aef3b893b3db:results/TECNOTRON-H6-IR003-DOMAIN-20261102-001/ORIGINAL_REVIEW_RESULT.json`.

Original v1 stored a `request_id` signature only after UTC normalization and discarded the original `occurred_at` argument bytes; those bytes are mathematically unrecoverable from v1 DB. V0 requires identical operation+arguments; implementing a strict new literal-byte comparison on these historical keys would falsely reject replay of an original call. Replacing v1 signatures with invented original argument bytes is forbidden.

## Narrow proposed/authorized Control disposition for the bounded historical migration

1. **New v2 requests:** all new `(subject_id, request_id)` are literal `operation + caller occurred_at` signature keys. Exact same caller arguments replay persisted response. Any textually different `occurred_at`, including another UTC offset for the same instant, must yield typed `REQUEST_CONFLICT`; no state change. This is V0 default.
2. **Only keys proven already persisted under schema v1:** explicit grandfather exception. The only provable historical identity is exact `operation + canonical UTC instant`, so v1 replay matches at that granularity, returning original persisted response, with no duplicate effects. Different canonical instant/operation must be typed `REQUEST_CONFLICT`. This exception MUST be tagged persistently `signature_version=1`, cannot be used for new v2 requests, and cannot be inferred from any unversioned future payload.
3. **Boundary and admission:** a storage file with `PRAGMA user_version=1` is eligible for atomic migration only if its historical rows have provably valid schema/signature/response and the original request identity can be represented without inventing bytes. A malformed signature or future schema version fails closed with typed `STORAGE_ERROR`, no partial migration; all state commits are atomic. Every v1 session/read still respects the V0 storage and open-interval invariants.
4. **Compatibility traceability:** the V0 contract remains an immutable predecessor. All fresh review interfaces for affected Domain/Operator must cite this exact approved addendum SHA plus V0 blob and the updated Control disposition. If Control does not make the compatibility ruling competent, candidate review remains `BLOCKED_POLICY`; this file alone has no authority.
5. **No additional schema/policy surface:** no Beads adoption, Kernel migration, scheduler, role, second Product SOT or new TC. User specifically authorized Control to evaluate and refreeze a material V0 semantic change on 2026-11-02 while continuing #35; integration/Developer acceptance/Phase2 are still separate.

## Tests and review

Mandatory adversarial coverage of an actual v1-produced request key, ordinary v2 literal replays, v1 alias by equivalent UTC with different original text, non-equivalent conflict, restart and malformed v1 signature/response, migration atomicity/rollback, and invalid SQLite filesystem paths. The three existing IR003 advisories remain until independently closed. Run native Python3.12 on exact new candidate, then a genuinely separated new Domain IR004; separately assess Operator original IR002 and corrections. No IR003 replay or automatic acceptance.
