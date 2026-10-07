# Worker C Qualification — Repair 001

Preserve draft status; do not claim PASS.

Align qualification fixtures to the reviewed Core contract:
1. canonical-sha256/v0 request input is:
   "input": { "payload_json": { "hello": "world", "n": 1 } }
   (ordering may differ; canonical digest remains sha256:32b769982a3a6e2df120530b06dcbaf1e8f75e004ceea92ac3e91bd7a248d728).
2. Current canonical/git profiles are READ_ONLY. Successful runner execution therefore has effect_state NONE, not CONFIRMED.
3. Fallback invariant:
   - Product_operation/profile/subject/context/input/request_id remain the same.
   - ExecutionAttempt_ref changes.
   - stable request_identity must remain the same because attempt identity is separate.
   - EFFECT_UNKNOWN still blocks fallback.
4. Keep every unexecuted proof PENDING_EXECUTION.

Do not edit src/** or workflows. Commit/push branch and stop.
