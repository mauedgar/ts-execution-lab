# TS-BEADS 047B — experimental dual-host dependency matrix after native installation

**Scope:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, `EXPERIMENTAL_CONTROL_ONLY`; this is an experimental version/runtime reference, NOT Product SOT or a new Product TaskCycle. The original `DOD.md` blob `26388665fc0782fd10b24adca96a7dfa47c6a952` is frozen. Product #34 `CLOSED_PASS`, #35 H6 independent and State Kernel `UNDECIDED` remain unchanged.

## Verified packages on 2026-11-03

| Component | Notebook native | Desktop native | Official release SHA/qualification |
|---|---|---|---|
| Dolt | v2.6.2 **PASS** | v2.6.2 **PASS** | Official `DoltHub.Dolt` MSI SHA256 `9DB861EF741F0F5AA557B7E7A910F53DC6F309DB753099CD64E91FAD694BB402`. Installed `dolt.exe` SHA256 `DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91` on BOTH hosts. |
| Beads | v1.3.2 **PASS** via `bd` | v1.3.2 installed **PASS** via absolute package binary; simple `bd` alias **NOT_AVAILABLE** | Official `GasTownHall.Beads` ZIP SHA256 `E59CB7742278185493E30C2EB97CB318DB8D7A58C28EE5E88C2A30C7630C0975`; installed `bd.exe` SHA256 `280517091DDA13CB195A39F991144771117B2BC26A4D472612F8FC9FD80F46E2` on BOTH hosts. |
| Tailscale | v1.104.4 | v1.104.4 | Official stable v1.104.5 was published 2026-11-03; service update deferred to avoid disconnection during dual-host experiment. No server or tailnet ACL changes. |

Both Dolt updates/installation from exact version winget returned exit 0, verified original vendor download hash, executable version and identical digest. Notebook Beads winget returned exit 0, and link + executable version validated. Desktop Beads winget returned exit 0 and official ZIP digest matched, executable version/hash validated **from the package store**; old `bd` command alias disappeared after the package update.

### Desktop WinGet alias — known OS privilege issue

- Existing package binary (no username serialized): `%LOCALAPPDATA%\Microsoft\WinGet\Packages\GasTownHall.Beads_Microsoft.Winget.Source_8wekyb3d8bbwe\bd.exe`, version 1.3.2, exact digest above. This **works when invoked by absolute path**, so the package is installed.
- The directory `%LOCALAPPDATA%\Microsoft\WinGet\Links` is present and in `PATH`, but its `bd.exe` symbolic link is absent. Notebook has the corresponding valid symbolic link.
- A **single conditioned link-only repair**, separately frozen in private Transport, failed terminal with `NewItemSymbolicLinkElevationRequired`. **No symlink was created**, no installed package was overwritten, no follow-up hardlink, WinGet retry, registry/Path mutation or admin privilege escalation performed.
- Future *experimental* runner design must accept a **known signed installed binary path**, not rely exclusively on `bd` in PATH: check the standard WinGet package path above and its exact SHA256/version, then invoke it by absolute path if no usable `bd` alias exists. This is a source-level compatibility guideline, not a request to modify Windows configuration; do not automatically create the missing symlink. Any command-alias repair requires separate operator/admin privilege or other properly authorized OS configuration fix.

## Source-only qualification, not server-mode admission

- Pinned pair `bd 1.3.2 + Dolt 2.6.2` downloaded and verified in GitHub-hosted Windows-2022 on original Actions `41677904118`, attempt 1, job `126063371015`, source `mauedgar/ts-execution-lab@0ce154322c98581210f69f5a58bfc90817e0effb`: `completed/success`, marker `BEADS_132_DOLT_262_NATIVE_BINARIES_PINNED_PASS`.
- Earlier Dolt v2.6.2 Windows isolated smoke run `41676512449`, attempt 1, 8/8 fresh synthetic databases with SELECT and hard-reset PASS.
- **Critical upstream compatibility caveat:** Beads `v1.3.2` tagged documentation still pins standalone Dolt **2.2.0**, even though Beads upstream main development pins minimum 2.6.0. Therefore Beads 1.3.2 + Dolt 2.6.2 external SQL/server mode is **not yet proven** or implicitly authorized by installation; do not launch any real 047B server until separate synthetic auth/privilege/client tests and dedicated original effect receipts.
- Desktop Dolt binary is optional for Beads remote-only client, but installed at user's explicit request, with no SQL service started. Do not treat parallel local databases as an authoritative 047B setup; notebook remains intended sole SQL primary.
- Tailscale 1.104.5 requires separate controlled network service upgrade with outage/rejoin and rollback evidence. Do not conflate it with Beads/Dolt pin updates.

## Security/authority boundary

No Product writes or Kernel change, no Dolt 047B database, SQL server or ingress, no client/sensitive data, no secret/credential emission in command arguments or receipts, no Beads issue graph and no new signatures. Existing V6P2 `ABANDONED_UNRECONCILED_UNKNOWN`, BETA `PROVIDER_UNKNOWN`, and CAS F03-02/F04 `BLOCKED_TOOL_SECURITY` remain fenced. This matrix **updates experimental documentation only**, never previously frozen source subjects or original receipts.

**Disposition:** `DUAL_HOST_DOLT262_INSTALLED / DUAL_HOST_BEADS132_BINARY_INSTALLED / DESKTOP_BD_ALIAS_BLOCKED_ADMIN / TAILSCALE1044_STABLE_BUT_ONE_PATCH_BEHIND / SERVER_PAIR_NOT_QUALIFIED / HOST_INDEPENDENCE_INCOMPLETE`.
