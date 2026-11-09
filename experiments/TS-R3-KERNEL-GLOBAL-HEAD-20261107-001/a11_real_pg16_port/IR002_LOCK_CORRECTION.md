# A11 — Lock contention experiment corrected for durable PostgreSQL transactions

Class: NONPRODUCT experiment, TS_EXECUTION_ENGINEERING, no Product change/Neon credentials/remote hosts.

Original local IR002 0F/2A asked for (1) exact deterministic mutation-ID collision rejection and (2) proven positive Postgres lock overlap. Collision's exact code is already tested by a dedicated native candidate. First lock candidate native GHA42553602037 attempt1 FAILED during lock probe. Separate frozen diagnostic GHA42553999371 attempt1 FAILED with bounded code A11_LOCK_STAGE_APPLY_A_NESTED_STORAGEREJECTED. Inspection of the unchanged real bridge.py reveals an intentional precondition _require_conn(transaction_status==IDLE): calling bridge.apply within an outer transaction would create a SAVEPOINT, and might falsely report COMMIT durability. DO NOT weaken that bridge invariant. Earlier diagnostic branch HEAD c955b06ce82f469384d4b13258a43d255fea66ad terminal; other automatic runs42553815446 and42553836950 both failed exact blob preflight before SQL. No blind reruns.

This corrected candidate uses FOUR independent PostgreSQL16 backends on ONE disposable runner:
- connection H holds SELECT HEAD FOR UPDATE inside a temporary outer transaction but performs **no Product/bridge mutation**;
- original JS V0 independently creates two different proposed events from the same revision5 using A10's qualified semantic adapter;
- real writer A and real writer B each start from an IDLE psycopg3 connection and invoke the same unmodified real bridge.apply as a top-level durable transaction (never nested);
- an independent observer checks both PostgreSQL backends show wait_event_type=Lock and pg_blocking_pids during simultaneous wait while H holds the row lock;
- H releases without writing, A/B race and exactly ONE gets CONFIRMED and ONE gets NONE_STALE; resulting durable revision6/HEAD1/events6/receipts6, no unintended retry;
- guard cleanup allows only the six exact disposable events and drops schema with RESTRICT after full object inventory.

No physical two-host concurrency, remote Neon, TLS authentication, Product integration, real TCP reply loss or distributed epoch is claimed. All prior terminal native executions remain separate. After exact source freeze, dispatch ONE new native workflow on an isolated branch, then independent read-only IR003, without a review PASS automatically granting Product acceptance.
