# TS-BEADS 047B — PowerShell expected-negative exit repair, no signing

**Existing experimental responsibility:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`. This is source-only mechanical regression work, not Product authority, a new TaskCycle, a new signing attempt, issuer appointment, SQL admission or distributed exclusivity grant.

## Original event preserved

Original public synthetic GitHub OIDC/Sigstore probe: `mauedgar/ts-execution-lab@499d172070aac6f7efb65aae425bf9d6545eba3e`, tree `7e0f9f0fb8ecfb0130d93a4f250c96052f2478df`, Actions run `41661195670`, attempt 1, job `126004528835`, `completed/failure`. Its logs show generated ephemeral keys, public synthetic sign-blob, local bundle creation, exact GitHub workflow identity `Verified OK`, tampered fixture rejection, followed by job exit 1. The tampered Cosign verification intentionally returned nonzero and the pwsh action shell propagated the last native command exit despite success markers. Upload-artifact was skipped and the run returned **no artifacts**. Potential externally published transparency effects must not be retried or presumed absent. No client data were supplied.

Source evidence and private data classification are frozen in `mauedgar/ts-execution-transport@99b53da1a3307221ce98f1b6b7ad972416e28050:results/TS-BEADS-047B-PUBLIC-KEYLESS-PRIVACY-20261103-001/CONTROL_DISPOSITION.md`, blob `2512c60b2781d41e45ed84838f17725ab73dca56`; original public privacy policy `mauedgar/ts-execution-lab@499d172070aac6f7efb65aae425bf9d6545eba3e:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/PUBLIC-KEYLESS-PRIVACY-20261103-001/PRIVACY_BOUNDARY.md`, blob `122da0cddfe65d75aea78dc39adf40f237e8025d`.

## New independent no-effect regression

`Test-047B-ExpectedNegativeExit.ps1` invokes only Windows `ComSpec /D /C exit /b 17` to simulate a rejected signature verification; if the captured code is nonzero and **exactly expected**, it writes `EXPECTED_NEGATIVE_PROCESS_REJECTED` and explicitly `exit 0`. An incorrect expected code must throw `NEGATIVE_MOCK_EXIT_MISMATCH` and exit nonzero.

The new GitHub-hosted Windows CI calls the script with `ExpectedRejectedExitCode=17` (expect success), and again with `ExpectedRejectedExitCode=19` (expect failure with exact marker). It verifies expected/observed process codes and source/fixture Git blobs. It never installs or invokes Cosign, GitHub OIDC, Fulcio or Rekor, never uploads a bundle, and never triggers a signature. No SQL, Dolt, Beads graph, Tailscale configuration or Product writes. GitHub credential access: `contents: read` only; no `id-token: write`. This is **not** a retry of the original run nor an admission to sign again.

## Security/privacy constraints and next dependency

Only a new independently selected **different** fixed `PUBLIC_SYNTHETIC` subject could be used in a *future* separately authorized signing trial, with a single original attempt, off-host reconciliation requirements and bundle preservation before expanding any use. Do not reuse the original fixture as a new signing attempt by editing a workflow. No customer data, secret bytes, internal operational IDs, correlated hashes, personal or health records in GitHub Actions, public Sigstore/Rekor, or logs. Public signing is for intentional public software provenance only; confidential grants need private authentication/KMS or an independently qualified private signing service.

Product SOT `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remains unchanged. #34 `CLOSED_PASS`, #35 H6 independent, Kernel `UNDECIDED`; previous BETA `PROVIDER_UNKNOWN`, V6P2 `ABANDONED_UNRECONCILED_UNKNOWN`, F03-02/F04 `BLOCKED_TOOL_SECURITY`, no retry or Product migration. Experimental host independence `INCOMPLETE`.

**Expected qualification:** `EXPECTED_NEGATIVE_EXIT_SOURCE_PASS / NO_SIGNATURE / NO_SQL / NO_PRODUCT`, no claim of portable signed bundle or two-host Dolt/Beads continuity.
