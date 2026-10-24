# TS — Beads 024 | Dictamen de Control experimental

**Identidad:** `TS-BEADS-024-EXPERIMENTAL-CONTROL-VERDICT-20261024-001`.  
**Estado:** `QUALIFIED_FOR_EXPERIMENTAL_INFORMATIONAL_READ_REUSE_WITH_LIMITATIONS`.  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`; **Product authority NONE**.  
**Fecha de corte:** 2026-10-24. No concede aceptación Product, Developer grant, Independent Review, integración canónica ni permiso de Phase 2.

## Entrada congelada

Se consumió la evidencia portable del 023: `mauedgar/ts-execution-transport@8231c0898c6ee6e9585ae946dacde13928d4c013:results/TS-BEADS-023-TXT-PORTABLE-CARRIER-20261024-001/EVIDENCE_CARRIER.txt` (`IR-TXT-CARRIER/1`, blob `df6a1c355635eee3ca5a88283eb8b3504457b9c3`).

Product vigente reobservado al seleccionar el experimento: `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`; laboratorio `main@b30241201d07a9590e1e845abe767cdcf9921479`. Producto no modificado, shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` inalterado según Actions.

## Selección experimental y resultado exacto

**Selección:** estudiar un consumidor de solo lectura sobre Beads, sin bloquear el progreso por la deuda separada de escritores de dependencias autoritativas. La hipótesis fue que dos recorridos consecutivos del grafo permitirían **informar** una vista estable o reportar inconsistencia ante cambios, pero nunca autorizar acciones.

**Intento 1 original:** [Actions 40109051604](https://github.com/mauedgar/ts-execution-lab/actions/runs/40109051604), source `9788f4f141e11644fa09e200343903da7d04163e`: test Beads nativo 18 PASS, pero **workflow FAIL** por falta de la variable `PRODUCT_ROOT` en el siguiente paso de transporte. El JSON original no quedó publicado; no inferir cierre terminal de ese primer workflow a partir del PASS del subpaso.

**Intento 2 distinto y acotado:** [Actions 40109272872](https://github.com/mauedgar/ts-execution-lab/actions/runs/40109272872), source `1f96415dc9c8faf94bf5f0ba42c9da2a8b07f28e`; **workflow SUCCESS**, 18/18 verificaciones PASS, resultado `PASS_NONAUTHORITATIVE_READ_MODEL_WITH_RACE_DETECTION`. No reejecutó efectos de proveedor de 023 ni otros pilotos.

**Recibo durable original:** `mauedgar/ts-execution-lab@95875081b15491a4ce10716c5c91ae4eac8f65bf:transport/TS-BEADS-024-READ-MODEL-20261024-001/EVIDENCE_CARRIER.txt`; blob `0bb53ee9b59f25ac288844ae7ab7594a5dee32d4`, SHA-256 `f48488da797658424401816d00986d8745bec7b152f559787bd639c2d56f475b`, 10.191 bytes. Formato existente `IR-TXT-CARRIER/1`, tres miembros: `CONTROL_EXPERIMENTAL.txt`, `evidence/ORIGINAL_024_RESULT.json` y `selection/PLAN.md`. Proyección, verificación, extracción y comparación byte a byte **PASS** reutilizando `scripts/review_txt_carrier.py` Product blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`. Sin ZIP nuevo como entrega principal.

## Evaluación técnica

- `41` solicitudes GET y `5` rondas de read-model, contadas por el resultado original. Son descriptivas de esta suite, no benchmark de producción.
- Estado inicial: tres nodos `NONAUTHORITATIVE_OBSERVATION`, con cierre transitivo conocido.
- Tras `bd dep add` no controlado, la revisión de `root` se mantuvo **idéntica**, pero el doble recorrido detectó la diferencia de **3 a 4 nodos**, retornó `INCONSISTENT_GRAPH` y **no** expuso una vista autorizante.
- Reobservar el grafo después incorporó la nueva dependencia; una mutación sobre un ancestro también produjo `INCONSISTENT_GRAPH`.
- Una mutación sobre issue **no relacionada** dejó la vista informativa sin conflicto global.
- `bd ready` fue consultado como **dato nativo informativo**; nunca como autorización Product.
- En todas las salidas, `authority=NONE_PRODUCT` y `mayAuthorize=false`.

**Restricción fundamental:** dos recorridos iguales **no son una instantánea transaccional**. Un escritor puede agregar la arista inmediatamente después del segundo GET; no existe autorización de ejecución ni admisión basada en esta lectura.

## Dictamen de Control experimental

1. **CALIFICAR** el mecanismo como candidato reutilizable para observabilidad, diagnóstico y proyección operacional **solo en experimentos aislados y no autoritativos**. No afirmar que ya se integró en Product ni que la infraestructura Beads sea la SOT Product.
2. **NO CALIFICAR** Beads como frontera de escritor del grafo Product. El contraejemplo del 023 sigue abierto; `update root + dep_add` requiere enforcement efectivo contra todas las rutas de bypass, no solo pruebas de escritor cooperativo.
3. **CONSERVAR** el hallazgo Developer `REJECTED` y su guard de memoria como **propuesta a review semántica competente**, no como parche aceptado ni corrección silenciosa.
4. **NO DECLARAR Independent Review** de esta propuesta: este dictamen es evaluación de Control en el mismo programa experimental, apoyada en originales deterministas, sin reviewer semántico externo independiente.
5. **TRANSPORTE:** el carrier 024 está **publicado y verificado en Git del laboratorio**. Una copia opcional hacia `ts-execution-transport` fue bloqueada en la herramienta, y la ausencia del destino fue comprobada; `NOT_PUBLISHED_IN_TRANSPORT`. No reconstruir ni repetir a ciegas esa copia. La referencia exacta en lab es suficiente para consumo experimental.
6. **Próximo frente recomendado, NO iniciado:** cualificar una frontera efectiva de escritura causal (aislamiento de los clientes capaces de escribir aristas, permisos reales y prueba adversarial de bypass) **sin introducir un ledger global nuevo**. La limitación de este frente no detiene mejoras read-only independientes.

**Estado terminal del 024:** `COMPLETE_WITH_LIMITATIONS`; siguiente decisión Product **NO TOMADA**; sin modificaciones Product/TaskCycle/IR/Phase 2, sin falsa continuidad con otro Control.
