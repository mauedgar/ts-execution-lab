# v0.2 Qualification Draft

Authority: `NONE`
Product effect: `NONE`
Worker: `C — QUALIFICATION / EFFICIENCY`

This is a qualification plan and fixture package. It is not the terminal
result and does not semantically approve Worker A or Worker B.

## Matrix

The complete machine-readable matrix is `qualification/matrix.json`. Every
DoD is intentionally `PENDING_EXECUTION`; this worker has not executed the
v0.2 runner or remote workflow and therefore claims no PASS.

| DoD | Qualification proof | Prepared evidence | Status |
|---|---|---|---|
| DOD-01 | Windows Node 22.x and Ubuntu Node 22.x native TS runner | none | PENDING_EXECUTION |
| DOD-02 | JSON carriers, Zod boundaries, malformed request blocked pre-effect | none | PENDING_EXECUTION |
| DOD-03 | bounded `validate`, `run`, `profiles`; result and receipt artifacts | none | PENDING_EXECUTION |
| DOD-04 | both registered bounded profiles and exact Git identity | none | PENDING_EXECUTION |
| DOD-05 | one local Node invocation versus v0.1 materialize/parse path | v0.1 result only | PENDING_EXECUTION |
| DOD-06 | same runner/profile and matching local/remote semantic output | `qualification/local-remote-equivalence.json` | PENDING_EXECUTION |
| DOD-07 | private caller topology and no added credentials | prior topology evidence | PENDING_EXECUTION |
| DOD-08 | three context classes and two isolated synthetic Products | none | PENDING_EXECUTION |
| DOD-09 | safe `EFFECT_NONE` Attempt A, new Attempt B, UNKNOWN block | `qualification/fallback-proof.json` | PENDING_EXECUTION |
| DOD-10 | receipt observations and experiment efficiency facts | none | PENDING_EXECUTION |
| DOD-11 | adaptive remote observation and information gain | prior wait evidence | PENDING_EXECUTION |
| DOD-12 | measured before/after for local, remote, private cases | `EFFICIENCY-DRAFT.json` | PENDING_EXECUTION |
| DOD-13 | friction by binding/stage; no steady-state OpenCode dependency | none | PENDING_EXECUTION |
| DOD-14 | terminal artifacts classify all DoDs | not yet authorized for Worker C | PENDING_EXECUTION |

## Equivalence Fixture

`qualification/local-remote-equivalence.json` fixes one v0.2 request, profile,
subject, context, and expected canonical digest. The only fields allowed to
differ after execution are provider-specific binding/native references and
timings. It does not substitute for actually running both bindings.

## Fallback Fixture

`qualification/fallback-proof.json` requires Attempt A to stop at a binding
preflight with `effect_state: NONE`, then requires Attempt B to use a distinct
`ExecutionAttempt_ref` while retaining the Product operation, profile, and
request identity. `EFFECT_UNKNOWN` remains blocking. The fixture does not
claim either attempt was executed in v0.2.

## Efficiency Measurement

`EFFICIENCY-DRAFT.json` carries the v0.1 evidence pointers and blank v0.2
measurements for the three required cases. A terminal disposition may be
`PASS` only after measured evidence improves at least two required dimensions;
architecture alone is insufficient.

## Scope Guard

No `src/**`, workflow, Product repository, main branch, or merge was modified
by Worker C.
