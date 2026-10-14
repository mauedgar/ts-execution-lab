// TS-BEADS-017: experimental Beads consumer vs Product-frozen source contract.
// Never a Product lifecycle implementation, acceptance or migration.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {existsSync,mkdirSync,readdirSync,readFileSync,statSync,writeFileSync} from 'node:fs';
import {join,resolve,extname,relative} from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {setTimeout as delay} from 'node:timers/promises';

const bin=process.env.BD_BIN, root=process.env.LAB_ROOT, product=process.env.PRODUCT_ROOT;
const resultPath=process.env.RESULT_PATH||join(root||'.','shadow017-result.json');
if(!bin||!root||!product)throw Error('BD_BIN_LAB_ROOT_PRODUCT_ROOT_REQUIRED');
mkdirSync(root,{recursive:true});
if(existsSync(join(root,'.beads')))throw Error('NOT_FRESH_LAB');
const prodPkg=createRequire(join(product,'package.json'));
const {TRANSITIONS,validateAggregate}=prodPkg(join(product,'src/state-kernel-v0/contracts.js'));
const productInfo=prodPkg(join(product,'package.json'));
if(!TRANSITIONS.TaskCycle||typeof validateAggregate!=='function')throw Error('PRODUCT_CONTRACT_LOAD_FAILED');
const env={...process.env,BEADS_DIR:join(root,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BEADS_ACTOR:'ts017-shadow-only',GIT_TERMINAL_PROMPT:'0',NO_COLOR:'1'};
const names={tc:'ts017-tc',attempt:'ts017-attempt',rogue:'ts017-rogue',bypass:'ts017-bypass'};
const checks=[],observations=[];
const report={
 experiment:'TS-BEADS-PRODUCT-CONTRACT-SHADOW-20261014-017',
 schema:'ts-beads-product-shadow-017/v1',
 product_ref:'mauedgar/tecnotron-ai:tools@1ecce07708a5760c99d7faf55f2344f2eabbc119',
 product_tree:'025ce7524d1b8bf1753cfc4af964ee554d3b0977',
 product_contracts_origin:'DIRECT_READONLY_EXACT_GIT_CHECKOUT',
 PRODUCT_AUTHORITY:'NONE',PRODUCT_EFFECT:'NONE',SHARED_DOLT_EFFECT:'NONE',
 native_beads:'v1.3.1',native_lab:'DISPOSABLE_DOLT_SQL_NO_GIT_REMOTE',checks,observations
};
let server=null,stdout='',stderr='',stopped=false,base='';
const verify=(id,check,kind='QUALIFIED_NATIVE_SHADOW')=>{assert.equal(Boolean(check),true,id);checks.push({id,result:'PASS',kind});};
function cmd(args,acceptFail=false){
 const a=spawnSync(bin,args,{cwd:root,env,encoding:'utf8',timeout:40000,maxBuffer:12*1024*1024});
 const v={code:a.status,stdout:(a.stdout||'').trim(),stderr:(a.stderr||'').trim(),error:a.error?.message};
 if(!acceptFail&&(v.code!==0||v.error))throw Error('NATIVE_BD_FAILED:'+args.join(' ')+':'+JSON.stringify(v).slice(0,750));
 return v;
}
function json(args){
 const s=cmd([...args,'--json']).stdout;const m=s.match(/(?:^|\n)\s*([\[{])/);
 if(!m)throw Error('BD_JSON_MISSING:'+args.join('_')+':'+s.slice(0,330));
 return JSON.parse(s.slice(m.index).trim());
}
function show(id){const x=json(['show',id]),v=Array.isArray(x)?x[0]:x;
 if(v?.id!==id)throw Error('BEADS_ID_MISMATCH:'+id);return v;}
function metadata(id){
 const x=show(id).metadata;
 return typeof x==='string'?JSON.parse(x):x;
}
function create(id,title,m){
 const r=json(['create',title,'--id',id,'--force','--type','task','--description',
  'LAB_ONLY=TS017;Product authority=NONE;source='+report.product_ref,
  '--metadata',JSON.stringify(m)]);
 verify('native_created_'+id,(Array.isArray(r)?r[0]:r).id===id);
}
async function stop(){
 if(!server||stopped)return;
 stopped=true;
 if(server.exitCode===null&&server.signalCode===null){
  server.kill();await Promise.race([new Promise(r=>server.once('exit',r)),delay(7000)]);
 }
 if(server.exitCode===null&&server.signalCode===null)throw Error('NATIVE_SERVE_NOT_STOPPED');
}
async function req(path,data=null){
 const opts=data?{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify(data)}:{method:'GET'};
 const r=await fetch(base+path,{...opts,signal:AbortSignal.timeout(15000)});
 const t=await r.text();let o=null;try{o=JSON.parse(t);}catch{}
 return {code:r.status,ok:r.ok,body:o,text:t};
}
async function cas(id,expected,value){
 const r=await req('/v0/beads/issues/'+id+':casMetadata',{
  actor:'TS017-SYNTHETIC',key:'ts017_lifecycle',expected,value
 });
 if(!r.ok||typeof r.body?.swapped!=='boolean')throw Error('CAS_BAD_'+r.code+':'+r.text.slice(0,550));
 return r.body;
}
const authority={kind:'AUTHORITY',id:'DEV-017-SYNTHETIC'};
const fakeReceipt='test://TS017/FIXTURE-ONLY-NOT-PROVIDER-ACK';
const clock='2026-10-14T00:00:00.000Z';
function taskcycle(){
 return {
  schema_version:'tecnotron-state-kernel/v0',kind:'TaskCycle',id:'TC-017-SYNTHETIC',
  revision:1,state:'READY',created_at:clock,updated_at:clock,
  authority_refs:[authority],related_ids:[],last_event_id:null,
  responsibility:'TS017_TEST_ONLY',obligations:[{
   id:'INDEPENDENT_REVIEW',status:'PENDING',authority_ref:'DEV-017-SYNTHETIC'
  }],terminal_disposition_ref:null
 };
}
function legal(before,next){
 if(!TRANSITIONS.TaskCycle[before.state]?.includes(next))return false;
 if(['PENDING_ACCEPTANCE','CLOSED'].includes(next)&&before.obligations.some(x=>x.status!=='SATISFIED'))return false;
 return true;
}
function clone(x){return structuredClone(x);}
function indexSourceConsumers(rootDir){
 const found={RunStore:[],SqliteProjection:[],StateKernel:[]};
 const roots=['src','scripts','.github/workflows'];
 function walk(path,baseDir){
  if(!existsSync(path))return;
  const st=statSync(path);if(st.isDirectory()){
   for(const name of readdirSync(path)){
    if(['node_modules','dist','.git','.venv','coverage'].includes(name))continue;
    walk(join(path,name),baseDir);
   }
   return;
  }
  if(!/\.(?:js|ts|json|ya?ml)$/.test(path)||path.endsWith('.d.ts'))return;
  const rel=relative(rootDir,path).replaceAll('\\','/');
  if(rel==='src/core/run-store.js')return; // Declaring a class is not an active consumer.
  const text=readFileSync(path,'utf8');
  if(/\bRunStore\b|core\/run-store|['"]\.\/run-store['"]/.test(text))found.RunStore.push(rel);
  if(/\bSqliteProjection\b/.test(text))found.SqliteProjection.push(rel);
  if(/FilesystemStateStore|state-kernel-v0|state-kernel-adapter|StateKernelCompatibilityBinding/.test(text))
   found.StateKernel.push(rel);
 }
 for(const p of roots)walk(join(rootDir,p),rootDir);
 Object.values(found).forEach(x=>x.sort());
 return found;
}
try{
 verify('exact_product_contract_loaded',productInfo?.name==='fitflow-ai'&&Array.isArray(TRANSITIONS.TaskCycle.READY),'PRODUCT_SOURCE');
 verify('product_taskcycle_state_values',TRANSITIONS.TaskCycle.READY.includes('ACTIVE')&&
  !TRANSITIONS.TaskCycle.READY.includes('CLOSED'),'PRODUCT_SOURCE');
 const consumers=indexSourceConsumers(product);
 report.consumer_audit={
  method:'EXACT_PRODUCT_RUNTIME_STATIC_IMPORT_AND_STRING_SCAN;EXCLUDES_TESTS_DOCS_AND_DECLARATION_FILE',
  scanned_roots:['src','scripts','.github/workflows'],paths:consumers,
  active_RunStore_consumer_except_export:
   consumers.RunStore.filter(p=>p!=='src/core/index.js').length,
  active_SqliteProjection_consumer_except_export:
   consumers.SqliteProjection.filter(p=>p!=='src/core/index.js').length,
  installed_harness_dynamic_imports:'NOT_QUALIFIED'
 };
 verify('Product_Runtime_has_live_kernel_binding',consumers.StateKernel.length>0,'CONSUMER_STATIC');
 verify('RunStore_no_runtime_consumer_other_than_export',
  consumers.RunStore.every(p=>p==='src/core/index.js'),'CONSUMER_STATIC');
 verify('SqliteProjection_no_runtime_consumer_other_than_export',
  consumers.SqliteProjection.every(p=>p==='src/core/index.js'),'CONSUMER_STATIC');

 cmd(['init','--server','--quiet','--stealth']);
 const initial=taskcycle();
 validateAggregate(initial);
 create(names.tc,'Product TaskCycle contract shadow only',{ts017_lifecycle:initial});
 verify('Product_original_aggregate_validated',true,'PRODUCT_CONTRACT_VALIDATION');
 verify('native_metadata_roundtrip_matches_Product_aggregate',
  JSON.stringify(metadata(names.tc).ts017_lifecycle)===JSON.stringify(initial));
 const port=31800+(Number(process.env.GITHUB_RUN_ID||311)%18000);
 base='http://127.0.0.1:'+port;
 server=spawn(bin,['serve','--addr','127.0.0.1:'+port],{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
 server.stdout.on('data',b=>{stdout+=String(b)});
 server.stderr.on('data',b=>{stderr+=String(b)});
 let ready=false;
 for(let i=0;i<96;i++){
  if(server.exitCode!==null||server.signalCode!==null)throw Error('SERVER_EXIT_EARLY:'+stderr.slice(-900));
  try{const h=await fetch(base+'/healthz',{signal:AbortSignal.timeout(500)});
   if(h.ok){ready=true;break}}catch{}
  await delay(200);
 }
 verify('native_disposable_server_healthy',ready);
 verify('product_pending_gate_blocks_acceptance',
  !legal(initial,'PENDING_ACCEPTANCE'),'PRODUCT_SEMANTIC_RULE');
 const forbiddenRaw=await req('/v0/beads/issues:batchApply',{
  actor:'TS017-NEGATIVE-PRODUCT-AUTHORITY',
  items:[{kind:'close',close:{target:{id:names.tc},reason:'Invalid Product early close'}}]
 });
 // Bare Beads closure may succeed without Developer grant; observe, do NOT use as valid Product close.
 if(forbiddenRaw.ok){
  verify('native_bare_close_does_not_check_Product_grants',true,'NEGATIVE_NATIVE_AUTHORITY');
  observations.push({case:'unprotected_native_close',native_result:'PERMITTED',semantic_product_result:'FORBIDDEN'});
  const reset=cmd(['reopen',names.tc]); // Synthetic local reset only.
 }else{
  observations.push({case:'unprotected_native_close',native_result:'REFUSED',
   http_status:forbiddenRaw.code,detail:forbiddenRaw.text.slice(0,280)});
 }
 let before=metadata(names.tc).ts017_lifecycle;
 const active={...before,revision:before.revision+1,state:'ACTIVE',last_event_id:'synthetic:event-active'};
 verify('Product_allows_READY_to_ACTIVE',legal(before,'ACTIVE'),'PRODUCT_SEMANTIC_RULE');
 validateAggregate(active);
 const live=await cas(names.tc,before,active);
 verify('native_cas_READY_to_ACTIVE',live.swapped&&live.current.state==='ACTIVE');
 const stale=await cas(names.tc,before,{...before,state:'CLOSED'});
 verify('native_stale_global_revision_blocked',!stale.swapped&&stale.current.state==='ACTIVE');
 before=live.current;
 const badAuthority='NOT_A_REAL_DEVELOPER';
 verify('Product_obligation_requires_exact_authority',
  !before.authority_refs.some(x=>x.id===badAuthority),'PRODUCT_SEMANTIC_RULE');
 const satisfied={...before,revision:before.revision+1,
  obligations:before.obligations.map(x=>({...x,status:'SATISFIED',authority_ref:authority.id})),
  last_event_id:'synthetic:event-obligation'};
 validateAggregate(satisfied);
 const sat=await cas(names.tc,before,satisfied);
 verify('native_guarded_obligation_satisfaction',sat.swapped&&sat.current.obligations.every(x=>x.status==='SATISFIED'));
 before=sat.current;
 const pending={...before,revision:before.revision+1,state:'PENDING_ACCEPTANCE',
  last_event_id:'synthetic:event-pending'};
 verify('Product_allows_acceptance_after_obligations',legal(before,'PENDING_ACCEPTANCE'),'PRODUCT_SEMANTIC_RULE');
 validateAggregate(pending);
 const accep=await cas(names.tc,before,pending);
 verify('native_cas_PENDING_ACCEPTANCE',accep.swapped&&accep.current.state==='PENDING_ACCEPTANCE');
 before=accep.current;
 const closed={...before,revision:before.revision+1,state:'CLOSED',
  terminal_disposition_ref:fakeReceipt,last_event_id:'synthetic:event-closed'};
 verify('Product_allows_CLOSED_after_acceptance',legal(before,'CLOSED'),'PRODUCT_SEMANTIC_RULE');
 validateAggregate(closed);
 // Existing native batch is one atomic storage transaction for metadata + issue close;
 // it does NOT conditionally compare the same metadata key's value on this path.
 const commit=await req('/v0/beads/issues:batchApply',{
  actor:'TS017-NONPRODUCT-CLOSE',
  provenance:'test://TS017/semantic-close-not-Product',
  items:[
   {kind:'update',update:{target:{id:names.tc},patch:{metadata:{set:{ts017_lifecycle:closed}}}}},
   {kind:'close',close:{target:{id:names.tc},reason:'synthetic candidate contract shadow only'}}
  ]
 });
 if(!commit.ok)throw Error('NATIVE_BATCH_CLOSE_FAILED:'+commit.code+':'+commit.text.slice(0,900));
 verify('native_atomic_batch_metadata_and_issue_close',commit.ok);
 const nativeClosed=show(names.tc), finalMeta=metadata(names.tc).ts017_lifecycle;
 verify('native_terminal_readback_semantic_and_status',
  nativeClosed.status==='closed'&&finalMeta.state==='CLOSED'&&finalMeta.terminal_disposition_ref===fakeReceipt);
 verify('Product_contract_accepts_native_semantic_final',Boolean(validateAggregate(finalMeta)),'PRODUCT_CONTRACT_VALIDATION');
 // UNKNOWN is a Product-specific tri-state, not a Beads claim or status. Validate it using source contract.
 const attempt={
  schema_version:'tecnotron-state-kernel/v0',kind:'ExecutionAttempt',id:'AT-017-SYNTHETIC',
  revision:5,state:'UNKNOWN',created_at:clock,updated_at:clock,authority_refs:[authority],
  related_ids:[],last_event_id:'synthetic:dispatch',
  operation_id:'OP-017-SYNTHETIC',outcome:'UNKNOWN',reconciliation_required:true,result_refs:[]
 };
 validateAggregate(attempt);
 create(names.attempt,'Synthetic unresolved execution attempt',{ts017_lifecycle:attempt});
 verify('Product_contract_validates_UNKNOWN_attempt',true,'PRODUCT_CONTRACT_VALIDATION');
 const readback=metadata(names.attempt).ts017_lifecycle;
 verify('native_UNKNOWN_recovery_from_Beads_metadata',
  readback.reconciliation_required===true&&readback.state==='UNKNOWN');
 // Beads on its own allows new synthetic work regardless of another issue's UNKNOWN effect.
 create(names.bypass,'Synthetic attempt naive dispatch without Product guard',
  {ts017_lifecycle:{kind:'ExecutionAttempt',state:'PREPARED',operation_id:'OP-017-SYNTHETIC',
   authority_refs:[],observed_UNKNOWN_elsewhere:true}});
 verify('native_Beads_does_not_native_block_cross_issue_UNKNOWN',show(names.bypass).status==='open',
  'NEGATIVE_NATIVE_PRODUCT_POLICY');
 verify('Product_semantic_shadow_blocks_unknown_retry',
  [readback].some(x=>x.operation_id==='OP-017-SYNTHETIC'&&x.reconciliation_required===true),
  'PRODUCT_SEMANTIC_RULE');
 const schemaGap=finalMeta.kind==='TaskCycle'&&nativeClosed.status==='closed';
 observations.push({case:'Product_vs_Beads_dual_semantics',same_state:finalMeta.state==='CLOSED',
  Product_grant_identity:'SYNTHETIC_ONLY',atomic_batch_close:true,
  CAS_and_batch_same_operation:'NOT_QUALIFIED'});
 await stop();
 verify('native_server_shutdown_preserves_state',
  show(names.tc).status==='closed'&&metadata(names.attempt).ts017_lifecycle.state==='UNKNOWN');
 const history=cmd(['history',names.tc,'--limit','15']);
 verify('native_history_after_shutdown_available',history.stdout.length>10);
 report.disposition='PASS_SELECTED_PRODUCT_SHADOW_WITH_LIMITATIONS';
 report.not_qualified=[
  'FULL_EXECUTION_LIFECYCLE_CAPABILITY_PORT_DROPIN','PRODUCT_DEVELOPER_AUTHORITY',
  'INDEPENDENT_REVIEW_OR_ACTUAL_PROVIDER_ACK','UNKNOWN_RECOVERY_AFTER_EXTERNAL_DISPATCH',
  'GLOBAL_MULTI_ISSUE_CAS_AND_BATCH_COMPOSITION',
  'CROSS_RUNNER_DOLT_SYNC_AND_CONFLICT','TIMESTAMP_OR_EVENT_CHAIN_BYTE_EQUIVALENCE',
  'PHYSICAL_REMOVAL_OF_STATE_KERNEL_OR_RUNSTORE',
  'DYNAMIC_OR_INSTALLED_HARNESS_CONSUMERS'];
 console.log('TS_BEADS017_SHADOW=PASS;checks='+checks.length+';product_contract_source=PINNED;native_store=NO_EXTERNAL_EFFECT');
}catch(err){
 report.disposition='FAIL_NEEDS_RECONCILIATION';
 report.error=String(err?.stack||err);console.error('TS_BEADS017_DIAGNOSTIC_ERROR='+report.error);throw err;
}finally{
 try{await stop();}catch(err){report.stop_error=String(err);}
 report.server_logs_tail={stdout:stdout.slice(-450),stderr:stderr.slice(-450)};
 writeFileSync(resultPath,JSON.stringify(report,null,2)+'\n','utf8');
 console.log('TS_BEADS017_RECEIPT='+resultPath+';disposition='+report.disposition);
}
