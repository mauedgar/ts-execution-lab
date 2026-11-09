'use strict';
// A02-LAN NONPRODUCT. Generate two exact competing Product-JS event proposals.
// No SQL, no credentials, no Product change. Output is an immutable artifact.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const fixture = path.resolve(process.env.TS_R3_A02_PRODUCT_FIXTURE_DIR || '');
assertPrivateTempPath(fixture, true);
const api = require(path.join(fixture, 'index.js'));
const {ShadowAsyncAdapter, snapshotBytes} =
  require('../a10_lc_core_semantics/shadow_async_adapter.cjs');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
function assertPrivateTempPath(candidate, existingDirectory) {
  const dest = path.resolve(candidate);
  const roots = [os.tmpdir(), process.env.RUNNER_TEMP]
    .filter(value => typeof value === 'string' && path.isAbsolute(value))
    .map(value => path.resolve(value))
    .filter(value => value !== path.parse(value).root);
  const root = roots.find(value => dest.startsWith(value + path.sep));
  assert.ok(root, 'EXACT_TEMP_ROOT_REQUIRED');
  assert.equal(fs.realpathSync.native(root), root, 'TEMP_ROOT_SYMLINK_FORBIDDEN');
  const parts = path.relative(root, dest).split(path.sep);
  assert.ok(parts.length >= 2, 'PRIVATE_SUBDIRECTORY_REQUIRED');
  const privateBase = path.join(root, parts[0]);
  const baseMeta = fs.lstatSync(privateBase);
  assert.ok(baseMeta.isDirectory() && !baseMeta.isSymbolicLink(),
    'PRIVATE_BASE_DIRECTORY_REQUIRED');
  if (typeof process.getuid === 'function') {
    assert.equal(baseMeta.uid, process.getuid(), 'PRIVATE_DIR_OWNER_REQUIRED');
    assert.equal(baseMeta.mode & 0o077, 0, 'PRIVATE_DIR_MODE_0700_REQUIRED');
  }
  let ancestor = privateBase;
  for (const part of parts.slice(1, -1)) {
    ancestor = path.join(ancestor, part);
    const meta = fs.lstatSync(ancestor);
    assert.ok(meta.isDirectory() && !meta.isSymbolicLink(),
      'INTERMEDIATE_SYMLINK_FORBIDDEN');
  }
  if (existingDirectory) {
    const meta = fs.lstatSync(dest);
    assert.ok(meta.isDirectory() && !meta.isSymbolicLink(),
      'FIXTURE_REAL_DIRECTORY_REQUIRED');
  } else {
    assert.ok(!fs.existsSync(dest), 'CREATE_ONLY_DESTINATION_REQUIRED');
  }
  return dest;
}
const SCOPE = 'A10-DISPOSABLE-SINGLE-SCOPE';
const SCHEMA = 'TS_R3_A02_LAN_PROPOSALS_V1';
const auth = [{kind:'AUTHORITY', id:'A02-LAN-SYNTHETIC-NONPRODUCT-ONLY'}];

assert.equal(process.argv.length, 3, 'one artifact path required');
const destination = path.resolve(process.argv[2]);
assertPrivateTempPath(destination, false);
assert.ok(!fs.existsSync(destination), 'CREATE_ONLY');
assert.ok(!process.env.TS_R3_NEON_CHILD_DSN && !process.env.TS_R3_NEON_CHILD_RO_DSN &&
  !process.env.DATABASE_URL && !process.env.PGPASSWORD);
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-a02-lan-gen-'));
try {
  const genesisDir = path.join(root, 'genesis');
  fs.mkdirSync(genesisDir);
  const store = new api.FilesystemStateStore(genesisDir);
  store.initialize();
  const genesis = snapshotBytes(store);
  assert.equal(genesis.revision, 0);
  assert.equal(genesis.eventBytes.length, 0);
  const observed = {revision:0, epoch:1,
    stateBytes:genesis.stateBytes, eventBytes:genesis.eventBytes};
  const adapter = new ShadowAsyncAdapter(api, root, {});
  const make = (writer, title) =>
    adapter.propose(observed, 'A10-A02-LAN-' + writer,
      (domain, storage, revision) =>
        domain.create(storage, revision, 'Milestone', 'MS-A02-LAN-' + writer,
          {title}, auth));
  const a = make('A', 'PHYSICAL-HOST-A');
  const b = make('B', 'PHYSICAL-HOST-B');
  assert.equal(a.scope, SCOPE);
  assert.equal(b.scope, SCOPE);
  assert.equal(a.expectedRevision, 0);
  assert.equal(b.expectedRevision, 0);
  assert.equal(a.previousEventHash, null);
  assert.equal(b.previousEventHash, null);
  assert.notEqual(a.eventHash, b.eventHash);
  assert.notEqual(a.mutationId, b.mutationId);
  const encode = p => ({
    scope:p.scope,
    mutationId:p.mutationId,
    fingerprint:p.fingerprint,
    expectedRevision:p.expectedRevision,
    expectedEpoch:p.expectedEpoch,
    previousEventHash:p.previousEventHash,
    eventHash:p.eventHash,
    stateBytes:p.stateBytes.toString('base64'),
    eventLine:p.eventLine.toString('base64'),
    stateSha256:sha(p.stateBytes),
    eventLineSha256:sha(p.eventLine),
  });
  const packet = {
    schema:SCHEMA,
    scope:SCOPE,
    source:'FROZEN_ORIGINAL_PRODUCT_V0_JS_VIA_A10_SHADOW',
    product_effect:'NONE',
    expected_revision_before:0,
    expected_revision_after:1,
    genesis_state:genesis.stateBytes.toString('base64'),
    genesis_sha256:sha(genesis.stateBytes),
    a:encode(a),
    b:encode(b),
  };
  const bytes = Buffer.from(JSON.stringify(packet)+'\n', 'utf8');
  assert.ok(bytes.length > 300 && bytes.length < 6*1024*1024);
  fs.writeFileSync(destination, bytes, {flag:'wx', mode:0o600});
  console.log(JSON.stringify({
    status:'A02_LAN_ORIGINAL_JS_COMPETING_PROPOSALS_PASS',
    file_bytes:bytes.length,
    file_sha256:sha(bytes),
    genesis_sha256:packet.genesis_sha256,
    competing_proposals:2, product_effect:'NONE',
    database:'NOT_RUN', neon:'NOT_RUN',
  }));
} finally {
  fs.rmSync(root, {recursive:true, force:true});
}
