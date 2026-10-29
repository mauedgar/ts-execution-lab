# Beads 035 — Control experimental terminal disposition

**Identity:** `TS-BEADS-035-GUARDED-RACE-20261029-001`.
**Authority:** `EXPERIMENTAL_CONTROL_ONLY`. No Product selection, TaskCycle start, Developer grant, Independent Review, Phase 2, SOT edit or Kernel removal.
**Terminal:** `PASS_NATIVE_CONCURRENT_GUARDED_CAUSAL_WRITER_WITH_PRIVILEGED_BOUNDARY_OPEN` / `COMPLETE_WITH_LIMITATIONS`. **NO REPLAY.**

## Frozen source / original attempt identities

- Product observed: `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`, `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`.
- Shared Dolt untouched: `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.
- Predecessor 034 terminal `mauedgar/ts-execution-lab@1c8509b4fa47d36609f0047c3ceaf8240e3732fb`. Never replay provider 033 or experiment 034.
- Bypass 028 already measured: `mauedgar/ts-execution-lab@9e8016004ef5d3ca74abd67914d8e1a03ffcd851:experiments/TS-BEADS-028-FAILCLOSED-20261028-001/CONTROL_EXPERIMENTAL_VERDICT.md`. Privileged direct `bd dep add` can bypass root revision, and privileged direct `bd serve` can bypass selected authenticated launcher. This was **not** retested, evaded or resolved in 035.
- **Attempt 1**: [GitHub Actions 40934697591](https://github.com/mauedgar/ts-execution-lab/actions/runs/40934697591), job `123662024312`, source `82cf2d02ae1d6993d0bade13f618197862cd1bfe`, `completed/failure`. Harness failed before any race (`NATIVE_HTTP_EARLY_EXIT`) because it tried `bd serve` against embedded Dolt. Pinned `gastownhall/beads@v1.3.1:cmd/bd/serve.go` explicitly refuses embedded mode to preserve atomic request semantics. Preserve, no retry.
- Distinct **attempt 2**: [GitHub Actions 40935082766](https://github.com/mauedgar/ts-execution-lab/actions/runs/40935082766), job `123663374277`, source `4b845ae857c01c8e181caa55858e08d609ebbfff`, `completed/success`, run_attempt 1. Scoped harness repair: isolated loopback Dolt SQL Server and `bd init --server`. Concurrency criteria unchanged.
- Original success evidence: `mauedgar/ts-execution-lab@2e456f0279f25e35a39a37c3fc909f4f7a1d8761:transport/TS-BEADS-035-GUARDED-RACE-20261029-001/EVIDENCE_CARRIER.txt`, Git blob `cd7a03fe593407ac3622abdec1358d62c0c67da6`, original 14,015 bytes / SHA-256 `351084731578db26c7aab16914f3f9da8483d2a2ccd1249a36c6bcea001301fa`. Native Product `IR-TXT-CARRIER/1` project, verify, extract and byte equivalence PASS. Three members including `original/RESULT035.json`.

## Exact native findings

Native Beads `v1.3.1` and Dolt `v2.2.0`, isolated local-only SQL server/Beads API, generated token, one disposable Git repo **with no remote**. Two independent Python worker OS processes per race each received the same server-minted root row revision, waited for a synchronization barrier and submitted distinct `batchApply` requests comprising `update root(expected_version)` and `dep_add root->child`.

**Four bounded races; all 29 checks PASS:**

| Race | A | B | Winner and sole edge |
| --- | --- | --- | --- |
| 1 | HTTP 409 | HTTP 200 | B: `ts035-r1b` |
| 2 | HTTP 200 | HTTP 409 | A: `ts035-r2a` |
| 3 | HTTP 200 | HTTP 409 | A: `ts035-r3a` |
| 4 | HTTP 200 | HTTP 409 | A: `ts035-r4a` |

In every race: exactly one accepted transaction and one conflict; root revision changed and metadata recorded winning writer; losing edge absent, previously committed edges preserved. After stopping Beads HTTP, a fresh CLI process recovered exactly the four winning edges. No production or shared Dolt changes.

## Competent interpretation

- **QUALIFIED_BOUNDED_GUARDED_CAUSAL_RACE:** under one native Beads API and an isolated Dolt SQL Server, competing callers honoring the same root revision guard do not both commit: at least in four observed races, native SQL/backend returned 409 to the loser and did not partially commit its edge.
- **NOT A UNIVERSAL MUTUAL EXCLUSION GUARANTEE:** this experiment does not cover malicious or privileged direct bd/Dolt actors, bypass routes, multiple servers/hosts, database service failure, effect replay, or exact causal read-set closure across unrelated roots. 028 demonstrated a material bypass, so universal exclusivity remains `BLOCKED`. The bearer token grants entire HTTP surface, not per-actor authorization; the HTTP actor string is caller asserted.
- **NO NEW KERNEL REQUIRED:** capability projection may compose Beads-native guarded transactions, existing provider-native receipts, and competent Control authority while preserving effects and no-retry semantics. But there is not yet a permitted proof of complete writer confinement or semantic equivalence with Product global revision/event-count/hash-chain.
- `NONE` Product effect; `NONE` shared Dolt effect; `NONE` new external provider operation. GitHub Actions itself executed only this bounded test, not a 033 provider retry.

## Next research, not initiated

**036 — B-first capability ownership and minimal causal authority boundary**: inventory the exact active Product consumers/invariants versus the qualifications 018/028/032/034/035, and compare (A) Beads informational/read projection + provider/Git as already authoritative vs (B) Beads-native guarded causal state behind an exclusively controlled writer identity. Quantify unavoidable authority/reconciliation adapter work and avoid new Kernel/daemon/ledger by default. Do **not** claim that a selected secure launcher contains privileged native writes. Any Product adoption remains for separate competent Product decision and validation.

Postflight Product `tools` and shared Dolt refs require independent verification outside this report.
