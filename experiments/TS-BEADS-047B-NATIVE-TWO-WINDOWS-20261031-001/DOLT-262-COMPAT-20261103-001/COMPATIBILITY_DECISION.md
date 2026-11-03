# TS-BEADS 047B — Dolt 2.6.2 qualification (experimental, no Product modification)

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, `EXPERIMENTAL_CONTROL_ONLY`. Original DoD blob `26388665fc0782fd10b24adca96a7dfa47c6a952` remains unchanged, and #34 CLOSED_PASS, #35 H6 independent, State Kernel UNDECIDED. This document is a qualification plan and does not declare server readiness, data migration or a new Product TaskCycle.

## Exact version decision

- Latest stable Dolt release observed through official GitHub API 2026-11-03: `dolthub/dolt@v2.6.2`, 2026-10-31. Official Windows AMD64 ZIP SHA256 `D804A06806A91B9E6ACD2A0AC6EBEC5C5D64756AFF4572FA079FBC5499F1916C`. Keep immutable version/digest, not `releases/latest`.
- Notebook existing global `C:\Program Files\Dolt\bin\dolt.exe` remains `2.2.0`, exact executable SHA256 `BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967`, zero Dolt processes, zero TCP 3307 listeners, original isolated %LOCALAPPDATA% TS-BEADS-047B absent at read-only preflight. This is rollback reference, **not authorization to overwrite it**.
- Native Beads on notebook and desktop: `bd 1.3.1`. Beads **tag v1.3.1 and v1.3.2** recommends Dolt **2.2.0** for server mode and embeds that engine. The *current main development docs* require >=2.6.0 and pin 2.6.0. **Do not silently assert that bd 1.3.1 + Dolt 2.6.2 are an upstream-qualified pair.** Same-version CLI help is not a complete server-compatibility test.
- Beads stable `v1.3.2` (2026-10-24) fixes least-privilege Dolt writes and multiple backup/retention correctness bugs. It is a separate candidate for later native Beads adoption, not an implicit host upgrade; the current Beads binary is unchanged.
- Dolt 2.6.2 includes storage consistency/fsck updates, replication/DDL fixes and shutdown improvements per its release notes. A newer version can have regressions. The tagged Beads v1.3.2 docs report hard-reset failure in 2.3.0/2.3.1 with later versions unmeasured at that tag; current Beads main measures pinned 2.6.0, but these measurements are **not evidence for 2.6.2**.

## Experimental acceptance and boundaries

1. First qualify exact Dolt 2.6.2 Windows ZIP and exact native version on ephemeral Windows CI. Test only disposable clean repo init, SELECT 1 and CALL DOLT_RESET('--hard') using explicit cwd under runner temp. No network SQL listener, Tailscale, privileged accounts, customer records, Product, real database, or public signatures.
2. Keep original Dolt 2.2.0 executable until a safe side-by-side 2.6.2 installation is confirmed. Never overwrite the pinned 2.2.0 rollback reference merely to run a smoke test. When changed on notebook, reverify current processes, source and SHA256, verify no open SQL, test new binary through absolute path with version/hash.
3. Source-adapt experimental manifests and scripts through **new version-qualified candidates** only. Do not edit frozen V6P1/V6P2, execution attempts, accepted DoD or published receipts. Add selected version/hash/rollback fields to future runners and CI. Pin Beads separately, never assume external Dolt changes the embedded Beads engine.
4. SQL privilege bootstrap, SQL server access, client Beads compatibility, two-host graph/outage/backup and provider UNKNOWN remain separate empirical dependencies. Do not call native CLI privilege readback an authorization check for SQL reader; server user privileges require their own tests and grants. Existing external provider UNKNOWN and blocked CAS effects are not retried.
5. Private user/customer/secret data remain excluded from this public lab. Only upstream public release archives and synthetic temp directories can appear in test logs. No secrets in CLI argv/records.

**Disposition before empirical CI:** `DOLT_262_SOURCE_CANDIDATE / NOTEBOOK_220_PRESERVED / NO_SQL_SERVICE / HOST_INDEPENDENCE_INCOMPLETE`.
