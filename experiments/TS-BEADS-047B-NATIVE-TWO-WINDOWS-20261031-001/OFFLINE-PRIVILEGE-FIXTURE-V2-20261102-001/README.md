# TS-BEADS 047B — offline privilege fixture V2 (source-only)

**Operation:** `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001` (unchanged). **Scope:** `EXPERIMENTAL_CONTROL_ONLY`; NO Product, #35, Kernel, Beads, Tailscale Serve/Funnel, SQL server, or original 047B retry. **State:** `SOURCE_CANDIDATE_V2 / NOT_DISPATCHABLE / NO_SQL_EFFECT / IR008_PENDING`.

## Provenance

- Source lab baseline before V2: `f3cca8b455e4ca3b23cfd0d551ed1615bc9231bf`; Product `tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`; Transport `main@8d818e6e76281d211992d5830e6a06b7ff05a0cd`.
- Original V1 remains frozen: lab `47cb03ab6b5d8f822e0370508620b89251fac39e`, Git blob `6dc82e1a32410018ad08c756bfbfd64eca3bf63b`.
- Independent IR007 FAIL: Transport `8d818e6e76281d211992d5830e6a06b7ff05a0cd`, blob `4b7883df0e53a926e68e4663b6a12a39257eeb6a`. Seven BLOCKER and three ADVISORY findings are NOT retroactively closed.
- 047B DoD: lab `e02c611dec74ce5d2ddcd5c169f407543ef2e3c4`, blob `26388665fc0782fd10b24adca96a7dfa47c6a952`.
- Dolt v2.2.0 source `go/cmd/dolt/commands/sql.go`, Git blob `4a1101d562ed5cf00b70bd271b9ef07e081a1608`. Native Windows behavior remains UNTESTED.

## Source files and execution design

`candidate/Security-047B-V2.psm1`: fixed operation/host/attempt, signed grant AND separately signed original-attempt reconciliation, SHA-256 pin of a competent issuer RSA public key, RSA-PSS/SHA256 verification, strict scope/expiry/source hash/nonce/claim fields, Windows-known LocalAppData, protected ACL at CreateDirectoryW time, reparse checks, and conservative port/Tailscale empty-config observations. The trusted issuer key is intentionally **NOT provisioned** (64 zero hex): every effect fails before SQL. Caller-provided JSON or SHA cannot provision the key.

`candidate/Start-047B-V2.ps1`: no-effect preflight or effect entrypoint; verifies runner Git blob and module SHA-256. Does not create or sign grants.

`candidate/Invoke-047B-V2-Fixture.ps1`: independently rechecks signed authority even if invoked directly; fixed one-attempt local CreateNew receipt, flushed intent/PID/exit events, atomically protected synthetic root/data/cfg, pinned Dolt binary hash, no network listener, bounded stdout/stderr (16 KiB each) and total stdin+exit deadline (15 s) per child, no automatic kill/retry. A real but **unexecuted** native SQL plan creates a synthetic database, reader and SELECT grant through stdin, reopens from separate processes, checks `mysql.user` and `mysql.db`, and compares privilege-file hashes. Child SQL and stderr are never serialized. A post-spawn failure is conservatively `UNKNOWN_EFFECT`, not permission to retry.

`tests/test_source_contract.py`: deterministic source-only assertions. `tests/Test-V2-Negative.ps1`: Windows read-only unsigned-grant rejection. `tests/Test-V2-ParserOnly.ps1`: PowerShell parser gate without executing scripts.

## IR007 finding disposition — IMPLEMENTER claims, not independent verdict

| Finding | V2 source change | Remaining acceptance gate |
| --- | --- | --- |
| F001 BLOCKER | RSA-PSS signed grant, pinned-key check, runner self-verification | **BLOCKED:** no competent signer public key, no real signed grant; source revision + independent IR required to provision pin |
| F002 BLOCKER | Fixed attempt, signed original-effect reconciliation, signed exclusive claim attestation, CreateNew local receipt | **BLOCKED:** authoritative original receipts and off-host exclusive registry claim not independently verified; attestation alone is insufficient |
| F003 BLOCKER | Bounded asynchronous stream pumps and total 15-second deadline covering stdin/output/exit | Native PowerShell/.NET deadlock and timeout negative tests NOT RUN |
| F004 BLOCKER | OS-known LocalAppData, atomic CreateDirectoryW+protected SDDL, ACL/reparse checks | Native Windows ACL, inherited privilege-file ACL, ancestor race/TOCTOU tests NOT RUN |
| F005 BLOCKER | Port 3307 all-listener refusal and fail-closed exact empty Serve/Funnel JSON | Exact Tailscale CLI/version/schema on notebook NOT VERIFIED; safe false negatives expected |
| F006 BLOCKER | Durable local CreateNew receipt, flushed intent, PID/start/exit and conservative UNKNOWN | No off-host tamper-evident receipt transport or original provider PID join; NOT CLOSED |
| F007 BLOCKER | Separate native process stages, `mysql.user` + `mysql.db` and privilege hash | No native SQL allowed/tested; first-run grammar and readback NOT VERIFIED |
| F008 ADVISORY | Password from cryptographic RNG; stdin only; never public stderr/SQL; clears byte buffer | Managed password string and native stderr can retain secrets in process memory; native negative-path validation pending |
| F009 ADVISORY | Signed grant carries executable path, pinned executable hash, parser-only script | Native WinGet path/PowerShell parser/Windows ACL behavior NOT RUN |
| F010 ADVISORY | Fixed LF UTF-8 hashes/blob, conservative BLOCKED/PARTIAL/UNKNOWN taxonomy | No confirmed-exit post-spawn terminal taxonomy; no runtime materialization test |

**Do not claim ten findings closed or zero advisories.** The V2 source is a substantial implementation repair, but **`TECHNICAL_NO_GO_UNPROVISIONED_COMPETENT_ISSUER_AND_ORIGINAL_EFFECT_FENCE`** remains the correct effect disposition. Source review may still find new defects. No native SQL was executed in preparing this V2.

## Preparation / review procedure (no execution grant)

1. Fetch the exact final V2 commit and verify every candidate/test file against `MANIFEST.json` SHA-256, Git blob and byte length. Use UTF-8 LF, never CRLF-transformed files. A mismatch is BLOCKED.
2. Review only the exact frozen commit; do not substitute the moving branch HEAD. Run `python -m unittest discover -s tests -p 'test_source_contract.py' -v` in the V2 directory as an optional static check (no host effects).
3. On the actual authorized Windows host, only after a separate **read-only** parser-test authorization, execute `pwsh.exe -NoLogo -NoProfile -NonInteractive -File tests/Test-V2-ParserOnly.ps1` and `tests/Test-V2-Negative.ps1`. Preserve original receipts; do not use Commander for source discovery or payload materialization.
4. Independent WEB_INLINE IR008 must assess authorization trust, original receipt fencing, native compatibility and security. A source PASS cannot authorize SQL. **No effect invocation should be attempted for V2** because the signer key is deliberately unprovisioned.
5. Only a future reviewed immutable candidate with a genuine competent signer pin, verified exclusive off-host claim, exact original attempts and a separate explicit one-time SQL grant could become dispatchable. Do not mutate V2 to insert a key or forge a grant.
6. Even a future `PASS_OFFLINE_PERSISTENCE_ONLY` is NOT authenticated remote denial, Beads host independence, backup/restore, or Product/Kernel adoption.

## Proposed independent IR008 prompt

> Actuá como revisor WEB_INLINE independiente (NO implementador). Revisá exclusivamente `mauedgar/ts-execution-lab@<FINAL_V2_COMMIT>:experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/OFFLINE-PRIVILEGE-FIXTURE-V2-20261102-001/` con MANIFEST SHA/blob y el IR007 original `mauedgar/ts-execution-transport@8d818e6e76281d211992d5830e6a06b7ff05a0cd`. Auditá cada F001-F010, seguridad de RSA-PSS y trust anchor no provisionado, firma y claim, original UNKNOWN, proceso y streams, ACL atómico, reparse, Tailscale, Dolt 2.2.0 Windows y persistencia. Emití PASS/PASS_LIMITED/FAIL con hallazgos nuevos y advisories; distinguí source-only de autorización SQL. No SQL, Commander, Beads, Tailscale Serve, Product ni aceptación automática. Publicá informe inmutable en Transport si hay autoridad; nunca confundas test estático con prueba nativa.

## Invariants

No change to V1, IR007, #34 CLOSED_PASS, #35 H6, `State_Kernel.final_disposition=UNDECIDED`, Product SOT, original host receipts, or original attempted effects. No auto retry, cleanup, alternate writer, remote fallback, or external SQL listener.
