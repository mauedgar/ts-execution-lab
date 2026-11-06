'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const cp = require('node:child_process');
const {SUBJECT, Blocked, parseRequest, gitBlob, digest, run} = require('./r3-offline-attempt-v1.cjs');
const PINNED = path.join(__dirname, 'r3-portable-host-preflight.cjs');
const successLine = 'PASS|TS-R3|PORTABLE_HOST_PREFLIGHT|node=v22.16.0|pg=8.23.1|sources=4|lock=GIT_BLOB_VERIFIED|installed=PACKAGE_METADATA_ONLY|tls=NOT_TESTED|physical=NOT_TESTED\n';
function prepare(t) {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-receipt-v1-'));
  t.after(() => fs.rmSync(base, {recursive:true,force:true}));
  const src = path.join(base, 'source'); const work=path.join(base,'attempt');
  fs.mkdirSync(src); fs.mkdirSync(work);
  fs.copyFileSync(PINNED,path.join(src,'r3-portable-host-preflight.cjs'));
  const request={schema:'TS_R3_OFFLINE_ATTEMPT_V1',operation:'CREDENTIAL_FREE_METADATA_PREFLIGHT',operation_id:'TS_R3_OP_20261105_001',execution_attempt_id:'TS_R3_ATTEMPT_20261105_001',subject:SUBJECT};
  fs.writeFileSync(path.join(work,'request.json'),JSON.stringify(request)+'\n');
  return {base,src,work,request};
}
function invoke(f,runner=()=>({status:0,stdout:successLine,stderr:'',signal:null,error:undefined})) {
  return run({attemptDir:f.work,sourceDir:f.src,spawn:runner});
}
function denied(fn,code){assert.throws(fn,e=>e instanceof Blocked&&e.code===code);}
test('frozen exact preflight blob is real',()=>{
  assert.equal(gitBlob(fs.readFileSync(PINNED)),SUBJECT.preflight_blob);
});
test('positive native mocked child yields correlated but untrusted receipt',t=>{
  const f=prepare(t);let captured;
  const o=invoke(f,(exe,args,opts)=>{captured={exe,args,opts};return{status:0,stdout:successLine,stderr:'',signal:null};});
  assert.equal(o.status,0);assert.equal(o.result.result,'PASS_METADATA_ONLY');
  assert.equal(o.result.request_sha256,digest(fs.readFileSync(path.join(f.work,'request.json'))));
  assert.equal(o.result.execution_attempt_id,'TS_R3_ATTEMPT_20261105_001');
  assert.equal(o.result.device_attestation,'NONE');assert.equal(o.result.package_integrity_proof,'NONE');
  assert.equal(o.result.product_effect,'NONE');
  assert.deepEqual(captured.args,[path.join(f.src,'r3-portable-host-preflight.cjs')]);
  assert.equal(captured.opts.timeout,30000);assert.equal(captured.opts.maxBuffer,16384);
  assert.equal(captured.opts.env.TS_R3_DATABASE_URL,undefined);
  assert.equal(o.receipt_sha256,digest(fs.readFileSync(path.join(f.work,'receipt.json'))));
});
test('pre-existing receipt means no replay or overwrite',t=>{
  const f=prepare(t);invoke(f);const before=fs.readFileSync(path.join(f.work,'receipt.json'));
  let executed=false;denied(()=>invoke(f,()=>{executed=true;return {}; }),'RECEIPT_ALREADY_EXISTS');
  assert.equal(executed,false);assert.deepEqual(fs.readFileSync(path.join(f.work,'receipt.json')),before);
});
test('receipt symlink is preserved, never overwritten',t=>{
  const f=prepare(t);fs.writeFileSync(path.join(f.base,'protected'),'UNCHANGED');
  fs.symlinkSync(path.join(f.base,'protected'),path.join(f.work,'receipt.json'));
  denied(()=>invoke(f),'RECEIPT_ALREADY_EXISTS');assert.equal(fs.readFileSync(path.join(f.base,'protected'),'utf8'),'UNCHANGED');
});
test('missing request denies without new receipt',t=>{
  const f=prepare(t);fs.unlinkSync(path.join(f.work,'request.json'));
  denied(()=>invoke(f),'PATH_MISSING');assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),false);
});
test('invalid JSON denies without receipt',t=>{
  const f=prepare(t);fs.writeFileSync(path.join(f.work,'request.json'),'not json');
  denied(()=>invoke(f),'REQUEST_BAD_JSON');assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),false);
});
test('changed subject commit cannot dispatch',t=>{
  const f=prepare(t);f.request.subject={...SUBJECT,commit:'0000000000000000000000000000000000000000'};
  fs.writeFileSync(path.join(f.work,'request.json'),JSON.stringify(f.request));
  denied(()=>invoke(f),'REQUEST_SUBJECT');
});
test('request with unknown fields fails closed',t=>{
  const f=prepare(t);f.request.surprise=true;
  fs.writeFileSync(path.join(f.work,'request.json'),JSON.stringify(f.request));denied(()=>invoke(f),'REQUEST_SHAPE');
});
test('invalid attempt identifier fails closed',t=>{
  const f=prepare(t);f.request.execution_attempt_id='../../bad';
  fs.writeFileSync(path.join(f.work,'request.json'),JSON.stringify(f.request));denied(()=>invoke(f),'REQUEST_ID');
});
test('source blob tampering rejects before subprocess',t=>{
  const f=prepare(t);fs.appendFileSync(path.join(f.src,'r3-portable-host-preflight.cjs'),'// tamper');
  let executed=false;denied(()=>invoke(f,()=>{executed=true;return {}; }),'RUNNER_SOURCE_MISMATCH');assert.equal(executed,false);
});
test('source symlink denies before subprocess',t=>{
  const f=prepare(t);const p=path.join(f.src,'r3-portable-host-preflight.cjs');fs.renameSync(p,p+'.real');fs.symlinkSync('r3-portable-host-preflight.cjs.real',p);
  denied(()=>invoke(f),'PATH_REDIRECT');
});
test('ancestor symlink denies before subprocess',t=>{
  const f=prepare(t);fs.renameSync(f.src,f.src+'-real');fs.symlinkSync(f.src+'-real',f.src,'dir');
  denied(()=>invoke(f),'PATH_REDIRECT');
});
test('tampered preflight success output yields BLOCKED receipt',t=>{
  const f=prepare(t);const result=invoke(f,()=>({status:0,stdout:'PASS|TS-R3|WRONG',stderr:''}));
  assert.equal(result.status,2);assert.equal(result.result.result,'BLOCKED');
  assert.equal(result.result.failure_class,'PREFLIGHT_NOT_PASS');
});
test('child error produces bounded blocked receipt',t=>{
  const f=prepare(t);const result=invoke(f,()=>({status:null,error:{code:'ENOENT'},stdout:'',stderr:'sensitive-test-secret'}));
  assert.equal(result.status,2);assert.equal(result.result.failure_class,'CHILD_EXEC_ERROR');
  assert.doesNotMatch(JSON.stringify(result.result),/sensitive-test-secret/);
});
test('child signal produces blocked receipt, no replay',t=>{
  const f=prepare(t);const result=invoke(f,()=>({status:null,signal:'SIGTERM',stdout:''}));
  assert.equal(result.status,2);assert.equal(result.result.failure_class,'CHILD_SIGNAL');
});
test('child stderr even with syntactic PASS means blocked',t=>{
  const f=prepare(t);const result=invoke(f,()=>({status:0,stdout:successLine,stderr:'warning'}));
  assert.equal(result.status,2);assert.equal(result.result.failure_class,'PREFLIGHT_NOT_PASS');
});
test('CLI bad argument fails closed and prints no secret',()=>{
  const r=cp.spawnSync(process.execPath,[path.join(__dirname,'r3-offline-attempt-v1.cjs')],{encoding:'utf8',env:{...process.env,TS_R3_DATABASE_URL:'SENSITIVE_SENTINEL_FOR_TEST'}});
  assert.equal(r.status,2);assert.match(r.stderr,/OFFLINE_ATTEMPT\|ARGUMENTS/);assert.doesNotMatch(r.stderr,/SENSITIVE_SENTINEL_FOR_TEST|Error:| at /);
});
test('CLI isolated negative produces receipt; no network credentials',t=>{
  const f=prepare(t);const res=cp.spawnSync(process.execPath,[path.join(__dirname,'r3-offline-attempt-v1.cjs'),f.work],{encoding:'utf8',env:{PATH:process.env.PATH||'',HOME:process.env.HOME||'',SYSTEMROOT:process.env.SYSTEMROOT||''}});
  // The real preflight cannot qualify: this synthetic source has no pinned sibling source or pg install.
  assert.equal(res.status,2);assert.match(res.stdout,/BLOCKED\|TS-R3\|OFFLINE_ATTEMPT/);assert.doesNotMatch(res.stdout,/PASS_METADATA_ONLY/);
  const receipt=JSON.parse(fs.readFileSync(path.join(f.work,'receipt.json'),'utf8'));
  assert.equal(receipt.result,'BLOCKED');assert.equal(receipt.device_attestation,'NONE');
});
