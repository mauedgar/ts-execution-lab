# TS — Beads 028 | Control experimental: fail-closed startup y superficie nativa completa

**Autoridad:** Control experimental, **Product NONE**. Investigación independiente; no SOT edit, no TaskCycle, Developer grant, IR Product ni Phase 2.

**Product reobservado 2026-10-28:** `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`. Comparación contra baseline 027 `7a722594...`: cuatro commits de mantenimiento Upper LC/OpenCode, sin cambios en State Kernel, SOT ni consumidor. `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`. Lab `main@b30241201d07a9590e1e845abe767cdcf9921479`; shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.

**Predecesor 027:** `mauedgar/ts-execution-lab@b5ffe777d318b823607330c59b0433f803fcc9a4:experiments/TS-BEADS-027-ISOLATED-WRITER-20261028-001/CONTROL_EXPERIMENTAL_VERDICT.md` — 28 PASS; credenciales privada/UID separada; arranque nativo sin `--auth-token-file` volvió a permitir write. La evaluación 028 no reejecuta efectos históricos.

## Hipótesis 028

Calificar si **un lanzador acotado** (sin nuevo scheduler/daemon ni ledger) impone `bd serve --auth-token-file <archivo privado>`, rechaza argumentos extras y conserva denegación de clientes de otra UID tras restart. Una ruta directa de CLI/servicio con UID privilegiada sigue siendo bypass aun cuando el lanzador elegido sea seguro; debe medirse y declararse sin fingir exclusividad general.

**Inventario de cobertura:** `gastownhall/beads@v1.3.1:internal/httpapi/routes.go` blob `50b5ad53f41204e15c0a55af31076f06918d26e1`, 41 rutas documentadas, 20 mutadoras (`POST/PUT/PATCH/DELETE`), 21 GET (incluido healthz). `ROUTES028.json` congelado es la proyección de esas 41 filas y no es un contrato Product nuevo. Toda ruta nativa no-liveness debe responder 401 a un proceso de lectura sin token; no enviar credenciales ni hacer escrituras en esa matriz negativa.

**Entorno:** dos Unix UID distintas, Dolt SELECT-only en lector, directorio de escritor 0700 y token 0600, Beads 1.3.1/Dolt 2.2.0 con SHA-256 fijados, stores Git sin remotos en Ubuntu descartable. El lanzador elegido obliga el token y no admite argumentos. Se prueba:
- 41 rutas / 20 escrituras (401 sin credencial), healthz 200;
- override `--insecure-no-auth` rechazado;
- escrituras root-update+dep_add atómicas y CAS obsoleto rechazado;
- restart con token, falta de archivo (fail closed), restauración;
- **NEGATIVA**: servicio nativo directo desde UID privilegiada sin token puede reabrir bypass al margen del launcher; CLI directo agrega arista sin mover root revision.

**Criterio terminal:** `PASS_SELECTED_FAILCLOSED_LAUNCHER_AND_FULL_ROUTE_MATRIX_WITH_PRIVILEGED_BYPASS` califica solo la ruta de arranque seleccionada y su cobertura HTTP **en este build**. No demuestra que todos los escritores nativos estén confinados, ni autorización Product, ni supervisor OS persistente y todas sus vías de bypass. Si falla, conservar el intento, medir motivo y reconciliar.

**Salida:** JSON original y `PLAN.md` en TXT `IR-TXT-CARRIER/1`, reutilizando `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`. Crear, verificar, extraer, comparar bytes y publicar solo en Git experimental. No ZIP para el consumidor. Esta investigación no modifica Product ni Dolt shared.
