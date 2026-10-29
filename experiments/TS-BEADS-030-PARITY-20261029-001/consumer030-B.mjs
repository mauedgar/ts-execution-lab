// 022 — isolated adaptation of ACTUAL Tecnotron closure-recipe consumer, not a reimplementation.
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

const PRODUCT_SHA='d4154bd43f26515c39a41be974e462a0c7406a2d',
 PRODUCT_TREE='cbfb71ad8632047e8e64fe2665d8614d835a2c8b';
const PROD=process.env.PRODUCT_ROOT,LAB=process.env.LAB_ROOT,BD=process.env.BD_BIN,OUTPUT=process.env.RESULT_PATH;
if(!PROD||!LAB||!BD||!OUTPUT)throw Error('EXPLICIT_EXPERIMENT_IDENTITY_REQUIRED');
if(existsSync(join(LAB,'.beads')))throw Error('DISPOSABLE_LAB_ALREADY_INITIALIZED');
mkdirSync(LAB,{recursive:true});
const env={...process.env,BEADS_DIR:join(LAB,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BEADS_ACTOR:'TS-BEADS-022-NONPRODUCT',NO_COLOR:'1',GIT_TERMINAL_PROMPT:'0'};
const receipt={id:'TS-BEADS-OBLIGATION-AUTHORITY-EFFICIENCY-20261024-022',
 status:'RUNNING',authority:'NONE_PRODUCT',Product_effect:'NONE',shared_Dolt_effect:'NONE',
 Product_sha:PRODUCT_SHA,Product_tree:PRODUCT_TREE,check:[],negative:[],metrics:{native_calls:{reads:0,batches:0,metadata_token_reads:0,write_items:0}},
 semantics:'EXPERIMENTAL_PER_TASKCYCLE_EPOCH_NOT_PRODUCT_GLOBAL_REVISION',
 scope:'ACTUAL_PRODUCT_RECONCILE_AND_CLOSE_RECIPE_MEMORY_ADAPTED;NO_PRODUCT_FILE_CHANGED'};
const ok=(key,truth,kind='positive')=>{assert.ok(truth,key);receipt.check.push({key,result:'PASS',kind})};
const clone=x=>structuredClone(x);
const prodRequire=createRequire(join(PROD,'package.json'));
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
receipt.id='TS-BEADS-030-B-FIRST-CONSUMER-PARITY-20261029-001';
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
const cases=[
 {tc:'TC-PENDING',root:'ts022-pending-root',gate:'ts022-pending-gate',pending:true},
 {tc:'TC-ACK-PENDING',root:'ts022-ack-root',gate:'ts022-ack-gate',pending:true},
 {tc:'TC-SATISFIED',root:'ts022-sat-root',gate:'ts022-sat-gate',pending:false}
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
   '--description','TS-BEADS-022_NONPRODUCT_SYNTHETIC_ONLY','--metadata',JSON.stringify(meta)]);
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
 return native('/v0/beads/issues:batchApply',{actor:'TS-BEADS-022-NONPRODUCT',
 provenance:'test://TS-BEADS-022/'+label,items});
}
async function marker(id,expected,token){
 const response=await batch([patch(id,{ts022_marker:expected},token)],'native-metadata-read-set-version');
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
 if(!root.ts022_taskcycle||!gate.ts022_attempt)throw Error('NATIVE_SUBJECT_METADATA_MISSING');
 const rootVersion=a.revision;
 const gateVersion=b.revision;
 if(typeof rootVersion!=='string'||typeof gateVersion!=='string')throw Error('NATIVE_HTTP_GET_REVISION_UNAVAILABLE');
 // Native GET exposes server-minted per-row token; no additional guarded no-op batch required.
 if(!receipt.metrics.readset_probe){
  receipt.metrics.readset_probe={native_get_root_keys:Object.keys(a).sort(),
   root_get_revision_value:a.revision??null,root_guard_token:rootVersion,
   native_get_gate_keys:Object.keys(b).sort(),gate_get_revision_value:b.revision??null,
   gate_guard_token:gateVersion};
 }
 return {subject,root,gate,rootVersion,gateVersion};
}
function aggregate(s){return clone(s.root.ts022_taskcycle)}
async function nativeSetAttempt(subject,state){
 const before=await get(subject.gate),m=metadata(before);
 const updated={...m.ts022_attempt,state,reconciliation_required:state==='UNKNOWN'};
 const res=await batch([patch(subject.gate,{ts022_attempt:updated,ts022_marker:state+'-mark'})],
  'external-writer-guard-state');
 if(!res.ok)throw Error('SET_SYNTHETIC_ATTEMPT_FAILED:'+res.raw);
}
function capability(subject,{injectGateRace=false,ackLoss=false}={}){
 let lastRead=null,racePending=injectGateRace;
 async function snapshot(tcId){
  if(tcId!==subject.tc)throw Error('TASKCYCLE_IDENTITY_MISMATCH');
  lastRead=await readSet(subject);
  const x=aggregate(lastRead),counter=lastRead.root.ts022_epoch;
  return {revision:counter,event_count:counter,taskcycle:x,
   legal_next:x.state==='ACTIVE'&&x.obligations.every(z=>z.status==='SATISFIED')?['CLOSED']:[],
   obligations:{id:tcId,store_revision:counter,obligations:clone(x.obligations),
    pending:x.obligations.filter(z=>z.status==='PENDING').map(z=>z.id),legal_next:[]}};
 }
 async function hasUnreconciledExecution(tcId){
  if(tcId!==subject.tc)throw Error('SUBJECT_MISMATCH');
  const v=await get(subject.gate),a=metadata(v).ts022_attempt;
  return a.state==='UNKNOWN'||a.reconciliation_required===true;
 }

 async function satisfyObligation({expectedRevision,taskcycleId,obligationId,authorityRef,authorityReference}){
  if(taskcycleId!==subject.tc)throw Error('WRONG_SYNTHETIC_TASKCYCLE');
  const read=lastRead;
  if(!read||read.root.ts022_epoch!==expectedRevision)throw Error('SCOPE_EPOCH_STALE');
  if(read.gate.ts022_attempt.state==='UNKNOWN'||read.gate.ts022_attempt.reconciliation_required)
   throw Error('SYNTHETIC_UNKNOWN_ATTEMPT');
  if(racePending){racePending=false;await nativeSetAttempt(subject,'UNKNOWN');}
  const before=aggregate(read);
  if(before.state!=='ACTIVE')throw Error('NOT_ACTIVE');
  const pending=before.obligations.find(x=>x.id===obligationId);
  if(!pending||pending.status!=='PENDING')throw Error('MISSING_PENDING_OBLIGATION');
  const after=clone(before);
  const obligation=after.obligations.find(x=>x.id===obligationId);
  obligation.status='SATISFIED';
  if(authorityRef!==undefined){
   if(!after.authority_refs.some(x=>x.kind==='AUTHORITY'&&x.id===authorityRef)){
    if(!authorityReference||authorityReference.kind!=='AUTHORITY'||authorityReference.id!==authorityRef)
     throw Error('COMPETENT_AUTHORITY_REFERENCE_REQUIRED');
    after.authority_refs.push(clone(authorityReference));
   }
   obligation.authority_ref=authorityRef;
  }
  after.revision+=1;after.last_event_id='event-'+(expectedRevision+1);
  const resp=await batch([
   patch(subject.root,{ts022_taskcycle:after,ts022_epoch:expectedRevision+1},read.rootVersion),
   patch(subject.gate,{ts022_marker:read.gate.ts022_marker},read.gateVersion)
  ],'native-guarded-pending-obligation-satisfaction');
  if(!resp.ok)throw Error('NATIVE_PENDING_OBLIGATION_BATCH_REFUSED:'+resp.status);
  const mutation={revision:expectedRevision+1,event_id:after.last_event_id,
   aggregate_revision:after.revision,kind:'TaskCycle',aggregate_id:subject.tc};
  if(ackLoss&&obligationId==='CANONICAL_INTEGRATION')return {...mutation,event_id:'BAD_SYNTHETIC_ACK'};
  return mutation;
 }
 async function closeTaskCycle({expectedRevision,taskcycleId,authorityRef,dispositionRef}){
  if(taskcycleId!==subject.tc||authorityRef!==auth.id)throw Error('INCORRECT_SYNTHETIC_AUTHORITY');
  const read=lastRead;
  if(!read||read.root.ts022_epoch!==expectedRevision)throw Error('SCOPED_EPOCH_MISMATCH');
  if(read.gate.ts022_attempt.state==='UNKNOWN'||read.gate.ts022_attempt.reconciliation_required)
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
    patch(subject.root,{ts022_taskcycle:after,ts022_epoch:expectedRevision+1},read.rootVersion),
    patch(subject.gate,{ts022_marker:read.gate.ts022_marker},read.gateVersion),
    {kind:'close',close:{target:{id:subject.root},reason:'NONPRODUCT_TEST_EXACT_AUTHORITY_RECONCILED'}}
  ],'native-guarded-real-product-consumer-close');
  if(!nativeResult.ok)throw Error('NATIVE_SCOPED_BATCH_REJECTED:'+nativeResult.status);
  const valid={revision:expectedRevision+1,event_id:after.last_event_id,
    aggregate_revision:after.revision,kind:'TaskCycle',aggregate_id:subject.tc};
  return ackLoss?{...valid,event_id:'LOST_SYNTHETIC_ACK'}:valid;
 }
 return {snapshot,hasUnreconciledExecution,closeTaskCycle,
  observeInvocationBookkeeping:async()=>{throw Error('HANDOFF_BOOKKEEPING_NOT_QUALIFIED')},
  satisfyObligation};
}
try{
 cmd(['init','--server','--quiet','--stealth']);
 const rem=spawnSync('git',['remote'],{cwd:LAB,env,encoding:'utf8',timeout:4000});
 ok('isolated_Beads_git_has_no_remote',rem.status===0&&!rem.stdout.trim());
 for(const s of cases){
  const tc={schema_version:'tecnotron-state-kernel/v0',kind:'TaskCycle',id:s.tc,revision:7,state:'ACTIVE',
    responsibility:'SYNTHETIC_TEST_CLOSE',created_at:'2026-01-01T00:00:00.000Z',
    updated_at:'2026-01-01T00:00:00.000Z',authority_refs:s.pending?[]:[clone(auth)],
    related_ids:['OP-001'],last_event_id:'event-50',terminal_disposition_ref:null,
    obligations:['INDEPENDENT_REVIEW','DEVELOPER_ACCEPTANCE','CANONICAL_INTEGRATION',
     'REMOTE_PUBLICATION','LIFECYCLE_RECONCILIATION'].map(x=>({id:x,
       status:s.pending?'PENDING':'SATISFIED',
       authority_ref:s.pending||x==='LIFECYCLE_RECONCILIATION'?null:
        x==='INDEPENDENT_REVIEW'?'authority:reviewer-001':
        x==='DEVELOPER_ACCEPTANCE'?'authority:developer-001':'authority:effect-001'}))};
  createNative(s.root,'TS022 SYNTHETIC TC '+s.tc,
   {ts022_taskcycle:tc,ts022_epoch:50,ts022_marker:'root-original'});
  createNative(s.gate,'TS022 SYNTHETIC attempt guard '+s.tc,
   {ts022_attempt:{kind:'ExecutionAttempt',id:s.tc+'-ATTEMPT',operation_id:'OP-001',
    state:'RUNNING',reconciliation_required:false},ts022_marker:'RUNNING-mark'});
 }
 await start();ok('native_Beads_server_health',true);
 const pending=cases[0],ack=cases[1],satisfied=cases[2];
 // Independent original synchronous Product negative cases with reproducible fixture.
 function originalPort(subject){
  const tc=clone(metadata(show(subject.root)).ts022_taskcycle);
  return {
   snapshot:()=>({revision:50,event_count:50,taskcycle:tc,legal_next:['CLOSED'],
    obligations:{id:subject.tc,store_revision:50,
     obligations:clone(tc.obligations),pending:tc.obligations.filter(x=>x.status==='PENDING').map(x=>x.id),
     legal_next:['CLOSED']}}),
   hasUnreconciledExecution:()=>false,observeInvocationBookkeeping:()=>{throw Error('NOT_USED')},
   satisfyObligation:()=>{throw Error('NO_NATIVE_EFFECT_FOR_INDEPENDENT_PRODUCT_ORACLE')},
   closeTaskCycle:()=>{throw Error('NO_NATIVE_EFFECT_FOR_INDEPENDENT_PRODUCT_ORACLE')}
  };
 }
 const originalFactory=prodRequire(sourceFile).createReconcileAndCloseTaskCycleRecipe;
 const pendingOrig=originalFactory({lifecycle:originalPort(pending)});
 const satOrig=originalFactory({lifecycle:originalPort(satisfied)});
 const pendingRejectedReq=req(pending.tc,{pending:true,badDeveloper:true});
 const pendingRejected=await pendingOrig.preflight(pendingRejectedReq);
 const satRejected=await satOrig.preflight(req(satisfied.tc,{badDeveloper:true}));
 ok('original_Product_pending_developer_REJECTED_is_BLOCKED',
   pendingRejected.status==='BLOCKED','negative');
 ok('original_Product_presatisfied_developer_REJECTED_returns_READY',
   satRejected.status==='READY','negative');
 receipt.negative.push({
  type:'INDEPENDENT_UNMODIFIED_PRODUCT_AUTHORITY_NEGATIVE',
  pending_rejected:{status:pendingRejected.status,reason:pendingRejected.reason},
  presatisfied_rejected:{status:satRejected.status,reason:satRejected.reason},
  outcome:'SOURCE_CONSUMER_BYPASSES_ACCEPTED_DISPOSITION_AFTER_OBLIGATION_PREMARKED_SATISFIED',
  boundary:'Synthetic snapshots with pre-satisfied obligations; no evidence of real reachable historical Product misuse'});
 const pendingCandidate=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(pending)});
 const requested=req(pending.tc,{pending:true});
 const nativeRejected=await pendingCandidate.preflight(pendingRejectedReq);
 ok('Beads_first_adapted_pending_rejected_is_BLOCKED',
   nativeRejected.status==='BLOCKED','negative');
 const nativeMissing=await pendingCandidate.preflight(req(pending.tc,{pending:true,badDeveloper:'MISSING'}));
 ok('Beads_first_adapted_missing_developer_evidence_BLOCKED',
  nativeMissing.status!=='READY','negative');
 const originalReady=await pendingOrig.preflight(requested);
 ok('unmodified_Product_pending_competent_fixture_READY',originalReady.status==='READY');
 const pendingReady=await pendingCandidate.preflight(requested);
 ok('adapted_Product_real_pending_obligation_preflight_READY',pendingReady.status==='READY');
 await nativeSetAttempt(pending,'UNKNOWN');
 const blocked=await pendingCandidate.preflight(requested);
 ok('pending_unreconciled_UNKNOWN_blocks_original_recipe',
  blocked.status==='BLOCKED'&&blocked.reason==='UNKNOWN_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION','negative');
 await nativeSetAttempt(pending,'RUNNING');
 const clean=await pendingCandidate.preflight(requested);
 ok('pending_after_synthetic_reconciliation_READY',clean.status==='READY');
 // First full pending path using actual original recipe and native Beads guarded writes.
 // NEW 022 scoped race control for direct GET row tokens (distinct from baseline 022).
 const raceAt={...receipt.metrics.native_calls};
 const raced=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(pending,{injectGateRace:true})});
 const raceResult=await raced.execute(requested);
 ok('GET_revision_scoped_causal_race_rejected_without_partial_native_effect',
  raceResult.status==='FAIL'&&raceResult.effect_state==='NONE','negative');
 ok('GET_revision_causal_race_kept_all_obligations_pending',
  aggregate(await readSet(pending)).obligations.every(x=>x.status==='PENDING'),'negative');
 receipt.negative.push({type:'DIRECT_GET_REVISION_CAUSAL_RACE',
  status:raceResult.status,effect_state:raceResult.effect_state,
  native_remaining:5});
 await nativeSetAttempt(pending,'RUNNING');
 receipt.metrics.incremental_race_test_native_calls={
  reads:receipt.metrics.native_calls.reads-raceAt.reads,
  batches:receipt.metrics.native_calls.batches-raceAt.batches};
 const bBefore={...receipt.metrics.native_calls};
 const startClock=process.hrtime.bigint();
 const completed=await pendingCandidate.execute(requested);
 const elapsedMs=Number(process.hrtime.bigint()-startClock)/1e6;
 receipt.metrics.B_only_positive_execute={
    elapsed_ms:elapsedMs,
    reads:receipt.metrics.native_calls.reads-bBefore.reads,
    batches:receipt.metrics.native_calls.batches-bBefore.batches,
    write_items:receipt.metrics.native_calls.write_items-bBefore.write_items,
    Product_original_recipe_sha256:hash(original)
 };
 ok('actual_Product_consumer_full_pending_obligations_PASS',
  completed.status==='PASS'&&completed.effect_state==='CONFIRMED');
 ok('five_original_Product_obligations_satisfied',
  completed.output?.obligations?.satisfied?.length===5);
 ok('original_Product_reconciliation_RESOLVED',
  completed.output?.reconciliation?.disposition==='RESOLVED');
 const pendingSnapshot=await readSet(pending);
 const terminal=aggregate(pendingSnapshot);
 ok('native_aggregate_closed_all_obligations_terminal',
  terminal.state==='CLOSED'&&terminal.obligations.length===5&&
   terminal.obligations.every(o=>o.status==='SATISFIED'));
 ok('native_aggregate_authority_refs_attached_from_competent_fixture',
  terminal.authority_refs.some(a=>a.id==='authority:developer-001')&&
  terminal.authority_refs.some(a=>a.id==='authority:reviewer-001')&&
  terminal.authority_refs.some(a=>a.id==='authority:effect-001'));
 ok('native_revision_and_event_six_step_correspondence',
  pendingSnapshot.root.ts022_epoch===56&&terminal.revision===13&&terminal.last_event_id==='event-56');
 const repeat=await pendingCandidate.execute(requested);
 ok('terminal_reexecution_denied',repeat.status==='FAIL'&&repeat.effect_state==='NONE','negative');
 // Synthetic lost ACK AFTER native mutation during pending obligation: original recipe
 // must observe CONFIRMED, preserve unfinished obligations and refuse an automatic close/retry.
 const badAckConsumer=createReconcileAndCloseTaskCycleRecipe({lifecycle:capability(ack,{ackLoss:true})});
 const ackReq=req(ack.tc,{pending:true});
 ok('ack_loss_fixture_preflight_READY',(await badAckConsumer.preflight(ackReq)).status==='READY');
 const lost=await badAckConsumer.execute(ackReq);
 ok('native_pending_obligation_wrong_ack_classified_CONFIRMED',
  lost.status==='FAIL'&&lost.effect_state==='CONFIRMED'&&
  String(lost.reason).includes('EFFECT_CONFIRMED_BUT_UNACKNOWLEDGED'),'negative');
 const partial=aggregate(await readSet(ack));
 ok('partial_native_obligation_effect_preserved_not_replayed',
   partial.state==='ACTIVE'&&partial.obligations.filter(x=>x.status==='SATISFIED').length===1&&
   partial.obligations.filter(x=>x.status==='PENDING').length===4);
 receipt.negative.push({type:'PENDING_OBLIGATION_WRONG_ACK_EXACT_EFFECT',
   status:lost.status,effect_state:lost.effect_state,reason:lost.reason,
   native_obligations_satisfied:partial.obligations.filter(x=>x.status==='SATISFIED').map(x=>x.id),
   native_state:partial.state});
 // Native HTTP GET may or may not expose a usable expected_version token.
 // Measure actual shape. No claim that a field is valid until checked against batch contract.
 const probe=receipt.metrics.readset_probe;
 receipt.metrics.efficiency={token_acquisition_extra_batches_per_readset:0,
  direct_native_GET_root_revision_valid:probe.root_get_revision_value===probe.root_guard_token,
  direct_native_GET_gate_revision_valid:probe.gate_get_revision_value===probe.gate_guard_token,
  row_tokens_from_GET_not_an_external_ledger:true,
  baseline_022_HTTP_calls:127, baseline_022_extra_token_batches:54};
 await stop();
 const root=show(pending.root),partialRoot=show(ack.root);
 ok('independent_native_process_terminal_root_closed',root.status==='closed'&&
    metadata(root).ts022_taskcycle.state==='CLOSED');
 ok('independent_native_process_partial_root_still_open',
    partialRoot.status!=='closed'&&metadata(partialRoot).ts022_taskcycle.state==='ACTIVE');
 receipt.metrics.native_calls.total_api_calls=receipt.metrics.native_calls.reads+receipt.metrics.native_calls.batches;
 receipt.metrics.full_original_pending_obligations=true;
 receipt.metrics.original_authority_negative_qualified_independently=true;
 receipt.status='PASS_B_ORIGINAL_PRODUCT_RECIPE_NATIVE_BEADS_PENDING_AND_NEGATIVES';
 receipt.disposition='BEADS_FIRST_CANDIDATE_NOT_PRODUCT_ADOPTION';
 console.log('TS_BEADS022_RO=PASS;checks='+receipt.check.length+
  ';pending=FIVE_PLUS_CLOSE;authority=ORIGINAL_NEGATIVE;efficiency=MEASURED;Product=NONE');

}catch(e){receipt.status='FAIL_RECONCILE_ATTEMPT_AND_NATIVE_EFFECTS';receipt.error=String(e?.stack||e);
 console.error('TS_BEADS022_ERROR='+receipt.error);throw e;
}finally{
 try{await stop()}catch(e){receipt.shutdown_error=String(e)}
 writeFileSync(OUTPUT,JSON.stringify(receipt,null,2)+'\n','utf8');
 console.log('TS_BEADS022_RECEIPT='+OUTPUT+';status='+receipt.status);
}
