'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const work = process.argv[2];
const snapshot = process.argv[3];
const events = process.argv[4];
assert(work && path.isAbsolute(work));
assert(snapshot && events && path.isAbsolute(snapshot) && path.isAbsolute(events));
assert(snapshot.startsWith(work + path.sep) && events.startsWith(work + path.sep));
const { FilesystemStateStore } = require(path.join(work, 'store.js'));
const home = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-d7-restore-'));
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
try {
  const root = path.join(home, 'state', 'kernel-v0');
  const generation = crypto.randomUUID();
  const directory = path.join(root, generation);
  fs.mkdirSync(directory, { recursive: true });
  const stateBytes = fs.readFileSync(snapshot);
  const eventBytes = fs.readFileSync(events);
  assert.equal(stateBytes.at(-1), 10);
  assert.equal(eventBytes.at(-1), 10);
  fs.writeFileSync(path.join(directory, 'state.json'), stateBytes, { flag: 'wx' });
  fs.writeFileSync(path.join(directory, 'events.ndjson'), eventBytes, { flag: 'wx' });
  const state = JSON.parse(stateBytes.toString('utf8'));
  const head = {
    schema_version: 'tecnotron-state-head/v0', generation,
    revision: state.revision,
    state_sha256: hash(stateBytes), events_sha256: hash(eventBytes),
  };
  fs.writeFileSync(path.join(root, 'HEAD.json'), JSON.stringify(head, null, 2) + '\n', { flag: 'wx' });
  const store = new FilesystemStateStore(home);
  const result = store.verify();
  assert.deepEqual(result, { valid: true, revision: 19, event_count: 19 });
  const read = store.read();
  assert.equal(hash(Buffer.from(JSON.stringify(read.state, null, 2) + '\n')), hash(stateBytes));
  assert.equal(hash(read.eventBytes), hash(eventBytes));
  process.stdout.write(JSON.stringify({status: 'D7_PRODUCT_JS_ORACLE_RESTORED_PASS', revision: 19,
    events: 19, state_sha256: hash(stateBytes), events_sha256: hash(eventBytes),
    product_effect: 'NONE'}) + '\n');
} finally {
  fs.rmSync(home, { recursive: true, force: true });
}
