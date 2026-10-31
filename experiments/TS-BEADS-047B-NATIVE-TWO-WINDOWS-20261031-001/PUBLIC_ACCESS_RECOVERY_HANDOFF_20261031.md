# TS-BEADS — 047B OPERATIONAL — Recovery carrier (public-safe projection)

**Date:** 2026-10-31. **Class:** NONCANONICAL_EXPERIMENTAL_HANDOFF_ACCESS_RECOVERY. **Recipient:** fresh chat TS-BEADS / TS Execution Engineering, OPERATIONAL. **Authority:** EXPERIMENTAL_CONTROL_ONLY. **Product effects:** NONE. **Status:** ACCESS_RECOVERED_BY_PUBLIC_NONSECRET_PROJECTION; **original private handoff is not republished**.

## Why this projection exists

A new TS-BEADS chat reported `BLOCKED_EVIDENCE_ACQUISITION` / HTTP 404 for the original private repository path. The source chat verified **via its connected GitHub plugin** that the immutable original exists:
- `mauedgar/ts-execution-transport@eb6a64ffcd7713a0df5b31650cc9dcd013052026:handoffs/TS-BEADS-047B-ROTATION-INTEGRAL-OPERATIONAL-20261031-001/HANDOFF.md`
- Original Git blob: `d799da0b01b74000a1b6c3f24851bc5b093431ac`, 12,713 JavaScript UTF-16 characters, commit `eb6a64ffcd7713a0df5b31650cc9dcd013052026`.
- `mauedgar/ts-execution-transport` is **PRIVATE**; HTTP 404 may be an authorization artifact when a chat uses an unauthenticated web fetch or different app grants. Do not interpret the failed HTTP fetch as evidence that the original source is absent.
- **This file is a separately scoped fallback, NOT a byte-exact copy** of that private handoff. It contains only public lab/state references and no Tailscale IPs, machine UUIDs, SQL passwords, OAuth values, unpublished receipts, or other private transport data. Do not treat it as authoritative Product SOT.

## Competent public evidence and cutoff

- Existing experimental branch at fallback creation: `mauedgar/ts-execution-lab:experiment/beads-047b-native-two-windows-20261031-001@9aa4994ae037fa50b03fb7be0e466792a063734f`, tree `72d5253fa848575af24adbd1fd3fc64e20b37429`.
- **047B DoD:** `experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.
- **047B terminal preparation result:** `experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/PREPARED_STATIC_TERMINAL_RESULT.md`, blob `9ffb4f35ea4a51c5d5e15c17d34d723a1a5dbc1b`.
- **047B native Windows read-only preflight source:** `experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/native-host-preflight.ps1`, Git blob `af0969d7b42cff53f20cbbded376f99aa50dce8e`, source commit `eed57c4f22c95b6a5c25e0dd6b22c58d43e3da84`. **Not yet materialized on either machine or executed**, at last observation.
- **047B static validation:** GitHub Actions run `41218243068`, subject `a2d29a041f585a703e676e7f2177ae9b86b1acdd`, run_attempt `1`, `completed/success`, job `124587188506`. Validates PowerShell parser/hash/no-side-effect static boundary, not live SQL.
- **047A prior (separate):** `mauedgar/ts-execution-lab:experiment/beads-047-notebook-remote-sql-20261031-001@b9be864a498355d4d7d03e7fd6c65cb01b66081e`; static runs `41214259307` and `41215865528` both terminal success attempt 1. **No 047A live SQL attempt dispatched; no one-shot sentinel created**. Do not run 047A automatically.
- **Product SOT read-only cutoff:** `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, tree `e6be65e0c3d9aca074218b2fff92e6d42fc76141`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`. Reobserve current SOT before any state-dependent Product statement; **no Product grant**.
- Existing experimental native Dolt Git ref `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`: immutable boundary; never overwrite with 047B.
- Execution Engineering contract: `mauedgar/ts-execution-lab:main@e6562d5d4289978c28623927877cc8e1d0c74530:docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md` Git blob `3f6b7bfa40e4d4199e3d12734d3ce2e4e76989f1`.

## Non-replay terminal evidence

- 028 and 030 retained original negative privileged-writer bypass / conservative UNKNOWN divergence; historical experiment matrix `reports/TS-BEADS-INTEGRAL-CAPABILITY-20261031-001.md` at `mauedgar/ts-execution-lab@a72af763c22d1cf61c6e0485565b90b884879bed`, blob `89bf2e16e54e2410b744c25ef4196832ebf84247`. 036–041 results are in that matrix; no new run required.
- 042 terminal: run `41174844096` PASS (single-host parallel native Beads/Kernel-free workflow), original report `ts-execution-lab@7b0fb033e9aa9a1e3d140622209ed427d77b1f12:experiments/TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md`.
- 045 terminal: original failed 001 `41176871863`, corrected separate attempt 002 run `41177022889` PASS server-mode 24/24 *single host*; report `ts-execution-lab@ac9012e56233024efc6135b8363fd794fdae7176:experiments/TS-BEADS-045-SERVER-BOUNDARY-20261031-002/EXPERIMENTAL_TERMINAL_RESULT.md`.
- 046 terminal: run `41210661485` PASS 43/43 (A+B) native Dolt cold backup across two GitHub hosts; **NOT** live SQL, forced crash, real in-flight external provider UNKNOWN, or permanent backup. Report `ts-execution-lab@d1e825df95b5a76618b1651d58adba9a4fbdcbfb:experiments/TS-BEADS-046-NATIVE-BACKUP-FAILOVER-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md`.
- DC044 separate distributed-control read-only experiment: run `41177310449` PASS only read-only multi-host Dolt remote. Do not conflate DC044 with any unqualified TS-BEADS 044 report.
- These original runs were reobserved `completed/success`, run_attempt `1`, at rotation, except 045 failed historical 001 preserved as failure. No retries, no silent reclassification of original evidence.

## 047B physical topology and current boundary

- Independent Windows **notebook** (Dolt SQL v2.2.0 + Beads v1.3.1) and **desktop** (Beads v1.3.1) were both observed Tailscale `Running/Online`, with successful native Tailscale peer ping **in each direction**; no exposed node addresses here.
- New 047B native local topology avoids *Tailscale OAuth*, GitHub Actions repo Secrets or paid cloud hosting: notebook sole Dolt SQL primary, loopback `127.0.0.1:3307` serving isolated lab database `ts047b_beads`; private Tailscale Serve TCP ingress for desktop; desktop Beads native SQL client with runtime environment credentials and endpoint. Endpoints are runtime configuration, no provider-specific architecture or Kernel replacement.
- At last verified cutoff **NO** Dolt SQL service/listener, database, SQL users, Tailscale Serve port forwarding, real Beads graph, physical disconnect, off-host backup, RPO/RTO validation or provider UNKNOWN provider-effect experiment was executed for 047B. **No 047B live ExecutionAttempt exists**. Source publication and CI static PASS do not authorize claiming live functionality.
- **Nearest step:** verify no new 047B attempts/effects and host identities, materialize the exact frozen preflight and any security runner through normal Git/repository surfaces on each computer, verify hashes/parser/integrity/preconditions, then use Commander **only for already-determined bounded execution and compact results**. No Commander repository exploration, source reading, materializing scripts, interactive editing or polling. If artifacts missing, stop and report exactly what's absent.
- Secure provisioning before network: fresh separate lab dir, root SQL password hardened, least-privilege writer and read-only SQL account, deny invalid credentials; only then activate **private** Tailscale Serve, NEVER Funnel, open internet SQL, router port forwarding, raw `0.0.0.0` listener or unprotected SQL. No secret printed in Git/ChatGPT/Commander log.
- Then 047B empirical scope: authentic native dependency graph and two independent Windows Beads clients against one SQL primary; role-owned original receipts, negative SQL/Beads ACLs, host A client interruption, host SQL outage fail-closed and recovery with original identity, concurrency conflicts, **native off-host Dolt backup/restore**, actual provider UNKNOWN witness reconciliation with zero blind retries, and net code removal measurement. Backup on desktop must not be promoted automatically to a second writable SQL primary. Reconcile original effect and fence old SQL primary before any restore-as-writer.
- Product migration/deletion of State Kernel, integration with #35, Attendance, TaskCycle Core, FitFlow, acceptance, Phase2 are **NOT AUTHORIZED**. Existing potential source footprint 85,014 B (Kernel + adapter + reconcile recipe) is a candidate inventory, **not measured net reduction**; Product bytes removed 0.
- **Global experimental verdict:** `HOST_INDEPENDENCE_INCOMPLETE`. **Technical current gate:** `047B_READY_FOR_SECURE_HOST_PROVISIONING` (no SQL attempt). Preserve both labels until original live evidence establishes otherwise.

## Resume instruction for recipient

Fetch this public-safe projection first if the private handoff's HTTP URL returns 404; it is a **lower-authority access fallback**, not a replacement for private source. Attempt private handoff via the *connected GitHub plugin* with exact `fetch_file(repository_full_name="mauedgar/ts-execution-transport",ref="eb6a64ffcd7713a0df5b31650cc9dcd013052026",path="handoffs/TS-BEADS-047B-ROTATION-INTEGRAL-OPERATIONAL-20261031-001/HANDOFF.md")`; never assume a web 404 means Git object absent. If missing details from the private original materially affect authority, secrets, host identity or effects, keep the corresponding operation BLOCKED rather than reconstructing it from Memory.

**No automatic execution, no automatic Product effect, no new TaskCycle.**
