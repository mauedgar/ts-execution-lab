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
assert(['probe','write','read','replay','collision'].includes(phase),'unsupported phase');
assert(/^(HOST_A|HOST_B)$/.test(TS_R3_HOST_LABEL||''),'host label required');
assert(/^R3-HOST-[A-Za-z0-9_-]{8,50}$/.test(TS_R3_TEST_ID||''),'unique synthetic test id');
assert(/^ep-[a-z0-9-]+\.c-2\.sa-east-1\.aws\.neon\.tech$/.test(TS_R3_EXPECTED_HOST||''),'expected Neon host');
assert(typeof TS_R3_DATABASE_URL==='string'&&TS_R3_DATABASE_URL.length<2048,'private database URL required');
const u=new URL(TS_R3_DATABASE_URL);
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
if(phase==='write')assert(TS_R3_HOST_LABEL==='HOST_A','only host A writes genesis');
if(['read','replay','collision'].includes(phase))assert(TS_R3_HOST_LABEL==='HOST_B','host B independently reads/reconciles');
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
 return {revision:1,effects:1,receipts:1,hash:eventHash.slice(0,16)};
}
async function main(){
 const c=new Client(options);
 try{
   await c.connect();
   const q=await c.query(`SELECT current_database() AS db,
     current_setting('server_version_num')::int AS ver,
     (SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls,
     (SELECT version FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls_version`);
   assert.equal(q.rows[0].db,'ts_remote_r3');
   assert(q.rows[0].ver>=160000&&q.rows[0].ver<170000,'PostgreSQL 16 required');
   assert.equal(q.rows[0].tls,true,'TLS required over external connection');
   const hostFingerprint=sha(os.hostname()).slice(0,16);
   // Do not log db URL, user, password, hostnames or OS identity.
   if(phase==='probe'){
     console.log(`PASS|R3|P01|host=${TS_R3_HOST_LABEL}|fingerprint=${hostFingerprint}|tls=${q.rows[0].tls_version}|pg=16|scope=synthetic`);
     return;
   }
   if(phase==='write'){
     await c.query('BEGIN');
     try{
       const existing=await c.query(`SELECT 1 FROM ${schema}.aggregate_state WHERE id=$1`,[id]);
       assert.equal(existing.rowCount,0,'attempt already exists; no retry');
       await c.query(`INSERT INTO ${schema}.aggregate_state(id,revision,state,last_event_sha256)
         VALUES ($1,1,$2::jsonb,$3)`,[id,JSON.stringify(state),eventHash]);
       await c.query(`INSERT INTO ${schema}.events(event_id,id,sequence,previous_hash,event_hash,payload)
         VALUES ($1,$2,1,NULL,$3,$4::jsonb)`,
         [eventId,id,eventHash,JSON.stringify(eventPayload)]);
       await c.query(`INSERT INTO ${schema}.receipts(mutation_id,command_fingerprint,original_revision,result)
         VALUES ($1,$2,1,$3::jsonb)`,
         [mutationId,commandHash,JSON.stringify({revision:1,event_id:eventId,synthetic:true})]);
       await c.query('COMMIT');
     }catch(err){await c.query('ROLLBACK');throw err;}
     const v=await verify(c);
     console.log(`PASS|R3|P02|host=HOST_A|fingerprint=${hostFingerprint}|revision=${v.revision}|effect=1|receipt=1|event_hash=${v.hash}`);
     return;
   }
   const v=await verify(c);
   if(phase==='read'){
     console.log(`PASS|R3|P03|host=HOST_B|fingerprint=${hostFingerprint}|revision=${v.revision}|event_hash=${v.hash}|A_absence=external_proof_required`);
     return;
   }
   await c.query('BEGIN');
   try{
     const receipt=await c.query(`SELECT command_fingerprint,original_revision,result
       FROM ${schema}.receipts WHERE mutation_id=$1 FOR UPDATE`,[mutationId]);
     assert.equal(receipt.rowCount,1,'missing receipt');
     const compared=phase==='collision'?sha(JSON.stringify({...command,authority_refs:['AUTH-DIFFERENT']})):commandHash;
     if(phase==='collision'){
       assert.notEqual(receipt.rows[0].command_fingerprint,compared,'mismatched authority accepted');
       await c.query('ROLLBACK');
       const after=await verify(c);
       assert.equal(after.hash,v.hash);
       console.log('PASS|R3|P04|host=HOST_B|mismatched_authority=rejected|effect=1|receipt=1');
       return;
     }
     assert.equal(receipt.rows[0].command_fingerprint,compared,'receipt identity mismatch');
     assert.equal(Number(receipt.rows[0].original_revision),1);
     await c.query('COMMIT');
     const after=await verify(c);
     assert.equal(after.hash,v.hash);
     console.log('PASS|R3|P04|host=HOST_B|reconciled=true|effect=1|receipt=1');
   }catch(err){try{await c.query('ROLLBACK');}catch{}throw err;}
 }finally{await c.end().catch(()=>{});}
}
main().catch(()=>{console.error('FAIL|R3|'+phase+'|safe_error=true|no_credentials_logged');process.exitCode=1;});
