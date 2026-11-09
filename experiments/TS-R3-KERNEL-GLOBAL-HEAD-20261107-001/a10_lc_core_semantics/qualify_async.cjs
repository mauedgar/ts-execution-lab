'use strict';
// A10 NONPRODUCT, no Neon/SQL. Runs original JS Product domain semantics in
// disposable shadow generations, verifies asynchronous CAS/UNKNOWN boundaries
// against a deliberately labelled fake storage port, never Product writes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {ShadowAsyncAdapter, DisposableFakeCasPort, snapshotBytes} =
  require('./shadow_async_adapter.cjs');
assert.equal(process.argv.length, 4, 'original JS fixture and disposable root');
const source = path.resolve(process.argv[2]), scratch = path.resolve(process.argv[3]);
assert.ok(scratch.startsWith(path.join(os.tmpdir(), 'ts-r3-a10-')));
const api = require(path.join(source, 'index.js'));
const authority = [{kind: 'AUTHORITY', id: 'A10-DESIGN-ONLY'}];

async function main() {
  const home = path.join(scratch, 'async-genesis');
  fs.mkdirSync(home, {recursive: false});
  let initial;
  try {
    const seed = new api.FilesystemStateStore(home);
    seed.initialize();
    initial = snapshotBytes(seed);
    assert.equal(seed.verify().revision, 0);
  } finally {
    fs.rmSync(home, {recursive: true, force: true});
  }
  const port = new DisposableFakeCasPort(initial);
  const adapter = new ShadowAsyncAdapter(api, scratch, port);

  const baseline = await adapter.observe();
  const winner = adapter.propose(baseline, 'A10-WRITER-1',
    (domain, store, revision) => domain.create(
      store, revision, 'TaskCycle', 'TC-A10-ASYNC',
      {responsibility: 'REMOTE-STORAGE-CANDIDATE', obligations: [{id: 'DONE', authority_ref: null}]},
      authority,
    ));
  const loser = adapter.propose(baseline, 'A10-WRITER-2',
    (domain, store, revision) => domain.create(store, revision, 'Milestone',
      'MS-A10-STALE', {title: 'STALE SHOULD NOT PERSIST'}, authority));
  const a = await adapter.commit(winner);
  assert.equal(a.disposition, 'CONFIRMED');
  assert.equal(a.revision, 1);
  const b = await adapter.commit(loser);
  assert.equal(b.disposition, 'NONE_STALE');
  assert.equal(port.commitCount, 1);
  assert.equal((await adapter.observe()).revision, 1);
  assert.equal(JSON.parse(port.stateBytes.toString('utf8'))
    .aggregates.Milestone['MS-A10-STALE'], undefined);

  const active = await adapter.observe();
  const lostReply = adapter.propose(active, 'A10-WRITER-3',
    (domain, store, revision) =>
      domain.transition(store, revision, 'TaskCycle', 'TC-A10-ASYNC', 'ACTIVE'));
  port.dropResponseOnce = true;
  const unknown = await adapter.commit(lostReply);
  assert.equal(unknown.disposition, 'UNKNOWN_FENCED');
  assert.equal(port.commitCount, 2, 'backend committed once before response loss');
  assert.throws(() => adapter.propose(active, 'A10-WRITER-FORBIDDEN',
    (domain, store, revision) => domain.create(store, revision, 'Milestone',
      'MS-A10-FORBIDDEN', {title: 'NO AUTO RETRY'}, authority)),
    /UNKNOWN_EFFECT_REQUIRES_RECONCILIATION/);
  const fenced = await adapter.commit(loser);
  assert.equal(fenced.disposition, 'BLOCKED_UNRECONCILED');
  assert.equal(port.commitCount, 2);
  // A03: an incorrectly attributed receipt MUST NOT clear the UNKNOWN fence.
  const originalReceipt = port.receipts.get(lostReply.mutationId);
  assert.ok(originalReceipt && originalReceipt.fingerprint === lostReply.fingerprint);
  const receiptFaults = [
    {mutationId: 'A10-WRONG-MUTATION'},
    {scope: 'A10-WRONG-SCOPE'},
    {fingerprint: '0'.repeat(64)},
    {expectedEpoch: originalReceipt.expectedEpoch + 1},
    {revision: originalReceipt.revision + 1},
    {eventHash: '0'.repeat(64)},
    {stateSha256: '0'.repeat(64)},
    {eventLineSha256: '0'.repeat(64)},
  ];
  for (const bad of receiptFaults) {
    port.receipts.set(lostReply.mutationId, {...originalReceipt, ...bad});
    const forged = await adapter.reconcile();
    assert.equal(forged.disposition, 'UNKNOWN_FENCED');
    assert.equal(adapter.pendingUnknown.mutationId, lostReply.mutationId);
    assert.equal(port.commitCount, 2, 'mismatched receipt must not cause redispatch');
  }
  port.receipts.set(lostReply.mutationId, originalReceipt);
  const joined = await adapter.reconcile();
  assert.equal(joined.disposition, 'CONFIRMED');
  assert.equal(joined.mutationId, 'A10-WRITER-3');
  assert.equal(joined.revision, 2);
  assert.equal(port.receipts.size, 2, 'no duplicate commit on reconciliation');

  const beforeCutover = await adapter.observe();
  const oldWriter = adapter.propose(beforeCutover, 'A10-WRITER-4',
    (domain, store, revision) =>
      domain.satisfy(store, revision, 'TC-A10-ASYNC', 'DONE'));
  port.epoch++;
  const oldResult = await adapter.commit(oldWriter);
  assert.equal(oldResult.disposition, 'NONE_FENCED');
  assert.equal(port.commitCount, 2);
  assert.equal(port.revision, 2);

  const afterCutover = await adapter.observe();
  const newWriter = adapter.propose(afterCutover, 'A10-WRITER-5',
    (domain, store, revision) =>
      domain.satisfy(store, revision, 'TC-A10-ASYNC', 'DONE'));
  const final = await adapter.commit(newWriter);
  assert.equal(final.disposition, 'CONFIRMED');
  assert.equal(port.commitCount, 3);
  assert.equal(port.receipts.size, 3);
  assert.equal(port.revision, 3);
  const state = JSON.parse(port.stateBytes.toString('utf8'));
  assert.equal(state.aggregates.TaskCycle['TC-A10-ASYNC'].obligations[0].status,
    'SATISFIED');
  assert.equal(state.aggregates.Milestone['MS-A10-STALE'], undefined);
  assert.equal(port.eventBytes.toString('utf8').trimEnd().split('\n').length, 3);

  // A04: force a real async interleaving. The second prepared operation is
  // rejected BEFORE reaching port.apply while the first awaits a response.
  const concurrentlyObserved = await adapter.observe();
  const firstPrepared = adapter.propose(concurrentlyObserved, 'A10-WRITER-6',
    (domain, store, revision) => domain.create(store, revision, 'Milestone',
      'MS-A10-INFLIGHT-WINNER', {title: 'ONE INFLIGHT WINNER'}, authority));
  const secondPrepared = adapter.propose(concurrentlyObserved, 'A10-WRITER-7',
    (domain, store, revision) => domain.create(store, revision, 'Milestone',
      'MS-A10-INFLIGHT-REJECTED', {title: 'NEVER DISPATCHED'}, authority));
  const directApply = port.apply.bind(port);
  let signalEntered, releaseApply;
  const entered = new Promise(resolve => { signalEntered = resolve; });
  const hold = new Promise(resolve => { releaseApply = resolve; });
  let dispatchCount = 0;
  port.apply = async proposal => {
    dispatchCount++;
    signalEntered();
    await hold;
    return directApply(proposal);
  };
  const firstInFlight = adapter.commit(firstPrepared);
  await entered;
  assert.throws(() => adapter.propose(concurrentlyObserved, 'A10-WRITER-8',
    (domain, store, revision) => domain.create(store, revision, 'Milestone',
      'MS-A10-PROPOSED-INFLIGHT', {title: 'BLOCKED PROPOSAL'}, authority)),
    /INFLIGHT_OPERATION_BLOCKED/);
  const secondRejected = await adapter.commit(secondPrepared);
  assert.equal(secondRejected.disposition, 'BLOCKED_INFLIGHT');
  assert.equal(dispatchCount, 1, 'only first original call entered async port');
  assert.equal(port.commitCount, 3, 'no commit before held response released');
  releaseApply();
  const firstConfirmed = await firstInFlight;
  port.apply = directApply;
  assert.equal(firstConfirmed.disposition, 'CONFIRMED');
  assert.equal(port.commitCount, 4);
  assert.equal(port.receipts.size, 4);
  assert.equal(port.revision, 4);
  assert.equal(JSON.parse(port.stateBytes.toString('utf8'))
    .aggregates.Milestone['MS-A10-INFLIGHT-REJECTED'], undefined);
  assert.equal(port.eventBytes.toString('utf8').trimEnd().split('\n').length, 4);

  console.log(JSON.stringify({
    status: 'A10_ASYNC_STORAGE_SHADOW_PRESERVATION_PASS',
    source_engine: 'FROZEN_ORIGINAL_PRODUCT_JS_V0',
    back_end: 'DISPOSABLE_IN_MEMORY_FAKE_CAS_NOT_POSTGRESQL',
    remote_storage_driver: 'NOT_IMPLEMENTED',
    cases: ['ORIGINAL_JS_BYTE_EXACT_PROPOSAL', 'STALENESS_NONE',
      'SYNTHETIC_POST_COMMIT_LOST_REPLY_UNKNOWN', 'NO_REDISPATCH',
      'READONLY_RECEIPT_RECONCILE', 'OLD_WRITER_EPOCH_FENCED',
      'NEW_EPOCH_SINGLE_COMMIT', 'MISMATCHED_RECEIPT_PRESERVES_UNKNOWN',
      'INFLIGHT_CONCURRENT_DISPATCH_BLOCKED'],
    committed_mutations: port.commitCount,
    event_count: 4,
    receipts: port.receipts.size,
    global_revision: port.revision,
    rejected_receipt_mismatches: receiptFaults.length,
    inflight_port_dispatches: dispatchCount,
    old_writer_effect: oldResult.disposition,
    unknown_reconciled: joined.disposition,
    neon: 'NOT_RUN', product_effect: 'NONE',
  }));
}
main().catch(error => {
  console.error('A10_ASYNC_CANARY_FAILED:' + (error?.code || error?.name || 'UNKNOWN'));
  process.exitCode = 1;
});
