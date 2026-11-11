---
artifact_id: TS-R3-A02-NATIVE-PG16-CI-QUAL-20261111-001
execution_attempt: TS-R3-A02-NATIVE-PG16-CI-QUAL-20261111-001-A001
owner: TS_REMOTE_STATE_002_NONPRODUCT_CONTROL
kind: ORIGINAL_FROZEN_SYNTHETIC_NATIVE_PG16_CI_EFFECT_INTENT
status: PREPARED_BEFORE_GITHUB_ACTIONS_DISPATCH
date: 2026-11-11
product_effect: NONE
real_a02_effect: NONE
neon_effect: NONE
---
# Native PG16 source/privilege qualifier — single original CI intent

## Authority, source subject and allowed write set
Authorized after terminal IR006 `NO_RECOMMEND/PARTIAL`, source graph 21/21 local files reviewed but external PostgreSQL catalog/role behavior and complete JS/Python differential not proven. This is a **new** bounded experiment under TS Remote State; it is not a replay of IR006 or an attempt to execute the historical A02 physical original, and does not grant Product acceptance or Kernel migration.

Product SOT `mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88`, `docs/SOURCE_OF_TRUTH.md` blob `498d338eb98e54e294db697c5574296febf77e6f` remains canonical. DRAFT PR #15 `mauedgar/ts-execution-lab@67941b33ee077ba8fc0dbcda0196232dbd7895eb`, tree `21f1953335ddab18f7ea5ce4726fcc92be618837` remains unchanged/unmerged; candidate branch `ee/ts-r3-a02-lp-ir003-repair-20261111-004` has no write in this experiment. This test instead has an independent branch `ee/ts-r3-a02-native-pg16-qual-20261111-001`, created exactly from the frozen PR15 HEAD, with write-set ONLY:
- `experiments/TS-R3-KERNEL-GLOBAL-HEAD-20261107-001/a02_lan/native_pg16_ci_qual.py`, source Git blob `a11a5cdda6b5e9ff453b6b1ae72169d2f905d8db`;
- this `NATIVE_PG16_CI_QUAL_INTENT.md`;
- new isolated `.github/workflows/ts-r3-a02-native-pg16-qual-20261111-001.yml`.

The original baseline `schema.sql` Git blob `3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0` and `a02_lan/role_boundary.py` Git blob `26110b845ae98f3590f6d7580b779ff968b40390` are **read-only verified**, not modified. The workflow is triggered ONLY on the one push containing its new YAML file to this separate branch, no cron/workflow_dispatch/pull_request trigger. No duplicate run/semantic retry is authorized for failure or UNKNOWN.

## Fully bounded temporary effect
GitHub-hosted Ubuntu 24.04 runner provisions a private `postgres:16-alpine` ephemeral service at localhost:5432; no remote source DB, Neon, VPN/Tailnet, notebook, Product or personal credentials. Static intentionally public, synthetic credentials are accepted ONLY as disposable CI fixture credentials; they are not secrets and never contact any external database. Script validates exact Git branch/event, PG16 major, pristine roles/database, frozen schema and current-user role/ACL/owner. It creates `tsr3_a02_lab` owner role/database and distinct `tsr3_a02_writer` restricted role only inside this service, runs original four-statement frozen schema, grants narrowly bounded database/schema/table rights and exact `pg_control_system()` function EXECUTE.

Real writer connection executes the **unchanged actual source `assert_writer_boundary`** against PostgreSQL16 native catalog/ACL, then truly executes `pg_control_system()`. Five native negative scenarios mutate and then restore ONLY ephemeral CI state: revoked SELECT, excessive DELETE, ENABLE RLS, rogue enum, revoked `pg_control_system()`; each must fail with exact guard code and pass restored baseline. Independent repeatable-read **READ ONLY** owner inventory reads three original tables, 19 columns, 18 constraints, five indexes, RLS flags and index validity, verifies declared counts/types/flags and stores canonical SHA256; an extra CHECK constraint must change that native digest, proving the source guard's bounded definition gap, then be removed before final readback. No writers or business data are operated; no original physical A02 attempt, persistent DB/user, Neon or Product effect.

## Strict limitations, expected native receipt and join
This does NOT test full JS/Python domain differential, real two physical clients/host IDs, lost COMMIT ACK, real outage/recovery/restore, or guaranteed native PG16 schema attestation on the user's notebook. Native snapshot is an internally checked isolated reference, **not** an independently qualified original golden dataset for real A02. `postgres:16-alpine` is major-pinned, not exact digest-pinned; report runtime minor and digest immutability caveat if known. Test fixture applies DDL and grants *only to its own GitHub ephemeral PostgreSQL service*; this is an actual synthetic CI database effect, not `database_effect: NONE` within the runner. It has `external_database_effect: NONE`, `Product_effect: NONE`. If the guard rejects the clean native state, this is a genuine BLOCKED/FAIL finding candidate, not a reason to weaken real permissions or to use admin as writer.

Expected one provider-native original workflow run at exact candidate HEAD, job and raw logs containing either unique JSON status `NATIVE_PG16_CI_SOURCE_GUARD_AND_ATTESTATION_PASS` with attempt, negative scenario count 5 and native snapshot digest, or one sanitized `NATIVE_PG16_FAIL_*`. Control must observe the original GitHub Actions run once and retain actual `run_id`, `job_id`, `commit/tree`, error, exact original result/log markers, effects and advisory disposition. Source/CI tests don't constitute Independent Review or Product acceptance; new code may require a different independent review/repair candidate if findings arise. If run FAILED/BLOCKED/UNKNOWN, do not rerun blindly. Physical A02 remains `NO_GO` and four physical advisories remain OPEN.
