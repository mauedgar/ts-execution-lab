# TS Beads 029 — Control experimental: costos y dependencia reales de dos arquitecturas

**Autoridad**: Control experimental de Beads únicamente. **No Product**, no TaskCycle, Developer grant, IR Product, Phase 2, integración o migración. No repetir 022–028.

## Pregunta seleccionada

¿Conviene priorizar Beads como (A) **proyección informativa read-only** manteniendo el lifecycle Product actual, o (B) **almacenamiento autoritativo** con ports async, CAS causal y aislamiento del escritor? Comparar con mediciones del repositorio competente y recibos nativos originales, sin extrapolaciones no sustentadas ni simular que unas llamadas HTTP ahorradas equivalen a mantenimiento/latencia de producción.

## Sujetos congelados

- Product `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`; SOT blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, current state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Lab main `b30241201d07a9590e1e845abe767cdcf9921479`. Shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` (no access for mutation).
- 022 report `mauedgar/ts-execution-lab@32f86383c979ba015024d0e70ccd98c61858e132:experiments/TS-BEADS-OBLIGATION-AUTHORITY-EFFICIENCY-20261024-022/RESULT.md`.
- 024 original native receipt `mauedgar/ts-execution-lab@4a2511e1fa02858b765715ac76e7d19a32aa67da:transport/TS-BEADS-024-READ-MODEL-20261024-001/EVIDENCE_CARRIER.txt`.
- 028 native original receipt `mauedgar/ts-execution-lab@9e8016004ef5d3ca74abd67914d8e1a03ffcd851:transport/TS-BEADS-028-FAILCLOSED-20261028-001/EVIDENCE_CARRIER.txt`. 023–027 hallazgos preservados en sus dictámenes, no reejecutar.

## Método

1. Clonar Product detached a SHA/tree exactos (read-only). Contar bytes/líneas, archivos Source Kernel, adapter, RunStore y Recipe original y las referencias de símbolos/imports runtime/tests. Las referencias son inventario de contacto, **no tareas de migración demostradas** ni autorización de borrado. El conteo y las categorías deben salir del código real.
2. Obtener 022/024/028 originales del Git exacto, verificar/extract TXT 024/028 mediante el proyector Product original y corroborar sus status originales. Medir solicitudes observadas de cada suite; comparar únicamente condiciones de un mismo workload. 022 compara 127 vs 73 solicitudes en dos variantes **dentro de B**; 024 mide GET del lector A en un fixture diferente; no hacer comparación de latencia A/B.
3. Comparar obligaciones no equivalentes: A conserva autoridad Product y no puede usar Beads ready/close como aceptación; B requiere ports async, cierre completo del read-set dinámico, exclusividad efectiva de los escritores, fail-closed en todos los arranques, competencia de la autoridad Developer, `NONE/CONFIRMED/UNKNOWN`, migración histórica y equivalencia fuente-nativa del lifecycle. 023–028 demostraron bypass de escritura al margen de un launcher seguro; no declararlo resuelto.
4. Entregar JSON de medidas y propuesta decisional **sin puntajes arbitrarios ni estimaciones de ahorros Product**. No se editará Product, no se instalará Beads en Product ni se creará otro ledger.

## DoD

Un intento acotado GitHub Actions por sujeto Git; resultado original JSON con métricas y controles, TXT `IR-TXT-CARRIER/1` creado/verificado/extraído con Product `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`. Publicación create-only en branch experimental lab, un único commit final y diagnóstico de fallos preservado. Comparación y recomendación experimental únicamente; Product authority NONE.

**Resultados no calificados:** medición de performance de producción, prueba de reducción neta del código, protección universal contra bypass privilegiado, migración de consumidores existentes, garantía de retención/archivo durante shutdown.
