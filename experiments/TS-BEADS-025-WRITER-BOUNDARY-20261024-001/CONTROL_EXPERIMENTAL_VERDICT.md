# TS — Beads 025 | Control experimental: frontera efectiva de escritura causal

**Estado terminal experimental:** `COMPLETE_WITH_MATERIAL_LIMITATIONS`.  
**Calificación de prueba:** `PASS_EFFECTIVE_UID_BOUNDARY_WITH_MATERIAL_SAME_UID_LIMITATIONS`.  
**Autoridad:** `EXPERIMENTAL_CONTROL_ONLY`; **Tecnotron Product authority NONE**, Independent Review Product **NOT PERFORMED**.  
**Fecha de corte:** 2026-10-24.

## 1. Sujetos reobservados, fuentes y resultados originales

- Product read-only `mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56`, tree `8caa56d36f3efeba359bbbf65b158ffb01a19da6`, SOT `docs/SOURCE_OF_TRUTH.md` blob `dd8d34a7e3ef3094805d014f9e59741d2c553957`, `docs/current-state.md` blob `0d8a6426f51020d51d74bfb50dc8702a07f02837`.
- Lab base `mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479`; rama aislada `experiment/beads-025-writer-boundary-20261024-001`.
- Shared Dolt `refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571` unchanged; native Beads v1.3.1 and Dolt v2.2.0 in disposable Ubuntu runner. No real Product TaskCycles, no Product writes.
- Parent experimental Control verdict `mauedgar/ts-execution-lab@4a2511e1fa02858b765715ac76e7d19a32aa67da:experiments/TS-BEADS-024-GRAPH-READ-MODEL-20261024-001/CONTROL_EXPERIMENTAL_VERDICT.md`; material graph bypass originated 023 and is preserved.
- Exact bounded script `experiments/TS-BEADS-025-WRITER-BOUNDARY-20261024-001/native025.py`; selection `PLAN.md`; TXT project/verify/extract `materialize025.py`.

**Executed terminal GitHub Actions:** [run 40118772611](https://github.com/mauedgar/ts-execution-lab/actions/runs/40118772611), job `120945561004`, source Git commit `fc1eec6d763f1de5b405531eb3041a018c80d1da`, workflow `completed/success`, **26/26 original native PASS**. Git commit containing its published receipt `01163e79e535da950c7a69eca297c1f77a5a46c6`.

**Portable envelope original:** `mauedgar/ts-execution-lab@01163e79e535da950c7a69eca297c1f77a5a46c6:transport/TS-BEADS-025-WRITER-BOUNDARY-20261024-001/EVIDENCE_CARRIER.txt`; Git blob `f1c8f113a2c6587961a6bacc31cc788f36f17407`, SHA-256 `195cdf5c2f81070e6d37f1d700d8eb181d43e0971af7a10cb5cd8b14e6d7259c`, **9750 bytes** in original runner. Format reused `IR-TXT-CARRIER/1`, 3 members: `README.txt`, `control/PLAN.md`, `original/RESULT025.json`, member result SHA256 `b89560dd04308e0c1f28464e90511d06c89d4eab058c0916c16bd9c802cbb060`. Qualified Product exporter `scripts/review_txt_carrier.py` blob `96971cf4a39a6bcb64e8b1982010b6d50a1f7ca4`: project, verify, extract and exact readback **PASS**, no ZIP used as consumer carrier.

## 2. Original attempt chronology; no blind retry

| Attempt | Original run / source | Terminal and disposition |
| --- | --- | --- |
| 1 | [40111367108](https://github.com/mauedgar/ts-execution-lab/actions/runs/40111367108), `c6ee2195ca200a088d214bc59ac774583df604d2` | **FAIL**, PyMySQL fixture `CREATE USER '@%'` percent formatting error; did not reach HTTP attack |
| 2 | [40111472323](https://github.com/mauedgar/ts-execution-lab/actions/runs/40111472323), `af3df25b57284e5df714b960784f8ac58e86c9b0` | **FAIL**, invalid YAML step title containing unquoted `:`; no jobs started |
| 3 | [40118636793](https://github.com/mauedgar/ts-execution-lab/actions/runs/40118636793), `134ee03322552b36c1792ecaefffee2b69eaca4b` | **FAIL**, untrusted UID could not read harness source in Actions workspace; test stopped before reaching adversarial HTTP condition |
| 4 | [40118772611](https://github.com/mauedgar/ts-execution-lab/actions/runs/40118772611), `fc1eec6d763f1de5b405531eb3041a018c80d1da` | **SUCCESS / 26 PASS**, attacker helper and PyMySQL-only package staged readably in ephemeral `/tmp` without sharing private Dolt workspace or root SQL credentials |

Every attempt has a distinct Git subject and GitHub Actions run. Fixtures were repaired by measured error and original outcomes preserved. No Product/provider original effect was replayed.

## 3. The observed safety-critical negative

A synthetic Beads native store was created in a private `0700` directory, with root SQL authenticated and a separate `ts025_readonly` user holding **SELECT** only. An untrusted process under OS UID `nobody`:
- **Could read** five synthetic Beads issues via the read-only SQL credential;
- **Could not UPDATE** the SQL issues table and **could not read** the protected Beads metadata directory;
- **Nevertheless could POST a native `dep_add`** to the Beads HTTP API reachable at `127.0.0.1`, resulting in a new dependency on the real native graph;
- The issue root's native `revision` stayed **identical before and after** the unauthorized dependency mutation (`7638680676507712774`).

**Finding: `SQL_ACL_AND_FILE_ACL_ALONE_INSUFFICIENT`.** A protected Dolt database does not protect the causal graph if an independently privileged Beads API writer can be called by a nonprivileged process. Reproduces the general nature of 023's bypass, now from a separate OS identity.

## 4. Qualified conditional mitigation

The test then installed an **ephemeral local Linux iptables OUTPUT rule**, using the OS `owner --uid-owner nobody` matcher to reject calls from that UID to the native write HTTP port. Native evidence shows:
- `nobody` could **no longer reach** the Beads write HTTP API and could **not add** the forbidden edge;
- Its read-only Dolt SQL connection remained usable and SQL writes continued to be denied;
- The privileged writer executed `update(root, expected_version) + dep_add` in **one native atomic `batchApply`**, creating the allowed edge and **advancing root revision**;
- A second writer using the previous revision was **rejected** by CAS.
- The rule was removed and services terminated in the test's cleanup. No shared/store remote persisted from the runner.

**Finding: `CONDITIONAL_EFFECTIVE_BOUNDARY`.** This is a real OS-isolated *separate-UID* example, not proof of general Beads authorization. Native receipt explicitly reports `bypass_under_same_UID: NOT_PREVENTED_BY_OWNER_POLICY`.

## 5. Limitations and product-adoption disposition

**Not qualified by 025:** code running under the **same UID as the privileged writer**; root/sudo escalation; credentials exposed to another execution actor; separately exposed native Beads write endpoints; bypass through direct filesystem access under the privileged identity; other ports/protocols/hosts; remote multiwriter replication; general rule persistence/recovery; full Product lifecycle, source-native TaskCycle equivalence, or actual Developer acceptance / IR. No Product acceptance was attempted.

**Experimental Control decision:**
1. **QUALIFY** the OS/SQL separation and native guarded writer under the *specific tested UID/endpoint scenario*; it is evidence that a practical enforcement route exists using existing primitives, **without adding a global mutable ledger**.
2. **DO NOT QUALIFY GENERAL EXCLUSIVE CAUSAL WRITER**. The same-UID and alternate-endpoint bypasses are neither enforced nor disproven. The 023 material blocker therefore remains for **authoritative Product graph effects**, though read-only experimental work can continue independently.
3. **DO NOT adopt** or change Product State Kernel, Upper LC, TaskCycles or Developer grants; the delegated Control role is limited to experiments.
4. **Prioritize next research** (not initiated): qualify a narrowly scoped separate-process execution boundary with actual credentials isolated from implementer processes, including direct same-UID attempt, exposure of all writable endpoints and failure/recovery of the temporary network policy, and compare deployment complexity against simpler nonauthoritative Beads use.
5. **Evidence output:** retain a durable TXT as the primary carrier on exact Git ref. Its existence is evidence publication, not Product consumption or acceptance.

**Status:** `COMPLETE_WITH_MATERIAL_LIMITATIONS`, Product and shared Dolt unchanged.
