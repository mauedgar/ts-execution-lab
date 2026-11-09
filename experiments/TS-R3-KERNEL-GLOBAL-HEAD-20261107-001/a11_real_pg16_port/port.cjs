'use strict';
// A11 disposable PostgreSQL16 storage port, NONPRODUCT. No Product authority.
// Calls existing Python/psycopg bridge through a bounded one-message JSON IPC.
// Uses only an exact synthetic local URI, never Neon or a real user database.
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const path = require('node:path');
const crypto = require('node:crypto');
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const ROOT = path.resolve(__dirname, '..');
const SCOPE = 'A10-DISPOSABLE-SINGLE-SCOPE';

class RealPg16DisposablePort {
  constructor(python) {
    assert.equal(typeof python, 'string');
    assert.ok(path.isAbsolute(python), 'pin absolute Python executable');
    this.python = python;
    this.simulateLostReplyOnce = false;
  }
  async call(body) {
    assert.ok(!process.env.TS_R3_NEON_CHILD_DSN, 'NEON_SECRET_FORBIDDEN');
    assert.ok(!process.env.DATABASE_URL, 'OTHER_DB_FORBIDDEN');
    assert.ok(!process.env.PGPASSWORD, 'UNEXPECTED_PASSWORD_ENV');
    const message = JSON.stringify({...body, scope: SCOPE});
    assert.ok(Buffer.byteLength(message) <= 6 * 1024 * 1024, 'OVERSIZED_MESSAGE');
    const worker = path.join(__dirname, 'worker.py');
    const args = ['-B', worker];
    return await new Promise((resolve, reject) => {
      const child = spawn(this.python, args, {
        cwd: ROOT,
        env: {
          PATH: process.env.PATH || '',
          HOME: process.env.HOME || '',
          TS_R3_LOCAL_SYNTHETIC_PG_URI: process.env.TS_R3_LOCAL_SYNTHETIC_PG_URI || '',
          PYTHONDONTWRITEBYTECODE: '1',
        },
        stdio: ['pipe', 'pipe', 'pipe'],
      });
      const stdout = [], stderr = [];
      let total = 0, timedOut = false;
      const deadline = setTimeout(() => {
        timedOut = true;
        child.kill();
      }, 15000);
      function collect(target, chunk) {
        total += chunk.length;
        if (total > 7 * 1024 * 1024) {
          timedOut = true;
          child.kill();
        } else target.push(chunk);
      }
      child.stdout.on('data', chunk => collect(stdout, chunk));
      child.stderr.on('data', chunk => collect(stderr, chunk));
      child.on('error', () => { /* classified on close */ });
      child.on('close', code => {
        clearTimeout(deadline);
        if (timedOut || code !== 0) {
          // Deliberately do NOT include stderr, argv or environment in errors.
          reject(new Error('A11_LOCAL_PORT_RESPONSE_UNAVAILABLE'));
          return;
        }
        try {
          const line = Buffer.concat(stdout).toString('utf8');
          assert.ok(line.length > 0 && line.length < 7 * 1024 * 1024);
          resolve(JSON.parse(line));
        } catch (_error) {
          reject(new Error('A11_LOCAL_PORT_MALFORMED_RESPONSE'));
        }
      });
      child.stdin.end(message);
    });
  }
  proposalWire(p) {
    assert.equal(p.scope, SCOPE);
    assert.match(p.fingerprint, /^[a-f0-9]{64}$/);
    return {
      scope: p.scope, mutationId: p.mutationId,
      fingerprint: p.fingerprint,
      expectedRevision: p.expectedRevision,
      expectedEpoch: p.expectedEpoch,
      previousEventHash: p.previousEventHash,
      eventHash: p.eventHash,
      stateBytes: p.stateBytes.toString('base64'),
      eventLine: p.eventLine.toString('base64'),
    };
  }
  async initialize(stateBytes) {
    return this.call({op: 'init', stateBytes: stateBytes.toString('base64')});
  }
  async read() {
    const result = await this.call({op: 'read'});
    const stateBytes = Buffer.from(result.stateBytes, 'base64');
    const eventBytes = Buffer.from(result.eventBytes, 'base64');
    assert.equal(hash(stateBytes), result.stateSha256);
    assert.equal(hash(eventBytes), result.eventsSha256);
    return {
      revision: result.revision, epoch: result.epoch, stateBytes, eventBytes,
    };
  }
  async apply(p) {
    const simulate_lost_reply = this.simulateLostReplyOnce;
    this.simulateLostReplyOnce = false;
    return this.call({
      op: 'apply', proposal: this.proposalWire(p), simulate_lost_reply,
    });
  }
  async reconcile(p) {
    return this.call({op: 'reconcile', proposal: this.proposalWire(p)});
  }
  async counts() {
    return this.call({op: 'counts'});
  }
}
module.exports = {RealPg16DisposablePort};
