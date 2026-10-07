# Worker A Core — Repair 001

Preserve current candidate. Apply only these review findings, run focused tests, commit/push branch, then stop.

1. Fallback identity invariant:
   - ExecutionAttempt_ref MUST NOT perturb request_identity.
   - request_identity represents the stable already-decided mechanical request across attempts/bindings.
   - It MUST still change if profile, Product operation, subject, context/context_manifest, Product_ref, request_id, contract version, or input changes.
   - Add tests proving attempt A vs B have the same request_identity when only ExecutionAttempt_ref differs, and different identity when actual request semantics/input differs.
   - Keep ExecutionAttempt_ref separately in result/receipt.

2. UNKNOWN_PROFILE is an unsupported request resolved before profile execution:
   - emit BLOCKED / effect_state NONE, not UNAVAILABLE.
   - Add/adjust test.

3. Preserve result_status/effect_state separation.
   - Current registered profiles are READ_ONLY, so successful execution effect_state NONE is correct.
   - Do not generalize profile exceptions to NONE if future effectful profiles are introduced. Either encode failure effect mechanically from profile.effect_class or keep v0.2 explicitly read-only in a way that fails closed for unsupported effectful profiles.

Do not edit workflows or qualification artifacts. Do not merge.
