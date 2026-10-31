# TS-BEADS-047B — Terminal preparation qualification, live SQL deferred

Date: 2026-10-31. Experimental authority only; Product authority/effects NONE.
**Disposition:** `PASS_NATIVE_TWO_WINDOWS_PEER_CONNECTIVITY_AND_STATIC_PREFLIGHT_WITH_LIMITATIONS`. **Full host independence:** `INCOMPLETE`. **No live SQL/backup/UNKNOWN run launched.**

## Original reobserved machine and provider evidence
- Notebook connected to existing private Tailscale tailnet: native Windows client `Running/Online`, Dolt 2.2.0 and Beads 1.3.1 installed/pinned on Windows. Physical hardware separately identified as HP Pavilion Sleekbook 14 in earlier 047.
- Desktop connected to same tailnet: different Windows device, Tailscale `Running/Online`. Desktop Beads 1.3.1 installed via original WinGet call with package SHA checked and terminal result `Instalado correctamente`, no local database initialized.
- A distinct original `tailscale ping --c=1` was executed on each machine toward the verified other online peer. Each original returned `PING_OK` and `PEER_CHECK_TERMINAL`; no private IP or credentials published.
- 047A `TS-BEADS-047-NOTEBOOK-REMOTE-SQL-20261031-001` remains separate and not dispatched. Its original static 001/002 runs `41214259307`, `41215865528` stayed terminal, not retried.
- New 047B branch `experiment/beads-047b-native-two-windows-20261031-001` branched from exact 047A preparation commit `b9be864a498355d4d7d03e7fd6c65cb01b66081e`.
- Immutable 047B experimental DoD at `experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/DOD.md`, originally created at commit `7625ce5eca69aab92e31251196ca4af397f5efcf`.
- Native read-only preflight `native-host-preflight.ps1` frozen Git blob `af0969d7b42cff53f20cbbded376f99aa50dce8e`, source commit `eed57c4f22c95b6a5c25e0dd6b22c58d43e3da84`. This script is already published on GitHub, but has **not** been materialized on either computer or run there.
- Separate original CI static validation: GitHub Actions run `https://github.com/mauedgar/ts-execution-lab/actions/runs/41218243068`, commit `a2d29a041f585a703e676e7f2177ae9b86b1acdd`, `run_attempt=1`, `completed/success`, original job `124587188506` `completed/success`. PowerShell parser, exact Git blob and no-effect/source boundary checked. This does **not** prove runtime SQL connectivity, Windows service start, user-permission enforcement or native Beads graph.
- Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` reobserved before branch creation. No Product integration or Kernel removal.
- Prior terminal 045 (single host SQL) `41177022889`, 046 (cross-host cold restore) `41210661485`, DC044 read-only Git Dolt `41177310449` preserved. Existing shared experimental `refs/dolt/data=1f72d68797114170a97fee27641858f2e55a4571` unchanged at last observation.

## Architectural disposition
The two **already-connected physical Windows machines** permit an experimental Dolt server and client topology without provisioning Tailscale OAuth, an ephemeral GitHub Actions runner tag or user-created GitHub Secrets. No additional cloud hosting subscription is necessary. This does NOT waive strong SQL credentials, private transport, least-privilege roles, nor off-host backup.

The notebook is the only proposed Dolt primary. The desktop is the first independent native Beads client and a future off-host native backup destination, **not** a second writable primary. A disconnected primary causes fail-closed writes until fenced and correctly restored. The original 047A GitHub workflow retains its missing sentinel and cannot launch from this branch's work.

## Operational remaining dependency
- Materialize and integrity-verify 047B execution artifacts through normal Git/repository surfaces on both Windows hosts before a bounded Commander execution. Commander must not fetch/materialize scripts, ZIP/patch/JSON or be used for semantic repository browsing.
- Host security preconditions must be qualified and native SQL service provisioned in an isolated fresh directory on notebook with root hardened before private Tailscale Serve. Provide separate scoped writer/reader credentials without putting them in command traces or chat.
- Native Beads clients must prove fresh remote `bd init --server --database ts047b_beads` and serializable concurrent graph updates; verify negative SQL/Beads ACL behavior. No SQL listener, Tailscale Serve proxy or real Beads issues were created by this preparation.
- Restore from **native off-host** backup remains unproven in 047B. No automatic promotion, no blind re-dispatch of possible `UNKNOWN` effect, no stale snapshot acceptance. Measure real RPO/RTO in a distinct bounded recovery gate.
- TinyFish installation confirmed enabled by Plugin Directory, but no callable TinyFish browser tools were exposed to this chat's tool surface; browser integration is OPTIONAL because two known devices already connect privately.

**Status:** `047B_READY_FOR_SECURE_HOST_PROVISIONING; HOST_INDEPENDENCE_INCOMPLETE`. Earlier 047A state untouched. No need for the user to enter the Tailscale OAuth admin interface for this new topology.
