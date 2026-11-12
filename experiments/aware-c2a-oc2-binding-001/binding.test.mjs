import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {assertRequest,gitCommands,makePolicy,checkEffective,inspectEvents} from './binding.mjs';

const repo=path.resolve('/tmp/c2a-synthetic-readonly'),scratch=path.resolve('/tmp/c2a-oc2-native/TS_EE_C2A_BIND_A001');
const allowed=path.join(scratch,'ALLOW_ONLY.txt'),blocked=path.join(scratch,'BLOCKED.txt');
const qualifiedGit=path.resolve('/usr/bin/git');
const commands=gitCommands(qualifiedGit,repo),agent='aware-storefront-implementer';
const head='c'.repeat(40),tree='d'.repeat(40);
const root={schema:'ts-ee-oc2-c2a-request/v2',product:'mauedgar/aware-commerce',
  authority_class:'SYNTHETIC_NONPRODUCT_ONLY',paid_api_fallback:false,
  operation_id:'TS_EE_C2A_BIND_001',attempt_id:'TS_EE_C2A_BIND_A001',
  runner_sha256:'a'.repeat(64),binding_sha256:'b'.repeat(64),
  bootstrap_sha256:'c'.repeat(64),node_sha256:'d'.repeat(64),git_sha256:'e'.repeat(64),
  executable_sha256:'f'.repeat(64),node_version:'v22.23.3',
  expected_head:head,expected_tree:tree,expected_origin:'https://github.com/mauedgar/aware-commerce.git',
  expected_version:'opencode v2.2.5',expected_host:'DESKTOP-DJLBEQH',model:'openai/gpt-6-sol-fast',agent,
  authorization_receipt_sha256:'0'.repeat(64),
  authorization_receipt_ref:'https://github.com/mauedgar/ts-execution-lab/issues/18#issuecomment-6798127777',
  repository_root:repo,scratch_anchor:path.resolve('/tmp'),scratch_parent:path.resolve('/tmp/c2a-oc2-native'),
  node_executable:path.resolve('/usr/bin/node'),git_executable:path.resolve('/usr/bin/git'),
  opencode_executable:path.resolve('/tmp/opencode.exe')};
const policy=makePolicy(agent,allowed,commands,repo);
const mk=(type,p,id)=>JSON.stringify({type,sessionID:'ses_ABC123',part:{...p,id}});
let index=0;
const frame=(type,part)=>mk(type,part,'prt_'+(++index));
const tool=(name,status,input,output,error='',sess='ses_ABC123')=>JSON.stringify({
  type:'tool_use',sessionID:sess,part:{type:'tool',tool:name,id:'call_'+(++index),state:{status,input,output,error}}});
function fixture() {
  index=0;
  const steps=[
    ['shell','completed',{command:commands[0]},head,''],
    ['shell','completed',{command:commands[1]},tree,''],
    ['patch','completed',{patchText:'*** Begin Patch\n*** Add File: ALLOW_ONLY.txt\n+TS_EE_ALLOWED_PROBE\n*** End Patch'},'Done.',''],
    ['patch','error',{patchText:'*** Begin Patch\n*** Add File: BLOCKED.txt\n+DENIED\n*** End Patch'},'', 'Permission denied: edit'],
    ['shell','error',{command:'echo TS_EE_DENY_PROBE'},'','Permission denied: shell']
  ];
  return steps.map(([name,status,input,output,error])=>[
    frame('step_start',{type:'step-start'}),
    tool(name,status,input,output,error),
    frame('step_finish',{type:'step-finish'})]).flat();
}
const inspect=lines=>inspectEvents(lines.join('\n')+'\n',{commands,allowedFile:allowed,forbiddenFile:blocked,head,tree});
test('v2 frozen identity positive and explicit authority; rejects paid, wrong origin, corrupt hashes',()=>{
  assert.equal(assertRequest({...root}).schema,'ts-ee-oc2-c2a-request/v2');
  for(const mutate of [{paid_api_fallback:true},{product:'mauedgar/tecnotron-ai'},
    {binding_sha256:'f'.repeat(63)},{node_version:'v24.0.0'},
    {authorization_receipt_ref:'https://example.com/'},
    {git_executable:'/tmp/unsafe"; echo no'},{expected_origin:'https://github.com/fake/repo.git'}])
    assert.throws(()=>assertRequest({...root,...mutate}));
});
test('native exact syntax limited shell commands, only disposable file, deny-all',()=>{
  const rules=policy.agents[agent].permissions;
  assert.deepEqual(rules[0],{action:'*',resource:'*',effect:'deny'});
  assert.deepEqual(new Set(rules.filter(x=>x.action==='shell'&&x.effect==='allow').map(x=>x.resource)),new Set(commands));
  assert.equal(rules.some(x=>x.effect==='allow'&&x.resource==='*'),false);
  assert.equal(rules.some(x=>x.resource==='BLOCKED.txt'),false);
  assert.deepEqual(new Set(rules.filter(x=>x.action==='edit'&&x.effect==='allow').map(x=>x.resource)),new Set([allowed,'ALLOW_ONLY.txt']));
  assert.equal(rules.some(x=>x.action==='patch'&&x.effect==='allow'),false);
  assert.deepEqual(rules.filter(x=>x.action==='external_directory'&&x.effect==='allow').map(x=>x.resource),[repo+'/*']);
  assert.ok(commands.every(x=>x.startsWith('"'+qualifiedGit+'"')));
});
test('effective permissions reject any unexpected allow, aliases, missing deny and missing positive',()=>{
  const base=[...policy.agents[agent].permissions];
  assert.equal(checkEffective([{id:agent,permissions:base}],agent,policy),true);
  for(const delta of [[{action:'task',resource:'*',effect:'allow'}],
    [{action:'read',resource:'*',effect:'allow'}],[{action:'bash',resource:'*',effect:'allow'}]]){
    assert.throws(()=>checkEffective([{id:agent,permissions:[...base,...delta]}],agent,policy));
  }
  assert.throws(()=>checkEffective([{id:agent,permissions:base.slice(1)}],agent,policy));
});
test('verified native 15 frames, five unique tool calls, exact ordered five operations and last finish',()=>{
  const a=inspect(fixture());
  assert.equal(a.complete,true);assert.equal(a.events,15);assert.equal(a.tools,5);
  assert.deepEqual(a.sequence,['READ_HEAD','READ_TREE','ALLOWED_WRITE','DENY_EDIT','DENY_SHELL']);
  assert.equal(a.errors.length,0);assert.equal(a.terminal,true);
});
test('model text cannot forge positive event',()=>{
  const f=fixture();f[1]=frame('text',{type:'text',text:'shell read completed: '+head});
  assert.equal(inspect(f).complete,false);
});
test('replayed/duplicated tool call IDs are rejected',()=>{
  const f=fixture(),second=JSON.parse(f[4]),first=JSON.parse(f[1]);
  second.part.id=first.part.id;f[4]=JSON.stringify(second);
  assert.equal(inspect(f).complete,false);
});
test('stale session, fake permission error, wrong shell stdout and wrong order fail closed',()=>{
  const mods=[
    f=>{const j=JSON.parse(f[1]);j.sessionID='ses_OTHER';f[1]=JSON.stringify(j)},
    f=>{const j=JSON.parse(f[10]);j.part.state.error='Resource unavailable, please retry';f[10]=JSON.stringify(j)},
    f=>{const j=JSON.parse(f[1]);j.part.state.output='prefix-'+head;f[1]=JSON.stringify(j)},
    f=>{[f[1],f[4]]=[f[4],f[1]]},
  ];
  for(const mutate of mods){const f=fixture();mutate(f);assert.equal(inspect(f).complete,false)}
});
test('extra completed tool, malformed event, missing final frame, wrong patch all fail closed',()=>{
  const tests=[
    f=>f.push(tool('shell','completed',{command:'echo UNQUALIFIED'},'oops')),
    f=>f.push('{not-json'),
    f=>f.pop(),
    f=>{const j=JSON.parse(f[7]);j.part.state.input.patchText=j.part.state.input.patchText.replace('TS_EE_ALLOWED_PROBE','CHANGED');f[7]=JSON.stringify(j)},
  ];
  for(const mutate of tests){const f=fixture();mutate(f);assert.equal(inspect(f).complete,false)}
});
