# TS Beads — Windows Dolt multiwriter empirical qualification (2026-10-13)

Status: **PASS_HOSTED_WINDOWS_MULTIWRITER_WITH_SEMANTIC_DUPLICATES**  
Scope: GitHub Actions `windows-2022` ephemeral only; NONE_PRODUCT; not native qualification of DESKTOP-3LJ0E54.

## Originals, no replay

- Attempt 1, GitHub Actions run [38444968673](https://github.com/mauedgar/ts-execution-lab/actions/runs/38444968673) / commit `b314d4e84613688ad2101d368b3fead0af34cce6`: terminal FAIL, accidental stdout contamination of archive path.
- Attempt 2, run [38445114291](https://github.com/mauedgar/ts-execution-lab/actions/runs/38445114291) / `b209a01bb6c4e76eee71fa438e53095a18e9b70d`: terminal FAIL at Beads server init because client parent directory missing; asset hashes/runtime versions PASS, no Beads issues created.
- Attempt 3, run [38445293168](https://github.com/mauedgar/ts-execution-lab/actions/runs/38445293168) / `6822ae0d55e244dd1f5c1aa1bd1b0ae3a5a11aec`: terminal PASS, pinned release assets, native Windows Dolt SQL server, `bd init --server`, two sequential synthetic create, two readback.
- Attempt 4, run [38445674670](https://github.com/mauedgar/ts-execution-lab/actions/runs/38445674670) / `905be5ed8da7c5c24040a63ed68217115bd61dfc`: terminal PASS, two concurrent job processes with barrier, overlapping operation intervals predicate true, both exit zero, four records. This run did not log the worker interval values separately (validation predicate only).
- Attempt 5, run [38445929222](https://github.com/mauedgar/ts-execution-lab/actions/runs/38445929222) / `57e9cf76c33760837b8efb826508a152bcfbff3b`: terminal **PASS**, native job `115464195450`, all worker timing data and duplicate test logged by the original provider.

## Proven identity

- Dolt Windows amd64 archive v2.2.0 SHA256 `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`, exact GitHub release official digest verified inside Actions.
- Beads Windows amd64 archive v1.3.1 SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`, verified inside Actions.
- Dolt SQL server: local `127.0.0.1` on isolated ephemeral Windows 2022 Actions runner, no user Product repository writes. Server stopped in test finalizer.

## Concurrent writers, instrumented original results

| Scenario | Worker | PID | Start UTC | End UTC | Exit |
|---|---|---:|---|---|---:|
| DISJOINT distinct issue creations | A | 5020 | 18:20:40.6942904 | 18:20:41.2045825 | 0 |
| DISJOINT distinct issue creations | B | 6248 | 18:20:40.7094972 | 18:20:41.2789008 | 0 |
| SAME_SOURCE | A | 820 | 18:20:42.2068502 | 18:20:42.7468981 | 0 |
| SAME_SOURCE | B | 1676 | 18:20:42.1085053 | 18:20:42.7231442 | 0 |

Times above are **2026-10-13 UTC** and come from original GitHub Actions job logs, not estimated. The native test verified interval intersection for each pair, exact independent job PIDs, exit 0 and DB readback.

Note: the first scenario's workers create **distinct Beads issue titles/IDs**, but both used the same `SOURCE_REF` marker in the test design. It proves simultaneous creation of distinct issues and server write ability, not a distinct-source-vs-distinct-title identity policy.

For the SAME_SOURCE case both used `SOURCE_REF=test://BEADS-SERVER-RACE/SAME-ORIGIN-001`. Readback found **2** records:
- `ts-execution-lab-2dw`
- `ts-execution-lab-7pp`

This is a verified negative result for **automatic semantic deduplication of a mere SOURCE_REF in descriptions** under simultaneous creation. It does **not** prove that Beads' dedicated `--external-ref`, explicit `--id`, `bd duplicates`, or other native mechanisms cannot implement idempotent source mapping. Those are separate unqualified adoption candidates.

## Limitations and next disposition

- Server multiwriter concurrency on **hosted Windows** is observed PASS, not a guarantee for any client concurrency load, cross-machine sync, automatic ChatGPT recovery, Product TaskCycles or native DESKTOP-3LJ0E54 host binding.
- The runner did not inspect cell-level Dolt commits or provider crash/durability under interruption; native GitHub Actions logs are the original execution evidence.
- Warning `beads.role not configured` arose on the ephemeral GitHub checkout, but synthetic writes succeeded (exit 0). It does not grant any Product role.
- Reuse-before-build next probe: native `--external-ref` semantics or explicit deterministic `--id` on the **same qualified temporary server surface**, rather than immediately authoring a new custom lock or dedup service.
- Local host `DESKTOP-3LJ0E54`: `dolt version` not available on PATH; transfer/pin the v2.2.0 archive through a qualified **non-Commander materialization** surface before performing a native-local qualification. Until then `HOST_BINDING_PENDING`. Pilot 003's original blocked runner remains **NOT_DISPATCHED**.

## Subsequent native identity alternatives — terminal empirical results

Version and isolated hosted Windows server surface identical to the above. No change to user host or Product.

- Run [38446455739](https://github.com/mauedgar/ts-execution-lab/actions/runs/38446455739), commit `f629c7c623b995c0b39948de002a06f5758aabcf`: **terminal FAIL** after obtaining two successful, overlapping `--external-ref` creates with same exact value and two distinct Beads records. A PowerShell report expression failed *after* these writes, before the intended explicit-ID test; do not claim the latter ran in this attempt. The two-record observation is preserved.
- Run [38446617378](https://github.com/mauedgar/ts-execution-lab/actions/runs/38446617378), commit `58d766d3c89b26b67a9dc77166935291a01a4db5`: **terminal SUCCESS**, job `115466561106`; all non-Product tests ran including two newly compared **native** flags.

### Native `--external-ref` race

Two simultaneous writer processes both used the same exact `--external-ref=test://BEADS-SERVER-RACE/EXTERNAL-REF-001` and also carried that ref in `SOURCE_REF=` description. Both creation calls exited **0**, and third-process readback returned **2 issues**. `TS_EXTERNAL_REF_NATIVE_CLASS=DUPLICATES_OBSERVED`.

**Conclusion:** using `--external-ref` alone did not enforce create-time at-most-once for that source in this version/binding. External references are useful for provenance and integration, but do not substitute a verified concurrency dedup strategy.

### Explicit deterministic `--id` race

Two simultaneous writer processes attempted **the same exact Beads ID** `ts-execution-lab-de7a6f3c` with `SOURCE_REF=test://BEADS-SERVER-RACE/EXPLICIT-ID-001`.

| Writer | PID | Start UTC 2026-10-13 | End UTC | Exit and meaning |
|---|---:|---|---|---|
| A | 7896 | 18:25:51.7768216 | 18:25:52.3705504 | **0**, created `ts-execution-lab-de7a6f3c` |
| B | 8168 | 18:25:51.8000183 | 18:25:52.4605976 | **1**, exact `already exists` conflict; original unchanged |

The test verified overlapping operation intervals, both native process receipts, and a fresh read via `bd list`. It found **1 issue**, exact ID `ts-execution-lab-de7a6f3c`: `TS_EXPLICIT_ID_SOURCE_MAPPING=ONE_RECORD_OBSERVED_WITH_CONCURRENT_CLIENTS`.

**Interpretation:** this is a supported experimental candidate for **at-most-one issue by derived stable ID**, using Beads' own ID collision behavior instead of inventing a global lock/ledger. It is **not** an idempotent `create` API returning the original on duplicate: the second call fails. A bounded consumer should map an exact immutable origin to a stable collision-resistant ID, and on a duplicate error perform an independent readback to verify that the existing object's immutable origin and intended meaning match before reusing it. Failure, hash collision, changed origin content, partial writes, missing receipts or `UNKNOWN` must remain reconciled, not treated as automatic success. A short example test ID does not qualify production collision resistance.

**DoD update:** Continuity under sequential writers and supported hosted Windows Dolt server mode with overlapping writers are now observed. Original `BEADS-CONCURRENCY-LOCAL-20261013-001` on `DESKTOP-3LJ0E54` is **still NOT_DISPATCHED**: a separate host-native server binding is not qualified. GitHub-hosted results do not supply an unattended ChatGPT wakeup or Product authorization.

Adoption assessment next: compare (a) embedded-mode Beads with a single operational writer versus (b) version-pinned Dolt server with concurrent native explicit-ID at-most-once. Choose lower total complexity; neither becomes Product canonical without competent owner/consumer equivalence check. Explore `--claim`, molecules, formulas, wisps, merge-slot and handoffs as **replacement candidates** before writing custom orchestration.
