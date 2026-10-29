# TS — Beads 032 | Dictamen de Control experimental: historia nativa B-first

**ID:** `TS-BEADS-032-NATIVE-HISTORY-20261029-001`  
**Fecha:** 2026-10-29.  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`. Este dictamen no crea autoridad Product, TaskCycle, Developer grant, Independent Review, aceptación, integración, Phase 2 ni adopción canónica.

## 1. Reconciliación de 031

El predecessor `TS-BEADS-031-B-FIRST-HISTORY-20261029-001` queda preservado terminal:

- branch/receipt: `mauedgar/ts-execution-lab@f88ea6809b58b2900209a565fc340359db9cc0dc`;
- source run: GitHub Actions `40907329055`, source `98b2cbebecf21980cbe84cfeba29129774743375`;
- terminal: `completed/success`;
- disposición: `PASS_SOURCE_AND_HISTORICAL_EVIDENCE_AUDIT_WITH_NATIVE_AND_PROVIDER_GATES_OPEN`;
- **NO REPLAY**.

Product permaneció read-only en `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`. El shared Dolt ref permaneció `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`.

## 2. Investigación 032 seleccionada

B-first se preservó. Se abrió únicamente el gate independiente de historia nativa que 031 había dejado sin calificar:

- branch: `experiment/beads-032-native-history-checkpoint-20261029-001`;
- Beads v1.3.1 / Dolt v2.2.0;
- store embedded y disposable;
- sin Git remote;
- `BD_DOLT_AUTO_COMMIT=on`, auto-push desactivado;
- dos únicas escrituras sintéticas sobre `ts032-history-root`: `TS032-V1` y `TS032-V2`;
- Product/provider/shared-Dolt effects: `NONE`.

### Intento 1 — preservado FAIL de harness

- run: `40928349563`;
- source: `0360389d38eb6e8ff4687927a3230a1e6bb78223`;
- job: `123639811068`;
- terminal: `completed/failure`.

El intento se detuvo antes de la primera escritura por una aserción falsa del harness que exigía el layout físico `.beads/dolt` para embedded Dolt. No produjo evidencia negativa sobre historia Beads y no se reejecutó ciegamente.

Corrección acotada: commit `86ff281c5106ac29a11678b4589d96b06e90e9d6`, eliminando solamente la suposición de path y preservando pregunta, criterios y efectos.

### Intento 2 — terminal PASS

- run: `40928581506`;
- source: `cbcf93891727bdfa6757889e6f12710826013f3d`;
- job: `123640627871`;
- terminal: `completed/success`;
- evidence publication commit: `8cbc04d5279138d027005fe09985310e1b526050`;
- evidence tree: `b480fd805cfcba657d4e8d740565f521778d4f67`;
- carrier: `transport/TS-BEADS-032-NATIVE-HISTORY-20261029-001/EVIDENCE_CARRIER.txt`;
- Git blob: `e75ebc1553d647cb5ba7e757cd3ab9b7675e9fb4`;
- carrier SHA-256: `d2c80e10fa8e329fe9e817763db452016493c32b05af1ee3e4a47c04032d9e0c`;
- carrier bytes: `9587`;
- result: `PASS_NATIVE_HISTORY_AUTOCOMMIT_AND_ASOF_REPLAY`, 18/18 checks.

## 3. Qualified result

Observed native Dolt commit sequence:

- initial: `nmkdn9ipiplc8kvsnl2vdqop65mijvti`;
- after create V1: `3jv8ctps7mi3la2uh8cmoaknnl4sofdd`;
- after update V2: `26gdn7svf0s772f0tk6f1e8e7a47ripp`.

Each successful write advanced the native commit identity. `bd history` exposed distinct V1/V2 snapshots; `bd show --as-of` replayed V1 and V2 at their exact commits; later fresh CLI processes retained current V2 and both history commits.

**Experimental disposition:** `B_FIRST_NATIVE_HISTORY_QUALIFIED_EXPERIMENTAL_ONLY`.

This qualifies the bounded native history mechanic required by the B-first line. It does **not** establish semantic equivalence to Tecnotron Kernel's global revision/hash-linked event journal.

## 4. Remaining boundaries

Still `NOT_QUALIFIED`:

1. semantic equivalence to Kernel global revision/hash-chain/event-count invariants;
2. real independent external-provider effect identity, actual lost ACK and UNKNOWN recovery without duplicate dispatch;
3. exclusive causal writer under privileged alternate `bd`/Dolt access;
4. production admission, installed Product integration and Kernel removal.

The historical 018 experiment proves only a disposable local filesystem provider fixture and explicitly leaves real GitHub/Actions/Transport/provider effects unqualified. The 031 rotation also records that a more privileged native/provider fixture publication was blocked by tool security controls before execution.

Therefore no new provider dispatch is selected here. A real-provider experiment requires a separately bounded, permitted provider fixture with exact effect identity and reconciliation semantics; absence of such a fixture is a technical/authority boundary, not a Product lifecycle state.

## 5. Continuation state

- B-first: **PRESERVED**.
- 031: **TERMINAL / NO REPLAY**.
- 032 history: **TERMINAL PASS**.
- Product writes: **NONE**.
- shared Dolt writes: **NONE**.
- new external provider effects: **NONE**.
- next safe research: provider/effect identity only after a permitted exact fixture exists; otherwise stop at this boundary.
