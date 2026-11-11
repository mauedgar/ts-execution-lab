---
document_id: TS-EE-CONSUMER-TASKCYCLE-POSTINIT-INTERFACE-v1
owner: TS_EXECUTION_ENGINEERING
type: bounded_consumer_operational_method
status: PROPOSED_PENDING_INDEPENDENT_REVIEW_NOT_QUALIFIED
updated: 2026-11-11
provenance: TS-EE-POSTINIT-AWARE-PR16-WEBINLINE-IR001-20261111-001
authority_product: NONE
authority_taskcycle: NONE
authority_implementation: NONE
---

# TS EE — Interfaz post-init TaskCycle v1 (reparación de IR001)

## 1. Clasificación y límites

**Esta es una propuesta de contrato de ejecución, NO una API implementada ni una capacidad calificada.** El Developer autorizó proponer un contrato operativo acotado para el consumidor Aware y remitir cualquier adaptación semántica a **Tecnotron Control**. [Tecnotron issue #71](https://github.com/mauedgar/tecnotron-ai/issues/71) es la solicitud competente de disposición. Ningún texto en este repositorio otorga grants, valida decisiones Product, cierra obligaciones, activa Phase_2, migra Kernel o autoriza a Commander a explorar/revisar código.

Baseline: `mauedgar/aware-commerce`, original `TASKCYCLE-AWARE-P0-REPAIR-001`, manifest SHA256 `73c8b8de6de6ece29f467b4c72cbb2ef83786039ae10d6a64ca623b91a24219f` y projection SHA256 `ce2e59c56ea67703730dd486bf6fbb98da1b8575691aab810dd57389273bb7a8`. El módulo verificado `tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88:src/deterministic-taskcycle-substrate-v0/taskcycle-initialization.js` no calificó una API post-init. [Recibo nativo original](https://github.com/mauedgar/aware-commerce/issues/19#issuecomment-6786411578); [P0 Product merge](https://github.com/mauedgar/aware-commerce/issues/19#issuecomment-6786168725); [SPEC/ADR v3 accepted](https://github.com/mauedgar/aware-commerce/issues/4#issuecomment-6786758557). Estos últimos efectos externos NO reescriben la proyección inicial.

**Cambio respecto a v0:** la [IR001 original de PR16](https://github.com/mauedgar/ts-execution-lab/pull/16#issuecomment-6787572764) emitió `TS_EE_CONTRACT_NO_RECOMMEND/4F/4A` sobre `HEAD=9ae410051c08349185fffe0ddc5078fd52d03f2b`. Este documento v1 es un **nuevo candidato semántico**, no un amend, replay ni reinterpretación de IR001/PR16; v0 permanece histórico, no integrado.

## 2. Separación de owners

| Owner | Decisión o efecto |
| --- | --- |
| Aware Product Developer/Control | Selecciona responsabilidad/gate/obligaciones, confirma qué evidencias externas satisfacen criterios y firma/atestigua la decisión Product exacta; puede rechazar Phase_2 aunque CI/IR pasen |
| Tecnotron Control/TaskCycle semantic owner | Decide si una transición post-init es válida en el lifecycle adoptado; selecciona mecanismo cualificado o adaptación con su propia autoridad; no necesita nuevo Kernel por omisión |
| TS Execution Engineering | Califica/verifica mecanismo determinista de transporte, identidad, autoridad **externa** vinculada, CAS/atomicidad/recibos, recovery y pruebas; nunca infiere semántica de un comentario o PASS |
| Runner materializer (futuro) | Solo ejecuta una solicitud ya completamente resuelta con guardas y límites comprobados; no decide qué transición se necesita, no reintenta UNKNOWN |
| Independiente Reviewer | Lee sujeto congelado, audita evidencias y emite recomendación, no muta Product ni acepta |

No permitir que `Actor`, `OpenCode session`, `model`, `chat`, `Github Issue`, `receipt file`, `Provider state` o un nuevo `execution_attempt_id` generen autoridad por sí mismos.

## 3. Identidad canónica de efecto, no de request (repara F01/A01)

La **identidad semántica de transición** debe existir fuera del transport y ser única por locus del ciclo. Identificadores operativos de request/attempt son aliases de una transición, nunca nuevas transiciones.

**Slot único** `(TaskCycle_id, original_initialization_manifest_digest, transition_slot_id)`, definido y fijado por el semantic owner competente. `transition_slot_id` representa una obligación/gate de ciclo **consumible una sola vez** en ese TaskCycle; la decisión semántica firmada incluye exactamente `from_gate`, `to_gate`, `from_state_version`, `sorted_unduplicated_obligation_ids`, `source_subject` (repo/commit/tree), `target_obligation_states`, `decision_id` y criterios. `transition_slot_id` no se derivará de un `request_id`, `execution_attempt_id`, actor ni ubicación del host.

`effect_identity_sha256 = SHA256("TS-EE-POSTINIT-v1:EFFECT\0" || canonical_cbor_or_json_v1(semantic_transition_without_transport_ids))`. El algoritmo/serialización canónicos exactos serán elegidos por el owner de la implementación y versionados antes de cualquier write. Mientras no exista esa calificación, no se aceptan efectos.

**Dos capas de identidad verificadas:**
- `unique(TaskCycle_id, transition_slot_id)` para evitar aplicar un gate/obligación otra vez bajo otro request/attempt, **incluso después de que HEAD avanzó**. Si el mismo slot ya existe, comparar el `effect_identity_sha256` y devolver el **recibo original** (idéntico) o `BLOCKED_PRECONDITION/NONE` (conflicto), jamás un nuevo evento.
- `unique(TaskCycle_id, expected_predecessor_seq, predecessor_digest)` junto con **CAS de HEAD** para impedir dos sucesores diferentes del mismo punto de la cadena, incluso si tienen slots diferentes.

Si Control produce dos `transition_slot_id` distintos para el **mismo gate semántico**, la definición del owner de lifecycle debe validar adicionalmente un **`single-use semantic gate invariant`** y los `target_obligation_states` contra el estado derivado actual; si ya está consumido, bloquear. No confiar solo en un digest que incluya un nuevo ID para evitar replay.

**Orden y hashes:** `sorted_unduplicated_obligation_ids` usa orden byte UTF-8 explicitado, sin duplicados; bytes del payload canónico no incluyen campos volátiles (`request_id`, hora de recepción, ubicación, `ExecutionAttempt`, timestamps). Dominios hash separados para `INIT`, `DECISION`, `EFFECT`, `EVENT`, `RECEIPT` y `HEAD`; no concatenar textos ambiguos, usar framing con longitud o canonical encoding cualificado. Toda huella lleva `schema_version` y `hash_profile`. La validación debe comparar pruebas de canonicalización (Unicode, CRLF, claves fuera de orden, enteros, lista de obligaciones permutada) antes del primer commit.

## 4. Authority / competent semantic attestation (repara F03)

`authority_ref` como string **no basta**. Se requiere `semantic_decision_attestation` verificable mediante **perfil de confianza versionado** seleccionado por Tecnotron Control, con:
- `decision_id`, `transition_slot_id`, issuer/principal competente, capacidad para el Product y TaskCycle declarado, emisión/cutoff, expiración/revocación si aplican y mecanismo de integridad del contenido (firma/hash Git inmutable/proveedor autenticado).
- Los campos exactos vinculados: `TaskCycle_id`, hashes originales, repo/branch/commit/tree, `from_gate`/`to_gate`, obligaciones y estados destino, `effect_ceiling`, predecessor/version esperado y `decision_body_digest`; `authority_ref` enlaza evidencia/registro inmutable o verificación nativa competente.
- Control confirma semántica y aceptación **antes** de generar la atestación. TS EE comprueba integridad, emisor/principal autorizado, binding exacto, fecha/revocación y ausencia de drift; **no** decide si la valoración de una IR es correcta.
- Un comentario GitHub editable, un documento de Library, la firma textual “Developer granted” o una clave proporcionada por el mismo worker **no prueban autoridad** sin un trust profile y verificación exterior.

**Fail closed:** `UNRESOLVABLE_AUTHORITY`, `AUTHORITY_BINDING_MISMATCH`, `REVOKED_OR_EXPIRED`, `WRONG_GATE`, `WRONG_OBLIGATION_SET`, `SUBJECT_DRIFT`, `MISSING_SEMANTIC_ATTESTATION` → `BLOCKED_PRECONDITION / NONE`; si verificar revocación depende de estado remoto ambiguo, `UNKNOWN / UNKNOWN` y no mutación. Esta interfaz **no selecciona/autoriza trust profile** para Aware/Tecnotron; Control debe hacerlo.

## 5. Authoritative CAS/head, write ordering and crash recovery (repara F02/A02)

Antes de implementar, seleccionar un provider duradero cuya operación calificada otorgue **un commit point atómico y linealizable**. Un `content_sha256` sin CAS no alcanza y no se garantiza esta cualidad en GitHub, Neon, filesystem u otro proveedor por su nombre.

**Modelo lógico candidato:**
- Un `genesis` inmutable referencia `TaskCycle_id`, SHA256 original manifest/projection, versión de esquema y namespace confiable; se verifica antes de todo evento. El directorio original queda sin cambios.
- `head` autoritativo identificable por `TaskCycle_id` contiene `seq` y `event_digest` con un único puntero. Los eventos incluyen el recibo/resultado terminal y la referencia a la atestación verificada, en un cuerpo inmutable. `HEAD` y evento/recibo deben ser visibles de forma **atómica** para consumidores o el evento no es visible hasta el CAS confirmado.
- En un **único commit transaccional calificado** se valida predecessor `(seq,digest)`, slot/gate single-use y autoridad; se registra evento+recibo, índices únicos y se mueve `head`. Si el proveedor no puede hacerlo en un solo commit, el protocolo tiene que definir staging invisible + CAS de head y **reconciliação** de orphans y dual-write con pruebas de crash **antes de calificación**.
- **Commit point**: la transición sólo tiene efecto cuando el head autoritativo fue actualizado y puede leerse con consistencia requerida. Un blob preescrito sin CAS/HEAD no es transición confirmada; un recibo emitido sin head confirmado no habilita gate.
- Lecturas de recuperación deben ser del mismo owner/consistency profile calificado; stale reads de réplicas/caches no acreditan ausencia de commit.

**CAS/precondition:** compare exact trusted genesis, `expected_seq`, `expected_head_digest`, versión del slot, original init hashes y autoridad. Para conflictos concurrentes uno gana, otro observa receptor original y `BLOCKED_PRECONDITION/NONE`; sin reintento a un nuevo predecessor por iniciativa del worker.

**Seguridad de paths:** ámbito aislado elegido por el owner, raíz confiable fija, checks de realpath, symlink/reparse/hardlink, traversal, path length/collision, create-only y allowlist por intento. Verificar SHA256 de la inicialización original **después** de cada transición cualificada. Nunca crear scripts, patches, zip o salidas arbitrarias en Commander; TS-EXB es transporte no ejecución de Product.

## 6. Terminal status, replay and uncertain effects (repara F04/A03)

`ALREADY_CONFIRMED` es únicamente **disposición de reobservación/replay**, no un nuevo status de transición, recibo, ExecutionAttempt o evento de Product. Remite por identidad única al **recibo terminal original** y a `head` probado. Reconsultar sin escribir no crea otro recibo y no altera secuencia.

| Terminal status | Effect state | Significado |
| --- | --- | --- |
| `PASS` | `CONFIRMED` | Commit point y postcondición comprobados; un evento autorizado queda confirmado |
| `BLOCKED_PRECONDITION` | `NONE` | No hay efecto, validación/autoridad/slot/CAS no pasó antes del commit |
| `FAILED` | `NONE` | Error mecánico demostrado antes de cualquier commit |
| `FAILED` | `CONFIRMED` | Error después de commit point **ya verificado**; efecto existe y no se puede repetir para “arreglar el resultado”; preservar recibo original y diagnóstico |
| `UNKNOWN` | `UNKNOWN` | Commit o lectura del efecto no determinables; bloquear operación conflictiva y toda repetición |

Cualquier otra combinación es inválida en v1 y debe ser rechazada por validador. `BLOCKED_PRECONDITION` es un resultado competente, no una falla de Commander. `FAILED/CONFIRMED` no delega aceptación semántica; sólo evita duplicar un efecto realmente observado.

**Matriz de recuperación (decisión por evidencia):**
- Error antes de submit, sin efecto proveedor confirmado: `FAILED/NONE`.
- Submit y ACK exacto con head/recibo coincidentes: `PASS/CONFIRMED`.
- Timeout/ACK perdido: consultar **una vez por identidad exacta** head, slot y recibo en provider nativo calificado; `CONFIRMED` si coincide, `NONE` sólo si el proveedor garantiza ausencia y el commit no puede completarse más tarde; de lo contrario `UNKNOWN`.
- HEAD no observado por lectura eventualmente consistente: `UNKNOWN`, no inferir `NONE`.
- Evento existe sin HEAD en protocolo staging certificado: `NONE` de transición si el staging es demostrablemente invisible/no puede publicarse tarde; si CAS aún puede ocurrir, `UNKNOWN`.
- Recibo corrupto o HEAD apunta a digest faltante: `UNKNOWN`, no crear reemplazo.
- Reobservación del mismo `transition_slot_id` y digest después de PASS: `ALREADY_CONFIRMED` remite a recibo original; identidad distinta misma semántica no crea transición.

**No blind retry:** interrupción del chat, ausencia de archivo o un nuevo modelo no conceden autoridad para generar `retryN`, reemplazar intento o modificar un evento terminal. Si la evidencia es insuficiente, parar y declarar `UNKNOWN`.

## 7. Complete proposed request fields (schema NOT IMPLEMENTED)

```yaml
schema: ts-ee-postinit-transition-envelope/v1-proposed
hash_profile: CANONICAL_PROFILE_NOT_YET_QUALIFIED
provider_profile: EXPLICIT_VERSIONED_PROVIDER_NOT_YET_QUALIFIED
trusted_genesis:
  taskcycle_id: exact
  original_manifest_sha256: sha256:...
  original_projection_sha256: sha256:...
  genesis_digest: sha256:...
semantic_transition:
  slot_id: owner_assigned_single_use_gate_key
  from_state_version: exact
  from_gate: exact
  to_gate: exact
  sorted_unique_obligation_ids: [exact]
  target_obligation_states: [exact]
  product_subject: {repo: owner/name, branch: exact, commit: full_sha, tree: full_sha}
  decision_id: semantic_owner_stable
  effect_identity_sha256: sha256:...
  semantic_decision_attestation:
    authority_ref: immutable_competent_source
    issuer: qualified_owner
    decision_body_digest: sha256:...
    trust_profile: exact_qualified_id
    verified_binding_status: independently_verified
preconditions:
  expected_predecessor_seq: integer
  expected_predecessor_digest: sha256:...
  intended_effect_ceiling: exact
execution_transport:
  request_id: transport_id_not_effect_identity
  execution_attempt_id: original_attempt_id
  runner_name: exact
  runner_version: exact
  runner_sha256: sha256:...
  allowed_destinations: [isolated_create_only_paths]
terminal_receipt:
  status: PASS|BLOCKED_PRECONDITION|FAILED|UNKNOWN
  effect_state: NONE|CONFIRMED|UNKNOWN
  original_receipt_ref: exact_if_replay
  head_digest: sha256:..._if_confirmed
  event_digest: sha256:..._if_confirmed
  result_digest: sha256:...
```

No usar el literal `verified_binding_status` provisto por el caller como prueba. La verificación debe ser un **acto de confianza independiente** y el recibo registrar el verifier/cutoff. El esquema sobre papel no ejecuta ni cualifica un proveedor.

## 8. Qualification test matrix and release gate

| Test ID | Negative / positive test | Required disposition |
| --- | --- | --- |
| Q01 | Valid attested decision, exact manifest/projection/predecessor, one writer | Single event+receipt+head committed, original initializer hashes unchanged |
| Q02 | Re-observe exact request/attempt, same slot and same semantic digest | `ALREADY_CONFIRMED` original receipt only, no new event |
| Q03 | Same semantic transition with **different** request/attempt or decision ID | One effect by unique slot/gate, no duplicate |
| Q04 | Same slot but different payload or target obligation set | `BLOCKED_PRECONDITION/NONE`, no second successor |
| Q05 | Two different valid slots race for same predecessor | Exactly one head CAS; other blocked/needs competent replan |
| Q06 | Unknown/missing/expired/revoked grant, wrong issuer/baseline/obligation | Fail-closed before effect; no self-authorized approval |
| Q07 | Crash before event staging, after staging, immediately before/after commit point, before response | Deterministic reconciliation or `UNKNOWN`; no blind retry or duplicate |
| Q08 | Provider stale read, unavailable receipt, HEAD/event mismatch/corrupt digest | `UNKNOWN/UNKNOWN` and stops until reconciliation |
| Q09 | Alter original init manifest/projection, wrong TaskCycle, wrong source subject | `BLOCKED_PRECONDITION/NONE` |
| Q10 | Payload canonicalization ambiguity: Unicode/CRLF/permutation/duplicate obligations | Same valid canonical bytes or input reject; no semantic alias |
| Q11 | Symlink/reparse/hardlink/traversal, collision, off-root files | Reject and verify no source writes |
| Q12 | Remote or local runner with wrong binary hash, permissions or model config | BLOCKED, no execution and no request mutation |
| Q13 | Semantic owner denies Phase_2 despite CI/IR PASS | No Phase_2 event; Execution Engineering cannot infer |
| Q14 | Forbidden status/effect combination, duplicate receipt or orphan staging | Rejected or `UNKNOWN`, preservation and disclosure |

**Required prereqs before native Product effect:** current Tecnotron Control decision/authority, trust verifier profile adopted, provider/atomicity profile qualified, complete runner/source/policy/allowlist hashes, deterministic tests Q01–Q14, Independent Review 0F/0 unresolved A and Developer acceptance for **exact** transition, not merely this document. No auth/verifier implementation was created by this proposal. No Product source code, Kernel/DBOS/Neon schema or file system was changed.

## 9. Disposition and handoff

`TS_EE_POSTINIT_INTERFACE_v1=PROPOSED_UNQUALIFIED`; **Product authority NONE**. `Phase_2` original Aware TC remains **NOT_ACTIVATED**. Original [PR16/IR001](https://github.com/mauedgar/ts-execution-lab/pull/16#issuecomment-6787572764) historical `NO_RECOMMEND/4F/4A` unchanged. A new independent v1 review, Control audit and integration authorization are required before this contract could become an accepted **method**; even then **no runtime** is qualified until provider+runner Q01–Q14 and semantic owner grant.

**Tecnotron Control** must choose adopted lifecycle owner, reuse vs adapter, exact semantic grant and effect decision, and whether/when this method is applicable. [Issue #71](https://github.com/mauedgar/tecnotron-ai/issues/71) is the recipient of that disposition. TS EE no longer invents a second Kernel. Aware may develop early catalogue in separate bounded TASKs without pretending the post-init TC has advanced.
