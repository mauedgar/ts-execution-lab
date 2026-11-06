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
  assert.equal(o.claim_sha256,digest(fs.readFileSync(path.join(f.work,'claim.json'))));
  assert.equal(o.result.claim_sha256,o.claim_sha256);
});
test('pre-existing receipt means no replay or overwrite',t=>{
  const f=prepare(t);invoke(f);const before=fs.readFileSync(path.join(f.work,'receipt.json'));
  let executed=false;denied(()=>invoke(f,()=>{executed=true;return {}; }),'CLAIM_ALREADY_EXISTS');
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

test('claim is durable and present before child starts',t=>{
  const f=prepare(t);const x=invoke(f,()=>{
    const claim=JSON.parse(fs.readFileSync(path.join(f.work,'claim.json'),'utf8'));
    assert.equal(claim.class,'NONREPLAYABLE_ATTEMPT_RESERVATION');
    assert.equal(claim.execution_attempt_id,f.request.execution_attempt_id);
    assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),false);
    return{status:0,stdout:successLine,stderr:''};
  });
  assert.equal(x.status,0);
});
test('simulated host crash after durable claim cannot re-dispatch same attempt',t=>{
  const f=prepare(t);let count=0;
  assert.throws(()=>run({attemptDir:f.work,sourceDir:f.src,spawn:()=>{count++;return{status:0,stdout:successLine,stderr:''}},
    onClaimDurable:()=>{throw Error('SIMULATED_POWER_LOSS')}}),/SIMULATED_POWER_LOSS/);
  assert.equal(count,0);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
  assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),false);
  denied(()=>invoke(f,()=>{count++;return{};}),'CLAIM_ALREADY_EXISTS');assert.equal(count,0);
});
test('actual subprocess exit after claim leaves no replayable attempt',t=>{
  const f=prepare(t);const src=path.join(__dirname,'r3-offline-attempt-v1.cjs');
  const command='require(process.argv[1]).run({attemptDir:process.argv[2],sourceDir:process.argv[3],onClaimDurable:()=>process.exit(77)})';
  const x=cp.spawnSync(process.execPath,['-e',command,src,f.work,f.src],{encoding:'utf8'});
  assert.equal(x.status,77);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
  assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),false);
  denied(()=>invoke(f),'CLAIM_ALREADY_EXISTS');
});
test('pre-existing partial claim blocks child before dispatch',t=>{
  const f=prepare(t);fs.writeFileSync(path.join(f.work,'claim.json'),'PARTIAL');
  let ran=false;denied(()=>invoke(f,()=>{ran=true;return{};}),'CLAIM_ALREADY_EXISTS');assert.equal(ran,false);
});
test('unsupported durable directory fsync refuses dispatch without claiming READY',t=>{
  const f=prepare(t);let ran=false;const io={...fs,constants:{...fs.constants,O_DIRECTORY:0}};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>{ran=true;return{};}}),'DURABLE_DIRECTORY_UNSUPPORTED');
  assert.equal(ran,false);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),false);
});
test('short claim write yields UNKNOWN with reserved artifact and no child',t=>{
  const f=prepare(t);let ran=false;const io={...fs,writeSync:()=>0};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>{ran=true;return{};}}),'DURABLE_EFFECT_UNKNOWN');
  assert.equal(ran,false);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
  denied(()=>invoke(f),'CLAIM_ALREADY_EXISTS');
});
test('write-all loop handles partial progress correctly',t=>{
  const f=prepare(t);const io={...fs,writeSync:(fd,buf,offset,length,pos)=>fs.writeSync(fd,buf,offset,Math.min(7,length),pos)};
  const x=run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>({status:0,stdout:successLine,stderr:''})});
  assert.equal(x.status,0);assert.equal(x.result.claim_sha256,x.claim_sha256);
});
test('claim file fsync failure stops before execution and preserves UNKNOWN claim',t=>{
  const f=prepare(t);let ran=false;const io={...fs,fsyncSync(fd){if(fs.fstatSync(fd).isFile())throw Error('FAULT_FILE_FSYNC');return fs.fsyncSync(fd)}};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>{ran=true;return{};}}),'DURABLE_EFFECT_UNKNOWN');
  assert.equal(ran,false);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
});
test('directory fsync failure after claim creation stops and preserves claim',t=>{
  const f=prepare(t);let ran=false,dirSyncs=0;const io={...fs,fsyncSync(fd){
    if(fs.fstatSync(fd).isDirectory()&&++dirSyncs>=2)throw Error('FAULT_DIR_FSYNC');return fs.fsyncSync(fd)}};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>{ran=true;return{};}}),'DURABLE_DIRECTORY_UNSUPPORTED');
  assert.equal(dirSyncs,2);assert.equal(ran,false);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
});
test('receipt fsync failure preserves claim and receipt as UNKNOWN',t=>{
  const f=prepare(t);let fileSyncs=0;const io={...fs,fsyncSync(fd){
    if(fs.fstatSync(fd).isFile()&&++fileSyncs===2)throw Error('FAULT_RECEIPT_FSYNC');return fs.fsyncSync(fd)}};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>({status:0,stdout:successLine,stderr:''})}),'DURABLE_EFFECT_UNKNOWN');
  assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
  assert.equal(fs.existsSync(path.join(f.work,'receipt.json')),true);
  denied(()=>invoke(f),'CLAIM_ALREADY_EXISTS');
});
test('close failure after claim write preserves uncertain effect and blocks dispatch',t=>{
  const f=prepare(t);let ran=false;const io={...fs,closeSync(fd){const st=fs.fstatSync(fd);fs.closeSync(fd);if(st.isFile())throw Error('FAULT_CLOSE')}};
  denied(()=>run({attemptDir:f.work,sourceDir:f.src,io,spawn:()=>{ran=true;return{};}}),'DURABLE_EFFECT_UNKNOWN');
  assert.equal(ran,false);assert.equal(fs.existsSync(path.join(f.work,'claim.json')),true);
});
