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
        C.demand(hash===digest(payload)&&payload.previous_hash===prior&&payload.sequence===reconstructed.revision+1&&C.KINDS.includes(payload.kind),'MALFORMED_STATE','hash-chain/order/kind');
        if(payload.action==='BOOTSTRAP_IMPORT'){
          C.demand(payload.kind==='TaskCycle'&&payload.before_revision===0&&payload.bootstrap_provenance!==undefined,'MALFORMED_STATE','bootstrap event type/shape');
          C.validateBootstrapProvenance(payload.bootstrap_provenance);
          const p=payload.bootstrap_provenance;
          C.demand(payload.after?.created_at===p.cutover_at&&payload.after?.updated_at===p.cutover_at,'MALFORMED_STATE','bootstrap cutover');
          C.demand(isDeepStrictEqual(payload.after?.authority_refs,p.authority_refs),'MALFORMED_STATE','bootstrap authority provenance');
          C.demand(payload.after?.terminal_disposition_ref===null&&!['CLOSED','CANCELLED'].includes(payload.after?.state),'MALFORMED_STATE','bootstrap nonterminal');
        }else C.demand(payload.bootstrap_provenance===undefined,'MALFORMED_STATE','unexpected bootstrap provenance');
        const previous=reconstructed.aggregates[payload.kind][payload.aggregate_id];
        C.demand((previous?.revision??0)===payload.before_revision&&payload.after?.id===payload.aggregate_id&&payload.after?.kind===payload.kind&&payload.after?.revision===payload.before_revision+1&&payload.after?.last_event_id===payload.id,'MALFORMED_STATE','event correspondence');
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
  await c.query('CREATE TABLE r1_receipts (mutation_id text PRIMARY KEY, fingerprint text NOT NULL, revision int NOT NULL, response text NOT NULL)');
  await c.query('INSERT INTO r1_data VALUES (1,0,$1,$2)',[JSON.stringify(emptyState()),'[]']);
});}
async function read(){return conn(async c=>{
  const r=(await c.query('SELECT * FROM r1_data WHERE id=1')).rows[0];
  return {state:JSON.parse(r.state),events:JSON.parse(r.events),revision:r.revision};
});}
// R1 keyed mutations use an explicit frozen request, NOT an opaque callback or function.toString().
// A command receipt must distinguish exact JSON input, not lossy
// JSON.stringify aliases (NaN/Infinity->null, -0->0, missing undefined).
function requireExactJson(value,where='$',seen=new WeakSet()){
  if(value===null||typeof value==='string'||typeof value==='boolean')return;
  if(typeof value==='number'){
    C.demand(Number.isFinite(value)&&!Object.is(value,-0),'INVALID_CONTRACT','non-JSON number '+where);
    return;
  }
  C.demand(typeof value==='object'&&value!==null,'INVALID_CONTRACT','non-JSON value '+where);
  const array=Array.isArray(value);
  C.demand(Object.getPrototypeOf(value)===(array?Array.prototype:Object.prototype),
           'INVALID_CONTRACT','exotic prototype '+where);
  C.demand(!seen.has(value),'INVALID_CONTRACT','cyclic JSON '+where);
  seen.add(value);
  const keys=Reflect.ownKeys(value);
  if(array){
    C.demand(keys.length===value.length+1,'INVALID_CONTRACT','sparse/extended JSON array '+where);
    for(let i=0;i<value.length;i++){
      const d=Object.getOwnPropertyDescriptor(value,String(i));
      C.demand(d&&d.enumerable&&Object.hasOwn(d,'value'),'INVALID_CONTRACT','invalid array entry '+where);
      requireExactJson(d.value,where+'['+i+']',seen);
    }
  }else{
    for(const key of keys){
      C.demand(typeof key==='string'&&!['__proto__','constructor','prototype'].includes(key),
               'INVALID_CONTRACT','unsafe JSON key '+where);
      const d=Object.getOwnPropertyDescriptor(value,key);
      C.demand(d&&d.enumerable&&Object.hasOwn(d,'value'),
               'INVALID_CONTRACT','accessor/nonenumerable JSON key '+where);
      requireExactJson(d.value,where+'.'+key,seen);
    }
  }
  seen.delete(value);
}
function requireOnlyKeys(value,allowed,scope){
  C.demand(Object.keys(value).every(key=>allowed.includes(key)),
    'INVALID_CONTRACT','unexpected '+scope+' fields');
}
function normalizeRequest(input){
  C.demand(input&&Object.getPrototypeOf(input)===Object.prototype&&!Array.isArray(input),'INVALID_CONTRACT','immutable command envelope');
  // No opaque callbacks or replay of unversioned command arguments: strict JSON
  // command shapes preserve revisions, identity, payload and authority for receipts.
  const shapes={
    MilestoneCreate:{required:['authority_refs','expected_revision','fields','id','type'],optional:[]},
    Create:{required:['authority_refs','expected_revision','fields','id','kind','type'],optional:[]},
    Transition:{required:['expected_revision','id','kind','options','target','type'],optional:[]},
    Satisfy:{required:['expected_revision','id','obligation_id','type'],optional:['authority_ref','authority_reference']},
    AddObligations:{required:['additions','authority_ref','expected_revision','id','type'],optional:['authority_reference']},
    BootstrapTaskCycle:{required:['expected_revision','request','type'],optional:[]}
  };
  requireExactJson(input);
  const shape=typeof input.type==='string'&&Object.hasOwn(shapes,input.type)?shapes[input.type]:undefined;
  C.demand(shape!==undefined,'INVALID_CONTRACT','recognized keyed command');
  const keys=Object.keys(input);
  C.demand(shape.required.every(k=>Object.hasOwn(input,k))&&
           keys.every(k=>[...shape.required,...shape.optional].includes(k)),
           'INVALID_CONTRACT','exact keyed command fields');
  C.demand(Number.isSafeInteger(input.expected_revision)&&input.expected_revision>=0,
           'INVALID_CONTRACT','expected global revision');
  if(input.type!=='BootstrapTaskCycle')
    C.demand(typeof input.id==='string'&&input.id.length>0,'INVALID_CONTRACT','aggregate identity');
  if(input.type==='Create'||input.type==='MilestoneCreate'){
    C.demand(input.type==='MilestoneCreate'||C.KINDS.includes(input.kind),'INVALID_CONTRACT','aggregate kind');
    C.demand(input.fields&&Object.getPrototypeOf(input.fields)===Object.prototype,'INVALID_CONTRACT','fields');
    C.refs(input.authority_refs);
    if(input.type==='Create'){
      const allowed={Milestone:['title'],TaskCycle:['responsibility','obligations'],
        Operation:['taskcycle_id','objective'],ExecutionAttempt:['operation_id']};
      requireOnlyKeys(input.fields,allowed[input.kind],'Create '+input.kind);
    }
    if(input.type==='MilestoneCreate')
      C.demand(Object.keys(input.fields).join(',')==='title'&&typeof input.fields.title==='string','INVALID_CONTRACT','legacy MilestoneCreate fields');
  }
  if(input.type==='Transition'){
    C.demand(C.KINDS.includes(input.kind)&&typeof input.target==='string'&&
      input.options&&Object.getPrototypeOf(input.options)===Object.prototype,
      'INVALID_CONTRACT','transition identity/options');
    const allowed=(input.kind==='TaskCycle'&&input.target==='CLOSED')
       ?['authority_ref','disposition_ref']
       :(input.kind==='Operation'&&input.target==='COMPLETED')
       ?['result_ref']
       :(input.kind==='ExecutionAttempt'&&['FAILED','COMPLETED','BLOCKED','UNAVAILABLE','CANCELLED'].includes(input.target))
       ?['authority_ref','outcome','result_refs']
       :(input.kind==='ExecutionAttempt'&&input.target==='UNKNOWN')
       ?['result_refs']
       :[];
    requireOnlyKeys(input.options,allowed,'Transition options');
  }
  if(input.type==='Satisfy'){
    C.demand(typeof input.obligation_id==='string','INVALID_CONTRACT','obligation identity');
    if(Object.hasOwn(input,'authority_ref'))C.demand(typeof input.authority_ref==='string','INVALID_CONTRACT','authority identity');
    if(Object.hasOwn(input,'authority_reference'))C.refs([input.authority_reference]);
  }
  if(input.type==='AddObligations'){
    C.demand(Array.isArray(input.additions)&&typeof input.authority_ref==='string','INVALID_CONTRACT','obligation extension');
    if(Object.hasOwn(input,'authority_reference'))C.refs([input.authority_reference]);
  }
  if(input.type==='BootstrapTaskCycle'){
    C.demand(input.request&&Object.getPrototypeOf(input.request)===Object.prototype,'INVALID_CONTRACT','bootstrap request');
    requireOnlyKeys(input.request,['id','responsibility','state','obligations','bootstrap_provenance'],'BootstrapTaskCycle');
  }
  const normalized=structuredClone(input);
  C.demand(JSON.stringify(normalized)===JSON.stringify(input),'INVALID_CONTRACT','JSON-stable request');
  return normalized;
}
function canonicalJSON(x){
  if(Array.isArray(x))return '['+x.map(canonicalJSON).join(',')+']';
  if(x!==null&&typeof x==='object')return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonicalJSON(x[k])).join(',')+'}';
  return JSON.stringify(x);
}
function runFrozenRequest(store,request){
  // This is a bounded, explicit dispatch to the ORIGINAL Product reducers;
  // it never reconstructs functions from request text or mutates Product files.
  const r=request,rev=r.expected_revision;
  switch(r.type){
    case 'MilestoneCreate': return K.create(store,rev,'Milestone',r.id,r.fields,r.authority_refs);
    case 'Create': return K.create(store,rev,r.kind,r.id,r.fields,r.authority_refs);
    case 'Transition': return K.transition(store,rev,r.kind,r.id,r.target,r.options);
    case 'Satisfy': return K.satisfy(store,rev,r.id,r.obligation_id,r.authority_ref,r.authority_reference);
    case 'AddObligations': return K.addObligations(store,rev,r.id,r.additions,r.authority_ref,r.authority_reference);
    case 'BootstrapTaskCycle': return K.bootstrapTaskCycle(store,rev,r.request);
    default: throw new C.KernelError('INVALID_CONTRACT','unsupported keyed command');
  }
}
async function tx(command,mutation=null){
  const request=mutation===null?null:normalizeRequest(command);
  C.demand((mutation===null&&typeof command==='function')||(typeof mutation==='string'&&mutation.length>0&&request!==null),'INVALID_CONTRACT','keyed request requirements');
  const fingerprint=request?crypto.createHash('sha256').update(canonicalJSON(request)).digest('hex'):null;
  return conn(async c=>{
    await c.query('BEGIN');
    try{
      // The global lock MUST precede the receipt lookup: concurrent same-key clients serialize.
      const r=(await c.query('SELECT * FROM r1_data WHERE id=1 FOR UPDATE')).rows[0];
      const s=new RamStore({state:JSON.parse(r.state),events:JSON.parse(r.events)});
      assert.equal(s.verify().revision,r.revision);
      if(mutation!==null){
        const prior=await c.query('SELECT fingerprint,revision,response FROM r1_receipts WHERE mutation_id=$1',[mutation]);
        if(prior.rowCount){
          C.demand(prior.rows[0].fingerprint===fingerprint,'MUTATION_IDENTITY_COLLISION','mutation key does not identify same immutable command');
          const original=JSON.parse(prior.rows[0].response);
          C.demand(original.revision===prior.rows[0].revision&&original.revision<=r.revision,'MALFORMED_STATE','receipt revision identity');
          await c.query('COMMIT');
          return {reconciled:true,original};
        }
      }
      const result=request?runFrozenRequest(s,request):command(s),out=s.read();
      await c.query('UPDATE r1_data SET revision=$1,state=$2,events=$3 WHERE id=1',[out.state.revision,JSON.stringify(out.state),JSON.stringify(out.events)]);
      if(mutation!==null)await c.query('INSERT INTO r1_receipts(mutation_id,fingerprint,revision,response) VALUES ($1,$2,$3,$4)',[mutation,fingerprint,out.state.revision,JSON.stringify(result)]);
      await c.query('COMMIT');return result;
    }catch(e){await c.query('ROLLBACK');throw e;}
  });
}
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
  await step('closed_late_obligations_rejected',s=>K.addObligations(s,17,'TC1',[{id:'FORBIDDEN'}],'AUTH-SYN'),'INVALID_TRANSITION');
  await step('milestone_illegal_transition',s=>K.transition(s,17,'Milestone','M1','CLOSED'),'INVALID_TRANSITION');
  await step('operation_cannot_complete_without_pass',s=>K.transition(s,17,'Operation','OP1','COMPLETED',{result_ref:'synthetic/result'}),'UNSATISFIED_OBLIGATION');
  await step('closed_taskcycle_rejects_transition',s=>K.transition(s,17,'TaskCycle','TC1','ACTIVE'),'INVALID_TRANSITION');
  // A forged, internally hash-consistent bootstrap must be rejected by BOTH stores.
  function forgedBootstrap(modifier){
    const fake=clone(file.read());
    const e=fake.events.find(x=>x.action==='BOOTSTRAP_IMPORT');
    modifier(e.after);
    fake.state.aggregates.TaskCycle[e.aggregate_id]=clone(e.after);
    let previous=null;
    for(const event of fake.events){
      event.previous_hash=previous;
      const {hash:ignored,...p}=event;event.hash=digest(p);previous=event.hash;
    }
    return fake;
  }
  const hashBytes=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
  function rejectBothStores(doc,label){
    assert.throws(()=>new RamStore(doc),{code:'MALFORMED_STATE'},label+' RAM');
    const dest=fs.mkdtempSync(path.join(os.tmpdir(),'ts-r1-forged-'));
    fs.cpSync(temp,dest,{recursive:true});
    const headPath=path.join(dest,'state','kernel-v0','HEAD.json');
    const head=JSON.parse(fs.readFileSync(headPath,'utf8'));
    const dir=path.join(dest,'state','kernel-v0',head.generation);
    const stateBytes=JSON.stringify(doc.state,null,2)+'\n';
    const eventBytes=doc.events.map(x=>JSON.stringify(x)).join('\n')+'\n';
    // The canonical Product commit writes durable generations mode 0444. Only the
    // isolated, copied negative-test fixture may be made writable for injection.
    // Never change source Product or the already committed baseline at 'temp'.
    const fixtureFiles=[path.join(dir,'state.json'),path.join(dir,'events.ndjson'),headPath];
    for(const target of fixtureFiles){
      assert.equal(fs.statSync(target).mode&0o222,0,'fixture source is immutable');
      fs.chmodSync(target,0o644);
    }
    try{
      fs.writeFileSync(fixtureFiles[0],stateBytes);
      fs.writeFileSync(fixtureFiles[1],eventBytes);
      head.state_sha256=hashBytes(stateBytes);head.events_sha256=hashBytes(eventBytes);
      fs.writeFileSync(fixtureFiles[2],JSON.stringify(head,null,2)+'\n');
    }finally{
      for(const target of fixtureFiles)fs.chmodSync(target,0o444);
    }
    for(const target of fixtureFiles)assert.equal(fs.statSync(target).mode&0o222,0,'fixture permissions restored');
    assert.throws(()=>new K.FilesystemStateStore(dest).read(),{code:'MALFORMED_STATE'},label+' original Product');
    fs.rmSync(dest,{recursive:true,force:true});
  }
  rejectBothStores(forgedBootstrap(after=>{after.created_at='2026-02-01T00:00:00.000Z';}),'forged cutover');
  rejectBothStores(forgedBootstrap(after=>{after.authority_refs=[future];}),'forged authority');
  rejectBothStores(forgedBootstrap(after=>{after.terminal_disposition_ref='synthetic/not-import';}),'forged terminal disposition');
  console.log('PASS|R1|bootstrap_forgery|3_negative_cases|original_kernel_parity=true');
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
  const ack={type:'MilestoneCreate',expected_revision:next,id:'M-ACK',fields:{title:'lost ack'},authority_refs:[auth]};
  const first=await tx(ack,'SYNTHETIC-MUTATION-R1-REPAIR-001');
  K.create(cold,next,'Milestone','M-ACK',{title:'lost ack'},[auth]);
  const receipt=await tx(ack,'SYNTHETIC-MUTATION-R1-REPAIR-001');
  assert.deepEqual(receipt,{reconciled:true,original:first});await equal(cold);
  console.log('PASS|R1|lost_ack|receipt=bound_to_command|no_second_effect');
  for(const other of [
    {...ack,fields:{title:'different command'}},
    {...ack,expected_revision:ack.expected_revision+1},
    {...ack,authority_refs:[future]},
  ]){
    await assert.rejects(()=>tx(other,'SYNTHETIC-MUTATION-R1-REPAIR-001'),e=>e.code==='MUTATION_IDENTITY_COLLISION');
    await equal(cold);
  }
  console.log('PASS|R1|mutation_collision|wrong_payload_revision_authority=rejected|no_effect');
  const next2=(await read()).revision;
  const same={type:'MilestoneCreate',expected_revision:next2,id:'M-SAME-KEY',fields:{title:'same-key concurrently'},authority_refs:[auth]};
  const paired=await Promise.all([tx(same,'SYNTHETIC-MUTATION-R1-SAMEKEY-001'),tx(same,'SYNTHETIC-MUTATION-R1-SAMEKEY-001')]);
  assert.equal(paired.filter(v=>v.reconciled===true).length,1);
  assert.equal(paired.filter(v=>v.reconciled!==true).length,1);
  const originalSame=paired.find(v=>!v.reconciled),joined=paired.find(v=>v.reconciled);
  assert.deepEqual(joined.original,originalSame);
  K.create(cold,next2,'Milestone','M-SAME-KEY',{title:'same-key concurrently'},[auth]);
  await equal(cold);
  console.log('PASS|R1|concurrent_same_key|commits=1|reconciled=1|no_unique_violation');
  const bad=await read();bad.events[0].hash='0'.repeat(64);
  assert.throws(()=>new RamStore(bad),{code:'MALFORMED_STATE'});await equal(cold);
  console.log('PASS|R1|tamper|fails_closed|original_reducers=exact_product');
  // A001: all mutation families are now exercised through immutable command
  // identity+revision+authority receipts, not only a legacy MilestoneCreate.
  let keyedIndex=0;
  async function keyed(name,body,concurrent=false){
    const request=normalizeRequest(body),key='SYNTH-A001-'+(++keyedIndex);
    const expected=runFrozenRequest(file,request);
    let actual;
    if(concurrent){
      const pair=await Promise.all([tx(request,key),tx(request,key)]);
      assert.equal(pair.filter(x=>x?.reconciled===true).length,1,name+' one reconciliation');
      assert.equal(pair.filter(x=>x?.reconciled!==true).length,1,name+' one commit');
      actual=pair.find(x=>!x.reconciled);
      assert.deepEqual(pair.find(x=>x.reconciled).original,actual,name+' same-key receipt');
    }else actual=await tx(request,key);
    assert.deepEqual(actual,expected,name+' original Product command return');
    await equal();
    const retry=await tx(request,key);
    assert.deepEqual(retry,{reconciled:true,original:actual},name+' lost ACK receipt');
    // The same key with changed expected_revision is always a collision, never
    // a new mutation or a stale-revision replay disguised as success.
    await assert.rejects(
      ()=>tx({...request,expected_revision:request.expected_revision+1},key),
      e=>e.code==='MUTATION_IDENTITY_COLLISION',name+' revision mismatch');
    await equal();
    console.log('PASS|A001|'+name+'|fingerprint_bound=true|lost_ack=true|collision=true|rev='+(await read()).revision);
    return {key,request};
  }
  async function keyedReject(name,request,expectedCode){
    const before=(await read()).revision;
    let oracleError;
    try{runFrozenRequest(file,normalizeRequest(request));}catch(e){oracleError=e.code;}
    assert.equal(oracleError,expectedCode,name+' Product rejection');
    await assert.rejects(()=>tx(request,'SYNTH-A001-REJECT-'+name),e=>e.code===expectedCode);
    assert.equal((await equal()).revision,before,name+' no effect');
    console.log('PASS|A001|'+name+'|rejected='+expectedCode+'|no_effect=true');
  }
  const nextRev=async()=>(await read()).revision;
  await keyed('create_taskcycle',{type:'Create',kind:'TaskCycle',id:'TC-KEY',
    expected_revision:await nextRev(),fields:{responsibility:'synthetic keyed',obligations:[{id:'CHECK'},{id:'MORE',authority_ref:'AUTH-FUTURE'}]},authority_refs:[auth]});
  await keyed('add_obligations',{type:'AddObligations',id:'TC-KEY',
    expected_revision:await nextRev(),additions:[{id:'ADDED'}],authority_ref:'AUTH-SYN'});
  await keyed('satisfy_free',{type:'Satisfy',id:'TC-KEY',
    expected_revision:await nextRev(),obligation_id:'CHECK'});
  await keyedReject('satisfy_missing_auth',{type:'Satisfy',id:'TC-KEY',
    expected_revision:await nextRev(),obligation_id:'MORE',authority_ref:'AUTH-FUTURE'},
    'MISSING_REQUIRED_AUTHORITY');
  await keyed('satisfy_authority',{type:'Satisfy',id:'TC-KEY',
    expected_revision:await nextRev(),obligation_id:'MORE',authority_ref:'AUTH-FUTURE',
    authority_reference:future});
  await keyed('satisfy_added',{type:'Satisfy',id:'TC-KEY',
    expected_revision:await nextRev(),obligation_id:'ADDED'});
  await keyed('taskcycle_active',{type:'Transition',kind:'TaskCycle',id:'TC-KEY',
    expected_revision:await nextRev(),target:'ACTIVE',options:{}});
  await keyed('create_operation',{type:'Create',kind:'Operation',id:'OP-KEY',
    expected_revision:await nextRev(),fields:{taskcycle_id:'TC-KEY',objective:'keyed objective'},authority_refs:[auth]});
  await keyed('operation_ready',{type:'Transition',kind:'Operation',id:'OP-KEY',
    expected_revision:await nextRev(),target:'READY',options:{}});
  await keyed('operation_running',{type:'Transition',kind:'Operation',id:'OP-KEY',
    expected_revision:await nextRev(),target:'RUNNING',options:{}});
  await keyed('create_attempt',{type:'Create',kind:'ExecutionAttempt',id:'ATT-KEY',
    expected_revision:await nextRev(),fields:{operation_id:'OP-KEY'},authority_refs:[auth]});
  await keyed('attempt_dispatched',{type:'Transition',kind:'ExecutionAttempt',id:'ATT-KEY',
    expected_revision:await nextRev(),target:'DISPATCHED',options:{}});
  await keyed('attempt_unknown',{type:'Transition',kind:'ExecutionAttempt',id:'ATT-KEY',
    expected_revision:await nextRev(),target:'UNKNOWN',options:{}});
  await keyedReject('unknown_fences_attempt',{type:'Create',kind:'ExecutionAttempt',id:'ATT-KEY-RETRY',
    expected_revision:await nextRev(),fields:{operation_id:'OP-KEY'},authority_refs:[auth]},
    'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  await keyed('attempt_reconciled',{type:'Transition',kind:'ExecutionAttempt',id:'ATT-KEY',
    expected_revision:await nextRev(),target:'FAILED',options:{authority_ref:'AUTH-SYN',outcome:'FAIL',result_refs:[ev]}});
  await keyed('bootstrap_import',{type:'BootstrapTaskCycle',expected_revision:await nextRev(),
    request:{id:'TC-KEY-IMP',responsibility:'synthetic imported keyed',state:'ACTIVE',obligations:[],bootstrap_provenance:imported}});
  await keyed('taskcycle_pending',{type:'Transition',kind:'TaskCycle',id:'TC-KEY',
    expected_revision:await nextRev(),target:'PENDING_ACCEPTANCE',options:{}});
  await keyed('taskcycle_closed',{type:'Transition',kind:'TaskCycle',id:'TC-KEY',
    expected_revision:await nextRev(),target:'CLOSED',options:{authority_ref:'AUTH-SYN',disposition_ref:'synthetic/keyed-close'}});
  await keyedReject('closed_obligation_fence',{type:'AddObligations',id:'TC-KEY',
    expected_revision:await nextRev(),additions:[{id:'NO-LATE'}],authority_ref:'AUTH-SYN'},
    'INVALID_TRANSITION');
  await keyed('milestone_create_two_clients',{type:'Create',kind:'Milestone',id:'M-KEY-RACE',
    expected_revision:await nextRev(),fields:{title:'two clients'},authority_refs:[auth]},true);
  const lastTransition=await keyed('milestone_transition',{type:'Transition',kind:'Milestone',id:'M-KEY-RACE',
    expected_revision:await nextRev(),target:'ACTIVE',options:{}});
  // IR004-F001: even on a previously committed same-key command, these
  // malformed envelopes MUST be rejected before receipt lookup or mutation.
  const cyclic={};cyclic.self=cyclic;
  const accessor={};Object.defineProperty(accessor,'unused',{enumerable:true,get(){return 1;}});
  const inherited=Object.create({unused:1});
  const bad=[
    ['nan',{...lastTransition.request,options:{unused:NaN}}],
    ['infinity',{...lastTransition.request,options:{unused:Infinity}}],
    ['neg_infinity',{...lastTransition.request,options:{unused:-Infinity}}],
    ['neg_zero',{...lastTransition.request,options:{unused:-0}}],
    ['unknown_null',{...lastTransition.request,options:{unused:null}}],
    ['undefined',{...lastTransition.request,options:{unused:undefined}}],
    ['function',{...lastTransition.request,options:{unused:()=>1}}],
    ['symbol',{...lastTransition.request,options:{unused:Symbol('x')}}],
    ['bigint',{...lastTransition.request,options:{unused:1n}}],
    ['cyclic',{...lastTransition.request,options:cyclic}],
    ['accessor',{...lastTransition.request,options:accessor}],
    ['inherited',{...lastTransition.request,options:inherited}],
    ['proto_type',{...lastTransition.request,type:'__proto__'}],
    ['constructor_type',{...lastTransition.request,type:'constructor'}],
    ['missing_type',{...lastTransition.request,type:undefined}],
    ['unknown_create_field',{type:'Create',kind:'Milestone',id:'M-BAD',expected_revision:await nextRev(),
       fields:{title:'good',unused:NaN},authority_refs:[auth]}]
  ];
  const revBefore=(await read()).revision;
  for(const [name,invalid] of bad){
    await assert.rejects(()=>tx(invalid,lastTransition.key),e=>e.code==='INVALID_CONTRACT',
      'reject malformed JSON/command before receipt '+name);
    assert.equal((await equal()).revision,revBefore,name+' without effect');
    console.log('PASS|A001|strict_json_reject_'+name+'|typed=true|no_effect=true');
  }
  console.log('PASS|A001|strict_json_domain|malformed='+bad.length+'|same_key_rejected=true|parity=true');
  console.log('PASS|A001|command_families=Create,Transition,Satisfy,AddObligations,BootstrapTaskCycle|historical_effects=NONE|parity=true');
  fs.rmSync(temp,{recursive:true,force:true});
}
main().catch(e=>{console.error('FAIL|R1|'+(e.stack||e));process.exitCode=1;});
