# TS — Beads 024 | Control experimental: selección y criterios

**Estado:** CONTRACT_SELECTED_FOR_NONPRODUCT_EXPERIMENT / NO_PRODUCT_AUTHORITY.  
**Propósito:** calificar una vista de lectura del grafo nativo Beads que sea explícitamente informativa, incluso cuando un escritor no controlado modifica aristas o revisiones.

**Autoridad experimental:** el usuario delegó Control dentro de la línea experimental. Control Product de Tecnotron **no** se transfirió; la SOT competente sigue en `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`, y el TXT 023 está en `mauedgar/ts-execution-transport@8231c0898c6ee6e9585ae946dacde13928d4c013:results/TS-BEADS-023-TXT-PORTABLE-CARRIER-20261024-001/EVIDENCE_CARRIER.txt`.

## Selección

El envelope 023 se consumió y se evaluó como entrada experimental. Se preserva la incompatibilidad demostrada: `bd dep add` puede agregar una dependencia sin actualizar `root.revision`. La mitigación `update root + dep_add` funciona solo con escritores controlados; **no** es exclusividad general.

Por tanto **no** se concede adopción del grafo para decisiones autoritativas. El siguiente incremento independiente es un consumidor de solo lectura que no emite permisos ni inicia/cierra TaskCycles, no ejecuta acciones externas y no interpreta `bd ready` como aceptación.

## Contrato acotado del 024

El lector realiza dos recorridos sucesivos independientes con `GET /v0/beads/issues/{id}?brief_deps=true`, arma el cierre transitivo del grafo con versiones por issue y devuelve sólo:
- `NONAUTHORITATIVE_OBSERVATION`, si dos pasadas tienen filas y aristas iguales;
- `INCONSISTENT_GRAPH`, si difieren filas, revisiones, estados o dependencias;
- `INCOMPLETE_READ`, si falla alguna adquisición.

**Siempre:** `authority=NONE_PRODUCT`, `mayAuthorize=false`. Incluso dos pasadas iguales **no** representan un snapshot transaccional ni protección contra cambios posteriores. No se crea estado mutable duplicado.

**Tests nativos aislados:** baseline transitivo, carrera `bd dep add` sin cambio de versión raíz, reobservación de arista nueva, mutación concurrente sobre ancestro, escritura irrelevante, consulta native `bd ready` como información y persistencia CLI independiente.

**DoD:** evidencia nativa terminal con sujeto commit/run exactos; TXT `IR-TXT-CARRIER/1` generado/verificado/extraído mediante `scripts/review_txt_carrier.py` existente; confirmación Product y Dolt compartido intactos; informe y limitaciones. Si falla el test, conservar intento y diagnosticar sin autoaceptar ni repetir efectos externos originales.

**Exclusiones:** decisiones Product, cambio de State Kernel, efecto remoto original, permiso de writer exclusivo, revisión independiente semántica como dictamen Product, migración de consumidores en Tecnotron, eliminación de deuda Developer `REJECTED`.
