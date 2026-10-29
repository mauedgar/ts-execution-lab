# TS Beads 033 — provider-native effect identity (B-first)

Authority: EXPERIMENTAL_CONTROL_ONLY. No Product or shared Dolt writes.
Product frozen: mauedgar/tecnotron-ai:tools@d4154bd43f26515c39a41be974e462a0c7406a2d; tree cbfb71ad8632047e8e64fe2665d8614d835a2c8b.
Shared Dolt frozen: refs/dolt/data@1f72d68797114170a97fee27641858f2e55a4571.
Predecessor 032 terminal: 09d60b117aecd08744da3747e98e16e7ad2381c3. Never replay 031 or 032.

Objective: use a genuine GitHub Actions provider run and an uploaded native provider artifact as a disposable external effect. Reconcile exactly by run, source commit, workflow, attempt and immutable request hash. Separate the fact of a real provider effect from a simulated client ACK loss. Do not present a simulated network fault as a real lost ACK.

A single push-triggered workflow runs once on this branch. It writes only a provider-native Actions artifact (not a repository commit, TaskCycle or Beads shared-Dolt object). A separate observer uses GitHub provider-native run, jobs and artifact metadata to reconcile the observed effect without dispatching again. The initial ACK is deliberately not used as the observation source; this is a client-ACK-discard scenario, not proven transport failure.

PASS source criteria: exactly one run under the expected SHA, completed/success, artifact with unique expected name, expected source/attempt IDs, and no retry; Product and shared Dolt unchanged.

This stage does NOT establish native Beads attempt-reconciliation integration, end-to-end true ACK loss, no duplicate provider effect under actual network outage, exclusive causal writers or Product migration. Preserve the later gate as NOT_QUALIFIED rather than introduce a Kernel-like new state owner. Architectural candidates can use provider-native receipts + Beads graph/history + competent Control without replicating Kernel structure, but invariants must be demonstrated explicitly.
