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

## IR001 disposition and successor metadata hardening

The original PR29 WEB_INLINE IR001 terminated NO_RECOMMEND / 1 confirmed F01 MEDIUM / 2 actionable advisories A01/A02 LOW, immutable original mauedgar/ts-execution-transport@df8626b12e5767620bf9c8006b8e0b7fa6e541dc:results/TS-EE-A03-GIT-GUARD-PR29-WEBINLINE-IR001-20261111-001/ORIGINAL.md. PR29 and historical A001 failed, A002 native CI successful results are frozen, neither retried nor rewritten. This new source successor repairs these findings under distinct responsibility and identity, not retroactive PR29 acceptance.

- F01: require GIT_NO_REPLACE_OBJECTS=1 in a fixed child environment; before local Git calls, require a regular owned non-writable repository root/.git/config with 16KB bound, strict UTF-8 parse and only documented core/remote origin/branch/user sections and keys. Reject include/extension/plugin/helper instructions, symlink local config, unsafe file ownership/mode, grafts, external object alternates and present loose/packed replacement references. Trust assumption is a freshly provisioned disposable, unchanged GitHub-hosted Actions checkout and competent external native GitHub parent/tree/request reconciliation; this is not general untrusted repository acceptance. No arbitrary Product/local host repository may be passed to the guard.
- A01: the superseded A001 workflow path is absent in this integration source candidate; its original frozen Git commit, failure receipt and reviewer remain preserved.
- A02: add actual disposable Git metadata adversarial negatives (unsafe local include/fsmonitor, replacement ref, grafts, alternates, symlink, group-writable config), selector injected failure and child-process-group kill evidence. Tests remain synthetic on disposable runner, not proof of arbitrary hostile subprocesses escaping POSIX process groups.

No new Product actor/state/gate/authority; all original marker source and workflow blob logic remains, and actual GitHub source must be independently frozen and reviewed before any general technical adoption. Physical A02 P0 BLOCKED and PA01–PA04 OPEN. PR28 bounded provider binding remains a separate source IR recommendation, not an integration or kernel replacement grant.
