# TS-BEADS 047B — SECURE_HOST_PROVISIONING — bounded implementation contract

**Authority:** User experimental authorization 2026-11-01; `EXPERIMENTAL_CONTROL_ONLY`; Product authority and effects NONE.
**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`.
**Responsible owner:** notebook `DESKTOP-DJLBEQH`, Commander device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2`.
**Peer:** desktop `DESKTOP-3LJ0E54`, Commander device `777b57a0-70df-4bd6-b9ed-f6a4998e6022`.
**Existing completed gate:** `NOTEBOOK_XFORM_MATERIALIZATION_AND_READONLY_PREFLIGHT` — original Orca terminal `term_3223128b-06b3-4205-b1c7-f952a75a17a8`, archived blob `17b5d39e9a7e02126b4b0a3f5c565598ae939548`, DO NOT REPLAY.
**Frozen base subject:** `mauedgar/ts-execution-lab@e02c611dec74ce5d2ddcd5c169f407543ef2e3c4`, branch `experiment/beads-047b-native-two-windows-20261031-001`, existing DoD `DOD.md`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.
**Terminal historical nonreplay:** 042, 045-001/002, 046 A/B, DC044, 047A-static-001/002, 047B-static, 047B notebook XFORM/read-only preflight.
**First execution purpose:** PREPARE_AND_STATICALLY_QUALIFY secure provisioning runner; leave native SQL and Serve unstarted pending independent review of security candidate, precise secret handling and effect preconditions. This is the FIRST bounded preparation of this authorized gate, NOT a reexecution of any historical attempt. No SQL effects during this preparation.

## Responsibilities

Implement only the narrowly scoped, native Windows **experimental** 047B provisioning. Reuse Dolt 2.2.0, Beads 1.3.1 and Tailscale already installed. No fresh cloud provider, no daemon, Kernel substitute, scheduler, Product dependencies or accounts. Work in a new isolated staging directory/repository worktree, not Product `mauedgar/tecnotron-ai` or its TaskCycles.

Before implementation, verify frozen references, native input receipt, owner/host identity and absence of a newer or conflicting `ExecutionAttempt`. If any of these cannot be established, fail closed and report the exact missing evidence.

Stage 1 (this OpenCode2 run):
1. Read existing lab DoD and execution contract, identify original grant/operation/host and original terminal results.
2. Produce a **bounded nonsecret provisioning runner candidate** plus strict static/negative tests and an operator procedure. Do not run a Dolt SQL server, do not invoke `dolt sql` to mutate state, and do not enable Tailscale Serve during Stage 1.
3. Strong stop conditions for the future effectful invocation: Windows-only notebook and correct device/host; correct Dolt 2.2.0 and Beads 1.3.1; authenticated tailnet peer; port 3307 vacant; no SQL listener, Tailscale Serve config or existing `%LOCALAPPDATA%\TS-BEADS-047B` directory; no ambiguous prior write or second primary; no Product DB path. Do NOT treat an absent file as proof of no external effect. Probe provider state and original receipt first.
4. Carefully design a **secure secret flow**. Generate random high-entropy root/writer/reader credentials locally using OS CSPRNG, protect with Windows user-scoped DPAPI or Credential Manager (document caveats for unattended execution), restrict local secret storage ACL, and NEVER put plaintext in chat, Git, Commander arguments, shell history, logs, transcripts, environment values returned by a tool, or output receipts. Prevent PowerShell verbose/transcript logging of SQL secrets and ensure errors do not echo queries.
5. Account for Dolt's default **passwordless `root@localhost`** created when privilege tables are uninitialized. Require hardening and testing of **all** relevant root/anonymous accounts and protected `.doltcfg/privileges.db`. `dolt sql` on local OS may have superuser powers independent of SQL grants: document the OS-user isolation limit and never claim a SQL read-only user blocks a privileged local Dolt CLI.
6. Before any private ingress, Dolt listener must be strictly `127.0.0.1:3307` with an isolated empty experimental data root. Configure a dedicated `ts047b_writer` scoped to `ts047b_beads` and separate SELECT-only reader. Positive and negative SQL tests must pass in loopback, including anonymous/root-passwordless denial, wrong password, writer scope, read-only mutation denial, and no public listener. Avoid unsupported MySQL dialect assumptions; verify CLI syntax against *pinned* Dolt 2.2.0, not just current docs.
7. Only **after** the localhost hardening and auth tests pass and an independent review authorizes the frozen effectful runner, permit private Tailscale Serve TCP forwarding with least-privilege tailnet ACL. NEVER Tailscale Funnel, `0.0.0.0` binding, router forwarding, unencrypted/public exposure, new cloud subscription or automatic host promotion.
8. Design deterministic `integrity/parser checks → host/provider preconditions → once-only conditioned effect → postconditions → compact terminal result`. Explicit execution attempt ID, owner, immutable hashes, boundary, role and expected receipt. Fail closed without re-dispatch after `UNKNOWN`; for partial effects preserve state and original receipts rather than cleanup or retry. Do not make claims about backup, graph concurrency or full host independence.
9. Tests must exercise parser/integrity, stale or existing lab directory, occupied port, alternate host, absent/unprotected secrets, incorrect ACL, unexpected Tailscale Serve, reentry and synthetic failed SQL auth. Validate negative paths **without starting live SQL**.
10. Document exact state/risks and publish the candidate/test report in **experimental** GitHub lab or Transport (never Product). Do not publish any secret or pairing token. If no reliable local secret and auth flow exists, return `BLOCKED_PRECONDITION` and stop.

## Review/stop

The user has authorized the secure provisioning dependency, **not** unlimited retries, unrelated adoption, Product change or silent service exposure. This first execution is an implementation/static-qualification substep. Return an immutable candidate and tests so ChatGPT Web can carry out independent review and only then evaluate effectful invocation under the existing grant.

**Expected return**: source commit/tree, candidate hash, parser/tests/negative test counts, exact host/ownership, whether original SQL/Serve remained untouched, limitations, and the next safe mechanical action or blocker.

**Relevant provider docs:** https://www.dolthub.com/docs/sql-reference/server/access-management/ ; https://www.dolthub.com/docs/sql-reference/server/configuration/ ; https://tailscale.com/docs/reference/tailscale-cli/serve .
