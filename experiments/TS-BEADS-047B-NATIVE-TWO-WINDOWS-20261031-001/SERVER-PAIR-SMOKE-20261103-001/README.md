# TS-BEADS 047B — One-shot native loopback server pair (experimental only)

**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`. This is a **new narrowly scoped synthetic Windows CI experiment**, not an effect replay, Product authority, new TaskCycle, customer-data use, root-secret provisioning on the user's hosts, or acceptance of the full DoD. Preserve original `DOD.md` Git blob `26388665fc0782fd10b24adca96a7dfa47c6a952`, Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, #34 CLOSED_PASS, #35 H6 independent, Kernel UNDECIDED.

## Why this test

Dolt 2.6.2 and Beads 1.3.2 are installed on notebook and desktop, but the *v1.3.2 Beads tagged docs* pin standalone Dolt 2.2.0, not 2.6.2. Successful independent SHA/version checks and Dolt-only fresh reset 8/8 do not prove the pair can actually run SQL-mode issue transactions. This original test qualifies **real native binaries on a disposable hosted Windows runner**, before any native notebook SQL or Tailscale ingress. It must never silently fall back to embedded Beads or SQL on a real device.

## Exact data/effect scope

- Runs only on a GitHub-hosted ephemeral Windows 2022 machine and only first attempt (`run_attempt=1`), pinned to one exact source commit/parent, with `contents:read` and no GitHub OIDC, signing or secrets.
- Downloads official released ZIPs, **verifies published SHA256**: Dolt v2.6.2 Windows AMD64 `D804A06806A91B9E6ACD2A0AC6EBEC5C5D64756AFF4572FA079FBC5499F1916C`, Beads v1.3.2 Windows AMD64 `E59CB7742278185493E30C2EB97CB318DB8D7A58C28EE5E88C2A30C7630C0975`.
- Requires private fresh `RUNNER_TEMP` root, no existing 14337 or 3307 TCP listener; locally creates a *synthetic* disposable database and SQL writer/reader, generates three high-entropy credentials inside the runner using OS CSPRNG, feeds SQL to the native **offline** Dolt CLI over redirected stdin, never passes passwords in arguments or logs. Explicitly changes the built-in root account password before starting a listener. Checks an isolated privileges file exists.
- Starts only the original, identifiable Dolt executable with `--host 127.0.0.1 --port 14337 --data-dir` inside the runner. Checks the listener is loopback-only. No Tailscale Serve/Funnel, LAN/public binding or SQL on notebook/desktop.
- Uses native Beads 1.3.2 for server-mode initialization, creates, reads and closes an explicitly synthetic issue across two fresh local workspaces. Checks wrong-password authentication and SELECT-only actor cannot create issues, without overriding or using a privileged reader. No customer/secret data in git, logs, public artifacts or signatures.
- A failed or timed-out native effect yields a compact fail-closed result. No automatic retry or cleanup of ambiguous processes, no built-in rerun or escalation. Runner deletion after CI is GitHub's ephemeral-host lifecycle and **not** a remote provider-effect absence proof.
- Only after full original PASS may Control conclude `SYNTHETIC_LOOPBACK_SERVER_PAIR_PASS`; this **cannot** establish host A→B continuity, Tailscale ACL, real server credential safety on user hardware, external backup/restore, conflicts or provider UNKNOWN reconciliation. Any native failure remains an exact evidence-bearing `INCOMPLETE/NO_GO for the pinned pair`, not permission to patch and replay the same original attempt.

**No effects on existing 047B DoD:** original BETA provider UNKNOWN, notebook V6P2 UNKNOWN, off-host CAS F03-02/F04 blocks and public Sigstore V2 security-blocked staging remain separate; no automatic adoption of Beads as Kernel. The next valid experiment, only after this pass and separate admission, is secure localhost 047B primary service plus two physically independent clients.
