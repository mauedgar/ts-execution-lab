'use strict';
// R1 is experimental only. Import the exact frozen Product reducers and validators.
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {isDeepStrictEqual}=require('node:util');
const {Client}=require('./r2-node/node_modules/pg');
const root=path.resolve(__dirname,'../../../product');
const K=require(path.join(root,'src/state-kernel-v0'));
const C=require(path.join(root,'src/state-kernel-v0/contracts'));
const {emptyState}=require(path.join(root,'src/state-kernel-v0/store'));
const digest=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
const clone=v=>structuredClone(v);
const NativeDate=Date, fixed='2026-11-04T16:00:00.000Z';
global.Date=class extends NativeDate{constructor(...args){super(...(args.length?args:[fixed]));}static now(){return NativeDate.parse(fixed);}};
class RamStore{
  constructor(doc){this.state=clone(doc?.state??emptyState());this.events=clone(doc?.events??[]);this.verify();}
  read(){this.verify();return {state:clone(this.state),events:clone(this.events)};}
  verify(){
    const reconstructed=emptyState();let prior=null;
    try{
      C.validateState(this.state);
      for(const e of this.events){
        const {hash,...payload}=e;
        C.demand(hash===digest(payload)&&payload.previous_hash===prior&&payload.sequence===reconstructed.revision+1,'MALFORMED_STATE','hash-chain/order');
        if(payload.action==='BOOTSTRAP_IMPORT')C.validateBootstrapProvenance(payload.bootstrap_provenance);
        else C.demand(payload.bootstrap_provenance===undefined,'MALFORMED_STATE','bootstrap shape');
        const previous=reconstructed.aggregates[payload.kind][payload.aggregate_id];
        C.demand((previous?.revision??0)===payload.before_revision&&payload.after?.revision===payload.before_revision+1&&payload.after?.last_event_id===payload.id,'MALFORMED_STATE','event projection');
        reconstructed.aggregates[payload.kind][payload.aggregate_id]=payload.after;
        reconstructed.revision++;prior=hash;
      }
      C.demand(isDeepStrictEqual(reconstructed,this.state),'MALFORMED_STATE','snapshot/replay');
      return {valid:true,revision:this.state.revision,event_count:this.events.length};
    }catch(e){throw new C.KernelError('MALFORMED_STATE',e.message);}
  }
  mutate(expected,fn){
    this.verify();
    C.demand(expected===this.state.revision&&Number.isSafeInteger(expected),'STALE_REVISION','global CAS');
    const proposed=clone(this.state);
    const u=fn(proposed); // Product's original create/transition/satisfy/bootstrap/addObligations reducer.
    C.demand(u&&C.KINDS.includes(u.kind)&&typeof u.id==='string','INVALID_CONTRACT','mutation target');
    for(const kind of C.KINDS){
      for(const [id,old] of Object.entries(this.state.aggregates[kind]))if(kind!==u.kind||id!==u.id)
        C.demand(isDeepStrictEqual(old,proposed.aggregates[kind][id]),'INVALID_CONTRACT','cross-aggregate edit');
      for(const id of Object.keys(proposed.aggregates[kind]))if(kind!==u.kind||id!==u.id)
        C.demand(Object.hasOwn(this.state.aggregates[kind],id),'INVALID_CONTRACT','cross-aggregate insertion');
    }
    const before=this.state.aggregates[u.kind][u.id],after=proposed.aggregates[u.kind][u.id];
    C.demand(after?.revision===(before?.revision??0)+1,'INVALID_CONTRACT','aggregate revision');
    proposed.revision++;after.last_event_id='event-'+proposed.revision;
    C.validateState(proposed);
    C.demand((u.action==='BOOTSTRAP_IMPORT')===(u.bootstrap_provenance!==undefined),'INVALID_CONTRACT','bootstrap flag');
    const p={id:after.last_event_id,sequence:proposed.revision,kind:u.kind,aggregate_id:u.id,before_revision:before?.revision??0,after,previous_hash:this.events.at(-1)?.hash??null,at:u.at,action:u.action};
    if(u.bootstrap_provenance!==undefined)p.bootstrap_provenance=u.bootstrap_provenance;
    const e={...p,hash:digest(p)};
    this.state=proposed;this.events.push(e);
    return {revision:proposed.revision,event_id:p.id,event_hash:e.hash,kind:u.kind,aggregate_id:u.id,aggregate_revision:after.revision};
  }
}
const url=process.env.R1_DATABASE_URL;
assert.match(url||'',/^postgresql:\/\/.*@127\.0\.0\.1:5432\//,'only isolated runner PostgreSQL');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ts-r1-product-'));
const file=new K.FilesystemStateStore(temp);file.initialize();
const auth={kind:'AUTHORITY',id:'AUTH-SYN',location:'synthetic/authority.json'};
const future={kind:'AUTHORITY',id:'AUTH-FUTURE',location:'synthetic/future.json'};
const ev={kind:'EVIDENCE',id:'EV-SYN',location:'synthetic/evidence.json'};
const imported={mode:'IMPORTED_ESTABLISHED_STATE',cutover_at:'2026-01-01T00:00:00.000Z',historical_events_reconstructed:false,authority_refs:[auth],evidence_refs:[ev]};
async function conn(fn){const c=new Client({connectionString:url});await c.connect();try{return await fn(c);}finally{await c.end();}}
async function init(){await conn(async c=>{
  await c.query('CREATE TABLE r1_data (id int PRIMARY KEY, revision int NOT NULL, state text NOT NULL, events text NOT NULL)');
  await c.query('CREATE TABLE r1_receipts (mutation_id text PRIMARY KEY, revision int NOT NULL)');
  await c.query('INSERT INTO r1_data VALUES (1,0,$1,$2)',[JSON.stringify(emptyState()),'[]']);
});}
async function read(){return conn(async c=>{
  const r=(await c.query('SELECT * FROM r1_data WHERE id=1')).rows[0];
  return {state:JSON.parse(r.state),events:JSON.parse(r.events),revision:r.revision};
});}
async function tx(fn,mutation=null){return conn(async c=>{
  await c.query('BEGIN');
  try{
    if(mutation){const prior=await c.query('SELECT revision FROM r1_receipts WHERE mutation_id=$1',[mutation]);
      if(prior.rowCount){await c.query('ROLLBACK');return {existing:true,revision:prior.rows[0].revision};}}
    const r=(await c.query('SELECT * FROM r1_data WHERE id=1 FOR UPDATE')).rows[0];
    const s=new RamStore({state:JSON.parse(r.state),events:JSON.parse(r.events)});
    assert.equal(s.verify().revision,r.revision);
    const result=fn(s),out=s.read();
    await c.query('UPDATE r1_data SET revision=$1,state=$2,events=$3 WHERE id=1',[out.state.revision,JSON.stringify(out.state),JSON.stringify(out.events)]);
    if(mutation)await c.query('INSERT INTO r1_receipts VALUES ($1,$2)',[mutation,out.state.revision]);
    await c.query('COMMIT');return result;
  }catch(e){await c.query('ROLLBACK');throw e;}
});}
async function equal(oracle=file){const r=await read(),l=oracle.read();
  assert.deepEqual(r.state,l.state,'Product aggregate differential');
  assert.deepEqual(r.events,l.events,'exact ordered hash-chain differential');
  assert.equal(r.revision,l.state.revision);return r;}
async function step(name,fn,code){
  let left,right,le,re;const before=file.verify().revision;
  try{left=fn(file);}catch(e){le=e.code||e.message;}
  try{right=await tx(fn);}catch(e){re=e.code||e.message;}
  assert.equal(re,le,name+' error equivalence');
  if(code)assert.equal(le,code,name+' required rejection');
  else{assert.equal(le,undefined,name+' expected success');assert.deepEqual(right,left,name+' receipt parity');}
  const r=await equal();assert.equal(r.revision,before+(code?0:1),name+' no side effects on rejection');
  console.log('PASS|R1|'+name+'|rev='+r.revision);
}
async function main(){
  await init();
  await step('milestone',s=>K.create(s,0,'Milestone','M1',{title:'synthetic'},[auth]));
  await step('taskcycle',s=>K.create(s,1,'TaskCycle','TC1',{responsibility:'synthetic',obligations:[{id:'VERIFY',authority_ref:null},{id:'ACCEPT',authority_ref:'AUTH-FUTURE'}]},[auth]));
  await step('operation',s=>K.create(s,2,'Operation','OP1',{taskcycle_id:'TC1',objective:'synthetic'},[auth]));
  await step('stale',s=>K.transition(s,2,'Operation','OP1','READY'),'STALE_REVISION');
  await step('op_ready',s=>K.transition(s,3,'Operation','OP1','READY'));
  await step('op_running',s=>K.transition(s,4,'Operation','OP1','RUNNING'));
  await step('attempt',s=>K.create(s,5,'ExecutionAttempt','ATT1',{operation_id:'OP1'},[auth]));
  await step('dispatched',s=>K.transition(s,6,'ExecutionAttempt','ATT1','DISPATCHED'));
  await step('unknown',s=>K.transition(s,7,'ExecutionAttempt','ATT1','UNKNOWN'));
  await step('fenced_retry',s=>K.create(s,8,'ExecutionAttempt','ATT2',{operation_id:'OP1'},[auth]),'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  await step('late_obligation',s=>K.addObligations(s,8,'TC1',[{id:'LATE'}],'AUTH-SYN'));
  await step('late_duplicate',s=>K.addObligations(s,9,'TC1',[{id:'LATE'}],'AUTH-SYN'),'INVALID_CONTRACT');
  await step('status_injection',s=>K.addObligations(s,9,'TC1',[{id:'BAD',status:'SATISFIED'}],'AUTH-SYN'),'INVALID_CONTRACT');
  await step('satisfy_verify',s=>K.satisfy(s,9,'TC1','VERIFY'));
  await step('satisfy_late',s=>K.satisfy(s,10,'TC1','LATE'));
  await step('missing_authority',s=>K.satisfy(s,11,'TC1','ACCEPT','AUTH-FUTURE'),'MISSING_REQUIRED_AUTHORITY');
  await step('authority_bound',s=>K.satisfy(s,11,'TC1','ACCEPT','AUTH-FUTURE',future));
  await step('tc_active',s=>K.transition(s,12,'TaskCycle','TC1','ACTIVE'));
  await step('reconcile_attempt',s=>K.transition(s,13,'ExecutionAttempt','ATT1','FAILED',{authority_ref:'AUTH-SYN',outcome:'FAIL',result_refs:[ev]}));
  await step('tc_acceptance',s=>K.transition(s,14,'TaskCycle','TC1','PENDING_ACCEPTANCE'));
  await step('tc_closed',s=>K.transition(s,15,'TaskCycle','TC1','CLOSED',{authority_ref:'AUTH-SYN',disposition_ref:'synthetic/closure'}));
  await step('bootstrap',s=>K.bootstrapTaskCycle(s,16,{id:'TC-IMP',responsibility:'import',state:'ACTIVE',obligations:[{id:'ACCEPT',status:'SATISFIED',authority_ref:'AUTH-SYN'}],bootstrap_provenance:imported}));
  await step('bootstrap_negative',s=>K.bootstrapTaskCycle(s,17,{id:'BAD-IMP',responsibility:'import',state:'ACTIVE',obligations:[],bootstrap_provenance:{...imported,historical_events_reconstructed:true}}),'INVALID_CONTRACT');
  const cold=new K.FilesystemStateStore(temp),r=await equal(cold);
  const ports=require(path.join(root,'src/operational-spine-v0/state-kernel-adapter'));
  const one=ports.createStateKernelTaskCycleLifecycle({store:cold});
  const two=ports.createStateKernelTaskCycleLifecycle({store:new RamStore(r)});
  assert.deepEqual(two.snapshot('TC1'),one.snapshot('TC1'));
  assert.deepEqual(two.snapshot('TC-IMP'),one.snapshot('TC-IMP'));
  assert.equal(two.hasUnreconciledExecution('TC1'),false);
  console.log('PASS|R1|cold_reopen|ports=equal|bootstrap_provenance=equal');
  const rev=r.revision, contenders=[
    s=>K.transition(s,rev,'Milestone','M1','ACTIVE'),
    s=>K.create(s,rev,'TaskCycle','TC-RACE',{responsibility:'race',obligations:[]},[auth])
  ];
  const results=await Promise.allSettled(contenders.map(fn=>tx(fn)));
  const winner=results.findIndex(x=>x.status==='fulfilled');
  assert.equal(results.filter(x=>x.status==='fulfilled').length,1);
  assert.equal(results.filter(x=>x.status==='rejected'&&x.reason.code==='STALE_REVISION').length,1);
  contenders[winner](cold);await equal(cold);
  console.log('PASS|R1|global_cas_race|commits=1|stale=1');
  const next=(await read()).revision;
  const ack=s=>K.create(s,next,'Milestone','M-ACK',{title:'lost ack'},[auth]);
  await tx(ack,'SYNTHETIC-MUTATION-R1-001');ack(cold);
  const receipt=await tx(ack,'SYNTHETIC-MUTATION-R1-001');
  assert.deepEqual(receipt,{existing:true,revision:next+1});await equal(cold);
  console.log('PASS|R1|lost_ack|receipt=found|no_second_effect');
  const bad=await read();bad.events[0].hash='0'.repeat(64);
  assert.throws(()=>new RamStore(bad),{code:'MALFORMED_STATE'});await equal(cold);
  console.log('PASS|R1|tamper|fails_closed|original_reducers=exact_product');
  fs.rmSync(temp,{recursive:true,force:true});
}
main().catch(e=>{console.error('FAIL|R1|'+(e.stack||e));process.exitCode=1;});
