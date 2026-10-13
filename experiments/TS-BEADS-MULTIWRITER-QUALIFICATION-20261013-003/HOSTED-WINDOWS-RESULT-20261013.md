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
