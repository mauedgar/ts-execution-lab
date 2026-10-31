# TS Beads 041 — Portable native Dolt/Beads store between independent GitHub runners

**Authority:** EXPERIMENTAL_CONTROL_ONLY; Product NONE. Canonical #35 remains Beta Control. This is a new **two-job** isolated experiment, not a replay of prior 040 or any Product state. One `TS-BEADS-041-CREATE-001` producer and a dependent `TS-BEADS-041-JOIN-001` consumer; both within **one original Actions run** and explicit GitHub artifact dependency. No retry or subsequent delegated work if producer fails.

**Fixed sources:** `native041.py@b8e9f34fdb5fd53a8b46f5967afaae3a81cb51a4`; `join041.py@0a1df5124a668a187d82967a8b91c95bf436c523`. Native Beads v1.3.1 SHA256 `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c` and Dolt v2.2.0 SHA256 `1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6`. Frozen raw original GitHub provider reference: 039 run `41173329767`, artifact `13031552292`, digest `sha256:96839db7c20212930ccb80a4147bb3c69f35d23ef70a65d909b58f8fff41593c`; provider not rerun.

## DoD

1. **Producer runner:** native `bd init/create/dep/update/close/ready/history/show` on disposable `.beads` embedded Dolt store; original 15 checks PASS and `ready=[]` terminal; verified original provider ref in issue descriptions; no Product, Git remote or provider execution.
2. **Transport:** create a tar of native `.beads` directory, persist original archive + its SHA256, original result and manifest in GitHub artifact. No credentials, auth tokens or Product files included. No reuse of existing state.
3. **Fresh consumer runner:** `needs: producer`, obtain exact artifact ID from current run via `download-artifact`, verify archive hash, extract to **new independent temp Git directory**, execute read-only native `bd ready/show/history` using pinned binaries. All tasks terminal/description references exact and history nonempty. No Product, provider effect, writes or Beads migration.
4. Preserve independently produced consumer `JOIN041.json` with hash and original logs, verify `provider_redispatch_count=0`.
5. No forced inference of distributed concurrent writers, global hash-chain equivalence, privileged writer exclusivity, multi-host Dolt live replication, external Product acceptance or physical power failure.

**Disposition:** `PASS_NATIVE_BEADS_STORE_PORTABLE_FRESH_RUNNER / COMPLETE_WITH_LIMITATIONS` only if exact creation and join success verified. If archive is structurally not portable, preserve original failure and report required migration instead of declaring native handoff READY.
