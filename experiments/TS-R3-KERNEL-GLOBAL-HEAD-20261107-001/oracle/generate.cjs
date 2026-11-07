'use strict';
// Experimental deterministic fixture. JSON.stringify + hashing follows frozen
// Product src/state-kernel-v0/store.js @ f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a.
// This is NOT a replacement for executing the complete Product contract suite.
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const KINDS = ['Milestone', 'TaskCycle', 'Operation', 'ExecutionAttempt'];
const base = { schema_version: 'tecnotron-state-kernel/v0', revision: 0,
               aggregates: Object.fromEntries(KINDS.map(k => [k, {}])) };
const seed = JSON.stringify(base, null, 2) + '\n';
const state = structuredClone(base);
const date = '2026-11-07T00:00:00.000Z';
const auth = [{kind:'AUTHORITY', id:'AUTH-SYNTHETIC-ONLY'}];
const snapshots = [];
let lastHash = null;
function common(kind, id, current, revision=1) {
  return {schema_version:'tecnotron-state-kernel/v0',kind,id,revision,state:current,
          created_at:date,updated_at:date,authority_refs:structuredClone(auth),related_ids:[],last_event_id:null};
}
function change(kind, ident, action, newValue, priorRev, extra={}) {
  const sequence = state.revision + 1;
  const after = structuredClone(newValue);
  after.revision = priorRev + 1;
  after.last_event_id = `event-${sequence}`;
  state.aggregates[kind][ident] = after;
  state.revision = sequence;
  const payload = {id:`event-${sequence}`,sequence,kind,aggregate_id:ident,
                   before_revision:priorRev, after, previous_hash:lastHash,at:date,action,...extra};
  const payloadRaw = JSON.stringify(payload);
  const h = sha(payloadRaw);
  const lineRaw = JSON.stringify({...payload,hash:h}) + '\n';
  const stateRaw = JSON.stringify(state,null,2) + '\n';
  assert.equal(h, sha(payloadRaw));
  const snap={mutation_id:`MUT-SYNTHETIC-${sequence}`,expected_revision:sequence-1,
              previous_event_hash:lastHash,authority_fingerprint:sha('synthetic authority no Product grant'),
              payload_b64:Buffer.from(payloadRaw).toString('base64'),
              line_b64:Buffer.from(lineRaw).toString('base64'),
              state_b64:Buffer.from(stateRaw).toString('base64'),
              event_hash:h};
  snapshots.push(snap);
  lastHash=h;
}
const tc = { ...common('TaskCycle','TC-SYNTHETIC','READY'),
             responsibility:'synthetic state bridge ☕ 😀 with newline\nquoted \"text\"',
             obligations:[{id:'EVIDENCE',status:'PENDING',authority_ref:null}],terminal_disposition_ref:null};
change('TaskCycle',tc.id,'CREATE',tc,0);
const ms={...common('Milestone','MS-SYNTHETIC','PLANNED'),title:'Café — synthetic milestone 😀'};
change('Milestone',ms.id,'CREATE',ms,0);
const op={...common('Operation','OP-SYNTHETIC','DEFINED'),taskcycle_id:tc.id,
          objective:'test only',result_ref:null};
change('Operation',op.id,'CREATE',op,0);
const next = (kind,id,target,action)=>{
  const before=state.aggregates[kind][id];
  change(kind,id,action||`TRANSITION:${target}`,{...before,state:target},before.revision);
};
next('Operation',op.id,'READY');
next('Operation',op.id,'RUNNING');
const at={...common('ExecutionAttempt','AT-SYNTHETIC','PREPARED'),operation_id:op.id,
          outcome:null,reconciliation_required:false,result_refs:[]};
change('ExecutionAttempt',at.id,'CREATE',at,0);
next('ExecutionAttempt',at.id,'DISPATCHED');
next('ExecutionAttempt',at.id,'RUNNING');
const beforeUnknown=state.aggregates.ExecutionAttempt[at.id];
change('ExecutionAttempt',at.id,'TRANSITION:UNKNOWN',
       {...beforeUnknown,state:'UNKNOWN',outcome:'UNKNOWN',reconciliation_required:true},beforeUnknown.revision);
const beforeFail=state.aggregates.ExecutionAttempt[at.id];
change('ExecutionAttempt',at.id,'TRANSITION:FAILED',
       {...beforeFail,state:'FAILED',outcome:'FAIL',reconciliation_required:false,
        result_refs:[{kind:'EVIDENCE',id:'EVIDENCE-SYNTHETIC-RECONCILE'}]},beforeFail.revision);
const beforeSatisfy=state.aggregates.TaskCycle[tc.id];
change('TaskCycle',tc.id,'SATISFY:EVIDENCE',
       {...beforeSatisfy,obligations:[{id:'EVIDENCE',status:'SATISFIED',authority_ref:null}]},beforeSatisfy.revision);
next('TaskCycle',tc.id,'ACTIVE');
const beforeClose=state.aggregates.TaskCycle[tc.id];
change('TaskCycle',tc.id,'TRANSITION:CLOSED',
       {...beforeClose,state:'CLOSED',terminal_disposition_ref:'EVIDENCE-SYNTHETIC-CLOSE'},beforeClose.revision);
const artifact={schema:'ts-r3-global-head-oracle/v0', source_product_store_blob:'f80d7cfe2bc9cd228cb6e3ca817c2e8802e74c8a',
                scope:'scope-synthetic-20261107',genesis_b64:Buffer.from(seed).toString('base64'),mutations:snapshots};
const dest=path.join(__dirname,'golden.json');
fs.writeFileSync(dest,JSON.stringify(artifact,null,2)+'\n',{flag:'w'});
process.stdout.write(`ORACLE ${snapshots.length} mutations, latest=${sha(JSON.stringify(state,null,2)+'\n')}\n`);
