# TS EE E3 — Frozen 17-file inventory and four-packet coverage contract

Responsibility: `TS-EE-E3-WEBINLINE-COVERAGE-20261119-002`
Fixture commit: `ed1e6e50402d74926821cce28f7e435989dc18c4`
Fixture tree: `0e5fe46cbc65afdcb40f5f3d7770f36124225a92`
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

- `PACK_1_OF_4.txt`: Git blob `b5429fe179fd10577592942a74499562e48a4197`, 5 complete file bodies, 4513 reported text characters.
- `PACK_2_OF_4.txt`: Git blob `b4897975b7242e4a54d7b90303b7fcda7225e415`, 4 complete file bodies, 3046 reported text characters.
- `PACK_3_OF_4.txt`: Git blob `207c69fc303acabb4def8d9091f94ab5cacb19b3`, 5 complete file bodies, 3749 reported text characters.
- `PACK_4_OF_4.txt`: Git blob `8068f36833785d937f5e5005085a7a93520f97de`, 3 complete file bodies, 2385 reported text characters.

## Reviewer conditions

The baseline and adaptive arms MUST share identical frozen fixture commit, tree, inventory, risk/contract and outputs. Baseline reads the 17 paths directly at the frozen commit; adaptive reads all four complete packets, and any individual file if packet materialization is suspicious. Neither can claim FULL_READ from a blob ID or manifest alone.

Return each path as `FULL_READ | PARTIAL | NOT_READ` with exact blob, a source-specific first-half and last-third observation (path+line+fact), plus four source-crossing relationships with exact paths. Explain all omissions. Return findings, advisories and asserted negatives with path:line evidence, and say tests NOT_RUN unless executed independently. Any omission means `COVERAGE_PARTIAL`; 0F0A never substitutes for coverage.

**Scope:** Only the 17 fixture paths are authorized. Other branches, control artifacts and earlier reviews are outside the input.

Metrics after both independent originals terminal: semantic coverage /17; independently supported defect findings (compared later by a separate Control oracle), negative-control false positives /2; four cross-file relations; stated omissions; end-to-end custody; tool calls/elapsed/provider cost only when measured. No Product effect or automatic canonical adoption.
