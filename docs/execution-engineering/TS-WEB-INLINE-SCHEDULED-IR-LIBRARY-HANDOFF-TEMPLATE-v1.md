# WEB_INLINE — Scheduled Independent Review + verified Library handoff template v1

```yaml
id: TS-WEB-INLINE-SCHEDULED-IR-LIBRARY-HANDOFF-TEMPLATE-v1
owner: TS_EXECUTION_ENGINEERING
kind: EXECUTION_BINDING_DISPATCH_TEMPLATE
scope: WEB_INLINE_SCHEDULED_ONLY
status: ACTIVE_DISPATCH_TEMPLATE
Product_authority: NONE
Product_effect: NONE
Independent_Review_adjudication: NONE
```

## Purpose and authority

This document repairs the **launch prompt contract**, not the Product reviewer responsibility or independence policy. The existing binding is `docs/execution-engineering/TS-WEB-INLINE-INDEPENDENT-REVIEW-BINDING-v0.md`. Its Library hop is mandatory for the scheduled WEB_INLINE arrangement; the previous shortened launch phrase ("consume handoff and execute IR") was **insufficient because it did not explicitly instruct the reviewer to persist ORIGINAL**. An immutable review handoff alone does not guarantee that the scheduled executor follows the separate transport contract.

The operator MUST replace the four tokens `<FROZEN_INPUT_GIT_REF>`, `<REVIEW_ID>`, `<EXECUTION_ATTEMPT>`, and `<EXPECTED_GIT_RESULT_PATH>` with the exact current authorized values. The scheduled task's **prompt itself** must contain the complete instructions below, even if the frozen handoff already references the binding. No new Product authority, review scope or retry is granted.

## Required scheduled task prompt (copy verbatim; replace tokens only)

```text
Consumí íntegramente <FROZEN_INPUT_GIT_REF> y ejecutá en ESTE contexto separado
una sola Independent Review WEB_INLINE STRICT_READ_ONLY conforme al input.
Review_ID: <REVIEW_ID>. ExecutionAttempt ORIGINAL: <EXECUTION_ATTEMPT>.
Resultado GitHub final previsto (NO escribirlo desde esta tarea):
<EXPECTED_GIT_RESULT_PATH>.

Verificá el sujeto Git exacto, leé y evaluá la totalidad del inventario requerido,
informá findings/advisories, cobertura real, pruebas realizadas y limitaciones.
No modifiques Product, PR, CI, Neon, secretos, roles, staging ni producción.

Generá exactamente UN ORIGINAL completo como bytes UTF-8 inmutables. Calculá
el tamaño exacto en bytes y SHA-256 del ORIGINAL. Antes de responder, SUBÍ
ese MISMO archivo a la Library personal de ChatGPT mediante la herramienta
de gestión de archivos/Library que esté disponible (no basta crear /mnt/data).
Confirmá que la herramienta devolvió status=succeeded y guardá el
library_file_id y file_id originales. Volvé a leer/materializar la copia de
Library cuando sea posible y compará tamaño, SHA-256 y bytes con el ORIGINAL.
No infieras éxito de una ruta local, un enlace sandbox o una intención de subida.

La respuesta debe contener:
- review_id, execution_attempt, commit/tree y disposición del ORIGINAL;
- transport_status: LIBRARY_VERIFIED, LIBRARY_UPLOADED_UNVERIFIED,
  BLOCKED_TRANSPORT o UNKNOWN_EFFECT (según la evidencia);
- library_file_id y file_id SOLO si fueron devueltos por la herramienta;
- tamaño byte_length y SHA-256 con método/evidencia; identificá si NO_VERIFIED;
- ubicación/identidad del ORIGINAL y el motivo exacto si hay bloqueo;
- confirmación de que la revisión semántica se ejecutó una sola vez.

Si la herramienta de Library no existe, está denegada, falla o no confirma
la persistencia, devolvé BLOCKED_TRANSPORT sin fingir éxito; preservá el
ORIGINAL y su identidad, junto con el enlace de descarga cuando exista.
Si el efecto de subida es ambiguo, devolvé UNKNOWN_EFFECT y NO vuelvas a
subir sin reconciliar el registro original. NO repitas la revisión semántica
para reparar transporte. No reescribas el ORIGINAL ni lo publiques como
resultado GitHub desde esta tarea programada: la publicación GitHub
idéntica por bytes corresponde al Control en puente interactivo.
```

## Control pre-dispatch — fail closed

Before **any** task creation, Control must check and record that:
1. A competent authority already selected WEB_INLINE, the exact candidate Git HEAD/tree and the frozen review input. No older original result or uncertain original attempt is being replayed.
2. All four template tokens are replaced with specific immutable identifiers. The complete Library requirement (explicit upload, succeeded receipt, `library_file_id`, `file_id`, byte length, SHA-256, verification, fail-closed) exists in the actual `automations.create.prompt` sent to the provider, **not only in this reference file**.
3. The scheduled task identity/return target is distinct from Control. A successful scheduling receipt is **SCHEDULED**, never REVIEW_PASS, LIBRARY_VERIFIED or PRODUCT_ACCEPTED.
4. The original result and review attempt are reconciled with provider-native state before a repeated task, run_now, change of surface or bridge operation. A single terminal reviewer result is not restarted due to a transport error.
5. Check whether Library upload tools are available in the selected scheduled context if the platform exposes that fact. If capability is unknown, explicitly classify `UNKNOWN_PRE_DISPATCH_CAPABILITY`; this is **not** proof Library will work, and the scheduled prompt must still fail closed on missing capability. Do not assume a scheduled task inherits interactive tools.

## Control post-run bridge — original bytes only

Observe the same scheduled `ExecutionAttempt` and provider-native terminal receipt, then:
- If `LIBRARY_VERIFIED`, read the precise `library_file_id`/`file_id` and verify original bytes/digest/length/identity in Control before publishing **create-only** to `<EXPECTED_GIT_RESULT_PATH>`. Verify Git blob, commit and readback. Git publication is not Product acceptance.
- If Library uploaded but verification unavailable, perform verification in Control without re-running the review.
- If `BLOCKED_TRANSPORT`, recover the original file from its reviewer output or user-provided attachment; preserve identity and digest. Library can be populated interactively and verified; publish Git original once. Do not reconstruct a full ORIGINAL from a short task summary.
- If `UNKNOWN_EFFECT`, reconcile exact Library identity/destination and original Git target before any retry.
- Never use success of task scheduling, a sandbox link or existence of an MD filename as evidence of verified Library persistence.

## Regression case that motivated this template

Attendance `ATTENDANCE-C5-V8-PR21-WEBINLINE-IR002-20261110-001`,
attempt `ATTENDANCE-C5-V8-PR21-IR002-A001` concluded
`NO_RECOMMEND, 0F/5A` in a separate scheduled context but returned only
`/mnt/data/ATTENDANCE-C5-V8-PR21-IR002-A001-ORIGINAL.md`. The prompt
omitted the explicit Library upload instruction. The user provided the exact
7,374-byte file, SHA-256
`fefd09b618f8e89d56dfce87a64e373259bc717e1188a91a1191c4566f0d04b2`.
Control preserved the original bytes in personal Library
`libfile_24278c95b154819197167c45d83d86d8` and published an identical
Git blob `20918b2d33db875773383497dea93ab183d74b8e` in Transport
commit `00cf96b0c787e6fdba12cd5d7dc441d333abe53e`.
This verified **interactive recovery of an existing original**, not a scheduled
Library upload. No new IR attempt, Product acceptance, integration or production
action resulted.

## Qualification limits

This template is an explicit prompt and audit requirement. It is **not a
guarantee** that future scheduled tasks have the Library tool, that provider
internal isolation is formally qualified, or that user-visible ChatGPT files
automatically persist. The original binding remains
`EXPERIMENTAL_SYNTHETIC_PASS_PENDING_PRODUCT_QUALIFICATION`.
Promoting it to a guaranteed unattended review + Library bridge requires a
separate empirical qualification; do not claim that from this documentation.
