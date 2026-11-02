# TS-BEADS 047B — V6P3 source-only A001/A003 hardening candidate

**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (experimental), NOT a new Product TaskCycle.

**Immutable baseline:** V6P2 `mauedgar/ts-execution-lab@ca8d467a8b8c4490db913bb76b20b59966d14acb`, tree `874b5428e0ec11fcc3a2349a2a89d6d80aa270f0`, reviewed by IR014. The V6P2 source, runner, receipts and independent verdict remain untouched. This is a fresh isolated candidate, not a repair-in-place or retry of any native effect.

## A001 — expanded static PowerShell source checks

`tests/Test-V6P3-ParserAndAst.ps1` parses the **three native source files**, rejects assignments to protected PowerShell automatic variables in nested LHS AST, unary ++/--, direct variable-provider mutation commands, a variable: drive command, and PSVariable.Set/Remove. It also asserts negative adversarial samples and one benign sample, with no script/effect invocation. This stricter check is a static guard, **not** a security sandbox or complete proof for dynamic PowerShell invocation/aliases, and native Windows execution is still required before reporting PASS.

## A003 — richer child ambiguity receipt, never automatic retry

`candidate/Invoke-047B-V6-Fixture.ps1` conservatively records `ChildEffectAmbiguous=true` if a child stage fails before durable `CHILD_EXIT` confirmation. The best-effort `CHILD_AMBIGUOUS` receipt includes original PID, observed HasExited/ExitCode if safely readable, `possibleAlive` tri-state, error **type** only (no secret message), `reconciled=false`. It never kills or retries a child. An observed exit code **does not** prove original SQL effect reconciliation. Receipt write failure preserves the preexisting `SPAWN_INTENT` where available and retains UNKNOWN classification.

The runner has a new source-only `attempt=TS-BEADS-047B-DOLT-FIXTURE-V6P3-20261102-001`, but **there is no Developer signed issuer, grant, original CAS, or authorization to dispatch a live V6P3 SQL fixture**. Launcher pins the new runner Git blob; security module bytes are identical to V6P2 and still have an unprovisioned trusted-key pin.

## Validations and limits

`tests/test_source_contract.py` retains the seven earlier source checks and adds ambiguity evidence, adversarial AST fixture inventory and **8-entry manifest byte/hash/LF** pin checks. `tests/Test-V6P3-Negative.ps1` still checks that missing issuer fails closed prior to effects. The manifest must be frozen after all eight files are published. Run Python unittest and native PowerShell parser/AST/negative tests on a verified isolated checkout; prefer GitHub Actions Windows hosted as a non-SQL test, and request fresh IR of **this exact candidate**. **A static source PASS is not notebook PASS.**

At cutoff the original notebook V6P2 Commander-launched process `18796→11384→20888→23184` remains `UNKNOWN`, without attributable native session/receipt; user allowed discarding it operationally, not erasing evidence or declaring `NONE`. V6P3 source-only work does not inspect/kill/retry that process or touch its uncertain write set. The full 047B DoD still requires authorized native Dolt/Beads dual-host effects, independent CAS/authority, outage and backup/restore proof. No SQL/Beads writes, Tailscale Serve/Funnel, Product, #35 H6, Kernel or TaskCycle effects here.

**V6P3R1 test-only correction:** New source candidate preserves all V6P3 executable PowerShell and parser/negative AST tests byte-identically; fixes only two incorrect escaped Python byte literals in manifest integrity source test (CR and UTF8 BOM). Original V6P3 Windows run 41470490400 attempt 1 FAILED 9/10 Python, AST and issuer-negative not executed; never rewrite or retry the run. Original failure reconciliation: mauedgar/ts-execution-transport@e3d9c44a4fd7cdf0076be70e70247179b2dcca13:results/TS-BEADS-047B-V6P3-WINDOWS-SOURCE-20261102-001/ORIGINAL_FAILURE_RECONCILIATION.md.

**Disposition until native validation and IR:** `SOURCE_ONLY_UNQUALIFIED`; `NO_GO_EFFECT`; `HOST_INDEPENDENCE_INCOMPLETE`.
