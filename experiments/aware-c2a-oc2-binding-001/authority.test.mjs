import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyControlGrant,AUTHORITY_GRANT_SCHEMA} from './authority.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const ref='mauedgar/ts-execution-transport@'+'a'.repeat(40)+':grants/AWARE-C2A-OC2-S0-001/GRANT.json';
const now=Date.UTC(2026,10,13,12,0,0);
const request={
  product:'mauedgar/aware-commerce',
  operation_id:'TS_EE_C2A_S0_TEST_001',attempt_id:'TS_EE_C2A_S0_TEST_A001',
  expected_head:'a'.repeat(40),expected_tree:'b'.repeat(40),
  expected_origin:'https://github.com/mauedgar/aware-commerce.git',
  expected_host:'DESKTOP-DJLBEQH',agent:'aware-storefront-implementer',
  model:'openai/gpt-6-sol-fast',repository_root:'C:\\work\\aware',
  scratch_anchor:'C:\\TS\\station',scratch_parent:'C:\\TS\\station\\ts-ee-oc2-c2a-synthetic',
  node_executable:'C:\\node22\\node.exe',git_executable:'C:\\Git\\bin\\git.exe',
  opencode_executable:'C:\\oc2\\opencode.exe',
  bootstrap_sha256:'a'.repeat(64),binding_sha256:'b'.repeat(64),
  authority_source_sha256:'c'.repeat(64),runner_sha256:'d'.repeat(64),
  node_sha256:'e'.repeat(64),git_sha256:'f'.repeat(64),executable_sha256:'0'.repeat(64),
  authorization_receipt_ref:ref
};
const subject={...request};
delete subject.product;
delete subject.authorization_receipt_ref;
const grant={
  schema:AUTHORITY_GRANT_SCHEMA,issuer:'AWARE_CONTROL',disposition:'CONDITIONAL_SYNTHETIC_S0_ONLY',
  product:'mauedgar/aware-commerce',control_issue:'https://github.com/mauedgar/aware-commerce/issues/29',
  developer_ruling_url:'https://github.com/mauedgar/aware-commerce/issues/29#issuecomment-9999999999',
  cloud_enabled:false,paid_api_fallback:false,product_write_allowed:false,production_allowed:false,
  expires_at:'2099-01-01T00:00:00Z',synthetic_write_set:['ALLOW_ONLY.txt'],
  forbidden_effects:['BLOCKED.txt','UNSCOPED_SHELL','PRODUCT_SOURCE'],subject
};
const material=(x=grant)=>{
  const bytes=Buffer.from(JSON.stringify(x),'utf8');
  const anchor={ref,sha256:sha(bytes)};
  return {bytes,anchor,request:{...request,authorization_receipt_sha256:anchor.sha256}};
};
test('external immutable Control anchor and exact scoped synthetic grant are required',()=>{
  const x=material(),verified=verifyControlGrant(x.request,x.bytes,x.anchor,{now});
  assert.equal(verified.issuer,'AWARE_CONTROL');
  assert.equal(verified.sha256,x.anchor.sha256);
  assert.equal(verified.note.includes('externally'),true);
});
test('self-selected request ref/digest without independent anchor cannot authorize anything',()=>{
  const x=material();
  for(const anchor of [null,undefined,{}, {ref,sha256:'0'.repeat(64)},
    {ref:'https://github.com/mauedgar/ts-execution-lab/issues/18#issuecomment-1',sha256:x.anchor.sha256}])
    assert.throws(()=>verifyControlGrant(x.request,x.bytes,anchor,{now}));
  assert.throws(()=>verifyControlGrant({...x.request,authorization_receipt_ref:'wrong'},x.bytes,x.anchor,{now}));
  assert.throws(()=>verifyControlGrant({...x.request,authorization_receipt_sha256:'0'.repeat(64)},x.bytes,x.anchor,{now}));
});
test('tampered or substituted grant is rejected against separately pinned original bytes',()=>{
  const x=material();
  const forged={...grant,issuer:'TS_EXECUTION_ENGINEERING'};
  assert.throws(()=>verifyControlGrant(x.request,Buffer.from(JSON.stringify(forged)),x.anchor,{now}));
  assert.throws(()=>verifyControlGrant(x.request,Buffer.concat([x.bytes,Buffer.from(' ')]),x.anchor,{now}));
  assert.throws(()=>verifyControlGrant(x.request,Buffer.from('invalid utf8 \ufffd'),x.anchor,{now}));
});
test('issuer, time, scope, developer source and unrelated attempts fail closed',()=>{
  const changes=[
    {issuer:'TS_EXECUTION_ENGINEERING'}, {disposition:'APPROVED_PRODUCT_WRITE'},
    {product:'mauedgar/tecnotron-ai'},{control_issue:'https://github.com/mauedgar/ts-execution-lab/issues/18'},
    {developer_ruling_url:'https://github.com/mauedgar/ts-execution-lab/issues/18#issuecomment-1'},
    {paid_api_fallback:true}, {cloud_enabled:true}, {product_write_allowed:true},
    {production_allowed:true},{expires_at:'2020-01-01T00:00:00Z'},
    {synthetic_write_set:['ALLOW_ONLY.txt','BLOCKED.txt']},
    {forbidden_effects:['UNSCOPED_SHELL']}
  ];
  for(const update of changes){
    const x=material({...grant,...update});
    assert.throws(()=>verifyControlGrant(x.request,x.bytes,x.anchor,{now}));
  }
  for(const [key,value] of [['attempt_id','ANOTHER_A001'],['model','openai/unverified'],
    ['expected_head','z'.repeat(40)],['authority_source_sha256','0'.repeat(64)],
    ['scratch_parent','C:\\different'],['node_sha256','1'.repeat(64)]]){
    const x=material({...grant,subject:{...subject,[key]:value}});
    assert.throws(()=>verifyControlGrant(x.request,x.bytes,x.anchor,{now}));
  }
});
test('malformed external bytes, expiry and mutable issue comment refs fail closed',()=>{
  const x=material();
  assert.throws(()=>verifyControlGrant(x.request,x.bytes,x.anchor,{now:Date.UTC(2099,0,1)}));
  const wrong={...x.anchor,ref:'mauedgar/ts-execution-transport@main:grants/AWARE-C2A-OC2-S0-001/GRANT.json'};
  assert.throws(()=>verifyControlGrant(x.request,x.bytes,wrong,{now}));
  assert.throws(()=>verifyControlGrant(x.request,Buffer.alloc(0),x.anchor,{now}));
  assert.throws(()=>verifyControlGrant(x.request,Buffer.from([0xC3,0x28,...x.bytes]),x.anchor,{now}));
});
