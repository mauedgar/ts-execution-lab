# TS Beads 027 — Control experimental | servicio de escritor aislado

**Estado:** CONTRACT_SELECTED, no Product adoption. **Autoridad:** Experimental Control only. No TaskCycle, Developer grant, IR Product ni Phase 2.

**Sujeto Product read-only:** mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56; tree 8caa56d36f3efeba359bbbf65b158ffb01a19da6; docs/SOURCE_OF_TRUTH.md blob dd8d34a7e3ef3094805d014f9e59741d2c553957; docs/current-state.md blob 0d8a6426f51020d51d74bfb50dc8702a07f02837. Base lab main@b30241201d07a9590e1e845abe767cdcf9921479; shared Dolt refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571.

**Motivo:** 025 separó UID con ACL SQL y red pero dejó bypass same-UID. 026 demostró 33/33 que el token Bearer Beads v1.3.1 protege endpoints, rota y se recupera, pero mismo UID accede al secreto y al CLI Dolt; servicio caliente conserva última credencial cuando desaparece el token. Dictamen original: mauedgar/ts-execution-lab@a01cf0d48698f4670facef9e899436c0c0e2b299:experiments/TS-BEADS-026-NATIVE-AUTH-20261026-001/CONTROL_EXPERIMENTAL_VERDICT.md.

## Selección de experiencia 027

Calificar dos identidades Unix **distintas** en runner Linux descartable: escritor tiene Dolt root y archivo bearer privados 0700/0600; lector tiene SELECT-only SQL, no acceso a directorios/secretos del escritor ni a API privilegiada. Ensayar write nativo exacto por root-update expected_version + dep_add atómicos, rechazo CAS obsoleto, reanudación tras restart con autenticación obligatoria y startup sin token (fail closed). Ejecutar negativa de despliegue: reiniciar servicio sin --auth-token-file y mostrar que un cliente lectura puede añadir una arista; detener inmediatamente ese servidor y restaurar el protegido.

Este contraste evita una falsa solución: **la separación de UID solo es segura si también se preserva la postura de autenticación**. No se instala un nuevo scheduler, daemon propio persistente ni ledger global; únicamente los servidores nativos BD/Dolt y un harness de prueba local.

**Evidencia positiva requerida:** identidad diferente, reader SELECT sí y UPDATE no, private files inaccesibles, cinco rutas HTTP 401, escritura nativa competente y CAS, reanudación segura y negativos de configuración correctamente clasificados. **Limitaciones permanentes:** root/sudo, distribución multihost, contenedores/Kubernetes, side channels, inventario exhaustivo de endpoints, credencial robada, validación Product.

**Formato de entrega:** exact original JSON y PLAN en IR-TXT-CARRIER/1, generado/verificado/extraído con el script Product existente scripts/review_txt_carrier.py blob 96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4. Git experimental create-only. Original workflow metadata/attempt history and original terminal receipt remain accessible.

**Éxito de calificación:** PASS_SEPARATE_UID_WRITER_WITH_NATIVE_AUTH_CONFIGURATION_GAP significa frontera condicional demostrada **con fallo seguro ante postura de configuración incorrecta explícitamente NO demostrado**. Nunca implica READY_FOR_PRODUCT_ADOPTION.
