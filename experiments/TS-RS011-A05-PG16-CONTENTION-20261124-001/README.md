# TS Remote State 011 — A05 PG16 one-host contention experiment

Status: **NONPRODUCT / ISOLATED / PENDING ORIGINAL CI**. Owner: TS_REMOTE_STATE_011. No Product authority or State Kernel replacement.

**What this is:** one disposable PostgreSQL 16 service container created by a dedicated GitHub Actions job; two *separate* `psql` client processes and PostgreSQL server backends on ONE GitHub-hosted runner. Writer A conditionally advances revision 0→1 while holding a PostgreSQL transaction for nine seconds; writer B enters concurrently and must be observed by a separate read-only client in `pg_stat_activity` with `wait_event_type=Lock`. After A commits, B must return 0/0/0 updated HEAD/events/receipts. Exact backend PIDs, wait classification, before/after counts and test-server version are emitted without passwords.

**What this does NOT prove:** physical two-host failover, real remote Neon vs PG16 parity, a genuine network-lost COMMIT ACK, P0 other-UID denial, P2 authenticated forbidden writes, A01 Developer grant/revocation consistency, Product acceptance, or any Orca→WSL child provenance. Its success may close only the narrow *single-host live PG16 contention* gap in A05; the higher-level A05 and Kernel gates remain OPEN.

## Isolation and controls

- `probe.py` refuses to connect without `GITHUB_ACTIONS=true`, `TS_RS011_EPHEMERAL=yes`, loopback `PGHOST=127.0.0.1`, port 5432, database/user `postgres`, exact disposable test password, and Python 3.15.2. No WSL, Tailscale, Neon, notebook, Product repo, network tunnel or source file writes.
- Runner creates only schema `rs011_a05` inside the disposable Actions service and does not request external credentials. Service lifetime is limited to this CI job. Different roles/hosts and real-time barrier remain future independent experiments.
- This is intentionally NOT an automatic replacement of earlier immutable Neon RACE-A/B results. Original historic sequential winner/loser and rollback receipts remain terminal; this is a new bounded experiment in a different disposable database.
- Source file blob must match exact pinned Git object in the workflow; no automatic fallback to paid providers or remote databases; job is `push` scoped to this dedicated isolated branch and one specific write-set. Previous PR63 source, TS EE PR77/78/79/81 and all Product sources are outside write-set.

## Original evidence and interpretation

Before running, record branch, HEAD/tree, event, workflow run ID/attempt and job ID. After the one native CI job, read original GitHub job/logs, classify PASS/FAILED/UNKNOWN, and never rerun blindly. Do not infer pass from a planned test. A source-only independent reviewer must inspect the exact SQL fixture, process orchestration, observed lock event and output for claims greater than source design.

Owner can repair a finding in a separate immutable candidate, never rewriting a terminal original. There is **no P0/P2 physical admission, Neon mutation or Product integration grant** from this file.

Product SOT immutable: `mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88`. Kernel final architectural disposition `NARROW/UNDECIDED`, migration `NO_GO`; Beta Run008 remains PAUSED.
