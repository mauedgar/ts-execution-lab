// 021 — isolated adaptation of ACTUAL Tecnotron closure-recipe consumer, not a reimplementation.
// Rewrites a small documented set of sync call sites in memory; uses native Beads/Dolt backing.
// Synthetic evidence, TaskCycles and receipt subjects only. Never Product authority.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import Module from 'node:module';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {setTimeout as delay} from 'node:timers/promises';

const PRODUCT_SHA='7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56',
 PRODUCT_TREE='8caa56d36f3efeba359bbbf65b158ffb01a19da6';
const PROD=process.env.PRODUCT_ROOT,LAB=process.env.LAB_ROOT,BD=process.env.BD_BIN,OUTPUT=process.env.RESULT_PATH;
if(!PROD||!LAB||!BD||!OUTPUT)throw Error('EXPLICIT_EXPERIMENT_IDENTITY_REQUIRED');
if(existsSync(join(LAB,'.beads')))throw Error('DISPOSABLE_LAB_ALREADY_INITIALIZED');
mkdirSync(LAB,{recursive:true});
const env={...process.env,BEADS_DIR:join(LAB,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BEADS_ACTOR:'TS-BEADS-021-NONPRODUCT',NO_COLOR:'1',GIT_TERMINAL_PROMPT:'0'};
const receipt={id:'TS-BEADS-FIRST-REAL-CONSUMER-20261024-021',
 status:'RUNNING',authority:'NONE_PRODUCT',Product_effect:'NONE',shared_Dolt_effect:'NONE',
 Product_sha:PRODUCT_SHA,Product_tree:PRODUCT_TREE,check:[],negative:[],metrics:{native_calls:{reads:0,batches:0,metadata_token_reads:0,write_items:0}},
 semantics:'EXPERIMENTAL_PER_TASKCYCLE_EPOCH_NOT_PRODUCT_GLOBAL_REVISION',
 scope:'ACTUAL_PRODUCT_RECONCILE_AND_CLOSE_RECIPE_MEMORY_ADAPTED;NO_PRODUCT_FILE_CHANGED'};
const ok=(key,truth,kind='positive')=>{assert.ok(truth,key);receipt.check.push({key,result:'PASS',kind})};
const clone=x=>structuredClone(x);
const dir=join(PROD,'src/operational-spine-v0/recipes');
const sourceFile=join(dir,'reconcile-and-close-taskcycle.js');
const original=readFileSync(sourceFile,'utf8');
const subs=[
 ['function authoritativeSnapshot(lifecycle, taskcycleId) {','async function authoritativeSnapshot(lifecycle, taskcycleId) {',1],
 ['function invokeMutation({ lifecycle, taskcycleId, expectedRevision, invoke, expectedEffect }) {','async function invokeMutation({ lifecycle, taskcycleId, expectedRevision, invoke, expectedEffect }) {',1],
 ['function prepare({ request, input, lifecycle, reconcilePostTaskCycle, handoffSnapshot = null }) {','async function prepare({ request, input, lifecycle, reconcilePostTaskCycle, handoffSnapshot = null }) {',1],
 ['lifecycleSnapshot = lifecycle.snapshot(','lifecycleSnapshot = await lifecycle.snapshot(',1],
 ['bookkeeping = lifecycle.observeInvocationBookkeeping(','bookkeeping = await lifecycle.observeInvocationBookkeeping(',1],
 ['if (hasUnreconciledUnknown(lifecycle, taskcycle)) {','if (await hasUnreconciledUnknown(lifecycle, taskcycle)) {',1],
 ['before = authoritativeSnapshot(lifecycle, taskcycleId);','before = await authoritativeSnapshot(lifecycle, taskcycleId);',1],
 ['after = authoritativeSnapshot(lifecycle, taskcycleId);','after = await authoritativeSnapshot(lifecycle, taskcycleId);',1],
 ['result = invoke();','result = await invoke();',1],
 ['const prepared = prepare(','const prepared = await prepare(',2],
 ['const mutation = invokeMutation(','const mutation = await invokeMutation(',1],
 ['const closeMutation = invokeMutation(','const closeMutation = await invokeMutation(',1],
 ['const observed = capability.snapshot(','const observed = await capability.snapshot(',1],
 ['finalSnapshot = capability.snapshot(','finalSnapshot = await capability.snapshot(',1],
];
let experimental=original;let replaced=0;
for(const [from,to,count] of subs){
 const actual=experimental.split(from).length-1;
 if(actual!==count)throw Error('PRODUCT_CONSUMER_UNEXPECTED_DRIFT:'+from+':'+actual);
 experimental=experimental.replaceAll(from,to);replaced+=count;
}
ok('original_product_consumer_source_loaded_and_transform_anchored',replaced===15);
const instance=new Module(sourceFile,undefined);instance.filename=sourceFile;
instance.paths=Module._nodeModulePaths(dirname(sourceFile));instance._compile(experimental,sourceFile);
const {createReconcileAndCloseTaskCycleRecipe}=instance.exports;
assert.equal(typeof createReconcileAndCloseTaskCycleRecipe,'function');
receipt.metrics.consumer_source={original_bytes:Buffer.byteLength(original),experimental_bytes:Buffer.byteLength(experimental),
 inserted_or_replaced_anchors:replaced,added_lines:experimental.split('\n').length-original.split('\n').length,
 extra_code_modules_added_in_Product:0};
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
function req(tcId,{badDeveloper=false}={}){
 const obs=obsFor(tcId);
 if(badDeveloper){obs.developer_acceptance=[{source_ref:'authority:developer-001',
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
   obligation_satisfactions:[],closure:{authority_ref:'authority:developer-001',disposition_ref:'result:closed'}}
 };
}
const cases=[
 {tc:'TC-001',root:'ts021-root',gate:'ts021-gate'},
 {tc:'TC-ACK',root:'ts021-ack-root',gate:'ts021-ack-gate'}
];
const store=new Map(cases.map(x=>[x.tc,x]));
function cmd(args){
 const r=spawnSync(BD,args,{cwd:LAB,env,encoding:'utf8',timeout:40000,maxBuffer:8*1024*1024});
 if(r.error||r.status!==0)throw Error('NATIVE_CLI_ERROR:'+args.slice(0,4).join('_')+':'+JSON.stringify({exit:r.status,error:r.error?.message,out:r.stdout,err:r.stderr}).slice(0,850));
 return (r.stdout||'').trim();
}
function cmdJ(args){let s=cmd([...args,'--json']),i=s.search(/[\[{]/);if(i<0)throw Error('NATIVE_JSON_MISSING');return JSON.parse(s.slice(i))}
function show(id){const v=cmdJ(['show',id]),one=Array.isArray(v)?v[0]:v;if(one.id!==id)throw Error('CLI_ID_MISMATCH:'+id);return one}
function metadata(issue){const m=issue.metadata;return typeof m==='string'?JSON.parse(m):m;}
function createNative(id,title,meta){
 const r=cmdJ(['create',title,'--type','task','--id',id,'--force',
   '--description','TS-BEADS-021_NONPRODUCT_SYNTHETIC_ONLY','--metadata',JSON.stringify(meta)]);
 const v=Array.isArray(r)?r[0]:r;ok('native_created_'+id,v.id===id);
}
let server=null,base='',log='';
async function start(){
 const port=32100+(Number(process.env.GITHUB_RUN_ID||2100)%15500);
 base='http://127.0.0.1:'+port;
 server=spawn(BD,['serve','--addr','127.0.0.1:'+port],{cwd:LAB,env,windowsHide:true,
 stdio:['ignore','pipe','pipe']});
 server.stdout.on('data',x=>log+=String(x));server.stderr.on('data',x=>log+=String(x));
 for(let i=0;i<100;i++){if(server.exitCode!==null||server.signalCode!==null)throw Error('NATIVE_HTTP_EXITED:'+log.slice(-500));
  try{if((await fetch(base+'/healthz',{signal:AbortSignal.timeout(450)})).ok)return;}catch{}
  await delay(180)}
 throw Error('NATIVE_HTTP_NOT_READY:'+log.slice(-400));
}
async function stop(){
 if(!server)return;
 if(server.exitCode===null&&server.signalCode===null){
  server.kill();await Promise.race([new Promise(done=>server.once('exit',done)),delay(6300)]);
 }
 if(server.exitCode===null&&server.signalCode===null)throw Error('NATIVE_HTTP_SHUTDOWN_UNCONFIRMED');
 server=null;
}
async function native(path,payload){
 if(payload===undefined)receipt.metrics.native_calls.reads++;
 else receipt.metrics.native_calls.batches++;
 const res=await fetch(base+path,{...(payload===undefined?{}:{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),
  signal:AbortSignal.timeout(12000)});
 const raw=await res.text();let data;try{data=JSON.parse(raw)}catch{data=null}
 return {ok:res.ok,status:res.status,data,raw:raw.slice(0,1800)};
}
function locate(o,id,level=0){
 if(!o||typeof o!=='object'||level>7)return null;
 if(o.id===id&&o.metadata!==undefined)return o;
 for(const v of Object.values(o)){const found=locate(v,id,level+1);if(found)return found}return null;
}
async function get(id){
 const res=await native('/v0/beads/issues/'+id);
 if(!res.ok)throw Error('NATIVE_GET_ERROR:'+id+':'+res.raw);
 const row=locate(res.data,id);
 if(!row)throw Error('NATIVE_ROW_NOT_IN_GET:'+id+':'+JSON.stringify(res.data).slice(0,300));
 return row;
}
const patch=(id,metadata,token)=>({kind:'update',update:{target:{id},
 ...(token?{expected_version:token}:{}),patch:{metadata:{set:metadata}}}});
async function batch(items,label){
 receipt.metrics.native_calls.write_items+=items.length;
 return native('/v0/beads/issues:batchApply',{actor:'TS-BEADS-021-NONPRODUCT',
 provenance:'test://TS-BEADS-021/'+label,items});
}
async function marker(id,expected,token){
 const response=await batch([patch(id,{ts021_marker:expected},token)],'native-metadata-read-set-version');
 if(!response.ok)throw Error('NATIVE_MARKER_REFUSED:'+id+':'+response.raw);
 const version=response.data?.items?.[0]?.revision;
 if(typeof version!=='string'||!version)throw Error('NATIVE_VERSION_NOT_RETURNED');
 receipt.metrics.native_calls.metadata_token_reads++;
 return version;
}
async function readSet(subject){
 // Native HTTP reads, then server-issued equality-only version guards for BOTH causal issues.
 const a=await get(subject.root),b=await get(subject.gate);
 const root=metadata(a),gate=metadata(b);
 if(!root.ts021_taskcycle||!gate.ts021_attempt)throw Error('NATIVE_SUBJECT_METADATA_MISSING');
 const rootVersion=await marker(subject.root,root.ts021_marker);
 const gateVersion=await marker(subject.gate,gate.ts021_marker);
 return {subject,root,gate,rootVersion,gateVersion};
}
function aggregate(s){return clone(s.root.ts021_taskcycle)}
async function nativeSetAttempt(subject,state){
 const before=await get(subject.gate),m=metadata(before);
 const updated={...m.ts021_attempt,state,reconciliation_required:state==='UNKNOWN'};
 const res=await batch([patch(subject.gate,{ts021_attempt:updated,ts021_marker:state+'-mark'})],
  'external-writer-guard-state');
 if(!res.ok)throw Error('SET_SYNTHETIC_ATTEMPT_FAILED:'+res.raw);
}
function capability(subject,{injectGateRace=false,ackLoss=false}={}){
 let lastRead=null,racePending=injectGateRace;
 async function snapshot(tcId){
  if(tcId!==subject.tc)throw Error('TASKCYCLE_IDENTITY_MISMATCH');
  lastRead=await readSet(subject);
  const x=aggregate(lastRead),counter=lastRead.root.ts021_epoch;
  return {revision:counter,event_count:counter,taskcycle:x,
   legal_next:x.state==='ACTIVE'&&x.obligations.every(z=>z.status==='SATISFIED')?['CLOSED']:[],
   obligations:{id:tcId,store_revision:counter,obligations:clone(x.obligations),
    pending:x.obligations.filter(z=>z.status==='PENDING').map(z=>z.id),legal_next:[]}};
 }
 async function hasUnreconciledExecution(tcId){
  if(tcId!==subject.tc)throw Error('SUBJECT_MISMATCH');
  const v=await get(subject.gate),a=metadata(v).ts021_attempt;
  return a.state==='UNKNOWN'||a.reconciliation_required===true;
 }
 async function closeTaskCycle({expectedRevision,taskcycleId,authorityRef,dispositionRef}){
  if(taskcycleId!==subject.tc||authorityRef!==auth.id)throw Error('INCORRECT_SYNTHETIC_AUTHORITY');
  const read=lastRead;
  if(!read||read.root.ts021_epoch!==expectedRevision)throw Error('SCOPED_EPOCH_MISMATCH');
  if(read.gate.ts021_attempt.state==='UNKNOWN'||read.gate.ts021_attempt.reconciliation_required)
   throw Error('UNRECONCILED_SYNTHETIC_ATTEMPT');
  if(racePending){
   racePending=false;await nativeSetAttempt(subject,'UNKNOWN');
  }
  const before=aggregate(read);
  if(before.state!=='ACTIVE'||before.obligations.some(x=>x.status!=='SATISFIED'))throw Error('INVALID_CLOSURE');
  if(!before.authority_refs.some(x=>x.id===auth.id))throw Error('COMPETENT_SYNTHETIC_AUTHORITY_MISSING');
  const after={...before,state:'CLOSED',revision:before.revision+1,
   last_event_id:'event-'+(expectedRevision+1),terminal_disposition_ref:dispositionRef};
  const nativeResult=await batch([
    patch(subject.root,{ts021_taskcycle:after,ts021_epoch:expectedRevision+1},read.rootVersion),
    patch(subject.gate,{ts021_marker:read.gate.ts021_marker},read.gateVersion),
    {kind:'close',close:{target:{id:subject.root},reason:'NONPRODUCT_TEST_EXACT_AUTHORITY_RECONCILED'}}
  ],'native-guarded-real-product-consumer-close');
  if(!nativeResult.ok)throw Error('NATIVE_SCOPED_BATCH_REJECTED:'+nativeResult.status);
  const valid={revision:expectedRevision+1,event_id:after.last_event_id,
    aggregate_revision:after.revision,kind:'TaskCycle',aggregate_id:subject.tc};
  return ackLoss?{...valid,event_id:'LOST_SYNTHETIC_ACK'}:valid;
 }
 return {snapshot,hasUnreconciledExecution,closeTaskCycle,
  observeInvocationBookkeeping:async()=>{throw Error('HANDOFF_BOOKKEEPING_NOT_QUALIFIED')},
  satisfyObligation:async()=>{throw Error('PENDING_OBLIGATION_MUTATION_NOT_QUALIFIED')}};
}
try{
 cmd(['init','--server','--quiet','--stealth']);
 const rem=spawnSync('git',['remote'],{cwd:LAB,env,encoding:'utf8',timeout:4000});
 ok('isolated_Beads_git_has_no_remote',rem.status===0&&!rem.stdout.trim());
 for(const s of cases){
  const tc={schema_version:'tecnotron-state-kernel/v0',kind:'TaskCycle',id:s.tc,revision:7,state:'ACTIVE',
    responsibility:'SYNTHETIC_TEST_CLOSE',created_at:'2026-01-01T00:00:00.000Z',
    updated_at:'2026-01-01T00:00:00.000Z',authority_refs:[clone(auth)],
    related_ids:['OP-001'],last_event_id:'event-50',terminal_disposition_ref:null,
    obligations:['INDEPENDENT_REVIEW','DEVELOPER_ACCEPTANCE','CANONICAL_INTEGRATION',
     'REMOTE_PUBLICATION','LIFECYCLE_RECONCILIATION'].map(x=>({id:x,status:'SATISFIED',
       authority_ref:x==='LIFECYCLE_RECONCILIATION'?null:
        x==='INDEPENDENT_REVIEW'?'authority:reviewer-001':
        x==='DEVELOPER_ACCEPTANCE'?'authority:developer-001':'authority:effect-001'}))};
  createNative(s.root,'TS021 SYNTHETIC TC '+s.tc,
   {ts021_taskcycle:tc,ts021_epoch:50,ts021_marker:'root-original'});
  createNative(s.gate,'TS021 SYNTHETIC attempt guard '+s.tc,
   {ts021_attempt:{kind:'ExecutionAttempt',id:s.tc+'-ATTEMPT',operation_id:'OP-001',
    state:'RUNNING',reconciliation_required:false},ts021_marker:'RUNNING-mark'});
 }
 await start();ok('native_Beads_server_health',true);
 const s=cases[0];
 const consumer=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(s)});
 const validRequest=req(s.tc);
 const badDev=req(s.tc,{badDeveloper:true});
 const missingAuthority=await consumer.preflight(badDev);
 ok('original_Product_reconciler_rejects_invalid_developer_evidence',
  missingAuthority.status!=='READY','negative');
 receipt.negative.push({kind:'INVALID_DEVELOPER_EVIDENCE',status:missingAuthority.status,reason:missingAuthority.reason});
 ok('invalid_authority_did_not_change_native_TC',aggregate(await readSet(s)).state==='ACTIVE','negative');
 await nativeSetAttempt(s,'UNKNOWN');
 const unknown=await consumer.preflight(validRequest);
 ok('original_Product_consumer_preflight_blocks_UNKNOWN',
  unknown.status==='BLOCKED'&&unknown.reason==='UNKNOWN_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION','negative');
 receipt.negative.push({kind:'UNRESOLVED_UNKNOWN',status:unknown.status,reason:unknown.reason});
 await nativeSetAttempt(s,'RUNNING');
 const ready=await consumer.preflight(validRequest);
 ok('actual_Product_preflight_evidence_and_authority_READY',ready.status==='READY');
 const racedConsumer=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(s,{injectGateRace:true})});
 const raced=await racedConsumer.execute(validRequest);
 ok('original_Product_recipe_refuses_native_related_stale_batch',
  raced.status==='FAIL'&&raced.effect_state==='NONE','negative');
 receipt.negative.push({kind:'RELATED_RACE',status:raced.status,effect_state:raced.effect_state,reason:raced.reason});
 ok('stale_related_read_set_left_TC_ACTIVE',aggregate(await readSet(s)).state==='ACTIVE','negative');
 await nativeSetAttempt(s,'RUNNING');
 const again=await consumer.preflight(validRequest);
 ok('preflight_READY_after_synthetic_attempt_reconciliation',again.status==='READY');
 const otherNative=cmdJ(['create','TS021 unrelated control','--type','task',
  '--id','ts021-unrelated','--force','--description','SYNTHETIC_UNRELATED_ONLY']);
 ok('unrelated_issue_created',(Array.isArray(otherNative)?otherNative[0]:otherNative).id==='ts021-unrelated');
 const unrelated=await batch([patch('ts021-unrelated',{ts021_marker:'unrelated-changed'})],
  'unrelated-independent-writer');
 ok('unrelated_native_issue_mutated_before_closure',unrelated.ok);
 const result=await consumer.execute(validRequest);
 ok('original_Product_recipe_with_async_native_Beads_reaches_PASS',
  result.status==='PASS'&&result.effect_state==='CONFIRMED');
 ok('original_Product_recipe_evidence_is_RESOLVED',result.output?.reconciliation?.disposition==='RESOLVED');
 ok('native_TaskCycle_terminal_and_receipt_correspondence',
  aggregate(await readSet(s)).state==='CLOSED'&&result.output?.transition?.after==='CLOSED');
 const duplicate=await consumer.execute(validRequest);
 ok('repeat_of_terminal_taskcycle_rejected_without_new_effect',
  duplicate.status==='FAIL'&&duplicate.effect_state==='NONE','negative');
 receipt.negative.push({kind:'TERMINAL_REPLAY',status:duplicate.status,effect_state:duplicate.effect_state});
 const ack=cases[1];
 const ackConsumer=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(ack,{ackLoss:true})});
 const ackReq=req(ack.tc);
 const ackReady=await ackConsumer.preflight(ackReq);
 ok('separate_receipt_loss_case_ready',ackReady.status==='READY');
 const lost=await ackConsumer.execute(ackReq);
 ok('original_Product_recipe_classifies_durable_effect_with_bad_ack_CONFIRMED',
  lost.status==='FAIL'&&lost.effect_state==='CONFIRMED'&&
  String(lost.reason).includes('EFFECT_CONFIRMED_BUT_UNACKNOWLEDGED'),'negative');
 receipt.negative.push({kind:'SYNTHETIC_RESPONSE_CORRUPTION_AFTER_NATIVE_COMMIT',
  status:lost.status,effect_state:lost.effect_state,reason:lost.reason});
 ok('reobserve_exact_native_ack_loss_effect_without_retry',
  aggregate(await readSet(ack)).state==='CLOSED');
 await stop();
 for(const subject of cases){
  const root=show(subject.root),x=metadata(root);
  ok('fresh_native_cli_terminal_readback_'+subject.tc,
   root.status==='closed'&&x.ts021_taskcycle.state==='CLOSED');
 }
 receipt.metrics.native_calls.total_api_calls=receipt.metrics.native_calls.reads+receipt.metrics.native_calls.batches;
 receipt.metrics.implemented_test_coverage={
  actual_Product_preflight_and_execute:true,actual_Product_reconciliation:true,
  actual_Product_receipt_semantics:true,
  full_pending_obligations_mutation:false,
  original_Product_suite_replay:false,
  native_taskcycle_closed:true,provider_ack_loss:'synthetic_response_corruption_only'};
 receipt.status='PASS_REAL_PRODUCT_CONSUMER_ASYNC_BEADS_FIRST_WITH_LIMITATIONS';
 receipt.disposition='RESEARCH_CANDIDATE_ONLY';
 console.log('TS_BEADS021=PASS;checks='+receipt.check.length+
  ';Product_consumer=ACTUAL_MEMORY_ADAPTED;native_closure=PASS;unknown=BLOCKED;ack_loss=CONFIRMED;Product=NONE');
}catch(e){receipt.status='FAIL_RECONCILE_ATTEMPT_AND_NATIVE_EFFECTS';receipt.error=String(e?.stack||e);
 console.error('TS_BEADS021_ERROR='+receipt.error);throw e;
}finally{
 try{await stop()}catch(e){receipt.shutdown_error=String(e)}
 writeFileSync(OUTPUT,JSON.stringify(receipt,null,2)+'\n','utf8');
 console.log('TS_BEADS021_RECEIPT='+OUTPUT+';status='+receipt.status);
}
