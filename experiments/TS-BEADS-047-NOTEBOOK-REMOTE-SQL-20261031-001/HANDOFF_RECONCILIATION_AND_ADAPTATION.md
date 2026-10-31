# TS-BEADS — Competence and handoff reconciliation for live SQL 047

Date 2026-10-31. Scope: TS-BEADS / TS Execution Engineering. Authority: EXPERIMENTAL_CONTROL_ONLY. Product authority NONE.

## Source and authorization
- User-provided continuation handoff interpreted as **experimental instructions / an authorization within the existing experimental responsibility**. It is NOT a Product canonical ruling, developer acceptance, taskcycle grant, policy override, or a command to repeat historical attempts. User may adapt experimental infrastructure, staging, providers, subgoals and fixtures while preserving authority and terminal evidence.
- Primary research source: `mauedgar/ts-execution-lab@02b1f5e4fff891286b233b01c78ee5783eb8182c:reports/TS-BEADS-HOST-INDEPENDENCE-RESEARCH-20261031-001.md`, blob `93f7e082c5856deb3e6c02a9f3fd016e41e8776e`, classification `RESEARCH_ONLY / INTERHOST_EMPIRICAL_INCOMPLETE`.
- Product SOT remains `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`; no Product write.
- Evidence already terminal and not to replay: 042 parallel without Kernel (one host); 045 real SQL/server mode single host `41177022889`; 046 cross-host native cold restore `41210661485`; independently DC044 read-only Dolt Git remote from two hosts `41177310449`. No equivalence between these individual PASS and entire goal.

## Disposition: divide one original goal into competent observable subresults; do not add Product gates
| Original handoff need | Evidence as of 047 preparation | Experimental disposition |
| --- | --- | --- |
| Two hosts, live single remote SQL store | 047 source/workflow frozen, notebook native Dolt/Beads installed, private tailnet not authenticated | **PENDING_EXTERNAL_TAILNET_AND_CREDENTIALS** |
| Native issue/dependency/readiness, no Kernel | 042, 045, 046 partly demonstrate; 047 runnable candidate for simultaneous external writers | GO only for prior bounded scopes; live interhost incomplete |
| Host A loss, B resumes without A workspace | 046 proved *clean ended host A* + cold restore from original remote backup; 047 live writers have no forced host interruption yet | INCOMPLETE for live host interruption |
| Real provider original receipt / UNKNOWN no replay | No original in-flight provider uncertain effect tested; a stored read-only provider 045 reference is not such a test | INCOMPLETE; preserve UNKNOWN and do not dispatch duplicate |
| Negative perms/concurrency/partition/revoke/read | 045 restricted SQL reader on one loopback host; 047 plans shared SQL and read-only denial | INCOMPLETE; cannot claim 028 privileged-writer confinement |
| Native off-host backup and clean restore under actual notebook failure | 046 cross-host native Dolt artifact restore, not notebook's operational DB backup; no 047 external destination provisioned | INCOMPLETE; no automatic promotion; RPO/RTO unmeasured |
| Custom Product modules absorbed, NET code eliminated in lab | Prior read-only footprint: three Product classes 85,014 bytes, Product deleted bytes 0 | Inventory only; **actual net deletion = 0**; don't claim theoretical footprint as savings |

## Architecture adaptation (valid within experimental authority)
- Select **self-hosted Dolt SQL primary on user's available Windows notebook**, Tailscale private TCP ingress (no public listener), two independent GitHub Actions runners, native Beads 1.3.1; native Dolt 2.2.0, all scoped to fresh lab data. No cloud hosting invoice. Fully runtime-configurable endpoint. This is an instance of researched Option A/C, without adopting a new Product component or making notebook an authority provider.
- Preserve **single-writer source of truth** for the Dolt service. Beads' concurrent clients can use restricted permissions but do not become two SQL primaries. Backups retain native Dolt history; GitHub/Transport original receipts stay separate.
- **Exceptional notebook disconnect:** clients fail closed and do not rewrite their work into an embedded store; never promote an obsolete backup concurrently with a returning primary. A physical notebook loss with no off-host backup does not meet disaster recovery.
- Distinguish **047A live shared SQL** from further bounded experiments (actual host interruption / original provider UNKNOWN / negative alternate writes / backup restore and RPO/RTO / measured module deletion). Those independent dependencies must be frozen separately if necessary, and cannot retroactively change 047A results.
- Full verdict `HOST_INDEPENDENCE_GO` only after entire requested DoD is proved, including cross-host recovery and provider reconciliation. A partial `PASS_TWO_INDEPENDENT_HOSTS_NOTEBOOK_LIVE_SQL_WITH_LIMITATIONS` can only support `HOST_INDEPENDENCE_INCOMPLETE` for the overall goal. No Product adoption or #35 effects.

## Corrective static preflight findings, before first SQL dispatch
- C001: original 047 code used a plain SHA256 of private endpoint. If it is a Tailscale 100.64/10 IP, offline enumeration can reveal it from publicly readable receipts. Use a keyed HMAC based on existing strong SQL credential (not serialize key or endpoint) or remove the host fingerprint.
- C002: original 047 native metadata tarball could include the runtime SQL hostname in `.beads/config.yaml` or `.beads/metadata.json`. Sanitize with explicit structured parsing and reject any credential or private endpoint in the portable artifact before GitHub upload.
- C003: original 047 catch-all classified errors `FAIL_CLOSED_ORIGINAL` even after a write might have committed before a network error. This is a concrete **UNKNOWN** semantic bug. Mark write-intent *before* each remote native mutation, preserve original provider identities, and stop with `UNKNOWN_RECONCILIATION_REQUIRED` when post-commit certainty is absent.
- C004: current 047 script uses a read-only direct SQL denial; test a Beads CLI write attempt under the read-only user as a separate negative fixture, and evaluate privilege exposure in the actual SQL account. Native server-mode CLI access cannot be equated to SQL account confinement without this.
- C005: original handshake/DB init semantics and metadata portability remain empirically unproven against actual remote notebook; do not claim static PASS validates them. Keep first live execution frozen and require full independent review before any production acceptance.

## Current stop
No live 047 GitHub dispatch (sentinel absent); Tailscale notebook login observed NeedsLogin; no scoped SQL credentials or remote SQL service yet provisioned; host-onboarding is a user-held dependency. Do independent code/negative-fixture/static validation in the lab only while that dependency is pending. Preserve terminal earlier runs and no automatic retry. Product Kernel actual deletion 0. Overall `HOST_INDEPENDENCE_INCOMPLETE`.
