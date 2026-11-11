# TS EE #18 — Aware C2A OpenCode2 synthetic permission qualifier, IR001 repair

**Identity:** `TS-EE-AWARE-C2A-OC2-BINDING-QUAL-001` • **class:** `NONPRODUCT_SYNTHETIC_ONLY` • **owner:** TS Execution Engineering • **consumer:** Aware Control #29 (PAUSED).  
**Baseline:** [PR #21](https://github.com/mauedgar/ts-execution-lab/pull/21) original candidate `dbf26d291b9356c2542ebe67c5b2a402c9a3e4e3`, original [IR001](https://github.com/mauedgar/ts-execution-transport/blob/259d6083bb45bdcc64847b74c2bcd7f600043be2/results/TS-EE-C2A-OC2-PR21-WEBINLINE-IR001-20261111-001/ORIGINAL.md) `NO_RECOMMEND / 5F / 4A` preserved unchanged.  
**This isolated repair:** proposed response to F01–F05 and A01–A04. Tests and review must independently establish actual closure; documentation does NOT qualify a native runner.

## Trust boundary, source closure and original attempt

`bootstrap.mjs` is a minimal **externally pinned entrypoint**, not a self-proving root of authority. The competent operator must check the exact Git commit/tree, original code path and SHA-256 of **bootstrap itself** against a separately approved immutable S0 request **before** executing. The bootstrap then validates its own source digest, those of `binding.mjs` and `qualify-native.mjs`, the exact Node 22 binary SHA-256/version/path, Git and OpenCode binary SHA-256/path, qualified Windows host identity, and root path identity **before** dynamic imports. A hostile operator can counterfeit an entire request and its hashes: a verified Developer/control grant remains mandatory.

Request schema `ts-ee-oc2-c2a-request/v2` fields: `product=mauedgar/aware-commerce`, `authority_class=SYNTHETIC_NONPRODUCT_ONLY`, `paid_api_fallback=false`, `operation_id`, `attempt_id`, `bootstrap_sha256`, `runner_sha256`, `binding_sha256`, `node_sha256`, `node_executable`, `node_version=v22.x.y`, `git_sha256`, `git_executable`, `executable_sha256`, `opencode_executable`, `expected_version=opencode v2.x.y`, `expected_host`, `model`, `agent`, `expected_head`, `expected_tree`, `expected_origin`, `repository_root`, `scratch_anchor`, `scratch_parent`, `authorization_receipt_ref`, `authorization_receipt_sha256`.

The current isolated prototype deliberately admits only original host `DESKTOP-DJLBEQH`; the competent Control must not substitute another host silently. The scratch anchor and parent must already exist, be locally provisioned by their owner, free of symlink/reparse traversal according to the native path checks, and be separated from Product. The scratch parent's final component must equal `ts-ee-oc2-c2a-synthetic`. File ownership/NTFS ACL and local OAuth provider credential mode are **separate S0 checks** not proven by Node unit tests. On uncertainty return `BLOCKED_PRECONDITION/NONE`, not PASS.

One original `attempt_id` must be fresh. The bootstrap supports only `--run` and `--observe`. `--observe` is read-only and returns existing original receipts; there is no resubmission. The qualified command, after S0, is:

```powershell
<verified-node22.exe> <verified-bootstrap.mjs> <verified-absolute-request.json> --run
```

This snippet is NOT authority to execute. In particular, Commander may execute only a **previously materialized, complete, versioned and hash-verified runner and bounded request**. No Commander semantic exploration, source creation or dynamic shell construction. `node.exe` as direct execution is permitted only if the bounded run has already been admitted; the preferred mechanical PowerShell runner contract remains applicable if that is the selected route.

## Native method

1. Read-only Git checks bind exact origin/HEAD/tree, clean worktree, pinned Git binary, and original approved synthetic host/source. This verifies git identity; it never modifies Aware.
2. Configure a strict OpenCode2 `OPENCODE_PURE=1` environment with **allowlisted environment names only**. `OPENCODE_CONFIG_CONTENT` declares deny-all and explicit agent allowances only for exact Git read commands and a disposable synthetic file. `--standalone debug agents` is checked for exact expected rules and rejects unexpected allows. **A debug snapshot is not runtime security proof.**
3. Persist `START.json`, native effective-config fingerprint, and `CONTEXT.json` with create-only writes in a new isolated directory. Before a provider process is launched, persist create-only `DISPATCH.json` to make any crash/ACK-loss `UNKNOWN` pending exact reconciliation, never a blind retry.
4. Invoke **one** model session, stream its native JSONL to `NATIVE.jsonl` with fsync, write hash/metadata and a final `RESULT.json` create-only. Verify five ordered, actual native tool events: two successful exact shell Git HEAD/tree reads, successful patch of `ALLOW_ONLY.txt`, native rejection of `BLOCKED.txt` patch, and native rejection of shell `echo TS_EE_DENY_PROBE`. Reject wrong sessions, duplicate call IDs, malformed/truncated frames, spoofed errors, wrong output/provenance, missing terminal, extra tool use, or changed Product tree.
5. Verify **exact UTF-8 bytes** `TS_EE_ALLOWED_PROBE` in the sole approved synthetic file and absence of forbidden sibling. Only then may receipt say `PASS / CONFIRMED_SYNTHETIC_ONLY`. All post-dispatch non-PASS terminal states remain `UNKNOWN / UNKNOWN_SYNTHETIC` conservatively; do not infer `NONE` from a nonzero process exit or missing output.
6. `--observe` retrieves the original START/DISPATCH/RESULT state without running model again; if dispatch marker exists and terminal receipt does not, effect stays UNKNOWN and must be reconciled through original provider-native evidence. All attempts keep their identity; do not append retry suffixes without a new competent grant.

## Limits and review

Provider authentication mode, no metered-API fallback, owner/ACL, real reparse-point behavior, final resolved per-session OpenCode permissions and actual tool registry **require empirical native qualification**; the synthetic source and CI cannot guarantee them. The original static PR #21 CI run 43039612021 PASS is not an OpenCode result. IR001 original 5F/4A preserved. Repair must undergo a NEW independent IR on a fresh exact HEAD/tree, followed by one new originally authorized synthetic execution on the intended host and separate Control audit. If native host differs, adapt only under new owner/binding qualification; do not weaken Product deny-all.

**No effects on** `mauedgar/tecnotron-ai`, `mauedgar/aware-commerce`, BE #6, FE #7, original P0 TaskCycle or Phase2, secrets, workflows in other repos, paid provider accounts, deployment or production. Aware remains PAUSED until both Tecnotron #71 and TS EE #18 produce actionable final technical results; **Developer** is the term for acceptance/escalation/semantic decisions.
