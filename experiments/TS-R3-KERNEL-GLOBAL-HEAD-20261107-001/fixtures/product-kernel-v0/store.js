'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');
const { KINDS, KernelError, demand, validateBootstrapProvenance, validateState } = require('./contracts');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const serialize = value => `${JSON.stringify(value, null, 2)}\n`;
function syncDir(dir) { const fd = fs.openSync(dir, 'r'); try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); } }
function durableWrite(file, data) { const fd = fs.openSync(file, 'wx', 0o444); try { fs.writeFileSync(fd, data); fs.fsyncSync(fd); } finally { fs.closeSync(fd); } }
function parse(data, what) { try { return JSON.parse(data); } catch { throw new KernelError('MALFORMED_STATE', `${what} JSON`); } }
function emptyState() { return { schema_version: 'tecnotron-state-kernel/v0', revision: 0, aggregates: Object.fromEntries(KINDS.map(kind => [kind, {}])) }; }
class FilesystemStateStore {
  constructor(home, options = {}) {
    demand(typeof home === 'string' && path.isAbsolute(home), 'INVALID_CONTRACT', 'TECNOTRON_HOME must be an absolute configured path');
    this.home = path.resolve(home);
    this.root = path.join(this.home, 'state', 'kernel-v0');
    this.head = path.join(this.root, 'HEAD.json');
    this.lock = path.join(this.root, 'writer.lock');
    this.failpoint = options.failpoint;
  }
  withLock(fn) {
    fs.mkdirSync(this.root, { recursive: true });
    try { fs.mkdirSync(this.lock); } catch (error) {
      if (error.code === 'EEXIST') throw new KernelError('WRITER_LOCKED', 'writer lock exists; inspect before manual recovery');
      throw error;
    }
    try { return fn(); } finally { fs.rmdirSync(this.lock); }
  }
  initialize() {
    return this.withLock(() => {
      demand(!fs.existsSync(this.head) && fs.readdirSync(this.root).every(name => name === 'writer.lock'), 'INVALID_TRANSITION', 'state directory already initialized or contains uncommitted data');
      for (const directory of ['state', 'evidence', 'artifacts', 'workspaces', 'cache']) fs.mkdirSync(path.join(this.home, directory), { recursive: true });
      return this.commit(emptyState(), '', false);
    });
  }
  read() {
    if (!fs.existsSync(this.head)) throw new KernelError('MALFORMED_STATE', 'uninitialized or missing HEAD');
    const head = parse(fs.readFileSync(this.head, 'utf8'), 'HEAD');
    demand(head.schema_version === 'tecnotron-state-head/v0' && typeof head.generation === 'string' && /^[a-f0-9-]{36}$/.test(head.generation) && Number.isSafeInteger(head.revision) && /^[a-f0-9]{64}$/.test(head.state_sha256) && /^[a-f0-9]{64}$/.test(head.events_sha256), 'MALFORMED_STATE', 'HEAD fields');
    const dir = path.join(this.root, head.generation);
    let stateBytes, eventBytes;
    try { stateBytes = fs.readFileSync(path.join(dir, 'state.json'), 'utf8'); eventBytes = fs.readFileSync(path.join(dir, 'events.ndjson'), 'utf8'); }
    catch { throw new KernelError('MALFORMED_STATE', 'missing committed generation'); }
    demand(sha(stateBytes) === head.state_sha256 && sha(eventBytes) === head.events_sha256, 'MALFORMED_STATE', 'generation checksum mismatch');
    const state = parse(stateBytes, 'state');
    try { validateState(state); } catch (error) { throw new KernelError('MALFORMED_STATE', error.message); }
    demand(state.revision === head.revision, 'MALFORMED_STATE', 'snapshot/HEAD revision mismatch');
    const reconstructed = emptyState();
    let previousHash = null;
    const lines = eventBytes ? eventBytes.trimEnd().split('\n') : [];
    demand(lines.length === state.revision, 'MALFORMED_STATE', 'event count/revision mismatch');
    for (const line of lines) {
      const event = parse(line, 'event');
      const { hash, ...payload } = event;
      demand(hash === sha(JSON.stringify(payload)) && payload.previous_hash === previousHash && payload.sequence === reconstructed.revision + 1 && KINDS.includes(payload.kind), 'MALFORMED_STATE', 'event chain mismatch');
      if (payload.action === 'BOOTSTRAP_IMPORT') {
        demand(payload.kind === 'TaskCycle' && payload.before_revision === 0 && payload.bootstrap_provenance !== undefined, 'MALFORMED_STATE', 'bootstrap event shape');
        try { validateBootstrapProvenance(payload.bootstrap_provenance); } catch (error) { throw new KernelError('MALFORMED_STATE', error.message); }
        demand(payload.after?.created_at === payload.bootstrap_provenance.cutover_at && payload.after?.updated_at === payload.bootstrap_provenance.cutover_at, 'MALFORMED_STATE', 'bootstrap cutover correspondence');
        demand(isDeepStrictEqual(payload.after?.authority_refs, payload.bootstrap_provenance.authority_refs), 'MALFORMED_STATE', 'bootstrap authority correspondence');
        demand(payload.after?.terminal_disposition_ref === null && !['CLOSED', 'CANCELLED'].includes(payload.after?.state), 'MALFORMED_STATE', 'bootstrap must be nonterminal');
      } else {
        demand(payload.bootstrap_provenance === undefined, 'MALFORMED_STATE', 'bootstrap provenance on non-bootstrap event');
      }
      const prior = reconstructed.aggregates[payload.kind][payload.aggregate_id];
      demand((prior?.revision ?? 0) === payload.before_revision && payload.after?.id === payload.aggregate_id && payload.after?.kind === payload.kind && payload.after.revision === payload.before_revision + 1 && payload.after.last_event_id === payload.id, 'MALFORMED_STATE', 'event correspondence mismatch');
      reconstructed.aggregates[payload.kind][payload.aggregate_id] = payload.after;
      reconstructed.revision++;
      previousHash = hash;
    }
    demand(isDeepStrictEqual(reconstructed, state), 'MALFORMED_STATE', 'snapshot does not correspond to committed events');
    return { state, events: lines.map(line => JSON.parse(line)), eventBytes };
  }
  commit(state, eventBytes, useFailpoint = true) {
    const generation = crypto.randomUUID();
    const dir = path.join(this.root, generation);
    fs.mkdirSync(dir);
    let published = false;
    const tempHead = path.join(this.root, `HEAD.${generation}.tmp`);
    try {
      const stateBytes = serialize(state);
      durableWrite(path.join(dir, 'state.json'), stateBytes);
      durableWrite(path.join(dir, 'events.ndjson'), eventBytes);
      syncDir(dir);
      const head = { schema_version: 'tecnotron-state-head/v0', generation, revision: state.revision, state_sha256: sha(stateBytes), events_sha256: sha(eventBytes) };
      durableWrite(tempHead, serialize(head));
      if (useFailpoint && this.failpoint === 'BEFORE_HEAD_REPLACE') throw new KernelError('INJECTED_FAILURE', 'before atomic HEAD replace');
      fs.renameSync(tempHead, this.head);
      published = true;
      try { syncDir(this.root); } catch { throw new KernelError('UNKNOWN_EFFECT_REQUIRES_RECONCILIATION', 'HEAD replacement occurred but directory sync did not complete'); }
      return head;
    } finally {
      if (!published) {
        if (fs.existsSync(tempHead)) fs.unlinkSync(tempHead);
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  }
  mutate(expectedRevision, change) {
    return this.withLock(() => {
      const { state, events, eventBytes } = this.read();
      demand(Number.isSafeInteger(expectedRevision) && expectedRevision === state.revision, 'STALE_REVISION', `expected ${expectedRevision}, observed ${state.revision}`);
      const proposed = structuredClone(state);
      const update = change(proposed);
      demand(update && KINDS.includes(update.kind) && typeof update.id === 'string', 'INVALID_CONTRACT', 'mutation target');
      for (const kind of KINDS) for (const [id, previous] of Object.entries(state.aggregates[kind])) {
        if (kind !== update.kind || id !== update.id) demand(isDeepStrictEqual(previous, proposed.aggregates[kind][id]), 'INVALID_CONTRACT', 'mutation changed another aggregate');
      }
      for (const kind of KINDS) for (const id of Object.keys(proposed.aggregates[kind])) {
        if (kind !== update.kind || id !== update.id) demand(Object.hasOwn(state.aggregates[kind], id), 'INVALID_CONTRACT', 'mutation created another aggregate');
      }
      const before = state.aggregates[update.kind][update.id];
      const after = proposed.aggregates[update.kind][update.id];
      demand(after && after.revision === (before?.revision ?? 0) + 1, 'INVALID_CONTRACT', 'aggregate revision must increment once');
      proposed.revision++;
      const id = `event-${proposed.revision}`;
      after.last_event_id = id;
      validateState(proposed);
      const previous_hash = events.length ? events.at(-1).hash : null;
      demand((update.action === 'BOOTSTRAP_IMPORT') === (update.bootstrap_provenance !== undefined), 'INVALID_CONTRACT', 'bootstrap provenance/action correspondence');
      if (update.bootstrap_provenance !== undefined) validateBootstrapProvenance(update.bootstrap_provenance);
      const payload = { id, sequence: proposed.revision, kind: update.kind, aggregate_id: update.id, before_revision: before?.revision ?? 0, after, previous_hash, at: update.at, action: update.action };
      if (update.bootstrap_provenance !== undefined) payload.bootstrap_provenance = update.bootstrap_provenance;
      const event = { ...payload, hash: sha(JSON.stringify(payload)) };
      const head = this.commit(proposed, `${eventBytes}${JSON.stringify(event)}\n`);
      return { revision: head.revision, event_id: id, event_hash: event.hash, kind: update.kind, aggregate_id: update.id, aggregate_revision: after.revision };
    });
  }
  verify() { const { state, events } = this.read(); return { valid: true, revision: state.revision, event_count: events.length }; }
}
module.exports = { FilesystemStateStore, emptyState };
