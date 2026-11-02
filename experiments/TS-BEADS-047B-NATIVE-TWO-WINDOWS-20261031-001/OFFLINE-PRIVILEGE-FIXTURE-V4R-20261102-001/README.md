# TS-BEADS 047B — V4R immutable source-repair candidate

**Experiment:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (same operation). **Scope:** EXPERIMENTAL_CONTROL_ONLY. **Status:** `SOURCE_ONLY_CANDIDATE / NOT_DISPATCHABLE / NO_SQL_EFFECT`. No Product/TaskCycle/Kernel/Attendance #35 changes.

## Provenance and no-replay
- V3 frozen `mauedgar/ts-execution-lab@b2bb1f26206000abe61e971f51be0a7c9d4051f3`; IR009 independent `mauedgar/ts-execution-transport@9d134dac7b3fa7c64452c0b295849c43f6394472:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V3-20261102-001/WEB_INLINE_IR009-SECURITY-V3-20261102.md`, Git blob `c1c7fcc34997b48b5ecd4c01c80d2605d4568d29`, FAIL.
- Prior intermediate `OFFLINE-PRIVILEGE-FIXTURE-V4-20261101-001` security module was discovered to contain duplicated source sections before review/effect. It is preserved as defective non-reviewable provenance, NOT reused.
- V4R rebuilt independently from immutable V3, without overwriting V1/V2/V3/V4. Git blob pins bind the V4R runner and module to the launcher.
- Distinct earlier GitHub ref/CAS experiment `CAS-REF-FIXTURE-20261102-001` is a **positive synthetic provider API** result only; it does not prove an authoritative off-host exclusive claim for a live SQL attempt.

## Source repairs and verification ceiling
- F004: private data/config directory SDDL now marks owner/SYSTEM ACEs inheritable; receipt still uses single CreateFileW CREATE_NEW with protected ACL. Dolt-created `privileges.db` checks permitted owner/SYSTEM identities and trusted private parent without wrongly requiring protected child DACL. **Native Windows ACL, P/Invoke and reparse races NOT tested.**
- F009: removed obsolete FileMode.CreateNew expectation; static test asserts atomic private receipt API, Git blob identities, stage classification, JSON schema, owner ACL and fail-closed trust anchor. Direct JS source inspection of frozen files: 16/16 structural checks passed; this does NOT equal running Python unittest or Windows parser.
- F010: separates an in-flight child (`UNKNOWN_EFFECT`) from previously exited stages followed by a later failure (`FAILED_OR_PARTIAL_SQL_EFFECT`), recording last exit and confirmed stage count. No automatic kill/cleanup/retry. Real process/PID durability and provider join not proved.
- F001: signed grant subjectBlob must match the runner's exact Git blob; grant and reconciliation subject IDs must agree. **Signer key remains deliberately unprovisioned**, no authority grant.
- F002/F006: signed reconciliation declares off-host CAS observation/original receipt join, but is **not a direct authoritative provider observation**. An external Control-owned claim and original-effect reconciliation remain missing; neither field boolean nor synthetic Git ref test confers authority.
- F003/F008: bounded I/O and stdin-only synthetic secret preserved; no native deadlock/redaction/telemetry proof.
- F005: Tailscale status is conservative and fail-closed but Windows schema/version and full exposure inventory remain unobserved.
- F007: JSON single-row preservation with -NoEnumerate, explicit rows-array restriction; Dolt v2.2.0 Windows data/readback NOT run.

## Mandatory next steps
1. Independent SOURCE-ONLY IR of this exact immutable V4R commit; do not claim zero advisories from implementer assertions.
2. Separately approved **non-SQL** Windows parser, C# interop compile-only, scratch ACL/reparse, listener/Tailscale read-only tests with exact original receipts, preferably materialized via existing GitHub/XFORM source pathway and only an already-determined bounded runner on Commander. No exploratory/editing Commander.
3. Competent Control must separately qualify a **real signer trust anchor**, off-host atomic exclusive claim/lease and original provider attempt reconciliation; no self-signed JSON/hash or inferred authority.
4. A future **specific one-time experimental SQL grant**, after source/host/claim review, is prerequisite for a disposable Dolt effect. None is supplied here. Do not run SQL, Dolt init/server, Tailscale Serve, or native Beads graph from this source-only publication.
5. Full 047B interhost, outage, auth/negative, backup/restore and RPO/RTO empirical DoD remains unproven. `HOST_INDEPENDENCE_INCOMPLETE`. Product `State_Kernel.final_disposition=UNDECIDED`; #34 CLOSED_PASS and #35 H6 independent.
