# TS Execution Engineering — Risk-Adaptive Product Delivery v1

- Document ID: TS-EE-RISK-ADAPTIVE-DELIVERY-20261114-001
- Status: candidate / method proposal under Developer's 2026-11-14 authorization
- Owner: TS Execution Engineering (HOW); consuming Product Control: FitFlow only
- Baseline: `ts-execution-lab main@099a82cd167b8943a13cbf813533339bd3645ac9`
- Authority: NO Product acceptance, Product semantic change, TaskCycle mutation,
  independent-review adjudication or beta grant.

## Purpose

Reduce process cost without removing source/effect integrity. The 2026-11-14
Developer ruling accepted five reforms for FitFlow as a bounded delivery
experiment: risk-weighted acceptance; one stable-candidate independent review;
explicit delegation of routine mechanical steps; small independent PRs; and
only functionally relevant infrastructure dependencies.

This method does **not** automatically propagate to Aware, Attendance,
Tecnotron or TS Remote State. Each Product Control adopts its own risk matrix.
Preserve existing TS EE execution/Orca/Commander/receipt rules where not
explicitly superseded by a competent Developer instruction.

## Risk-adaptive execution contract

1. Before dispatch, record Product, exact task/attempt, immutable source, owner
   of write-set, acceptance/CI gates and original output destination.
2. Allow `LOW` documentation/fixtures and isolated tests to use narrowly
   delegated deterministic validation and bounded integration **only if the
   Product grant covers the exact mutation**. A generic "autonomy" or IR PASS is
   not merge authority.
3. For `MEDIUM` changes, require exact-SHA relevant CI and a competent
   independent *final* semantic review of a stable candidate. Allow tracked
   nonblocking LOW/MEDIUM advisories only per Product disposition.
4. For `HIGH` security/session/DDL/retained-data changes, retain negative
   HTTP/DB tests and independent security review; never waive material safety,
   integrity, authentication or data-recovery conditions for speed.
5. Once a reviewer has inspected a frozen exact subject, record the original
   verdict and receipt; new source revisions are distinct subjects. Do not
   relaunch an identical review, poll Commander, alter UNKNOWN or fabricate
   a PASS. Prefer incremental deterministic checks while editing, then one
   complete final semantic review per stable composition.
6. Prefer two truly independent workers. OpenCode2 local execution must use a
   **visible Orca terminal** on the authorized Windows/WSL host and worktree.
   Codex Cloud is optional/experimental until its source/task/receipt binding
   is qualified; never an automatic choice or paid OpenAI API assumption.
7. Use GitHub native branches, checks and append-only evidence. Never mix
   multiple simultaneous writers of API contract, auth routes, migration,
   lockfile or Git ref. A nonforced merge needs a current target/ruleset check
   and the Product acceptance/grant required for that scope.
8. Introduce no new dependency on TS Remote State, Tecnotron Core or an
   unqualified host simply to deliver an unrelated Product vertical.
   Reuse existing FitFlow R002–R006 staging procedures.

## Observability and outcome

Measure time-to-integrated-functional-vertical, not number of reviewer rounds.
Capture (a) elapsed task→merged, (b) exact E2E PASS/FAIL/NOT_RUN,
(c) CI/IR cost, (d) mandatory vs avoidable gates, (e) Developer decision count.
Stop the experiment if this policy causes a security or data-integrity
regression. No override of `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md`
for provider-native identity, frozen effects, no-blind-retry or Commander scope.

## Handoff

Consumer FitFlow policy counterpart:
`mauedgar/FitFlow:docs/operations/fitflow-exceptional-delivery-v1.md`.
FitFlow Control 013 paused with PR107/PR109 frozen and terminal PR109 IR005
`CONDITIONAL_RECOMMEND_A1_ONLY / 4 OPEN advisories`; no retroactive closure.
A future Control must reconcile its original attempt before new execution.
