# TS Beads 032 — B-first native history checkpoint

**ID:** `TS-BEADS-032-NATIVE-HISTORY-20261029-001`

**Authority:** `EXPERIMENTAL_CONTROL_ONLY`. No Product authority, TaskCycle, Developer grant, Independent Review, acceptance, integration, Phase 2 or canonical adoption is created by this experiment.

## Frozen read-only references

- Product: `mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d`, tree `cbfb71ad8632047e8e64fe2665d8614d835a2c8b`.
- Product SOT blob: `dd8d34a7e3ef3094805d014f9e59741d2c553957`.
- Shared native Dolt ref: `mauedgar/ts-execution-lab:refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`; it must remain unchanged.
- Predecessor terminal receipt: `TS-BEADS-031-B-FIRST-HISTORY-20261029-001` at `f88ea6809b58b2900209a565fc340359db9cc0dc`; run `40907329055` is terminal and must not be replayed.
- Beads release: v1.3.1, tag target commit `c1c4b642ac1c08d8c828007a1c2f96e47e43ef7c`.
- Dolt release: v2.2.0.

## Question

Empirically qualify the **native Beads B history path** that 031 left open:

1. with `dolt.auto-commit=on`, does each successful isolated native Beads write advance the native Dolt commit identity;
2. does `bd history <id>` expose distinct persisted snapshots for those writes;
3. can `bd show --as-of <commit>` replay the prior issue state;
4. do current state and history remain readable from fresh Beads CLI processes after the writes.

This is an adequacy/history experiment, **not a claim of equivalence** to Tecnotron Kernel's global hash-linked event journal.

## Bounded fixture

Use a fresh disposable Git directory and Beads embedded Dolt store only. No remote is configured. Set:

- `BD_DOLT_AUTO_COMMIT=on`
- `BD_DOLT_AUTO_PUSH=false`
- `BD_NO_PUSH=1`
- `BEADS_ACTOR=TS-BEADS-032-NONPRODUCT`

Perform exactly two synthetic issue writes:

1. create `ts032-history-root` with description `TS032-V1`;
2. update the same issue to description `TS032-V2`.

For each write, record `bd vc status --json` commit identity and `bd history --json`. Then read V1 and V2 through `bd show --as-of` using the observed native commit hashes and re-read current state/history in later CLI processes.

## PASS ceiling

`PASS_NATIVE_HISTORY_AUTOCOMMIT_AND_ASOF_REPLAY` requires all of:

- Product/tools and shared Dolt refs unchanged before and after;
- isolated experiment Git has no remote;
- initial, create and update native commit identities are non-empty and each write advances HEAD;
- history contains distinct commit snapshots for V1 and V2;
- as-of replay at the V1 commit returns V1;
- as-of replay at the V2 commit and fresh current read return V2;
- later fresh-process history preserves both commit identities;
- Product effect, shared Dolt effect and provider effect are all `NONE`.

## Explicit non-claims

This experiment does **not** qualify:

- semantic equivalence to Kernel global revision/hash-chain/event-count invariants;
- real external provider effect identity, lost ACK, UNKNOWN recovery or no-duplicate dispatch;
- exclusive causal writer under privileged `bd`/Dolt access;
- production admission, installed Product integration, Kernel removal or Product architecture adoption.

After a PASS, the next independent B-first research priority may be a **separate** real-provider/effect-identity experiment under tooling that authorizes the exact bounded fixture.
