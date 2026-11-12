---
artifact_id: TS-EE-ORIGINAL-GIT-GUARD-A03-HARDENING-v1
owner: TS_EXECUTION_ENGINEERING_NONPRODUCT
class: EXPERIMENTAL_SOURCE_REPAIR_CANDIDATE
status: NOT_YET_NATIVE_QUALIFIED_OR_INDEPENDENT_REVIEWED
date: 2026-11-11
product_effect: NONE
---
# Original Git process boundary hardening — inherited PR23 A03

## Source authority and exact scope
The earlier TS EE PR23 IR001 source review confirmed A03: original early Git subprocess guard inherited mutable GIT_CONFIG_*, GIT_EXEC_PATH, other Git environment and inherited PATH, and used subprocess.run(...PIPE...) with unbounded stdout/stderr collection. Subsequent PR25/26/27/28 source reviews did NOT repair A03. The PR28 original independent IR001 terminal RECOMMEND_BOUNDED_NONPRODUCT_EE_SOURCE_ONLY, FULL_SOURCE 8/8 0 confirmed findings/0 actionable PR28 source advisories, is immutable at mauedgar/ts-execution-transport@65bdf675b97d559118917cec71f0154482dd31c5:results/TS-EE-GITHUB-NATIVE-PR28-WEBINLINE-IR001-20261111-001/ORIGINAL.md. No prior original CI or review is rerun or rewritten.

This **new distinct nonProduct** source candidate branches from frozen PR28 HEAD aa31a86ea172235e7cac3d48820706320e61778a and modifies ONLY tools/ts_ee_original_actions_binding.py, tools/selftest_ts_ee_original_actions_binding.py and this contract. No Product or physical A02 source/effect changes.

## Hardening contract
- Linux GitHub-hosted ubuntu-24.04 runner ONLY: the guard fails closed elsewhere rather than assuming arbitrary host Git semantics. Require installed /usr/bin/git as the exact executable; no inherited PATH search, shell, or Git executable helper path.
- Supply an explicit allowlisted child environment with fixed PATH, HOME, XDG_CONFIG_HOME, LC_ALL, GIT_CONFIG_NOSYSTEM, GIT_CONFIG_GLOBAL/SYSTEM, GIT_ATTR_NOSYSTEM, GIT_TERMINAL_PROMPT and GIT_OPTIONAL_LOCKS. Do not import caller GIT_CONFIG_COUNT/KEY_*/VALUE_*, GIT_EXEC_PATH, GIT_TRACE*, Git prompt/config/alias options, HOME or other unexpected variables. Disable fsmonitor and hooks for every internal Git invocation.
- Use a new process group, stdin DEVNULL, stdout/stderr pipes observed with selectors. Bounded 15 second monotonic deadline across process startup/reads/exit, 65536-byte maximum for short textual Git outputs, 4096-byte maximum for marker content and 16384-byte maximum for stderr. Output is never dumped to logs. Oversize, invalid UTF-8, nonzero exit, missing binary, unsupported platform and deadline overflow BLOCKED_PRECONDITION. Kill the new process group and reap the child after timeout/error, never kill unrelated processes or retry.
- The guard's earlier semantic checks remain: original GitHub SHA/ref/run attempt 1, exact single parent, frozen source parent/tree, exact only added marker path, workflow blob unchanged and original external request. Product/Developer authority is a SEPARATE immutable Control decision; marker JSON never self-grants it.
- Existing source selftest must still pass its original one positive and nine negative cases plus an environment-tampered positive and seven negative hardening checks (real oversized Git object, oversized stdout/stderr, nonzero child exit, invalid UTF-8, shortened injected deadline and missing trusted Git executable). The tests use disposable temporary Git repositories and synthetic injected subprocess programs, NOT an external Product or physical host, and assert exact fail-closed codes.

## Qualification / stop
A NEW isolated source parent, immutable external Control request, marker-only Actions dispatch, native Python3.15.2 positive+negative suite, actual qualified Git guard invocation, terminal provider native run/job/receipt and independent STRICT_READ_ONLY source review are mandatory before claiming the inherited A03 repaired. None of these may repeat PR28/PR23 original CI/IR; use a unique ExecutionAttempt and create-only result. Do not equate synthetic unit PASS with Product integration or an Independent Review PASS. Fail/UNKNOWN requires original identity/effect reconciliation, never blind retry.

No Product/Neon/notebook/PG16 role/SQL/physical A02 effects. PA01–PA04 and physical A02 remain BLOCKED; Beta Run008 and Kernel replacement NO_GO.


## IR001 disposition and isolated 2026-11-12 successor (not historical rewrite)
The original PR29 IR001 is terminal NO_RECOMMEND: F01 MEDIUM (local .git/config and replacement-ref trust), A01 LOW (superseded historical A001 workflow), A02 LOW (adversarial coverage). Original A001 FAILURE, A002 native SUCCESS, and their original receipts remain immutable. A distinct stacked successor branch fixes source only:
- Explicitly requires a normal non-symlink .git directory and an allowlisted local Git config profile limited to inert checkout core, origin and branch bookkeeping, with bounded strict UTF-8 parsing. Reject local includes, executable hooks/fsmonitor settings, unusual sections, object alternates, grafts, config.worktree and metadata symlinks. Trust is CONDITIONAL on a frozen isolated actions/checkout source, not authentication of arbitrary repositories. Unrecognized checkout config blocks the new qualification rather than silently broadening trust.
- Set GIT_NO_REPLACE_OBJECTS=1 and GIT_NO_LAZY_FETCH=1 in minimal Git child environment; kill original process group on exceptional exit even if direct parent exited.
- Add local config poisoning, alternate objects, symlink, replacement ref, descendant-held-pipes and selector-failure tests; original A002 suite remains unchanged in its historic Git commit.
- Remove the obsolete A001 workflow from successor integration candidate; retain historical original commit/receipt via immutable Git provenance. Keep predecessor PR29 DRAFT and unmerged.
- New source qualification uses unique branch, original ExecutionAttempt and frozen request; native CI success cannot substitute for a new independent review. No Product or physical A02 effect, Kernel/Beta Run008 NO_GO.

## A003 original failure and diagnostic isolation
The immutable A003 Actions original at https://github.com/mauedgar/ts-execution-lab/actions/runs/43158162462, job 130982847793, attempt 1, completed FAILURE. Native logs show checkout and AST parse PASS, original metadata precondition BLOCKED at UNTRUSTED_GIT_OBJECT_REDIRECTION (prior aggregate code), and Python 3.15.2 tests SKIPPED. Exact terminal receipt: mauedgar/ts-execution-transport@267cb2095b695e3ba0c6b1c8339eecd56344cb32:results/TS-EE-A03-GIT-METADATA-QUAL-20261112-001-A003/ORIGINAL_RUN_RECEIPT.md. This is an accepted fail-closed stop, not CI qualification. No original rerun or Product effect.

A distinct diagnostic successor instruments which metadata redirect precondition failed, preserving refusal for all four paths. It logs only existence booleans and aggregate config section categories (never config values, tokens or object bytes) before the guard. No trust relaxation is authorized by this diagnostic. The A003 marker and original workflow are removed only from the successor's net source tree, not history. New unique frozen request and one original qualification are needed. No physical A02, Neon, SQL, host, Product or Kernel effect.

## A004 observed checkout artifact — constrained inert worktree configuration
The terminal original A004 GitHub Actions https://github.com/mauedgar/ts-execution-lab/actions/runs/43158954839, job 130985365852, run_attempt 1, confirmed config.worktree PRESENT, other redirections ABSENT; root local Git config section categories core, remote, gc, branch, without extensions. Source-qualification stopped with UNTRUSTED_GIT_OBJECT_REDIRECTION_WORKTREE_CONFIG; CPython suite NOT_RUN. Original receipt: mauedgar/ts-execution-transport@826f43fa42d1a76a3cd70fbee8b21ee27ec29f56:results/TS-EE-A03-GIT-METADATA-QUAL-20261112-002-A004/ORIGINAL_RUN_RECEIPT.md. No replay.

Git documentation: config.worktree is read only if extensions.worktreeConfig is enabled. We retain a strict allowlist that rejects ALL [extensions] in the root local config. Under this proved precondition, checkout's config.worktree is inert: allow bounded regular file up to 4096 bytes, reject symlinks, while alternates/grafts/commondir stay forbidden. Tests explicitly exercise inert positive, enabled extensions negative, symlink and oversize negatives. This is not unrestricted trust of local Git metadata. Next distinct A005 workflow removes the one-time diagnostic step, uses frozen parent/tree/workflow/marker and independent source review if qualified. Product/physical A02/Neon/SQL/host effect NONE.
