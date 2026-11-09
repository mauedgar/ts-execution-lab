'use strict';
// NONPRODUCT EXPERIMENT ONLY. Original Product JavaScript runs the semantic mutation;
// this temporary shadow uses disposable FS to obtain its canonical bytes. NOT a
// production driver, not a second lifecycle, not a source of Product authority.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const copy = value => Buffer.from(value);
const SHADOW_SCOPE = 'A10-DISPOSABLE-SINGLE-SCOPE';
function fingerprint(p) {
  // Bind all identity/commit dimensions, including the exact bytes.
  return sha([
    p.scope, p.mutationId, String(p.expectedRevision), String(p.expectedEpoch),
    p.previousEventHash ?? '<GENESIS>', p.eventHash, sha(p.stateBytes), sha(p.eventLine),
  ].join('\\0'));
}

function restoreSingleGeneration(api, home, observed) {
  const store = new api.FilesystemStateStore(home);
  fs.mkdirSync(store.root, {recursive: true});
  const generation = crypto.randomUUID();
  const dir = path.join(store.root, generation);
  fs.mkdirSync(dir);
  fs.writeFileSync(path.join(dir, 'state.json'), observed.stateBytes, {flag: 'wx'});
  fs.writeFileSync(path.join(dir, 'events.ndjson'), observed.eventBytes, {flag: 'wx'});
  const head = {
    schema_version: 'tecnotron-state-head/v0',
    generation,
    revision: observed.revision,
    state_sha256: sha(observed.stateBytes),
    events_sha256: sha(observed.eventBytes),
  };
  fs.writeFileSync(store.head, JSON.stringify(head, null, 2) + '\n', {flag: 'wx'});
  assert.equal(store.verify().revision, observed.revision, 'source JS reader must validate');
  return store;
}
function snapshotBytes(store) {
  const head = JSON.parse(fs.readFileSync(store.head, 'utf8'));
  const dir = path.join(store.root, head.generation);
  return {
    revision: head.revision,
    stateBytes: fs.readFileSync(path.join(dir, 'state.json')),
    eventBytes: fs.readFileSync(path.join(dir, 'events.ndjson')),
  };
}
class ShadowAsyncAdapter {
  constructor(api, root, port) {
    this.api = api;
    this.root = root;
    this.port = port;
    this.pendingUnknown = null;
    this.inflight = false;
    this.proposalNumber = 0;
  }
  async observe() { return await this.port.read(); }
  propose(observed, mutationId, originalJsCall) {
    assert.equal(this.pendingUnknown, null, 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
    assert.equal(this.inflight, false, 'INFLIGHT_OPERATION_BLOCKED');
    assert.match(mutationId, /^A10-[A-Z0-9-]+$/);
    const work = path.join(this.root, 'proposal-' + (++this.proposalNumber));
    fs.mkdirSync(work, {recursive: false});
    try {
      const store = restoreSingleGeneration(this.api, work, observed);
      const before = snapshotBytes(store);
      assert.equal(before.revision, observed.revision);
      originalJsCall(this.api, store, observed.revision);
      const after = snapshotBytes(store);
      assert.equal(after.revision, observed.revision + 1, 'one original JS event per proposal');
      assert.ok(after.eventBytes.subarray(0, before.eventBytes.length).equals(before.eventBytes),
        'append-only event stream must preserve previous exact bytes');
      const line = after.eventBytes.subarray(before.eventBytes.length);
      assert.ok(line.length > 0 && line[line.length - 1] === 10, 'exact newline event');
      const parsed = JSON.parse(line.toString('utf8'));
      const originalLast = before.eventBytes.length > 0
        ? JSON.parse(before.eventBytes.toString('utf8').trimEnd().split('\n').at(-1)).hash : null;
      assert.equal(parsed.previous_hash, originalLast);
      assert.equal(parsed.sequence, after.revision);
      const fields = {
        scope: SHADOW_SCOPE,
        mutationId,
        expectedRevision: observed.revision,
        expectedEpoch: observed.epoch,
        previousEventHash: originalLast,
        eventHash: parsed.hash,
        stateBytes: copy(after.stateBytes),
        eventLine: copy(line),
      };
      return Object.freeze({...fields, fingerprint: fingerprint(fields)});
    } finally {
      fs.rmSync(work, {recursive: true, force: true});
    }
  }
  async commit(proposal) {
    if (this.pendingUnknown !== null)
      return {disposition: 'BLOCKED_UNRECONCILED', effect: 'UNKNOWN'};
    if (this.inflight)
      return {disposition: 'BLOCKED_INFLIGHT', effect: 'NONE'};
    this.inflight = true;
    try {
      return await this.port.apply(proposal);
    } catch (_error) {
      // Every post-dispatch exception conservatively preserves original attempt.
      this.pendingUnknown = proposal;
      return {disposition: 'UNKNOWN_FENCED', effect: 'UNKNOWN'};
    } finally {
      this.inflight = false;
    }
  }
  async reconcile() {
    assert.ok(this.pendingUnknown !== null, 'NO_UNCERTAIN_ATTEMPT');
    if (this.inflight)
      return {disposition: 'BLOCKED_INFLIGHT', effect: 'UNKNOWN'};
    this.inflight = true;
    const original = this.pendingUnknown;
    try {
      const result = await this.port.reconcile(original);
      if (result.disposition === 'CONFIRMED' &&
          result.mutationId === original.mutationId &&
          result.scope === original.scope &&
          result.fingerprint === original.fingerprint &&
          result.eventHash === original.eventHash &&
          result.revision === original.expectedRevision + 1 &&
          result.expectedEpoch === original.expectedEpoch &&
          result.stateSha256 === sha(original.stateBytes) &&
          result.eventLineSha256 === sha(original.eventLine)) {
        this.pendingUnknown = null;
        return result;
      }
      return {disposition: 'UNKNOWN_FENCED', effect: 'UNKNOWN'};
    } catch (_error) {
      return {disposition: 'UNKNOWN_FENCED', effect: 'UNKNOWN'};
    } finally {
      this.inflight = false;
    }
  }
}

// In-memory fake port is TEST SUPPORT ONLY, not a persistent backend or
// certified substitute for PostgreSQL transaction/lock/receipt semantics.
class DisposableFakeCasPort {
  constructor(initial) {
    this.stateBytes = copy(initial.stateBytes);
    this.eventBytes = copy(initial.eventBytes);
    this.revision = initial.revision;
    this.epoch = 1;
    this.receipts = new Map();
    this.commitCount = 0;
    this.dropResponseOnce = false;
  }
  async read() {
    return {
      revision: this.revision, epoch: this.epoch,
      stateBytes: copy(this.stateBytes), eventBytes: copy(this.eventBytes),
    };
  }
  async apply(p) {
    assert.equal(p.scope, SHADOW_SCOPE, 'ISOLATED_SCOPE_REQUIRED');
    assert.equal(p.fingerprint, fingerprint(p), 'REQUEST_FINGERPRINT_INVALID');
    if (p.expectedEpoch !== this.epoch) return {disposition: 'NONE_FENCED', effect: 'NONE'};
    if (p.expectedRevision !== this.revision) return {disposition: 'NONE_STALE', effect: 'NONE'};
    assert.ok(!this.receipts.has(p.mutationId), 'DUPLICATE_ATTEMPT_NOT_REISSUED');
    const originalLast = this.eventBytes.length > 0
      ? JSON.parse(this.eventBytes.toString('utf8').trimEnd().split('\n').at(-1)).hash : null;
    assert.equal(p.previousEventHash, originalLast, 'previous event chain');
    const event = JSON.parse(p.eventLine.toString('utf8'));
    assert.equal(event.previous_hash, originalLast);
    assert.equal(event.hash, p.eventHash);
    assert.equal(event.sequence, this.revision + 1);
    const state = JSON.parse(p.stateBytes.toString('utf8'));
    assert.equal(state.revision, this.revision + 1);
    this.revision++;
    this.eventBytes = Buffer.concat([this.eventBytes, p.eventLine]);
    this.stateBytes = copy(p.stateBytes);
    this.commitCount++;
    const receipt = Object.freeze({
      disposition: 'CONFIRMED', effect: 'CONFIRMED',
      scope: p.scope, mutationId: p.mutationId,
      fingerprint: p.fingerprint, expectedEpoch: p.expectedEpoch,
      revision: this.revision, eventHash: p.eventHash,
      stateSha256: sha(p.stateBytes), eventLineSha256: sha(p.eventLine),
    });
    this.receipts.set(p.mutationId, receipt);
    if (this.dropResponseOnce) {
      this.dropResponseOnce = false;
      throw new Error('SYNTHETIC_POST_COMMIT_RESPONSE_LOSS');
    }
    return receipt;
  }
  async reconcile(p) {
    // Read-only original-ID receipt lookup; a missing receipt is UNKNOWN.
    return this.receipts.get(p.mutationId) || {disposition: 'UNKNOWN_FENCED', effect: 'UNKNOWN'};
  }
}
module.exports = {ShadowAsyncAdapter, DisposableFakeCasPort, snapshotBytes};
