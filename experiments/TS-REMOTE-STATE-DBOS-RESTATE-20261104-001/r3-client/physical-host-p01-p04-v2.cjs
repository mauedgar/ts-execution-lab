'use strict';
// R3 bounded client. No credentials in source, args, output or Git transport.
// Physical provenance and A-offline proof must come from independent provider
// host/device receipts; env labels and this program alone never prove those.
const crypto=require('node:crypto');
const os=require('node:os');
const core=require('./r3-command-core.cjs');
const {SafeError,planned,applyCreate,resolveUnknown,inspect}=core;
const EXPECTED_HOST='ep-ancient-flower-b6eb9w6c.c-2.sa-east-1.aws.neon.tech';
const DATABASE='ts_remote_r3';
const ROLES=Object.freeze({HOST_A:'tsr3_host_a_rw',HOST_B:'tsr3_host_b_rw'});
const allowedPhases=new Set(['probe','write','write-ack-loss','read','reconcile','replay','collision']);
const safe=(ok,code)=>{if(!ok)throw new SafeError(code);};
function input() {
 const phase=process.argv[2];
 safe(allowedPhases.has(phase),'INVALID_PHASE');
 const host=process.env.TS_R3_HOST_LABEL;
 safe(Object.hasOwn(ROLES,host),'INVALID_HOST_LABEL');
 safe((host==='HOST_A' && ['probe','write','write-ack-loss'].includes(phase)) ||
   (host==='HOST_B' && ['probe','read','reconcile','replay','collision'].includes(phase)), 'PHASE_ROLE_VIOLATION');
 const id=process.env.TS_R3_TEST_ID;
 const expected=planned(id);
 const actualHostHash=crypto.createHash('sha256').update(os.hostname().toLowerCase()).digest('hex');
 const externallyEnrolledHash=process.env.TS_R3_ENROLLED_HOST_SHA256;
 safe(/^[a-f0-9]{64}$/.test(externallyEnrolledHash||'') &&
   externallyEnrolledHash===actualHostHash,'HOST_ENROLLMENT_MISMATCH');
 // Host enrollment must be independently observed by Control, not merely asserted here.
 const ref=process.env.TS_R3_ENROLLMENT_RECEIPT_REF;
 safe(typeof ref==='string' && /^TS-R3-P01-(HOST_A|HOST_B)-[A-Za-z0-9-]{8,60}$/.test(ref),
   'HOST_RECEIPT_MISSING');
 safe(ref.includes(host),'HOST_RECEIPT_MISMATCH');
 const secret=process.env.TS_R3_DATABASE_URL;
 safe(typeof secret==='string'&&secret.length>0&&secret.length<2048,'MISSING_SECRET');
 let u;
 try { u=new URL(secret); } catch { throw new SafeError('INVALID_SECRET_FORMAT'); }
 safe(['postgresql:','postgres:'].includes(u.protocol),'INVALID_DB_PROTOCOL');
 safe(u.hostname===EXPECTED_HOST && Number(u.port||5432)===5432,'INVALID_DB_HOST');
 safe(u.pathname==='/'+DATABASE,'INVALID_DB_NAME');
 safe(!u.hash,'INVALID_DB_FRAGMENT');
 safe([...u.searchParams].length<=1 && [...u.searchParams.keys()].every(k=>k==='sslmode') &&
   (!u.searchParams.has('sslmode') || u.searchParams.get('sslmode')==='verify-full'),
   'INVALID_DB_OPTIONS');
 let user,pass;
 try {user=decodeURIComponent(u.username);pass=decodeURIComponent(u.password);}catch{throw new SafeError('INVALID_SECRET_FORMAT');}
 safe(user===ROLES[host] && pass.length>0, 'INVALID_DB_PRINCIPAL');
 return {phase,host,plan:expected,hostHash:actualHostHash,
   config:{host:EXPECTED_HOST,port:5432,database:DATABASE,user,password:pass,
     connectionTimeoutMillis:15000,ssl:{rejectUnauthorized:true,servername:EXPECTED_HOST}}};
}
async function main() {
 const {phase,host,plan,hostHash,config}=input();
 // Lazy dependency load: can inspect/parse without a configured credential.
 const {Client}=require('../r2-node/node_modules/pg');
 const c=new Client(config);
 try{
   await c.connect();
   const q=await c.query(`SELECT current_database() AS db,current_user AS principal,
     current_setting('server_version_num')::int AS version,
     (SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS ssl,
     (SELECT version FROM pg_stat_ssl WHERE pid=pg_backend_pid()) AS tls`);
   safe(q.rowCount===1 && q.rows[0].db===DATABASE && q.rows[0].principal===config.user,
     'DATABASE_IDENTITY_MISMATCH');
   safe(Number(q.rows[0].version)>=160000 && Number(q.rows[0].version)<170000,
     'PG_VERSION_MISMATCH');
   safe(q.rows[0].ssl===true && /^TLSv1\.[23]$/.test(q.rows[0].tls||''),'TLS_NOT_VERIFIED');
   if(phase==='probe'){
     process.stdout.write(`PASS|R3|P01_CLIENT|role=${host}|host_sha256=${hostHash.slice(0,16)}|tls=verified|pg=16|external_host_proof=separate\n`);
     return;
   }
   if(phase==='write' || phase==='write-ack-loss'){
     const result=await applyCreate(c,plan);
     safe(result.disposition==='COMMITTED','NOT_NEW_COMMAND');
     if(phase==='write-ack-loss'){
       // An injected client crash AFTER successful COMMIT; an actual network
       // ACK-loss unknown outcome requires B's separate read-only reconcile.
       process.exit(73);
     }
     await inspect(c,plan);
     process.stdout.write(`PASS|R3|P02_HOST_A|committed=1|event=1|receipt=1|host_sha256=${hostHash.slice(0,16)}\n`);
     return;
   }
   if(phase==='read'){
     await inspect(c,plan);
     process.stdout.write(`PASS|R3|P03_HOST_B|state=1|event=1|receipt=1|host_sha256=${hostHash.slice(0,16)}|A_offline=EXTERNAL_PROOF_REQUIRED\n`);
     return;
   }
   if(phase==='reconcile'){
     const r=await resolveUnknown(c,plan);
     if(r.disposition!=='CONFIRMED'){
       process.stdout.write('BLOCKED|R3|UNKNOWN_EFFECT|receipt_not_observed|retry_authorized=false\n');
       process.exitCode=2;
       return;
     }
     process.stdout.write('PASS|R3|ACK_RECONCILED_HOST_B|effect=CONFIRMED|receipt=1|new_effect=0\n');
     return;
   }
   if(phase==='replay'){
     const observed=await resolveUnknown(c,plan);
     if(observed.effect==='UNKNOWN') {
       process.stdout.write('BLOCKED|R3|UNKNOWN_EFFECT|receipt_not_observed|retry_authorized=false\n');
       process.exitCode=2;
       return;
     }
     const before=await inspect(c,plan);
     const reply=await applyCreate(c,plan,{allowCreate:false}); // SAME handler, B never inserts or locks for UPDATE.
     safe(reply.disposition==='RECONCILED','DUPLICATE_MUTATION');
     const after=await inspect(c,plan);
     safe(after.hash===before.hash && after.effects===1 && after.receipts===1,'EFFECT_CHANGED');
     process.stdout.write('PASS|R3|P04_HOST_B|same_command_reconciled=1|effect=1|receipt=1\n');
     return;
   }
   if(phase==='collision'){
     const observed=await resolveUnknown(c,plan);
     if(observed.effect==='UNKNOWN') {
       process.stdout.write('BLOCKED|R3|UNKNOWN_EFFECT|receipt_not_observed|retry_authorized=false\n');
       process.exitCode=2;
       return;
     }
     const before=await inspect(c,plan);
     const altered={...plan.cmd,authority_refs:['AUTH-DIFFERENT-R3']};
     const collisionPlan=planned(plan.id,altered);
     try {
       await applyCreate(c,collisionPlan,{allowCreate:false}); // SAME command handler in B read-only mode.
       throw new SafeError('COLLISION_ACCEPTED');
     } catch(e) {
       safe(e instanceof SafeError && e.code==='MUTATION_IDENTITY_COLLISION','COLLISION_NOT_REJECTED');
     }
     const after=await inspect(c,plan);
     safe(after.hash===before.hash && after.effects===1 && after.receipts===1,'COLLISION_CHANGED_EFFECT');
     process.stdout.write('PASS|R3|P04_HOST_B|changed_authority_rejected=1|effect=1|receipt=1\n');
     return;
   }
 }finally{try{await c.end();}catch{}}
}
// The error handler NEVER prints Error.toString(), stack or parsed URL: those
// may reveal passwords supplied by local OS secret injection.
if(require.main===module) main().catch(e=>{
 const code=e instanceof SafeError?e.code:'UNCLASSIFIED_SAFE_FAILURE';
 if(code==='RECEIPT_NOT_OBSERVED_UNKNOWN') {
   process.stderr.write('BLOCKED|R3|UNKNOWN_EFFECT|receipt_not_observed|retry_authorized=false\n');
   process.exitCode=2;
 } else {
   process.stderr.write(`FAIL|R3|${code}|secret_output=false\n`);
   process.exitCode=1;
 }
});
module.exports={input};
