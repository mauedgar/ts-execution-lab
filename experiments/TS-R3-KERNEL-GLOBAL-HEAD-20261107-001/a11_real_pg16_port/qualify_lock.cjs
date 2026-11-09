'use strict';
// A11 NONPRODUCT: original JS proposals, real PG16 row lock overlap across
// distinct backends, one host only. No Neon, Product or credentials.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {ShadowAsyncAdapter} = require('../a10_lc_core_semantics/shadow_async_adapter.cjs');
const {RealPg16DisposablePort} = require('./port.cjs');

assert.equal(process.argv.length, 5, 'original JS source, scratch and python required');
const source = path.resolve(process.argv[2]);
const scratch = path.resolve(process.argv[3]);
const python = path.resolve(process.argv[4]);
assert.ok(scratch.startsWith(path.join(os.tmpdir(), 'ts-r3-a11-')));
assert.ok(fs.existsSync(scratch));
assert.ok(!process.env.TS_R3_NEON_CHILD_DSN && !process.env.DATABASE_URL &&
          !process.env.PGPASSWORD);
const api = require(path.join(source, 'index.js'));
const authority = [{kind: 'AUTHORITY', id: 'A11-SYNTHETIC-AUTH-ONLY'}];

function lockedProbe(a, b) {
  const script = path.join(__dirname, 'lock_race.py');
  const wire = JSON.stringify({a, b});
  assert.ok(Buffer.byteLength(wire) < 6 * 1024 * 1024);
  return new Promise((resolve, reject) => {
    const child = spawn(python, ['-B', script], {
      cwd: path.resolve(__dirname, '..'),
      env: {
        PATH: process.env.PATH || '', HOME: process.env.HOME || '',
        TS_R3_LOCAL_SYNTHETIC_PG_URI: process.env.TS_R3_LOCAL_SYNTHETIC_PG_URI || '',
        PYTHONDONTWRITEBYTECODE: '1',
      },
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const output = [];
    let count = 0, abnormal = false, safeStage = 'A11_LOCK_STAGE_UNKNOWN';
    const timeout = setTimeout(() => { abnormal = true; child.kill(); }, 18000);
    child.stdout.on('data', chunk => {
      count += chunk.length;
      if (count > 512 * 1024) { abnormal = true; child.kill(); }
      else output.push(chunk);
    });
    child.stderr.on('data', chunk => {
      // Only a bounded synthetic marker is accepted; discard all other stderr.
      const marker = chunk.toString('utf8').match(/A11_LOCK_STAGE_[A-Z_]+/);
      if (marker && marker[0].length <= 90) safeStage = marker[0];
    });
    child.stdin.on('error', () => {});
    child.on('error', () => { abnormal = true; });
    child.on('close', code => {
      clearTimeout(timeout);
      if (abnormal || code !== 0) return reject(new Error(safeStage));
      try { resolve(JSON.parse(Buffer.concat(output).toString('utf8'))); }
      catch (_error) { reject(new Error('A11_LOCK_PROBE_MALFORMED')); }
    });
    child.stdin.end(wire);
  });
}

async function main() {
  const aDir = path.join(scratch, 'lock-original-js-a');
  const bDir = path.join(scratch, 'lock-original-js-b');
  fs.mkdirSync(aDir, {recursive: false});
  fs.mkdirSync(bDir, {recursive: false});
  const port = new RealPg16DisposablePort(python);
  const observed = await port.read();
  assert.equal(observed.revision, 5);
  const a = new ShadowAsyncAdapter(api, aDir, port).propose(
    observed, 'A10-PG16-LOCK-WRITER-A',
    (domain, store, rev) => domain.create(
      store, rev, 'Milestone', 'MS-A11-LOCK-WRITER-A', {title:'A'}, authority));
  const b = new ShadowAsyncAdapter(api, bDir, port).propose(
    observed, 'A10-PG16-LOCK-WRITER-B',
    (domain, store, rev) => domain.create(
      store, rev, 'Milestone', 'MS-A11-LOCK-WRITER-B', {title:'B'}, authority));
  const outcome = await lockedProbe(port.proposalWire(a), port.proposalWire(b));
  assert.equal(outcome.status, 'A11_REAL_PG16_POSITIVE_LOCK_OVERLAP_PASS');
  assert.equal(outcome.host_count, 1);
  assert.equal(outcome.backend_count, 2);
  assert.equal(outcome.server_blockers_observed, true);
  assert.equal(outcome.wait_event_type, 'Lock');
  assert.equal(outcome.winner, 'CONFIRMED');
  assert.equal(outcome.contender, 'NONE_STALE');
  assert.equal(outcome.revision, 6);
  const end = await port.read();
  assert.equal(end.revision, 6);
  const state = JSON.parse(end.stateBytes.toString('utf8'));
  assert.ok(state.aggregates.Milestone['MS-A11-LOCK-WRITER-A']);
  assert.equal(state.aggregates.Milestone['MS-A11-LOCK-WRITER-B'], undefined);
  assert.deepEqual(await port.counts(), {heads:1, events:6, receipts:6});
  console.log(JSON.stringify({
    status: 'A11_REAL_PG16_JS_CAS_WITH_LOCK_OVERLAP_PASS',
    server_lock_overlap_positive: true,
    backend_sessions: 2, physical_hosts: 1,
    heads: 1, events: 6, receipts: 6, revision: 6,
    original_js_proposal: true,
    neon: 'NOT_RUN', product_effect: 'NONE',
  }));
}
main().catch(error => {
  const marker = typeof error?.message === 'string' &&
    /^A11_LOCK_STAGE_[A-Z_]+$/.test(error.message)
    ? error.message : 'A11_LOCK_STAGE_UNCLASSIFIED';
  console.error('A11_LOCK_QUALIFICATION_FAIL_CLOSED_' + marker);
  process.exitCode = 1;
});
