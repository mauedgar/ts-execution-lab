# TS — Beads 026 | Dictamen de Control experimental

**ID:** `TS-BEADS-026-NATIVE-AUTH-SAME-UID-RECOVERY-20261026-001`  
**Fecha:** 2026-10-26.  
**Estado experimental terminal:** `COMPLETE_WITH_MATERIAL_WRITER_EXCLUSIVITY_BLOCKER`.  
**Calificación técnica original:** `PASS_AUTH_BOUNDARY_WITH_SAME_UID_AND_TOKEN_LOSS_GAPS`, **33/33 verificaciones PASS**.  
**Control:** únicamente `EXPERIMENTAL_CONTROL`. **Tecnotron Product authority NONE**; no nueva TaskCycle, Developer grant, Phase 2, Independent Review Product, adopción canónica ni eliminación State Kernel.

## Reobservación de sujetos competentes

- Product read-only `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`, `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`. Branch experimental `experiment/beads-026-native-auth-boundary-20261026-001`.
- Shared Dolt ref `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` unchanged.
- Source Beads **v1.3.1**, `cmd/bd/serve.go`, `internal/httpapi/auth.go`, `internal/httpapi/server.go`: built-in `--auth-token-file` enforces Bearer auth for nearly all HTTP routes; bearer is a **full-surface shared secret**, no authenticated per-client identity or scopes. Reload failures retain last-good token set and do not immediately fail closed.
- Previous native authority and graph evidence in 023–025 preserved. 025 Control verdict `mauedgar/ts-execution-lab@c57f8594ad3f4b349c1146e800cd46b10051123a:experiments/TS-BEADS-025-WRITER-BOUNDARY-20261024-001/CONTROL_EXPERIMENTAL_VERDICT.md`.

## Original executions and identity

| Original run | Git subject | Terminal | Effects |
| --- | --- | --- | --- |
| [40271146459](https://github.com/mauedgar/ts-execution-lab/actions/runs/40271146459) | `1eedef08f8f419e02656e67324a87817cf957b86` | **FAIL**, workflow initially had stale name of 026 experiment branch in two mechanical references; before substantive native qualification | no Product |
| [40271201228](https://github.com/mauedgar/ts-execution-lab/actions/runs/40271201228), job `121404189609` | `7b68f53dceb1261c1beea1ffafe5e69c34afafc1` | **SUCCESS**, `PASS_AUTH_BOUNDARY_WITH_SAME_UID_AND_TOKEN_LOSS_GAPS`; native 33/33, TXT project/verify/extract PASS | disposable native Beads/Dolt only, Product NONE |

**Published original TXT envelope (qualified consumer format):** `mauedgar/ts-execution-lab@f5c102fa7d192dae5274ea1009783f2d13e64aad:transport/TS-BEADS-026-NATIVE-AUTH-20261026-001/EVIDENCE_CARRIER.txt`, blob `aa59c5b1c2c16bd19aa6121aeea4bf767ebea7e9`, SHA256 `55a5a0fc8b0ead967f93608ef6e419df162933cabe8ef3e139cbc7fc43a39883`, original 7,432 bytes. Existing `IR-TXT-CARRIER/1`, three members; `original/RESULT026.json` original member SHA256 `db963630758d812a6e424a708b983348358ad7d259954c20451253d244db9635`. Created, verified and extracted with Product `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4` and byte-wise readback. No ZIP carrier and no retry of original effect.

## Evidence: what works

1. **Native HTTP bearer protection:** each of six tested routes returned **401** without token and with invalid token: `GET /v0/beads/context`, `GET /v0/beads/issues/{id}`, `POST /v0/beads/issues:batchApply`, `POST /v0/beads/dependencies:add`, `POST /v0/beads/issues:claimNext`, `POST /v0/beads/issues/{id}:casMetadata`. `GET /healthz` remains public by design. Exact tested set, **not a census of every write endpoint**.
2. **Rotation and revocation:** native token-file reload permitted additional token and rejected removed token without restart, under native reload window (sample tested after ~1.3 seconds).
3. **Restart recovery:** absent token file refused new authenticated server startup; restoring token and restarting restored valid-client operations and continued rejecting revoked token.
4. **Competent synthetic path still works:** with valid token, `update(root, expected_version) + dep_add` in the same native batch committed and advanced root revision. A stale competing update was refused.

## Reproduced material counterexamples

1. **Same-UID process:** even with token-file permissions `0600`, an independently launched process with the same Unix effective UID as the Beads server read the shared token and posted `dep_add` through the authenticated HTTP API, **without SQL root password**. The root issue `revision` was the same before/after. Native finding `SAME_UID_SECRET_CANNOT_ISOLATE_PRIVILEGED_HTTP_WRITER`.
2. **Privileged direct CLI:** the same authority context could run native `bd dep add` directly through Dolt outside HTTP authentication; this also did not advance the root revision. A bearer token is **not a causal-writer contract**.
3. **Hot token-file loss:** removing the file while the authenticated server was running left its last-good credential active; the client still received HTTP 200 with that token. Native finding `TOKEN_FILE_LOSS_RUNNING_SERVER_LAST_GOOD`. This matches native source semantics and has security implications for fail-closed policy. A brand-new server started without the file **did** fail closed.
4. **Scope of token:** each token grants all endpoints; it is not a read-only access token and does not authenticate a specific agent/role.

## Control experimental decision

**QUALIFIED FOR BOUNDED NATIVE AUTH TEST:** native bearer auth, route refusal, rotation, recovery after restart and guarded batch were confirmed for the tested service and endpoints.

**NOT QUALIFIED FOR EXCLUSIVE CAUSAL WRITER:** a bearer token accessible to the same UID and a separate direct CLI path both bypass the guarded root contract; the 023 graph-expansion counterexample survives. Claiming secure Product admission would be unsupported.

**Candidate simplest safe direction for next experiment, not adopted:** run the privileged Beads writer and its Dolt credentials under a *distinct OS security principal / isolated process boundary*, allow implementer clients only explicit read-only interfaces, and prevent them from accessing all privileged write endpoints, socket and private store. Where needed, expose the smallest guarded write capability through the existing authorized effect execution route, not a new scheduler/orchestrator/global ledger. Must test direct CLI, same-UID compromise assumptions, network exposure, persisted credential recovery, and accidental policy removal. A stable double-read model (024) remains informational, not a decision authority.

**Important caveat:** Unix UIDs separate ordinary processes; code running with the privileged writer's UID or escalated root is outside a simple user-ACL security boundary. Do not claim a universal guarantee without containment evidence. Consider operational cost versus keeping Beads nonauthoritative.

**Next priority recommended, not started:** experiment 027 to qualify isolated privileged service identity and reduced write exposure, across a supervised service restart and a read-only client; inventory all writable paths. This is an **experimental selection recommendation**, not Product authorization, contract change, acceptance or handoff.

**Effect status:** Product branch and Dolt shared ref remained unchanged; no terminal original historical effects repeated.
