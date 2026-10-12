import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
const script = new URL('./publish-native-transport.mjs', import.meta.url).pathname;
function git(cwd,...args){const z=spawnSync('git',args,{cwd,encoding:'utf8'});assert.equal(z.status,0,z.stderr);return z.stdout.trim()}
function fixture(status='PASS',options={}){
  const root=mkdtempSync(join(tmpdir(),'ts-native-publish-'));
  const bare=join(root,'bare.git');git(root,'init','--bare',bare);
  const seed=join(root,'seed');mkdirSync(seed);git(seed,'init','-b','experiment');git(seed,'config','user.email','ee-test@example.invalid');git(seed,'config','user.name','EE Test');
  writeFileSync(join(seed,'BASE.txt'),'baseline\n');git(seed,'add','.');git(seed,'commit','-m','baseline');git(seed,'remote','add','origin',bare);git(seed,'push','-u','origin','experiment');
  const checkout=join(root,'worktree');git(root,'clone','-b','experiment',bare,checkout);git(checkout,'config','user.email','ee-test@example.invalid');git(checkout,'config','user.name','EE Test');
  const source=join(root,'output');mkdirSync(source);mkdirSync(join(source,'logs'));writeFileSync(join(source,'logs','native.log'),'large-log\n'.repeat(100));
  const rid='sha256:'+'a'.repeat(64);const attempt='NATIVE-TEST-001';const common={Product_operation_ref:'op://lab/synthetic',ExecutionAttempt_ref:attempt,request_identity:rid,result_status:status,effect_state:'NONE'};
  const observation={binding:'test',profile:'test',result_class:status,effect_state:'NONE',timings:{validation_ms:1,profile_ms:1,total_ms:2},subprocess_count:0};
  const result={contract_version:'ts-execution-result/v0.2',request_id:'req-1',Product_ref:'synthetic/lab',...common,execution_profile_ref:'profile://lab/test',subject_ref:'testsubject',context_id:'ctx1',observation};
  const receipt={contract_version:'ts-execution-receipt/v0.2',...common,selected_binding_ref:'test-binding',exact_subject_ref:'testsubject',started_at:'2026-10-12T00:00:00Z',completed_at:'2026-10-12T00:00:01Z',result_ref:'result.json',authority_created:false,Product_effect_created:false,observation};
  writeFileSync(join(source,'result.json'),JSON.stringify(result));writeFileSync(join(source,'receipt.json'),JSON.stringify(receipt));
  const parent=git(checkout,'rev-parse','HEAD');
  const request={contract:'ts-ee-native-transport-publication/v0-experimental',transport_checkout:checkout, result_dir:source,expected_head:parent,expected_remote_url:bare,branch:'experiment',package_path:'results/NATIVE-TEST-001',artifacts:['logs/native.log'],...options};
  const config=join(root,'request.json');writeFileSync(config,JSON.stringify(request));
  return {root,bare,checkout,source,parent,config,request,result,receipt};
}
function invoke(f){let x=spawnSync(process.execPath,[script,f.config],{encoding:'utf8'});let line=(x.status===0?x.stdout:x.stderr).trim();return {status:x.status,body:JSON.parse(line),stderr:x.stderr}}
for(const status of ['PASS','FAIL','BLOCKED'])test('terminal '+status+' publishes exact artifacts once',()=>{
  const f=fixture(status);const r=invoke(f);assert.equal(r.status,0,r.stderr);assert.equal(r.body.status,'PUBLISHED_VERIFIED');assert.equal(r.body.result_status,status);
  assert.equal(git(f.checkout,'rev-parse','HEAD'),git(f.checkout,'ls-remote','origin','refs/heads/experiment').split(/\s+/)[0]);
  const m=JSON.parse(readFileSync(join(f.checkout,'results/NATIVE-TEST-001/manifest.json')));assert.equal(m.files.length,3);
  assert.equal(m.result_status,status);
  const second=invoke(f);assert.equal(second.status,1);assert.match(second.body.reason,/PACKAGE_COLLISION/);assert.equal(git(f.checkout,'rev-parse','HEAD'),r.body.commit);
});
test('stale remote HEAD blocks before writing',()=>{
 const f=fixture();f.request.expected_head='b'.repeat(40);writeFileSync(f.config,JSON.stringify(f.request));const r=invoke(f);assert.equal(r.status,1);assert.equal(r.body.reason,'LOCAL_HEAD_MISMATCH');assert.equal(existsSync(join(f.checkout,'results')),false);
});
test('mismatched identity blocks before writing',()=>{
 const f=fixture();f.receipt.ExecutionAttempt_ref='OTHER';writeFileSync(join(f.source,'receipt.json'),JSON.stringify(f.receipt));const r=invoke(f);assert.equal(r.status,1);assert.match(r.body.reason,/ENVELOPE_IDENTITY_MISMATCH/);assert.equal(existsSync(join(f.checkout,'results')),false);
});
test('unsafe artifact path blocked',()=>{
 const f=fixture('PASS',{artifacts:['../BASE.txt']});writeFileSync(f.config,JSON.stringify(f.request));const r=invoke(f);assert.equal(r.status,1);assert.match(r.body.reason,/UNSAFE_RELATIVE_PATH/);
});
test('remote moved by another writer blocks before writing',()=>{
 const f=fixture();const other=join(f.root,'other');git(f.root,'clone','-b','experiment',f.bare,other);git(other,'config','user.email','ee-test@example.invalid');git(other,'config','user.name','EE Test');writeFileSync(join(other,'NEW'),'change');git(other,'add','.');git(other,'commit','-m','new');git(other,'push','origin','experiment');const r=invoke(f);assert.equal(r.status,1);assert.equal(r.body.reason,'REMOTE_HEAD_MISMATCH');assert.equal(existsSync(join(f.checkout,'results')),false);
});
test('oversized payload blocked before writing',()=>{
 const f=fixture('PASS',{max_package_bytes:10});writeFileSync(f.config,JSON.stringify(f.request));const r=invoke(f);assert.equal(r.status,1);assert.equal(r.body.reason,'PACKAGE_TOO_LARGE');
});
test('not clean transport checkout blocks before writing',()=>{
 const f=fixture();writeFileSync(join(f.checkout,'UNTRACKED'),'x');const r=invoke(f);assert.equal(r.status,1);assert.equal(r.body.reason,'DIRTY_TRANSPORT_CHECKOUT');
});

test('push failure preserves exact local commit for reconciliation',()=>{
 const f=fixture();const hook=join(f.bare,'hooks','pre-receive');
 writeFileSync(hook,'#!/bin/sh\nexit 1\n',{mode:0o755});
 const r=invoke(f);assert.equal(r.status,1);assert.equal(r.body.status,'PUBLICATION_UNKNOWN');assert.match(r.body.local_commit,/^[0-9a-f]{40}$/);assert.equal(r.body.retry_authorized,false);
 assert.equal(git(f.checkout,'rev-parse','HEAD'),r.body.local_commit);
 assert.equal(git(f.checkout,'ls-remote','origin','refs/heads/experiment').split(/\s+/)[0],f.parent);
});
