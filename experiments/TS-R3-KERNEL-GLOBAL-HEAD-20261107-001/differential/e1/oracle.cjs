'use strict';
const assert = require('node:assert/strict');
const os = require('node:os');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const work = process.argv[2];
assert(work && path.isAbsolute(work), 'EXPECTED_DISPOSABLE_ABSOLUTE_WORKDIR');
const { FilesystemStateStore, create, bootstrapTaskCycle, addObligations, transition, satisfy, inspect } = require(path.join(work, 'index.js'));
const home = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-product-v0-oracle-'));
const authority = { kind: 'AUTHORITY', id: 'DEV-GRANT-SYNTHETIC-E1' };
const evidence = { kind: 'EVIDENCE', id: 'EV-SYNTHETIC-RECONCILIATION-E1' };
try {
  const store = new FilesystemStateStore(home);
  store.initialize();
  const rev = () => store.verify().revision;
  const make = (kind, id, fields, refs = []) => create(store, rev(), kind, id, fields, refs);
  const advance = (kind, id, target, options = {}) => transition(store, rev(), kind, id, target, options);
  const reject = (fn, code) => assert.throws(fn, error => error && error.code === code, 'expected ' + code);
  assert.equal(rev(), 0);
  make('Milestone', 'M-1', { title: 'Synthetic milestone' }, [authority]);
  advance('Milestone', 'M-1', 'ACTIVE');
  make('TaskCycle', 'TC-1', { responsibility: 'Synthetic TaskCycle', obligations: [{ id: 'O-1', authority_ref: authority.id }] }, [authority]);
  advance('TaskCycle', 'TC-1', 'ACTIVE');
  addObligations(store, rev(), 'TC-1', [{ id: 'O-2' }], authority.id);
  make('Operation', 'OP-1', { taskcycle_id: 'TC-1', objective: 'Synthetic operation' }, [authority]);
  advance('Operation', 'OP-1', 'READY');
  advance('Operation', 'OP-1', 'RUNNING');
  make('ExecutionAttempt', 'ATT-1', { operation_id: 'OP-1' }, [authority]);
  advance('ExecutionAttempt', 'ATT-1', 'DISPATCHED');
  advance('ExecutionAttempt', 'ATT-1', 'UNKNOWN');
  reject(() => advance('Operation', 'OP-1', 'COMPLETED', { result_ref: 'RESULT-1' }), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  reject(() => make('ExecutionAttempt', 'ATT-2', { operation_id: 'OP-1' }, [authority]), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  advance('ExecutionAttempt', 'ATT-1', 'COMPLETED', { outcome: 'PASS', authority_ref: authority.id, result_refs: [evidence] });
  advance('Operation', 'OP-1', 'COMPLETED', { result_ref: 'RESULT-1' });
  reject(() => advance('TaskCycle', 'TC-1', 'PENDING_ACCEPTANCE'), 'UNSATISFIED_OBLIGATION');
  satisfy(store, rev(), 'TC-1', 'O-1', authority.id);
  satisfy(store, rev(), 'TC-1', 'O-2');
  advance('TaskCycle', 'TC-1', 'PENDING_ACCEPTANCE');
  advance('TaskCycle', 'TC-1', 'CLOSED', { authority_ref: authority.id, disposition_ref: 'DISPOSITION-1' });
  reject(() => addObligations(store, rev(), 'TC-1', [{ id: 'O-3' }], authority.id), 'INVALID_TRANSITION');
  advance('Milestone', 'M-1', 'CLOSED');
  const provenance = {
    mode: 'IMPORTED_ESTABLISHED_STATE',
    cutover_at: '2026-11-07T00:00:00.000Z',
    historical_events_reconstructed: false,
    authority_refs: [authority],
    evidence_refs: [evidence],
  };
  bootstrapTaskCycle(store, rev(), {
    id: 'TC-BOOTSTRAP', responsibility: 'Synthetic imported TaskCycle',
    state: 'BLOCKED', obligations: [{ id: 'OB-BOOT', status: 'PENDING' }],
    bootstrap_provenance: provenance,
  });
  reject(() => bootstrapTaskCycle(store, rev(), {
    id: 'TC-INVALID', responsibility: 'Invalid terminal import',
    state: 'CLOSED', obligations: [], bootstrap_provenance: provenance,
  }), 'INVALID_CONTRACT');
  assert.equal(inspect(store, 'TaskCycle', 'TC-1').aggregate.state, 'CLOSED');
  assert.equal(inspect(store, 'ExecutionAttempt', 'ATT-1').aggregate.reconciliation_required, false);
  assert.equal(inspect(store, 'TaskCycle', 'TC-BOOTSTRAP').aggregate.state, 'BLOCKED');
  const final = store.verify();
  const { state, events } = store.read();
  assert.equal(final.revision, state.revision);
  assert.equal(final.event_count, events.length);
  assert(final.event_count >= 17, 'EXPECTED_COVERED_SEQUENCE');
  assert.equal(state.aggregates.TaskCycle['TC-1'].terminal_disposition_ref, 'DISPOSITION-1');
  assert.equal(Object.keys(state.aggregates.ExecutionAttempt).length, 1);
  const kinds = Object.fromEntries(Object.entries(state.aggregates).map(([kind, items]) => [kind, Object.keys(items).length]));
  const evidenceJson = {
    status: 'PRODUCT_JS_V0_FOUR_KIND_GOLDEN_PASS',
    kinds, revision: final.revision, events: final.event_count,
    unknown_fenced: true, late_obligations_guarded: true, bootstrap_nonteminal: true,
    exact_product_source: true, backend: 'EPHEMERAL_PRODUCT_FILESYSTEM_ONLY',
    remote_pg_equivalence: 'NOT_RUN', product_effect: 'NONE',
  };
  process.stdout.write(JSON.stringify(evidenceJson) + '\n');
} finally {
  fs.rmSync(home, { recursive: true, force: true });
}
