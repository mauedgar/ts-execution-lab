# TS-DC044 — Prospectively frozen read-only native GitHub remote test

Experiment `TS-DISTRIBUTED-CONTROL-001-REMOTE-READ-20261031-001` / authority `EXPERIMENTAL_CONTROL_ONLY`, `Product NONE`.

Exact native subject `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, pre-observed. Shared ref is **READ ONLY**: do not push, amend, delete, merge, bootstrap into it, or perform any native mutating command against it. All data are historical synthetic Beads 009. Original provider attempts are terminal and must never be redispatched.

Frozen script `remote_read044.py` Git blob to be verified before running; native Beads 1.3.1 Linux `sha256=3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`. No new SQL/Dolt server, scheduler, ledger, or Kernel. Two GitHub Actions Ubuntu runners are separate native execution hosts, with `contents:read` and no retained checkout credentials. One script invocation per host, independent source directories.

## Expected tests

1. Pin remote `refs/dolt/data` before/after each client and fail closed on drift or missing reference.
2. Fresh Git clone of the original Beads 009 experimental branch with **no .beads directory**; native `bd bootstrap` from remote; exact 3 original IDs and original `SOURCE_REF` recovered.
3. Host Alpha and Host Beta execute on separate runners in parallel, both independently recover same graph without any shared local folder, Product State Kernel, provider redispatch, or push.
4. Independent join compares original `RESULT044_ALPHA.json` and `RESULT044_BETA.json`, exact shared remote ID/status and source origin, verifies zero Product/remote writes and preserves original receipts/hashes.
5. No retry of terminal historical 009 or DC043/Beads 042/045; no integration, Product TC init, migration, #35 or new authority.

PASS limit: native remote hosted GitHub read-only hydration on two independent runners. It is **not** a remote write or multiwriter consistency test, not privileged writer fencing, not production backups, not TC Core parity, and does not establish authoritative State Kernel retirement. Derived cost comparison must cite Beads 029/030 rather than assume savings.