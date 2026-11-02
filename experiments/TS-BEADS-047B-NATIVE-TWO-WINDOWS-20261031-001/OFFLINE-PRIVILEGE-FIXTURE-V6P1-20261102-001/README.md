# TS-BEADS 047B — V6P1 targeted pin repair (SOURCE ONLY)

**Operation unchanged:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`. This is a new immutable **source candidate**, not a new Product TaskCycle, effect attempt, signer grant, acceptance or authorized SQL. **Disposition:** `SOURCE_ONLY / NO_GO_DISPOSABLE_SQL_EFFECT / NO_NATIVE_WINDOWS_EVIDENCE`.

## Frozen subject / review history

- Baseline executable V6: `mauedgar/ts-execution-lab@978cabfa256eb1655f222f994893589f7bebfe72:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE-PRIVILEGE-FIXTURE-V6-20261102-001/`.
- Independent IR012 original: `mauedgar/ts-execution-transport@ee6e2f797f88e99068b20a64f52af2f09997b078:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V6-20261102-001/WEB_INLINE_IR012-FINAL-SOURCE-978cabfa-20261102.md`; verdict FAIL.
- IR011 V5 original: `mauedgar/ts-execution-transport@765132242f65bb752c890752603d3ca38fb46ded:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V5-20261102-001/WEB_INLINE_IR011-SECURITY-V5-20261102.md`.
- Original V6 branch manifest metadata `noRealCAS=false` was incorrect. A later source-branch commit `38cb689c04d54a694e73f1a29646884c5b8cd6f0` corrected it to **true**, but did not mutate the original frozen 978cab commit. This new candidate explicitly documents `realOffHostExclusiveClaimVerified=false`.
- Targeted test correction: `tests/test_source_contract.py` V6 launcher pin `af06633d104a8c860773fda4b96bc3f9200c1f7b` was V5's blob; V6's correct blob is `694abdf96b693a1d66d384ba1543237947248ef5`. All three executable sources and both PowerShell tests were copied **byte for byte**, without renaming V6 runner/attempt identifiers or changing behavior.

## Evidence and limitations

This candidate keeps the pinned trust-key hash at 64 zeros, with **no competent issuer, SQL grant, signed authority or original effect reconciled**. A previous positive GitHub branch CAS fixture is synthetic **and does not constitute a verified authoritative off-host exclusive claim** for the live effect. The read-only native notebook gate has not run; PowerShell/Windows ACL/PInvoke, Tailscale schema, subprocess lifecycle and real Dolt 2.2.0 privilege persistence have no native original receipts. Unknown original effect state blocks retries. Offline CLI persistence would not establish remote reader denial or host independence.

**Review request:** independent reviewer inspect exact V6P1 frozen commit; verify the seven source/test/README raw blobs, SHA256, bytes and immutable diff vs original V6; scrutinize whether the Python test actually passes, signature fail-closed, no automatic variable assignments, native requirements, and any newly introduced source issue. Report `PASS_SOURCE_LIMITED`, `PASS_WITH_ADVISORIES` or `FAIL`, keeping external effect blockers explicit. No SQL, Commander, Beads, Tailscale Serve, Product or #35. Do not falsely declare zero advisories from source inspection.

**Next beyond source review:** qualify read-only/negative Windows receipts on notebook after exact materialization by a permitted normal repository surface; independently qualify issuer, real CAS claim and original provider effect reconciliation; only then consider a separately explicit one-time disposable SQL grant. Maintain `#34 CLOSED_PASS`, `#35 H6` independent of Beads, and Product `State_Kernel.final_disposition=UNDECIDED`.
