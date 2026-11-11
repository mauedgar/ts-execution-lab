---
artifact_id: TS-R3-A02-PG16-NATIVE-SCHEMA-ATTESTATION-20261111-001
kind: NONPRODUCT_NATIVE_CONTROL_PRE_ADMISSION_SPECIFICATION
status: SOURCE_ONLY_SPEC__PG16_NOT_RUN__PHYSICAL_A02_NO_GO
owner: TS Remote State 002 / competent native Control
date: 2026-11-11
product_authority: NONE
source_effect: NONPRODUCT_DOC_ONLY
database_effect: NONE
---
# A02-LAN original PG16 physical admission — native schema definition attestation

## Authority and scope

This is an **additional evidence requirement within the existing physical A02 preflight**, not a new Product actor, scheduler, TaskCycle gate, SQL permission, role-provisioning attempt, DDL/grant authorization or Product integration. It does **not** itself execute any SQL or qualify the source guard. The existing Product filesystem State Kernel remains authoritative. Original terminal A001 SECURITY_DENIED, A11 local 0F/0A, source IR001/IR002/IR003 and all physical receipts are immutable; no replay.

Source IR003 `TS-R3-A02-LAN-LP-PR14-IR003-A001` was `NO_RECOMMEND / PARTIAL / 0F / SA01 1 / physical A01–A04 OPEN`. Source guard `a02_lan/role_boundary.py` currently checks selected catalog object names, types, relation owners and privilege matrices. It is **not** a complete DDL-definition attestation and must not be presented as such. The next source-only repair checks RLS/force-RLS, persistence, partition marker, relation options, index valid/ready/live/primary/unique/exclusion, but complete live **column, constraint and index definition parity** remains a separate required native observation.

## Frozen source target / mandatory preconditions

- Independent native Control must first identify a **disposable nonProduct** dedicated PostgreSQL 16 cluster and exact original Docker container ID + dedicated volume/cluster system identifier/host, freeze both physical client fingerprints, and confirm network exclusivity, no cross-Product credentials, and no foreign object/DB footprint.
- Freeze original schema source at `mauedgar/ts-execution-lab@96993b370ddb0e822d1d464bc3f08e31ab44dea5:experiments/TS-R3-KERNEL-GLOBAL-HEAD-20261107-001/schema.sql`, blob `3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0`. Source **three** tables: `head`, `events`, `receipts`. Original schema creation and genesis effects require their own distinct durable write-ahead intents and receipt reconciliation. A prior UNKNOWN or foreign DB means NO_GO.
- Actual restricted writer identity `tsr3_a02_writer` MUST be distinctly provisioned with an original independently reviewable role/grant effect + receipt; its no-owner/no-membership/no-CREATE/no-TEMP/default-PUBLIC and exact function EXECUTE evidence requires native validation. NEVER connect writer A/B with the historical superuser owner `tsr3_a02_lab`.
- Do not run this attestation against Production, Neon production, another User's data, a host not tied to the original known system identifier, or a stale/unverified Git candidate. **No target host is authorized solely by this document.**

## Required one-snapshot native read-only inventory (spec only, NOT_RUN)

A competent native read-only observer with *separately attested* rights must, within one consistent `REPEATABLE READ READ ONLY` transaction on the original disposable database, acquire:

1. Database/owner/server identity: `current_database()`, `current_user`, `session_user`, PostgreSQL major, externally observed original `system_identifier` and native container+volume; no inference from arbitrary client variables or `application_name`.
2. All `pg_namespace` user schemas and `pg_class` rows incl relation kind, actual owner, `relrowsecurity`, `relforcerowsecurity`, `relpersistence`, `relispartition`, `reloptions`; exact three ordinary tables + five implicit PK/UNIQUE indexes and no additional user object. Record RLS forced/enabled flags, no hidden policies and no noninternal user triggers.
3. **Every `pg_attribute` for the three tables**, in `attnum` order: name, `format_type(atttypid,atttypmod)`, `attnotnull`, `atthasdef`, `attidentity`, `attgenerated`, `attcollation`, default/generated expression with `pg_get_expr(pg_attrdef.adbin,pg_attrdef.adrelid)`, and column ACL. Reject dropped, additional, reordered, unknown-type or defaulted columns. Frozen expected declarations from `schema.sql`: `head` six columns (scope text PK NOT NULL, revision bigint NOT NULL, state_bytes bytea NOT NULL, state_sha256 text NOT NULL, events_sha256 text NOT NULL, last_event_hash text nullable); `events` six columns (scope text NOT NULL, revision bigint NOT NULL, event_hash text NOT NULL, previous_event_hash text nullable, payload_bytes bytea NOT NULL, event_line bytea NOT NULL); `receipts` seven columns (scope text NOT NULL, mutation_id text NOT NULL, command_fingerprint text NOT NULL, expected_revision bigint NOT NULL, result_revision bigint NOT NULL, event_hash text NOT NULL, authority_fingerprint text NOT NULL). No defaults/identity/generated columns were defined.
4. **Every `pg_constraint`** on the three tables: `conname`, `contype`, `conkey`, `confrelid`, `convalidated`, `condeferrable`, `condeferred`, and normalized `pg_get_constraintdef(oid,true)`. Compare to exactly: PK for each table; UNIQUE `events(scope,event_hash)`, `receipts(scope,result_revision)`; FK `events.scope` and `receipts.scope` reference `head.scope`; every `CHECK` declared by the frozen SQL for numeric revisions and 64-char lowercase hex hashes; reject altered, missing, unvalidated or added constraints. No assumption that a name-only match proves expression equality.
5. **Every `pg_index` row** for the five indexes: `indisunique`, `indisprimary`, `indisexclusion`, `indisvalid`, `indisready`, `indislive`, `indnullsnotdistinct` and `pg_get_indexdef(indexrelid)`. Match each normalized definition, indexed column order and predicate/expression to the frozen PK/UNIQUE declarations; reject pending/invalid/rebuilding or extra indexes.
6. Namespace-scoped `pg_type` rows, user operator/collation/conversion/opclass/opfamily/text-search/stats, and relevant nonnamespace catalogs and PUBLIC grants. Do **not** mistake the six automatic table composite/array types for unexpected user types. Record global-owner/public/unscoped object uncertainties separately; no blanket empty-cluster claim from only one schema's catalogs.

Any divergence or uncertainty => **BLOCKED_PRECONDITION** / physical NO_GO without any A/B write. Unknown connection/commit ACK or inconsistent provider-native identity => **UNKNOWN**, no retry. A green source-only CI is never native SQL evidence.

## Required durable, reconciled result (future, not created here)

A future competent read-only native operator would return an **original create-only receipt** binding `Original_ExecutionAttempt`, frozen Git commit/tree/schema blob, PG major+original cluster ID hash, exact database, server identity, native host identity and observer credential class (not secret), snapshot time/transaction, stable canonical JSON of table+index+column+constraint+RLS inventory with SHA-256, required counts, each discrepancy, native queries/exits, and `database_effect: NONE` for this read-only attestation. Report independently `PASS`, `BLOCKED_PRECONDITION`, `FAILED` or `UNKNOWN` with source exclusions; do not invent a future result path or state Product PASS.

The Control must validate exact receipt identity/bytes and compare against an independently reviewed known-good native PG16 fixture of the immutable schema, not against self-authored FakeConn values alone. The reference fixture's own DDL/materialization has independent effect/authority and cannot be assumed to exist. Until these obligations and the separately scoped role/ACL provisioning are satisfied, **PHYSICAL_A02_NO_GO**, even if source review reaches 0F/0A. In particular, no extra PostgreSQL rights may be granted merely to make a failing attestation pass.

## Relationship to remote-state goal

This local PG16 experiment is a **qualification fixture**, not mandatory permanent hosting; backend retirement still requires **host-independent** Neon/DBOS equivalence, failover/lost ACK, durable provenance, zero-cost/free-tier admission and competent Developer Product acceptance. No change to Upper LC/TaskCycle Core is made by this contract.
