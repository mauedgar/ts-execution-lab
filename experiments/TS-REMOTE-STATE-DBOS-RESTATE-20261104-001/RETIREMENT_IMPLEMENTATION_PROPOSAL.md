# TS-REMOTE-STATE — propuesta integral de retiro físico del Kernel
**ID:** TS-REMOTE-STATE-KERNEL-RETIREMENT-PROPOSAL-20261104-001
**Perfil:** OPERATIONAL — @Autónomo Experimental + @Rotación
**Clase:** propuesta técnica y evidencia experimental, **NO Product SOT / NO Product grant**.
**Objetivo:** retirar el almacenamiento filesystem de State Kernel sin perder las capacidades vigentes ni reconstruir efectos históricos, conservando Upper LC y TaskCycle Core.

## 0. Corte de evidencia y hechos reconciliados

- Tecnotron Product `mauedgar/tecnotron-ai:tools@35bfcc8e4fdd69976ef4bdfea6b9f10d9fda6a84`; tree `25d1a151d651bb41936c69334fb0b0772ef22519`. Reobservar antes de cualquier cambio Product.
- Product SOT `docs/SOURCE_OF_TRUTH.md` blob `498d338eb98e54e294db697c5574296febf77e6f`; arquitectura/ownership blob `330fdc82f75e1126939cd718c1facb28abe00c62`: State Kernel `NARROW`, disposición final `UNDECIDED`, `NEEDS_EQUIVALENCE_BEFORE_CHANGE`.
- Política Python `docs/python-runtime-policy.md` blob `ba997668102151a9be26ba5d3ff31c03a11fc93f`: 3.15.2 canónico por defecto para *nuevos componentes Python Product*; no migrar componentes legados ni H6 por inferencia.
- Contrato núcleo `docs/state-kernel-v0/README.md` blob `1c1fc35ef510ac46f4ba84af4b8434adffb47fe1`.
- Inventario de consumidores publicado `mauedgar/ts-execution-lab@a6d02908a4a428e5f004d7ba712a35e42cc4d8d2:TS-REMOTE-STATE-CONSUMER-AND-CUTOVER-MATRIX-20261104-001.md`.
- Mecánica V4 **PASS real** en `mauedgar/ts-execution-lab@77f6201ef9122ce682dc405b7afb9a6378701fd4`, GitHub Actions run `41862024848`, attempt 1, job `126686105687`, conclusion `success` y recibos de log:
  - `PASS|DBOS|phase=first|...|step_count=1`;
  - `PASS|DBOS|phase=second|...|step_count=1`;
  - `PASS|POSTGRES_V4|boot|aggregates=4|revision=4|audit=valid`;
  - `PASS|POSTGRES_V4|race|commits=1|stale=1|revision=5|audit=valid`;
  - `PASS|POSTGRES_V4|unknown|retry=blocked|rollback=atomic|revision=6`;
  - `PASS|POSTGRES_V4|restore|replayed_events=6|objects=4`.
- **Límite de V4:** PostgreSQL efímero dentro de un único runner; el fixture es un esquema/reducer sintético, no aplica las transiciones Product exactas. No valida dos hosts distintos, Neon, secretos, backup fuera de proveedor ni retención histórica.
- La publicación competitiva en la rama experimental Git-ledger tuvo un segundo `update_ref` con `GithubGraphQLAPIError`, clasificado `UNKNOWN` respecto del efecto de B; cabeza observada A `c29fb2f990081a3ddaa27a270ceb7f83b29a6b59`, B `bed36d401266e6e2ecbd6872b4eef6c6bcb20427`. No reintentar B ni declarar CAS probado por ese error. Sin relación con los UNKNOWN Product V6P2/BETA (también preservados).
- Beads 047B: integración Product NO-GO en ese experimento, ninguna eliminación de evidencia o autoridad por esta decisión.

## 1. Implementación propuesta — mínimo código propio

**SOT y autoridad:** Git, documentación Product, Upper LC y TaskCycle Core siguen dueños de decisiones, grants y aceptación.
**Estado mutable remoto:** PostgreSQL con transacciones atómicas, índice por agregado, revisión global, ledger de eventos y recibos indexados.
**Ejecutores durables:** DBOS para workflows y checkpoints, no para validar transición Product ni aceptar candidatos. Puede ejecutarse desde Actions y eventualmente otros workers; DBOS *no* vuelve continua una ejecución sin proceso/servicio que reciba trabajo.
**Evidencia inmutable:** GitHub Transport/artefactos protegidos por identidad Git y recibo exacto; no guardar datos privados, PII, secretos ni snapshots sensibles en Git.
**UI, notebook y Commander:** superficies reemplazables, solo cache/dev cuando sean útiles. Commander nunca es almacenamiento ni superficie semántica.

El Product actual es principalmente Node/TypeScript en este límite. Preferir **un adaptador PostgreSQL TypeScript** a las interfaces ya existentes `ExecutionLifecycleCapability` (6 métodos) y `TaskCycleLifecycleCapability` (5 métodos). Mantener los reducers/validadores Product que hoy residen parcialmente en `src/state-kernel-v0/index.js` y `contracts.js` hasta reubicarlos con revisión competente. No copiar reglas a un servicio Python. DBOS Python 3.15.2 queda para Execution Engineering; evaluar la SDK DBOS TypeScript únicamente si elimina un puente innecesario o reduce código verificado. No imponer LangGraph/Temporal/Restate en el camino crítico; Restate queda comparador si no se alcanzan invariantes con PostgreSQL + DBOS.

### Persistencia propuesta (esquema experimental, no SQL Product autorizado)

- `store_meta(id=1, global_revision, event_head_hash, schema_version)`: fila única serializada.
- `aggregates(kind, id, aggregate_revision, payload_jsonb)`: cuatro agregados ya definidos; mismo modelo Product, no estado nuevo.
- `events(seq, aggregate_kind/id, previous_hash, event_hash, deterministic_payload, mutation_id)`: ledger inmutable verificable y replayable, con orden global.
- `mutation_receipts(mutation_id PRIMARY KEY, expected_revision, committed_revision, result_ref)`: resolver acknowledgement perdido sin inferir ni repetir efectos.
- Índice de `ExecutionAttempt.operation_id` y de sus resultados no reconciliados: bloquear la siguiente ejecución mientras exista `UNKNOWN` o presencia incierta.
- Artefactos de ejecución: solo referencias portables con controles de acceso y retención; sin copia paralela autoritativa.

Operación transaccional: verificar `expected_revision`; seleccionar la fila de meta con lock; validar contrato mediante reducer Product exacto; aplicar agregado + evento hash + recibo en **una sola transacción**; commit o ninguna modificación. Si el ACK se pierde después del commit: **leer `mutation_id`** y comprobar estado/recibo originales; NO repetir dispatch. Errores de consulta o proveedor no se convierten en `ABSENT` automáticamente.

### Dos persistencias distintas que deben sustituirse

1. `createStateKernelCompatibilityBinding` y `FilesystemStateStore` — lifecycle/estado.
2. `FilesystemInvocationArtifactStore` dentro del default de `recipe-invocation.js` — stdout, stderr, receipts y resultados.

Las Recipes y sus ports ya separaron parte de la semántica, pero el default todavía cae a filesystem. Eliminar `store.js` sin sustituir *ambas* rutas rompería consumidores.

## 2. Dependencias e instalación real

**Instaladas y ejercitadas en Actions V4 (runner aislado; NO instalación permanente en notebook/desktop):**
CPython `3.15.2`, `dbos==3.4.0`, `psycopg==3.3.8`, `psycopg-binary==3.3.8`; dependencias resueltas observadas en log: `sqlalchemy==2.1.8`, `greenlet==3.5.6`, `click==8.5.0`, `croniter==6.2.4`, `python-dateutil==4.0.0`, `PyYAML==6.0.3`, `typing-extensions==4.16.0`, `tzdata==2026.6`. `pip install` PASS y ejecuciones PASS en el mismo entorno. No tomar este log como un `uv.lock` reproducible.

**Próxima instalación acotada:** componente experimental Python con `.python-version=3.15.2`, `pyproject.toml` y `uv.lock` generado y versionado; verificar `uv lock --check`, `uv sync --locked` en Linux/Windows cuando sea pertinente, sin alterar entorno Product legado ni Node global. Para el adaptador TS, calificar la dependencia `pg` y sus tipos en entorno separado antes de adoptar un pin; no simular instalación previa de `pg`. `@Neon`/PostgreSQL administrado requiere conectar credenciales/almacenamiento externo con autorización específica y un presupuesto seguro; no se ha provisionado Neon.

## 3. Roadmap de implementación integral (sin nuevas gates Product)

**R0 — estado y corte técnico, CERRADO EXPERIMENTAL.** V4 fuente/commit/tree, proveedor/receipt y matriz de consumidores preservados. No repetir run `41862024848`. Congelar expectativas de comportamiento del Kernel V0 a partir de sus pruebas aceptadas.

**R1 — vertical sintético reutilizando reducer real (PRIMERO).** Aislar adapters sin tocar Product: harness en lab que consume fixtures exactos de los cuatro agregados y contratos V0, preserva vocabularios/error codes, late obligations, legal-next, bootstrap de hechos históricos sin eventos inventados, `UNKNOWN`, generación/replay/hashes. El adapter no decide autoridad; solo persiste mutaciones autorizadas por capa semántica. Comparación diferencial contra Kernel local read-only en fixtures sintéticos. DoD: todas las trazas autorizadas coinciden, rechazos no dejan estado, revisión independiente sobre commit/tree exactos.

**R2 — dependencia reproducible y reversibilidad.** Publicar lockfile Python 3.15.2 y Node TS con pins calificados, tests Linux y Windows cuando sean aplicables; pruebas de pérdida de ACK pre/post commit, corte de conexión, conflictos simultáneos, tamper, restauración, payloads inválidos, prohibición de nuevos intentos en UNKNOWN, credenciales inadecuadas. DoD: sin regresiones semánticas, ninguna acción externa duplicada, ninguna versión Product existente desplazada.

**R3 — PostgreSQL realmente remoto y dos clientes independientes.** Neon Free candidato de costo $0 bajo cuotas; si su conexión no está habilitada, detener solo este gate y continuar R1/R2. Crear namespace sintético de privilegio mínimo, TLS, secretos administrados fuera del repo, backups externos y retorno verificable; cliente A escribe y termina, cliente B en **otro runner/host** observa y continúa usando identidad exacta; anotar latencia/errores/cuotas. DoD: persistencia multi-runner, recuperación de base/restauración desde copia, fail-closed ante outage/cuota, sin escritura local autoritativa. Free (escala a cero, restauración limitada) no equivale a garantía de disponibilidad permanente.

**R4 — propuesta Product de adopción acotada.** Una responsabilidad Product seleccionada por autoridad competente, sin introducir nuevo TaskCycle por conveniencia. Implementar un único consumer vertical por los ports existentes, compatible con el antiguo binding; CI/Independent Review exactos, aceptación Developer, Phase 2 separada y comprobación de efectos. Estado Kernel anterior se mantiene accesible read-only para contraste; sin migración automática de activos.

**R5 — adopción por consumidores y retiro físico.** Migrar por partes default de lifecycle y ArtifactStore, restauración histórica tipada con provenance y sin reejecuciones; comparar recibos y obligaciones, pasar tests de rutas/CLI/harnesses y demostrar ausencia de consumidores del filesystem. Solo entonces decidir y ejecutar la eliminación de implementación local, limpieza de documentación canónica y cierre lógico. Conservar historia Git/Transport/UNKNOWN intacta.

## 4. DoD integral y límites de decisión

- Las capacidades Product efectivas sobreviven: cuatro agregados, transiciones legal/illegal, revisión global, CAS, autoridad/obligaciones, late extension, import tipado, historial verificable/replay, UNKNOWN/reconciliación, receipt/Git identities, rendering/proyecciones.
- A igualdad de operación autorizada y fuente congelada, no cambia resultado ni modelo de autoridad; no se altera el meaning de acceptance/Phase 2, CI y revisión.
- Dos clientes independientes consultan el mismo estado remoto y no dependen de `TECNOTRON_HOME` como autoridad.
- Pérdida de conexión y confirmación ambigua no producen reintento ciego, reset de revision ni duplicación de efecto; backup/restauración y audit tamper comprobados.
- Seguridad: least privilege, secretos fuera de repos/receipts, TLS, no PII de usuarios, retención y backup bajo decisión competente; libre de gasto imprevisto.
- Dependencias productivas aisladas/locked y validadas en targets; uso de `uv` y pins sin cambio global de runtime. Contar costo real en llamadas Commander y disponibilidad.
- Cierre solo con equivalencia + review independiente + aceptación y Phase 2 Product competentes; no es suficiente un PASS de Actions o un PR abierto.
- Sin red de proveedores o autoridad Product suficiente, devolver `PENDING_EXTERNAL_RESULT` o `BLOCKED` exacto; continuar trabajo técnico independiente sin inventar grants.

## 5. Próxima instrucción concreta para receptor

En nuevo chat OPERATIONAL, consumir este documento y el carrier exacto; reobservar Product SOT/branch/tree, confirmar V4 original `41862024848` PASS **sin rerun** y preparar R1/R2 como un candidato experimental portable/revisable. Seleccionar mínimo de deps en runtime aislado; realizar las pruebas negativas/diferenciales y generar resultados con identidades exactas. Solicitar conexión Neon solo al llegar R3; no hacer Product Phase 2, no reactivar Beads/047B ni tocar H6, no reintentar el Git-CAS B UNKNOWN. Reportar decisión y deuda residual, no resumen genérico.
