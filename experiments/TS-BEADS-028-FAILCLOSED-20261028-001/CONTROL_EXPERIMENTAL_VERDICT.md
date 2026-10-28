# TS — Beads 028 | Dictamen de Control experimental: launcher autenticado y rutas de mutación

**ID:** `TS-BEADS-028-FAILCLOSED-20261028-001`  
**Fecha:** 2026-10-28.  
**Estado terminal:** `COMPLETE_WITH_PRIVILEGED_WRITER_BYPASS_LIMITATION`.  
**Resultado nativo:** `PASS_SELECTED_FAILCLOSED_LAUNCHER_AND_FULL_ROUTE_MATRIX_WITH_PRIVILEGED_BYPASS` (**35/35 verificaciones PASS**).  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`; Product adoption **NONE**, Independent Review Product **NOT_PERFORMED**, no Developer grant, TaskCycle real ni Phase 2.

## 1. Fuentes y frontera de autoridad

- Product actual reobservado: `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`, SOT `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, current state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Product avanzó desde baseline del 027 `7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56` por cuatro commits relacionados con mantenimiento de agentes Upper LC/OpenCode (incluye PR #55). Comparación de árbol/diff: no cambios en State Kernel/SOT/consumer, sin reactivar otras responsabilidades.
- Laboratorio base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`, rama aislada `experiment/beads-028-failclosed-route-inventory-20261028-001`; shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` intacto.
- Predecesor `027`: `mauedgar/ts-execution-lab@b5ffe777d318b823607330c59b0433f803fcc9a4:experiments/TS-BEADS-027-ISOLATED-WRITER-20261028-001/CONTROL_EXPERIMENTAL_VERDICT.md`. Se consumió como antecedente; no se reejecutaron sus efectos. La limitación de Beads `bd dep add` que no altera versión de raíz proviene de 023 y se retiene.
- Inventario fuente exacta: `gastownhall/beads@v1.3.1:internal/httpapi/routes.go`, Git blob `50b5ad53f41204e15c0a55af31076f06918d26e1`; la fuente registra 41 operaciones router, **20 métodos mutadores** (`POST/PATCH/PUT/DELETE`) y 21 lecturas (`GET`, incluido `GET /healthz`). `ROUTES028.json` es proyección congelada de esa fuente para el fixture, no nuevo contrato Product ni prueba de rutas ocultas u otros transportes.
- Ejecutados Beads v1.3.1 y Dolt v2.2.0 en Ubuntu descartable, cuentas Unix distintas, credential 0600 y directorio privado 0700; ningún recurso Product o Dolt remoto compartido escrito.

## 2. Intento nativo exacto y evidence carrier

**Un solo ExecutionAttempt** para el 028:

- [GitHub Actions run 40786754096](https://github.com/mauedgar/ts-execution-lab/actions/runs/40786754096), job `123161759907`, source Git SHA `1abe8936379a8fefafae40d2ec7d1ec836913ad5`. `completed/success`, log `TS_BEADS028=PASS;checks=35;WRITES_AUTH=20/20;LAUNCHER=FAIL_CLOSED;DIRECT_UID_BYPASS=CONFIRMED;Product=NONE`.
- Source scripts: `experiments/TS-BEADS-028-FAILCLOSED-20261028-001/native028.py`, `reader028.py`, `ROUTES028.json`, `PLAN.md`, `materialize028.py`.
- **Original transport TXT:** `mauedgar/ts-execution-lab@0a427c1578420fb2668bdcec6ad8f4c911882516:transport/TS-BEADS-028-FAILCLOSED-20261028-001/EVIDENCE_CARRIER.txt`; Git blob `7c96a1886eebeb693f5f0c7de6d2f117c39b9111`, original SHA256 `404d3a4c0283dd397fb1897f4ec7cd7f53208f1ec4ee857aaa51aabcabb1a2f1`, 8,879 bytes como archivo UTF-8 original del runner.
- Formato `IR-TXT-CARRIER/1`, tres miembros `README.txt`, `control/PLAN.md`, `original/RESULT028.json` (miembro original sha256 `4caba36920fa5c6465963e33c8dd246ff61c906b106af490948a2962699a103d`). Generado, **verificado, extraído y comparado byte a byte PASS** con script Product existente `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`.
- Git lab branch actualizado por mecanismo create-only posterior al test, commit `0a427c1578420fb2668bdcec6ad8f4c911882516`. No copia a Transport repo afirmada; esta referencia exacta en Git del laboratorio es el carrier.
- Los 35 controles y hallazgos exactos están en `original/RESULT028.json`; este dictamen los interpreta sin sustituir el recibo.

## 3. Hallazgos técnicos

**A. Arranque autenticado seleccionado — PASS condicionado.** En una sola identidad de servicio privilegiada con código acotado, `secure-serve.sh` impone de forma estática `bd serve --addr 127.0.0.1:<puerto> --auth-token-file <secreto privado>`, no acepta argumentos adicionales y rechazó `--insecure-no-auth` cuando se intentó pasarlo al launcher. No se añadió scheduler ni una segunda base de datos ni un ledger mutable global.

**B. Inventario de superficie HTTP — PASS en versión y configuración ensayadas.** En el servidor autenticado, las 20 operaciones HTTP mutadoras de `ROUTES028.json` rechazaron sin token (`401`). Las otras 20 rutas no-liveness también dieron 401 y la única liveness `GET /healthz` retornó 200. El cliente con UID separada conservó SELECT SQL, no UPDATE SQL, no acceso a token/almacén privado. Se califica **este router v1.3.1 y estas operaciones**, no otros servicios/puertos/rutas futuras.

**C. Reconciliación/recuperación — PASS condicionado.** El reinicio seleccionado siguió autenticado, el arranque con archivo de token faltante rechazó iniciar y la restauración volvió a denegar a lectores. El escritor privilegiado mantuvo su batch nativo atómico `update root(expected_version) + dep_add` que avanza `root.revision`; se rechazó un CAS competidor obsoleto.

**D. Bypass material preservado — NO EXCLUSIVIDAD GENERAL.** Fuera del launcher seleccionado, un servidor nativo arrancado directamente desde la identidad privilegiada sin `--auth-token-file` volvió a permitir `dep_add` por HTTP sin token. Asimismo, el `bd dep add` directo del escritor modificó el grafo por fuera del launcher HTTP y **no** avanzó `root.revision`. La restauración posterior de auth cerró el endpoint probado, pero **no** impide que un actor autorizado con shell/CLI privilegiado abra otra ruta. La evidencia demuestra seguridad *del camino seleccionado*, no confinamiento de todos los escritores.

## 4. Dictamen de Control experimental

1. `QUALIFIED_BOUNDED_STARTUP_POSTURE`: usar las capacidades actuales de Beads (Bearer, servidor y batch nativos), UID separadas, directorio privado, launcher de configuración fija y validación de read-only/401 es técnicamente viable **en el fixture local Ubuntu**. Su sencillez no implica por sí sola menor costo operativo Product.
2. `BLOCK_GENERAL_EXCLUSIVE_CAUSAL_WRITER`: mientras una UID privilegiada, CLI directo, segundo `bd serve`, otro puerto, credencial filtrada o proceso con privilegios equivalentes pueda mutar sin la convención root+edge, no hay garantía universal de read-set causal. No activar un TaskCycle Product basándose en ello.
3. `NO_PRODUCT_ADOPTION`: ni este PASS, ni el estado Beads `ready`, ni la publicación del TXT equivalen a aceptación Product, cierre, Developer grant o Phase 2. El guard Developer `REJECTED` y las disposiciones de 023 permanecen separados.
4. **Siguiente prioridad experimental sugerida, no iniciada:** evaluar cuantitativamente si Beads como capa informativa/read-only + un único componente ya autorizado para efectos protegidos permite eliminar dependencias/código sin necesidad de imponer exclusividad nativa global del grafo. Si se necesita Beads autoritativo, calificar contención efectiva de todos los escritores privilegiados y recuperación de servicios fuera de la simple convención del launcher, con costes demostrados. No añadir nuevo daemon, scheduler, rol o ledger por defecto.

**Terminal:** `028 COMPLETE_WITH_PRIVILEGED_WRITER_BYPASS_LIMITATION`. Product actual y Dolt compartido verificados sin cambios. 
