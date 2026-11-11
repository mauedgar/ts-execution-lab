# A02-LAN restricted writer role — source-only repair candidate

**Scope:** NONPRODUCT / experimental only. **Status:** SOURCE_ONLY_CANDIDATE, NOT_SQL_APPROVED, NOT_PRODUCT. No role, credential, schema, database or service mutation is authorized by this file. All historical attempts and A11/A001 effects remain immutable.

## Ownership and identity

- Existing lab bootstrap/database/schema/table owner is `tsr3_a02_lab`. It is historically a PostgreSQL cluster **superuser**; this credential must remain notebook-local and must never be used by remote writer A/B, nor exported in a GitHub receipt. Physical security admission remains blocked until a distinct restricted role is verified.
- New **proposed, not created** login is `tsr3_a02_writer`: `NOSUPERUSER NOCREATEROLE NOCREATEDB NOREPLICATION NOBYPASSRLS LOGIN NOINHERIT`, no memberships at all (including owner, `pg_monitor`, `pg_read_all_data`, `pg_write_all_data`), no grant options, no ownership, no `SET ROLE` escalation. The actual secret would be created separately through an authorized protected channel, not in a source artifact.
- Only the owner on the notebook may run `setup`, `reconcile-ddl`, `reconcile-genesis` and the **read-only Control witness**. Holder, two writers, verify and read-only mutation reconciliation select the restricted role. The witness uses the existing local Control/owner credential (historically a superuser) only for notebook-local observation; that credential is NEVER supplied to either A/B writer or desktop. A future dedicated observer identity, if needed, is a separate ungranted design.
- The existing `schema.sql` blob `3b1604bd7aca0f7cf6c8db84fa615913fa39e9f0` remains byte-identical. Any live role creation/grant/revocation/bootstrap/DDL or genesis requires separately scoped and receipted effects, not this source-only review.

## Proposed effective privilege matrix (none issued)

| Object | Required for restricted writer | Explicitly denied / absent |
| --- | --- | --- |
| Dedicated database `tsr3_a02_lab` | CONNECT | CREATE, TEMP/TEMPORARY |
| Schema `ts_r3_global_head_20261107_001` | USAGE | CREATE |
| `head` | SELECT, UPDATE (including FOR UPDATE) | INSERT, DELETE, TRUNCATE, REFERENCES, TRIGGER |
| `events` | SELECT, INSERT | UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER |
| `receipts` | SELECT, INSERT | UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER |
| Other databases/tables/functions/roles | No newly granted object privileges | Role ownership, admin memberships, other Product capabilities |

These are *effective* grants: inherited PUBLIC privileges (especially database TEMP), owner implied permissions, inherited memberships and predefined roles must be accounted for. The source guard checks actual `has_database_privilege`, `has_schema_privilege`, `has_table_privilege`, grant options, `pg_auth_members`, `rolinherit` and a restricted `pg_control_system()` EXECUTE privilege. It also rejects unexpected user schemas, non-A02 relations/table owners, public/custom functions, column ACLs, foreign cluster roles/databases/extensions **inside this isolated fixture**. This does not prove privileges in other databases, remote host identity, network ACL or catalog attestation across a disconnected server. The metadata guard is not a substitute for an independent real PostgreSQL 16/driver-based least-privilege negative test.

## Rollout must remain disjoint

1. Native Control freezes host identity, original isolated target Docker ID / volume / cluster system identifier, exclusivity, and verifies role/bootstrap owner is still synthetic-only. Any mismatch => NO_GO.
2. Separate original role-provisioning attempt (not defined or executed here): a privileged local administrator only, a disposable isolated database, least-privilege role/grants, no secret disclosure. Do not treat the historical superuser role as the proposed writer.
3. Separate qualified original DDL+genesis intents and effective privilege test in PostgreSQL 16. **Current frozen setup requires two original write-ahead effects**, so any new order involving role creation needs its own protected durable intent and reconciliation contract first.
4. Freeze source change as a distinct commit and run new source-only tests. Independent IR evaluates full changed files, privileged transitions, schema assumptions, source status, native provisioning compatibility and negative tests. The previous IR005 SOURCE_ONLY review did NOT cover this new commit.
5. Only afterward may competent Control consider a new physical two-host attempt under original receipts and strict no-retry, assuming WSL/host-lifecycle and Tailnet ACL plus SQL connection identity admit it.

## Remaining blockers explicitly NOT solved

- Original host WSL foreground keepalive exited; Windows reported no running distros. No persistent service/daemon lifecycle was established.
- Native remote PostgreSQL client authenticated over Tailnet, ACL and unique cluster identity remain unqualified. `pg_control_system()` on the restricted writer must have actual EXECUTE privilege for this source path, checked explicitly by `has_function_privilege` with **no grant option**; a narrowly reviewed, original-effect-scoped GRANT on that one system function is the proposed compatibility path. Do not bypass via `pg_monitor`, role membership or superuser, and do not claim the function is callable without real PG16 tests. Qualify this access on a separate synthetic PG16 fixture, or use a reviewed independent native Control attestation mechanism.
- The `witness` mode requires visibility of other sessions. It is now bound to the notebook-local owner/Control path and cannot be called from the desktop or via the restricted A/B writer credential. A privileged local Control credential is not a least-privilege monitoring solution; any eventual dedicated observer requires separate role/ACL qualification. No new role was created.
- Source-only tests use a fake SQL metadata connection. They do **not** prove real PostgreSQL grants or first physical CAS, actual lost COMMIT ACK, outage/restart or Product Kernel equivalence.
- For the **final remote-state goal**, WSL/local PG16 is a disposable fallback/testing fixture, not a permanent host-independent storage owner. Neon Free hosted Postgres plus DBOS remains an independently evaluated candidate; DBOS orchestration is not itself a grant to replace Upper LC/TaskCycle.

**DoD for this candidate:** static security tests + new CI result + independent full changed-file IR 0F/0A before recommending source-only readiness. Physical phase still NO_GO pending separate safety gates. Product `mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88` remains authoritative.

## IR001 source repair limits and required native follow-up

- IR001 was terminal `NO_RECOMMEND` on prior HEAD `e55304d265b4c6fef9da3b314f7b0594dceb00c3`, 3 findings / 3 advisories. This subsequent repair does not rewrite or repeat that review.
- Mandatory `assert_synthetic_catalog` now rejects foreign user schemas, non-A02 relation footprint/ownership, public/custom functions, explicit column ACLs, foreign cluster roles/databases and extensions in the selected synthetic database. Remaining PostgreSQL global `PUBLIC` access (such as the otherwise empty `postgres` database) is outside this source-only guard: competent native Control must attest absence of foreign application data and effective grants before physical admission. **Do not describe the source guard as complete cluster ACL enforcement.**
- Effective role checks now explicitly include `rolinherit=false`, no direct memberships and no table/schema/database/function grant options. Native test must verify equivalent effective permissions across roles and default PUBLIC grants; source-only FakeConn does not prove catalog/role security.
- New source-only integration test intercepts `psycopg.connect` and exercises real `lan_probe.connect()` code, positive mock writer and witness paths, and fail-closed connection cleanup. No external PG connection occurs.
- Provisioning remains a separately conditioned, durable original effect. The privileged function `pg_control_system()` requires a dedicated least-power EXECUTE grant decision and real PG16 positive/negative verification; no other system function permissions or broad monitoring memberships may be silently granted. Original role-free fresh catalog and provisioning sequence must be reconciled before setup.
