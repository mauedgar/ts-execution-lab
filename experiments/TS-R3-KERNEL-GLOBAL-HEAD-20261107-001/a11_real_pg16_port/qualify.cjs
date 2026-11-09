'use strict';
// NONPRODUCT exact original JS -> async IPC -> real disposable PG16 experiment.
// Never Neon, never live Product, never a standalone authority decision engine.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {ShadowAsyncAdapter, snapshotBytes} = require('../a10_lc_core_semantics/shadow_async_adapter.cjs');
const {RealPg16DisposablePort} = require('./port.cjs');
const sha = v => crypto.createHash('sha256').update(v).digest('hex');
const SCOPE = 'A10-DISPOSABLE-SINGLE-SCOPE';
let phase = 'ENTRY';

assert.equal(process.argv.length, 5, 'fixture, unique scratch, pinned python');
const fixture = path.resolve(process.argv[2]);
const scratch = path.resolve(process.argv[3]);
const python = path.resolve(process.argv[4]);
assert.ok(scratch.startsWith(path.join(os.tmpdir(), 'ts-r3-a11-')));
assert.ok(fs.existsSync(scratch));
const api = require(path.join(fixture, 'index.js'));
const auth = [{kind: 'AUTHORITY', id: 'A11-SYNTHETIC-AUTH-ONLY'}];

function makeOriginalReader(recovered, dirname) {
  const home = path.join(scratch, dirname);
  fs.mkdirSync(home, {recursive: false});
  const store = new api.FilesystemStateStore(home);
  fs.mkdirSync(store.root, {recursive: true});
  const gen = 'a11-recovered-gen';
  const dir = path.join(store.root, gen);
  fs.mkdirSync(dir);
  fs.writeFileSync(path.join(dir, 'state.json'), recovered.stateBytes, {flag: 'wx'});
  fs.writeFileSync(path.join(dir, 'events.ndjson'), recovered.eventBytes, {flag: 'wx'});
  fs.writeFileSync(store.head, JSON.stringify({
    schema_version: 'tecnotron-state-head/v0',
    generation: gen,
    revision: recovered.revision,
    state_sha256: sha(recovered.stateBytes),
    events_sha256: sha(recovered.eventBytes),
  }, null, 2) + '\n', {flag: 'wx'});
  const result = store.verify();
  assert.equal(result.revision, recovered.revision);
  return store;
}
async function main() {
  assert.ok(!process.env.TS_R3_NEON_CHILD_DSN);
  assert.ok(!process.env.DATABASE_URL);
  assert.ok(!process.env.PGPASSWORD);
  const genesisHome = path.join(scratch, 'genesis');
  fs.mkdirSync(genesisHome, {recursive: false});
  const original = new api.FilesystemStateStore(genesisHome);
  original.initialize();
  const genesis = snapshotBytes(original);
  assert.equal(genesis.revision, 0);
  const port = new RealPg16DisposablePort(python);
  phase = 'INIT';
  assert.equal((await port.initialize(genesis.stateBytes)).revision, 0);
  const adapter = new ShadowAsyncAdapter(api, scratch, port);
  phase = 'READ_GENESIS';
  const first = await adapter.observe();
  assert.equal(first.revision, 0);
  assert.ok(first.stateBytes.equals(genesis.stateBytes));
  phase = 'PROPOSE_A';
  const commandA = adapter.propose(first, 'A10-PG16-A',
    (domain, store, revision) => domain.create(store, revision,
      'TaskCycle', 'TC-A11', {
        responsibility: 'A11-PERSISTENCE-EQUIVALENCE',
        obligations: [{id: 'VALIDATE', authority_ref: null}],
      }, auth));
  const stale = adapter.propose(first, 'A10-PG16-STALE',
    (domain, store, revision) => domain.create(store, revision,
      'Milestone', 'MS-A11-STALE', {title: 'SHOULD-NOT-PERSIST'}, auth));
  phase = 'APPLY_A';
  const confirmedA = await adapter.commit(commandA);
  assert.equal(confirmedA.disposition, 'CONFIRMED');
  assert.equal(confirmedA.revision, 1);
  phase = 'STALE_B';
  const none = await adapter.commit(stale);
  assert.equal(none.disposition, 'NONE_STALE');
  assert.equal((await port.counts()).events, 1);
  phase = 'READ_1';
  const second = await adapter.observe();
  assert.equal(second.revision, 1);
  phase = 'PROPOSE_B';
  const commandB = adapter.propose(second, 'A10-PG16-B',
    (domain, store, revision) => domain.transition(
      store, revision, 'TaskCycle', 'TC-A11', 'ACTIVE'));
  port.simulateLostReplyOnce = true;
  phase = 'POST_COMMIT_LOSS';
  const uncertain = await adapter.commit(commandB);
  assert.equal(uncertain.disposition, 'UNKNOWN_FENCED');
  assert.equal((await port.counts()).events, 2,
    'real PG transaction was committed before synthetic IPC response loss');
  assert.throws(() => adapter.propose(second, 'A10-PG16-RETRY',
    (domain, store, revision) => domain.create(store, revision,
      'Milestone', 'MS-A11-RETRY', {title: 'FORBIDDEN'}, auth)),
    /UNKNOWN_EFFECT_REQUIRES_RECONCILIATION/);
  assert.equal((await adapter.commit(stale)).disposition, 'BLOCKED_UNRECONCILED');
  phase = 'RECONCILE_B';
  const originalOnly = await adapter.reconcile();
  assert.equal(originalOnly.disposition, 'CONFIRMED');
  assert.equal(originalOnly.mutationId, 'A10-PG16-B');
  assert.equal(originalOnly.revision, 2);
  assert.equal((await port.counts()).receipts, 2,
    'reconciliation is read-only, not a new mutation');

  phase = 'READ_2';
  const third = await adapter.observe();
  phase = 'PROPOSE_C';
  const commandC = adapter.propose(third, 'A10-PG16-C',
    (domain, store, revision) => domain.satisfy(
      store, revision, 'TC-A11', 'VALIDATE'));
  phase = 'APPLY_C';
  assert.equal((await adapter.commit(commandC)).disposition, 'CONFIRMED');

  phase = 'READ_3';
  const fourth = await adapter.observe();
  phase = 'PROPOSE_D';
  const commandD = adapter.propose(fourth, 'A10-PG16-D',
    (domain, store, revision) => domain.transition(
      store, revision, 'TaskCycle', 'TC-A11', 'PENDING_ACCEPTANCE'));
  phase = 'APPLY_D';
  assert.equal((await adapter.commit(commandD)).disposition, 'CONFIRMED');
  phase = 'READ_4';
  const result = await adapter.observe();
  assert.equal(result.revision, 4);
  const counts = await port.counts();
  assert.deepEqual(counts, {heads: 1, events: 4, receipts: 4});
  phase = 'ORIGINAL_RESTORE';
  const originalJs = makeOriginalReader(result, 'original-js-restore');
  assert.ok(originalJs.read().state.aggregates.TaskCycle['TC-A11']);
  assert.equal(originalJs.read().state.aggregates.TaskCycle['TC-A11'].state,
    'PENDING_ACCEPTANCE');
  assert.equal(originalJs.verify().revision, 4);
  assert.equal(result.eventBytes.toString('utf8').trimEnd().split('\n').length, 4);
  assert.equal(result.stateBytes[result.stateBytes.length - 1], 10);
  assert.equal(result.eventBytes[result.eventBytes.length - 1], 10);
  phase = 'EMIT_RESULT';
  console.log(JSON.stringify({
    status: 'A11_ORIGINAL_JS_ASYNC_REAL_POSTGRES16_BRIDGE_PASS',
    original_product_js: 'PINNED_3_BLOBS',
    real_backend: 'DISPOSABLE_REAL_POSTGRESQL16',
    shadow_async_adapter: 'A10_IR003_LOCAL_0_0',
    exact_state_sha256: sha(result.stateBytes),
    exact_events_sha256: sha(result.eventBytes),
    cases: ['ORIGINAL_JS_GENESIS_TO_PG', 'ORIGINAL_JS_PROPOSAL_REAL_PG_CAS',
      'STALE_NONE_NO_EVENT', 'REAL_PG_COMMIT_SYNTHETIC_IPC_REPLY_LOSS_UNKNOWN',
      'ORIGINAL_MUTATION_READ_ONLY_RECONCILIATION_NO_REDISPATCH',
      'ORIGINAL_JS_OBLIGATION_AND_ACCEPTANCE', 'ORIGINAL_JS_RESTORE_FINAL_BYTES'],
    heads: counts.heads, events: counts.events, receipts: counts.receipts,
    revision: result.revision,
    synthetic_ipc_loss: 'YES',
    real_tcp_ack_loss: 'NOT_RUN',
    physical_two_hosts: 'NOT_RUN',
    remote_neon: 'NOT_RUN',
    product_effect: 'NONE',
  }));
}
main().catch(_err => {
  // JSON status for CI; no local connection strings or error stack.
  console.error('A11_FAIL_CLOSED_' + phase);
  process.exitCode = 1;
});
