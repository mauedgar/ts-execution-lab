'use strict';
// A10 NONPRODUCT: execute frozen Product JS V0 as the semantic oracle.
// This DOES NOT migrate, copy or modify the Product Upper LC / TaskCycle Core rules.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

assert.equal(process.argv.length, 4, 'fixture and disposable root required');
const source = path.resolve(process.argv[2]);
const scratch = path.resolve(process.argv[3]);
assert.ok(scratch.startsWith(path.join(require('node:os').tmpdir(), 'ts-r3-a10-')),
  'must use unique isolated disposable temp namespace');
assert.equal(fs.existsSync(scratch), true, 'disposable root must preexist');
const api = require(path.join(source, 'index.js'));
const rules = require(path.join(source, 'contracts.js'));
const authority = [{kind: 'AUTHORITY', id: 'A10-DEV-EXPLICIT'}];
const evidence = [{kind: 'EVIDENCE', id: 'A10-RECONCILIATION-EVIDENCE'}];
const outcomes = [];
let activeStore = null;
function persistedBytes(store) {
  const head = fs.readFileSync(store.head);
  const generation = JSON.parse(head.toString('utf8')).generation;
  const committed = path.join(store.root, generation);
  return {
    head,
    state: fs.readFileSync(path.join(committed, 'state.json')),
    events: fs.readFileSync(path.join(committed, 'events.ndjson')),
  };
}
function negative(action, code) {
  const before = activeStore === null ? null : persistedBytes(activeStore);
  assert.throws(action, error => Boolean(error && error.code === code),
    'expected exact Product KernelError ' + code);
  if (before) {
    const after = persistedBytes(activeStore);
    assert.deepEqual(after.head, before.head, code + ': HEAD bytes changed after rejection');
    assert.deepEqual(after.state, before.state, code + ': snapshot bytes changed after rejection');
    assert.deepEqual(after.events, before.events, code + ': event bytes changed after rejection');
    assert.equal(activeStore.verify().revision, JSON.parse(before.state.toString('utf8')).revision,
      code + ': revision changed after rejection');
  }
  outcomes.push(code);
}
function withStore(label, check) {
  const home = path.join(scratch, label);
  fs.mkdirSync(home, {recursive: false});
  const store = new api.FilesystemStateStore(home);
  const genesis = store.initialize();
  assert.equal(genesis.revision, 0);
  try {
    assert.equal(activeStore, null, 'no nested stores');
    activeStore = store;
    check(store);
    const result = store.verify();
    assert.equal(result.valid, true);
    assert.equal(result.revision, result.event_count);
  } finally {
    activeStore = null;
    fs.rmSync(home, {recursive: true, force: true});
  }
}
assert.deepEqual(rules.KINDS, ['Milestone', 'TaskCycle', 'Operation', 'ExecutionAttempt']);
assert.deepEqual(rules.STATES.TaskCycle,
  ['READY', 'ACTIVE', 'BLOCKED', 'PENDING_ACCEPTANCE', 'CLOSED', 'CANCELLED']);
assert.deepEqual(rules.TRANSITIONS.ExecutionAttempt.UNKNOWN,
  ['COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED']);
assert.equal(typeof api.create, 'function');
assert.equal(typeof api.bootstrapTaskCycle, 'function');
assert.equal(typeof api.addObligations, 'function');
assert.equal(typeof api.satisfy, 'function');
assert.equal(typeof api.transition, 'function');

withStore('milestone-positive-and-negative', store => {
  api.create(store, 0, 'Milestone', 'MS-A10-01', {title: 'MILESTONE-CANARY'}, authority);
  negative(() => api.transition(store, 1, 'Milestone', 'MS-A10-01', 'CLOSED'),
    'INVALID_TRANSITION');
  api.transition(store, 1, 'Milestone', 'MS-A10-01', 'ACTIVE');
  api.transition(store, 2, 'Milestone', 'MS-A10-01', 'CLOSED');
  negative(() => api.transition(store, 3, 'Milestone', 'MS-A10-01', 'CANCELLED'),
    'INVALID_TRANSITION');
  const projection = api.inspect(store, 'Milestone', 'MS-A10-01');
  assert.equal(projection.aggregate.state, 'CLOSED');
  assert.deepEqual(projection.legal_next, []);
  assert.equal(store.verify().revision, 3);
});

withStore('taskcycle-obligation-close', store => {
  api.create(store, 0, 'TaskCycle', 'TC-A10-01',
    {responsibility: 'A10-SEMANTIC-CANARY', obligations: [{id: 'VALIDATE', authority_ref: null}]},
    authority);
  api.transition(store, 1, 'TaskCycle', 'TC-A10-01', 'ACTIVE');
  negative(() => api.transition(store, 2, 'TaskCycle', 'TC-A10-01', 'PENDING_ACCEPTANCE'),
    'UNSATISFIED_OBLIGATION');
  api.satisfy(store, 2, 'TC-A10-01', 'VALIDATE');
  api.transition(store, 3, 'TaskCycle', 'TC-A10-01', 'PENDING_ACCEPTANCE');
  negative(() => api.transition(store, 4, 'TaskCycle', 'TC-A10-01', 'CLOSED',
    {disposition_ref: 'A10-DISPOSITION'}), 'MISSING_REQUIRED_AUTHORITY');
  api.transition(store, 4, 'TaskCycle', 'TC-A10-01', 'CLOSED',
    {disposition_ref: 'A10-DISPOSITION', authority_ref: authority[0].id});
  negative(() => api.addObligations(store, 5, 'TC-A10-01',
    [{id: 'FORBIDDEN-LATE'}], authority[0].id), 'INVALID_TRANSITION');
  assert.equal(api.inspect(store, 'TaskCycle', 'TC-A10-01').aggregate.state, 'CLOSED');
  assert.equal(store.verify().revision, 5);
});

withStore('attempt-unknown-fencing', store => {
  api.create(store, 0, 'TaskCycle', 'TC-A10-02',
    {responsibility: 'RECOVERY-CANARY', obligations: []}, authority);
  api.create(store, 1, 'Operation', 'OP-A10-02',
    {taskcycle_id: 'TC-A10-02', objective: 'ONE EFFECT'}, authority);
  api.transition(store, 2, 'Operation', 'OP-A10-02', 'READY');
  api.transition(store, 3, 'Operation', 'OP-A10-02', 'RUNNING');
  api.create(store, 4, 'ExecutionAttempt', 'ATT-A10-02',
    {operation_id: 'OP-A10-02'}, authority);
  api.transition(store, 5, 'ExecutionAttempt', 'ATT-A10-02', 'DISPATCHED');
  api.transition(store, 6, 'ExecutionAttempt', 'ATT-A10-02', 'UNKNOWN');
  negative(() => api.create(store, 7, 'ExecutionAttempt', 'ATT-A10-02-NEW',
    {operation_id: 'OP-A10-02'}, authority), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  negative(() => api.transition(store, 7, 'Operation', 'OP-A10-02', 'COMPLETED',
    {result_ref: 'ATT-RESULT'}), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  negative(() => api.transition(store, 7, 'ExecutionAttempt', 'ATT-A10-02', 'COMPLETED',
    {outcome: 'PASS', result_refs: evidence}), 'MISSING_REQUIRED_AUTHORITY');
  api.transition(store, 7, 'ExecutionAttempt', 'ATT-A10-02', 'COMPLETED',
    {outcome: 'PASS', result_refs: evidence, authority_ref: authority[0].id});
  api.transition(store, 8, 'Operation', 'OP-A10-02', 'COMPLETED',
    {result_ref: 'ATT-RESULT'});
  assert.equal(api.inspect(store, 'ExecutionAttempt', 'ATT-A10-02')
    .aggregate.reconciliation_required, false);
  assert.equal(store.verify().revision, 9);
});

withStore('monotonic-late-obligation', store => {
  api.create(store, 0, 'TaskCycle', 'TC-A10-03',
    {responsibility: 'LATE-OBLIGATION', obligations: []}, authority);
  negative(() => api.addObligations(store, 1, 'TC-A10-03',
    [{id: 'LATE-1'}], 'WRONG-GRANT'), 'MISSING_REQUIRED_AUTHORITY');
  api.addObligations(store, 1, 'TC-A10-03',
    [{id: 'LATE-1'}], authority[0].id);
  negative(() => api.addObligations(store, 2, 'TC-A10-03',
    [{id: 'LATE-1'}], authority[0].id), 'INVALID_CONTRACT');
  api.transition(store, 2, 'TaskCycle', 'TC-A10-03', 'ACTIVE');
  negative(() => api.transition(store, 3, 'TaskCycle', 'TC-A10-03', 'PENDING_ACCEPTANCE'),
    'UNSATISFIED_OBLIGATION');
  api.satisfy(store, 3, 'TC-A10-03', 'LATE-1');
  api.transition(store, 4, 'TaskCycle', 'TC-A10-03', 'PENDING_ACCEPTANCE');
  negative(() => api.addObligations(store, 5, 'TC-A10-03',
    [{id: 'LATE-2'}], authority[0].id), 'INVALID_TRANSITION');
  assert.equal(store.verify().revision, 5);
});

withStore('no-historical-event-invention', store => {
  const provenance = {
    mode: 'IMPORTED_ESTABLISHED_STATE',
    cutover_at: '2026-11-08T12:00:00.000Z',
    historical_events_reconstructed: false,
    authority_refs: authority,
    evidence_refs: evidence,
  };
  negative(() => api.bootstrapTaskCycle(store, 0, {
    id: 'TC-A10-04', responsibility: 'IMPORT', obligations: [], state: 'CLOSED',
    bootstrap_provenance: provenance,
  }), 'INVALID_CONTRACT');
  negative(() => api.bootstrapTaskCycle(store, 0, {
    id: 'TC-A10-04', responsibility: 'IMPORT', obligations: [], state: 'ACTIVE',
    bootstrap_provenance: {...provenance, historical_events_reconstructed: true},
  }), 'INVALID_CONTRACT');
  api.bootstrapTaskCycle(store, 0, {
    id: 'TC-A10-04', responsibility: 'IMPORT', obligations: [], state: 'ACTIVE',
    bootstrap_provenance: provenance,
  });
  const {events} = store.read();
  assert.equal(events.length, 1);
  assert.equal(events[0].action, 'BOOTSTRAP_IMPORT');
  assert.equal(events[0].bootstrap_provenance.historical_events_reconstructed, false);
  assert.equal(events[0].after.created_at, provenance.cutover_at);
  assert.equal(store.verify().revision, 1);
});

// Demonstrate why an asynchronous network store CANNOT be silently swapped
// under old synchronous index.js API; a separately designed caller boundary is needed.
const asyncStore = {
  mutate: async () => ({revision: 1, event_id: 'not-real'}),
  read: async () => ({state: {aggregates: {Milestone: {}}}}),
};
const proposed = api.create(asyncStore, 0, 'Milestone', 'M-A10-ASYNC', {title: 'ASYNC'});
assert.equal(typeof proposed.then, 'function', 'old API now returns Promise');
assert.throws(() => api.inspect(asyncStore, 'Milestone', 'M-A10-ASYNC'),
  error => error instanceof TypeError, 'old synchronous read caller must not silently accept Promise');

console.log(JSON.stringify({
  status: 'A10_FROZEN_PRODUCT_SEMANTICS_PRESERVATION_PASS',
  frozen_product: 'mauedgar/tecnotron-ai:tools@26509b74d50207bb247dcc9bdb929a63f5451e88',
  four_kinds: rules.KINDS,
  cases: ['Milestone-positive-negative', 'TaskCycle-closure-obligation-authority', 'UNKNOWN-no-retry-reconciliation',
          'monotonic-authorized-late-obligation', 'no-invented-bootstrap-history',
          'async-boundary-explicit'],
  exact_rejections: outcomes.length,
  no_new_lifecycle: true,
  async_storage_dropin: 'REJECTED',
  original_product_source_mutated: false,
  neon: 'NOT_RUN',
  product_effect: 'NONE',
}));
