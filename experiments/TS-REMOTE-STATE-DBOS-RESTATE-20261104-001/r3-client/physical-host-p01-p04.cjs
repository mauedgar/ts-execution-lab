'use strict';
// R3 experimental client: synthetic data only. No Product/Kernel data, no secrets in stdout.
// This client is NOT physical attestation; external A/B host witnesses and scoped roles are gates.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const os = require('node:os');
const { Client } = require('../r2-node/node_modules/pg');

const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
function canonical(value) {
  if (value === null) return 'null';
  if (typeof value === 'string') return JSON.stringify(value);
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') {
    assert(Number.isSafeInteger(value), 'canonical integers only');
    return String(value);
  }
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  assert(value && Object.getPrototypeOf(value) === Object.prototype, 'plain object only');
  return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
}
const hashObject = (kind, value) => sha('TS-R3-JSON-SORTED-V1\n' + kind + '\n' + canonical(value));

const {
  TS_R3_DATABASE_URL, TS_R3_EXPECTED_HOST, TS_R3_TEST_ID, TS_R3_HOST_LABEL,
  TS_R3_EXPECTED_DB_ROLE, TS_R3_EXPECTED_DEVICE_DIGEST
} = process.env;
const phase = process.argv[2];
const phases = ['probe', 'write', 'write-drop-ack', 'read', 'replay', 'collision', 'recover', 'tls-negative'];
assert(phases.includes(phase), 'unsupported phase');
assert(/^(HOST_A|HOST_B)$/.test(TS_R3_HOST_LABEL || ''), 'invalid host label');
assert(/^R3-HOST-[A-Za-z0-9_-]{8,50}$/.test(TS_R3_TEST_ID || ''), 'isolated synthetic test id');
assert(/^ep-[a-z0-9-]+\.c-2\.sa-east-1\.aws\.neon\.tech$/.test(TS_R3_EXPECTED_HOST || ''), 'pinned endpoint required');
assert(/^[A-Za-z_][A-Za-z0-9_]{0,62}$/.test(TS_R3_EXPECTED_DB_ROLE || ''), 'pinned scoped DB role required');
assert(/^[a-f0-9]{64}$/.test(TS_R3_EXPECTED_DEVICE_DIGEST || ''), 'external device digest preflight required');
assert(typeof TS_R3_DATABASE_URL === 'string' && TS_R3_DATABASE_URL.length < 2048, 'private URL required');

const selfDigest = sha(os.hostname());
assert(selfDigest === TS_R3_EXPECTED_DEVICE_DIGEST, 'device self-identity does not match preflight');
const u = new URL(TS_R3_DATABASE_URL);
assert(['postgres:', 'postgresql:'].includes(u.protocol), 'Postgres protocol required');
assert(u.hostname === TS_R3_EXPECTED_HOST && u.pathname === '/ts_remote_r3', 'endpoint/database pin mismatch');
assert(!u.hash && !u.searchParams.has('options'), 'unsupported URL fragment/options');
for (const [k, v] of u.searchParams) assert(k === 'sslmode' && v === 'verify-full', 'only verify-full URL option supported');
const options = {
  host: u.hostname, port: Number(u.port || 5432), database: 'ts_remote_r3',
  user: decodeURIComponent(u.username), password: decodeURIComponent(u.password),
  connectionTimeoutMillis: 15000, query_timeout: 15000,
  ssl: { rejectUnauthorized: true, servername: u.hostname }
};
assert(options.port === 5432 && options.user && options.password, 'private credentials required');
assert(!options.user.includes('tsr3_owner'), 'owner credential forbidden for host tests');
if (['write', 'write-drop-ack'].includes(phase)) assert(TS_R3_HOST_LABEL === 'HOST_A', 'A writes only');
if (['read', 'replay', 'collision', 'recover'].includes(phase)) assert(TS_R3_HOST_LABEL === 'HOST_B', 'B verifies only');

const SCHEMA = 'ts_r3_synthetic_20261105_001';
const id = TS_R3_TEST_ID;
const eventId = id + '-event1';
const mutationId = id + '-command1';
const baseCommand = Object.freeze({
  type: 'Create', kind: 'TaskCycle', id, expected_revision: 0,
  authority_refs: ['AUTH-SYNTHETIC-R3'],
  fields: { responsibility: 'synthetic R3 two physical hosts', obligations: [] }
});
const state = { kind: 'TaskCycle', id, state: 'READY', revision: 1, synthetic: true };
const event = { action: 'CREATE', kind: 'TaskCycle', id, sequence: 1, previous_hash: null, after: state };
const eventHash = hashObject('event', event);
const originalResult = { revision: 1, event_id: eventId, synthetic: true };
const originalFingerprint = hashObject('command', baseCommand);

async function checkIdentity(c) {
  const q = await c.query("SELECT current_database() AS db, current_user AS principal, current_setting('server_version_num')::int AS ver, (SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls, (SELECT version FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls_version");
  assert(q.rowCount === 1, 'one server identity row');
  const r = q.rows[0];
  assert.equal(r.db, 'ts_remote_r3');
  assert.equal(r.principal, TS_R3_EXPECTED_DB_ROLE, 'principal mismatch');
  assert(Number(r.ver) >= 160000 && Number(r.ver) < 170000, 'PostgreSQL 16 required');
  assert.equal(r.tls, true, 'external session must negotiate TLS');
  return r;
}
async function verify(c) {
  const q = await c.query(
    'SELECT a.revision,a.state,a.last_event_sha256,e.sequence,e.previous_hash,e.event_hash,e.payload,r.command_fingerprint,r.original_revision,r.result ' +
    'FROM ' + SCHEMA + '.aggregate_state a JOIN ' + SCHEMA + '.events e ON e.id=a.id ' +
    'JOIN ' + SCHEMA + '.receipts r ON r.mutation_id=$2 WHERE a.id=$1 AND e.event_id=$3',
    [id, mutationId, eventId]
  );
  assert.equal(q.rowCount, 1, 'single joined immutable subject');
  const r = q.rows[0];
  assert.equal(Number(r.revision), 1);
  assert.deepEqual(r.state, state);
  assert.equal(r.last_event_sha256, eventHash);
  assert.equal(Number(r.sequence), 1);
  assert.equal(r.previous_hash, null);
  assert.equal(r.event_hash, eventHash);
  assert.deepEqual(r.payload, event);
  assert.equal(r.command_fingerprint, originalFingerprint);
  assert.equal(Number(r.original_revision), 1);
  assert.deepEqual(r.result, originalResult);
  const counts = await c.query(
    'SELECT (SELECT COUNT(*)::int FROM ' + SCHEMA + '.aggregate_state WHERE id=$1) AS states, ' +
    '(SELECT COUNT(*)::int FROM ' + SCHEMA + '.events WHERE id=$1) AS events, ' +
    '(SELECT COUNT(*)::int FROM ' + SCHEMA + '.receipts WHERE mutation_id=$2) AS receipts',
    [id, mutationId]
  );
  assert.deepEqual(counts.rows[0], { states: 1, events: 1, receipts: 1 }, 'one actual effect/receipt');
  return { revision: 1, event_hash: eventHash, receipt: r.result };
}
// Same command handler for initial write, exact replay, and mismatched-authority replay.
// HOST_B uses the exact handler in EXISTING_ONLY mode; a missing receipt is UNKNOWN,
// never an invitation to create from B or replay an ambiguous HOST_A write.
async function dispatch(c, command, allowCreate) {
  const fingerprint = hashObject('command', command);
  await c.query(allowCreate ? 'BEGIN' : 'BEGIN READ ONLY');
  let commitStarted = false;
  try {
    // Serializes same-key concurrent dispatches; PK uniqueness is defense in depth.
    await c.query('SELECT pg_advisory_xact_lock(hashtextextended($1,0))', [mutationId]);
    const prior = await c.query(
      'SELECT command_fingerprint,original_revision,result FROM ' + SCHEMA + '.receipts WHERE mutation_id=$1',
      [mutationId]
    );
    if (prior.rowCount) {
      assert.equal(prior.rowCount, 1);
      if (prior.rows[0].command_fingerprint !== fingerprint) {
        const err = new Error('KEY_COLLISION');
        err.safeCode = 'KEY_COLLISION';
        throw err;
      }
      assert.equal(Number(prior.rows[0].original_revision), 1);
      assert.deepEqual(prior.rows[0].result, originalResult);
      commitStarted = true;
      await c.query('COMMIT');
      return { status: 'REPLAY', result: prior.rows[0].result };
    }
    if (!allowCreate) {
      const err = new Error('UNCONFIRMED_ORIGINAL');
      err.safeCode = 'UNCONFIRMED_ORIGINAL';
      throw err;
    }
    assert.deepEqual(command, baseCommand, 'genesis command only');
    const existing = await c.query('SELECT revision FROM ' + SCHEMA + '.aggregate_state WHERE id=$1', [id]);
    if (existing.rowCount !== 0) {
      const err = new Error('STALE_REVISION');
      err.safeCode = 'STALE_REVISION';
      throw err;
    }
    await c.query('INSERT INTO ' + SCHEMA + '.aggregate_state(id,revision,state,last_event_sha256) VALUES ($1,1,$2::jsonb,$3)',
      [id, JSON.stringify(state), eventHash]);
    await c.query('INSERT INTO ' + SCHEMA + '.events(event_id,id,sequence,previous_hash,event_hash,payload) VALUES ($1,$2,1,NULL,$3,$4::jsonb)',
      [eventId, id, eventHash, JSON.stringify(event)]);
    await c.query('INSERT INTO ' + SCHEMA + '.receipts(mutation_id,command_fingerprint,original_revision,result) VALUES ($1,$2,1,$3::jsonb)',
      [mutationId, fingerprint, JSON.stringify(originalResult)]);
    // A failed/dropped COMMIT ACK cannot be safely rolled back or retried.
    commitStarted = true;
    await c.query('COMMIT');
    return { status: 'CREATED', result: originalResult };
  } catch (err) {
    if (commitStarted) {
      const unknown = new Error('AMBIGUOUS_COMMIT_ACK');
      unknown.safeCode = 'AMBIGUOUS_COMMIT_ACK';
      throw unknown;
    }
    try { await c.query('ROLLBACK'); } catch {}
    throw err;
  }
}
async function reconcileOnly(c) {
  // Fresh B connection, read only, never reissues an UNKNOWN mutation.
  const row = await c.query(
    'SELECT command_fingerprint,original_revision,result FROM ' + SCHEMA + '.receipts WHERE mutation_id=$1', [mutationId]
  );
  if (!row.rowCount) return { status: 'UNKNOWN_NO_RECEIPT' };
  assert.equal(row.rowCount, 1);
  assert.equal(row.rows[0].command_fingerprint, originalFingerprint, 'receipt fingerprint mismatch');
  assert.equal(Number(row.rows[0].original_revision), 1);
  assert.deepEqual(row.rows[0].result, originalResult);
  const v = await verify(c);
  return { status: 'CONFIRMED', result: v };
}
function passed(stage, fields) {
  const attrs = Object.entries(fields).map(([k, v]) => k + '=' + String(v)).join('|');
  console.log('PASS|R3|' + stage + '|' + attrs + '|external_physical_attestation=REQUIRED');
}
async function main() {
  if (phase === 'tls-negative') {
    // Actual negative test: same pinned TCP endpoint, deliberately incorrect SNI.
    const c = new Client({ ...options, ssl: { rejectUnauthorized: true, servername: 'incorrect-r3-host.invalid' } });
    try {
      await c.connect();
      throw new Error('NEGATIVE_TLS_UNEXPECTED_SUCCESS');
    } catch (err) {
      if (err.code !== 'ERR_TLS_CERT_ALTNAME_INVALID') throw new Error('NEGATIVE_TLS_NOT_PROVEN');
      passed('P09_TLS_NEGATIVE', { negative_hostname: 'CERT_ALTNAME_INVALID' });
    } finally { await c.end().catch(() => {}); }
    return;
  }
  const c = new Client(options);
  try {
    await c.connect();
    const server = await checkIdentity(c);
    if (phase === 'probe') {
      passed('P01', { host: TS_R3_HOST_LABEL, device_self_digest: selfDigest.slice(0, 16),
        role_digest: sha(server.principal).slice(0, 16), tls: server.tls_version, pg: 16 });
      return;
    }
    if (phase === 'write' || phase === 'write-drop-ack') {
      const r = await dispatch(c, baseCommand, true);
      assert.equal(r.status, 'CREATED', 'write must have fresh unique ID');
      if (phase === 'write-drop-ack') {
        // Controlled simulation only: client suppresses ACK after a successful COMMIT.
        console.log('UNKNOWN_CLIENT_ACK|R3|P04|synthetic_drop_after_commit=true|new_HOST_B_reconciliation_required=true');
        return;
      }
      const v = await verify(c);
      passed('P02', { host: 'HOST_A', revision: v.revision, effect: 1, receipt: 1,
        event_hash: v.event_hash.slice(0, 16) });
      return;
    }
    if (phase === 'recover') {
      const r = await reconcileOnly(c);
      if (r.status !== 'CONFIRMED') throw Object.assign(new Error('UNKNOWN'), { safeCode: 'UNKNOWN_NO_RECEIPT' });
      passed('P04_RECOVER', { host: 'HOST_B', effect: 1, receipt: 1, result: 'CONFIRMED' });
      return;
    }
    const before = await verify(c);
    if (phase === 'read') {
      passed('P03', { host: 'HOST_B', revision: before.revision, event_hash: before.event_hash.slice(0, 16),
        A_offline_evidence: 'REQUIRED' });
      return;
    }
    const mismatch = { ...baseCommand, authority_refs: ['AUTH-DIFFERENT'] };
    if (phase === 'collision') {
      let rejected = false;
      try { await dispatch(c, mismatch, false); } catch (err) {
        if (err.safeCode === 'KEY_COLLISION') rejected = true;
        else throw err;
      }
      assert(rejected, 'mismatched command must be rejected by actual handler');
    } else {
      const r = await dispatch(c, baseCommand, false);
      assert.equal(r.status, 'REPLAY');
      assert.deepEqual(r.result, originalResult);
    }
    const after = await verify(c);
    assert.deepEqual(after, before, 'replay/collision cannot change state or receipt');
    passed('P04', { host: 'HOST_B', mode: phase, effect: 1, receipt: 1,
      changed_authority: phase === 'collision' ? 'REJECTED' : 'NOT_REQUESTED' });
  } finally { await c.end().catch(() => {}); }
}
main().catch(err => {
  const code = err && err.safeCode === 'AMBIGUOUS_COMMIT_ACK' ? 'UNKNOWN_COMMIT_ACK'
    : err && err.safeCode === 'UNKNOWN_NO_RECEIPT' ? 'UNKNOWN_NO_RECEIPT' : 'FAIL';
  console.error(code + '|R3|' + phase + '|safe_error=true|no_secrets_logged=true');
  process.exitCode = code.startsWith('UNKNOWN') ? 2 : 1;
});
