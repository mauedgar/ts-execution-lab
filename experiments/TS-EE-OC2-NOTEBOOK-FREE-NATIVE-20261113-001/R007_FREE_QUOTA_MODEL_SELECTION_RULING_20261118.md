# R007 — Developer grant: any genuinely free-quota model, explicit bounded selection (2026-11-18)

**Responsibility preserved:** `TS-EE-OC2-NOTEBOOK-FREE-NATIVE-20261113-001`, R007 B1→B2→B3. **Authority:** experimental Execution Engineering only, Product NONE. This is a prospective grant; it does not retroactively authorize, retry, integrate, or reclassify historical A001.

## Developer intent and selection rule

The Developer explicitly permits selection of **any model with an available free quota**, not only `opencode/deepseek-v4.1-flash-free`, to complete the qualification experiment. Providers already have free-quota offers. This is **not** authorization for pay-as-you-go costs, using paid OpenRouter balance, hidden paid fallback, spending credits reserved elsewhere, or removing security gates.

The currently tested strict-free candidate remains exactly pinned to `opencode/deepseek-v4.1-flash-free`, as its effective `plan` denial and isolated standalone catalog are already supported by native receipts. Reuse-first: prefer this observed candidate while the offer and quota are **natively verified**. If unavailable, a new model is eligible only under a separately frozen immutable candidate with exact provider/model/agent/auxiliary binding and original `ExecutionAttempt` identity, verified free-tier entitlement, effective deny-all policy and no billable fallback. Never silently swap the model under the same attempt.

Signed-out `opencode` free tier and authenticated free quotas from other providers are eligible in principle but must be distinguished from their paid account/routing modes. Catalog labels and `cost=0` event fields are not billing proof. Existing credentials must not be revoked or altered globally to make this experiment pass.

## Reconciled qualifying mechanical evidence

- R007 file-based isolated provider preflight: native `models --standalone` exposed 12 `opencode/` models, zero outside, including the pinned free candidate; `plan` effective native permissions reported 11 rules, explicit wildcard deny-all, no subsequent allow/ask, and exact model providerID `opencode`. Source and native receipt already published.
- Cross-worktree synthetic ledger root was found already populated; read-only SHA reconciliation preserved A001 NONE, A002 CONFIRMED, A003 purposely UNKNOWN, A004 absent, **without** replay or deleting the unknown. Full original previous test completion marker not recovered, so do not claim 4/4 new PASS.
- Separated binary stdout/stderr capture source `R007_B1_SEPARATED_CAPTURE_V1.ps1` and corrected synthetic selftest V2 were run in the isolated Orca terminal. Native terminal reported **3/3 PASS**, including stdout 23 B, stderr 18 B, nonzero exit 7 retaining effect CONFIRMED and duplicate rejection. Exact originals and terminal receipt hashes are in `R007_B1_SEPARATED_CAPTURE_NATIVE_SYNTHETIC_20261118.md`. No OpenCode2 inference or external charge.

## Remaining mandatory boundary

Before any new model inference: integrate complete immutable request/carrier/executable admission, safely bind the host-wide ledger and separated native capture to an exact Orca-owned terminal, confirm provider identity/zero-charge quota with native evidence, preserve original JSONL bytes, validate structure, then ONE grouped source IR with complete PRIMARY-file coverage. Only then B2 may execute exactly the three synthetic semantic cases under separately frozen attempts, followed by ONE grouped behavioral IR. All results remain experimental and OpenCode2 optional.

**Current observation:** `B1_MECHANICAL_COMPONENTS_PROGRESS / FREE_PROVIDER_SELECTION_EXPANDED_PROSPECTIVELY / FULL_BRIDGE_NOT_QUALIFIED / NO_NEW_INFERENCE / PRODUCT_EFFECT_NONE`.
