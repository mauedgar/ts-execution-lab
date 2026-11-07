'use strict';
const assert = require('node:assert/strict');
const os = require('node:os');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const work = process.argv[2];
const output = process.argv[3];
assert(work && path.isAbsolute(work), 'EXPECTED_DISPOSABLE_ABSOLUTE_WORKDIR');
assert(output && path.isAbsolute(output) && output.startsWith(work + path.sep),
       'EXPECTED_DISPOSABLE_OUTPUT_INSIDE_WORKDIR');
const { FilesystemStateStore, create, bootstrapTaskCycle, addObligations, transition, satisfy, inspect } = require(path.join(work, 'index.js'));
const home = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-product-v0-oracle-'));
const authority = { kind: 'AUTHORITY', id: 'DEV-GRANT-SYNTHETIC-E1' };
const evidence = { kind: 'EVIDENCE', id: 'EV-SYNTHETIC-RECONCILIATION-E1' };
try {
  const store = new FilesystemStateStore(home);
  const captured = [];
  const originalCommit = store.commit.bind(store);
  store.commit = (state, eventsBytes, useFailpoint = true) => {
    const head = originalCommit(state, eventsBytes, useFailpoint);
    const dir = path.join(store.root, head.generation);
    const snapshot = fs.readFileSync(path.join(dir, 'state.json'));
    const events = fs.readFileSync(path.join(dir, 'events.ndjson'));
    const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    assert.equal(sha(snapshot), head.state_sha256);
    assert.equal(sha(events), head.events_sha256);
    const seq = head.revision;
    const eventLines = events.length ? events.toString('utf8').trimEnd().split('\n') : [];
    assert.equal(eventLines.length, seq, 'event count matches every committed Product generation');
    let eventPayload = null;
    let eventLine = null;
    let previousHash = null;
    let eventHash = null;
    if (seq > 0) {
      const line = eventLines.at(-1) + '\n';
      const parsed = JSON.parse(line);
      const { hash, ...payload } = parsed;
      const payloadBytes = Buffer.from(JSON.stringify(payload), 'utf8');
      assert.equal(sha(payloadBytes), hash, 'Product authentic event hash');
      assert.equal(line, JSON.stringify(parsed) + '\n');
      assert.equal(payload.sequence, seq);
      eventPayload = payloadBytes.toString('base64');
      eventLine = Buffer.from(line, 'utf8').toString('base64');
      previousHash = payload.previous_hash;
      eventHash = hash;
    }
    captured.push({
      revision: seq,
      state_b64: snapshot.toString('base64'),
      events_b64: events.toString('base64'),
      payload_b64: eventPayload,
      event_line_b64: eventLine,
      previous_hash: previousHash,
      event_hash: eventHash,
    });
    return head;
  };
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
  assert.equal(final.event_count, 19, 'FROZEN_PRODUCT_GOLDEN_EXACT_EVENT_COUNT');
  assert.equal(captured.length, 20, 'GENESIS_PLUS_19_PRODUCT_COMMITS');
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
  fs.writeFileSync(output, JSON.stringify({
    kind: 'PRODUCT_JS_V0_EXACT_GENERATIONS',
    product_git_commit: '26509b74d50207bb247dcc9bdb929a63f5451e88',
    source_blobs: {
      contracts: '5d2d3a8a24ebc17339675e0c801595956e0cd353',
      index: '0219b92e5f546407a6060a6dc449865c14c7f144',
      store: 'f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a'
    },
    scope: 'ts-r3-e1-product-bridge-20261107-002',
    generations: captured,
  }), { encoding: 'utf8', flag: 'wx' });
  process.stdout.write(JSON.stringify({ ...evidenceJson,
    fixture_generations: captured.length, exact_events: 19,
    fixture_output: 'EPHEMERAL_ONLY', postgres_effect: 'NONE'
  }) + '\n');
} finally {
  fs.rmSync(home, { recursive: true, force: true });
}
