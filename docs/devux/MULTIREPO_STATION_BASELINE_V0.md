# TS Dev UX — portable multirepo station baseline v0

Date: 2026-10-15. Status: TECHNICAL_CANDIDATE (not accepted Product policy).
Authority: TS Execution Engineering mechanics only. Does not select TaskCycles, grant Product acceptance, advance Upper LC, adopt Beads or replace a repository Source of Truth.

## Ownership
- FitFlow owns its domain, API, Python 3.11 baseline, dependencies, tests, migrations, Product Profile and CI.
- Tecnotron owns the AI Core/runtime contracts and its own Product decisions.
- Git is authoritative for repo/commit/tree/branch/write-set.
- Orca owns local workspace setup, native host runtime, terminals, session UX and mechanical Git worktrees.
- OpenCode is a replaceable agent provider. Inference and semantic independent review require separate exact qualifications.
- ChatGPT Web coordinates within competent Developer/Product grants; Github Issues/Projects are projections, never automatic authorization.
- TS Execution Engineering provides deterministic runners, independent result verification, identities and durable joins. Transport carries receipts, not Product state.
- Beads remains separately experimental; no migration, authority, mandatory dependency or Kernel replacement assumed.

## Logical station roles (no canonical absolute host paths)
FF_PRODUCT: mauedgar/FitFlow, separate task worktrees, qualified Windows Python 3.11+frontend; no Product changes in primary checkout.
TS_AI_CORE: mauedgar/tecnotron-ai, native Linux ext4 checkout for compiled Node modules; Windows checkout is navigation only until repaired.
TS_EXECUTION_LAB: mauedgar/ts-execution-lab, technical recipes and qualified infrastructure.
TS_EXECUTION_TRANSPORT: mauedgar/ts-execution-transport, durable exact results and handoffs.
TS_STATION: neutral non-Git local user folder with nonsecret paths and selected active provider host.
Separate local station profile example: examples/devux/station-profile.example.yaml.

The current notebook DESKTOP-DJLBEQH is selected as local execution host. The original desktop DESKTOP-3LJ0E54 is excluded from new dispatches, but that restriction is not enforced as remote provider ACL, revocation or shutdown. Neither hostname becomes Product doctrine.

## Validated notebook environment (not universal mandate)
Ubuntu-24.04 WSL2 user tsops; WSL native checkout /home/tsops/workspaces/tecnotron-ai. Orca uses UNC path to the same checkout. Tested Orca 1.4.224, terminal creation against the WSL repo WITHOUT forcing --shell: provider selected hostPlatform linux, tsops, pwd, Node22.23.3, npm10.9.9, exact Tecnotron commit f40236d24023159bc38aca06b3fa3862ac62608c.
Windows FF: uv0.13.1 managed Python3.11.17, 56 packages installed from unchanged lock; FF 50/50 unit tests with ephemeral synthetic configuration and frontend build PASS.
TS Linux: 108 native npm packages, 579 PASS / 6 SKIP / 0 FAIL at the frozen SHA and tree 786758a44bd4c0170d864cb1391af934b5cdc75b. Windows TS npm ci FAILED due to node-gyp; never treat its node_modules as valid Linux or complete Windows installation.
PostgreSQL16, Redis7, compiler and header prerequisites qualified locally, loopback only; no Product databases or secrets initialized.
No Docker was used to qualify local checks; this does not replace FitFlow's canonical Compose validation.

## Safe Orca mechanics
Do not copy .env between worktrees; never propagate secrets by default.
Do not run npm install / docker compose build automatically in setup hooks. Use explicit uv sync --locked (Python 3.11 minor fixed) or npm ci from committed lock only for selected work.
Never share native node_modules or virtualenv between worktrees or OSes. Reuse native per-user package download caches.
For a native WSL workspace, register its UNC root with orca repo add then call orca terminal create --worktree path:<UNC> --json with **no explicit --shell**. A successful terminal create must be followed by terminal read-back of user/cwd/runtime/branch/HEAD. For terminal send, accepted:true with provider observation unsupported does not prove command delivery; inspect terminal screen and never blindly retry.
Do not create a TaskCycle from an Orca child worktree or infer permission from a tab title.

## New-machine bootstrap, ordered DoD
1. Non-destructive host preflight: OS, WSL support, user, disk, tool provenance, existing Git checkouts, Orchard/Commander process owner, secret policy and native runner choice; fail closed on unknown effects.
2. Establish **local** nonsecret station profile (not Product SOT): roots, distro/user, active host, disabled-for-dispatch hosts, auth handled outside file.
3. Install version-pinned checksum-verified tools in user scope, preserve system Python, Node/npm ABI and native caches; no latest installers by default.
4. Clone only four selected repositories if destinations are absent. Verify origin, branch, exact commit/tree and clean status before actions; never overwrite checkouts.
5. Bind FF and TS native Orca setups with base refs selected at current Product checkout; keep TS Windows navigation distinct from native WSL. Do not run Product setup hooks merely for registration.
6. Materialize dependencies explicitly with Product lockfiles, not on every new worktree. Qualify local PostgreSQL/Redis without creating Product DB/role/secret until competent need.
7. Qualify terminal cwd/user/Node/Python, deterministic tests and output against exact commit/tree. Negative drift/write-set checks must fail closed.
8. Record bounded ExecutionAttempt, provider session/identity, expected receipt, actual result and UNCERTAINTY. Deferred durable join before retry; no extra daemon/orchestrator.
9. Qualify OpenCode real inference, reviewer independence and provider authorization separately. Qualified stored Windows credentials alone are insufficient for WSL.
10. Measure warm/cold behavior and recover Commander independently of Orca before claiming automated resilience. On a new machine, read-only preflight and bounded real first-run/rollback must pass before BOOTSTRAP_REPRODUCIBLE_PASS.

## Upper LC technical delta
Source: Tecnotron Upper LC operational maturity issue #31 and related #32/#33/#34/#35. Upper LC v1 adopted semantic; TC Core v1 frozen maintenance, not reinitialized.

Provider capability | Consumer | Guard:
- Orca project setup host/runtime, WSL auto-shell, worktreeId and terminal handle | ULC-OP-02 Actor/context/handoff | commit+tree+write-set+authority from Product, never Orca metadata.
- Orca terminal send/terminal read --screen | ULC-OP-02 evidence | accepted input != delivered, verify output and process incarnation; no blind resend.
- Distinct FF and TS worktree checkout/owner | H6 multi-TaskCycle | one owner per path/write-set; no inferred TaskCycle from UI.
- GitHub Projects Ready/Done and Actions results | ULC-OP-03/06 | typed provider receipts and competent Product grants only; not status-driven acceptance.
- OpenCode provider | ULC-OP-02 | qualify Linux auth+synthetic inference+scope, not assumed from Windows.
- Beads potential coordination | future separately adopted work | experimental only, do not migrate Product state.

No new state, grant, recipe, role, orchestrator, Kernel migration, acceptance or control ownership is introduced by this baseline.

## Remaining non-PASS qualifications
Native WSL OpenCode inference/agent isolation; original Windows OpenCode synthetic smoke has unresolved running effect and must be reconciled before retry. Commander independent lifecycle from Orca; canonical FF backend integration/database gates; cold/warm caching measurements; CI/Actions optimizations; two-agent disjoint worktrees; new-machine reproducible installer tested on another host.
Readiness: technical station ready with bounded FF Windows and TS WSL validations; FULL_PRODUCT_PLATFORM_PASS and BOOTSTRAP_REPRODUCIBLE_PASS NOT CLAIMED.

References:
- ts-execution-transport@833d0b033716a3ccad3aec20fea542e7620acb03:results/TS-DEV-UX-NOTEBOOK-DEPENDENCY-QUALIFICATION-20261015-008/TECHNICAL_RETURN.md
- ts-execution-transport@3722ef1a678158d1be0bd4be3157f87691b601b1:results/TS-DEV-UX-ORCA-WSL-BINDING-20261015-009/TECHNICAL_RETURN.md
- FF SOT docs/SOURCE_OF_TRUTH.md; TS SOT docs/SOURCE_OF_TRUTH.md and architecture-knowledge-ownership-baseline.
