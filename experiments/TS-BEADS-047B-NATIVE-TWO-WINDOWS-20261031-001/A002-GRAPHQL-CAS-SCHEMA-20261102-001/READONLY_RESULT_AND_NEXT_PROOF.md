# TS-BEADS 047B — GitHub GraphQL atomic ref schema, source-only verified

**Existing responsibility:** TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001; authority EXPERIMENTAL_CONTROL_ONLY; Product NONE; no new TaskCycle. This is a READ-ONLY provider-schema proof, not an approved Git ref claim, issuer, lease, SQL writer gate or new permission.

## Original frozen subject and evidence

- Source `mauedgar/ts-execution-lab@a11fbf2e5073c53da583bb73e95336074dddaf56`, path `experiments/TS-BEADS-047B-NATIVE-TWO-WINDOWS-20261031-001/A002-GRAPHQL-CAS-SCHEMA-20261102-001/Read-Graphql-Cas-Schema.ps1`, Git blob `4818729c575fd5a331918f50812c6d6d1dd16766`.
- Workflow trigger `mauedgar/ts-execution-lab@660061e71847c05c17af75a51fbdd819085b950d`, `windows-2022`, `contents:read`, `actions/checkout@v5` with `persist-credentials:false`, checkout exact frozen source.
- Original GitHub Actions **run `41539483313` attempt 1, completed/success**, job `125599690599`, all native Windows steps successful; https://github.com/mauedgar/ts-execution-lab/actions/runs/41539483313 .
- Original native log: `PASS_A002_GRAPHQL_SCHEMA_READ_ONLY`, `hasUpdateRefs=true`, `refUpdateHasBeforeOid=true`, `refUpdateHasAfterOid=true`, `updateRefInputHasBeforeOid=false`, `mutationExecuted=false`, `refMoved=false`, `sqlExecuted=false`, `beadsMutated=false`. Source queried only GraphQL `__schema` and `__type`; **no GraphQL mutation**. Authenticated ephemeral GitHub Actions token was used only in `GH_TOKEN` with read permissions, no credentials logged.

## Competent interpretation

- Provider **schema** supports documented atomic `updateRefs` with `RefUpdate.beforeOid` and `afterOid`. Official docs: https://docs.github.com/en/graphql/reference/git . REST `PATCH /git/refs/{ref}` `force=false` guarantees fast-forward, not arbitrary `beforeOid` atomic match: https://docs.github.com/en/rest/git/refs .
- Existing ChatGPT connector `mcp__GitHub__update_ref` advertises `expected_sha` but does NOT expose its internal GraphQL/REST binding or the typed original BETA error. **Its CAS atomicity is still unverified.** No generic authenticated raw GraphQL mutation action is exposed in the available GitHub connector. This proof does not change its behavior.
- Original ALPHA Git ref `experiment/ts-beads-047b-a002-offhost-cas-20261102-001` remains `615dafedb94a0fea6430fc966f69ea5ccf02ecf0` at previous readback, whereas original competing BETA `b78eea621102d621190d27c69ab67f80f27b17f8` returned an `UNKNOWN` provider GraphQL error. **Never retry BETA or force/reset the original ref**. IR018 original `EXTERNAL_REF_STORAGE_PASS_CAS_UNPROVEN` in `mauedgar/ts-execution-transport@e855e7bd9e66e67511d83c97bce06e651b9c8892:results/TS-BEADS-047B-A002-EXTERNAL-CAS-IR018-20261102-001/ORIGINAL_REVIEW.md`, blob `fca1e973ee080cbe19bc2ffd988676eb263a04d7`.

## Next *separately authorized* mutating experiment (NOT started here)

1. In a fresh **write-disjoint** experiment and never reusing original G0/ALPHA/BETA identity, freeze two conflicting claim commits from one fresh Git ref G0. Define exact repository owner, token permissions, two actors, run identity, expected head, bounded CAS call, terminal receipt, original provider failure semantics, and fail-closed conditions. The Git source/hosted workflow must be independently reviewed before any mutating dispatch.
2. Use actual `gh api graphql` to invoke the documented `updateRefs` mutation with `RefUpdate.beforeOid=G0`, `afterOid=ALPHA`, `force=false`, with **write-scoped token only under an explicit bounded grant**. Never embed credentials in source/log/arguments beyond the ephemeral host token environment. After original success, request one conflicting BETA attempt with stale `beforeOid=G0` only if safely authorized under its own `ExecutionAttempt`; preserve any `UNKNOWN` instead of blind retry. Distinguish application-level `errors` from transport/provider failures; verify result against exact branch HEAD and immutable original provider receipt.
3. Even if GraphQL CAS rejects the stale reference, this is **only Git ref atomicity**. Fencing for the actual Dolt/Beads writer requires authenticated distinct notebook and desktop actors, monotonic epochs enforced by the storage writer, off-host durability, recovery/backup and externally signed receipt before Product consideration.
4. **Do not start** real SQL, Tailscale proxy, Beads graph, full V6P3R2 launcher/manifest, or original notebook process operation. V6P2 notebook PID `18796→11384→20888→23184` remains `ABANDONED_UNRECONCILED_UNKNOWN`; #34 CLOSED_PASS, #35 H6 independent, Kernel UNDECIDED.

**Current disposition:** `PROVIDER_GRAPHQL_CAS_SCHEMA_READONLY_PASS`, `CONNECTOR_CAS_BINDING_UNVERIFIED`, `BETA_PROVIDER_UNKNOWN`, `HOST_INDEPENDENCE_INCOMPLETE`, `NO_GO_SQL_BEADS_PRODUCT`.
