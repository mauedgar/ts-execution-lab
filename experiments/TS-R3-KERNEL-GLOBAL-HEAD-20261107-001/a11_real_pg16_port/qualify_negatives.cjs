'use strict';
// A11 NONPRODUCT: exact original JS proposals against two real disposable PG16 clients,
// plus isolated subprocess fault fixtures. No remote SQL/credentials/Product effects.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {ShadowAsyncAdapter} = require('../a10_lc_core_semantics/shadow_async_adapter.cjs');
const {RealPg16DisposablePort, BoundedPortError} = require('./port.cjs');

assert.equal(process.argv.length, 5, 'exact JS fixture scratch python');
const source = path.resolve(process.argv[2]);
const scratch = path.resolve(process.argv[3]);
const python = path.resolve(process.argv[4]);
assert.ok(scratch.startsWith(path.join(os.tmpdir(), 'ts-r3-a11-')));
assert.ok(fs.existsSync(scratch));
assert.ok(!process.env.TS_R3_NEON_CHILD_DSN && !process.env.DATABASE_URL &&
          !process.env.PGPASSWORD);
const api = require(path.join(source, 'index.js'));
const auth = [{kind: 'AUTHORITY', id: 'A11-SYNTHETIC-AUTH-ONLY'}];

async function expectPortError(fn, code, stage) {
  await assert.rejects(fn, err => err instanceof BoundedPortError &&
    err.code === code && err.message === code && err.stage === stage,
    'exact bounded IPC result ' + code + '/' + stage);
}

async function main() {
  const leftRoot = path.join(scratch, 'competing-left');
  const rightRoot = path.join(scratch, 'competing-right');
  fs.mkdirSync(leftRoot, {recursive: false});
  fs.mkdirSync(rightRoot, {recursive: false});
  const aPort = new RealPg16DisposablePort(python);
  const bPort = new RealPg16DisposablePort(python);
  const aAdapter = new ShadowAsyncAdapter(api, leftRoot, aPort);
  const bAdapter = new ShadowAsyncAdapter(api, rightRoot, bPort);
  const observed = await aAdapter.observe();
  assert.equal(observed.revision, 4);
  const a = aAdapter.propose(observed, 'A10-PG16-COMPETE-A',
    (domain, store, revision) => domain.create(
      store, revision, 'Milestone', 'MS-A11-RACE-A', {title: 'A'}, auth));
  const b = bAdapter.propose(observed, 'A10-PG16-COMPETE-B',
    (domain, store, revision) => domain.create(
      store, revision, 'Milestone', 'MS-A11-RACE-B', {title: 'B'}, auth));
  const outcomes = await Promise.all([aAdapter.commit(a), bAdapter.commit(b)]);
  assert.deepEqual(outcomes.map(x => x.disposition).sort(), ['CONFIRMED', 'NONE_STALE']);
  const winner = outcomes[0].disposition === 'CONFIRMED' ? a : b;
  const stored = await aPort.read();
  assert.equal(stored.revision, 5);
  const projection = JSON.parse(stored.stateBytes.toString('utf8'));
  const keys = Object.keys(projection.aggregates.Milestone).filter(
    k => k === 'MS-A11-RACE-A' || k === 'MS-A11-RACE-B');
  assert.equal(keys.length, 1, 'single CAS winner across independent real connections');
  const afterRace = await aPort.counts();
  assert.deepEqual(afterRace, {heads: 1, events: 5, receipts: 5});

  // Same ID, different payload: must not generate a sixth event/receipt.
  const collision = aAdapter.propose(stored, winner.mutationId,
    (domain, store, revision) => domain.create(
      store, revision, 'Milestone', 'MS-A11-COLLISION', {title: 'COLLIDE'}, auth));
  await expectPortError(() => aPort.apply(collision),
    'A11_IPC_EXIT_UNCERTAIN', 'POSSIBLE_DISPATCH');
  assert.deepEqual(await aPort.counts(), afterRace);

  // An unknown receipt cannot be treated as NONE. This operation is a
  // READ-ONLY reconcile on a never-dispatched proposal.
  const absent = bAdapter.propose(stored, 'A10-PG16-MISSING-RECEIPT',
    (domain, store, revision) => domain.create(
      store, revision, 'Milestone', 'MS-A11-MISSING', {title: 'ABSENT'}, auth));
  await expectPortError(() => bPort.reconcile(absent),
    'A11_IPC_EXIT_UNCERTAIN', 'POSSIBLE_DISPATCH');
  assert.deepEqual(await aPort.counts(), afterRace);

  // No fake worker can reach the database or receive an actual PostgreSQL URI.
  process.env.TS_R3_A11_SYNTHETIC_FAULTS = '1';
  try {
    for (const [fault, code, timeout] of [
      ['MALFORMED', 'A11_IPC_MALFORMED_RESPONSE', 15000],
      ['EXIT', 'A11_IPC_EXIT_UNCERTAIN', 15000],
      ['TIMEOUT', 'A11_IPC_TIMEOUT', 250],
    ]) {
      const p = new RealPg16DisposablePort(python, {fault, timeoutMs: timeout});
      await expectPortError(() => p.call({op: 'read'}), code, 'POSSIBLE_DISPATCH');
    }
  } finally {
    delete process.env.TS_R3_A11_SYNTHETIC_FAULTS;
  }
  // Spawn failure before executable ever started is distinct from lost ACK.
  const missingExecutable = path.join(scratch, 'definitely-absent-interpreter');
  assert.equal(fs.existsSync(missingExecutable), false);
  const impossiblePort = new RealPg16DisposablePort(missingExecutable);
  await expectPortError(() => impossiblePort.call({op: 'read'}),
    'A11_IPC_SPAWN_FAILED', 'PRE_DISPATCH');
  assert.deepEqual(await aPort.counts(), afterRace);
  const finalRead = await bPort.read();
  assert.equal(finalRead.revision, 5);
  assert.equal(finalRead.eventBytes.toString('utf8').trimEnd().split('\n').length, 5);
  console.log(JSON.stringify({
    status: 'A11_REAL_PG16_NEGATIVE_BOUNDARIES_PASS',
    cases: ['TWO_CLIENT_REAL_PG_CAS_ONE_WINNER', 'MUTATION_ID_COLLISION_NO_EFFECT',
      'MISSING_RECEIPT_NOT_CONFIRMED_OR_NONE', 'MALFORMED_IPC_RESPONSE',
      'NONZERO_IPC_EXIT', 'IPC_DEADLINE', 'PRE_DISPATCH_SPAWN_ERROR'],
    real_postgres: 'DISPOSABLE_PG16',
    physical_host_count: 1,
    proven_server_lock_overlap: false,
    original_product_js: true,
    heads: 1, events: 5, receipts: 5, revision: 5,
    no_product_effect: true, neon: 'NOT_RUN',
    state_sha256: crypto.createHash('sha256').update(finalRead.stateBytes).digest('hex'),
  }));
}
main().catch(error => {
  console.error('A11_NEGATIVE_FAIL_CLOSED_' +
    (error instanceof BoundedPortError ? error.code : 'ASSERTION'));
  process.exitCode = 1;
});
