# TS-BEADS 047B — corrected ONE-SHOT original candidate publisher

**Operation:** TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001, EXPERIMENTAL_CONTROL_ONLY, Product NONE.
**NEW ExecutionAttempt:** TS-BEADS-047B-OFFLINE-PRIVILEGE-PUBLISH-20261101-002.
**Owner:** notebook DESKTOP-DJLBEQH / Commander device 40cc0b10-fa7b-4a6a-98cf-1c94f93791b2 / Orca station C:\TS\station.
**Original builder:** TS-BEADS-047B-OFFLINE-PRIVILEGE-CANDIDATE-20261101-001, terminal term_4c4a2ea9-5532-4902-88dc-0a6b6d50a6e1, result NO_GO/BLOCKED_OFFLINE_PRIVILEGE_FEASIBILITY, local ORIGINAL candidate created under C:\TS\station\experiments\TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001\OFFLINE-PRIVILEGE-CANDIDATE-20261101-001\candidate\.
**Original publisher 001:** TS-BEADS-047B-OFFLINE-PRIVILEGE-PUBLISH-20261101-001, terminal term_88a74d7b-0c19-4f75-b7a9-b86f85ccb557, reported BLOCKED_COPY_POLICY and no files/remote writes. No retry of 001; current request is a distinct corrected publication permission.
**Frozen original task source:** same PUBLIC repo @efef3eac25f1883b783a086f58740515d41db691:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE_PRIVILEGE_BOOTSTRAP_CANDIDATE_REQUEST_20261101-001.md, Git blob 8c064389be200c47cb9f1b3bf282d389b68fb67e.
**EXACT target:** public repo mauedgar/ts-execution-lab, branch experiment/beads-047b-native-two-windows-20261031-001, experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE-PRIVILEGE-CANDIDATE-20261101-001/candidate/.

## IMPORTANT: Copying to the new destination IS authorized

The previous worker mistakenly interpreted the prohibition on modifying ORIGINAL files as a prohibition on creating Git destination copies. This is expressly corrected:
- YES, authorized: read original candidate file bytes, compute hashes/scan, create a fresh isolated Git clone/checkout, **COPY the originals byte-for-byte INTO THE NEW REPOSITORY DESTINATION**, `git add` EXACTLY those NEW destination copies, create one Git commit, push once, verify remote blob hashes, return receipt.
- NO, forbidden: modify/reformat/rewrite any ORIGINAL source bytes, execute/reconstruct the candidate, re-run original mocks, create passwords, Dolt init/sql/sql-server, Tailscale Serve/Funnel, Beads mutation, Product writes, blanket git reset or deleting unrelated files.

The expected original allowlist is **six existing files**: `OfflinePrivilegeBootstrap.psm1`, `MockNativeHarness.ps1`, `MOCK_RECEIPT.json`, `NO_EFFECT_REPORT.md`, `README.md`, `HASHES.json`. Read exact source from the original local staging directory, NOT private Transport and NOT other repos. If missing/mismatched hashes or unexpected sensitive data, STOP without publication.

## Deterministic procedure

1. Verify original builder and prior publisher are terminal, remote branch has no published candidate, and no same attempt is running; confirm exact source path and original hashes. No source editing.
2. Validate no real secrets/tokens/private Tailscale pairing values in original content and no symlinks/traversal. If sensitive, fail closed.
3. Obtain an isolated fresh clone of the public lab branch via authenticated GitHub (do not use Orca station root as a Git repo). Verify `origin` and branch, repo write permissions and HEAD; no force-push. Source files are immutable; **writing the new target copies is the intended permitted effect of this publication action**.
4. Use authenticated `gh api user` to ground owner identity. Prior 047B authenticated login was mauedgar with permission admin; reverify. Use only per-command `git -c user.name=mauedgar -c user.email=mauedgar@users.noreply.github.com` if these values match CURRENT authenticated repo/Git evidence. No global config, tokens in command args or credentials in files.
5. Stage ONLY six target copies. Check staged paths contain exactly expected files and no deletion/unrelated edits. Commit once, push once, verify from GitHub current branch the exact six source bytes Git blobs, SHA256 and no unrelated modifications. If push ambiguous, observe GitHub before retry; no blind retry. Return exact commit/tree and original source checksum receipts.
6. The original builder already returned **NO_GO**, so this publication is for **independent review of a blocked candidate**. Never label it SQL_GO or host-independent; no Product authority.

**Provider:** OpenCode2 build standalone --model openai/gpt-5.6-terra. If the Git clone/auth source cannot be verified, return BLOCKED with exact reason. This task is finite, transport-only, one dispatch, no retry.
