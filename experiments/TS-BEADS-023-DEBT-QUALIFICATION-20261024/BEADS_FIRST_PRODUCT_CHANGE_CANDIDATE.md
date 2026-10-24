# Tecnotron — Propuesta experimental de reestructuración Beads-first

**Documento de investigación, NO decisión Product ni contrato canónico.**  
**Base:** [Beads 023 RESULT](RESULT.md); Beads 019–022, originales con SHAs en esos informes.  
**Product todavía competente:** `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`.

## Propuesta

**Dar prioridad a la funcionalidad nativa comprobada de Beads** — almacenamiento Dolt, dependencia, read-only GET revision, CAS de issues y batch transaccional — y rediseñar interfaces de consumidores seleccionados **asíncronos y de concurrencia causal**, en lugar de construir un reemplazo que emule exactamente el State Kernel.

No confundir esta preferencia arquitectónica con autorización para reemplazar el lifecycle vigente: issue Beads abierta/ready/cerrada no es TaskCycle iniciada/cerrada, Independent Review, Developer aceptación ni concesión de autoridad.

## Cambios que la evidencia justificaría someter a Product

1. **Autoridad explícita en preflight de cierre.** El original `reconcile_and_close_taskcycle` permite `READY` con evidencia Developer recién reconciliada como `REJECTED` sobre un estado genuinamente alcanzable de obligaciones satisfechas. Propuesta: exigir explícitamente `developer_acceptance.disposition === ACCEPTED` donde corresponda a cierre, con un contrato claro de vigencia/correspondencia de evidencia. Un guard de **tres líneas**, aplicado en memoria, fue positivo (11/11); no es parche aceptado. Antes de integración: revisión independiente de semántica y casos de contradicción/revocación, alcance de documentación/callers, y negativos fuente-nativos.
2. **Escritor único *de hecho*, no un rol/orquestador nuevo.** La ruta de mutación de aristas que resulte seleccionada debe hacer `update root metadata + dep_add` bajo una sola transacción `batchApply`, usando `expected_version` del root. Una operación de cierre/admisión debe proteger el **read-set causal descubierto completo** en la misma transacción nativa. Prohibir técnicamente o aislar las rutas de escritura que omiten ese contrato (por ejemplo `bd dep add` directo). El experimento reproduce bypass: CLI agrega edge sin tocar `root.revision`; un CAS sobre la revisión antigua **lo acepta**. Sin enforcement contra bypass la propuesta permanece bloqueada.
3. **Simplificación del modelo de versiones.** No conservar `global store_revision` por inercia para nuevos consumidores, si un contrato versionado por sujetos causales efectivamente protege sus invariantes. 021–022 ejecutaron el consumidor original transformado en memoria y 022 midió 42,5 % menos llamadas para mismo workload de prueba al usar `GET(...).revision`, conservando CAS. No equivale a throughput ni reducción neta de código.
4. **Semántica de efectos fuera de Beads.** El contrato Tecnotron para `NONE/CONFIRMED/UNKNOWN`, identidad Git/proveedor y no-blind-retry permanece explícito. 023 recuperó un artifact externo real de GitHub después de ocultar un acuse sintético; provider real y lectura independiente, no timeout real. Beads no confiere ni reemplaza autoridad Product.
5. **Migración por consumidor y eliminación, no duplicación.** Priorizar reutilizar Beads para read-only backlog / grafo operacional no autoritativo como posible primer consumidor; para lifecycle autoritativo exigir primero cierre causal y revalidación de evidencias. Inventariar los consumidores instalados de RunStore/SQLite/Kernel antes de retirar interfaces. No crear un segundo journal global Beads, scheduler, orquestador o pipeline de aprobación por defecto.

## Arquitectura propuesta en capas mínimas

- **Datos operacionales:** Beads/Dolt para graph, status operativo, etiquetas, ready, claims y persistencia.
- **Frontera de mutación causal:** una ruta nativa acotada, con autorización explícita en Control y atomicidad issue-update/dep_add, protegida de bypass. No implica un actor o scheduler separado por defecto.
- **Semántica Product:** responsabilidad, selección, fase, autoridad, IR, aceptación, cierre y reconciliación de efectos originales siguen en Tecnotron bajo autoridad competente. Se permiten nuevos puertos asíncronos si la decisión Product los selecciona explícitamente.
- **Evidencia portable:** sujetos Git exactos, receipts verificables y handoffs; publicación y actualizaciones operacionales no implican aceptación.

## Precondiciones materiales **para recomendar** adopción autoritativa

- Calificar la ruta de escritura elegida **en todos los escritores relevantes** y demostrar técnicamente que no se puede modificar una arista relevante sin invalidar el token causal o bloquear la operación.
- Calificar read-set dinámico, aparición/eliminación de aristas, concurrencia multi-actores, fallas reales de proveedor y composición de evidencia competente, sin repetir efectos UNKNOWN.
- Revisar independientemente el guard Developer/REJECTED, con corpus fuente-nativo de observaciones vigentes y pasadas.
- Demostrar reducción neta de complejidad, recuperación y compatibilidad histórica de cada consumidor seleccionado; no migrar retrospectivamente acciones/fallos originales.

**Decisión propuesta para Control:** mantener `State Kernel` operativo allí donde sigue siendo autoridad, **dar prioridad de investigación y posible evolución futura a Beads-first**, y no conceder aún `READY_FOR_PRODUCT_ADOPTION` para lifecycle o graph autoritativo por el bypass demostrado.

Esta propuesta no modifica la SOT, ni selecciona #34, ni inicia TaskCycles, ni autoriza Phase 2, IR o integración. Sólo Control/autoridad Product competente puede convertirla en decisión e implementación canónica.
