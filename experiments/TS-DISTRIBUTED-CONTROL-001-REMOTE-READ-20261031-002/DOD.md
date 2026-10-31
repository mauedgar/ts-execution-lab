# TS-DC044-002 — Prospective corrected read-only remote qualification

**Operation:** `TS-DISTRIBUTED-CONTROL-001-REMOTE-READ-20261031-002`. **Attempts:** `TS-DC044-REMOTE-READ-ALPHA-ATTEMPT-002`, `TS-DC044-REMOTE-READ-BETA-ATTEMPT-002`. **Authority:** EXPERIMENTAL_CONTROL_ONLY; Product NONE.

## Original 001 (terminal, preserved; never rerun)

[Run 41177181291](https://github.com/mauedgar/ts-execution-lab/actions/runs/41177181291): original source `e67c8bfa2d1e9059dd90fabf52ed549dbc721dcf`, two fresh runners completed `FAIL` due to original fixture asserting exact issue cardinality = 3. Both `bd bootstrap` succeeded and failed after `bd list --all`; no provider dispatch, DB push or Product effect. Live remote readback remained `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`. This was an overly restrictive assertion on a shared historical experimental ref that may have additional native records, not native remote restore failure. Original result is not reclassified PASS.

## Frozen distinct 002

- New isolated branch `experiment/distributed-control-001-remote-read-20261031-002`; source file `remote_read044.py` Git blob `d717bb625d177b48c8c0b0d6ebd497f3d0866ad4`.
- Native read-only hosted GitHub Dolt remote `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` as pinned **immutable original**, with `contents:read`, `BD_NO_PUSH=1`, and no mutating Beads CLI calls.
- Native Beads 1.3.1 ZIP SHA256 `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`. Two separate Ubuntu Actions hosts, one read-only `bd bootstrap` each.
- Corrected invariant: original three Beads 009 issue identities must all be present; additional historical experimental issues are permitted, but their ID/status projections must match exactly on both hosts against the same pinned remote ref. The original `SOURCE_REF` is verified, readback before/after each read must match pin. No Kernel used, no push or provider effect. Join validates original host receipts and reports.

## Terminal conditions and scope

Only a single branch-triggered workflow `run_attempt=1`. If current remote changes or both original host receipts differ: fail closed and do not retry. Output artifacts retain source/attempt/remote identity and hashes. PASS would qualify `TWO_HOST_NATIVE_GITHUB_DOLT_READ_ONLY`, not write authority, live multiwriter, privileged writer confinement, Product audit/TC parity, high availability or global Kernel removal. #35 and Product untouched.
