---
artifact_id: TS-R3-A02-NATIVE-PG16-CI-QUAL-20261111-001-A003
kind: DISTINCT_NONPRODUCT_NATIVE_PG16_CI_ORIGINAL_EFFECT_INTENT
date: 2026-11-11
owner: TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL
status: PREPARED_BEFORE_ORIGINAL_DISPATCH
product_effect: NONE
neon_effect: NONE
external_database_effect: NONE
physical_a02: NO_GO
---
# A003 independently identified native golden DDL repair

This is a NEW original experimental attempt distinct from historical A001 (run 43033888589, terminal FAILED parser) and A002 (run 43034758039, terminal synthetic CI PASS). No rerun, overwrite or correction of terminal provider receipts. The independent source review PR19 IR001 terminal NO_RECOMMEND/FULL_SOURCE, 1 HIGH finding and 4 advisories, is preserved EXACTLY at mauedgar/ts-execution-transport@b0a96af0dcccf54027ad3536c7afa36ad57d13ef:results/TS-R3-A02-NATIVE-PG16-PR19-WEBINLINE-IR001-20261111-001/ORIGINAL.md. Control disposition @893609785ccaa32e68ede173d0c4dc72282a4ceb records the repair selection. This is within the user's delegated nonProduct TS Remote State experimental repair scope; NOT a Product-level grant.

Product SOT mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88 remains authoritative. DRAFT PR15 frozen HEAD 67941b33ee077ba8fc0dbcda0196232dbd7895eb and DRAFT PR19 native A002 HEAD 7bfc538bd2f3bb1a314700e565d3608ef6df7de9 are unchanged, unmerged. This successor isolated branch ee/ts-r3-a02-native-pg16-qual-20261111-003 starts exactly at PR19 native A002 HEAD and has a THREE-new-file write set:
- a02_lan/native_pg16_ci_qual_003.py blob 5aac1d747b207b8226741848e7f4e3b3a9f44821;
- this NATIVE_PG16_CI_QUAL_INTENT_003.md;
- workflow .github/workflows/ts-r3-a02-native-pg16-qual-20261111-003.yml.
All source files paths are under experiments/TS-R3-KERNEL-GLOBAL-HEAD-20261107-001 except .github workflow. Original role_boundary.py blob 26110b845ae98f3590f6d7580b779ff968b40390 and schema.sql blob 3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0 MUST NOT change.

F01 HIGH repair: create an independent second native PostgreSQL instance of the frozen schema inside the **already present default postgres database** of one disposable Actions service, owned by the same synthetic owner role. The original lab database retains exactly the two databases postgres/lab expected by source role guard; no Golden extra database is created. Compile the same four-statement frozen Git schema in lab and only its three table DDL statements in separate default postgres DB schema, with original owner identity. Compare full actual catalog snapshots (all columns incl collation and default expression, constraints with pg_get_constraintdef, conkey, FK target/columns, index pg_get_indexdef, indexed key order/predicate/expression and flags) across separately instantiated databases in repeatable-read READ ONLY transactions, supplemented with frozen known 3 tables/19 columns/18 constraints/5 indexes. The golden comparison derives from a distinct native compilation of an independently frozen, immutable original SQL source and does NOT itself qualify the Product physical schema golden nor arbitrary SQL engine correctness.

Adversarial same-count tests after the existing 5 role privilege negatives include: modify CHECK predicate with same name/type/count, alter FK ON DELETE action while retaining name/count, swap UNIQUE constraint key while preserving associated index name and total count; each must differ from read-only golden snapshot while the known deliberately bounded source guard alone can still pass. Restore all changes, require exact golden snapshot equality. The old extra CHECK count scenario remains. Important: do not silently extend Product privileges, use writer as owner, bypass source guard, or run original physical writer A/B. Preflight now checks parsed frozen four statements BEFORE any ephemeral role/DB provisioning.

A01 reviewer advisory: pin actual Docker image manifest SHA256 aa6cb33cf4c19c765cefcf48d96176258800870a9a1e930ad126200f9d825139 as observed directly in the terminal A002 original GitHub job logs for PostgreSQL16.15; all actions pinned SHAs, uv0.13.7, Python3.15.2 and psycopg binary3.3.8. Workflow only push to this unique branch when its new workflow file is created, no manual/recurrence/rerun; GITHUB_RUN_ATTEMPT must equal 1. Original run is bound to exact Git SHA through immutable GitHub provider run receipt. Repository-level token contents:read, checkout persist-credentials false. A02 cleanup/teardown remains ephemeral service constraint, not original physical host proof.

Expected one new GitHub Actions run at original ExecutionAttempt TS-R3-A02-NATIVE-PG16-CI-QUAL-20261111-001-A003 with terminal status; report actual CI markers and golden SHA256 if PASS; if FAIL preserve original as terminal, no automatic retry. Actual fixture SQL/role provisioning occurs ONLY inside the Actions disposable PostgreSQL service; no external DB/Neon/notebook/Product effect. New source/CI STILL requires independent review before source acceptance. Four physical advisories and original IR006 full JS/Python differential remain OPEN, A02 physical NO_GO.
