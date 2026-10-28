# TS — Beads 027 | Dictamen de Control experimental: identidad aislada y reinicio seguro

**ID:** `TS-BEADS-027-ISOLATED-WRITER-20261028-001`  
**Fecha:** 2026-10-28, Argentina.  
**Estado terminal experimental:** `COMPLETE_WITH_CONFIGURATION_ENFORCEMENT_GAP`.  
**Calificación técnica original:** `PASS_SEPARATE_UID_WRITER_WITH_NATIVE_AUTH_CONFIGURATION_GAP`, **28/28 checks PASS**.  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`; **NO Product adoption, NO Product authority, NO TaskCycle, Developer grant, Phase 2 ni Independent Review Product**.

## Reobservación de fuente y sujetos competentes

- `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`; SOT `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`; current-state blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`. Read-only throughout.
- Experimental lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`, branch `experiment/beads-027-isolated-writer-service-20261028-001`.
- Shared Dolt remote `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571`, unchanged in postflight, zero shared remote writes.
- 026 predecessor Control verdict `mauedgar/ts-execution-lab@a01cf0d48698f4670facef9e899436c0c0e2b299:experiments/TS-BEADS-026-NATIVE-AUTH-20261026-001/CONTROL_EXPERIMENTAL_VERDICT.md`; original same-UID bypass and native bearer semantics preserved, NOT reexecuted.
- Test uses pinned native Beads v1.3.1, Dolt v2.2.0, `native027.py`, `reader027.py` and original design `PLAN.md`, all in disposable Ubuntu GitHub runner. No additional daemon/orchestrator beyond the two native vendor services.

## Six bounded attempts: terminal history preserved

| Attempt | Exact GitHub Actions run | Source SHA | Observed terminal |
| --- | --- | --- | --- |
| 1 | [40735994928](https://github.com/mauedgar/ts-execution-lab/actions/runs/40735994928) | `3590d8e396fc59b4c033e25ea6facf0533ecdfaa` | **FAIL**: Python syntax in test shell expression before native execution |
| 2 | [40736184886](https://github.com/mauedgar/ts-execution-lab/actions/runs/40736184886) | `dd9e28888c40e1a9c5b0b0a4ef57df31a81ae869` | **FAIL**: fixture tried `stat` of secret as runner, permission denied after successful ownership isolation |
| 3 | [40736440921](https://github.com/mauedgar/ts-execution-lab/actions/runs/40736440921) | `7154dc11edc73ba1b6a4dc0bc6873bd2c3e47883` | **FAIL**: Dolt server terminated before native tests |
| 4 | [40736670773](https://github.com/mauedgar/ts-execution-lab/actions/runs/40736670773) | `e688748435117f2736a9b33d6254f2b16daa8cd5` | **FAIL**: Dolt server terminated despite accessible `/tmp` fixtures |
| 5 | [40736882302](https://github.com/mauedgar/ts-execution-lab/actions/runs/40736882302) | `12ff174332388760651bb0929f5cb318968ed448` | **FAIL**, exact native log: `Failed to load the HOME directory: stat /home/ts027w: no such file or directory` |
| 6 | [40737074572](https://github.com/mauedgar/ts-execution-lab/actions/runs/40737074572), job `122988392478` | `41e3205d0bda0800de4f52676f2da7d099e1ef92` | **SUCCESS / 28/28 PASS**, fixed private HOME for native Dolt writer, full scoped tests and qualified TXT publication |

There were **no retries of historical external/Product effects**. Every attempt has an immutable Git/Actions identity; the first five were mechanical harness failures, never authorization or safety PASS.

## Exact original receipt and TXT carrier

- GitHub Actions run `40737074572`, source `41e3205d0bda0800de4f52676f2da7d099e1ef92`, execution terminal success.
- Published original `IR-TXT-CARRIER/1` envelope: `mauedgar/ts-execution-lab@2a15ca93ea4ae21fb89cc2d4719558db9bdd4d67:transport/TS-BEADS-027-ISOLATED-WRITER-20261028-001/EVIDENCE_CARRIER.txt`, Git blob `b6b04598210ab4f807e49fbb9399985fb12a412b`, original runner SHA-256 `b9e9e34bc5d26e40945596be7e007950a0710136ee6dc2a3d68b82b966051448`, 7,694 bytes.
- Exact members: `README.txt`, `control/PLAN.md`, `original/RESULT027.json`; original JSON SHA-256 `79075d6855028720b783f22d90144dcb5aca5963a7fc89dca147a7c495b8c81e`.
- Generated, verified, extracted, and bytewise readback **PASS** with existing Product tool `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`. No ZIP as the consumer carrier. Transport copy is **not** asserted; the immutable lab Git ref is the qualified evidence.
- All 28 individual check names and two compact observation objects are preserved in the JSON original inside the TXT; the dictamen does not replace the receipt.

## Native observations

### Effective boundary, inside the tested local threat model

- Two distinct Unix identities `ts027w` privileged writer and `ts027r` read-only implementer; writer's native Git, Dolt context, SQL root credentials, executable wrapper and bearer file owned by writer under a private `0700` directory and `0600` credential. The reader could not read the writer's files or native Beads storage.
- Separate reader successfully queried 3 native issue rows through SQL `SELECT` privileges, and its attempt at SQL UPDATE was **refused**.
- Reader calls without token to five native endpoints—`GET /v0/beads/issues/{id}`, `GET /v0/beads/context`, `POST /v0/beads/issues:batchApply`, `POST /v0/beads/dependencies:add`, `POST /v0/beads/issues:claimNext`—returned **401**. This is tested route coverage, **not all writable routes**.
- Competent writer executed `update(root, expected_version) + dep_add` natively in one transaction: root revision advanced and the new edge persisted; a stale competing update was rejected.
- Service restart with `--auth-token-file` kept reader denied and privileged read functional. Starting service with missing token file and `--auth-token-file` was refused. Restoring the file and restarting restored the protected behavior.

### Material deployment configuration bypass

- A deliberately insecure loopback restart **without** `--auth-token-file` allowed the read-only process to POST `dep_add` successfully through the privileged HTTP service, despite Unix/SQL separation.
- The newly inserted edge persisted; root revision did **not** advance. The original 023 causal-graph bypass therefore remains possible when secure deployment configuration is omitted.
- The insecure test server was stopped; the final restart restored bearer authentication and reader requests returned 401.
- **Classification:** `AUTH_POSTURE_NOT_ENFORCED_ON_NATIVE_LOOPBACK_START`. OS/SQL credential separation is necessary within the experiment but not sufficient to guarantee causal exclusivity across recovery/config drift.

## Control experimental decision

1. **QUALIFY bounded principle separation**: distinct Unix service identity, private credentials, SQL SELECT-only implementer and native bearer authentication can protect the tested writer API and preserve a competent guarded transaction across authenticated restart.
2. **RETAIN material blocker** for general authoritative work graph: native Beads can still start unauthenticated on loopback unless the deployment ensures fail-closed launch posture; privileged writer identity may itself use native CLI to bypass `root revision + dep_add` discipline, as established previously. Nor does 027 prove exhaustive writable endpoint coverage, root/sudo containment, multihost isolation or deployed service supervision.
3. **DO NOT declare Product adoption** or change any Tecnotron state, SOT, TaskCycle lifecycle, developer authorization or Phase 2.
4. **Next bounded research recommendation, not initiated:** qualify minimal **fail-closed startup configuration enforcement** and a complete writer-path inventory using the same native tools and OS service constraints. Compare the operational burden of this isolation model against retaining Beads solely as nonauthoritative state/projection before any proposed Product lifecycle refactor. Avoid introducing a new scheduler/daemon/orchestrator/global ledger by default.

**Terminal disposition:** `027 COMPLETE_WITH_CONFIGURATION_ENFORCEMENT_GAP`, all original native results preserved. Product branch and shared Dolt remain unchanged.
