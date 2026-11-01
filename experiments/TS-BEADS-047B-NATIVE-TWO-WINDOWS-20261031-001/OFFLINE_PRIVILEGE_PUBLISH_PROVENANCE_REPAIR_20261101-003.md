# TS-BEADS 047B — corrected original-file publication after independently proven manifest blob error

**Operation** TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001, experimental only, Product NONE.
**NEW ExecutionAttempt:** TS-BEADS-047B-OFFLINE-PRIVILEGE-PUBLISH-20261101-003, distinct from terminal failed publishers 001 (misread copy permission) and 002 (manifest Git blob metadata discrepancy).
**Owner:** notebook DESKTOP-DJLBEQH, Commander 40cc0b10-fa7b-4a6a-98cf-1c94f93791b2, Orca C:\TS\station.
**Original builder** TS-BEADS-047B-OFFLINE-PRIVILEGE-CANDIDATE-20261101-001, terminal NO_GO_OFFLINE_PRIVILEGE_FEASIBILITY, source ORIGINAL C:\TS\station\experiments\TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001\OFFLINE-PRIVILEGE-CANDIDATE-20261101-001\candidate\.
**Frozen original task** this public repo @efef3eac25f1883b783a086f58740515d41db691:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE_PRIVILEGE_BOOTSTRAP_CANDIDATE_REQUEST_20261101-001.md Git blob 8c064389be200c47cb9f1b3bf282d389b68fb67e.
**Exact DESTINATION** public mauedgar/ts-execution-lab experiment/beads-047b-native-two-windows-20261031-001:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE-PRIVILEGE-CANDIDATE-20261101-001/candidate/. NO other target.
**Scope** transport-only, no SQL/init/server, credentials, Beads, Serve, Product, code edit or test rerun.

## Precise evidence-based provenance correction

Original producer HASHES.json has one bad Git blob for `MOCK_RECEIPT.json`: declared `8f3e0857efe8bfb66cb8c4b1323ccd377699ccec` but original bytes SHA-256 `E4223CF75CD25B7C954935CEBF400F54BF642D93EEB89DE6D3F0D820A2F8A3ED` match both original producer and exact after-build verification. Original publisher and a DISTINCT Control mechanical git hash-object --no-filters on that exact original file produced the correct blob `6d500acb167e2b536be9e5b180877e4bd82dd1c2`. This is a metadata mismatch only, not a waived SHA256. Keep original source file AND original HASHES.json immutable. Explicitly permit publication of ORIGINAL bytes provided that **all six SHA-256 match producer declarations**, five other original Git blobs match producer, and the one corrected blob equals exactly `6d500acb167e2b536be9e5b180877e4bd82dd1c2`. Any other mismatch -> BLOCKED; no generic waiver.

## One bounded transport execution

1. Confirm original producer and both prior publisher attempts are terminal, no concurrent writers, target remains absent remotely, exact paths and no unknown remote Git effect.
2. Verify six exact original files `OfflinePrivilegeBootstrap.psm1`, `MockNativeHarness.ps1`, `MOCK_RECEIPT.json`, `NO_EFFECT_REPORT.md`, `README.md`, `HASHES.json`. Recompute all SHA256 and git hash-object --no-filters from raw bytes, reject symlinks/other files/secret values. Use ONLY the specific original manifest correction above. Original hash manifest is evidence and MUST be published UNALTERED, even though it has the known metadata error.
3. IT IS AUTHORIZED TO CREATE an isolated **DESTINATION** Git clone of this PUBLIC experimental branch, COPY the ORIGINAL SIX files byte-for-byte to the NEW destination paths, stage exactly six new files, make one commit and one push, and verify the published remote Git blob/SHA256. It is FORBIDDEN to modify any source original, change their bytes or re-run implementation/tests; do not confuse permission to create copies with source modification.
4. `gh api user` verifies authenticated owner and repo permission; per-command Git author from verified account only, no global identity configuration. Previously verified user login mauedgar and `mauedgar@users.noreply.github.com` in original Git evidence, recheck. No destructive git reset, force push, unrelated files or secrets. If branch moved unexpectedly reconcile before any effect.
5. After commit/push verify remote branch current commit, diff exactly six files and new file contents equal original bytes. If ambiguous, do not retry; preserve original. Return compact receipt with commit/tree/original and corrected blob and original NO_GO disposition. This publication neither asserts live credential privilege security nor SQL GO.

**Model:** OpenCode2 standalone --agent build --model openai/gpt-5.6-terra. Once only, no retry. If another mismatch, stop with specific evidence. Independent review by ChatGPT Web only after immutable source published.
