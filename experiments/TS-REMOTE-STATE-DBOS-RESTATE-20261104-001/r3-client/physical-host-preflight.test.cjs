'use strict';
// Offline deterministic test only. The fake PG client never opens a socket.
// No Product DB, Neon secret or physical-host PASS follows from these tests.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,'physical-host-p01-p04.cjs'),'utf8');
const split = source.indexOf('\nmain().catch(err => {');
assert(split > 0, 'known terminal catch must exist');
const script = new vm.Script(source.slice(0,split) + '\nmain();', {filename:'r3-preflight-synthetic.cjs'});
const host = 'ep-ancient-flower-b6eb9w6c.c-2.sa-east-1.aws.neon.tech';
const selfDigest = name => crypto.createHash('sha256').update(name,'utf8').digest('hex');
function empty() { return {state:null,event:null,receipt:null}; }
function shape(row) { return row ? JSON.parse(JSON.stringify(row)) : null; }
function mockAssert(pred, message) { if(!pred)throw new Error(message||'assertion'); }
mockAssert.equal = (a,b,msg) => mockAssert(a===b,msg||'equal');
mockAssert.deepEqual = (a,b,msg) => mockAssert(JSON.stringify(shape(a))===JSON.stringify(shape(b)),msg||'deepEqual');
function database() {
  const db = { data: empty(), commits:0, failAck:false };
  db.Client = class FakePg {
    constructor(opts) { this.opts=opts; this.snap=null; }
    async connect() {
      if(this.opts.ssl.servername !== host) throw Object.assign(new Error('cert mismatch'),{code:'ERR_TLS_CERT_ALTNAME_INVALID'});
    }
    async end(){}
    async query(q,params=[]) {
      const s=q.trim().replace(/\s+/g,' ');
      if(s==='BEGIN'||s==='BEGIN READ ONLY'){this.snap=shape(db.data);return {rowCount:0,rows:[]};}
      if(s==='COMMIT'){
        db.commits++; this.snap=null;
        if(db.failAck){db.failAck=false;throw new Error('simulated acknowledgement lost after commit');}
        return {rowCount:0,rows:[]};
      }
      if(s==='ROLLBACK'){if(this.snap)db.data=this.snap;this.snap=null;return {rowCount:0,rows:[]};}
      if(s.includes("current_database() AS db")){
        return {rowCount:1,rows:[{db:'ts_remote_r3',principal:this.opts.user,ver:160015,tls:true,tls_version:'TLSv1.3'}]};
      }
      if(s.startsWith('SELECT pg_advisory_xact_lock'))return {rowCount:1,rows:[{}]};
      if(s.startsWith('SELECT command_fingerprint,original_revision,result FROM')){
        const r=db.data.receipt;
        return {rowCount:r?1:0,rows:r?[shape(r)]:[]};
      }
      if(s.startsWith('SELECT revision FROM'))return {rowCount:db.data.state?1:0,rows:db.data.state?[{revision:1}]:[]};
      if(s.startsWith('INSERT INTO')&&s.includes('.aggregate_state')){
        if(db.data.state)throw new Error('duplicate aggregate');
        db.data.state={revision:1,state:JSON.parse(params[1]),last_event_sha256:params[2]};
        return {rowCount:1,rows:[]};
      }
      if(s.startsWith('INSERT INTO')&&s.includes('.events')){
        if(db.data.event)throw new Error('duplicate event');
        db.data.event={sequence:1,previous_hash:null,event_hash:params[2],payload:JSON.parse(params[3])};
        return {rowCount:1,rows:[]};
      }
      if(s.startsWith('INSERT INTO')&&s.includes('.receipts')){
        if(db.data.receipt)throw new Error('duplicate receipt');
        db.data.receipt={command_fingerprint:params[1],original_revision:1,result:JSON.parse(params[2])};
        return {rowCount:1,rows:[]};
      }
      if(s.startsWith('SELECT a.revision,a.state,a.last_event_sha256')){
        const a=db.data.state,e=db.data.event,r=db.data.receipt;
        return {rowCount:a&&e&&r?1:0,rows:a&&e&&r?[{...shape(a),...shape(e),...shape(r)}]:[]};
      }
      if(s.startsWith('SELECT (SELECT COUNT(*)')){
        return {rowCount:1,rows:[{states:Number(!!db.data.state),events:Number(!!db.data.event),receipts:Number(!!db.data.receipt)}]};
      }
      throw new Error('unexpected mocked query: '+s.slice(0,100));
    }
  };
  return db;
}
async function run(db,phase,who) {
  const device = who==='HOST_A'?'independent-host-a':'independent-host-b';
  const role = who==='HOST_A'?'tsr3_host_a':'tsr3_host_b';
  const env = {
    TS_R3_DATABASE_URL:'postgresql://'+role+':fixture-not-secret@'+host+'/ts_remote_r3?sslmode=verify-full',
    TS_R3_EXPECTED_HOST:host,TS_R3_TEST_ID:'R3-HOST-SYNTHETIC001',
    TS_R3_HOST_LABEL:who,TS_R3_EXPECTED_DB_ROLE:role,
    TS_R3_EXPECTED_DEVICE_DIGEST:selfDigest(device)
  };
  const outs=[];
  const fakeRequire = name => {
    if(name==='node:assert/strict')return mockAssert;
    if(name==='node:crypto')return crypto;
    if(name==='node:os')return {hostname:()=>device};
    if(name==='../r2-node/node_modules/pg')return {Client:db.Client};
    throw new Error('unrecognized import '+name);
  };
  const context={require:fakeRequire,process:{env,argv:['node','fixture',phase]},console:{log:msg=>outs.push(msg),error:msg=>outs.push(msg)},URL};
  await script.runInNewContext(context);
  return outs.join('\n');
}
test('P04 controlled lost-ACK simulation, B fresh recovery, real handler replay/collision, immutable row counts',async()=>{
  const d=database();
  assert.match(await run(d,'write-drop-ack','HOST_A'),/UNKNOWN_CLIENT_ACK/);
  assert.equal(d.commits,1);
  assert.match(await run(d,'recover','HOST_B'),/P04_RECOVER/);
  assert.match(await run(d,'read','HOST_B'),/P03/);
  assert.match(await run(d,'replay','HOST_B'),/mode=replay/);
  assert.match(await run(d,'collision','HOST_B'),/changed_authority=REJECTED/);
  assert.equal(d.commits,2,'A create and B exact replay commit; collision rolls back safely');
  assert.deepEqual(Object.keys(d.data).sort(),['event','receipt','state']);
});
test('UNKNOWN before receipt must fail closed with no host B write or ack reissue',async()=>{
  const d=database();
  await assert.rejects(run(d,'recover','HOST_B'));
  await assert.rejects(run(d,'replay','HOST_B'));
  assert.equal(d.commits,0);
  assert.deepEqual(d.data,empty());
});
test('real ambiguous COMMIT ACK error does not rollback confirmed effect; B alone reconciles',async()=>{
  const d=database();d.failAck=true;
  await assert.rejects(run(d,'write','HOST_A'));
  assert.equal(d.commits,1);
  assert.ok(d.data.receipt);
  assert.match(await run(d,'recover','HOST_B'),/result=CONFIRMED/);
});
test('negative TLS path requires certificate-name mismatch; no SQL needed',async()=>{
  const d=database();
  assert.match(await run(d,'tls-negative','HOST_B'),/P09_TLS_NEGATIVE/);
  assert.equal(d.commits,0);
});
