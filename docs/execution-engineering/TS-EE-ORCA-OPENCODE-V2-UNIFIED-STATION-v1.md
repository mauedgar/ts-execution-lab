# TS EE — Orca + OpenCode V2 unified station method v1

status: NONPRODUCT_STATION_METHOD_OPERATIONAL_BOUNDED
authority: TS_EXECUTION_ENGINEERING_NONPRODUCT_ONLY
Product_authority: NONE
Product_effect: NONE
date: 2026-11-20
scope: original authorized Windows notebook + Ubuntu-24.04 WSL; provider-native CLI management
original_validation: native Orca terminal + Windows and Linux CLI version readbacks
Independent_Review: NOT_RUN
Product_adoption: NONE

## Outcome: one package per operating system

**Canonical agent/CLI identity: OpenCode V2, CLI command `opencode`.** The term "OpenCode2" in existing TS/Developer launch requests names the v2 agent family, not permission to select an old independent executable or to bypass Orca. Preserve the 2026-11-13 Developer ruling in `ORCA-DEVELOPER-UX-v1.md` §7.1: any *new local semantic* OpenCode invocation MUST originate in a visible, Orca-owned Windows or native WSL terminal attached to the exact authorized host/worktree and attempt. Commander is mechanical preflight/transport only; it does NOT launch semantic inference.

| Platform | Single canonical package / binary | New launches |
|---|---|---|
| Windows | npm global `@opencode/cli`, currently v2.3.2 under fnm Node 24.21.0 | `opencode` through a Windows Orca-owned terminal |
| Ubuntu-24.04 WSL `tsops` | npm global at stable user prefix `/home/tsops/.local/opt/opencode-managed`, currently v2.3.2, native Linux Node 22.23.3 / npm 10.9.9 | `/home/tsops/.local/bin/opencode` through a native WSL Orca-owned terminal |

Compatibility-only: `opencode2` on Windows resolves to the npm 2.3.2 via existing `C:/Users/Mauri/.local/bin/opencode2.cmd`; in WSL `/home/tsops/.local/bin/opencode2` is a symlink to the SAME managed V2 binary as `opencode`. Neither compatibility alias needs an independent installer, model selection or service. Do NOT use or migrate back to Windows old standalone `C:/TS/tools/bin/opencode2.exe` v2.0.26 or WSL old `/home/tsops/.local/opt/opencode-2.1.0` as a fallback for NEW work. Historical installations remain physically preserved for existing sessions/effects. Do not remove old binaries, services or Orca terminals until their owners/effects are reconciled.

## Current native evidence ceiling

- Windows `opencode --version` and npm package readback both `2.3.2`; native Windows alias `opencode2.cmd --version` also `2.3.2`.
- WSL new isolated npm install original PID `9512`, exit `0` after `293.15s`; `@opencode/cli@2.3.2` installed in stable user prefix, native Linux ELF x86-64, CLI binary SHA256 `e6543f6e5c39c40971ba38afd1819ac852c29ac735b5a89065d3d148d47f27ad`. Linux `opencode` and compatibility `opencode2` both return `2.3.2` and realpath to the same managed executable.
- Orca Windows `1.4.265` status `ready / reachable / connected`, runtimeId at qualification `247c3eb7-94c7-4615-a1a9-f485ddcb0a68`. This ID is historical after restart and MUST NOT be reused as current without observation.
- One isolated new Orca terminal attempt `TS-EE-ORCA-OPENCODE-WSL-TERMINAL-PREFLIGHT-20261120-001-A001`: Orca native `terminal create` returned original `ok=true`, visible terminal handle `term_cc5e6abb-7cc5-487d-97c1-2ca92e64a1f1`, incarnation `f66aaa22-9de2-4d73-a3aa-e2c9ea6bd278` on neutral station `C:/TS/station`; `show` confirmed connected, non-orphaned WSL prompt. A single frozen `opencode --version` send was accepted with original requestId `f837e145-7b56-4506-a90e-a3fd2fa80cd6`; `terminal read --screen` printed `opencode v2.3.2` and returned to the Linux prompt. No inference or Product work.
- The diagnostic tab was closed via native `orca terminal close --terminal <exact handle> --json`, original PID `2608`, `ok=true`, exact handle/tab, `ptyKilled=true`. An earlier unsupported `--tab` syntax was denied with `invalid_argument`, effect NONE, and was not replayed.
- This qualifies a narrow current **CLI installation + Orca-owned visible WSL terminal/version-echo binding** only. It does NOT attest an arbitrary Linux child PID/UID/namespace/exit, independent provider authenticity/signatures, model inference, reviewer completeness, or Product execution/acceptance. E0b/E1 deeper custody remains separate.
- Original requests are published in `mauedgar/ts-execution-transport@22a8e54c0041cc66289e5b22185d0e71914a1b1f:requests/TS-EE-ORCA-OPENCODE-WSL-TERMINAL-PREFLIGHT-20261120-001/REQUEST.md` and `mauedgar/ts-execution-transport@a81fa5047d6b185c6912e27c67dcd487fe8547d3:requests/TS-EE-ORCA-OPENCODE-WSL-VERSION-PROBE-20261120-001/REQUEST.md`. Tool original outputs were observed in the ChatGPT Web Control turn; this method document is a derivative summary, not an authenticated byte-identical CLI stdout archive.

## Update mechanics: no new version-numbered prefix per release

Before a new technical update: observe original attempt(s) and live processes; verify known published stable target, native provider/OS, package source/integrity, disk, exact executable paths and targeted write-set; preserve terminal and service owners. Never perform automatic or blind retry.

Windows, in an authorized bounded station maintenance action: use the current npm global prefix with an exact version:
`npm.cmd install --global @opencode/cli@<verified_version> --no-audit --no-fund`.
Verify both `opencode --version` and `npm.cmd list --global @opencode/cli --depth=0`. Do not separately update `opencode2.cmd` compatibility shims or rename live binaries.

Linux from the authorized notebook, using native Ubuntu `tsops` tools with explicit PATH (no Windows-injected binaries):
`wsl.exe --distribution Ubuntu-24.04 --user tsops --exec /usr/bin/env HOME=/home/tsops PATH=/home/tsops/.local/bin:/usr/bin:/bin /home/tsops/.local/bin/npm install --global --prefix /home/tsops/.local/opt/opencode-managed @opencode/cli@<verified_version> --no-audit --no-fund`.
Verify `/home/tsops/.local/bin/opencode --version`, `opencode2 --version`, installed package version, Linux ELF target, realpath and SHA-256. The same stable prefix and its bin symlinks persist across future package updates. Do not install from an unverified remote `curl | bash`, duplicate numbered folders or copy Windows `node_modules` into WSL.

The exact `<verified_version>` is a *placeholder in the method*, never pass it literally to a machine. All new platform mutations require their own competent request/attempt and precondition checks. Avoid updating while relevant sessions/services are active or effects are uncertain.

## Orca/agent usage

- New semantic work: competent Control freezes Product-or-nonProduct subject and grant, isolated worktree, platform, exact model/provider/effort/cost permission, native terminal and result/receipt. Orca is launch/terminal correspondence; OpenCode V2 is the optional semantic executor; Git/competent Product Control owns Product meaning.
- Prefer Orca's supported native `OpenCode` agent integration using the actual v2 executable. Do not assume Orca's GUI default was changed by these CLI package updates: its actual agent command/host and terminal must be read/qualified before any *new* semantic launch. Old native `OpenCode2` UI requests remain aliases to the same v2 family, not a second distribution.
- Windows and WSL retain independent credentials/config/DB/services; no copying secrets, Yolo/trust changes, global model pinning, account migration or unapproved inference.
- For a real Linux-repository task use an Orca-owned native WSL repository/worktree, not the neutral Windows station diagnostic terminal; source/validation remains the competent Product's responsibility.
- Legacy Orca terminal `orphaned` statuses after runtime upgrade require exact owner/effect reconciliation before closing. Do not infer empty effect from GUI labels or process silence.
- Orca itself remains WinGet-managed v1.4.265; official v1.4.266 existed on GitHub at cutoff but was not yet indexed in WinGet. Do not run unqualified parallel/multiple installer upgrades merely to match a newer release; Orca update choices remain separately version/hash/runtime-bound. The installed provider already exposes `agent-cli-update.v1`, but the native agent update mechanism is not a substitute for this verified npm prefix ownership until its actual behavior is qualified.

## Boundary

TS EE station integration is technically operational at the CLI/visible-terminal layer. Product_authority NONE; Product_effect NONE; Remote State P0/P2 physical and PR63 untouched; Kernel replacement NO_GO; Beta Run008 paused. This document does not supersede the deeper original Orca provider custody/Windows-WSL child-exit qualification or invent an Independent Review. Do not promote synthetic, historical or agent-model results from this station verification.
