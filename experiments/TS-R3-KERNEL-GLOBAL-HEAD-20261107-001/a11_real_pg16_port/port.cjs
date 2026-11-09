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

class BoundedPortError extends Error {
  constructor(code, stage) {
    super(code);
    this.name = 'BoundedPortError';
    this.code = code; // bounded constants only, never stderr or raw process errors
    this.stage = stage; // PRE_DISPATCH or POSSIBLE_DISPATCH
  }
}
class RealPg16DisposablePort {
  constructor(python, options = {}) {
    assert.equal(typeof python, 'string');
    assert.ok(path.isAbsolute(python), 'pin absolute Python executable');
    const fault = options.fault ?? null;
    assert.ok([null, 'MALFORMED', 'EXIT', 'TIMEOUT'].includes(fault),
      'TEST_FAULT_MODE_NOT_ALLOWED');
    if (fault !== null) {
      assert.equal(process.env.TS_R3_A11_SYNTHETIC_FAULTS, '1',
        'SYNTHETIC_FAULT_ADMISSION_REQUIRED');
    }
    const deadlineMs = options.timeoutMs ?? 15000;
    assert.ok(Number.isSafeInteger(deadlineMs) && deadlineMs >= 100 &&
      deadlineMs <= 15000, 'BOUNDED_TIMEOUT_REQUIRED');
    this.python = python;
    this.timeoutMs = deadlineMs;
    this.fault = fault;
    this.simulateLostReplyOnce = false;
  }
  async call(body) {
    assert.ok(!process.env.TS_R3_NEON_CHILD_DSN, 'NEON_SECRET_FORBIDDEN');
    assert.ok(!process.env.DATABASE_URL, 'OTHER_DB_FORBIDDEN');
    assert.ok(!process.env.PGPASSWORD, 'UNEXPECTED_PASSWORD_ENV');
    const message = JSON.stringify({...body, scope: SCOPE});
    assert.ok(Buffer.byteLength(message) <= 6 * 1024 * 1024, 'OVERSIZED_MESSAGE');
    const worker = path.join(__dirname, this.fault ? 'fault_worker.py' : 'worker.py');
    const args = ['-B', worker, ...(this.fault ? [this.fault] : [])];
    return await new Promise((resolve, reject) => {
      const child = spawn(this.python, args, {
        cwd: ROOT,
        env: {
          PATH: process.env.PATH || '',
          HOME: process.env.HOME || '',
          TS_R3_LOCAL_SYNTHETIC_PG_URI: process.env.TS_R3_LOCAL_SYNTHETIC_PG_URI || '',
          PYTHONDONTWRITEBYTECODE: '1',
          ...(this.fault ? {TS_R3_A11_SYNTHETIC_FAULTS: '1'} : {}),
        },
        stdio: ['pipe', 'pipe', 'pipe'],
      });
      const stdout = [];
      let total = 0, timedOut = false, overflow = false, spawnError = false;
      const deadline = setTimeout(() => {
        timedOut = true;
        child.kill();
      }, this.timeoutMs);
      function collect(chunk, asOutput) {
        total += chunk.length;
        if (total > 7 * 1024 * 1024) {
          overflow = true;
          child.kill();
        } else if (asOutput) stdout.push(chunk);
        // stderr is counted but never stored or surfaced.
      }
      child.stdout.on('data', chunk => collect(chunk, true));
      child.stderr.on('data', chunk => collect(chunk, false));
      child.on('error', () => { spawnError = true; });
      child.stdin.on('error', () => { /* already classified by close */ });
      child.on('close', code => {
        clearTimeout(deadline);
        const stage = child.pid === undefined ? 'PRE_DISPATCH' : 'POSSIBLE_DISPATCH';
        if (spawnError && stage === 'PRE_DISPATCH') {
          reject(new BoundedPortError('A11_IPC_SPAWN_FAILED', stage));
          return;
        }
        if (timedOut) {
          reject(new BoundedPortError('A11_IPC_TIMEOUT', stage));
          return;
        }
        if (overflow) {
          reject(new BoundedPortError('A11_IPC_OUTPUT_LIMIT', stage));
          return;
        }
        if (code !== 0 || spawnError) {
          reject(new BoundedPortError('A11_IPC_EXIT_UNCERTAIN', stage));
          return;
        }
        try {
          const line = Buffer.concat(stdout).toString('utf8');
          assert.ok(line.length > 0 && line.length < 7 * 1024 * 1024);
          const result = JSON.parse(line);
          assert.ok(result && typeof result === 'object' && !Array.isArray(result));
          resolve(result);
        } catch (_error) {
          reject(new BoundedPortError('A11_IPC_MALFORMED_RESPONSE', stage));
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
module.exports = {RealPg16DisposablePort, BoundedPortError};
