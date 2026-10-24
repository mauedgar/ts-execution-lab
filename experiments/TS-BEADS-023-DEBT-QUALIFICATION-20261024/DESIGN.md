# TS Beads 023 — independent debt qualification and deferred GitHub provider join

**Classification:** NONPRODUCT_EXPERIMENTAL / no Product authority / no TaskCycle initiation / no Developer grant.

## Original competent anchors

- Product: mauedgar/tecnotron-ai:tools@7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56; tree 8caa56d36f3efeba359bbbf65b158ffb01a19da6.
- SOT docs/SOURCE_OF_TRUTH.md blob dd8d34a7e3ef3094805d014f9e59741d2c553957; docs/current-state.md blob 0d8a6426f51020d51d74bfb50dc8702a07f02837.
- Lab base mauedgar/ts-execution-lab:main@b30241201d07a9590e1e845abe767cdcf9921479.
- Prior bounded Beads 022: mauedgar/ts-execution-lab@32f86383c979ba015024d0e70ccd98c61858e132:experiments/TS-BEADS-OBLIGATION-AUTHORITY-EFFICIENCY-20261024-022/RESULT.md.
- Beads shared refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571 unaffected; all writes only lab Git experimental branch and per-run disposable native stores plus experimental GitHub Actions artifacts.

## Independent authorized operations

### Source-native authority, real original Product implementation

Exact new source: experiments/TS-BEADS-023-DEBT-QUALIFICATION-20261024/source-native-authority.mjs and fixtures023.mjs, executed in detached Product clone on Ubuntu (supported native fsync). Creates an original FilesystemStateStore in the runner temp, calls real `create`, `transition`, and `satisfy` five times on a synthetic ACTIVE TaskCycle to arrive at an actual valid all-obligations-SATISFIED state with reviewer/developer/effect authority refs attached. Invokes **original unmodified** `createReconcileAndCloseTaskCycleRecipe`. A new, synthetically verified Developer REJECTED observation yields `preflight READY`, without actual execute or close.

Limits: native state reachability now verified; later contradictory external evidence's provenance/legitimacy is not established by this test. A competent Product authority review must decide whether to constrain admission, change semantics, or update negative tests. No historical case is asserted.

### Beads-native causal edge discovery

Exact new source: experiments/TS-BEADS-023-DEBT-QUALIFICATION-20261024/native-graph023.mjs. Creates root, related gate, transitive ancestor, unrelated issue and late new dependency using Beads native `bd dep add --type related`, and evaluates dependencies returned by **native GET**. Must distinguish fixed discovered read-set CAS success/failure from **mutation of the graph itself after discovery**. A row-token-only batch might miss the new edge. If so, preserve the counterexample as a material open design gap; do **not** add a global ledger by default, accept unsafe effects, or claim migration readiness. All data disposable.

### Actual external provider one-shot publication with lost consumer ACK

Exact workflow original: `.github/workflows/ts-beads-023-authority-provider.yml`, run [40104370902](https://github.com/mauedgar/ts-execution-lab/actions/runs/40104370902), source HEAD f34df4c706c92e66a850a50a6f55d2315400736f. One immutable experimental GitHub artifact was uploaded exactly once: provider artifact ID 12564166868, name `ts-beads-023-external-provider-40104370902`, ZIP SHA-256 `8331b34121a1a2dcb3df9b08d3bd00cf9cf851abf79590024a0292e9d2f5bd3a`.

The workflow intentionally withholds upload-artifact result/ACK from consumer. After run terminal, ChatGPT performed deferred durable join against **the actual independent GitHub provider artifact**, downloaded the exact ZIP, verified ZIP SHA and original payload SHA256 `14bd7b15c34957c4cd851be1fcef01d7e0bf654a45469741308e36d3360822b5`, then parsed JSON:
- schema_version: `ts-beads-023-github-artifact-effect/v1`
- attempt_id: `TS-BEADS-023-ORIGINAL-GITHUB-ARTIFACT-40104370902`
- source_git_subject: `f34df4c706c92e66a850a50a6f55d2315400736f`
- provider `GITHUB_ACTIONS_ARTIFACT`, status `PUBLISHED_ONCE`, Product effect `NONE`.

**Proven:** source native remote provider effect happened and reconciled with the exact attempt without blind retry or reading original ACK. Not proven: an actual network timeout/ACK loss, GitHub issue/PR mutations, original Code Product external effect. This is a deliberately simulated lost consumer ACK around a genuine external artifact provider publication.

The original Linux authority receipt ID 12564401090 (`ts-beads-023-source-native-authority-receipt`), ZIP SHA256 `62e93e9289d5c6037e1bab0c180e39fe04ac169c3c090aabd6df25f8959e1ae9`, JSON SHA256 `4a15b5b3651349cf8da0ea63a723095fcc8dc91fcacef771e88f37e5b91c8e9a`, **9/9 PASS** and untouched Product.

## Boundaries and disposition

Source-native authority reachability is a strong **finding for competent Product review**, not a default permission to close on REJECTED. Genuine remote artifact effect was reconciled exactly, not a license to rerun original actions or synthesize success from missing data. Native causal graph experiments are distinct and their exact terminal result must be attached to RESULT.md once independently verified.

No product migration, no State Kernel removal, no second mutable ledger, no hidden new scheduler/gates/roles, and no grant/acceptance for any TaskCycle or issue #34. Research may propose structural replacement of prior canonical dependencies after final evidence, not activate it.
