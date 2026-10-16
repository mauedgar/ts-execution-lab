# TS — Dev UX | Notebook station profile (provisional)

> Status: **PROVISIONAL_TECHNICAL_STATION_PROFILE**, observation date **2026-10-15**. Owner: TS technical execution tooling. **Not Product SOT**, not an accepted Upper LC architecture, not a Beads adoption, not a production bootstrap, not a new Actor/Recipe, and not an authorization to run Product gates. This document is a navigational technical profile, not a new source of Product truth.

## 1. Authority and correspondence

- Product FitFlow is governed by `mauedgar/FitFlow`, normally integration branch `develop`, SOT `docs/SOURCE_OF_TRUTH.md` (observed blob `f36307af0777fd3b493792ad42115fec56ac44b3`). Product owns its runtimes, dependencies, backend/frontend, domain, migrations, tests and CI.
- Product Tecnotron is governed by `mauedgar/tecnotron-ai`, reference branch `tools`, `docs/current-state.md` (observed blob `cac3955f1040e743248f015c974bbc397edb9650`). Product owns AI Core, harness interfaces and its own tests/CI.
- Execution method belongs to `mauedgar/ts-execution-lab`, `docs/execution-engineering/TS-EXECUTION-ENGINEERING-AUTONOMOUS-OPERATING-CONTRACT-v1.md` (observed blob `3f6b7bfa40e4d4199e3d12734d3ce2e4e76989f1`), **execution semantics only; Product authority NONE**.
- `mauedgar/ts-execution-transport` is a carrier for handoffs/results/receipts, not a Product integration authority. Immutable exact evidence and observations: `ts-execution-transport@23f2235ef7119c340654099797d2c4ea0d17b45c:results/TS-DEV-UX-DUAL-PRODUCT-STATION-QUALIFICATION-20261015-009/TECHNICAL_RETURN.md`. Reobserve moving refs at any new effect.

## 2. Host routing — do not conflate with platform ACL

| Host | Routing in THIS station workstream | Commander device |
| --- | --- | --- |
| Notebook `DESKTOP-DJLBEQH` | `ACTIVE`; only eligible host for new specifically authorized technical execution | `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2` |
| Old desktop `DESKTOP-3LJ0E54` | `DISABLED_FOR_NEW_DISPATCH`; physically online may persist | `777b57a0-70df-4bd6-b9ed-f6a4998e6022` |

The disabled routing is a selection recorded here, **not** enforced access control, power-off, revocation or cancellation. An independently authorized Beads migration chat may read the former desktop under its own bounded scope. No automatic switch to the desktop upon notebook errors.

## 3. Repo-to-workspace map

| Namespace | Windows navigation checkout | Native Ubuntu WSL2 checkout | Git ref at 009 |
| --- | --- | --- | --- |
| `FF` | `C:\TS\repos\FitFlow` | `/home/tsops/workspaces/FitFlow` | `develop@3f819a2a3590de72db68ca4e1c4a268bc2323671` |
| `TS` | `C:\TS\repos\tecnotron-ai` | `/home/tsops/workspaces/tecnotron-ai` (created by separate earlier workstream; do not usurp) | `tools@f40236d24023159bc38aca06b3fa3862ac62608c` |
| Execution lab | `C:\TS\repos\ts-execution-lab` | not required | `main` (moving) |
| Transport | `C:\TS\repos\ts-execution-transport` | not required | `main` (moving) |
| Synthetic private-consumer | `C:\TS\repos\ts-execution-private-consumer` | not required | **EXCLUDED_FIXTURE**, no routine dispatch |

`C:\TS\station` is a neutral Orca station folder, **not a Git/Product SOT**. Each Git worktree and owner write-set is independent. Windows and WSL are distinct physical checkouts; no implicit equivalence from a shared `origin`.

### Orca UX and execution
- `FF | FitFlow` Windows navigation, `TS | Tecnotron` Windows navigation, and `TS | Infrastructure` neutral terminal labels are present.
- `FF | FitFlow WSL` terminal **PASS** on 2026-10-15: Orca-created terminal `term_8b777046-dfb5-4a8f-b65d-d20ff1ba1a32`, worktree `\\wsl.localhost\Ubuntu-24.04\home\tsops\workspaces\FitFlow`, `hostPlatform=linux`, native `tsops@DESKTOP-DJLBEQH:~/workspaces/FitFlow$` and `refs/heads/develop`.
- Correct Orca CLI behavior for this WSL UNC is **omit `--shell`**; let Orca auto-select. The historical `--shell wsl.exe` and `--shell pwsh.exe` attempts were rejected by contradictory host guards with **no terminals created**. Do not create a remote Orca environment merely to fix this working native WSL binding.
- TS WSL project/terminal exists separately; must preserve independent owner and not reinitialize. Terminal tab labels have no Product authority and are not execution acceptance.

## 4. Toolchains and reproducibility

| Provider | Verified | Scope |
| --- | --- | --- |
| Windows/WSL `uv` | `0.13.1` checksum-verified release | Per-user caches, per-OS |
| Windows/WSL CPython | `3.11.17` selected with `uv` | **FitFlow remains on Python 3.11**. Migration `DEFERRED`; Ubuntu OS Python 3.12 unchanged |
| Windows/WSL Node | explicit Node `22.23.3`; Linux npm `10.9.9` | Tecnotron; Windows default Node24/npm11 must not silently control Node22 operations |
| FF locked Windows venv | `C:\TS\station\environments\FF` | `uv sync --locked`, `uv pip check`, FF imports PASS on `3f819a2...` |
| FF locked Linux venv | `/home/tsops/.cache/ts-preflight/FF-py311` | `uv sync --locked`, `uv pip check`, FF imports PASS on `3f819a2...` |
| TS isolated native build/test | `/home/tsops/.cache/ts-preflight/tecnotron-tools` | `npm ci` PASS, workspace verify PASS, typecheck PASS, build PASS, `npm test` **579 PASS, 6 SKIP, 0 FAIL (585 tests)** on `f40236d...`; this is NOT Product acceptance |
| PostgreSQL/Redis in WSL | PostgreSQL **16** serves localhost:5432; Redis **7.0.15** PONG | Not FF test schema/role PASS; GitHub Actions FF uses PostgreSQL **15**. Synthetic published Actions password failed locally. No role/DB/schema mutations authorized. |

Cachés are native to the OS/user; reuse download artifacts keyed by exact dependencies/runtimes, **not** unqualified virtualenvs or `node_modules` across platforms. No automatic dependency update, Python migration or Docker requirement.

## 5. Remaining bindings — explicitly not PASS
1. `OPENCODE_PROVIDER_MODEL_BINDING_UNKNOWN`: `opencode2.exe v2.0.26`, OpenAI credential metadata stored, but previous synthetics `openai/gpt-6-sol` and `openai/gpt-5.6-sol` returned **HTTP 400** in existing terminal `term_bd2636c6-ca95-4a1d-b19e-b5124308fbbc`. Root cause **UNKNOWN**; `models --standalone` did not return a usable catalog. Do NOT replay prior prompts or infer entitlement. Only explicitly qualified provider/model route can be marked PASS after a new separate synthetic request and receipt.
2. `COMMANDER_INDEPENDENT_LIFECYCLE_UNKNOWN`: existing Commander works; whether it survives Orca stop/restart or has a single independent startup owner is not demonstrated. Do not create duplicate daemon, kill current process, install autostart or restart Orca without a safe original-owner reconciliation and service contract.
3. `FITFLOW_PRODUCT_NATIVE_TEST_DB_PARITY_UNKNOWN`: local DB reachable but synthetic role auth failed; PostgreSQL16 local versus 15 Actions. Requires FF Product choice and isolated test database credentials/schema/migrations. Readiness of server != readiness of Product validation.
4. `ACTIONS_ECONOMY_UNMEASURED`: no cache-hit/speedup evidence; any change to CI or action major versions requires each Product's competent Control.
5. `BEADS_UPPER_LC_PENDING`: Beads experimental migration and Upper LC horizontal design in separately governed workstreams. Do not import/adopt Beads, replace State Kernel, impose a fixed agent count, promote autonomy or create a new orchestrator here.

## 6. Nonfinal future bootstrap

There is **NO FINAL BOOTSTRAP**. A future machine bootstrap may be created only after Beads and Upper LC dispositions are reconciled and the operative capabilities stabilized. This snapshot intentionally contains **no installer**. Eventual manifest should encode host selection, versioned downloads+hashes, repo identity, native filesystem owners, isolation, cross-platform cache roots, Orca runtime binding, provider secrets boundary, verified setup gates, rollback and compact receipt. It must not become a parallel Product SOT.

## 7. Recommendations awaiting Product Control; no implementation authority

`FITFLOW_CONTROL`: reconcile `pyproject.toml`+`uv.lock` versus historical `requirements_test.txt` dev/test versions *without changing Python 3.11 or dependencies in this station run*; decide PostgreSQL15-vs-16 and isolated test role/schema; evaluate exact-sha Actions cache/triggers only on a Product-selected TaskCycle/candidate.

Tecnotron competent Control: preserve `tools` branch and the current Node22/npm lockfile; decide any Action cache changes and whether Product wants a separately bound acceptance gate beyond the technical 579/6 isolated run. Do not transplant its PASS to another commit.

This document is a **cross-repo execution navigation snapshot**, not a semantic SOT change. Publication does not mean either Product accepted these recommendations. Reobserve exact commit/tree, current contracts and scoped authority before new actions.
