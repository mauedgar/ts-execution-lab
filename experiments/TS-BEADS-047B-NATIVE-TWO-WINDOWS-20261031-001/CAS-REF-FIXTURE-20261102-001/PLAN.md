# TS-BEADS 047B — GitHub off-host ref/CAS synthetic qualification (pre-effect freeze)

**Class:** EXPERIMENTAL_EXECUTION_ENGINEERING_ONLY. **Product authority:** NONE. **Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (same). **Single experimental ExecutionAttempt:** `TS-BEADS-047B-GITHUB-CAS-FIXTURE-20261102-001`.

## Bound subject and intended effect
- Provider: authenticated GitHub repository `mauedgar/ts-execution-lab`; **not** Product `mauedgar/tecnotron-ai`, not `refs/dolt/data`, no SQL or Beads writes.
- Exact precondition lab branch `experiment/beads-047b-native-two-windows-20261031-001@b2bb1f26206000abe61e971f51be0a7c9d4051f3`, source read-only original IR009 at `mauedgar/ts-execution-transport@9d134dac7b3fa7c64452c0b295849c43f6394472:handoffs/TS-BEADS-047B-OFFLINE-PRIVILEGE-FIXTURE-V3-20261102-001/WEB_INLINE_IR009-SECURITY-V3-20261102.md` blob `c1c7fcc34997b48b5ecd4c01c80d2605d4568d29`.
- Fresh synthetic claim branch (MUST NOT PREEXIST): `refs/heads/experiment/ts-beads-047b-cas-fixture-20261102-001`. Branch enumeration returned 0 matches at selection. Any ambiguity or conflict must block without retry.
- Conditioned effect A: create this ref once, anchored to exact original `b2bb1f26206000abe61e971f51be0a7c9d4051f3`; then fetch the exact provider ref identity. Stop on failure or unexpected SHA.
- Conditioned effect B, ONLY if A is confirmed: issue exactly ONE guarded ref update from `b2bb1f26206000abe61e971f51be0a7c9d4051f3` to frozen prior commit `ee5efa31cf9674c4f148e5ef51b710899df5c359`, requiring `expected_sha=b2bb1f26206000abe61e971f51be0a7c9d4051f3` / force-with-lease semantics. Then fetch the resulting ref, record exact sha. Do not retry B if provider effect is UNKNOWN. This intentionally moves only the new disposable claim branch; it does not touch the experimental source branch.
- Result/receipt: original GitHub API responses and immutable exact `sha` of the new branch; publish a read-only result in this lab only if observed. Never infer successful CAS from ref presence alone.

## Evidence ceiling and stop
A fresh ref creation + positive guarded update only qualifies the mechanical API path, **NOT competing-actor negative race behavior, security grants, original provider receipts, signature issuer or Beads host independence**. An immutable branch ref is not a new Product State Kernel, actor, scheduler, Ledger or work DB. No nonexistent account or secret is created.

Do not perform an intentionally duplicated create/update merely to force a conflict. The existing original 047B SQL effects remain absent/unproved by this test. No runtime SQL, Tailscale Serve/Funnel, credentials, privilege file, Beads graph, Kernel migration, #35 or Product TaskCycle effects. Later SQL requires a separate exact conditioned grant, even if this mechanical CAS test passes.
