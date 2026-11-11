# TS EE — Aware C2A OpenCode2 native permission-binder qualification candidate

**Identity:** `TS-EE-AWARE-C2A-OC2-BINDING-QUAL-001` / [issue #18](https://github.com/mauedgar/ts-execution-lab/issues/18)  
**Classification:** CANDIDATE / NONPRODUCT_SYNTHETIC_ONLY / NO_NATIVE_PASS until original host execution and IR.  
**Owner:** TS Execution Engineering. **Consumer:** Aware Control issue #29.  
**Source base:** `mauedgar/ts-execution-lab:main@71e4384ffdfb0ec3b11d89ad356ff2ef0ff133d1`.  
**Write-set:** exclusively this directory and `.github/workflows/ts-ee-aware-c2a-oc2-static.yml`, no Tecnotron/Aware edits.

## Why this candidate exists

Aware `main@21c848753211319df137c778d3b406f409ebdc5c` keeps `opencode.json` deny-all. Historical original P0 A007 validates only native read; original A002 validates a different negative experiment. No original C2A native positive write-binding qualification exists. **Do not reuse or relabel A002/A007, and do not modify global deny-all.**

`binding.mjs` validates an exact, synthetic-only request, creates narrow native OpenCode2 policy, checks `opencode --standalone debug agents` effective rules, rejects unexpected shell/edit permissions, and classifies provider-native JSONL positive/negative tool events. `qualify-native.mjs` is a one-shot runner that verifies executable/version/SHA256, runner source SHA256, host, clean exact Aware worktree HEAD/tree/origin, disjoint scratch directory, synthetic-only allowlist and two forbidden probes, then publishes original create-only `START.json`, `NATIVE.jsonl`, `NATIVE_META.json`, and `RESULT.json` under the isolated attempt directory. An existing attempt directory is **OBSERVE_ONLY/NO_REPLAY**.

This test can create a file **only in a disposable synthetic directory** if OpenCode actually invokes native edit/write with an allowed resource; it must also observe native permission denials for `BLOCKED.txt` and `echo TS_EE_DENY_PROBE`. A model assertion or refusal does **not** count. A native success requires read HEAD/tree events, allowed edit event, two denied events, at least nine provider JSONL events, no unexpected tool completions, exact approved file contents/hash, no forbidden sibling file, and no error. Other outcomes remain BLOCKED or UNKNOWN with exact original effects preserved.

## Preparation and current verification limit

The candidate requires a **fresh competent S0 native request**, not an arbitrary user payload. Freeze via a competent execution owner outside Commander:

- current signed or versioned, hash-verified runner source and exact original Git commit/blob;
- absolute verified OpenCode executable and SHA256, `opencode v2.x` exact version, host identity, model and provider with no paid API fallback;
- clean local Aware worktree (current repository commit/tree to be reobserved), expected Git origin, owner-controlled disposable scratch parent outside Product;
- unique new `operation_id` and original `attempt_id`; file `request.json` with `schema=ts-ee-oc2-c2a-request/v1`, `product=mauedgar/aware-commerce`, `authority_class=SYNTHETIC_NONPRODUCT_ONLY`, `paid_api_fallback=false`, `runner_sha256`, `executable_sha256`, `expected_head`, `expected_tree`, `expected_origin`, `expected_version`, `expected_host`, `model`, `agent`, `repository_root`, `scratch_parent`, `opencode_executable`;
- one-shot bounded execution/transport grants and expected durable receipt. Command to run **only after all those preconditions are satisfied**:

```powershell
node <verified-absolute-path-to-qualify-native.mjs> <verified-absolute-request.json> --run
```

Do **not** treat this Markdown command as permission to launch. Commander may only execute a fully determined existing hash-verified runner with exact bounds; it cannot create the scripts, explore source, construct a request, poll or retry. If runner/request are not pre-materialized, stop `BLOCKED_PRECONDITION/NONE`. No ZIP/Base64 transport shortcut. The exact carrier may be delivered via a qualified bridge only when its envelope/extractor integrity contract is already satisfied.

## Tests and gate

The pinned read-only PR CI workflow runs `node --check` and `node --test experiments/aware-c2a-oc2-binding-001/binding.test.mjs` on Node22. This only validates **deterministic code behavior**. It does not exercise real OpenCode, positive permissions, effective configuration on the target host, Product BE/FE, nor native results.

The next independent reviewer must inspect all files, bounded authority, self/CLI hash guard, path safety, config-debug provenance, native JSONL status handling, negative probes, PASS/UNKNOWN inference and idempotency/attempt preservation. Repair findings/advisories under a new exact reviewed candidate and prove the native evidence before reporting a result to Aware Control. Source static CI PASS, if obtained, never substitutes for host-native positive and negative evidence.

**Caution for BE/FE:** this candidate does not grant Product work. Aware Control must separately issue task-specific BE #6 and FE #7 TaskCycle/Operation/Attempt grants; perform effective configuration admission in their actual worktrees; keep the shared bootstrap manifest, migrations and routes with their unique serial owners; and require actual CI, IR, acceptance and integration. Original P0 historical post-init issue #71 remains a separate Tecnotron Control decision.
