---
artifact_id: TS-A02-INDEPENDENT-PHYSICAL-GOLDEN-READONLY-PREFLIGHT-v1
owner: TS_REMOTE_STATE_002_EXPERIMENTAL_CONTROL
kind: NONPRODUCT_PROPOSED_PHYSICAL_ORACLE_READONLY_PREFLIGHT
status: FROZEN_PROCEDURE_NOT_EXECUTED
date: 2026-11-11
Product_effect: NONE
database_effect: NONE
physical_admission: NO_GO
---
# TS Remote State — A02 independently curated physical golden, read-only

## Basis, distinct from identity A01
PR20 original IR002 NO_RECOMMEND / FULL_SOURCE / 0F / 2A. Advisory A02: two native PostgreSQL databases created by the **same program, from the same frozen schema.sql file, in the same ephemeral cluster** can agree while both carry an identical source or implementation defect. Their PG16.15 consistency is useful bounded CI evidence, **not independent physical schema attestation**. A003 original Actions run 43037911945 SUCCESS remains terminal; this procedure does not rerun it.

Product SOT mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88, docs/SOURCE_OF_TRUTH.md, preserves filesystem Kernel authority. PR15 original candidate commit 67941b33ee077ba8fc0dbcda0196232dbd7895eb, schema.sql blob 3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0, native PG16 contract blob 81988e0659f3b88fe5aee00ed44fda9b53ad0dd2 and PR20 original isolated CI A003 HEAD b9263f8e20dad3b6c2060cff55b1abbc7bfdecd4 remain unchanged. Neither acceptance nor physical original A02 effects are granted.

## Stage P0: compulsory identity/authority/absence verification — BLOCKED by default
Control must recover and freeze a single competent real A02 TaskCycle responsibility and original ExecutionAttempt, not recycle denied A001 or completed A11/A02 synthetic attempts. Before any physical connection, identify and verify an expressly dedicated, disposable **nonProduct** PostgreSQL16 cluster and exact physical host, container ID, volume ID and cluster system_identifier from competent native receipts. Freeze actual network exclusivity, separate notebook Control witness versus remote desktop writer sites, original roles/owner grants, original schema DDL/genesis effects and admission receipts. No incidental desktop Docker container, default local Postgres or Neon project is implicitly an A02 target.

Prerequisite independent authorization matrix must identify:
- owner competent for reading on this exact host;
- dedicated observer connection with read-only privileges, which cannot be writer A/B or admin fallback in disguise;
- explicit original physical operation ID and exact expected read-only receipt path;
- approved safe target DB/connection binding (never log a password/DSN);
- no UNKNOWN original effects, foreign schemas, credentials, external users or competing TaskCycles.

Any missing identity/receipt, stale Git ref, unverifiable role, foreign database footprint, unrestricted credential, or UNKNOWN: return BLOCKED_PRECONDITION and **do not connect**. No extra rights, provisioning, grants, schema migration, server startup, synthetic data injection, A/B writes or undo actions to satisfy this preflight. Physical selection and credential authorization are separate Developer/competent Control decisions.

## Stage P1: independently authored expected oracle, WITHOUT live DB access
A reviewer **different from native harness author** must derive an expected schema manifest from the frozen source SQL, using a separately implemented, deterministic parser or hand-checked explicit inventory rather than reusing native_pg16_ci_qual_003.py or copying its just-observed JSON. Peer-check all constraints/keys/FK actions and normalized PG16 definition rules. The original immutable oracle must enumerate:
- exactly 3 ordinary permanent tables: head (6 columns), events (6), receipts (7);
- 19 exact ordered columns: name, type, NOT NULL, collation, identity/generated/default, dropped flags;
- 18 constraints: exact names/type, CHECK formulas, PRIMARY/UNIQUE key order, FK referenced table/key and update/delete actions, validated/deferrability;
- exactly 5 indexes: name, keys/order, uniqueness/primary, predicate/expression, valid/ready/live and nulls-not-distinct;
- table owner and RLS/force-RLS/persistence/options/partition state, automatic row/array type footprint, no unauthorized foreign table/function/type/operator/trigger/policy;
- exact expected PUBLIC, owner, writer privilege matrix, schema/database CREATE/USAGE/CONNECT/TEMP, membership/grant options and allowed pg_catalog.pg_control_system() EXECUTE.

The oracle is reviewed and frozen on a durable Git immutable commit with measured SHA-256, reviewer identity, expected PG16 version and specific normalization rules. **No new live database/role is created** while constructing the oracle. Self-generated reference copied from the same fixture/cluster **is explicitly forbidden** as independent golden.

## Stage P2: independent native READ ONLY observation (NOT RUN)
After P0/P1 PASS and a separately authorized original reader effect: competent observer connects to the exact admitted disposable nonProduct PG16 host via established native binding. Execute a single REPEATABLE READ READ ONLY transaction observing pg_namespace, pg_class, pg_attribute, pg_attrdef, pg_constraint, pg_index, pg_type, pg_roles/pg_auth_members, role ACLs/has_*_privilege, pg_proc, relevant functions and namespace-scoped operator/collation/trigger/policy state. Compare **each full normalized definition** against the independent golden; all discrepancies => FAIL / BLOCKED_PRECONDITION. Query actual current_database(), current_user, session_user, server_version_num and pg_control_system() system identifier only if separately authorized and privilege-attested; no elevation and no fallback to owner if denied. Record time/snapshot/transaction status and native query outputs with credential secrets redacted.

The observer must not run DDL, change ACL/roles, insert/update/delete Product or lab data, simulate a fault, or touch other databases. This is an observation, not re-provisioning. Actual network/IP and container/volume identities must derive from native trusted receipts, not editable SQL session tags. An exact SQL source without a physical original host identity is still BLOCKED.

## Stage P3: original durable receipt and Control join
One create-only immutable result ties: responsibility and original ExecutionAttempt, Product source authority, frozen PR15/schema oracle Git blobs and SHA-256, target physical host/cluster/container+volume hashed identifiers and native witness, identity of actual observer/credential class (not secret), PostgreSQL16 major/minor, stable normalized per-column/constraint/index/ACL inventory, SHA-256 of raw observation and comparison report, number/severity of discrepancies, granted read-only scope, start/end and original provider-native proof. Record effect READ_ONLY_OBSERVATION_CONFIRMED with no DB mutation; UNKNOWN means no conflicting future effects. A read receipt alone never authorizes A/B writer effects; it only satisfies this subrequirement.

Control independently verifies exact original native result bytes/identity and reconciles with original DDL/genesis/role authority, PA01–PA04, physical two-host lock graph, lost COMMIT ACK, outage/restore and external Neon/DBOS host-independent persistence. If all are not satisfied: PHYSICAL_A02_NO_GO and Product Kernel replacement NOT_GRANTED.

## Current disposition
- P0: BLOCKED — no current independently verified original physical target/container/volume/role receipt available in this responsibility. Do not guess from memory, user location, synthetic GitHub service or prior Docker installation.
- P1: SPECIFIED, source-only; independent oracle construction/review NOT_RUN.
- P2/P3: NOT_RUN; no host/DB effects.
- A003 bounded native CI proof: CONFIRMED, unchanged.
- PR20 IR002 A02: OPEN for independent physical qualification, not a source-only repair and not suitable for an IR retry to chase 0A.
- All physical PA01–PA04 and Product replacement: NO_GO.

This supplements the existing NATIVE_SCHEMA_ATTESTATION_CONTRACT.md; it creates no new Product actor/state/gate/scheduler and cannot override a prior SECURITY_DENIED or UNKNOWN effect.
