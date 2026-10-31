# TS — Beads | Cierre integral de investigación y disposición consumible por TECNOTRON_BETA_RUN_001

**Corte y propietario:** 2026-10-31; investigación experimental de Beads/TS Execution Engineering. **Clase:** `EXPERIMENTAL_RESEARCH_CLOSED_WITH_LIMITATIONS`, **no** estado Product ni adopción. **Efecto Product:** `NONE`. **Destino para consumo independiente:** `TECNOTRON_BETA_RUN_001 / Beta Control`; `PUBLICADO_NO_ENVIADO`, ninguna TaskCycle se inicia desde este documento. `discusión != decisión != autoridad != implementación`.

**Source of truth Product reobservada:** `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`; `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; `docs/architecture-knowledge-ownership-baseline.md` blob `330fdc82f75e1126939cd718c1facb28abe00c62`; `docs/implementation-roadmap.md` blob `c0db94f5d8a957b106ea19827f79f3c072266cca`; `docs/context-strategy.md` blob `8b32f6b9a149ef5b240c7e31f42dc05f92e457e1`. **Estas refs son corte observado, no locks para ejecución futura.**

**Estado competente #35:** [issue canónico](https://github.com/mauedgar/tecnotron-ai/issues/35) `OPEN`, `ULC-OP-05/09`; comentario [selección Attendance 6537328286](https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6537328286): alcance de responsabilidad seleccionado por Control, **TaskCycle no inicializada ni implementación despachada** al corte; comentario [acoplamiento 6539442025](https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6539442025): H6 avanza **sin esperar adopción de Beads**. No interpretar código host-local de Attendance como baseline canónica sin refs verificadas. Attendance tiene base SQLite de dominio propia, nunca Beads/Dolt. H6 exige Parent genuino y al menos dos child TaskCycles reales, write-sets disjuntos, revisiones/aceptaciones/integraciones/cierres separados; H7 solo después de repetición competente.

## 1. Decisión técnica final, explícita y acotada

| Opción de consumo | Calificación final de esta investigación | Disposición propuesta a Beta Control |
|---|---|---|
| **0 — Sin Beads para ejecutar #35** | **GO, RECOMENDADA**. Aprovecha TC Core `FROZEN_MAINTENANCE`, Kernel actual, Git/worktrees, Provider receipts, IR y Developer grants ya existentes | **Continuar H6 con mecanismos vigentes** y gate competente `H6_ATTENDANCE_BASELINE_AND_INTERFACE_FREEZE`; no meter Beads en caminos críticos ni esperar otro experimento |
| **A — Proyección Beads informativa/read-only en laboratorio** | **GO solo experimental y opcional**, con fuente Product verificada, sin mutación de TaskCycles ni asignación/decisión autoritativa | Mantener como capacidad reutilizable sin adopción. Solo si Beta Control identifica un consumidor y un beneficio medible, seleccionar experimento shadow aislado; jamás condición de H6 |
| **B — Beads/Dolt backend autoritativo reemplazando Kernel/TC Core** | **NO-GO para #35**. Invariantes obligatorias no equivalentes o no implementadas; ninguna eliminación Product demostrada | **No migrar, no desinstalar Kernel, no publicar `bd ready` como gate Product ni delegar aceptación/Phase2/cierre a Beads** |
| **C — Registro/gestor Beads como dependencia obligatoria previa a #35** | **NO-GO** por decisión competente #35/6539442025 y ausencia de beneficio demostrado | Desacoplar y ejecutar Product H6; la investigación se archiva |

Estas son **recomendaciones experimentales sustentadas por recibos**, no cambios del ruling de Control, ni Developer acceptance ni autorización de escritura Product.

## 2. Evidencia original, incluida evidencia negativa

| Identidad | Original y comprobación | Qué queda demostrado |
|---|---|---|
| 021 | [run 40094843290](https://github.com/mauedgar/ts-execution-lab/actions/runs/40094843290) | Recipe original adaptada **en memoria** a Beads; no instalación Product |
| 028 | [run 40786754096](https://github.com/mauedgar/ts-execution-lab/actions/runs/40786754096), [veredicto](https://github.com/mauedgar/ts-execution-lab/blob/9e8016004ef5d3ca74abd67914d8e1a03ffcd851/experiments/TS-BEADS-028-FAILCLOSED-20261028-001/CONTROL_EXPERIMENTAL_VERDICT.md) | **35/35 selected-path PASS** y **BYPASS REAL**: CLI privilegiado `bd dep add` no incrementó root revision; servidor alternativo sin auth hizo write. Solo se protege ruta autenticada elegida |
| 030 | [run 40882306183](https://github.com/mauedgar/ts-execution-lab/actions/runs/40882306183), [veredicto](https://github.com/mauedgar/ts-execution-lab/blob/5cd88a9ce63aadbe08385f63ac11588192f31f6d/experiments/TS-BEADS-030-PARITY-20261029-001/CONTROL_EXPERIMENTAL_VERDICT.md) | **12/12** tests del comparador pero divergencia semántica: A Kernel `UNKNOWN/UNKNOWN` vs B original `FAIL/NONE` ante carrera |
| 032–035 | [032 history](https://github.com/mauedgar/ts-execution-lab/actions/runs/40928581506), [033 receipt](https://github.com/mauedgar/ts-execution-lab/actions/runs/40930288498), [034 join](https://github.com/mauedgar/ts-execution-lab/actions/runs/40931812435), [035 concurrency](https://github.com/mauedgar/ts-execution-lab/actions/runs/40935082766) | Historia/as-of nativa, referencia de efecto real, relectura de original sin redespacho y 4 carreras `batchApply` protegidas. No exclusión total de escritor privilegiado |
| 036 | [run 41172317720](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172317720), [original terminal](https://github.com/mauedgar/ts-execution-lab/blob/60fd974cb713f436d751cdf5fea99f7658a505bb/experiments/TS-BEADS-036-CAPABILITY-OWNERSHIP-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md) | 10 invariantes, 8 fuentes previas, **85.014 bytes** Kernel+adapter+Recipe actuales; **0 bytes Product eliminados**; auditoría estática de fuentes congeladas, no nuevo Beads test |
| 037-001 | [run 41172687235](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172687235) | **FAIL infra**: Dolt code 2 pre-inicialización, sin veredicto de seguridad. No reintento del mismo ExecutionAttempt |
| 037-002 | [run 41172852201](https://github.com/mauedgar/ts-execution-lab/actions/runs/41172852201), [terminal](https://github.com/mauedgar/ts-execution-lab/blob/1baef35511fa7fc3cadb89475a54365b25cace0b/experiments/TS-BEADS-037-OS-PRINCIPALS-20261031-001/EXPERIMENTAL_TERMINAL_002.md) | **27/27**: dos UID Unix, lector no puede escribir vía CLI/HTTP/store privados; owner sí puede usar CLI alternativo. No reparación de bypass 028 |
| 038 | [run 41173079645](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173079645), [terminal](https://github.com/mauedgar/ts-execution-lab/blob/73c7fe65c8237c9335e2cc997766d996d4c319a6/experiments/TS-BEADS-038-UNKNOWN-RECEIPT-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md) | Beads native `UNKNOWN→CONFIRMED` con CAS e identidad externa GitHub verificada, historia y no redespacho. No-retry **caller-owned** |
| 039 | [run 41173329767](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173329767), [terminal](https://github.com/mauedgar/ts-execution-lab/blob/ea269b9fb18957093fd1c605d9a593e30cbe7bd7/experiments/TS-BEADS-039-UNKNOWN-RACE-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md) | **13/13**: nueva relectura B después del rechazo causal re-clasifica `UNKNOWN/UNKNOWN` como Kernel A. **Requiere adaptador externo**, conserva `FAIL/NONE` original |
| 040 | [run 41173507307](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173507307), [terminal](https://github.com/mauedgar/ts-execution-lab/blob/9e509514b9ac73c0b4804c5d3f15d502037dc1e6/experiments/TS-BEADS-040-FULL-NATIVE-LIFECYCLE-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md) | **15/15**: `bd create/dep/ready/update/close/history/show`, preflight→2 hijos→join→terminal, referencia externa sin efecto nuevo |
| 041 | [run 41173712803](https://github.com/mauedgar/ts-execution-lab/actions/runs/41173712803), [terminal](https://github.com/mauedgar/ts-execution-lab/blob/7808245708f2d642f29fb1ffae19665f123122b5/experiments/TS-BEADS-041-PORTABLE-NATIVE-STORE-20261031-001/EXPERIMENTAL_TERMINAL_RESULT.md) | Productor 15/15 y consumidor en runner independiente **10/10**: base nativa Dolt exportada y recuperada con SHA-256 verificado; **no** replicación viva/multihost |

**Última consolidación antecedente:** `mauedgar/ts-execution-lab@a72af763c22d1cf61c6e0485565b90b884879bed:reports/TS-BEADS-INTEGRAL-CAPABILITY-20261031-001.md`, blob `89bf2e16e54e2410b744c25ef4196832ebf84247`. El reporte de cierre presente completa esa matriz y evita que Beta Control reconstruya conversación o experimente de nuevo.

## 3. Invariantes Product: obligaciones y límites exactos

**I. Autoridad / lifecycle:** TC Core `FROZEN_MAINTENANCE`, Upper LC vigente; Product Control selecciona responsabilidad/candidato, Developer da aceptación, IR independiente juzga candidato congelado, integración y cierre siguen contratos originales. Beads `ready` no sustituye ninguno.

**II. State Kernel:** el archivo Product `src/state-kernel-v0/store.js@f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a` verifica `HEAD` y snapshot, `revision = event_count`, hash encadenado con `previous_hash`, reconstrucción integral de agregados, provenance bootstrap y CAS global. En Beads, `bd history`/Dolt y `expected_version` por issue **no equivalen** a esa cadena/revisión global. La SOT clasifica Kernel `NARROW` y **final físico `UNDECIDED`**, no autoriza eliminación. La Recipe original `src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js@1e89df1a1885e3d0d24576338f0ffbd9b79890bc` sigue siendo consumidor real.

**III. Escritor confiable:** Beads 028 verificó que el propietario del store puede saltar el guard con otro CLI o servidor. 037 mitigó el riesgo para **usuarios distintos** mediante permisos 0700/0600, **no** para writer UID/root. Para volver B autoritativo, Beta Control debe verificar el *trusted computing base* y toda ruta de escritura con autoridad propia; no es aceptable solo prohibir CLI mediante prompt o un `root revision` convencional.

**IV. Effects / UNKNOWN:** ante error después de dispatch, conservar identidad `Operation/ExecutionAttempt`, proveedor original, `UNKNOWN`, no-retry sin reconciliar y prueba nativa de commit/receipt. 039 muestra que post-CAS readback puede preservar clasificación conservadora, pero el wrapper no está instalado ni revisado como Product. 048 demostró el límite general de proveedor sin status/idempotencia; ninguna base de tareas resuelve ese caso universalmente.

**V. Trabajo/estado:** 040–041 sí califican **uso integral nativo experimental** de Beads/Dolt. Se recomienda usar ese resultado como evidencia técnica y no repetirlo. No existe evidencia de beneficio neto de mantenimiento ni Product bytes retirados. La presencia de un nuevo store como shadow opcional impone costo real que debe justificarse por consumidor.

## 4. DoD final de la investigación

- [x] Adquisición de fuentes canónicas/identidades reales y clasificación de autoridad.
- [x] Dependencias + issue lifecycle + CAS/transacciones nativos Beads/Dolt.
- [x] Separación de UID con permisos OS, con bypass privilegiado conservado como hallazgo material.
- [x] `UNKNOWN` más provider-native original receipt sin replay, diferencia semántica y corrección prospectiva externa.
- [x] Historia recuperable, `ready=[]` al cierre y transferencia de base nativa entre runners independientes.
- [x] Integridad de fuente y resultados por Git/Actions/artifacts, antecedentes FAIL preservados, Product no mutado.
- [x] Matriz `GO/NO-GO` y stop condition para Beta Control.
- [ ] **NO CALIFICADO (no requisito para cerrar investigación, sí bloquea adopción B):** exclusión universal de escritor privilegiado; paridad/adopción de nueva semántica global de auditoría; integración/IR/acceptance Product; rentabilidad/retirada efectiva de Kernel.

**Stop condition cumplida:** experimentación repetitiva adicional no aporta al DoD de #35 ni convierte un bloqueo de autoridad en capacidad Beads. **No iniciar 042 ni nuevos trabajos** por defecto. Terminar esta línea experimental aquí; solo reabrir ante un requisito Product nuevo y competente, una corrección comprobable de Beads que afecte específicamente 028/030, o un nuevo consumo que justifique su coste. Esto es cierre de **investigación**, no Issue/TaskCycle Product.

## 5. Instrucción operativa para Beta Control: sin efectos automáticos

**Disposición recomendada para consumir:** `BEADS_EXPERIMENTAL_RESEARCH_TERMINAL_NO_GO_AUTHORITATIVE_PRE_35`; preservar `A_OPTIONAL_NONAUTHORITATIVE`, seleccionar `OPTION_0_NO_BEADS_FOR_H6`. Reconciliar explícitamente la selección antigua `ATTENDANCE_STANDALONE_B_FIRST_PILOT_001` con el comentario más reciente `#35/6539442025` (separación H6 / Beads); no fingir que el experimento crea un Product ruling. No implica cambiar la responsabilidad Attendance o el DoD H6.

**Próximo gate ya competente en #35:** `H6_ATTENDANCE_BASELINE_AND_INTERFACE_FREEZE`, **planning/control only**: adquisición del código real/receipts (o fuente greenfield si no verificable), dominio SQLite separado, interfaz compartida congelada, dos responsabilidades genuinas con write-sets disjuntos; luego solo TC/Assignment/Product effects bajo autoridad existente. H7 diferido.

**No hacer:** no instalar Beads en repositorio Product, no migrar Kernel ni TC Core, no ejecutar #35 desde esta rama, no asumir aceptación Developer, no reabrir 028/030, no re-dispatch del proveedor original, no crear nuevo Kernel/scheduler por déficit experimental.

**Retención:** recibos originales GitHub Actions/ZIP 036–041 tienen vencimiento aproximadamente **2026-11-30**; sus identidades y hashes quedan en reportes Git durables. Si Beta Control necesita bytes originales más allá de esa retención, seleccionar traslado competente de artefactos sin modificar recibos; no confundir informe con preservación perpetua de ZIP original.

## 6. Handoff compacto, listo para pegar en el chat Beta (no enviado)

> Continuá `TECNOTRON_BETA_RUN_001` desde `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, reobservando SOT/#35. Consumí `mauedgar/ts-execution-lab:experiment/beads-041-portable-native-store-20261031-001:reports/TS-BEADS-FINAL-RESEARCH-CLOSE-TO-BETA-20261031-001.md`: Beads está experimentalmente calificado pero **NO-GO autoritativo previo a #35**; continuá el `H6_ATTENDANCE_BASELINE_AND_INTERFACE_FREEZE` con los mecanismos Product existentes, sin reiniciar efectos ni promover Beads por un PASS experimental. Devolvé el delta competente de Control, source freeze y siguiente gate real.

**Publicación del documento:** resultado `PUBLICADO_NO_ENVIADO`; su Git commit/blob final se verificará tras guardar. La rama de laboratorio no confiere autoridad Product.
