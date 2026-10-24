# TS — Beads 025 | Contrato de Control experimental: frontera real del escritor causal

**Selección experimental autorizada por el usuario:** investigar la frontera efectiva de escritura del grafo Beads, sin añadir un ledger global, sin modificar Product ni dar nuevos grants o estados TaskCycle.

**Originales competentes reobservados:** `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56` tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`, SOT blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, estado actual blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`. Lab base `main@b30241201d07a9590e1e845abe767cdcf9921479`, Dolt remoto compartido `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.

**Evidencia previa:** 023 documentó bypass de `bd dep add` sin cambio de `root.revision`, contra CAS del conjunto viejo, y la mitigación condicional `update(root, expected_version) + dep_add` en una transacción nativa. Control experimental 024 calificó solo una vista no autoritativa. Ambas pruebas y receipts se preservan, no se repiten como efectos.

## Pregunta verificable

¿Puede un cliente no privilegiado, con acceso sólo a consultas nativas del grafo, alterar dependencias por el SQL o HTTP del mismo runner? ¿Puede bloquearse la ruta HTTP sin afectar a un escritor competente, usando políticas existentes de Dolt y del SO, **sin inventar otro orquestador o ledger**?

### Ensayo acotado, no Product

En un runner Ubuntu descartable:
1. Dolt SQL Server Beads v1.3.1/Dolt v2.2.0 en carpeta privada `0700`, root SQL protegido con contraseña efímera; usuario SQL distinto sólo con SELECT.
2. Proceso separado UID `nobody` lee SQL y se le niega escritura, y no accede al almacén directo del usuario competente.
3. Antes de proteger la API HTTP, ese proceso intenta `dep_add` sin `update(root)`: debe registrarse si una API local alcanzable permite eludir SQL y filesystem ACL y agregar arista sin cambiar la revisión raíz. Este es un **control negativo**, no una operación legítima.
4. Calificar un firewall de OS `iptables -m owner --uid-owner nobody` para impedir sólo conexiones de ese UID al puerto HTTP de escritura. Repetir ataque: debe quedar rechazado; el lector SQL sigue funcionando y el escritor autorizado aún hace `root update + dep_add` en batch con CAS; un segundo batch obsoleto debe ser rechazado.
5. Retirar la regla temporal en `finally`, terminar servicios y archivar sólo recibos sin claves ni tokens.

**El permiso de escritura SQL no basta**, porque el API HTTP nativo y el acceso a disco pueden eludirlo. Toda conclusión de aislamiento aplica únicamente al conjunto acotado de identidades, puertos y procesos probados. **La misma UID con acceso a credenciales / servidor, root o sudo, otro endpoint expuesto y varios hosts NO quedan calificados por una regla owner de iptables.** No declarar exclusividad general ni adopción Product si subsisten esas rutas.

Si `iptables` u otro control no existe en el runner, no simular una frontera segura: el resultado será `BLOCKED_NETWORK_OWNER_POLICY_UNAVAILABLE` con el contraejemplo conservado. Si cualquier prueba falla, el intento queda FAIL y se reconcilia antes de posibles correcciones.

## Evidencia y transporte

Un solo intento acotado por workflow GitHub Actions, original `ExecutionAttempt` ligado a Git SHA, runner, recibo JSON local. Emisión de TXT `IR-TXT-CARRIER/1` **mediante el script Product existente** `scripts/review_txt_carrier.py`, verificación y extracción byte-a-byte, publicación create-only en rama experimental del laboratorio; nunca sustituir por un nuevo ZIP como formato de transferencia. GitHub Actions podrá almacenar su artifact nativo histórico ZIP, pero no será la entrega principal.

**Criterio de control experimental:** `PASS_EFFECTIVE_UID_BOUNDARY_WITH_MATERIAL_SAME_UID_LIMITATIONS` sólo si todos los controles técnicos de ese caso pasan. Aun así, `READY_FOR_PRODUCT_ADOPTION` permanece **NO**; requiere calificación de todos los clientes, endpoints, identidad y credenciales reales y protección multi-host. Product sigue fuera de alcance.
