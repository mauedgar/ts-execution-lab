'use strict';
// TS Execution Engineering R3 experiment — NONPRODUCT, NO HISTORICAL DATA.
// Never put passwords/connection strings in logs, Git/Transport, or OneDrive.
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const os=require('node:os');
const {Client}=require('../r2-node/node_modules/pg');
const sha=v=>crypto.createHash('sha256').update(v).digest('hex');
const {TS_R3_DATABASE_URL,TS_R3_EXPECTED_HOST,TS_R3_TEST_ID,TS_R3_HOST_LABEL}=process.env;
const phase=process.argv[2];
assert(['probe','write','write-lost-ack','read','replay','collision','reconcile'].includes(phase),'unsupported phase');
assert(/^(HOST_A|HOST_B)$/.test(TS_R3_HOST_LABEL||''),'host label required');
assert(/^R3-HOST-[A-Za-z0-9_-]{8,50}$/.test(TS_R3_TEST_ID||''),'unique synthetic test id');
assert(/^ep-[a-z0-9-]+\.c-2\.sa-east-1\.aws\.neon\.tech$/.test(TS_R3_EXPECTED_HOST||''),'expected Neon host');
assert(typeof TS_R3_DATABASE_URL==='string'&&TS_R3_DATABASE_URL.length<2048,'private database URL required');
let u;
try{u=new URL(TS_R3_DATABASE_URL);}catch{throw Error('INVALID_PRIVATE_URL');}
assert(u.protocol==='postgresql:'||u.protocol==='postgres:','Postgres URL');
assert(u.hostname===TS_R3_EXPECTED_HOST,'host pin mismatch');
assert(u.pathname==='/ts_remote_r3','database pin mismatch');
assert(!u.searchParams.has('sslmode')||u.searchParams.get('sslmode')==='verify-full',
  'TLS mode must be verify-full');
const options={
  host:u.hostname,port:Number(u.port||5432),database:'ts_remote_r3',
  user:decodeURIComponent(u.username),password:decodeURIComponent(u.password),
  connectionTimeoutMillis:15000,
  ssl:{rejectUnauthorized:true,servername:u.hostname}
};
assert(options.port===5432&&options.user&&options.password,'credential and port preconditions');
if(['write','write-lost-ack'].includes(phase))assert(TS_R3_HOST_LABEL==='HOST_A','only host A writes genesis');
if(['read','replay','collision','reconcile'].includes(phase))assert(TS_R3_HOST_LABEL==='HOST_B','host B independently reads/reconciles');
const expectedRole=TS_R3_HOST_LABEL==='HOST_A'?'tsr3_host_a_rw':'tsr3_host_b_rw';
assert(options.user===expectedRole,'wrong credentialed role for A/B');
const schema='ts_r3_synthetic_20261105_001';
const id=TS_R3_TEST_ID;
const eventId=id+'-event1';
const mutationId=id+'-command1';
const command={type:'Create',kind:'TaskCycle',id,expected_revision:0,
  authority_refs:['AUTH-SYNTHETIC-R3'],fields:{responsibility:'synthetic R3 two physical hosts',obligations:[]}};
const commandHash=sha(JSON.stringify(command));
const state={kind:'TaskCycle',id,state:'READY',revision:1,synthetic:true};
const eventPayload={action:'CREATE',kind:'TaskCycle',id,sequence:1,previous_hash:null,after:state};
const eventHash=sha(JSON.stringify(eventPayload));
async function verify(client){
 const query=`SELECT a.revision,a.state,a.last_event_sha256,e.sequence,e.previous_hash,
 e.event_hash,e.payload,r.command_fingerprint,r.original_revision,r.result
 FROM ${schema}.aggregate_state a
 JOIN ${schema}.events e ON e.id=a.id
 JOIN ${schema}.receipts r ON r.mutation_id=$2
 WHERE a.id=$1 AND e.event_id=$3`;
 const q=await client.query(query,[id,mutationId,eventId]);
 assert.equal(q.rows.length,1,'one aggregate/event/receipt join');
 const row=q.rows[0];
 assert.equal(Number(row.revision),1);
 assert.deepEqual(row.state,state);
 assert.equal(row.last_event_sha256,eventHash);
 assert.equal(Number(row.sequence),1);
 assert.equal(row.previous_hash,null);
 assert.equal(row.event_hash,eventHash);
 assert.deepEqual(row.payload,eventPayload);
 assert.equal(row.command_fingerprint,commandHash);
 assert.equal(Number(row.original_revision),1);
 assert.deepEqual(row.result,{revision:1,event_id:eventId,synthetic:true});
 const counts=await client.query('SELECT (SELECT count(*) FROM '+schema+'.aggregate_state WHERE id=$1) AS states, (SELECT count(*) FROM '+schema+'.events WHERE id=$1) AS events, (SELECT count(*) FROM '+schema+'.receipts WHERE mutation_id=$2) AS receipts',[id,mutationId]);
 assert.equal(Number(counts.rows[0].states),1);
 assert.equal(Number(counts.rows[0].events),1);
 assert.equal(Number(counts.rows[0].receipts),1);
 return {revision:1,effects:1,receipts:1,hash:eventHash.slice(0,16)};
}
// Same command dispatcher handles first invocation, replay and collisions.
// B never creates a missing effect while reconciling an UNKNOWN A outcome.
async function processCommand(c,requested,allowNew){
 const expectedHash=sha(JSON.stringify(requested));
 let commitAttempted=false,txOpen=false;
 await c.query('BEGIN');txOpen=true;
 try{
   const row=await c.query('SELECT command_fingerprint,original_revision,result FROM '+schema+'.receipts WHERE mutation_id=$1 FOR UPDATE',[mutationId]);
   if(row.rowCount){
     if(row.rows[0].command_fingerprint!==expectedHash){
       await c.query('ROLLBACK');txOpen=false;
       return {status:'MUTATION_IDENTITY_COLLISION',effect:'NONE'};
     }
     assert.equal(Number(row.rows[0].original_revision),1);
     const original=row.rows[0].result;
     assert.deepEqual(original,{revision:1,event_id:eventId,synthetic:true});
     commitAttempted=true;
     await c.query('COMMIT');txOpen=false;
     return {status:'RECONCILED',original};
   }
   if(!allowNew){
     await c.query('ROLLBACK');txOpen=false;
     return {status:'UNKNOWN',effect:'NONE_OBSERVED',no_retry:true};
   }
   assert.deepEqual(requested,command,'only original synthetic A command can write');
   await c.query('INSERT INTO '+schema+'.aggregate_state(id,revision,state,last_event_sha256) VALUES ($1,1,$2::jsonb,$3)',[id,JSON.stringify(state),eventHash]);
   await c.query('INSERT INTO '+schema+'.events(event_id,id,sequence,previous_hash,event_hash,payload) VALUES ($1,$2,1,NULL,$3,$4::jsonb)',[eventId,id,eventHash,JSON.stringify(eventPayload)]);
   await c.query('INSERT INTO '+schema+'.receipts(mutation_id,command_fingerprint,original_revision,result) VALUES ($1,$2,1,$3::jsonb)',[mutationId,expectedHash,JSON.stringify({revision:1,event_id:eventId,synthetic:true})]);
   commitAttempted=true;
   await c.query('COMMIT');txOpen=false;
   return {status:'COMMITTED'};
 }catch{
   if(txOpen&&!commitAttempted){try{await c.query('ROLLBACK');}catch{}}
   if(commitAttempted)throw Error('UNKNOWN_COMMIT_EFFECT_REQUIRES_RECONCILIATION');
   throw Error('FAIL_CLOSED_NO_CONFIRMED_EFFECT');
 }
}
async function main(){
 const c=new Client(options);
 try{
   await c.connect();
   const q=await c.query(`SELECT current_database() AS db, current_user AS db_user,
     current_setting('server_version_num')::int AS ver,
     (SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls,
     (SELECT version FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls_version`);
   assert.equal(q.rows[0].db,'ts_remote_r3');
    assert.equal(q.rows[0].db_user,expectedRole,'DB principal must match physical role');
    const roles=await c.query('SELECT rolsuper FROM pg_roles WHERE rolname=current_user');
    assert.equal(roles.rows[0].rolsuper,false,'non-superuser role required');
   assert(q.rows[0].ver>=160000&&q.rows[0].ver<170000,'PostgreSQL 16 required');
   assert.equal(q.rows[0].tls,true,'TLS required over external connection');
   const hostFingerprint=sha(os.hostname()).slice(0,16);
   // Do not log db URL, user, password, hostnames or OS identity.
   if(phase==='probe'){
     console.log(`PASS|R3|P01|host=${TS_R3_HOST_LABEL}|fingerprint=${hostFingerprint}|tls=${q.rows[0].tls_version}|pg=16|scope=synthetic`);
     return;
   }
   if(['write','write-lost-ack'].includes(phase)){
     const answer=await processCommand(c,command,true);
     assert.equal(answer.status,'COMMITTED','writer attempted an existing effect');
     if(phase==='write-lost-ack'){
       // Inject client loss AFTER server COMMIT but before A publishes ACK.
       // B must inspect the immutable receipt without recreating the effect.
       process.exit(73);
     }
     const v=await verify(c);
     console.log('PASS|R3|P02|host=HOST_A|fingerprint='+hostFingerprint+'|revision='+v.revision+'|effect=1|receipt=1|event_hash='+v.hash);
     return;
   }
   if(phase==='read'){
     const v=await verify(c);
     console.log('PASS|R3|P03|host=HOST_B|fingerprint='+hostFingerprint+'|revision='+v.revision+'|event_hash='+v.hash+'|A_absence=external_proof_required');
     return;
   }
   // Replay, collision, and uncertain ACK reconciliation use the exact same
   // immutable-command dispatcher as A, but do not authorize any new effect.
   const requested=phase==='collision'?{...command,authority_refs:['AUTH-DIFFERENT']}:command;
   const answer=await processCommand(c,requested,false);
   if(answer.status==='UNKNOWN'){
     console.log('UNKNOWN|R3|P04|host=HOST_B|missing_receipt=true|no_new_effect=true');
     process.exitCode=2;
     return;
   }
   if(phase==='collision'){
     assert.equal(answer.status,'MUTATION_IDENTITY_COLLISION','changed authority MUST reject');
     const v=await verify(c);
     console.log('PASS|R3|P04|host=HOST_B|authority_collision_rejected=true|effects='+v.effects+'|receipts='+v.receipts);
     return;
   }
   assert.equal(answer.status,'RECONCILED','original immutable receipt required');
   const v=await verify(c);
   if(phase==='reconcile')
     console.log('CONFIRMED|R3|P04|host=HOST_B|lost_ack_reconciled=true|effects='+v.effects+'|receipts='+v.receipts);
   else
     console.log('PASS|R3|P04|host=HOST_B|dispatcher_replayed=true|effects='+v.effects+'|receipts='+v.receipts);
 }finally{await c.end().catch(()=>{});}
}
main().catch(()=>{console.error('FAIL|R3|'+phase+'|safe_error=true|no_credentials_logged');process.exitCode=1;});
