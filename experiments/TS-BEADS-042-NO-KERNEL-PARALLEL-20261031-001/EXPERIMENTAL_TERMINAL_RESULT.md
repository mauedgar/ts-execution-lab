# Beads 042 — Dictamen terminal definitivo: paralelización Beads-first sin State Kernel

**Fecha:** 2026-10-31. **Línea:** TS Beads / Execution Engineering, `EXPERIMENTAL_CONTROL_ONLY`. **Product effect:** `NONE`. **Veredicto:** `GO_EXPERIMENTAL_BEADS_AS_PRIMARY_PARALLEL_WORK_STATE_WITHOUT_KERNEL / COMPLETE_WITH_LIMITATIONS`. **NO** es Product acceptance, migración ni autorización de modificar TaskCycle Core o ejecutar #35.

## I. Hallazgo decisivo y rectificación

**Sí es viable el propósito original de Beads:** usar Beads/Dolt de forma nativa como **almacén principal del estado del trabajo**, sus dependencias y preparación, lanzar **dos procesos ejecutores reales en paralelo**, consumir recibos de ambos y cerrar `join` + `parent`, **sin State Kernel en ese flujo experimental**. No necesitamos construir un segundo Kernel/scheduler para esas funciones; el coordinador solo conserva contratos de autoridad/identidad y validación de efectos, no una base paralela de estados.

**Rectificación explícita del anterior dictamen no-go:** el documento de cierre previo `reports/TS-BEADS-FINAL-RESEARCH-CLOSE-TO-BETA-20261031-001.md` (histórico en Git `293a58de63341f51f6b2dbf05710f488392e4754`) decía NO-GO autoritativo previo a #35. Esa prohibición **no debe extrapolarse** a la capacidad de Beads de gobernar el estado de trabajo paralelo: el 042 la confirmó experimentalmente. El NO-GO **permanece** para reemplazar *sin calificación* todos los efectos, auditoría global, autoridad Product y State Kernel canónico. Estas dos conclusiones son diferentes.

## II. Identidad original, pruebas y recibos

- Exact Git subject ejecutado: `mauedgar/ts-execution-lab@ab346906fe6e35d64bde67eecbe951baed91ad59`; rama `experiment/beads-042-no-kernel-parallel-go-nogo-20261031-001`. Original `ExecutionAttempt=TS-BEADS-042-ATTEMPT-001`, writer GitHub Actions runner aislado.
- [Original GitHub Actions run 41174844096](https://github.com/mauedgar/ts-execution-lab/actions/runs/41174844096), **completed/success**, run_attempt `1`, job `124460152527`. Un despacho, no reintentos.
- Código original `experiments/TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001/native042.py` Git blob `ba518e866b644378610e730574a3df840f75ecea`, DoD `experiments/TS-BEADS-042-NO-KERNEL-PARALLEL-20261031-001/DOD.md` prospectivamente congelado. Beads 1.3.1 ZIP SHA256 `3219443a9734b89b93fb16ee8d65844759fa1b3cd3cf139c606b7353cfb0715c`; Dolt 2.2.0 ZIP SHA256 `1f7ad8c2622995789420a3fb0f2d16b4aa7430000a825dd91d5938f36480cbf6`.
- [Artefacto original 13032244367](https://github.com/mauedgar/ts-execution-lab/actions/runs/41174844096/artifacts/13032244367), ZIP SHA-256 `9ff8e4fc5a1aea261926a7b7dd9a696d1d395230916eb182d613748193302182`, 506.167 bytes, vence 2026-11-30T06:01:25Z. Contiene `RESULT042.json`, log original, TAR de **almacén Beads/Dolt nativo** y manifest original SHA256.
- `RESULT042.json` SHA-256 `9dd9064734a39b126f0ae36bbe86b422522f4126b9fbc89ffc7fe9e9e7e08032` reportado por el propio run.
- Log: `TS_BEADS042=PASS_REAL_PARALLEL_BEADS_FIRST_NO_STATE_KERNEL_WITH_TRUSTED_POLICY_BOUNDARY;real_parallel=2;overlap_ns=480201111;parent=CLOSED;Product=NONE`. El control final de Actions verificó `worker_dispatch_count=2`, `kernel_used=false`, `state_backend=NATIVE_BEADS_DOLT_ONLY`, `len(checks)>=24` y todas PASS. La ejecución usó dos subprocesses reales **sintéticos**, no dos agentes LLM remotos.

**Comportamiento real:** `bd ready` desbloqueó preflight, luego Alpha y Beta, ambos trabajos corrieron temporalmente solapados **480.201111 ms**, cada uno generó fichero propio e identidad/recibo SHA256. El coordinador confió únicamente en recibos verificados, registró descripción y cierre native Beads de Alpha; Beta seguía lista y join seguía bloqueado. Al cerrar Beta, join fue única lista; luego parent, y `bd ready=[]` con las **cinco issues nativas cerradas**. Historia nativa de cada hijo recuperada; ningún State Kernel usado ni nuevo store de tareas construido.

## III. Arquitectura candidata de Beads-first **sin Kernel de trabajo**

```text
TECNOTRON Beta Control + Developer (autoridad, selección, contrato)
              |
  Coordinator mínimo, sin DB propia de estado ni scheduler
     | permisos / ExecutionAttempt / no-retry / receipts
     v
     BEADS + DOLT  (SOT del estado de TRABAJO en experimento)
      ├─ Parent, tareas hijas, dependencias, status y ready
      ├─ reserva / causal version (selected write route)
      ├─ historia y almacenamiento durable nativo
      └─ referencias inmutables a recibos GitHub/Transport
     |                 |
     v                 v
  Actor Alpha       Actor Beta    [worktrees / write-sets disjuntos]
     \                 /
           join por Beads
                 |
      Review independiente / Developer acceptance
                 |
       Product close bajo TC Core competente
```

**Distinción crítica:** se puede reemplazar el **estado del trabajo y scheduling casero** por Beads sin un nuevo Kernel. **No** se ha demostrado reemplazar la **autoridad y auditoría canónicas de TaskCycle**. Una parte del código actual podría eliminarse tras una decisión Product específica; todavía **0 bytes** de Product fueron removidos o medidos como ahorro. «Sin Kernel de trabajo» no equivale a «sin controles de autoridad», ni permite anticipar Phase 2.

## IV. Límites empíricos que la arquitectura debe respetar

1. **Actor aislado / writer TCB:** #028 demostró que el propietario privilegiado puede escribir con CLI nativo o servidor alternativo fuera del CAS. #037 aisló efectivamente UIDs de lectura/ejecución respecto al writer, pero **no contiene al propio writer**. Arquitectura viable solo con **un actor/servicio propietario confiable** y sin entregar su cuenta, token ni acceso BD/Dolt directo a ejecutores/reviewers. Aun así requiere revisión competente de todas las superficies mutadoras si se va a adoptar como Product.
2. **Efectos/UNKNOWN:** #038 obtuvo estado native UNKNOWN→CONFIRMED con recibo externo verificado, #039 corrigió conservadoramente por relectura una carrera de CAS, sin instalar corrección Product. Beads no implementa la política externa de no-retry. El #048 probó que ante proveedores sin idempotencia/status, un UNKNOWN no puede recuperarse automáticamente. El coordinator mínimo debe preservar esos controles, no reemplazarlos con `bd ready`.
3. **Auditoría:** `bd history` y snapshots Dolt funcionan (#032, #040, #041), pero **no se demostró igualdad** con el Kernel Product `revision/event_count/hash-chain/snapshot HEAD`. Una sustitución de esta garantía requiere decisión/DoD explícita de Product Control, no basta el 042.
4. **Autoridad/Review:** separar `ready` de `authorized`. El 042 usó un grant sintético acotado por el DoD; no tiene Developer grant real ni IR de #35. La aceptación, integración y cierre Product siguen bajo mecanismos vigentes hasta decisión competente.
5. **Escala / proveedor:** dos trabajos Python locales en ~0,48 s de solapamiento y un GitHub runner. No es una prueba de agentes OpenCode reales, ejecución distribuida multimáquina, HA ni carga sostenida.
6. **Dominio:** la base de Attendance es independiente. Beads sería infraestructura de trabajo, no el almacenamiento de negocio de Attendance.

## V. GO/NO-GO definitivo para Beta Control

| Objetivo | Resultado experimental | Propuesta para Control |
|---|---|---|
| Usar Beads para **paralelizar y coordinar responsabilidades**, dependencias, `ready`, trabajo/cierre | **GO EXPERIMENTAL** demostrado, incluyendo ejecución simultánea real sin State Kernel | **Candidato real a consumo de Beta**, a evaluar con un Product Consumer fit limitado, no descartarlo |
| Evitar mantener un Kernel **adicional de work tracking** | **GO de diseño experimental**: native Beads es el almacén de trabajo en 042, sin DB casera de estado | No crear Kernel/scheduler/ledger nuevos para ese propósito |
| Eliminar directamente TODO State Kernel Product, reemplazar toda autoridad/auditoría con Beads | **NO-GO con evidencia actual** | No retirar archivos existentes ni cambiar semánticas TC por el fixture; solo un gate Product expreso podría modificar invariantes |
| Hacer Beads **precondición obligatoria de #35** | **NO-GO de autoridad**: Control ya desacopló H6 de Beads [#35/6539442025](https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6539442025) | No paralizar #35 para investigar. Product puede continuar mientras juzga propuesta |

**Recomendación corregida:** **no descartar Beads**. Proponer a Beta Control un **piloto de consumo limitado: Beads dueño del grafo/estado del trabajo de dos children; coordinator mínimo sin Kernel de trabajo; actor writer aislado; GitHub native receipts; TC Core/Developer/IR mantienen autoridad**. Medir **código y estado Product eliminables**, efecto de un fallo `UNKNOWN` y riesgo de writer antes de cualquier adopción. Si un pilotaje Product no puede preservar los invariantes obligatorios con ese límite de complejidad, declarar **NO-GO definitivo para sustitución** sin construir un segundo Kernel.

El pilotaje y la decisión posterior corresponden íntegramente a `TECNOTRON_BETA_RUN_001`; esta rama ha terminado el alcance experimental. No ejecutar #35 ni promover automáticamente el resultado.

## VI. Handoff preparado (no enviado)

```text
Continuá TECNOTRON_BETA_RUN_001 reobservando mauedgar/tecnotron-ai:tools y #35. Consumí el dictamen corregido Beads-first de ts-execution-lab@<publicación de este informe>: Beads 042 demostró DOS trabajadores reales concurrentes con grafo/estado/join/Parent nativos y SIN State Kernel; por eso NO descartarlo para coordinación del trabajo. Calificá un Product consumer-fit limitado con writer aislado, receipts/no-retry y autoridad TC Core existentes, sin nueva DB/scheduler/Kernel de trabajo; no confundas esta calificación con autorización de retirar TODO Kernel Product ni con inicio automático del TaskCycle #35.
```

**Material original y reproducibilidad:** DoD/source/result 042 y terminales 028/030/036–041 quedan en Git y artifacts. Ninguna evidencia fue sobrescrita. El documento histórico NO-GO anterior queda preservado como decisión experimental provisional anterior a 042, y **es reemplazado en el punto específico de paralelismo por este resultado empírico posterior**.
