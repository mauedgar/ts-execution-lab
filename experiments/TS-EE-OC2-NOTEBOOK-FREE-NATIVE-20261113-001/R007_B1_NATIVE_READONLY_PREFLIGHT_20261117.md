# R007 — B1 native read-only preflight and safe stop (2026-11-17)

**Responsibility:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`; authority NONE, Product effect NONE.
**Status:** `B1_PARTIAL_PRECONDITIONS_OBSERVED / MODEL_DISPATCH_NOT_AUTHORIZED_BY_PRECONDITIONS / NO_NEW_INFERENCE`. This is NOT OpenCode2 optional reviewer qualification, standing Orca-bridge approval, or Product integration.

## Exact frozen preparatory material

- Experimental plan `mauedgar/ts-execution-lab@796cfbabd669e0986aa285ee1e92b05696b82ba2:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/R007_OPTIONAL_OC2_QUALIFICATION_AND_BOUNDED_IR_PLAN_20261117.md`, blob `14c4b782822cecee38042fd478536635ffedb1e6`.
- Strict-free, zero-tools config **candidate**, `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_CLOSED_CONTEXT_FREE_NO_TOOLS_CONFIG_CANDIDATE.json`, blob `16ed6e50bddf955db6f27484624b47cbe762fb3b`. Its `integration.use` permits only the **signed-out opencode** integration after wildcard denial; `provider.use` permits only opencode; tool/MCP/skill/plugin use denied. The config has NOT been proven loaded/effective on the native server or in an Orca semantic session.
- Three immutable synthetic self-contained cases, `experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/OC2_CLOSED_CONTEXT_SEMANTIC_CASES_V1.json`, blob `c0be212f4e64b6ee1d8ac64346f7ed20ab62194a`; no case has been dispatched. Source model ID `opencode/deepseek-v4.1-flash-free`.
- R006 parser source-only `RECOMMEND_SOURCE_ONLY / 0F / 5A` and 60/60 POSIX tests remain independent of the current OpenCode model/server. Historical A001 remains terminal failed/nonconformant; no replay.

## Exact qualified host and mechanical observations (NO semantic source review by Commander)

Host `DESKTOP-DJLBEQH`, native Commander device `40cc0b10-fa7b-4a6a-98cf-1c94f93791b2` online; other desktop offline and out of scope.

| Observation | Native identity | Exact terminal result |
|---|---|---|
| OpenCode2 version preflight, `C:\\Users\\Mauri\\.local\\bin\\opencode2.cmd --version` | mechanical PID `4536` | exit 0, `opencode v2.2.5` |
| `models opencode` syntax probe | PID `3972` | parser rejected unexpected positional argument; no model or mutation |
| `models` against default/background location | PID `6344` | exit 1: `ServiceUnavailableError: Location plugins did not finish activating`; not a model absence proof |
| `models --standalone` (different, private server binding) | PID `6492` | exit 0, 593 output lines; explicit listed `opencode/deepseek-v4.1-flash-free`. No model inference or provider billing attestations |
| Exact launcher shim `Get-FileHash` | PID `10404` | SHA-256 `4D793D1A5A4CEBEA5A404B53EB6D6D2065EC36AEB11CDA8803B7BF16CB8F2F49`, exit 0. **Shim only**, not full underlying runtime package hash |

The catalog did include many providers, including paid or external providers. Listing a model is NOT a guarantee that the connected account is signed-out, that the model is bill-free now, that the strict candidate config is active, or that automatic paid routing is impossible. The native `--standalone` result isolates an earlier service activation issue but does not prove all implicit calls use the selected provider. Do not retry the failed default catalog attempt as if it were a model call.

Independent public upstream reports document that on OpenCode2 v2.2.5 the plugin activation timeout can block `/api/model` even though models exist, with different causes (slow plugins, credential refresh, filesystem watchers). This bounded observation **does not identify which cause** applies on this notebook; do not modify plugins, accounts or install globally based on a guess.

## Remaining B1 gates, in one coherent batch

1. Native *effective* config/policy/provider/session attestation for strict-free profile, including the status of signed-out `opencode` integration, no paid account, no network/tool fallback, and tests of actual no-tool enforcement. Current static config validation is insufficient.
2. Exact installed executable/package identity beyond the CMD shim; qualified separate Orca terminal/worktree/HEAD, free memory, and resource caps.
3. Create-only cross-worktree/host launch ledger, full source/prompt digest and unique attempt fencing; distinguish `NONE`, `CONFIRMED`, `UNKNOWN`. Do not reuse historical A001 runner unmodified.
4. Separate stdout/stderr capture, complete provider session and terminal receipt, private original custody, reuse R006 parser on raw unchanged JSONL. No failed-tool canaries mixed with semantic cases.
5. Only then a **single grouped source IR** of runner/config/ledger/test batch. Reviewer files must fit bounded IR inventory; missing primary file means `BLOCKED_COVERAGE`.

If all B1 requirements become PASS, a separate new and explicitly frozen set of B2 unique attempts may run the 3 synthetic cases in an Orca-owned visible terminal; no paid fallback. Then ONE grouped behavioral IR. If B1 remains blocked, keep OpenCode2 as a nonblocking experimental option and continue using other competent review bindings when selected.

**No semantic model calls, no replay, no Actions activation, no Product files, no admission to Product pipeline.**
