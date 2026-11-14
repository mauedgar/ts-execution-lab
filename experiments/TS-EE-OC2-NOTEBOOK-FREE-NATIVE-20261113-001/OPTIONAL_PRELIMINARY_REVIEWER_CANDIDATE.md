# TS EE — Optional preliminary reviewer profile (experimental, NOT canonical)

**Profile_ID:** `TS-EE-OPTIONAL-PRELIM-REVIEWER-20261113-001`  
**Candidate state:** `PREPARED_NOT_QUALIFIED / NOT_DISPATCHED`  
**Authority:** TS Developer Lab method only, Product NONE.  
**Reference A001:** `mauedgar/ts-execution-lab@23559b2ff640df49aec8c360ac8286a7573e2c54:experiments/TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001/CONTROL_DISPOSITION_A001_20261113.md`.
**Developer ruling:** a reviewer is ALWAYS a **competent per-responsibility selection**, not a mandatory OpenCode2 phase, fallback default, reviewer monopoly or canonical pipeline change.

## Review binding selection is explicit

| Alternative binding | Potential use, only if selected and qualified | Limits |
| --- | --- | --- |
| `WEB_INLINE` | Independent source/semantic review in a separate ChatGPT Web context | Distinct binding, review identity and original; not auto-selected by OC2 results |
| `OPENCODE_LOCAL` | Optional, non-OpenAI/free preliminary review in an Orca-owned notebook Windows or WSL terminal | Currently A001 semantic NO_RECOMMEND; **NOT** a qualified formal IR or an automatic gate |
| `ACTIONS_REMOTE` | Manual remote capacity fallback only after notebook effect NONE and cross-host exclusion qualified | Inert source-only candidate; not active or automatically selected |
| Other competent harness | Reviewer when its independence, access, evidence, cost and scope are explicitly selected | No harness chosen by model availability or prior success alone |

**Selection authority:** competent Control for the given responsibility and frozen subject, within Product SOT/lifecycle where applicable; Developer decides any acceptance or new gate. If no reviewer binding is explicitly selected and the task requires one, stop at `REVIEW_BINDING_UNSELECTED`. Never assume OpenCode2 is default, never automatically substitute WEB_INLINE after OC2 failure or vice versa. Changing binding after a dispatched attempt requires exact effect reconciliation, new identity and competent scope.

## A001 outcome preserved without reinterpretation

A001's Orca terminal transport and free-model process ran successfully, but the model disregarded the self-contained inline TypeScript bug and explored unrelated repository files. Its final response falsely classified the already executed effect as NONE and proposed a new large fixture. Source `CONTROL_DISPOSITION_A001_20261113.md`: `ORCA_NATIVE_BRIDGE_FUNCTIONAL_PASS / REVIEWER_SEMANTIC_NONCONFORMANCE / NO_RECOMMEND`. The 399,890-byte local ORIGINAL and SHA-256 `EA873A99533684F3EE2AB9D7F39FB634031969C689BFF7A95919F5BA53085AE9` are preserved on the notebook, not made public; the derived Control account is NOT a replacement original. No retry of A001.

## Revised OPTIONAL synthetic design (not an executed request)

A future independent **new** attempt can qualify a much narrower closed-context preliminary reviewer. The bug and requirements belong **in the frozen prompt itself**, not an inferred external fixture. Do not combine a semantic quality test with live tool-denial canaries or repo discovery in the same model call.

**One closed-context prompt candidate:**

```text
Review only this self-contained synthetic TypeScript snippet. Do not search the repository or request additional files. Do not use tools. Return one bug finding or NONE, with a minimal correction and two tests.

Requirement: only a strictly positive quantity can be booked; zero and negative values are invalid.
Code:
function canBook(quantity: number): boolean { return quantity >= 0; }

Output JSON only:
{"findings":[{"code":"F01","file":"INLINE.ts","line":1,"problem":"...","fix":"..."}],
 "tests":["...", "..."],
 "scope":"INLINE_ONLY",
 "tool_calls_claimed":0,
 "limitations":["synthetic, not Product; no execution of tests"]}
```

**Predetermined evaluation oracle:** `>= 0` admits zero and violates the requirement. Correct `> 0`. Regression checks include `canBook(0) === false`, `canBook(1) === true`, and preferably `canBook(-1) === false` (two focused tests minimum). A response that invents missing fixtures, reads outside scope or misstates its own effect fails even if plausible. Do not ask the model to decide the TaskCycle/effect state; Control determines effect from provider-native records.

**Admission (future, separately authorized):** Orca native terminal binding, selected reviewer identity/model, non-OpenAI zero-cost provider/account verified at run-time, explicit no-paid-fallback, private `--standalone`, effective read-only policy and absence of active competing attempts. For this closed-context test, **tool calls must be zero**; model/auxiliary calls and cost/side calls recorded. The terminal result requires complete JSONL ORIGINAL, SHA-256, exact provider session/attempt and readable bounded verdict. A separate negative permission canary with its own frozen request and execution identity tests actual denials; its outcome must not be conflated with semantic reviewer quality.

**Scoring and DoD:** original response parsed independently; exact finding, fix, tests, scope and tool-call verification; no fabricated review status; all model-related provider costs verified zero; no Product effects. A model completing the task is only a candidate preliminary binding. Independent WEB_INLINE IR remains a **separately chosen** option, never automatically required by this profile.

## Stop conditions

This document **does not** authorize A002, any OpenCode2 launch, use of a paid model, an Actions fallback, a Product review, or adoption of a routing default. It prepares a reproducible optional candidate. Any future run needs a new, expressly granted operation/attempt, frozen subject, write-set, budget and independent original custody.

**Disposition:** `OPTIONAL_PROFILE_PREPARED / CHOICE_NOT_CANONICAL / NO_RUN / PRODUCT_EFFECT_NONE`.
