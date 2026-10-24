# TS — Beads 020 | Beads-first: prueba de rediseño de contratos y dependencias

**Responsabilidad:** investigación aislada bajo `@Autónomo Experimental`. **Fecha:** 2026-10-24.  
**Disposición:** `PASS_SCOPED_ASYNC_MODEL_WITH_LIMITATIONS / COMPLETE_WITH_LIMITATIONS`.  
**Clasificación:** `BEADS_FIRST_ARCHITECTURE_CANDIDATE_ONLY`; autoridad Product **NONE**, sin TaskCycles reales ni IR/aceptación/Developer grant, sin implementación canónica.

## 1. Cambio de hipótesis

El resultado negativo de 019 no demuestra que Tecnotron deba conservar eternamente un `store_revision` global o un API síncrono. Demuestra que **Beads no es un sustituto drop-in** de ese diseño. Por autorización del usuario se investigó la arquitectura inversa: **rediseñar contratos experimentales para usar primero las capacidades nativas de Beads**, no reconstruir State Kernel dentro de Beads.

La SOT es competente para el Product **vigente**; sus interfaces pueden proponerse para sucesión mediante autoridad competente futura. Esta investigación no la reemplaza, no resuelve deuda histórica y no inicia #34.

## 2. Sujetos exactos y ejecución

- Product reobservado, read-only: `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, árbol `8caa56d36f3efeba359bbbf65b158ffb01a19da6`. SOT `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, current-state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479` (tree `089a1a797560204b73a3fbb52e06fc819cd7fc1a`), nueva rama aislada `experiment/beads-first-contract-redesign-20261024-020`.
- Script ejecutado `experiments/TS-BEADS-FIRST-CONTRACT-REDESIGN-20261024-020/native020.mjs`, workflow `.github/workflows/ts-beads-020-first-contract-redesign.yml`. **Único** intento nativo, sujeto `0a562b802f96082977977e3fe717a252d20173bb`. No reejecución de 001–019.
- [GitHub Actions run 40093123281](https://github.com/mauedgar/ts-execution-lab/actions/runs/40093123281), job `120869721396`, `completed/success`. Logs originales:
  - `TS_BEADS020=PASS;checks=24;async=scoped;global_revision=NOT_REQUIRED_BY_EXPERIMENTAL_CONTRACT;Product=NONE`
  - `TS_BEADS020_RECEIPT=...beads020-native-first-result.json;status=PASS_SCOPED_ASYNC_MODEL_WITH_LIMITATIONS`
  - `TS_BEADS020_NO_EXTERNAL_EFFECT=PASS;product=7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56;dolt=1f72d68797114170a97fee27641858f2e55a4571`
- Archivo original del workflow `ts-beads-020-async-scope-receipt`, artifact `12559399429`; digest ZIP **verificado independientemente** `sha256:09bd3109f1f5b5bb73d317db3fb5c34663e22dbb758514a404e39639f2bfe8ea`, expira `2026-10-31T12:15:48Z`. Dentro está `beads020-native-first-result.json`: **24 PASS**, detalles de dos negativos y token de revisión protegido.
- Beads `v1.3.1` ZIP SHA256 `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76`, Dolt SQL Server `v2.2.0` ZIP SHA256 `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`. Git local disposable sin remotos, API/DB nativos. Shared remote `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` y Product HEAD reconfirmados sin cambios por el workflow.
- Hipótesis de opciones previa y código fuente editable: `experiments/TS-BEADS-FIRST-CONTRACT-REDESIGN-20261024-020/ARCHITECTURE-HYPOTHESES.md` y `native020.mjs` bajo esta rama; no se escribió en repositorio Product.

## 3. Qué se ensayó nativamente, distinto de los pilotos anteriores

Este experimento **no** reproduce 019. En 019 se confirmó la diferencia entre CAS por issue y revisión global. Aquí se prueba una **alternativa contractual explícita** basada en las issues **realmente relacionadas** con una decisión, con función asíncrona y sin segundo ledger mutable.

Tres registros nativos sintéticos: `ts020-root` (candidato), `ts020-gate` (dependencia causal) y `ts020-unrelated` (trabajo no relacionado). Para efectos de un *fixture experimental*, se admite un `authorityFixture` tipado `TS020-SYNTHETIC_ONLY`; esto **no** concede autoridad Product y **no** valida aceptación real.

**Resultados 24/24:**

1. Los contratos Product actuales aún se observaron con revisión global y retornos síncronos; el motor de prueba no editó esos archivos.
2. Una llamada `async decide(...)` devuelve una Promise, y usa operaciones nativas `batchApply` con `expected_version` de **dos issues relevantes**.
3. La ausencia de autorización en el fixture se rechaza antes de invocar el batch. El candidato queda intacto.
4. Concurrencia relevante: un escritor sintético avanza `ts020-gate` después de la lectura; la transacción `root + gate` con la revisión anterior **se rechaza atómicamente**, sin escribir parcialmente `root`.
5. Concurrencia irrelevante: cambia `ts020-unrelated` después de la lectura de `root + gate`. La transacción de ambas issues causales **se acepta**; el cambio ajeno no introduce un falso conflicto global.
6. Repetir el vector de revisiones ya usado **se rechaza**. Esta protección no es idempotencia de un proveedor externo ni confirma un ACK perdido.
7. Tras detener el servidor, procesos CLI Beads independientes observan el estado terminal sintético y la marca exacta de la dependencia.

**Resultado adicional cuantificado por el recibo original:** el guard de `ts020-gate` fue un `update` con el **mismo valor de metadata existente** y `expected_version` correcto. Se aceptó como parte del batch, y el token `3669443674536019650` **no cambió** (antes y después). No observamos write amplification de versión sobre esa issue *en esta ejecución específica*. No equivale a una garantía de no-op bajo todas las versiones, concurrencias, journal/evento o proveedores: esa calificación está pendiente.

## 4. Arquitectura candidata, no una sustitución canónica

**Beads-first**: usar un único almacén de issues/Dolt para el work graph, dependencias, claimed work, checkpoint, etiquetas/metadata, CAS sobre filas y batches. Usar operaciones **asíncronas** con tokens de revisión de las issues en el read-set causal conocido, no una revisión global que se modifique con cualquier agregado ajeno. No introducir otro estado mutable solo para emular `State Kernel`.

**Tecnotron sigue poseyendo la semántica necesaria:** aceptación y Developer grants, Independent Review, identidad exacta de la operación/attempt Git/proveedor, correspondencia de recibos, `NONE/CONFIRMED/UNKNOWN` y no blind retry. Datos `bd ready/close` son **indexación operacional**, no transiciones canónicas por sí solos. Evidencia inmutable verificable puede vivir en Git/Transport, no depende exclusivamente del journal local de Beads.

| Diseño | Calificación y coste |
| --- | --- |
| Imitar el contrato anterior sin modificar Product | `INCOMPATIBLE_DROP_IN` (019): globals y sincronía no son nativos de Beads |
| Rediseñar contrato de consumidores asíncronos y CAS por read-set | **`BEADS_FIRST_ARCHITECTURE_CANDIDATE_ONLY`**: 020 demostró el mecanismo sintético y sus conflictos relevantes/irrelevantes |
| Agregar issue global mutable actualizada por todas las operaciones | No seleccionada: parece reconstruir la misma complejidad que se quiere retirar |
| Retener lifecycle actual y adaptar solo vistas operacionales primero | Alternativa escalonada prudente, especialmente con Beta Run activo; todavía requiere cuantificar ganancia neta |

### Futuras dependencias y posibles retirements que sí debemos cuestionar

- `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts`: el contrato sync/global puede ser candidato explícito a versión asíncrona/scoped en futuras responsabilidades, **sin** alterarlo hoy.
- `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js`: es un consumidor real que exige `revision` global, `event_count` y acknowledgements inmediatos. Un rediseño debe modificar sus precondiciones, efectos, controles de evidencia y negativos, no solo cambiar nombre de proveedor.
- `src/operational-spine-v0/state-kernel-adapter.js` y `src/state-kernel-v0`: eventual retiro solo al demostrar correspondencia Product de todos los consumidores seleccionados y disponer continuidad histórica. El resultado 020 **no** habilita eso.
- `RunStore/SQLite`: investigar eliminación directa e independientes consumidores, sin recrear RunStore dentro de Beads.

## 5. Limitaciones materiales y próximo frente propuesto

El read-set puede ser correcto únicamente si su **cierre causal es completo**: deben identificarse todas las issues cuyo estado influye en la decisión. 020 ejercitó solo dos issues relacionadas y una ajena, sin resolver descubrimiento de dependencias dinámicas, instalaciones de plugins, permisos, segundo actor remoto, conflicto multi-harness ni un proveedor externo con ACK realmente perdido.

El control `authorityFixture` es sintético; **no** prueba una autorización Product ni la validez de un cierre TaskCycle. No se ejecutaron suites completas originales del consumidor Product con un adaptador Beads-first, ni se verificó compatibilidad tipada de todos los callers; esto exige un **rediseño deliberado** bajo autoridad competente. No se midieron costo/latencia netos, reducción de archivos o horas de mantenimiento.

**Conclusión experimental:** el rediseño Beads-first merece prioridad investigativa, pero no exclusividad dogmática. Los resultados 019 y 020 son compatibles: **Beads es incompatible como reemplazo drop-in de los contratos actuales; un contrato asíncrono y versionado por dependencia sí funciona en el caso sintético probado**.

**Siguiente experimento recomendado (no iniciado):** 021 — adaptar un **consumidor Product concreto en copia experimental aislada**, con su fixture de evidencia y originales tests negativos reformulados conscientemente para el nuevo contrato; validar la selección correcta del read-set, errores `UNKNOWN`, caída/readback y coste/beneficio en líneas, llamadas y writes, sin editar Product. Comparar con la alternativa de sustituir solo el índice operacional primero. Publicar una propuesta de cambio Product **después** de suficiente evidencia, sin suponer que el canon histórico es diseño permanente ni declararlo reemplazado por una prueba sintética.

**Estado de efectos:** Git lab branch experimental únicamente; Product `tools@7a722594…` y shared Dolt ref `1f72d687…` intactos. #34 no iniciada, sin Phase 2 ni nuevas gates/roles/orquestadores por defecto.
