# TS-BEADS 047B — Dolt 2.6.2 source-only compatibility repair

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, experimental only; Product effects **NONE**. **Status:** `SOURCE_ONLY / NOT_DISPATCHABLE / NO_SQL_GRANT / NO_NATIVE_HOST_EXECUTION`.

## Why a distinct candidate is necessary

The original immutable `OFFLINE-PRIVILEGE-FIXTURE-V6P1-20261102-001` (source base `7184ea0461f3fd4c25b4e9a4b6f157e40c92a754`) pins Dolt 2.2.0 SHA256 `BED880C0E6B522498A563FCD1F0FC1E25527BA07E66C1E0A85C2242B64DFD967`. The physical hosts were later upgraded to Dolt 2.6.2; the recorded installed-executable SHA256 is `DF49F737CB80FC0F32B02220C701F476D378F322FA1BB51D696728FDAE825B91`. The original one-shot V6 attempt is not a retry target and its files, refs and effects remain frozen.

This **new** source candidate uses attempt `TS-BEADS-047B-DOLT262-OFFLINE-FIXTURE-20261104-001` and isolated parent `%LOCALAPPDATA%\TS047B-Offline-D262` (distinct from historical `TS047B-Offline-V6`). It reuses the existing V6P1 Windows ACL, signed-grant, atomic receipt and fail-closed offline fixture mechanics instead of creating a parallel authority engine. Module/runner/launcher source Git blob IDs are internally pinned; the Python test verifies them.

**Hard safety fence:** `Security-047B-D262.psm1` deliberately retains `V6TrustedKeySha256=('0' * 64)`; the authority verifier refuses every effect until a **different** independently reviewed source revision pins a competent trust anchor. No client argument, unsigned JSON document, this source commit or user chat instruction can provision that anchor. Neither `-Preflight` nor source-only CI is acceptance or a SQL execution grant.

## Reused evidence and exact scope

- Original frozen 047B DoD Git blob `26388665fc0782fd10b24adca96a7dfa47c6a952`, unchanged. Product TaskCycle/Kernel/#35 not touched.
- Dolt 2.6.2 / Beads 1.3.2 isolated real-native Windows SQL compatibility: `ts-execution-lab@9d43ee8ab079a3793623941f8497280a6a42fe69`, Actions `41741981354` attempt 1, 19? **Not claimed** for this new candidate. Its exact original server-pair job `126285476360` was `completed/success`; it used one hosted runner, not two physical hosts.
- Independent IR008 `mauedgar/ts-execution-transport@0a0e8f9a4788058b362099c4750e2ce5e5e923e4` qualifies **only** the separate Tailscale peer read-only script, not this SQL-capable source.
- Previous notebook and desktop peer-readonly terminal receipts are preserved without replay. Earlier BETA `PROVIDER_UNKNOWN`, V6P2 `ABANDONED_UNRECONCILED_UNKNOWN` and off-host CAS security block are not cured by changing a pinned binary.

## Source-only test

`python -m unittest discover -s tests -p test_source_contract.py -v`

Checks immutable new attempt, disjoint physical parent, exact Dolt hash, still-disabled trust anchor, LF-only inputs, actual module/runner blob correlation, and no `sql-server`/Tailscale configuration step. Windows hosted CI may additionally parse PowerShell AST. These static tests **do not execute the runner, native SQL, registry changes, secrets, Tailscale status or Beads graph**.

## Next dependency (not automatic)

Independent source/security review of the **final exact** new candidate commit/tree, 3 source blobs and original CI if run. A future *separate* accepted revision must reconcile original effect identity/collision-free write-set, competent issuer/trust binding and one-time grant, OS owner/ACL, protected credentials, actual Dolt 2.6.2 offline SQL dialect/privilege semantics, bounded child process and durable original provider receipt. Only then may Control consider **one** conditioned disposable localhost/offline effect; current source cannot perform it.

**No** current Product adoption, full 047B DoD, SQL service, Tailscale ingress, backup/restore, or host independence is claimed.
