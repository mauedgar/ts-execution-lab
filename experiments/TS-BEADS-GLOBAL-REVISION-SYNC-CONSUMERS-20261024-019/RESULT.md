# TS — Beads 019 | Consumidores reales de revisión global y puerto síncrono

**Experiment ID:** `TS-BEADS-GLOBAL-REVISION-SYNC-CONSUMERS-20261024-019`  
**Fecha:** 2026-10-24 (Jujuy).  
**Autoridad:** `NONPRODUCT_EXPERIMENTAL_ONLY` — no aceptación, decisión Product, concesión Developer, Phase 2 ni modificación de TaskCycles.  
**Resultado:** `PASS_NEGATIVE_CONFORMANCE_GAP_CONFIRMED`.  
**Disposición de investigación:** `INCOMPATIBLE_DROP_IN / RESEARCH_CANDIDATE_ONLY` — **no** reemplazar físicamente State Kernel, no crear un ledger mutable duplicado.

## 1. Entrada y referencias congeladas

- Handoff consumido: `mauedgar/ts-execution-transport@cf6aceb81b54559b3c5c7f48bc775c0d0ea69157:handoffs/TS-BEADS-EXPERIMENT-019-CONTINUATION-20261024-001/HANDOFF.md`, blob `1630ceb9405f2820bc10809679cf9ca7096ed103`.
- Informe de consolidación previo en Library: `/TS - Experimental Adoptions/Beads/Informe_avances_experimentacion_Beads_2026-10-24.md`, `libfile_ccb817987dc48191a5c3bd1ca024a017`. Los pilotos 001–018 siguen terminales e inmutables; no se reejecutaron.
- Exacto Product leído y ejecutado en **checkout separado read-only**: `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, árbol `8caa56d36f3efeba359bbbf65b158ffb01a19da6`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Original Code bajo prueba: `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js` blob `1e89df1a1885e3d0d24576338f0ffbd9b79890bc`, `src/operational-spine-v0/state-kernel-adapter.js` blob `b8970d6e78b77878a8cb8ef0fbd3c2568954c82e`, puerto tipado `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts` blob `2ab6e2655944fd98653d673d5d5a4dce69da3a06`, `src/state-kernel-v0/store.js` blob `f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a`.
- Oráculos reales inspeccionados: `tests/operational-spine-v0/reconcile-and-close-taskcycle.test.js` blob `b4fe6e032d1f0186964d2964d476a2b978553a24`; `tests/operational-spine-v0/taskcycle-lifecycle-capability.test.js` blob `70b0956318f99892e786edcbb868bf7c2283d9c5`. **No** se afirma que toda la suite Product haya sido ejecutada en 019. El original `017` ejecutó un subconjunto de 76 tests sobre un cutoff anterior.
- Dueño de escritura: `mauedgar/ts-execution-lab` rama experimental `experiment/beads-global-revision-sync-audit-20261024-019`; script `experiments/TS-BEADS-GLOBAL-REVISION-SYNC-CONSUMERS-20261024-019/qualification019.mjs` y workflow `.github/workflows/ts-beads-019-global-revision-sync.yml`. Un único efecto sintético disposable por workflow nativo; no otros pilotos reusados como efectos.

## 2. Resultado original y recibos

**GitHub Actions:** [run 40091996279](https://github.com/mauedgar/ts-execution-lab/actions/runs/40091996279), job `120866407998`, source commit exacto `f10078b3ad83c4cce4ba941b2e069b4751eb8651`, `completed / success`.

Logs terminales:

```text
TS_BEADS019=PASS;checks=18;async_drop_in=INCOMPATIBLE;native_global_revision=NOT_EQUIVALENT;Product=NONE
TS_BEADS019_RECEIPT=...beads019-global-revision-sync-result.json;status=PASS_NEGATIVE_CONFORMANCE_GAP_CONFIRMED
TS_BEADS019_NO_EXTERNAL_EFFECT=PASS;product=7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56;dolt=1f72d68797114170a97fee27641858f2e55a4571
```

**Artifact nativo original:** `ts-beads-019-global-revision-sync-receipt`, ID `12559362502`, ZIP digest `sha256:0996e1ab127c12e8e9f99517d2c1ac1a586aed6f2721983d45d6846930b36188`, caducidad `2026-10-31T11:59:00Z`. El JSON incluye el mapa de líneas/archivos de consumidores inspeccionados; los tests y este informe se conservan en Git sin depender de la retención del artifact.

El workflow fijó Beads 1.3.1 Windows ZIP hash `48cd82e1d3e311c9bf9a5d6d67ad1a8542ae13d4e20c5bfb527656c5e666af76` y Dolt 2.2.0 ZIP hash `7a4be662d5548bc63ae4ab6d8d93daa2a6681f3e076817908ac4a08d782eb6f6`. Todo en runner Windows/Dolt local y `git init` disposable **sin remotos**. HEAD Product y `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` contrastados antes y después, sin modificaciones.

## 3. Auditoría de consumidores — contratos reales (no propuestas)

| Consumidor / fuente | Garantía activa observada | Consecuencia para Beads |
| --- | --- | --- |
| `src/state-kernel-v0/store.js` | `FilesystemStateStore.mutate(expectedRevision)` exige una revisión de estado global; su `verify()` produce `revision` y `event_count`; cada evento tiene secuencia y vinculación previas | Row revision individual de Beads no equivale a un orden total de mutaciones de agregados |
| `src/operational-spine-v0/state-kernel-adapter.js` | Captura `verified.revision`, lee agregados/obligaciones con la misma `store_revision`, devuelve snapshot y mutation result inmediatamente | No basta con un `bd show` por issue ni con `Promise<Snapshot>` |
| `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js` | `prepare` compara `lifecycle.snapshot().revision` contra `input.expected_state_revision`; valida `event_count`, `observeInvocationBookkeeping().revision`; `invokeMutation` compara before/after/revision/event_id tras `invoke()` **sin await** | Consumidor funcional de revisión global, conteo de eventos, instantánea coherente y semántica síncrona |
| `src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts` | `snapshot(): TaskCycleLifecycleSnapshot`, `satisfyObligation(): LifecycleMutationResult` y `closeTaskCycle(): LifecycleMutationResult` tipados como retornos inmediatos (no `Promise`) | Cambiar a API async altera contrato existente; exige decisión/scope independiente, no una sustitución transparente |
| Originales `tests/operational-spine-v0/reconcile-and-close-taskcycle.test.js` | Ejercitan revisiones globales obsoletas, incrementos de eventos, UNKNOWN y efecto NONE/CONFIRMED, además de un test con mutación de revisión en medio | Una prueba exclusiva de Beads-native `CAS` no demuestra paridad con el conjunto de oráculos Product |

El scanner reproducible de 019 recorrió `src/`, `src-typescript/`, `scripts/`, `tests/` y `.github/workflows/`, registrando `path`, línea, símbolo y fragmento exacto. El inventario en artifact permite diferenciar llamadas runtime vs declaraciones TS vs pruebas. La auditoría de código estático **no demuestra la totalidad de consumidores dinámicos o instalados**.

## 4. Dos controles negativos ejecutados en 019

### A. Puerto asíncrono frente a receta síncrona

Se importó **el código Product actual** de `createReconcileAndCloseTaskCycleRecipe` y `requireTaskCycleLifecycleCapability`, no una emulación nueva del validador. El guard estructural aceptó el objeto del proveedor con métodos correctos cuyo `snapshot` retorna `Promise`. Cuando la receta Product ejecutó su preflight sintético, leyó `lifecycleSnapshot.revision === undefined` y retornó **BLOCKED** por `LIFECYCLE_REVISION_DRIFT:undefined`; un control síncrono con `revision=111` atravesó esa comprobación inicial. Ningún efecto Product se solicitó.

**Hallazgo:** cumplir solo nombres de métodos puede pasar la validación de forma, pero no preserva la semántica de ejecución del consumidor. Una interfaz async exige adaptación competente en el consumidor o calificación de bridge síncrono; el puerto existente **no** es drop-in.

### B. Revisión individual Beads frente a revisión global Product

Un almacén nativo y disposable Beads 1.3.1 creó `ts019-root` y `ts019-unrelated`, ambos sintéticos. Se obtuvieron revisiones nativas originales de ambas issues. Se mutó `ts019-unrelated` y su revisión avanzó. Un `batchApply` protegido con `expected_version` **anterior** de `ts019-root` fue aceptado, porque *esa issue* no había cambiado; así no se detectó la escritura concurrente sobre el otro agregado. En contraste, repetir el `expected_version` viejo de la *misma* issue fue rechazado. Una lectura CLI nueva tras detener el servidor confirmó que la mutación obsoleta sobre la misma issue no se aplicó.

**Hallazgo:** el CAS nativo por issue funciona, pero **no es el CAS global** requerido por el Kernel y por la receta actual. El fallo que habría que evitar no es una escritura rota; es un **falso OK semántico de precondición global** al mutar otro agregado. El native batch se probó con solo el issue target y sin ningún ledger nuevo: se preservó así el contraejemplo.

## 5. Opciones de arquitectura (costo de complejidad no medido)

| Ruta | Evaluación 019 | Costo/invariante |
| --- | --- | --- |
| **Usar Beads como índice operacional/adquisición de work graph; dejar lifecycle Product competente** | **RESEARCH_CANDIDATE_ONLY** | Reutiliza native ready/blocked/claim/persistencia; correlación de identidad con Git y Product obligatoria, sin autoridad automática |
| **Reemplazar directamente el adaptador State Kernel por API Beads asíncrona y row version por issue** | **INCOMPATIBLE_DROP_IN (demostrado)** | Viola revisión global y sync contrato; guard estructural insuficiente |
| **Mantener revisión global a través de una issue “root” y event_count mutable**, reconstruir reglas y sincronismo sobre Beads | **NO SELECCIONADO** | Reproduce un coordinador/ledger del estilo Kernel dentro de Beads; el estudio de simplificación no justifica añadir esa complejidad sin prueba de ahorro |
| **Cambiar contratos Product a atomicidad por conjunto/version vectors y async** | **DEFER_PRODUCT_DECISION** | Requiere análisis de invariantes, consumidores y autorización Product explícita; el experimento no puede decidirlo |
| **Retirar directamente RunStore/SQLite sin migrar datos** | **SEPARATE_CANDIDATE_ONLY** | El hallazgo estático de 017 debe verificarse en consumidores externos/dinámicos; ninguna eliminación en 019 |

No se probó que preservar global revision sobre Beads sea matemáticamente imposible. Sí se demostró que **los mecanismos nativos probados no suministran por sí solos** el contrato actual, y que una reimplementación oculta puede destruir el objetivo de simplificar.

## 6. Resolución experimental y próximos pasos

**019 terminal:** `PASS_NEGATIVE_CONFORMANCE_GAP_CONFIRMED` / `COMPLETE_WITH_LIMITATIONS`. Las **18/18 assertions PASS** incluyen controles negativos esperados; su PASS acredita que se observó la incompatibilidad, **no** compatibilidad o adopción.

**Decisión sugerida, no ejercida:** preferir Beads para *coordinación operacional no autoritativa* y continuar solo investigación de adaptadores con un consumidor exacto, sin calendario de migración de State Kernel. Frente lifecycle, proponer a Control mantener como caso separado hasta una necesidad real verificable; no añadir automáticamente orquestador, scheduler, otra SOT, gates ni autoridad.

Antes de cualquier cambio de Product, contrastar fuentes competentes del Beta Run y el contrato de una TaskCycle seleccionada; Project issue #34 no fue activada por este experimento. No migración física, ni accept/grant Product, ni cambios al Transport, ni publicación nativa como fuente de autoridad.

**Próxima investigación opcional no iniciada:** 020 podría calificar costo/ergonomía real de un lector Beads de backlog operacional en checkpoint Control (sin Product writes), mientras la equivalencia global de lifecycle permanece explícitamente diferida. Otra opción es cerrar esta línea de sustitución física con `INCOMPATIBLE_DROP_IN` e interconsulta competente; ambas requieren selección explícita de alcance experimental y no autorizan integración.
