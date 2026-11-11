import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {assertRequest,gitCommands,makePolicy,checkEffective,inspectEvents} from './binding.mjs';
const root=path.resolve('/tmp/ts-ee-aware-c2a-synthetic-source');
const scratch=path.resolve('/tmp/ts-ee-aware-c2a-synthetic-only');
const allow=path.join(scratch,'ALLOW_ONLY.txt'),forbid=path.join(scratch,'BLOCKED.txt');
const commands=gitCommands(root),agent='aware-storefront-implementer';
const policy=makePolicy(agent,allow,commands);
const base={schema:'ts-ee-oc2-c2a-request/v1',product:'mauedgar/aware-commerce',
  authority_class:'SYNTHETIC_NONPRODUCT_ONLY',paid_api_fallback:false,
  operation_id:'TS_EE_C2A_BIND_001',attempt_id:'TS_EE_C2A_BIND_A001',
  runner_sha256:'a'.repeat(64),executable_sha256:'b'.repeat(64),
  expected_head:'c'.repeat(40),expected_tree:'d'.repeat(40),
  expected_origin:'https://github.com/mauedgar/aware-commerce.git',
  expected_version:'opencode v2.2.5',expected_host:'DESKTOP-TEST',
  model:'openai/gpt-6-sol-fast',agent,repository_root:root,scratch_parent:scratch,
  opencode_executable:path.resolve('/tmp/ts-ee-bin/opencode')};
test('exact frozen request accepted; paid fallbacks, unknown repo and unsafe paths rejected',()=>{
  assert.equal(assertRequest({...base}).product,'mauedgar/aware-commerce');
  for(const bad of [{paid_api_fallback:true},{product:'mauedgar/tecnotron-ai'},
    {repository_root:'/tmp/a";rm -rf b'},{runner_sha256:'a'.repeat(63)},
    {expected_origin:'https://github.com/other/other.git'}])
    assert.throws(()=>assertRequest({...base,...bad}));
});
test('allow rules are minimum exact shell reads and synthetic write only',()=>{
  const r=policy.agents[agent].permissions.filter(p=>p.effect==='allow');
  assert.deepEqual(new Set(r.filter(x=>x.action==='shell').map(x=>x.resource)),new Set(commands));
  assert.equal(r.filter(x=>x.action==='write').length,2);
  assert.equal(r.some(x=>x.resource==='BLOCKED.txt'),false);
  assert.equal(r.some(x=>x.resource==='*'),false);
});
test('effective native agent must retain deny-all and exact allowed calls',()=>{
  assert.equal(checkEffective([{id:agent,permissions:policy.agents[agent].permissions}],agent,policy),true);
  const broad=[...policy.agents[agent].permissions,{action:'shell',resource:'*',effect:'allow'}];
  assert.throws(()=>checkEffective([{id:agent,permissions:broad}],agent,policy));
  assert.throws(()=>checkEffective([{id:agent,permissions:broad.slice(1,-1)}],agent,policy));
});
const e=(tool,status,input,output='',error='')=>JSON.stringify({part:{type:'tool',tool,state:{status,input,output,error}}});
test('native exact positive read/write and negative denials are distinguishable',()=>{
  const lines=[
    e('shell','completed',{command:commands[0]},base.expected_head),
    e('shell','completed',{command:commands[1]},base.expected_tree),
    e('write','completed',{filePath:allow},'ok'),
    e('edit','error',{filePath:forbid},'','permission.rejected'),
    e('shell','error',{command:'echo TS_EE_DENY_PROBE'},'','permission.rejected'),
  ].join('\n')+'\n';
  const a=inspectEvents(lines,{commands,allowedFile:allow,forbiddenFile:forbid,
    head:base.expected_head,tree:base.expected_tree});
  assert.equal(a.events,5);assert.equal(a.tools,5);assert.equal(a.read_head,true);
  assert.equal(a.read_tree,true);assert.equal(a.write_allow,true);
  assert.equal(a.edit_denied,true);assert.equal(a.shell_denied,true);
  assert.equal(a.forbidden_completed,false);assert.equal(a.invalid_events,0);
});
test('model assertions and completed forbidden calls do not pass',()=>{
  const f=JSON.stringify({part:{type:'text',text:'I denied everything and wrote correctly'}});
  const events=[f,e('shell','completed',{command:'echo TS_EE_DENY_PROBE'},'bad'),
    e('write','completed',{filePath:forbid},'bad'),'not-json'].join('\n');
  const x=inspectEvents(events,{commands,allowedFile:allow,forbiddenFile:forbid,
    head:base.expected_head,tree:base.expected_tree});
  assert.equal(x.read_head,false);assert.equal(x.write_allow,false);
  assert.equal(x.forbidden_completed,true);assert.equal(x.invalid_events,1);
});
