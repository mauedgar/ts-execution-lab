# TS-BEADS 047B — IR002 advisory follow-up: OS-only read-only source

**Responsibility:** existing `TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001`, experimental, Product effects NONE. **Baseline:** independently reviewed non-effectful candidate `mauedgar/ts-execution-lab@8f484644d9e28f5095a9b3c4cb2c99c18761e6a0`, tree `d2a94e90aa99018715b117fc15b26e7165df0aa2`, `WEB_INLINE_IR002_SECURITY.md` blob `fe9d76346f905ca19e4fc1aee7de035f84418749` at private transport `ad4a24cb34441f2c17a60c80a9c27f5abb9a4c80`. IR002 concluded `GO_SOURCE_LIMITED / NO_GO_EFFECT`, 0 new source findings, 3 residual advisories. This is acceptance **only as an experimental reference baseline**, not effect admission, native qualification or Product decision.

## Bounded changes in this follow-up candidate

- **IR002-A001:** `Inspect` no longer calls `dolt version`, `bd version`, `tailscale status`, `serve` or `funnel` through an arbitrary CLI. It checks immutable known binary SHA256 and Windows OS state using read-only local APIs. Third-party version/status is correctly `UNVERIFIED`. This is an explicit **loss of observation breadth** in exchange for a stronger no-external-executable boundary, not a claim that a complete preflight now exists.
- **IR002-A002:** known TCP listeners, Dolt process, root absence and Windows reparse ancestors remain observational snapshots; the runner explicitly returns `ALTERNATE_SQL_LISTENERS_UNVERIFIED` and `REPARSE_SNAPSHOT_NOT_ATOMIC`. It does not guess that missing known ports means no service. Exact SID, peer, Tailscale Serve/Funnel state and provider receipt must be verified separately before any effect.
- **IR002-A003:** a source-only `ProbePath` fixture mode exercises the **same** `Assert-NoReparseAncestor` function on disposable Windows CI directories, missing directories, relative paths and, when available, an NTFS junction. It returns generic status only; it is **not** native host qualification. A forged host environment cannot unlock `Execute`. No SQL, DPAPI, real credentials, Tailnet changes or Product data.
- **Unchanged:** `-Mode Execute` denies with exit 41 **before** any OS read. No `GrantPath` or caller-supplied hash can elevate it. No original attempt reuse.

## Testing and reviewer boundary

The workflow checks exact `github.sha`, unchanged frozen DoD Git blob `26388665fc0782fd10b24adca96a7dfa47c6a952`, changes scoped to these four preexisting files, PowerShell parser, and Windows behavioral negatives. It is `SOURCE_ONLY`: hosted CI is not the notebook. No future SQL/Tailscale/security state can be declared PASS solely from this CI.

Native read-only notebook qualification should be a **separate, frozen mechanical command**, with exact host/device, binary and source SHA, permitted OS-only observations and compact scrubbed receipt, materialized through GitHub checkout/normal source surfaces (never via Commander payload creation). Commander may invoke only the already-materialized command and observe its one terminal result. If source/materialization identity, read-only guarantee or path cannot be verified, report `BLOCKED_PRECONDITION` instead of probing/retrying. `ProbePath` only tests a path invariant, not notebook state.

Before any new effectful experiment, a distinct grant/provider receipt, exact SID/peer, tested Dolt auth/privilege persistence, ACL/effective permissions, DPAPI recovery/backup, child lifecycle and UNKNOWN reconciliation, independent source/security review are still required. **NO_GO_EFFECT; HOST_INDEPENDENCE_INCOMPLETE.** No assumption of two-host Beads graph or outage/restore proof.

**Product invariant:** `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909` remains unchanged; #34 CLOSED_PASS, #35 independent, Kernel UNDECIDED.
