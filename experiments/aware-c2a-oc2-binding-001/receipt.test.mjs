import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {reconcileOriginalReceipt} from './bootstrap.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const r={
  operation_id:'TS_EE_C2A_BIND_001',attempt_id:'TS_EE_C2A_BIND_A001',
  product:'mauedgar/aware-commerce',expected_head:'a'.repeat(40),
  expected_tree:'b'.repeat(40),expected_origin:'https://github.com/mauedgar/aware-commerce.git',
  bootstrap_sha256:'c'.repeat(64),binding_sha256:'d'.repeat(64),
  runner_sha256:'e'.repeat(64),authority_source_sha256:'8'.repeat(64),node_sha256:'f'.repeat(64),
  git_sha256:'0'.repeat(64),executable_sha256:'1'.repeat(64),
  authorization_receipt_sha256:'2'.repeat(64),
  authorization_receipt_ref:'mauedgar/ts-execution-transport@'+'a'.repeat(40)+':grants/AWARE-C2A-OC2-S0-001/GRANT.json'
};
const bytes=Buffer.from('{"native":true}\n');
const allowed=Buffer.from('TS_EE_ALLOWED_PROBE');
const subject={
  operation_id:r.operation_id,attempt_id:r.attempt_id,product:r.product,
  source:{head:r.expected_head,tree:r.expected_tree,origin:r.expected_origin},
  bundle:{bootstrap:r.bootstrap_sha256,binding:r.binding_sha256,runner:r.runner_sha256,authority:r.authority_source_sha256},
  executable:{node_sha256:r.node_sha256,git_sha256:r.git_sha256,opencode_sha256:r.executable_sha256},
  authority:{ref:r.authorization_receipt_ref,sha256:r.authorization_receipt_sha256,issuer:'AWARE_CONTROL',trust_root:'EXTERNALLY_PINNED_GIT_BLOB'}
};
const make=()=>{
  const meta={sha256:sha(bytes),bytes:bytes.length,exit_code:0,signal:null,
    spawn_error:null,native_error:null,stdout_truncated:false,session_id:'ses_ABC123'};
  return {
    'START.json':{...structuredClone(subject),status:'STARTED',native_dispatched:false},
    'DISPATCH.json':{...structuredClone(subject),status:'DISPATCH_MARKER'},
    'CONTEXT.json':{scope:'SYNTHETIC_NONPRODUCT_ONLY'},
    'EFFECTIVE.json':{debug_config_only:true},
    'NATIVE_META.json':meta,
    'RESULT.json':{...structuredClone(subject),status:'PASS',effect_state:'CONFIRMED_SYNTHETIC_ONLY',
      native_dispatched:true,terminus_proven:true,
      observed:{session:'ses_ABC123',complete:true},
      original_native_log:{sha256:sha(bytes),bytes:bytes.length},
      forbidden_file_exists:false,product_source_drift:false,
      allowed_file_sha256:sha(allowed)}
  };
};
const read=(records,overrides={})=>reconcileOriginalReceipt(r,records,
  {native:bytes,allowed,denied:false,...overrides});

test('original complete receipt: hashes, identity and synthetic bytes match, provider not authenticated',()=>{
  const x=read(make());
  assert.equal(x.status,'PASS');assert.equal(x.effect_state,'CONFIRMED_SYNTHETIC_ONLY');
  assert.equal(x.receipt_consistency,'LOCAL_HASH_AND_BYTE_MATCH');
  assert.equal(x.native_provider_authenticated,false);
});
test('wrong original identity, provenance or missing result always UNKNOWN',()=>{
  for(const change of [
    x=>{x['START.json'].source.head='9'.repeat(40)},
    x=>{x['RESULT.json'].authority.ref='forged'},
    x=>{x['DISPATCH.json'].bundle.runner='3'.repeat(64)},
    x=>{x['RESULT.json']=null},
    x=>{x['RESULT.json'].native_dispatched=false},
  ]){
    const records=make();change(records);
    assert.equal(read(records).status,'UNKNOWN');
    assert.equal(read(records).effect_state,'UNKNOWN');
  }
});
test('changed or absent log, wrong log size, foreign session and wrong file bytes cannot produce PASS',()=>{
  const cases=[
    {change:x=>{x['NATIVE_META.json'].sha256='9'.repeat(64)}},
    {change:x=>{x['NATIVE_META.json'].bytes+=1}},
    {change:x=>{x['RESULT.json'].original_native_log.sha256='9'.repeat(64)}},
    {change:x=>{x['RESULT.json'].observed.session='ses_ANOTHER'}},
    {change:x=>{x['NATIVE_META.json'].session_id='ses_ANOTHER'}},
    {change:x=>{x['RESULT.json'].allowed_file_sha256='9'.repeat(64)}},
    {override:{native:null}},
    {override:{allowed:Buffer.from('TAMPERED')}},
    {override:{denied:true}},
    {override:{corrupt:['RESULT.json']}},
  ];
  for(const t of cases){
    const records=make();t.change?.(records);
    const result=read(records,t.override);
    assert.equal(result.status,'UNKNOWN');assert.equal(result.effect_state,'UNKNOWN');
  }
});
test('native post-dispatch failures are UNKNOWN even when a result exists',()=>{
  for(const change of [
    x=>{x['RESULT.json'].status='BLOCKED'},
    x=>{x['RESULT.json'].effect_state='NONE'},
    x=>{x['RESULT.json'].observed.complete=false},
    x=>{x['NATIVE_META.json'].exit_code=1},
    x=>{x['NATIVE_META.json'].stdout_truncated=true},
    x=>{x['RESULT.json'].product_source_drift=true},
  ]){
    const records=make();change(records);
    assert.equal(read(records).status,'UNKNOWN');
  }
});
test('confirmed pre-dispatch block keeps NONE, lost/ambiguous receipt never does',()=>{
  const records=make();
  records['DISPATCH.json']=null;
  records['NATIVE_META.json']=null;
  records['RESULT.json']={...structuredClone(subject),status:'BLOCKED_PRECONDITION',effect_state:'NONE',
    native_dispatched:false};
  const confirmed=reconcileOriginalReceipt(r,records,{});
  assert.equal(confirmed.status,'BLOCKED_PRECONDITION');
  assert.equal(confirmed.effect_state,'NONE');
  delete records['RESULT.json'];
  assert.equal(reconcileOriginalReceipt(r,records,{}).status,'UNKNOWN');
});
