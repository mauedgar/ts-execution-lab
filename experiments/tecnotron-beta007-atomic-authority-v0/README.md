# TS Beta007 — Atomic Authority / Effect V0

**Classification:** isolated NONPRODUCT experiment. **Authority: NONE. Product effect: NONE.**

## Responsibility and boundary

Beta Run 007 owns its PR67 source-custody candidate; the remote-state Kernel retirement owner retains independent authority. This experiment changes neither write-set. The canonical Tecnotron SOT says State Kernel disposition is UNDECIDED and does not authorize SQLite adoption, Kernel migration, shutdown or new Product authority.

IR011/IR012 found an actual A01 cross-service race: GitHub current Developer-grant verification and filesystem rename cannot form one atomic transaction. The experiment investigates only this hypothesis: **if** current grant status and the authoritative effect record share ONE serialized transactional store, then revocation and effect commit can be linearly ordered. An external filesystem view becomes a rebuildable projection, not the authoritative effect.

## Frozen invariants under test

- Immutable grant/subject/attempt/payload-digest identities, with refusal of conflicting replays.
- PREPARED attempt before any effect; SQLite BEGIN IMMEDIATE + COMMIT serializes authority check, effect insertion, attempt CONFIRMED and audit event. Revocation acquires the SAME write lock.
- Revocation first => BLOCKED / NONE. Commit first => CONFIRMED once even when subsequently revoked. Read reconciliation uses a consistent SQLite snapshot and rejects nested/reentrant access.
- Real process death before COMMIT rolls back to PREPARED/NONE; real process death after COMMIT leaves CONFIRMED durable and reconciles by SAME attempt ID without repeating effect.
- Projection is derived create-only output of a committed row, using Linux/POSIX directory-descriptor anchored open/link/unlink, symlink/inode safeguards, **a single SQLite read snapshot**, and a required trusted parent. Both link creation and staged-file removal fsync their directory. Interrupted staging can be recovered idempotently; a tampered external file is rejected, not overwritten.
- No caller-supplied callback is executed inside `commit_effect`. Concurrency tests instrument their test-owned SQLite connection only. GitHub Product grants, H6 Phase2, original denied Domain effects, PR67, tools and Kernel remain untouched.

## Empirical original tests

Run from this directory using the Python standard library only:

    python3 -m unittest -v test_transactional_authority.py

Current exact candidate: GitHub Actions Ubuntu 24.04 Python 3.12.3 original run [#42161967536](https://github.com/mauedgar/ts-execution-lab/actions/runs/42161967536), attempt 1: **16 PASS / 0 FAIL**. Previous local Python 3.13.5 execution passed 14/14 tests on the earlier candidate, but does not qualify this new 16-test candidate locally. The GitHub Linux pull_request workflow records the host Python version. This does NOT claim Python 3.15.2 compatibility or cross-platform qualification.

## Limits that CANNOT be suppressed by the experiment

1. **GitHub authority is independent today.** A copy of GitHub comments in SQLite can be stale. Closing A01 would require a competent Product choice of a single authority/effect serialization point, including off-host Developer revoke semantics. This project does NOT make that choice.
2. **External projection is not atomically committed.** A projection of an earlier CONFIRMED effect can materialize after revoke; the authorization was at the DB commit time. If the filesystem publication itself remains the authoritative Product effect, the original race persists.
3. **SQLite host trust is bounded.** No tests cover hostile same-UID/root actors, NFS, multi-host distributed DB, real power loss or external side-effect exactly-once semantics.
4. **No implicit migration.** This is not Beads, Dolt, a new Product scheduler, a TaskCycle owner, a GitHub-to-DB authority mirror, or a replacement for the remote-state Kernel retirement control.
5. **Proof is not adoption.** Independent security review, original native run evidence, an explicit Developer architecture decision and integration ownership would be required before any Product modification.

## Next competent gate

Preserve a fresh original review on exact code and provider runs, then hand evidence to the remote-state/Kernel retirement control. No adoption, merge into Tecnotron, H6 effect replay or automatic 0F/0A claim.

Status: EXPERIMENT_ONLY / NOT_PRODUCT_ACCEPTED.
