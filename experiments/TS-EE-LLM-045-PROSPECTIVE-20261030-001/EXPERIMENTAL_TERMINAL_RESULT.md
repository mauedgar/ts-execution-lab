# TS EE LLM045 — Prospective independent benchmark, terminal experimental result

**Date:** 2026-10-30. **Authority:** TS_EXECUTION_ENGINEERING experimental; Product NONE. **Disposition:** COMPLETE_WITH_LIMITATIONS. No #34/#35 Product change, no TaskCycle initiation, Phase 2, model-routing adoption or Beads Product adoption.

## Prospective freeze and baseline

- Original exact input Git subject: mauedgar/ts-execution-lab@93838b18e9e04ee814e261e7fee409b9f12da547 (all 4 Orca worktrees started on this commit).
- DoD, two contracts and tests: experiments/TS-EE-LLM-045-PROSPECTIVE-20261030-001/DOD.md, cases/recovery and cases/ready.
- Independent oracle frozen **before first model invocation** in the exact original subject; oracle/recovery.test.mjs Git blob d1c74afa166cffdaa4bade48c23a09f6bec9d29a; oracle/ready.test.mjs Git blob d5ac32f48a1c87222a075e9c9cb760eb4ee8be4a. Read allowlists explicitly did not expose these oracle files to coding agents.
- Original expected-red baseline [GitHub Actions run 41115875432](https://github.com/mauedgar/ts-execution-lab/actions/runs/41115875432), attempt 1, completed/success; original logs artifact 13005457556, artifact digest sha256:47d3f30e1ab7dab0c644256f5343a92d33b384e0871e236b2adcb5388f0e46a2. Both initial stubs fail expected tests. No model inference in baseline.
- Scope: case A pure function recoverAttempt for sticky UNKNOWN, identity collision and CONFIRMED without receipt; case B pure function selectReady for DAG/conditional readiness. No real external effect invocation or provider-ACK-loss recovery was performed.

## Exact attempts and immutable original candidates

| ExecutionAttempt | Model | Case | Candidate commit | Code blob | Visible 7 | Prospective oracle 8 | Disposition |
|---|---|---|---|---|---|---|---|
| LLM045-D-A-001 | DeepSeek V4.1 Flash Free | A recovery | NONE | NONE | — | — | BLOCKED_DISPATCH_TOOL_SAFETY; no provider session/result observed |
| LLM045-M-A-001 | MiMo V2.6 Flash Free | A recovery | 27da6ce976e3873875da28ac9dee21b24be88f30 | eedbc21ac69d4b2367946ad317bee52a9160ca73 | 7/7 | **8/8** | PASS_BOUNDED_SYNTHETIC |
| LLM045-D-B-001 | DeepSeek V4.1 Flash Free | B ready | 124f10e272ce416c90f0980696d84661bf097fb8 | a1dac89fcb1a0b95f02eccecf0864d8026accca8 | 7/7 | **8/8** | PASS_BOUNDED_SYNTHETIC |
| LLM045-M-B-001 | MiMo V2.6 Flash Free | B ready | c0cea66472498e45962d0ecfdef51025a48db9d7 | 702940ba430bb5919c4a3099553f081f6b6f1a8e | 7/7 | **8/8** | PASS_BOUNDED_SYNTHETIC |

Each executed model used a separate visible Orca terminal and isolated worktree on DESKTOP-DJLBEQH, native OpenCode v2.1.0, exact free model ID and effective deny-by-default permissions. Allowed read only role-local WORK_PACKAGE.md, owned source, visible tests; allowed edit only owned source. Postflight prior to candidate commit showed exactly the permitted source changed; test sources/config untouched. Each candidate was committed once on its own branch and published without merging; native worktrees were clean after commit.

**Blocked attempt D-A:** Its first dispatch tool call was rejected by the assistant tool safety system (no accepted Orca send, provider session or original JSONL). One targeted observation found the original terminal still at preflight prompt; the expected JSONL path was absent. No retry or alternative dispatch was attempted. This is not a model-quality FAIL; nor is missing receipt universally proof no effect. Treat as BLOCKED_DISPATCH with observed absence of native effects.

Original native event JSONL files remain host-local, NOT cloud-archived; original SHA-256:
- LLM045-M-A-001: C7072BB8C4C46AECCC76FF2084AD1ECD48181D33FB9AC70B7665C190050BE091; session ses_e71b05aaaffeyUYZVSNMuDU2jt.
- LLM045-D-B-001: F83132695BD9D8240D5BA09E3A90C0DF8BFF17397882E414F449600347E568B5; session ses_e71b0379fffehr2acUmW2oWsju.
- LLM045-M-B-001: 424E25DDE292EEBA8FB5BC1895531CA021323D2A8B822A24A3E3D1F3D109D12F; session ses_e71b0fef3ffeweBlQK0vARG8dV.
These host original SHA references do not establish portable original bytes or measured model costs. No duplicate model inference, no retroactive result edits.

## Independent validation

- Independent review/validator source: experiment/llm-045-independent-20261030-001@81050f32dbe440956d8679914c5ddc456a1fb279. Static source code/commit blob hashes and two frozen oracle blobs were asserted by native Actions.
- [GitHub Actions run 41117255603](https://github.com/mauedgar/ts-execution-lab/actions/runs/41117255603), attempt 1, job 124274587273, completed/success.
- **Original visible 21/21 PASS and prospectively frozen independent 24/24 PASS = 45/45** on three original candidates; no model was run by this validator. Result original JSONL SHA-256 a09eb4a994bad8c2531b3159211cb46f447fe95a06d72ce0bf09a4c085eb04f4.
- Exact original validator artifacts: native logs 13006931292, zip SHA-256 f609599378cc302498fb5c32d2770cff05884b1937dc0e149a1f4c261edc3221; results 13006826528, zip SHA-256 3a12bb3d3ec646999994f28e452e2d21040bb92adac53ff683493a9300630a03. Provider artifact expiry 2026-11-29, so the Git-indexed report alone is NOT original artifact bytes.

## Adversarial result and limits

**Case A** exercises sticky UNKNOWN, CONFIRMED with absent receipt and identity mismatch under partially observed journal. The MiMo candidate passed all prospectively frozen cases: recovery decision logic is bounded qualified for these synthetic examples. **No real process crash, partial external write, provider result loss or durable join was injected**; those remain separate, unqualified infrastructure experiments.

**Case B** both original candidates passed the visible and hidden DAG checks. This is not a benchmark of real concurrent task scheduling or Beads multi-host execution.

Do not rank DeepSeek versus MiMo universally: only one model had a valid attempt in case A; only two cases, one attempt per binding; no calibrated cost/latency distribution. Experimental Git/Library may preserve findings; native JSONL cloud publication previously blocked by repository transport policy, do not circumvent. No Product promotion until Upper LC #34/#35 DoD reconciled or specific competent authority grants earlier adoption.

**Next research (not authorized Product):** if needed, a separate crash/ACK-loss fixture with durable provider receipt identity, native effect reconciliation, no blind retry and finite artifact retention. Preserve D-A block without relaunch. PRODUCT SOT observed tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909.
