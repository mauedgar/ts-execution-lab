# TS-BEADS 047B — measured Orca-visible OpenCode2 invocation and original-attempt fence

**Artifact class:** experimental execution-binding observation, **not** a new orchestrator, gate, Recipe, Product contract, acceptance or permission to dispatch. Existing Execution Engineering operating contract remains controlling. No Product effects.

## Failure mode proved (original attempt remains UNKNOWN)

The standalone CLI launched by Commander as `opencode2 run --standalone --agent build "..." ` generated Windows process tree `18796→11384→20888→23184` on notebook `DESKTOP-DJLBEQH`. Native CLI logs at `2026-11-02T13:52:39Z` identified `run=ba800ff3` (launcher) and `run=9ec3e131` (standalone). Working directory was `C:\Users\Mauri\AppData\Local\npm-cache\_npx\4b4c857f6efdfb61\node_modules\@wonderwhy-er\desktop-commander\dist`, **not** the desired Orca workspace `C:\TS\station`. There was no matched session, tool calls or terminal effect receipt among 64 queried native sessions. The absence of expected staging/Transport original is not evidence of zero effects. **Do not kill, retry or overwrite the original write set as if it never started.** Original reconciliation: `mauedgar/ts-execution-transport@bb8ff4bc5255f80d714f9c215531a233f7e2d296:results/TS-BEADS-047B-V6P2-ORCA-RECOVERY-20261102-002/NATIVE_SESSION_JOIN.md`.

## Reused existing Orca CLI binding actually observed

Using **Commander solely to invoke bounded, preselected mechanical Orca CLI operations**, the following was observed (not a grant for future operations):

1. `orca terminal list --worktree 'path:C:\TS\station' --json` exposed 18 existing Orca terminals. No old V6P2 test terminal was identified.
2. `orca terminal create --worktree 'path:C:\TS\station' --title 'TS-BEADS-047B-V6P2-RECOVERY-002' --json` created **exactly one** new Orca visible terminal `term_2a198a2d-9cdc-492b-9737-f61cc094c4bd`, processId `11208`, incarnation `fc7b8331-98c1-4e47-80d9-c489f2bd0950`, `executionHostId=local` (local to Orca server **on the notebook**, not to the ChatGPT server).
3. The first quoted `orca terminal send ... --text "opencode2 run ..."` under Windows PowerShell parsing returned `invalid_argument` **without accepted input**. The corrected one-token `orca terminal send --terminal term_... --text opencode2 --enter --json` was accepted exactly once. Orca declared provider delivery unsupported, so Control *separately verified* actual screen showing OpenCode 2.2.5 TUI. Orca launch was no longer a silent Commander background process.
4. Initial OpenCode TUI showed a What's New modal. One ESC removed it. One Shift-Tab selected **Plan** instead of Build, screen verified `Plan · GPT-6.1 Sol OpenAI · high`.
5. An exact read-only recovery prompt was sent to the same terminal using `orca terminal send --terminal term_... --text '<short prompt containing frozen Git carrier>' --enter --json`. The provider only attested input acceptance, **not** delivery. Later native Orca screen proved agent analysis, read-only commands, response and terminal completion. This is bounded native visibility, **not** native source test PASS.
6. Frozen handoff `mauedgar/ts-execution-transport@b320e1fc060f81ec6a651dc4249d70a3b327433d:handoffs/TS-BEADS-047B-V6P2-ORCA-RECOVERY-20261102-002/HANDOFF.md`; source `mauedgar/ts-execution-lab@ca8d467a8b8c4490db913bb76b20b59966d14acb`, tree `874b5428e0ec11fcc3a2349a2a89d6d80aa270f0`.

**Do not treat Orca's visible terminal creation, provider unsupported delivery, a TUI prompt, or `Plan` conclusion as execution of the native V6P2 test gate.**

## Deterministic future dispatch selection (when competent authority and original effects allow)

- Reobserve host/Orca `worktreeId`, workspace, existing exact terminal/attempt, source commit/tree, frozen handoff, source-only flags and test write-set first. Preserve old terminal identities; do not assume every preexisting `C:\TS\station` terminal belongs to 047B. If exact attempt RUNNING, observe/join instead of duplicate.
- Do **not** use Commander's inherited working directory for OpenCode source execution. Route via existing Orca CLI to the **Orca-visible notebook-owned terminal**. For native test preflight, actor may use source/working copy tools in Orca after verifying scratch exclusivity; Commander remains execution/result only. Use short fixed commands; avoid nested `pwsh -Command`, escaping brittle prompt payloads, `WaitForExit`, polling or forced kill.
- If Orca `terminal send` returns `accepted=true` but delivery `unsupported`, do **not** send again to recover a missing acknowledgment. Observe the same terminal and verify the exact result. If original write effects are UNKNOWN, do not dispatch an equivalent new preflight even in a different scratch dir until their exact effects are reconciled.
- Never expose authenticating secrets/tailnet addresses or use SQL/Beads/Dolt/Tailscale Serve under the source-only V6P2 review. The full 047B DoD still requires independently authorized, provisioned, observed dual-host state, ACL, failover, recovery and backup experiments before possible Product adoption.

**Binding capability:** `ORCA_VISIBLE_NATIVE_AGENT_INVOCATION=PROVEN` for one read-only recovery actor; `V6P2_NOTEBOOK_NOSQL_PRE-FLIGHT=NOT_PROVEN`; `LIVE_BEADS_DOLT_INTERHOST=NOT_PROVEN`; `PRODUCT_KERNEL_MIGRATION=NOT_AUTHORIZED`.
