# TS EE E3 — Frozen 17-file inventory and four-packet coverage contract

Responsibility: `TS-EE-E3-WEBINLINE-COVERAGE-20261119-001`
Fixture commit: `6f94f83c53bd9f57149a27039dedece9a0a1ed71`
Fixture tree: `a9d9664c25ff9cdc2c43fd4b31f67cb7e2a664bf`
Evidence packets: four exact Git blobs listed below, created from source reads pinned to fixture commit.
Scope: all 17 fixture paths. This inventory proves **materialization** only, not semantic coverage by a reviewer.

| Path | Git blob | Git bytes | Pack |
|---|---|---:|---:|
| `fixture/docs/CONTRACT.md` | `b9e5b52c92965853a2128c73ed622ab14ebb85ce` | 1338 | 1 |
| `fixture/package.json` | `9cc36ad2deb6f4981ce5f21e07b4fef9ffc132f9` | 150 | 1 |
| `fixture/src/approval.mjs` | `7ff861fd69a9a3f40f85838c4cb1266b92236008` | 579 | 2 |
| `fixture/src/availability.mjs` | `d6d34842514b740921f419fe3bde9e5e6f1436c1` | 494 | 2 |
| `fixture/src/catalog.mjs` | `3eb1f37e502ad24f31fadbfa96f9410cc722b819` | 683 | 2 |
| `fixture/src/checkout.mjs` | `6f76602717d83232dc2e8173d119faabdb83ac13` | 819 | 3 |
| `fixture/src/fetchSupport.mjs` | `4adcc77e8ea8d874487ffd2f55a12bc7886ddd77` | 434 | 3 |
| `fixture/src/leadAudit.mjs` | `19e5c6f5893ece30c246d38c678ccdd24ebbd3e4` | 403 | 3 |
| `fixture/src/money.mjs` | `bc5a6a71e71c57ae78169b94cba09b1f4d0b63f9` | 629 | 1 |
| `fixture/src/roles.mjs` | `6c886d0129cb07d1b2799110eac201ccc335361c` | 426 | 2 |
| `fixture/src/searchState.mjs` | `847a813aa43184b5bcf7893e2199541471b4617d` | 656 | 3 |
| `fixture/src/sku.mjs` | `945043cf6b6ea64486be789153bc64126733fd45` | 675 | 1 |
| `fixture/src/stock.mjs` | `d7778cf5b66155834747ad520ca0f55f173a0d54` | 729 | 1 |
| `fixture/src/whatsapp.mjs` | `10d5416ebce88db1f07a37666e249bc5c45e0657` | 398 | 3 |
| `fixture/tests/happyPath.test.mjs` | `6937e0746e1fcdd8a0c11f6a315b2fc8cc984428` | 897 | 4 |
| `fixture/tests/http.test.mjs` | `0134251b21d0e40ec41d6f59bcbf652782cad5a0` | 441 | 4 |
| `fixture/tests/search.test.mjs` | `f1212effa8b7c93686354b72e0013af64b24070b` | 310 | 4 |

## Packet identity

- `PACK_1_OF_4.txt`: Git blob `05f58b6c64b7ccb4d4c06f82c1bca64faccb60a5`, 5 complete file bodies, 4513 reported text characters.
- `PACK_2_OF_4.txt`: Git blob `18c2e8db8ec7db43045dfd562079c854d1603c95`, 4 complete file bodies, 3046 reported text characters.
- `PACK_3_OF_4.txt`: Git blob `f7af522963c0cfc8f25d17f0b91244d873c878df`, 5 complete file bodies, 3749 reported text characters.
- `PACK_4_OF_4.txt`: Git blob `7b34f40e082ed58622e43c2c867b98bf508bfed7`, 3 complete file bodies, 2385 reported text characters.

## Reviewer conditions

The baseline and adaptive arms MUST share identical frozen fixture commit, tree, inventory, risk/contract and outputs. Baseline reads the 17 paths directly at the frozen commit; adaptive reads all four complete packets, and any individual file if packet materialization is suspicious. Neither can claim FULL_READ from a blob ID or manifest alone.

Return each path as `FULL_READ | PARTIAL | NOT_READ` with exact blob, a source-specific first-half and last-third observation (path+line+fact), plus four source-crossing relationships with exact paths. Explain all omissions. Return findings, advisories and asserted negatives with path:line evidence, and say tests NOT_RUN unless executed independently. Any omission means `COVERAGE_PARTIAL`; 0F0A never substitutes for coverage.

**Blindness:** `control/ORACLE_PRIVATE_DO_NOT_SEND_TO_REVIEWERS.json` is Control-only and **excluded** from all packets and reviewer instructions. No other branch/old reviewer outcomes should be inspected.

Metrics after both independent originals terminal: semantic coverage /17; latent defect recall /8 (oracle compared by Control), negative-control false positives /2; four cross-file relations; stated omissions; end-to-end custody; tool calls/elapsed/provider cost only when measured. No Product effect or automatic canonical adoption.
