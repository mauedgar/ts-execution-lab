// 030 / A actual Product State Kernel reference implementation, no fake lifecycle.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {mkdirSync,writeFileSync,readFileSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const PROD=process.env.PRODUCT_ROOT,ROOT=process.env.A_KERNEL_ROOT,OUT=process.env.A_RESULT;
if(!PROD||!ROOT||!OUT||existsSync(ROOT))throw Error('A_EXACT_FRESH_ROOT_REQUIRED');
mkdirSync(ROOT,{recursive:true});
const requireProduct=createRequire(join(PROD,'package.json'));
const kernel=requireProduct(join(PROD,'src/state-kernel-v0/index.js'));
const {createStateKernelTaskCycleLifecycle}=requireProduct(join(PROD,'src/operational-spine-v0/state-kernel-adapter.js'));
const sourceFile=join(PROD,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js');
const recipeFactory=requireProduct(sourceFile).createReconcileAndCloseTaskCycleRecipe;
const original=readFileSync(sourceFile,'utf8');
const checks=[],receipt={id:'TS-BEADS-030-A-KERNEL-REFERENCE-20261029-001',status:'RUNNING',Product_effect:'NONE',authority:'EXPERIMENTAL_CONTROL_ONLY',checks,
 product_recipe_sha256:createHash('sha256').update(original).digest('hex'),measurements:{}};
const ok=(id,condition)=>{assert.ok(condition,id);checks.push(id)};
const auth={kind:'AUTHORITY',id:'authority:developer-001',location:'evidence/authority-developer-001.json'};
function obsFor(tcId){
 return {
  candidate_identity:[{source_ref:'candidate:001',observed:{
   commit:'a'.repeat(40),tree:'b'.repeat(40),parent:'c'.repeat(40),changed_paths:['src/recipe.js','tests/recipe.test.js']}}],
  terminal_results:[{source_ref:'terminal:001',observed:[{reference:'terminal:001',subject_id:'AT-001',status:'PASS'}]}],
  independent_review:[{source_ref:'review:001',observed:{reference:'review:001',disposition:'PASS'}}],
  developer_acceptance:[{source_ref:'authority:developer-001',observed:{reference:'authority:developer-001',disposition:'ACCEPTED'}}],
  canonical_integration:[{source_ref:'integration:001',observed:{reference:'integration:001',status:'INTEGRATED'}}],
  remote_publication:[{source_ref:'publication:001',observed:{reference:'publication:001',status:'PUBLISHED'}}],
  canonical_state_delta:[{source_ref:'state-delta:001',observed:{
   from:{reference:'state:40',revision:40,sha256:'d'.repeat(64)},
   to:{reference:'state:50',revision:50,sha256:'e'.repeat(64)},
   changed_aggregates:[{kind:'TaskCycle',id:tcId,before_revision:6,after_revision:7}]}}]
 };
}
const evidenceKinds={candidate_identity:'CANDIDATE_IDENTITY',terminal_results:'TERMINAL_RESULTS',
 independent_review:'INDEPENDENT_REVIEW_RESULT',developer_acceptance:'DEVELOPER_ACCEPTANCE',
 canonical_integration:'CANONICAL_INTEGRATION',remote_publication:'REMOTE_PUBLICATION',
 canonical_state_delta:'CANONICAL_STATE_DELTA'};
const competence={independent_review:['INDEPENDENT_REVIEW','authority:reviewer-001'],
 developer_acceptance:['DEVELOPER','authority:developer-001'],
 canonical_integration:['EFFECT_AUTHORITY','authority:effect-001'],
 remote_publication:['EFFECT_AUTHORITY','authority:effect-001']};
const hash=s=>createHash('sha256').update(s).digest('hex');
function verifiedEvidence(tc,obs){
 return Object.entries(obs).flatMap(([field,entries])=>entries.map(entry=>{
 const c=competence[field],payload={schema_version:'tecnotron-reconciliation-evidence/v0',
  kind:evidenceKinds[field],subject:{kind:'TaskCycle',id:tc,field},observed:entry.observed,
  verification:{status:'VERIFIED',verification_ref:'verification:'+entry.source_ref,
   verifier_ref:'verifier:fixture',authority_competence:c?
   {status:'ESTABLISHED',kind:c[0],authority_ref:c[1],basis_ref:'basis:'+field}:null}};
 const json=JSON.stringify(payload);
 return {ref:entry.source_ref,sha256:hash(json),artifact_json:json};
 }));
}
const obligationsRules=[
 {obligation_id:'INDEPENDENT_REVIEW',source:'independent_review',
  authority_ref:'authority:reviewer-001',
  authority_reference:{kind:'AUTHORITY',id:'authority:reviewer-001',location:'evidence/authority-reviewer-001.json'}},
 {obligation_id:'DEVELOPER_ACCEPTANCE',source:'developer_acceptance',
  authority_ref:'authority:developer-001',authority_reference:auth},
 {obligation_id:'CANONICAL_INTEGRATION',source:'canonical_integration',
  authority_ref:'authority:effect-001',
  authority_reference:{kind:'AUTHORITY',id:'authority:effect-001',location:'evidence/authority-effect-001.json'}},
 {obligation_id:'REMOTE_PUBLICATION',source:'remote_publication',remote_expected_status:'PUBLISHED',
  authority_ref:'authority:effect-001'},
 {obligation_id:'LIFECYCLE_RECONCILIATION',source:'reconciliation'}
];
function req(tcId,{badDeveloper=false,pending=false}={}){
 const obs=obsFor(tcId);
 if(badDeveloper==='MISSING')obs.developer_acceptance=[];
 else if(badDeveloper){obs.developer_acceptance=[{source_ref:'authority:developer-001',
  observed:{reference:'authority:developer-001',disposition:'REJECTED'}}];}
 return {
  recipe_id:'reconcile_and_close_taskcycle',recipe_version:'v0',
  operation_id:'OP-CLOSE',execution_attempt_id:'AT-CLOSE',
  context:{schema_version:'tecnotron-execution-context/v0',operation_id:'OP-CLOSE',
   taskcycle_id:tcId,repository:{identity:'fixture',location:'/synthetic/no-repository-effect'},
   runtime:{executor:'test',platform:'synthetic',runtime_identity:'node:test'},
   state_store:{reference:'synthetic-state'},authority_refs:[],evidence_refs:[]},
  authorization:{disposition:'AUTHORIZED',authority_reference:'DEV-CLOSE',
    effect_constraints:[{effect:'state.taskcycle.write',scope:'exact taskcycle only'}]},
  evidence_refs:[],
  input:{expected_state_revision:50,observations:obs,evidence:verifiedEvidence(tcId,obs),
   obligation_satisfactions:pending?obligationsRules:[],closure:{authority_ref:'authority:developer-001',disposition_ref:'result:closed'}}
 };
}

const counters={read:0,verify:0,mutate:0};
function createFixture(tc,dir){
 const home=join(ROOT,dir);
 const store=new kernel.FilesystemStateStore(home);
 const oldRead=store.read.bind(store),oldVerify=store.verify.bind(store),oldMutate=store.mutate.bind(store);
 store.read=(...a)=>{counters.read++;return oldRead(...a)};
 store.verify=(...a)=>{counters.verify++;return oldVerify(...a)};
 store.mutate=(...a)=>{counters.mutate++;return oldMutate(...a)};
 store.initialize();
 const rev=()=>store.verify().revision;
 kernel.create(store,rev(),'TaskCycle',tc,{responsibility:'SYNTHETIC_TEST_CLOSE',
   obligations:obligationsRules.map(x=>({id:x.obligation_id}))});
 kernel.transition(store,rev(),'TaskCycle',tc,'ACTIVE');
 kernel.create(store,rev(),'Operation','OP-CLOSE',{taskcycle_id:tc,objective:'SYNTHETIC_CLOSE'});
 kernel.transition(store,rev(),'Operation','OP-CLOSE','READY');
 kernel.transition(store,rev(),'Operation','OP-CLOSE','RUNNING');
 kernel.create(store,rev(),'ExecutionAttempt','AT-CLOSE',{operation_id:'OP-CLOSE'});
 kernel.transition(store,rev(),'ExecutionAttempt','AT-CLOSE','DISPATCHED');
 kernel.transition(store,rev(),'ExecutionAttempt','AT-CLOSE','RUNNING');
 const request=req(tc,{pending:true});
 request.input.expected_state_revision=rev();
 return {store,rev,request,capability:createStateKernelTaskCycleLifecycle({store})};
}
try{
 const a=createFixture('TC-PENDING','positive');
 const recipe=recipeFactory({lifecycle:a.capability});
 const pre=await recipe.preflight(a.request);
 ok('original_Kernel_preflight_READY',pre.status==='READY');
 const before={...counters};
 const at=process.hrtime.bigint();
 const executed=await recipe.execute(a.request);
 const elapsedMs=Number(process.hrtime.bigint()-at)/1e6;
 const positiveOps={read:counters.read-before.read,verify:counters.verify-before.verify,mutate:counters.mutate-before.mutate};
 const aggregate=kernel.inspect(a.store,'TaskCycle','TC-PENDING').aggregate;
 ok('original_Kernel_closure_PASS_CONFIRMED',executed.status==='PASS'&&executed.effect_state==='CONFIRMED');
 ok('original_Kernel_all_five_obligations_SATISFIED',aggregate.state==='CLOSED'&&aggregate.obligations.length===5&&aggregate.obligations.every(o=>o.status==='SATISFIED'));
 ok('original_Kernel_authority_refs_reconciled',['authority:reviewer-001','authority:developer-001','authority:effect-001'].every(id=>aggregate.authority_refs.some(a=>a.id===id)));
 const repeatre=req('TC-PENDING',{pending:true});
 repeatre.input.expected_state_revision=a.rev();
 const replay=await recipe.execute(repeatre);
 ok('original_Kernel_terminal_replay_denied',replay.status==='FAIL'&&replay.effect_state==='NONE');
 receipt.measurements.positive={
  elapsed_ms:elapsedMs,store_calls:positiveOps,
  status:executed.status,effect_state:executed.effect_state,
  final_state:aggregate.state,satisfied:aggregate.obligations.filter(o=>o.status==='SATISFIED').length,
  authority_ids:aggregate.authority_refs.map(x=>x.id).sort(),
  repeated_status:replay.status,
  initial_global_revision:a.request.input.expected_state_revision,
  final_global_revision:a.rev(),kernel_event_count:a.store.verify().event_count};
 const u=createFixture('TC-UNKNOWN','unknown');
 kernel.transition(u.store,u.rev(),'ExecutionAttempt','AT-CLOSE','UNKNOWN');
 u.request.input.expected_state_revision=u.rev();
 const unknown=await recipeFactory({lifecycle:u.capability}).preflight(u.request);
 ok('original_Kernel_UNKNOWN_blocks',unknown.status==='BLOCKED'&&unknown.reason==='UNKNOWN_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION');
 const k=createFixture('TC-ACK-PENDING','ack-loss');
 const corrupted={...k.capability,satisfyObligation:(args)=>{
    const real=k.capability.satisfyObligation(args);
    return args.obligationId==='CANONICAL_INTEGRATION'?
      {...real,event_id:'BAD_ACK_AFTER_REAL_PRODUCT_KERNEL_MUTATION'}:real;
 }};
 const ack=await recipeFactory({lifecycle:corrupted}).execute(k.request);
 const ackState=kernel.inspect(k.store,'TaskCycle','TC-ACK-PENDING').aggregate;
 ok('original_Kernel_lost_ack_effect_CONFIRMED',ack.status==='FAIL'&&ack.effect_state==='CONFIRMED');
 ok('original_Kernel_ACK_partial_not_closed',ackState.state==='ACTIVE'&&
    ackState.obligations.filter(o=>o.status==='SATISFIED').length===1);
 const r=createFixture('TC-RACING','race');
 let once=false;
 const racing={...r.capability,satisfyObligation:(args)=>{
    if(!once){once=true;kernel.transition(r.store,r.rev(),'ExecutionAttempt','AT-CLOSE','UNKNOWN');}
    return r.capability.satisfyObligation(args);
 }};
 const race=await recipeFactory({lifecycle:racing}).execute(r.request);
 const raceState=kernel.inspect(r.store,'TaskCycle','TC-RACING').aggregate;
 console.log('TS_BEADS030_A_RACE_OBSERVED='+JSON.stringify({
    status:race.status,effect_state:race.effect_state,reason:race.reason,
    preserved_pending:raceState.obligations.filter(o=>o.status==='PENDING').length,
    attempt_state:kernel.inspect(r.store,'ExecutionAttempt','AT-CLOSE').aggregate.state
 }));
 ok('original_Kernel_CAS_race_preserves_all_TaskCycle_obligations',
    race.status==='FAIL'&&['NONE','UNKNOWN'].includes(race.effect_state)&&
    raceState.obligations.every(o=>o.status==='PENDING'));
 const old=createFixture('TC-SATISFIED','rejected');
 for(const rule of obligationsRules){
    kernel.satisfy(old.store,old.rev(),'TC-SATISFIED',rule.obligation_id,
      rule.authority_ref,rule.authority_reference);
 }
 const rejectedReq=req('TC-SATISFIED',{badDeveloper:true});
 rejectedReq.input.expected_state_revision=old.rev();
 const rejected=await recipeFactory({lifecycle:old.capability}).preflight(rejectedReq);
 ok('original_Kernel_presatisfied_REJECTED_gap_reproduced',rejected.status==='READY');
 receipt.measurements.negative={unknown:{status:unknown.status,reason:unknown.reason},
   ack:{status:ack.status,effect_state:ack.effect_state,satisfied:ackState.obligations.filter(o=>o.status==='SATISFIED').length},
   race:{status:race.status,effect_state:race.effect_state,remaining:raceState.obligations.filter(o=>o.status==='PENDING').length},
   presatisfied_developer_rejected:{status:rejected.status,reaches_valid_Kernel_snapshot:true,
     note:'Fixture directly satisfies all obligations using native Kernel methods; not evidence of legitimate Product historical transition'}};
 receipt.measurements.source={original_product_recipe_bytes:Buffer.byteLength(original),
   original_Kernel_source_present:true,Product_installed_files_modified:0};
 receipt.status='PASS_A_ACTUAL_KERNEL_SAME_RECIPE_POSITIVE_AND_NEGATIVES';
 console.log('TS_BEADS030_A=PASS;checks='+checks.length+';kernel=ORIGINAL;Product=NONE');
}catch(e){receipt.status='FAIL_A_ORIGINAL_KERNEL_ATTEMPT';receipt.error=String(e?.stack||e);console.error('TS_BEADS030_A_ERROR='+receipt.error);throw e}
finally{writeFileSync(OUT,JSON.stringify(receipt,null,2)+'\n','utf8');console.log('TS_BEADS030_A_RECEIPT='+OUT)}
