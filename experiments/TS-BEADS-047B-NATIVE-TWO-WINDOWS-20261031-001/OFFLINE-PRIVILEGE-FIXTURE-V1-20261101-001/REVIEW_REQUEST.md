# TS-BEADS 047B — source candidate for independent security review

**Class:** EXPERIMENTAL_SOURCE_REVIEW_REQUEST, not an Independent Review verdict, not a Developer/Product grant and not an execution receipt.
**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (unchanged); owner notebook `DESKTOP-DJLBEQH`.
**Review subject:** `mauedgar/ts-execution-lab@47cb03ab6b5d8f822e0370508620b89251fac39e:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE-PRIVILEGE-FIXTURE-V1-20261101-001/candidate/Invoke-DisposableDoltPrivilege.ps1`.
**Pinned file blob:** `6dc82e1a32410018ad08c756bfbfd64eca3bf63b`.
**Independently recalculated SHA-256 over fetched UTF-8 source bytes:** `40c5443b941ef59ad1db8dc3c688340016793b07cb3cc3e092cdf21d190bdbb5` (12,667 bytes, reference "abc" SHA-256 test vector matched). Publish and materialize exactly these bytes; Windows Git CRLF conversion will alter this hash and MUST block an effect rather than be accepted silently.

## Predecessor / rationale

- Transport `main@f74ac6f4d263d7b8ccd458e12e14aa6d31083c09` handoff `TS-BEADS-047B-OPERATIONAL-ROTATION-IR006-20261101-001`.
- Previous frozen static runner at lab `6019d22f1175899525a3607a7807880fb10f4c1e` remains terminal and unchanged; its `IR006_PASS_LIMITED_FAIL_CLOSED_STATIC / NO_GO_DISPOSABLE_SQL_EFFECT` stands.
- Experimental qualification `DISPOSABLE_DOLT_2_2_0_QUALIFICATION_20261101.md`, Git blob `5e7dc259fb1c682b1b336917f0b489f1e49292c1`.
- Dolt upstream source `dolthub/dolt@v2.2.0:go/cmd/dolt/commands/sql.go`, blob `4a1101d562ed5cf00b70bd271b9ef07e081a1608`; official privilege and CLI docs at https://www.dolthub.com/docs/sql-reference/server/access-management/ and https://www.dolthub.com/docs/cli-reference/cli/.
- Product SOT `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`; `State_Kernel.final_disposition=UNDECIDED`. #34 CLOSED_PASS; #35 H6 separate; no Product effects.

## Narrow positive path in source (NOT empirically run)

1. Read-only host/port/ACL/Tailscale observations and pinned Dolt 2.2.0 executable SHA-256; refuse any prior fixture or same-attempt receipt.
2. Require exact source hash and an explicitly scoped one-time grant file plus independent Control-side verification; untrusted JSON text or caller-provided hash is **not** competent authority by itself.
3. Claim an exclusive original local receipt before first SQL spawn, then create an isolated owner-only data/config root.
4. Pass one synthetic SQL account creation and minimal SELECT grant over stdin, not argv; persist and hash `privileges.db`; start a *second* CLI process from the same isolated data/config/privilege paths and perform structured query readback of `mysql.db`. Report `PASS_OFFLINE_PERSISTENCE_ONLY` only if exact fields and hash match. Every spawned PID/exit is written in append-only receipt; an unresolved PID must not be retried, killed or cleaned automatically.
5. Never start SQL server, Tailscale Serve, Funnel, native Beads clients, backups, Attendance, or Product changes.

## Required reviewer questions and known issues to challenge

- **Critical authorization boundary:** `Check-Grant` validates fields/hash only. A malicious caller can forge both a file and a matching SHA256. It is NOT a complete authorization verifier. Independent review MUST reject any effect until a separate *already materialized*, immutable launcher validates **actual issuer, signed/competent grant origin, Git blob/commit, exact attempt/host/owner and prior effects**, and this source is bound to that launcher. External launcher must neither create/modify the grant nor default to SQL.
- **Critical subprocess/receipt:** `ReadToEndAsync` currently bounds result length only **after** subprocess exit; this is not a memory bound on live stdout/stderr. `WriteAsync` can also be delayed. Decide whether the reviewed bounded-input fixture plus exact original process receipt is adequate or require streaming output caps and independent watchdog/receipt contract. Timeout keeps PID as UNKNOWN; never automatically kill or retry.
- **Critical safety observations:** verify whether `tailscale serve status --json` schema and exit states are truly handled safely on the pinned Windows Tailscale; unknown keys / empty output must NOT be interpreted as absence of exposure. Query all port-3307 listeners, validate all reparse ancestors and inherited ACL conditions, test OS-specific `DirectorySecurity` / `Set-Acl` behavior. Absent or ambiguous native observation must fail closed.
- **Critical SQL semantics:** confirm pinned Dolt 2.2.0 understands global flags before `sql`, multi-statement stdin, `--result-format json`, first-run creation of `ts047b_fixture`, `mysql.db` field schema and second-process readback. A permitted local superuser is NOT an authenticated reader; no remote denial/security claim from this experiment.
- **Execution isolation:** verify SQL never receives password in argv, logs, portable receipt, or final output; no concurrent writer, accidental instance redirect, default storage path, Product directory, public SQL listener or implicit fallback.
- **Original attempt:** prove previously attempted 047B effects/receipt states from original durable sources before a new effect; missing local receipt alone does NOT mean no earlier effect. Ensure unique `ExecutionAttempt` and owner, exact source, destination and lock preconditions.
- **Testing:** no native PowerShell parser, Windows ACL tests, empirical Dolt SQL, original process receipt, or positive privilege lifecycle tests have been executed for this new candidate. Require parser/static negative tests and independent qualified Windows review before any grant. Do not issue IR PASS solely from mock tests.

## Decision boundary

**Current candidate disposition:** `SOURCE_PUBLISHED / IR_NOT_PERFORMED / NOT_DISPATCHABLE / NO_SQL_EFFECT`.
If review finds blockers, publish a distinct corrected immutable candidate + IR; do not patch frozen history or repeat old attempts. If secure native privilege persistence cannot be safely proved, `TECHNICAL_NO_GO_OFFLINE_PRIVILEGE_PERSISTENCE` is a valid result.

**No SQL grant is present.** Separate explicit conditioned experimental grant is needed **after** an independently reviewed source+launcher and host/native precondition validation. No automatic Product/Kernel adoption even if the offline fixture later passes.
