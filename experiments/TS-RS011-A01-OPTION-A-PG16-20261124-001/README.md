# RS011 A01 Option A — disposable PostgreSQL authorization serialization

Developer gate: NONPRODUCT prototype authorized 2026-11-24. Exact grant: mauedgar/ts-execution-transport@397275505fb74eb289bf4c54061b9ecb588df3a5:requests/TS-RS011-A01-OPTION-A-PG16-20261124-001/REQUEST.md. No Product authority transfer, no actual GitHub approval, no Neon or notebook connection, no Upper LC / TaskCycle Core changes. Product filesystem Kernel remains authoritative; migration NO_GO.

## Model and linearization

Each synthetic scope has one grant and one allowed effect. A grant has exact version, active status, expiry and JSONB subject including repo, branch, tree, TaskCycle, Operation, attempt and effect subject. Synthetic authority role alone may revoke, writer alone may invoke apply, observer has only SELECT on the fixture tables. Owner/admin is a trusted test harness, not a Product identity provider. Fixed SECURITY DEFINER search path, no public execute. The revoker and writer use the same row lock held until transaction end. Effective revocation means committed revocation, not a cached or external approval change. If revocation commits first, the stale writer must be denied; if writer acquires the lock first and commits, revocation must wait. Expiry is checked during locked admission, not promised valid through wall-clock commit. This prototype neither authenticates real Developer decisions nor defines authority bootstrapping, regrant, multi-effect scope, migration or versioned policy.

The effect transaction changes the synthetic head, event and immutable receipt atomically. Same scope with different mutation id or payload returns conflict. The original receipt is the read-only reconciliation source. No replay after UNKNOWN.

## Tests and scope ceiling

- N01: both commit orders, independently bound backend PIDs, explicit READ COMMITTED, exact pg_blocking_pids relationship observed before committing lock owner.
- N02: stale positive cached grant denied after effective committed revocation.
- N03: all seven synthetic identity fields independently altered, wrong version and expired grant, forbidden direct mutation and role-crossed calls.
- N04: original committed mutation followed by distinct malicious request with same ID/changed payload; no second effect.
- N05: real grant row lock timeout SQLSTATE 55P03 and rollback/readback; not total authority service outage.
- N06: controlled real two-session blocking relationship in one host; two physical hosts NOT_TESTED.
- N07: local TCP proxy receives genuine PostgreSQL CommandComplete(COMMIT) and intentionally disconnects client before forwarding it. Expected client failure, original receipt read-only proves CONFIRMED from UNKNOWN, no mutation replay. Only local controlled network fault; not remote Neon failure or host outage.
- N08: revoke within transaction then rollback; observe still active, commit revocation using a separate connection, reconnect writer denied. Server restart, distributed failover and durability NOT_TESTED.

One original GitHub Actions run, disposable PG16.15 service, Python3.15.2, no persistent DB. Read source/CI original and review independently; narrow PASS is not A01 Product acceptance or full distributed A05. Do not rerun a terminal attempt or automatically merge.
