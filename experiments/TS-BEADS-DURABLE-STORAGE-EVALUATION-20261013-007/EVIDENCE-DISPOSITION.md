# TS — Beads durable store evaluation 007/008
Date: 2026-10-13
Classification: NONPRODUCT EXPERIMENTAL EVIDENCE / ADOPTION NOT DECIDED
Research authority: evaluation and synthetic experiments only. Product effects: NONE.

## Decision question

Can we use upstream Beads + Dolt + ordinary Git/Actions/local to own operational obligations, blocked work and recovery, replacing internal non-authoritative tracking and reducing TS-specific code, while keeping Tecnotron Product invariants and protecting against duplicate/unknown effects?

**Disposition: CONTINUE_RESEARCH_WITH_NATIVE_GIT_REMOTE_PRIORITY.** Not a Product grant, implementation, or replacement order.

### Competent Product reference observed (read-only)

- `mauedgar/tecnotron-ai:tools@2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89`, `docs/SOURCE_OF_TRUTH.md`, `docs/architecture-knowledge-ownership-baseline.md`, `docs/current-state.md`, `docs/operational-architecture.md` (fresh observations during this evaluation).
- Product retains authority, TaskCycle/Upper LC selection, Developer grants, IR, acceptance, Phase 2, exact Git subjects, `NONE/CONFIRMED/UNKNOWN` effect reconciliation, no blind retry, canonical repo truth. Beads `ready`/`claim`/`gate` **do not** grant those effects.

## Empirical case 007: full native backup persisted in ordinary Git history

1. **Source producer**: GitHub Actions [run 38484553116](https://github.com/mauedgar/ts-execution-lab/actions/runs/38484553116), workflow commit `02f30a7f98fcdf60e86859a8cb6b80146c2d8215`, terminal SUCCESS. Fresh synthetic Beads v1.3.1 embedded database with original A, dependency B, blocked A continuation, independent C; full native Dolt `bd backup sync` (three files + manifest with per-file SHA256). Published via normal, nonforced `git push` to isolated **experiment-only storage branch** `experiment/beads-git-store-20261013-007`. Immutable original data commit `090d59190f48e42f90e7811ee93a48341b83b1c1`.
2. **Independent Git recovery**: [run 38484656695](https://github.com/mauedgar/ts-execution-lab/actions/runs/38484656695), workflow commit `a33b5c0785a2bf25263b927b203b20648bf32d41`, terminal SUCCESS. Pinned checkout of the above immutable Git commit, verified native three-file backup hashes and source identity, restored in a *new Actions runner*, confirmed four original records and dependency/continuation state, then resumed synthetically. Provider `TS_GIT_NATIVE_BACKUP_PINNED=...;native_filecount=3`, `TS_CROSSRUN_CONSUME=PASS;...;records=4`. **No timed Actions artifact required as the source**.
3. **Competing writer experiment**: [run 38484908944](https://github.com/mauedgar/ts-execution-lab/actions/runs/38484908944), workflow commit `66f255b283f06abc6f3f52eec61f542f5d653978`, terminal SUCCESS at workflow level with distinct child dispositions:
   - Writer A, job `115596091265`: original snapshot `090d5919…`, modified one synthetic issue `ts-execution-lab-6d0a55aa`, committed full native backup and **published** immutable candidate `bca6155824edc0c44f207d218337ef3c8e23f43d`, `PUBLISHED_CONFIRMED`, push exit 0.
   - Writer B, job `115596090987`: same original snapshot, attempted different issue `ts-execution-lab-6d0b66bb`; local candidate `6ae973de750a42d99593034ced91a40423664c81` **NOT published**; remote rejected stale ref with `cannot lock ref ... is at bca615... but expected 090d591...`. Terminal `CONFLICT_NOT_PUBLISHED`, push exit 1.
   - Both matrix jobs finished 'success' as **experiment findings**. This MUST NOT be read as acceptance or publication of writer B. No force-push or blind retry.
   - Original attempt receipts retained as [writer A artifact 11859730045](https://github.com/mauedgar/ts-execution-lab/actions/runs/38484908944/artifacts/11859730045), [writer B artifact 11859076363](https://github.com/mauedgar/ts-execution-lab/actions/runs/38484908944/artifacts/11859076363). Artifacts expire approximately 2026-10-20; evidence here is portable text, **not** permanent preservation of the losing binary candidate.
4. **Conditional reconciliation by exact original identity**: [run 38485071554](https://github.com/mauedgar/ts-execution-lab/actions/runs/38485071554), commit `c995b15ffb4eecd40c635911dd915e795e106d10`, terminal SUCCESS, verified original rejected B receipt (artifact ID, digest, exact candidate, source marker, remote after A) and restored exact committed A winner state. **Checked that B was absent** before creating one record with B's original ID/source. Published a new full native backup via nonforced Git push. New immutable store commit: `f9c6111f749af3ca9afed158cd32d9d7031e4108`. Original log `TS_GIT_RECONCILIATION=PASS;...;issues=6`. No replay of original B Git push; this is a new, separately identified reconciled attempt.
5. **Independent third-run audit**: [run 38485193703](https://github.com/mauedgar/ts-execution-lab/actions/runs/38485193703), commit `74e7335a162e4f510ac86a7a947e8ca8b210de81`, terminal SUCCESS. Fresh Windows runner checked immutable final Git commit `f9c6111f...`, verified the complete backup file SHA256 inventory, restored with `bd backup restore --force`, read exact **six original and reconciled Beads IDs** once each, and verified original writer A/B SOURCE_REF descriptions. `TS_GIT_RECONCILED_INDEPENDENT_AUDIT=PASS;...;total=6;writer_a=1;writer_b=1;native_backup_sha_verified=YES`.

**Observations:** Git ordinary branch CAS/non-fast-forward prevents destructive overwrite, and exact original source identity permits controlled later reconciliation. **Limits:** this Git snapshot publisher was experiment-specific; it is **not adopted** as a new TS publisher or state authority. The losing candidate commit was not remote-persisted, and its original receipt artifact has limited retention. Real obligations need an independently durable originating handoff/source to recreate them safely. No resilience proof for crash after remote push but before local terminal receipt, branch deletion, malicious mutation, multi-org auth, large-store scale or automatic cross-chat wakeup.

## Empirical case 008: Beads' native Dolt-backed Git remote

Isolated **ephemeral bare Git remote within Actions**, NOT a persistent GitHub Dolt ref and NOT Product.

- Attempt [38485366895](https://github.com/mauedgar/ts-execution-lab/actions/runs/38485366895), commit `50cd6c02114308b2769f163be3d7bb51120d6a94`: terminal FAIL before issue creation due to Beads auto-prefix `producer-` disagreeing with specified test ID. No remote Dolt data publication.
- Attempt [38485417827](https://github.com/mauedgar/ts-execution-lab/actions/runs/38485417827), commit `2b940f4d7530a71fc99c3b78c2cc4e3a4291c653`: terminal FAIL on **fresh bootstrap**. Beads native `bd dolt remote add pilotgit git+file:///D:/...`, `bd dolt push --remote pilotgit` and `refs/dolt/data` publication **passed**; fresh Git clone used raw Windows local remote path parsed as `git+D:\...`, unsuitable for Dolt `bootstrap`. Exact published ephemeral ref `4d1c802305fe28ca6dc2565ed26fcbef20017d48`.
- Attempt [38485480692](https://github.com/mauedgar/ts-execution-lab/actions/runs/38485480692), commit `349da7eb988f0f711bc94a447a22792e15f321b0`: terminal **SUCCESS**. Explicit `file:///D:/...` remote binding on cloned checkout. Native `bd dolt push` published `refs/dolt/data` commit `315247154be38bb2f4cb03a044bf22d8887d60c0`; newly cloned Git checkout successfully `bd bootstrap`-recovered exact synthetic issue `producer-8a5a55aa`, `TS_BEADS_NATIVE_GIT_REMOTE=PASS_PUSH_REF_AND_FRESH_BOOTSTRAP`.

**Important:** this tests native Beads–Dolt Git transport and fresh bootstrap **without a bespoke binary snapshot publisher**, using a disposable local bare Git server in an Actions runner. GitHub-hosted remote credentials, actual remote GitHub ref behavior and concurrent native `dolt push/pull` conflict remain **UNTESTED**; the ephemeral bare repository was deleted with its runner after the test. Native upstream Dolt supports `git+https` / `git+ssh` and configurable `refs/dolt/data`; never infer qualification of a specific GitHub credential binding from documentation or this file remote test.

## Current evidence-based comparison

| Candidate operational continuity binding | Persistence / portability | Parallel writers | Empirical disposition | Expected ownership cost / caveat |
|---|---|---|---|---|
| Local embedded Dolt / Beads | Local disk cross-process (Pilots 001/002/004) | Embedded single writer | PASS locally for sequential tasks | Lowest initial dependence; host availability and off-host transport needed |
| Actions artifacts + native `bd backup` | Cross-run restoring while artifact retained (Pilot 006) | Not a shared datastore | PASS with verified hash/run / seven-day retention | Suitable evidence carrier, **not** permanent inbox |
| Actions + full Dolt backup committed to ordinary Git branch | Durable Git commits accessible from independent runners | CAS guard prevents stale writes, manual conflict reconciliation required | PASS producer/restore, conflict, reconcile and final audit (007) | **Adds experiment-specific snapshot transport code**; candidate only, avoid making it a default adapter |
| Beads/Dolt **native Git remote** `refs/dolt/data` | Full Dolt sync via Git, native fresh bootstrap | Needs independent concurrent remote push qualification | PASS on disposable bare Git; NOT QUALIFIED on persistent GitHub remote (008) | **Promising lowest custom-code option**; Git auth, ref ownership, version compatibility and recovery must be pinned |
| Dedicated durable Dolt server / DoltHub | Persistent shared backend when separately hosted/qualified | Server-mode simultaneous writes observed in *ephemeral Actions* in earlier trials | Hosting + security + recovery + cost not qualified | Extra always-available service credentials/ops, not justified as default yet |
| GitHub Issues / Projects | Durable centralized Product planning projection | Native provider concurrency/version semantics | Already used for Product backlog; no equivalent TaskCycle authority transfer | Must avoid duplicate operational authority, GitHub Projects not required as a Beads graph mirror |

**Actions and local are both valid execution surfaces** when bound and available. Separately choose the store's persistence owner. A successful Actions run is not itself a durable shared Beads inbox. Native Beads `ready/claim` does not select/authorize a Product TaskCycle or permit effects.

## Experimental DoD remaining before any canonical adoption decision

- [x] Local sequential persistence, exact provenance linking, blocked continuation recovery (001/002/004).
- [x] Hosted Windows Dolt server concurrency, deterministic ID collision, atomically claimed work (003/005).
- [x] Formula compile/pour, dependency fanout/fanin, synthetic gate (005); ad hoc `bd ready --mol` difference still requires poured-molecule inspection.
- [x] Native Dolt backup cross-run recovery through temporary artifact (006).
- [x] Durable full native backup via ordinary Git; optimistic conflict; original identity reconciliation; independent six-item readback (007).
- [x] Native Git remote `bd dolt push` + `bd bootstrap` on isolated bare Git (008).
- [ ] Qualify **real GitHub-backed native Dolt ref** on dedicated experimental scope with qualified authentication, exact ref identity and no shared Product write.
- [ ] Test competing native Dolt `push/pull` and source-ref idempotency/claim leases, including `UNKNOWN` after interrupted publish; no blind automatic replays.
- [ ] Evaluate availability/fallback, Git history/remote backup recovery, authorization boundaries, privacy, read/write scopes, credential handling, maintenance/upgrades, artifact/retention cost, and throughput for expected workload.
- [ ] Compare exact current Tecnotron operational consumers against Beads native features, proposed components to *remove* and necessary bridge, then competent Product Control chooses adoption/no adoption. State Kernel `NONE/CONFIRMED/UNKNOWN` and TaskCycle authority remain protected unless separately proven equivalent.
- [ ] Validate actual durable **real handoff** across independent chats/surfaces without injecting it into an active TaskCycle and without automatically creating Product work.

**Recommendation for the next research pass:** first prioritize a **native Git remote** binding, not expanding the snapshot adapter. Retain ordinary Git snapshot tests as a known-safe reference/fallback. Avoid any physical migration, MCP installation or new always-on Dolt server until empirically needed.
