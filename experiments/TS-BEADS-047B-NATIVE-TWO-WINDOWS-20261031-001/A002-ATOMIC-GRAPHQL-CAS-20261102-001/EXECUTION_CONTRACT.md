# TS-BEADS 047B A002 — one-shot external atomic Git GraphQL CAS, experimental grant

## Authority and identity

- Existing responsibility: TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001, EXPERIMENTAL_CONTROL_ONLY. User authorized the next bounded dependencies to obtain optimal experimental results on 2026-11-02. This permits **only** one harmless isolated Git ref mutation for each of ALPHA/BETA after source review, not SQL, Beads, native host state, Kernel, TaskCycle Product, or any provider retry.
- Experimental GitHub repo: mauedgar/ts-execution-lab, target ref `refs/heads/experiment/ts-beads-047b-a002-atomic-cas-target-20261102-001`, initial G0 `566258f2307360137de765e8116c9174912d3c51`.
- ALPHA immutable competing candidate `4f6486b45bfec63a30653b1e5cbc556a82fa9217`; BETA `99bab25a46d13fba92ceb80b2df9c01cddd80e2a`, both unique direct children of G0. Their `CLAIM.json` is synthetically marked `sql=false`, `beads=false`, `product=false`. Proposal objects have been created without modifying the target ref.
- Exact one-shot operation `TS-BEADS-047B-A002-ATOMIC-GRAPHQL-CAS-20261102-001-ATTEMPT-001` with frozen script `Invoke-AtomicRefCas-Fixture.ps1` in this directory. GitHub Actions Windows hosted runner, ephemeral token from `github.token` scoped to repository contents:write only in this workflow, no credential persistence; no operator credentials.
- Preconditions: independently frozen script and workflow, PowerShell parser + IR; target ref SHA exactly G0, both claim commits immutable/direct parent G0, correct repository id. Failure of any precondition => no GraphQL mutation.
- Conditioned ALPHA effect: exactly one GitHub GraphQL `updateRefs(input:{ repositoryId,refUpdates:[{ name: targetRef, beforeOid:G0, afterOid:ALPHA, force:false}] })` call. Terminal accepted response and HEAD exactly ALPHA required before second call.
- BETA incompatible proposal: exactly one `updateRefs` with same `beforeOid:G0` and `afterOid:BETA`. Require typed provider error consistent with rejected stale condition; if transport/response ambiguous, classify UNKNOWN, preserve ref and stop. No retry, branch reset, force or reroute. HEAD must remain ALPHA. Distinguish provider reply from point-in-time HEAD.
- Preserve original job/provider receipt as a GitHub Actions artifact if available and exact run/job logs, join and independently review. No live 047B effect depends on this claim.

## Nonclaims

A one-repository GraphQL CAS test is **not** two independent Windows hosts, not authenticated native actors, not a durable Dolt/Beads writer lease, not PID recovery or original UNKNOWN reconciliation, not offhost backup/restore and not authority Product. Prior old experimental BETA on `experiment/ts-beads-047b-a002-offhost-cas-20261102-001` remains `PROVIDER_UNKNOWN`, its branch still ALPHA `615dafedb94a0fea6430fc966f69ea5ccf02ecf0`; no reuse of refs or retries. Original V6P2 notebook PID lineage 18796→11384→20888→23184 remains ABANDONED_UNRECONCILED_UNKNOWN. Product `mauedgar/tecnotron-ai:tools@bc9e60b9cad79037b40c298d5c9a84f17a33d909`, #34 CLOSED_PASS, #35 H6 separate, Kernel UNDECIDED.

**Stop conditions**: immutable identity mismatch, unauthorized token privilege or provider mutation error, unexpected other ref, lost original receipt, source reviewer FAIL, ambiguous result. Such a result is `BLOCKED` or `UNKNOWN` not an automatic retry.
