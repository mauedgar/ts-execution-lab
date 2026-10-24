# TS — Beads 023 | Cierre de deudas, evidencia contradictoria y recuperación del proveedor

**Fecha:** 2026-10-24.  
**Responsabilidad:** Beads experimental, aislado, bajo @Autónomo Experimental.  
**Disposición:** `COMPLETE_WITH_MATERIAL_ADOPTION_BLOCKER` — experimentación terminal, propuesta Product todavía **NO ADOPTADA**.  
**Autoridad:** `NONPRODUCT_ONLY`; ningún cambio a Product, TaskCycles reales, State Kernel canónico, GitHub Issues Product ni Dolt compartido.

## Identidad de fuentes, no deriva

- Product observado: `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`, `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`, rama aislada `experiment/beads-023-closure-authority-dependencies-provider-20261024`.
- Parent 022 `mauedgar/ts-execution-lab@32f86383c979ba015024d0e70ccd98c61858e132:experiments/TS-BEADS-OBLIGATION-AUTHORITY-EFFICIENCY-20261024-022/RESULT.md`.
- Shared Dolt remoto protegido: `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, verificado sin cambios en las ejecuciones nativas.
- Beads `v1.3.1`, Dolt `v2.2.0`, sólo stores descartables Git sin remotos y repositorio Product en clone detached read-only.

## Matriz terminal de sujetos exactos

| Operación acotada | Original run/commit | Terminal | Evidencia |
| --- | --- | --- | --- |
| Fuente-nativa Product + GitHub proveedor externo publicado una vez | [40104370902](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104370902), `f34df4c706c92e66a850a50a6f55d2315400736f`, job `120902884949` | **SUCCESS**, 9/9 PASS, publicación única y deferred durable join | Authority artifact `12564401090`; provider artifact `12564166868` |
| Primer lector causal, sin metadatos nativos seed | [40104322456](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104322456), `97143d8bb690dc4bf0263c63d42728fbbda05d5c`, job `120902741314` | **FAIL** `MISSING_DETAIL_ts023-root` por lector experimental demasiado estricto; no se evaluó la carrera | Artifact `12564530519` preservado |
| Descubrimiento de grafo causal corregido | [40104466243](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104466243), `5e1add19b0748bc5bf7f06e4a6cbe932bc7b6be0`, job `120903166603` | **SUCCESS / 17/17** con **GAP material** en expansión del grafo | Artifact `12563759008` |
| Mitigación de escritor causal atómico, distinta operación | [40104741250](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104741250), `34d8f2969d33ea5d4ca4b580182746c61b1f1a46`, job `120903976787` | **SUCCESS / 27/27** — mitigación **condicionada**; conserva contraejemplo de ruta sin control | Artifact `12563878788` |
| Calificación de guard de autoridad en memoria | [40104867163](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104867163), `9cdf1bb6e223b476bb8f9127aed7eab0a0be5462`, job `120904357049` | **SUCCESS / 11/11** | Artifact `12564725164` |

**No hubo retry ciego de efectos reales**, especialmente del artifact externo. Los ensayos con fallas son intentos terminales distintos y se conservaron.

## Deuda 1: rechazo Developer tras obligaciones satisfechas

Se utilizó el **State Kernel original auténtico** en Linux, con FS durable en carpeta descartable. Se ejecutaron las primitivas Product reales `create`, `transition ACTIVE` y `satisfy` para las cinco obligaciones de una TaskCycle sintética, adjuntando autoridades reviewer/developer/effect vía referencias válidas. Se llegó a `ACTIVE` con las cinco `SATISFIED` y `authority:developer-001` asociada; no se utilizó una instantánea inventada para ese estado.

Sobre ese estado **realmente alcanzable**, la receta Product original e intacta `createReconcileAndCloseTaskCycleRecipe` devolvió **`preflight READY`** ante una nueva observación Developer sintética verificable con `disposition=REJECTED`. Esta discrepancia procede del consumidor original y no de Beads. El preflight no mutó ni cerró la TaskCycle.

En una **variante en memoria, exclusivamente investigativa**, se añadió un control tras la reconciliación para exigir `reconciliation.observed_facts.developer_acceptance.disposition === 'ACCEPTED'` antes de disponer el cierre. La variante:
- `REJECTED` tras obligaciones satisfechas → **BLOCKED**;
- `ACCEPTED` → **READY**;
- 11/11 controles sobre tienda Product fuente-nativa → **PASS**.

**Fuente nativa original:** artifact `12564401090`, ZIP sha256 `62e93e9289d5c6037e1bab0c180e39fe04ac169c3c090aabd6df25f8959e1ae9`, JSON sha256 `4a15b5b3651349cf8da0ea63a723095fcc8dc91fcacef771e88f37e5b91c8e9a`.  
**Variante corregida en memoria:** artifact `12564725164`, ZIP sha256 `dcb46ce0a1600597692abd82c6d9b5631518ce70bde2998317cb707878dcc314`, JSON sha256 `4a0534dc3366df1a782cf13b770a4add56219c3e04f7c710a2a0267375706686`.  
Código: `source-native-authority.mjs`, `source-native-authority-guard.mjs`, `fixtures023.mjs`.

**Límite:** la alcanzabilidad del estado source-native quedó probada, **no** la admisibilidad Product real de presentar después evidencia contradictoria con una aceptación previa, ni un cierre indebido histórico. El fix de tres líneas es **propuesta de semántica**, no cambio canónico, aceptación Product o Developer grant. Debe pasar review competente y regresiones relevantes.

## Deuda 2: descubrimiento transitorio del read-set causal

Beads nativo descubrió, mediante `GET /v0/beads/issues/{id}`, el grafo `root → gate → ancestor`. Un cambio a `ancestor` tras snapshot fue rechazado con CAS nativo de las tres issues; ninguna mutación parcial de `root`. Un cambio en issue independiente **no** impidió transacción sobre el conjunto causal.

**Hallazgo crítico reproducido:** un escritor ejecutó `bd dep add root late --type related` **después** de observar el conjunto causal. Se encontró nueva arista en el GET siguiente, pero la revisión **de root no avanzó**. Una transacción `batchApply` con versiones del conjunto anterior fue **aceptada (HTTP 200)**, ignorando el nuevo miembro: `GAP_NATIVE_GRAPH_EXPANSION_NOT_ATOMIC_WITH_ROW_GUARDS`. Esto invalidó la premisa de que el mero `expected_version` del root sella el grafo y **bloquea la adopción general**.

Receipts originales:
- Caso negativo 17/17: artifact `12563759008`, ZIP sha256 `c9b9c2c9d45596ec9b815cca52cb09d5f60ca9626ada4c76937bb9ccbd4b6b50`, JSON sha256 `570966abdda2ddcf502a1f3c2d3e44d5f15039c7159ceef2f3a2594e017f7e6e`.
- Código `native-graph023.mjs`; el hallazgo se preserva **sin redefinir PASS como equivalencia**.

### Mitigación nativa condicional probada

Un escritor controlado llamó **una sola transacción** `POST /v0/beads/issues:batchApply` con:
1. `update` a la issue raíz, `expected_version` previamente leído y cambio de marca semántica de grafo en la metadata **de esa misma issue**, produciendo nueva revisión raíz.
2. `dep_add` de la nueva arista, en el mismo batch atómico.

27/27 verificaciones PASS: nueva arista visible; revisión raíz avanzó; otro escritor que llevaba la revisión anterior no pudo añadir su arista (rollback de toda la transacción); un efecto con revisión anterior fue rechazado. **No se añadió un ledger global ni un coordinador aparte.**

**Limitación ineludible:** `bd dep add` usado directamente fuera del escritor controlado sigue pudiendo crear aristas **sin** cambiar revisión raíz, como demostró el contraejemplo original. El requisito de una ruta de escritores exclusivos/contractuales **no está hoy impuesto por Beads a todos los clientes**. La mitigación es válida sólo con exclusividad efectiva de la ruta de mutación del grafo y protección contra bypass. No habilita ejecución automática Product.

Artifact `12563878788`, ZIP sha256 `859ee8f4f65262753f2a205160068c4e1c0cbd890e761875ac2e3fc9128a1330`, JSON sha256 `7f99f8badb776bbeca21d8a1fea89fa0fd17e94baecfd6d6d87270bd2933c0b4`.
Código `native-graph023-guarded.mjs`. Disposición `GRAPH_EXPANSION_REQUIRES_EXCLUSIVE_CAUSAL_EDGE_WRITER_CONTRACT`.

## Deuda 3: efecto externo real con ACK no consumido

GitHub Actions **publicó una única vez** un artifact externo nativo; no era un stub local. El step siguiente ocultó al consumidor los outputs del upload; posteriormente, ChatGPT realizó **deferred durable join** mediante GitHub API del run exacto, descargó su ZIP, verificó SHA-256 y validó payload interno. **No se repitió el upload ni se fabricó un recibo de ejecución.**

- Original run `40104370902`; provider artifact `12564166868`, `ts-beads-023-external-provider-40104370902`.
- ZIP SHA256 `8331b34121a1a2dcb3df9b08d3bd00cf9cf851abf79590024a0292e9d2f5bd3a`.
- Payload JSON SHA256 `14bd7b15c34957c4cd851be1fcef01d7e0bf654a45469741308e36d3360822b5`.
- `attempt_id: TS-BEADS-023-ORIGINAL-GITHUB-ARTIFACT-40104370902`, `source_git_subject: f34df4c706c92e66a850a50a6f55d2315400736f`; `provider: GITHUB_ACTIONS_ARTIFACT`, `status: PUBLISHED_ONCE`, `product_effect: NONE`.
- **Disposición:** `EXTERNAL_EFFECT_CONFIRMED`, exact original provider publication; no repeat.

**Límite:** la falta de ACK fue simulada intencionalmente; no fue una desconexión real del proveedor ni prueba de conciliación de cualquier GitHub Issue, PR o implementación. Se acreditó un efecto **real** de GitHub Actions Artifact y su recuperación por identidad.

## Balance de deuda e invariantes

| Frente | Evidencia 023 | Disposición |
| --- | --- | --- |
| Alcanzabilidad de TaskCycle original con obligaciones satisfechas | **9/9 fuente-nativo** | Calificada; la admisión de nueva evidencia contradictoria requiere revisión Product |
| Posible guard ACCEPTED al cierre | **11/11 memoria original + variante** | Propuesta concreta de 3 líneas, no adoptada |
| Cierre transitivo de dependencias conocidas | **17/17 negativo/positivo** | El CAS nativo protege filas conocidas |
| Expansión dinámica no declarada del grafo | **Unsafe contraejemplo reproducido** | **BLOQUEO MATERIAL de adopción general** |
| Escritor nativo de aristas controlado con revisión raíz | **27/27 PASS** | Mitigación **condicionada a exclusividad del escritor**; falta enforcement/qualificación de consumidores |
| Efecto externo y pérdida de ACK | 1 artifact genuino, recibo recuperado y verificado | `EXTERNAL_EFFECT_CONFIRMED`, sin retry |
| Ahorro de complejidad Product y migración de consumidores instalados | 022 reducción medida de llamadas, no migración instalada | **DIFERIDO**, no calculada reducción neta |

**Conclusión:** la experimentación 023 cumplió la responsabilidad de caracterizar y ensayar reparaciones nativas, pero reveló una condición crucial que no puede eliminarse fingiendo equivalencia. Beads-first tiene prioridad como **candidato arquitectónico** (async, native CAS, batching, work graph), no como reemplazo autoritativo inmediato. El resultado 023 es `COMPLETE_WITH_MATERIAL_ADOPTION_BLOCKER`, no `READY_FOR_PRODUCT_ADOPTION`.

El paso recomendado es entregar una propuesta explícita a Control: (a) guard de aceptación Developer con revisión independiente; (b) contrato de **único escritor causal** para cambios de dependencias o alternativa técnicamente equivalente, verificada frente a bypass; (c) migración experimental de un consumidor de lectura no autoritativo antes de cambios reales de TaskCycle; (d) plan de compatibilidad histórica. No introducir orquestadores, schedulers, roles o nuevas gates por defecto; reemplazar/reducir duplicaciones sólo tras justificar necesidades y autoridad.

**Efectos:** no Product, no modificaciones de `tecnotron-ai:tools`, no TaskCycle #34, no PR Product, ningún efecto de proveedor repetido y shared Dolt intacto.
