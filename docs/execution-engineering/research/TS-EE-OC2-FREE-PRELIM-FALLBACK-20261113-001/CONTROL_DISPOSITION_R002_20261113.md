# TS EE OpenCode2 free preliminary reviewer — Control disposition R002 (2026-11-13)

**Responsibility:** `TS-EE-OC2-FREE-PRELIM-FALLBACK-20261113-001`  
**Class:** `DEVLAB_EXPERIMENTAL_SOURCE_DISPOSITION`; **not** canonical TS Execution Engineering adoption and **not** Product authority.  
**Decision:** `SOURCE_PREPARATION_QUALIFIED_0F0A / REMOTE_EXECUTION_BLOCKED / DEVELOPER_RULING_REQUIRED`.  
**Authority:** experimental continuation within the existing grant, no Product or integration authority.
**Branch:** `mauedgar/ts-execution-lab:experiment/ts-ee-oc2-free-review-fallback-20261113-001`, intentionally isolated from main.
**Subject:** `c07112e4031ca970aff2b4054229989508379e7b`, tree `346389269fa09841d01a0a49bb3f2c4991d2b11b`.
**Source baseline:** `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`.

## Independent review chain, preserved

- IR001: `NO_RECOMMEND / 7F / 6A`, initial candidate `0288f0cb7e3f950274fbe69bd044e7a2d1c569f1`. ORIGINAL is durable in `mauedgar/ts-execution-transport@5d27d494c9ce027eb04c1a03783555723961d18e:results/TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR001-20261113-001/ORIGINAL.md` (SHA256 `e1e47e7104ce246c3742bd6729be2cad8baa54c5ae25c6d58506c3cc121ae612`).
- R002 repairs remain source-only and intentionally removed OpenCode/LLM invocation, npm installations, diff forwarding, artifacts and uncertain positive admission. They changed the Python tool and YAML workflow and clarified the operating disposition.
- IR002: `RECOMMEND_SOURCE_ONLY / 0F / 0A`, frozen request `mauedgar/ts-execution-lab@64e86a19cfb9a8baf17230882dffeb1c936ba468:reviews/TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR002-20261113/FROZEN_INPUT.md` (blob `ecc98262569f183a1aff3fd3c79dd6aaccc99c59`).
- IR002 ORIGINAL: `mauedgar/ts-execution-transport@c257072e83e3ca0ba6aa3c3c5fec95d63e8dfd70:results/TS-EE-OC2-FREE-PRELIM-FALLBACK-WEBINLINE-IR002-20261113-001/ORIGINAL.md`, Git blob `4208751a01f665e44798e37217ccabf343c01781`, exactly 8,803 bytes SHA-256 `95f5d39b7592b5738d80c6930c0012f4ea62d6799b71f65a719f77d44f465cad`. Library original file `libfile_65c2e421e9c8819185827488cdac3089`, file id `file_000000001d6881f69ff76600d10ddff0`; both original and Git readback were verified.
- Control independently reconciled the R002 Git tree directly from GitHub native Git commit endpoint: `346389269fa09841d01a0a49bb3f2c4991d2b11b` EXACT. This closes the reviewer-noted tree observation limitation without changing the semantic verdict.

## Scope qualified — and scope not qualified

**Qualified only:** a repository-isolated manual `workflow_dispatch` candidate with read-only GitHub token, fixed-source checkout `github.workflow_sha`, exact script blob pin, exact synthetic HEAD/tree/base checks, and an unconditional fail-closed preflight (exit 42). Source-only IR found 0F/0A; no real LLM reviewer is implemented or authorized.

**Not qualified:** notebook native OpenCode2 runtime permissions/negative tests; model provider/price/quotas/retention; process-state attestation and cross-host fencing; trusted notebook capacity receipts; Linux CLI/package provenance; GitHub Actions remote inference; output verdict parsing or durable semantic custody; Product data disclosure/security; real fallback equivalence. A successful source-only IR does NOT satisfy any of these.

**No model quota:** this candidate contains no model call. No OpenAI/GPT tokens, OpenRouter paid balance or external inference spent for OpenCode reviewer.

## Observed non-effects at cutoff

- GitHub `main` HEAD observed unchanged at `dc5a755cba5ffb4cb7bc6ee5995f20a27d692aa5`; workflow path absent from `main`.
- Experiment branch HEAD before this evidence commit: `64e86a19cfb9a8baf17230882dffeb1c936ba468`. Candidate source remains frozen at `c07112e4...`.
- GitHub Actions query for experiment branch returned `total_count=0`; no candidate workflow run observed.
- Independent WEB_INLINE IR002: no Actions, OpenCode, model calls, Product writes or Git modifications during review.
- No main merge, PR, deployment, Product, TaskCycle, Phase, or acceptance effect.

## Next Developer ruling — mandatory before runtime

**Proposed bounded scope:** authorize a separate **notebook-first synthetic** OpenCode2 qualification with one non-OpenAI genuinely free model and explicitly zero paid fallback. The dedicated qualification must verify effective model/provider endpoint and pricing/quotas, native hard-deny tool behavior under real attempts, exact worktree/ownership, resource admission evidence, and reliable terminal/native process correspondence. No Product implementation, no Actions fallback yet.

After notebook and trust/fencing gates are technically qualified, prepare a DIFFERENT, versioned Actions candidate with verified CLI/provenance, provider policy and output custody; new source-only WEB_INLINE IR and runtime qualification; a later Developer ruling controls actual activation. Do not transform the current ALWAYS-DENY script into a live reviewer through a configuration toggle.

If no new grant arrives, state `READY_BUT_IDLE` at this boundary. All historical attempts and UNKNOWN effects remain untouched.
