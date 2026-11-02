# TS-BEADS 047B — V6P2 EOL and native proof traceability (isolated source-only delta)

**Kind:** experimental documentation repair, **NOT a new TaskCycle, ExecutionAttempt, source candidate, runner or acceptance**.
**Write set:** exactly this new Markdown file on a fresh isolated lab branch. The frozen V6P1 and V6P2 paths, CI attempts, manifest, Python and PowerShell executable bytes remain unchanged. **Product authority/effects: NONE**.

## Immutable identities and provenance

- Reviewed V6P2 `mauedgar/ts-execution-lab@ca8d467a8b8c4490db913bb76b20b59966d14acb`, tree `874b5428e0ec11fcc3a2349a2a89d6d80aa270f0`, candidate folder `OFFLINE-PRIVILEGE-FIXTURE-V6P2-20261102-001`, manifest Git blob `55bf4e57cf6f04fb0e6ef54497de5073e7a1e620`, eight pinned LF file entries; nine total files including manifest.
- Previous V6P1 `@0118028c2508c2ce274fd42240f847adf7ff2187` remains separate. Its IR013 `PASS_SOURCE_LIMITED` does NOT transfer; V6P2's original independent IR014 `PASS_SOURCE_LIMITED`, 0 new source findings, 9 advisories and 4 full-effect blocker families, Git original `mauedgar/ts-execution-transport@172bf41d44ecdafdbc91c108043e2deafeaa4750:results/TS-BEADS-047B-V6P2-WEB_INLINE-IR014-20261102-001/ORIGINAL_REVIEW.md`, raw Git blob `8f700b5215fcce7df782fd4560b604591bc845a9`.
- V6P1 temporary patched COPY native Windows 003: GitHub run `41386952103`, attempt 1 PASS, **not an unpatched V6P1 test PASS**. V6P2 unpatched native Windows 004: GitHub run `41387669028`, attempt 1 success, trigger sha `17381aa13013f7dc70ea07da3e44c9f945bc8beb`, artifact `13115632444`; original terminal evidence `mauedgar/ts-execution-transport@72d7457054a3c4fce72d510181a83e23b6a8d972:results/TS-BEADS-047B-V6P2-WINDOWS-NATIVE-20261102-004/ORIGINAL_TERMINAL_RESULT.md`, blob `67230cd3bdab6121836a666285c0abc2653d6cce`. Source 8/8 and Python 7/7, AST, issuer negative, Win32 scratch ACL. This is hosted Windows **only**.
- Notebook direct Commander attempt **still UNKNOWN**: host `DESKTOP-DJLBEQH`, Windows PID chain `18796→11384→20888→23184`, original `opencode2 run --standalone --agent build` logged under Commander npm package directory instead of `C:\TS\station` at `2026-11-02T13:52:39Z`; run IDs `ba800ff3`/`9ec3e131`, no attributable session/tool/effect/terminal record. Original expected `results/TS-BEADS-047B-V6P2-NOTEBOOK-NOSQL-20261102-001/ORIGINAL_RESULT.json` absent at reconciliation. This negative evidence cannot prove no effects. Read-only Plan recovery Orca terminal `term_2a198a2d-9cdc-492b-9737-f61cc094c4bd`, independent source `mauedgar/ts-execution-transport@bb8ff4bc5255f80d714f9c215531a233f7e2d296:results/TS-BEADS-047B-V6P2-ORCA-RECOVERY-20261102-002/NATIVE_SESSION_JOIN.md`. Never re-label UNKNOWN as FAILED or retry granted.

## IR014 advisories A007–A009 — factual repair of documentation, not edits to original

### A007 — README EOL guidance ambiguity

The frozen V6P2 README states CI **must** pin `core.autocrlf=false` *before checkout*. This is a useful independent control for staging byte-exact pinned sources, **not** a precondition for the separate `.gitattributes` portability proof. Two DISTINCT checks were actually performed in native attempt 004:

1. Challenge Windows checkout with `core.autocrlf=true` and V6P2 local `.gitattributes` `text eol=lf`, confirm `i/lf w/lf` (no CR) despite global autocrlf TRUE.
2. Pin `core.autocrlf=false`, `core.safecrlf=true` and `core.eol=lf` for the **separate byte-exact source checkout**, materialize raw Git index and verify length, SHA-256, Git blob and no CR/BOM for all eight manifest files.

Thus the README's single precondition must not be read as contradicting the observed portability test. This erratum repairs explanatory provenance **outside the immutable V6P2 README**. This does not constitute an independent IR closure or change the original source.

### A008 — workflow step label drift

Native run 004's UI step **"Checkout immutable V6P1 original source"** is a stale label. The original job log proves its actual frozen V6P2 source checkout `ca8d467...`, and separate `TS047B_V6P2_ATTRS=PASS_AUTOCRLF_TRUE_I_LF_W_LF`. **Action deferred to a new workflow revision if one is needed**, not retroactive edit of the run or original receipt. Advisory remains open in the immutable 004 workflow; the mismatch is identified here and must not be mistaken for wrong subject execution.

### A009 — frozen manifest vs later provider receipt

V6P2's frozen `MANIFEST.json` field `nativeHostedWindowsV6P1WithPatchedCopyReceipt=41386952103` correctly points to the **earlier V6P1 temporary-COPY test 003** and cannot contain a later run 004 identifier. The authoritative subsequent proof is 004 as linked above. The manifest must not be retroactively rewritten to suggest its candidate had run 004 at freeze time. This forward traceability entry repairs the missing documentation mapping, not the source.

## Independent development boundary / next action

The experimental branch may carry source-only documentation fixes and independently reviewed hardening. It **must not** run a new local V6P2 source preflight, kill PID 18796 or the original server, use SQL, mutate Beads, start Dolt, configure Tailscale Serve, or change Product. Continue the exact old attempt reconciliation separately; do not turn its ambiguous effect into a global freeze of unrelated source-only work. For any future *new* workflow, re-freeze subject/runner/expected outputs and use qualified Orca-visible terminal **only after** original effect boundaries and conflicting write sets are verified.

**Global verdict remains** `HOST_INDEPENDENCE_INCOMPLETE`; Kernel `UNDECIDED`, migration/removal not granted; #34 `CLOSED_PASS`, #35 H6 independent.
