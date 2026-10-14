// TS-BEADS-018 | Native separate-issue lifecycle/effect recovery laboratory.
// Original Product contracts read-only; native Beads workspace and provider fixture disposable.
// This is NOT a Product TaskCycle port implementation and DOES NOT provide Developer authority.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readFileSync,writeFileSync,openSync,fsyncSync,closeSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const BD=process.env.BD_BIN,ROOT=process.env.LAB_ROOT,PROD=process.env.PRODUCT_ROOT,
 PROVIDER=process.env.PROVIDER_ROOT,OUT=process.env.RESULT_PATH;
if(!BD||!ROOT||!PROD||!PROVIDER||!OUT)throw Error('MISSING_EXPLICIT_LAB_BINDING');
if(existsSync(join(ROOT,'.beads')))throw Error('NONEMPTY_BEADS_ROOT_FORBIDDEN');
mkdirSync(ROOT,{recursive:true});mkdirSync(PROVIDER,{recursive:true});
const fsEnv={...process.env,BEADS_DIR:join(ROOT,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BEADS_ACTOR:'ts018-test-nonproduct',GIT_TERMINAL_PROMPT:'0',NO_COLOR:'1'};
const mod=createRequire(join(PROD,'package.json'));
const {validateAggregate,TRANSITIONS}=mod(join(PROD,'src/state-kernel-v0/contracts.js'));
const {requireExecutionLifecycleCapability,requireTaskCycleLifecycleCapability}=
 mod(join(PROD,'src/operational-spine-v0/taskcycle-lifecycle-capability.js'));
const PRODUCT_REF='mauedgar/tecnotron-ai:tools@f40236d24023159bc38aca06b3fa3862ac62608c';
const ids={tc:'ts018-tc',op:'ts018-op',at:'ts018-at'};
const names={tc:'TC-018-LAB',op:'OP-018-LAB',at:'AT-018-LAB'};
const effect={id:'EXECUTION-EFFECT-018-SYNTHETIC',provider:'LOCAL_PROVIDER_FIXTURE_NOT_REAL',
 subject:'mauedgar/ts-execution-lab:synthetic@TS018',operation:names.op,
 attempt:names.at,request_hash:createHash('sha256').update('TS018-exact-provider-effect-request').digest('hex')};
const authority=[{kind:'AUTHORITY',id:'DEV-018-SYNTHETIC',location:'test://ts018/authority'}];
const check=[],observed=[];
const report={
 experiment:'TS-BEADS-LIFECYCLE-EFFECT-RECOVERY-20261014-018',
 status:'RUNNING',authority:'NONE_PRODUCT',Product_effect:'NONE',remote_shared_dolt_effect:'NONE',
 Product_source:PRODUCT_REF,provider_kind:'INDEPENDENT_LOCAL_DURABLE_SYNTHETIC_FIXTURE',
 native_provider:'Beads v1.3.1 on disposable Dolt SQL Server',
 check,observed,qualified:[],not_qualified:[]
};
const ok=(id,p,kind='NATIVE')=>{assert.ok(p,id);check.push({id,result:'PASS',kind})};
const sha=(x)=>createHash('sha256').update(x).digest('hex');
const cloned=x=>structuredClone(x);
function bd(args){
 const r=spawnSync(BD,args,{cwd:ROOT,env:fsEnv,encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
 if(r.error||r.status!==0)throw Error('BD_FAIL:'+args.slice(0,4).join('_')+':'+JSON.stringify({code:r.status,out:r.stdout,err:r.stderr,error:r.error?.message}).slice(0,800));
 return (r.stdout||'').trim();
}
function bdJson(args){const t=bd([...args,'--json']),i=t.search(/[\[{]/);if(i<0)throw Error('NATIVE_BD_JSON_MISSING');return JSON.parse(t.slice(i));}
function bdShow(id){const a=bdJson(['show',id]),x=Array.isArray(a)?a[0]:a;if(x.id!==id)throw Error('ISSUE_READBACK_ID_MISMATCH');return x;}
function meta(id){const m=bdShow(id).metadata;return typeof m==='string'?JSON.parse(m):m;}
function valid(x){assert.ok(validateAggregate(x));return x;}
const stamp='2026-10-14T00:00:00.000Z';
const common=(kind,id,state)=>({schema_version:'tecnotron-state-kernel/v0',kind,id,revision:1,state,
 created_at:stamp,updated_at:stamp,authority_refs:cloned(authority),related_ids:[],last_event_id:null});
const tc=valid({...common('TaskCycle',names.tc,'ACTIVE'),responsibility:'TS018_SYNTHETIC_PORT_TEST',
 obligations:[{id:'INDEPENDENT_REVIEW',status:'PENDING',authority_ref:'DEV-018-SYNTHETIC'}],
 terminal_disposition_ref:null});
const op=valid({...common('Operation',names.op,'RUNNING'),taskcycle_id:names.tc,objective:'TS018 synthetic effect',result_ref:null});
const at=valid({...common('ExecutionAttempt',names.at,'DISPATCHED'),operation_id:names.op,outcome:null,
 reconciliation_required:false,result_refs:[]});
let srv=null,stopped=true,srvOut='',srvErr='',base='',nativeStartCount=0;
async function start(){
 const port=31200+(Number(process.env.GITHUB_RUN_ID||1818)%19000);
 base='http://127.0.0.1:'+port;
 stopped=false;nativeStartCount++;
 srv=spawn(BD,['serve','--addr','127.0.0.1:'+port],{cwd:ROOT,env:fsEnv,windowsHide:true,
  stdio:['ignore','pipe','pipe']});
 srv.stdout.on('data',x=>srvOut+=String(x));
 srv.stderr.on('data',x=>srvErr+=String(x));
 for(let i=0;i<95;i++){
  if(srv.exitCode!==null||srv.signalCode!==null)throw Error('SERVE_EXITED:'+srvErr.slice(-450));
  try{const r=await fetch(base+'/healthz',{signal:AbortSignal.timeout(500)});
   if(r.ok)return;}catch{}
  await delay(220);
 }
 throw Error('NATIVE_HTTP_HEALTH_NOT_READY:'+srvErr.slice(-650));
}
async function stop(){
 if(!srv||stopped)return;
 stopped=true;
 if(srv.exitCode===null&&srv.signalCode===null){
  srv.kill();await Promise.race([new Promise(resolve=>srv.once('exit',resolve)),delay(6500)]);
 }
 if(srv.exitCode===null&&srv.signalCode===null)throw Error('NATIVE_HTTP_KILL_NOT_CONFIRMED');
 srv=null;
}
async function http(path,body){
 const opt=body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
 const res=await fetch(base+path,{...opt,signal:AbortSignal.timeout(14000)});
 const raw=await res.text();let data;try{data=JSON.parse(raw)}catch{data=null}
 return {code:res.status,ok:res.ok,data,raw};
}
async function issue(id){const r=await http('/v0/beads/issues/'+id);
 if(!r.ok)throw Error('HTTP_ISSUE_READ_FAILED:'+id+':'+r.code);
 return r.data;
}
async function aggregate(id){const r=await issue(id);
 function find(v,depth=0){
  if(depth>6||v===null||typeof v!=='object')return null;
  if(v.id===id&&v.metadata){let m=v.metadata;if(typeof m==='string')m=JSON.parse(m);return m.ts018_aggregate}
  for(const vv of Object.values(v)){const z=find(vv,depth+1);if(z)return z;}return null;
 }
 const result=find(r);if(!result)throw Error('NATIVE_AGGREGATE_MISSING:'+id+':'+JSON.stringify(r).slice(0,400));
 return valid(result);
}
async function cas(id,prev,next){
 valid(next);
 const r=await http('/v0/beads/issues/'+id+':casMetadata',{
  actor:'TS018-SYNTHETIC-PORT',key:'ts018_aggregate',expected:prev,value:next
 });
 if(!r.ok||typeof r.data?.swapped!=='boolean')throw Error('HTTP_CAS_ERROR:'+id+':'+r.code+':'+r.raw.slice(0,430));
 return r.data;
}
async function batch(items,provenance='test://TS018/SYNTHETIC-NATIVE-TRANSACTION'){
 return http('/v0/beads/issues:batchApply',{actor:'TS018-NONPRODUCT',provenance,items});
}
const tRef=id=>({id});
const patch=(id,metadata,expected_version)=>({kind:'update',update:{
 target:tRef(id), ...(expected_version?{expected_version}:{}),
 patch:{metadata:{set:metadata}}}});
function issueCreate(id,title,x){
 const r=bdJson(['create',title,'--id',id,'--force','--type','task',
 '--description','LAB_ONLY;NO_PRODUCT_EFFECT;REF='+PRODUCT_REF,
 '--metadata',JSON.stringify({ts018_aggregate:x})]);
 const j=Array.isArray(r)?r[0]:r;ok('fixture_'+id+'_created',j.id===id);
}
function receiptPath(){return join(PROVIDER,'effect-'+effect.id+'.json')}
function providerExecuteOnce(){
 const path=receiptPath();
 if(existsSync(path))return {created:false,receipt:JSON.parse(readFileSync(path,'utf8'))};
 const unsigned={schema:'ts018-synthetic-external-receipt-v1',...effect,status:'CONFIRMED',
  observed_at:'2026-10-14T00:00:00.000Z',provider_ack:'SYNTHETIC_LOCAL_FILE'};
 const receipt={...unsigned,sha256:sha(JSON.stringify(unsigned))};
 const fd=openSync(path,'wx');
 try{writeFileSync(fd,JSON.stringify(receipt,null,2)+'\n','utf8');fsyncSync(fd)}finally{closeSync(fd)}
 return {created:true,receipt};
}
function providerReobserve(receipt){
 const path=receiptPath();if(!existsSync(path))return false;
 const actual=JSON.parse(readFileSync(path,'utf8'));
 const {sha256:digest,...payload}=actual;
 if(sha(JSON.stringify(payload))!==digest)return false;
 if(receipt&&JSON.stringify(actual)!==JSON.stringify(receipt))return false;
 return actual.provider===effect.provider&&actual.id===effect.id&&actual.subject===effect.subject&&
  actual.operation===effect.operation&&actual.attempt===effect.attempt&&
  actual.request_hash===effect.request_hash&&actual.status==='CONFIRMED';
}
function next(x,state,event,more={}){
 const o={...cloned(x),...more,revision:x.revision+1,state,
  updated_at:stamp,last_event_id:event};
 return valid(o);
}
async function token(id,phase){
 // A native metadata update is a genuine row mutation and returns a server-minted,
 // equality-only issue row revision token for native batchApply expected_version.
 const r=await batch([patch(id,{ts018_token_phase:phase})],'test://TS018/acquire-exact-native-row-version');
 if(!r.ok)throw Error('NATIVE_REVISION_PROBE_REFUSED:'+r.code+':'+r.raw.slice(0,550));
 const token=r.data?.items?.[0]?.revision;
 if(typeof token!=='string'||!token)throw Error('NATIVE_REVISION_TOKEN_MISSING:'+JSON.stringify(r.data));
 return token;
}
const inspect={};
async function opRead(){const a=await aggregate(ids.op);return {aggregate:a,store_revision:a.revision,legal_next:TRANSITIONS.Operation[a.state]||[]}}
async function attemptRead(){return aggregate(ids.at)}
const executionLifecycle={
 observeOperation:()=>opRead(),
 observeAttemptPresence:async (attemptId)=>{if(attemptId===names.at)return 'PRESENT';return 'UNKNOWN'},
 prepareAttempt:async ({attemptId,operationId,authorityRefs})=>{
  if(operationId!==names.op)throw Error('OPERATION_ID_MISMATCH');
  const prior=await attemptRead();
  if(prior.reconciliation_required)throw Error('UNKNOWN_EFFECT_REQUIRES_RECONCILIATION');
  if(attemptId===names.at)return {operation:await opRead(),attempt:{aggregate:prior,store_revision:prior.revision,legal_next:[]}};
  throw Error('NOT_QUALIFIED_MULTI_ATTEMPT_PREPARE');
 },
 confirmDispatchStart:async attemptId=>{
  if(attemptId!==names.at)throw Error('ATTEMPT_ID_MISMATCH');
  return {aggregate:await attemptRead()};
 },
 recordPreflightTerminalOutcome:async()=>{throw Error('UNQUALIFIED_PREFLIGHT_TERMINAL_OUTCOME')},
 recordExecutionOutcome:async ({attemptId,operationId,coordinatorOutcome})=>{
  if(attemptId!==names.at||operationId!==names.op)throw Error('ATTEMPT_OPERATION_ID_MISMATCH');
  if(coordinatorOutcome.status!=='UNKNOWN')throw Error('ONLY_UNKNOWN_QUALIFIED');
  const before=await attemptRead();
  const after=next(before,'UNKNOWN','test://TS018/outcome-unknown',
   {outcome:'UNKNOWN',reconciliation_required:true});
  const r=await cas(ids.at,before,after);
  if(!r.swapped)throw Error('LOST_NATIVE_CAS_DURING_UNKNOWN');
  return {attempt:{aggregate:r.current},operation:await opRead()};
 }
};
const taskcycleLifecycle={
 snapshot:async()=>{const x=await aggregate(ids.tc);return {
  revision:x.revision,event_count:null,taskcycle:x,legal_next:TRANSITIONS.TaskCycle[x.state]||[],
  obligations:{id:x.id,store_revision:x.revision,obligations:x.obligations,
  pending:x.obligations.filter(z=>z.status==='PENDING').map(z=>z.id),legal_next:[]}
 }},
 observeInvocationBookkeeping:async()=>({revision:null,operation:(await opRead()).aggregate,attempt:await attemptRead()}),
 hasUnreconciledExecution:async()=> (await attemptRead()).reconciliation_required,
 satisfyObligation:async ({expectedRevision,taskcycleId,obligationId,authorityRef})=>{
  if(taskcycleId!==names.tc||obligationId!=='INDEPENDENT_REVIEW'||authorityRef!==authority[0].id)
   throw Error('COMPETENT_AUTHORITY_ID_REQUIRED');
  const before=await aggregate(ids.tc);
  if(before.revision!==expectedRevision)throw Error('LIFECYCLE_REVISION_DRIFT');
  const after=next(before,before.state,'test://TS018/satisfy', {obligations:before.obligations.map(x=>
   ({...x,status:'SATISFIED',authority_ref:authorityRef}))});
  const r=await cas(ids.tc,before,after);
  if(!r.swapped)throw Error('STALE_NATIVE_CAS');
  return {revision:r.current.revision,event_id:r.current.last_event_id,
   aggregate_revision:r.current.revision,kind:'TaskCycle',aggregate_id:names.tc};
 },
 closeTaskCycle:async ({expectedRevision,taskcycleId,authorityRef,dispositionRef})=>{
  const before=await aggregate(ids.tc);
  if(taskcycleId!==names.tc||expectedRevision!==before.revision)throw Error('LIFECYCLE_REVISION_DRIFT');
  if(authorityRef!==authority[0].id||!dispositionRef)throw Error('MISSING_COMPETENT_CLOSURE_AUTHORITY');
  if(before.obligations.some(x=>x.status!=='SATISFIED'))throw Error('UNSATISFIED_OBLIGATION');
  if(await taskcycleLifecycle.hasUnreconciledExecution(taskcycleId))throw Error('UNKNOWN_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION');
  const after=next(before,'CLOSED','test://TS018/close',{terminal_disposition_ref:dispositionRef});
  // A compare of ONE native issue's row version + same-transaction issue close.
  const rev=await token(ids.tc,'ready_for_guarded_close');
  const native=await batch([
    patch(ids.tc,{ts018_aggregate:after},rev),
    {kind:'close',close:{target:tRef(ids.tc),reason:'LAB_ONLY_SYNTHETIC_LIFECYCLE'}}
  ],'test://TS018/qualified-limited-taskcycle-close');
  if(!native.ok)throw Error('ATOMIC_CLOSE_REFUSED:'+native.code+':'+native.raw.slice(0,650));
  return {revision:after.revision,event_id:after.last_event_id,
   aggregate_revision:after.revision,kind:'TaskCycle',aggregate_id:names.tc};
 }
};
try{
 ok('Product_source_TRANSITIONS_loaded',TRANSITIONS.TaskCycle.ACTIVE.includes('CLOSED'),'PRODUCT_CONTRACT');
 const typedExec=requireExecutionLifecycleCapability(executionLifecycle);
 const typedTC=requireTaskCycleLifecycleCapability(taskcycleLifecycle);
 ok('real_Product_structural_lifecycle_ports_accept_method_set',
  typedExec===executionLifecycle&&typedTC===taskcycleLifecycle,'PRODUCT_PORT_STRUCTURAL');
 observed.push({key:'port_sync_gap',Product_methods:'SYNCHRONOUS',experiment_methods:'ASYNC_PROMISE',
  status:'NOT_DROP_IN_EQUIVALENT'});
 bd(['init','--server','--quiet','--stealth']);
 issueCreate(ids.tc,'TS018 SYNTHETIC TASKCYCLE',tc);
 issueCreate(ids.op,'TS018 SYNTHETIC OPERATION',op);
 issueCreate(ids.at,'TS018 SYNTHETIC ATTEMPT',at);
 bd(['dep','add',ids.tc,ids.op,'--type','blocks']);
 await start();
 ok('native_dolt_server_health',true);
 const originalTC=(await typedTC.snapshot(names.tc));
 ok('original_Product_taskcycle_aggregate_readback',originalTC.taskcycle.state==='ACTIVE'&&originalTC.obligations.pending.length===1);
 ok('native_attempt_presence_from_partial_port',await typedExec.observeAttemptPresence(names.at)==='PRESENT','PORT_SUBSET');
 ok('native_operation_running_from_partial_port',(await typedExec.observeOperation(names.op)).aggregate.state==='RUNNING','PORT_SUBSET');
 ok('native_initial_zero_unknown',!(await typedTC.hasUnreconciledExecution(names.tc)),'PORT_SUBSET');
 const enteredUnknown=await typedExec.recordExecutionOutcome({attemptId:names.at,operationId:names.op,coordinatorOutcome:{status:'UNKNOWN'}});
 ok('native_cas_UNKNOWN_written_through_partial_port',
  enteredUnknown.attempt.aggregate.state==='UNKNOWN'&&enteredUnknown.attempt.aggregate.reconciliation_required,'PORT_SUBSET');
 const snapshotAfterUnknown=await typedTC.snapshot(names.tc);
 ok('native_TC_revision_does_not_track_attempt_mutation',
  snapshotAfterUnknown.revision===originalTC.revision,'NEGATIVE_GLOBAL_REVISION');
 let blocked=false;try{await typedExec.prepareAttempt({attemptId:'AT-018-RETRY',operationId:names.op,authorityRefs:[]})}
 catch(e){blocked=String(e).includes('UNKNOWN_EFFECT_REQUIRES_RECONCILIATION')}
 ok('Product_guard_blocks_retry_while_UNKNOWN',blocked,'PORT_SUBSET');
 const external=providerExecuteOnce();
 ok('synthetic_provider_confirmed_once',external.created&&providerReobserve(external.receipt),'SYNTHETIC_EXTERNAL_ORACLE');
 const sameExternal=providerExecuteOnce();
 ok('synthetic_external_effect_idempotent_reobserve',
  !sameExternal.created&&providerReobserve(sameExternal.receipt),'SYNTHETIC_EXTERNAL_ORACLE');
 // Simulate native client losing the provider response after its write.
 const wrong={...external.receipt,attempt:'AT-018-OTHER'};
 ok('wrong_attempt_receipt_is_rejected',!providerReobserve(wrong),'NEGATIVE_RECEIPT_MATCH');
 const wrongHash={...external.receipt,request_hash:'0'.repeat(64)};
 ok('wrong_request_hash_receipt_is_rejected',!providerReobserve(wrongHash),'NEGATIVE_RECEIPT_MATCH');
 let prematureBlocked=false;try{
  await typedTC.closeTaskCycle({expectedRevision:originalTC.revision,taskcycleId:names.tc,
   authorityRef:authority[0].id,dispositionRef:'test://TS018/unapproved'});
 }catch(e){prematureBlocked=/UNSATISFIED_OBLIGATION|UNKNOWN_EXECUTION/.test(String(e))}
 ok('Product_semantic_guard_rejects_premature_TC_close',prematureBlocked,'PORT_SUBSET');
 await stop();await start();
 ok('native_Beads_HTTP_restart_recovered_UNKNOWN',
  (await attemptRead()).state==='UNKNOWN'&&await typedTC.hasUnreconciledExecution(names.tc),'PORT_SUBSET');
 ok('external_provider_receipt_survives_independent_restart',
  providerReobserve(external.receipt),'SYNTHETIC_EXTERNAL_ORACLE');
 // Simulate provider outcome verified by exact identity, but not actual provider authority.
 if(!providerReobserve(external.receipt))throw Error('EXTERNAL_RECEIPT_NOT_CORRESPONDENT');
 const atBefore=await attemptRead(),opBefore=(await opRead()).aggregate;
 const atComplete=next(atBefore,'COMPLETED','test://TS018/reconciled-confirmed',
  {outcome:'PASS',reconciliation_required:false,
   result_refs:[{kind:'EVIDENCE',id:effect.id,location:'test://TS018/provider-fixture',sha256:external.receipt.sha256}]});
 const opComplete=next(opBefore,'COMPLETED','test://TS018/operation-completed',
  {result_ref:'test://TS018/provider-fixture/'+external.receipt.sha256});
 const staleAt=await token(ids.at,'version_before_injected_race');
 const staleOp=await token(ids.op,'version_before_injected_race');
 const racedOp=await token(ids.op,'other_writer_advanced_native_version');
 const refused=await batch([
  patch(ids.at,{ts018_aggregate:atComplete},staleAt),
  patch(ids.op,{ts018_aggregate:opComplete},staleOp)
 ],'test://TS018/reject-cross-issue-stale-version');
 ok('native_expected_version_miss_rejects_entire_transaction',refused.code>=400,'NEGATIVE_NATIVE');
 ok('native_failed_batch_did_not_partially_clear_UNKNOWN',
  (await attemptRead()).state==='UNKNOWN'&&(await opRead()).aggregate.state==='RUNNING','NEGATIVE_NATIVE');
 const freshAt=await token(ids.at,'reconcile_version_current');
 const freshOp=await token(ids.op,'reconcile_version_current');
 const settled=await batch([
  patch(ids.at,{ts018_aggregate:atComplete},freshAt),
  patch(ids.op,{ts018_aggregate:opComplete},freshOp),
  {kind:'close',close:{target:tRef(ids.at),reason:'SYNTHETIC_ATTEMPT_RECONCILED'}},
  {kind:'close',close:{target:tRef(ids.op),reason:'SYNTHETIC_OPERATION_FINISHED'}},
 ],'test://TS018/reconcile-exact-receipt-in-one-native-transaction');
 if(!settled.ok)throw Error('NATIVE_NATIVE_TRANSACTION_REFUSED:'+settled.code+':'+settled.raw.slice(0,800));
 ok('native_multi_issue_reconciliation_one_transaction',settled.data?.items?.length===4,'NATIVE');
 ok('native_recovered_attempt_and_operation_complete',
  (await attemptRead()).state==='COMPLETED'&&(await opRead()).aggregate.state==='COMPLETED');
 ok('native_UNKNOWN_flag_cleared_only_after_exact_receipt',
  !(await typedTC.hasUnreconciledExecution(names.tc)),'PORT_SUBSET');
 // This port is NOT global-revision conforming: original TaskCycle revision still 1.
 ok('native_global_revision_missing_after_cross_aggregate_mutations',
  (await typedTC.snapshot(names.tc)).revision===originalTC.revision,'NEGATIVE_GLOBAL_REVISION');
 let illegal=false;
 try{await typedTC.satisfyObligation({expectedRevision:1,taskcycleId:names.tc,
  obligationId:'INDEPENDENT_REVIEW',authorityRef:'WRONG_AUTHORITY'})}
 catch(e){illegal=/COMPETENT_AUTHORITY/.test(String(e))}
 ok('Product_obligation_authority_guard_is_required',illegal,'PORT_SUBSET');
 const satisfaction=await typedTC.satisfyObligation({
  expectedRevision:1,taskcycleId:names.tc,
  obligationId:'INDEPENDENT_REVIEW',authorityRef:authority[0].id});
 ok('Product_validated_obligation_lands_in_Beads_CAS',
  satisfaction.aggregate_revision===2&&(await typedTC.snapshot(names.tc)).obligations.pending.length===0,'PORT_SUBSET');
 let staleClosure=false;
 try{await typedTC.closeTaskCycle({expectedRevision:1,taskcycleId:names.tc,
  authorityRef:authority[0].id,dispositionRef:'test://TS018/closed'})}
 catch(e){staleClosure=/REVISION_DRIFT/.test(String(e))}
 ok('Product_taskcycle_stale_closure_revision_rejected',staleClosure,'PORT_SUBSET');
 const close=await typedTC.closeTaskCycle({
  expectedRevision:2,taskcycleId:names.tc,authorityRef:authority[0].id,
  dispositionRef:'test://TS018/fixture-terminal-not-Product'});
 ok('native_guarded_batch_TC_close_after_reconciliation',
  close.aggregate_revision===3&&(await aggregate(ids.tc)).state==='CLOSED'&&bdShow(ids.tc).status==='closed','PORT_SUBSET');
 await stop();
 ok('native_CLI_post_server_close_observes_terminal_and_external_identity',
  meta(ids.tc).ts018_aggregate.state==='CLOSED'&&
  meta(ids.at).ts018_aggregate.result_refs[0].sha256===external.receipt.sha256,'RECOVERY');
 const history=bd(['history',ids.tc,'--limit','25']);
 ok('native_issue_history_present_after_restart',history.length>20,'RECOVERY');
 report.status='PASS_BOUNDED_LIFECYCLE_SHADOW_WITH_MATERIAL_GAPS';
 report.qualified=[
 'PINNED_PRODUCT_CONTRACT_AGGREGATE_VALIDATION','PRODUCT_PORT_METHOD_SHAPE_ONLY',
 'NATIVE_SINGLE_KEY_CAS','NATIVE_PER_ISSUE_ROW_VERSION_OPTIMISTIC_BATCH',
 'NATIVE_ATOMIC_MULTI_ISSUE_RECONCILIATION','SYNTHETIC_PROVIDER_EXACT_IDENTITY_REOBSERVE',
 'NATIVE_UNKNOWN_RECOVERY_AFTER_HTTP_RESTART','SYNTHETIC_CLOSURE_AFTER_SATISFACTION'];
 report.not_qualified=[
 'REAL_EXTERNAL_PROVIDER_RECEIPT_OR_ACK','PRODUCT_AUTHORITY_OR_INDEPENDENT_REVIEW',
 'DROP_IN_SYNC_PRODUCT_PORT_ADAPTER','GLOBAL_PRODUCT_STORE_REVISION_AND_EVENT_SEQUENCE',
 'ATOMIC_CAS_METADATA_SEMANTIC_EQUALS_BATCH_MULTIISSUE_CLOSE',
 'PRODUCTION_MULTI_RUNNER_REMOTE_SYNC','CONSUMPTION_OF_ALL_EXISTING_PRODUCT_TEST_VECTORS',
 'REAL_PRODUCT_TASKCYCLE_LIFECYCLE_EFFECT','MIGRATION_OR_MODULE_RETIREMENT'];
 observed.push({key:'native_server_restarts',count:nativeStartCount});
 observed.push({key:'native_row_version_refused_stale',stale_accepted:refused.ok,
  status:refused.code,token_examples:[staleAt,staleOp,racedOp]});
 console.log('TS_BEADS018_NATIVE=PASS;checks='+check.length+';unknown=BLOCKED_THEN_SYNTHETIC_RECONCILED;stale_batch=ROLLED_BACK;Product=NONE');
}catch(e){
 report.status='FAIL_REQUIRES_RECONCILIATION';report.error=String(e?.stack||e);
 console.error('TS_BEADS018_ERROR='+report.error);throw e;
}finally{
 try{await stop()}catch(e){report.shutdown_error=String(e)}
 report.native_http_logs={stdout:srvOut.slice(-450),stderr:srvErr.slice(-450)};
 writeFileSync(OUT,JSON.stringify(report,null,2)+'\n','utf8');
 console.log('TS_BEADS018_RECEIPT='+OUT+';status='+report.status);
}
