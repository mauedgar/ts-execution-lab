# Beads 037 — Real Dolt/Beads OS-principal isolation and guarded causal writing

**Authority:** EXPERIMENTAL_CONTROL_ONLY. Product NONE. Canonical `mauedgar/tecnotron-ai#35` wholly owned by `TECNOTRON_BETA_CONTROL`; Attendance and Product TaskCycles are not touched. This is an isolated native Beads experiment, not a declaration of adopted architecture.

Frozen native source `native037.py` Git blob `ab60ebeef0bc28b11c3f769f27d7c4327b1f3702`. Git parent `ts-execution-lab@60fd974cb713f436d751cdf5fea99f7658a505bb` (036 terminal). **New** ExecutionAttempt `TS-BEADS-037-ATTEMPT-001`, one push-triggered run on a unique Git commit. No historical 028/035/036 replay.

### Runtime

Native Beads `v1.3.1` release archive SHA-256 `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`; Dolt `v2.2.0` archive SHA-256 `1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6`. Disposable Unix two-UID `ts037writer`/`ts037reader`, writer-only 0700 directory with secret 0600 token, authenticated local Dolt SQL root, authenticated `bd serve` on loopback. No Product or shared remote. No direct SQL/secret access granted to reader.

### DoD

1. Verify distinct UIDs and denied reader file access to writer root/credentials, using OS behavior rather than a prompt-only policy.
2. Reader's direct `bd dep add` and independent `bd serve` pointed at the writer's private repository **must not mutate** the protected graph. No privilege escalation, no bypass outside this authorized fixture.
3. SQL root authentication requires the writer secret; reader may reach localhost socket but not acquire privileged credentials. HTTP without bearer cannot read/mutate the selected Beads service.
4. Native writer uses `bd init`, `bd create` three real issues, selected authenticated HTTP `batchApply` with root `expected_version` and dep addition. Version increases, exactly one correct edge persists; stale batch fails.
5. Fresh native `bd show --json`/ `bd ready --json` readback after HTTP shutdown succeeds.
6. Historical privileged-bypass finding #028 and divergent `UNKNOWN` classification #030 **remain open**. Test shall **not** claim universal writer isolation, Product audit parity or permission to retire Kernel. Explicit authorized sudo/root on ephemeral runner is not Product containment.
7. Runner original `RESULT037.json` + no-secret original logs and pinned binaries metadata conserved in a 30-day artifact. Terminal status `PASS_SCOPED_UNPRIVILEGED_DENIAL_AND_GUARDED_NATIVE_PATH_WITH_PRIVILEGED_BYPASS_OPEN` only if every check PASS; otherwise FAIL/BLOCKED original no auto retry.

No new Kernel/daemon/scheduler, no canonical adoption, no automatic #35 dependency. Results may inform Beta Control but do not alter its authority.
