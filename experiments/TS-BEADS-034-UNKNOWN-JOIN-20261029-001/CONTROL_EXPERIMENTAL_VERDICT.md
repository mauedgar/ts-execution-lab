# TS Beads 034 — experimental terminal control disposition

**Identity:** TS-BEADS-034-UNKNOWN-JOIN-20261029-001
**Authority:** EXPERIMENTAL_CONTROL_ONLY, user-authorized B-first research; no Product TaskCycle or Developer acceptance.
**Verdict:** PASS_B_FIRST_UNKNOWN_TO_CONFIRMED_REAL_PROVIDER_READ_ONLY_JOIN (26/26 checks PASS). Terminal; NO REPLAY.

## Exact observed source and original evidence

- GitHub Actions experimental runner [40931812435](https://github.com/mauedgar/ts-execution-lab/actions/runs/40931812435), job 123651911617, attempt 1, head/source `045e795100d8eb9631147b1290e9ca4ae386231c`, `completed/success`.
- Original result published by same job as `mauedgar/ts-execution-lab@c693603fc44227062751030fd5f93c5f95b3d365:transport/TS-BEADS-034-UNKNOWN-JOIN-20261029-001/EVIDENCE_CARRIER.txt`, Git blob `81a34a4e2a7de6cae5919b2dc6e3728051a94685`, TXT carrier 8500 UTF-8 bytes, SHA-256 `562a71a725d087d426bead89c4eaad5dcb29475bb6c406e29d1592a6653e88ca`.
- Product-qualified `IR-TXT-CARRIER/1` project/verify/extract with 3 members and byte-roundtrip PASS (read-only reused exact tool from frozen Product).
- Original `original/RESULT034.json` recovered from carrier and corroborated by native logs: 26 PASS. No other 034 provider artifact published.

## Reused real provider effect, never replayed

The only target provider effect is terminal **033**: original run `40930288498`, job `123646594227`, source `eebf8e72b83df5aed61416ffc0fa81e84fdf55ea`, attempt `TS-BEADS-033-PROVIDER-20261029-001/ATTEMPT-001`, artifact `12921817863`, ZIP digest `sha256:329d05a218ea04dd740ab1579aed31d00a3f110700670e4d380993a0bde98dc6`, request hash `350fb2c516c5ae94cf34cac7c38f5ea10ef11e3d715bf35826dadbce25dfdfe2`.

034 queried only provider-native GET endpoints for the exact 033 run, job, artifact metadata and artifact ZIP. It downloaded 477 bytes, rehashed the actual ZIP, extracted and validated the internal receipt and source/attempt/run/operation/request identity; malformed attempt, run id, hash and source were rejected. **No retry or dispatch of the 033 provider effect.** GitHub Actions run 034 itself is a real *test execution*, so `new_provider_effect=NONE` in the original result refers to **new 033-like application/provider operation effects**, not to absence of the 034 CI run.

## B-first native lifecycle recovered

A disposable isolated Beads v1.3.1 embedded Dolt store was created with no Git remote; per-write Dolt auto-commit enabled, auto-push off. One synthetic native issue representing the exact 033 attempt initially recorded effect state `UNKNOWN` and `reconciliation_required=true`. A separate Python process with separate native CLI calls observed the unchanged UNKNOWN, independently reobserved the exact original provider evidence, then committed `CONFIRMED` with identity-bearing `result_ref`. Another fresh process verified CONFIRMED and native historical replay via `bd history` and `bd show --as-of` for both UNKNOWN and CONFIRMED.

- Native Dolt before: `ncdjhqe1a3f0695qob6bsp3mrnigtp57`.
- Native Dolt after: `evv91m0cmq4avnu0bn3ktf6lhp7vcoq0`.
- Explicit experiment caller guard refused a *hypothetical* second attempt while UNKNOWN. No second native attempt/dispatch was executed. The guard is not a Beads-native permission or concurrency guarantee.
- No Product or shared remote Dolt writes. The disposable native Beads DB was not promoted or synchronized to a persistent shared server. Durable proof is TXT/Git, not a migrated state store.

## Precise capability frontier

**Qualified experimentally:** real, previously executed external provider receipt verified by exact native API/artifact bytes, fresh-process recovery of UNKNOWN to CONFIRMED in native Beads history, bounded no-retry caller policy.

**NOT QUALIFIED:** actual external lost ACK/timeout; two competing workers with stale CAS; privileged native alternate writer exclusivity; native Beads enforcing authority/attempt uniqueness; global Product Kernel revision/hash-chain/event_count equivalence or feature parity; cross-runner remote Dolt; Product migration, retirement or Phase 2.

**Architectural hypothesis (not adopted):** native Beads scoped causal state/history + provider-owned immutable receipt and identity + Control-managed retry/authority. Capabilities and invariants matter; no obligation to recreate Kernel internals or a second mutable ledger.

## Next independent B-first research

035 (not initiated): **causal write exclusivity / alternate-writer adversarial boundaries**. Start read-only with exact published Beads native APIs and native ACL/privilege options; if destructive or privileged fixtures remain blocked, document limitations rather than evading safety. Test protective caller CAS under disposable unprivileged isolated store only when viable and no shared writes. Preserve UNKNOWN no-replay.

Product remained `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`. Shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` (postflight required separately).
