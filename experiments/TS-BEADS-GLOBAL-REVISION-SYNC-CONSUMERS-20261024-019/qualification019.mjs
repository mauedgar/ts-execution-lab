// TS-BEADS-019 — current Product consumer audit + native per-issue/global and synchronous-port negative controls.
// Nonproduct, isolated disposable store. No replacement adapter and no second mutable ledger.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readdirSync,readFileSync,statSync,writeFileSync} from 'node:fs';
import {join,relative} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const PRODUCT_SHA='7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56';
const PRODUCT_TREE='8caa56d36f3efeba359bbbf65b158ffb01a19da6';
const P=process.env.PRODUCT_ROOT,R=process.env.LAB_ROOT,BD=process.env.BD_BIN,OUT=process.env.RESULT_PATH;
if(!P||!R||!BD||!OUT)throw Error('EXACT_BINDINGS_REQUIRED');
if(existsSync(join(R,'.beads')))throw Error('NO_REPLAY_DISPOSABLE_ROOT_EXISTS');
mkdirSync(R,{recursive:true});
const env={...process.env,BEADS_DIR:join(R,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
BEADS_ACTOR:'TS-BEADS-019-TEST-NONPRODUCT',NO_COLOR:'1',GIT_TERMINAL_PROMPT:'0'};
const req=createRequire(join(P,'package.json'));
const {requireTaskCycleLifecycleCapability,requireExecutionLifecycleCapability}
 =req(join(P,'src/operational-spine-v0/taskcycle-lifecycle-capability.js'));
const {createReconcileAndCloseTaskCycleRecipe}=req(join(P,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js'));
const checked=[], negative=[], observations=[];
const report={id:'TS-BEADS-EXPERIMENT-019-CONTINUATION-20261024-001',status:'RUNNING',
 product_sha:PRODUCT_SHA,product_tree:PRODUCT_TREE,authority:'NONE_PRODUCT',product_effect:'NONE',
 shared_remote_effect:'NONE',native_binding:'isolated Beads 1.3.1 / Dolt 2.2.0 Windows',
 checked,negative,observations};
const ok=(key,test,cls='positive')=>{assert.ok(test,key);checked.push({key,result:'PASS',class:cls});};
const paths=[];
for(const dir of ['src','src-typescript','scripts','tests','.github/workflows']){
 const root=join(P,dir);
 if(!existsSync(root))continue;
 const walk=(d)=>{for(const e of readdirSync(d,{withFileTypes:true})){
  const f=join(d,e.name);if(e.isDirectory())walk(f);
  else if(/\.(js|ts|mjs|cjs|yml|yaml)$/.test(e.name)&&!e.name.endsWith('.d.ts'))paths.push(f);
 }};walk(root);
}
const keys=['store_revision','event_count','expected_state_revision','expectedRevision','observeInvocationBookkeeping',
 'hasUnreconciledExecution','snapshot(','satisfyObligation(','closeTaskCycle('];
const occurrences=[];
for(const file of paths){
 const r=relative(P,file).replaceAll('\\','/');
 const lines=readFileSync(file,'utf8').split(/\r?\n/);
 lines.forEach((line,i)=>{for(const symbol of keys){
  if(line.includes(symbol))occurrences.push({path:r,line:i+1,symbol,source:line.trim().slice(0,185),
  scope:r.startsWith('tests/')?'TEST_ORACLE':r.startsWith('src-typescript/')?'SOURCE_TS':
   r.startsWith('src/')?'RUNTIME_JS':'OTHER'});
 }});
}
report.consumer_scan={files_scanned:paths.length,occurrences:occurrences.length,
 counts:Object.fromEntries(keys.map(k=>[k,occurrences.filter(x=>x.symbol===k).length])),
 runtime_files:[...new Set(occurrences.filter(x=>x.scope==='RUNTIME_JS').map(x=>x.path))].sort(),
 relevant_occurrences:occurrences.filter(x=>/reconcile-and-close-taskcycle|state-kernel-adapter|state-kernel-v0\/store|taskcycle-lifecycle-capability|recipe-invocation/.test(x.path)),
 test_occurrences:occurrences.filter(x=>x.scope==='TEST_ORACLE'&&/reconcile-and-close-taskcycle|taskcycle-lifecycle-capability/.test(x.path)).slice(0,80)};
ok('source_contract_actual_compat_binding',report.consumer_scan.runtime_files.includes('src/operational-spine-v0/state-kernel-adapter.js'));
ok('source_actual_recipe_consumes_global_revision',occurrences.some(x=>x.path==='src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js'&&x.symbol==='event_count'));
ok('source_actual_recipe_uses_expected_global_revision',occurrences.some(x=>x.path==='src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js'&&x.symbol==='expected_state_revision'));
const recipeSrc=readFileSync(join(P,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js'),'utf8');
ok('source_recipe_sync_snapshot_without_await',recipeSrc.includes('lifecycleSnapshot = lifecycle.snapshot(request.context.taskcycle_id)')&&!recipeSrc.includes('await lifecycle.snapshot(request.context.taskcycle_id)'));
ok('source_recipe_sync_mutation_without_await',recipeSrc.includes('result = invoke();')&&!recipeSrc.includes('result = await invoke();'));
const contractsSrc=readFileSync(join(P,'src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts'),'utf8');
ok('source_types_sync_lifecycle',contractsSrc.includes('snapshot(taskcycleId: string): TaskCycleLifecycleSnapshot;')&&!contractsSrc.includes('snapshot(taskcycleId: string): Promise'));
const lifecycleShape={
 snapshot:async()=>({revision:111,event_count:111,taskcycle:{id:'TC019',state:'ACTIVE',revision:1,obligations:[]},
   obligations:{pending:[],obligations:[]},legal_next:['CLOSED']}),
 observeInvocationBookkeeping(){},hasUnreconciledExecution(){return false},
 satisfyObligation(){},closeTaskCycle(){}};
ok('structural_guard_accepts_async_shape_without_return_validation',requireTaskCycleLifecycleCapability(lifecycleShape)===lifecycleShape,'negative');
const input={expected_state_revision:111,observations:[],evidence:[],obligation_satisfactions:[],
 closure:{authority_ref:'SYNTHETIC-NOT-GRANT',disposition_ref:'test://019-no-product'}};
const req19={input,context:{taskcycle_id:'TC019'},operation_id:'OP019',execution_attempt_id:'AT019',
 recipe_id:'reconcile_and_close_taskcycle',recipe_version:'v0'};
const recipe=createReconcileAndCloseTaskCycleRecipe({lifecycle:lifecycleShape});
const response=await recipe.preflight(req19);
ok('actual_Product_recipe_blocks_async_snapshot_due_undefined_revision',response.status==='BLOCKED'&&String(response.reason).includes('LIFECYCLE_REVISION_DRIFT:undefined'),'negative');
negative.push({key:'ASYNC_DROP_IN',result:response,meaning:'method-name structural acceptance does not imply valid synchronous semantics'});
const minimalSync={...lifecycleShape,snapshot:()=>({revision:111,event_count:111,taskcycle:{id:'TC019',state:'ACTIVE',revision:1,obligations:[]},
  obligations:{pending:[],obligations:[]},legal_next:['CLOSED']})};
const recipeSync=createReconcileAndCloseTaskCycleRecipe({lifecycle:minimalSync});
let syncResult;try{syncResult=await recipeSync.preflight(req19);}catch(e){syncResult={threw:String(e)}}
ok('sync_fixture_crosses_revision_guard',!String(syncResult.reason||'').includes('LIFECYCLE_REVISION_DRIFT:undefined'),'negative');
observations.push({key:'sync_fixture_preflight_after_global_revision_gate',result:syncResult});

function bd(args){const p=spawnSync(BD,args,{cwd:R,env,encoding:'utf8',timeout:45000,maxBuffer:8*1024*1024});
 if(p.error||p.status!==0)throw Error('BD_NONZERO:'+args.slice(0,4).join('_')+':'+JSON.stringify({exit:p.status,err:p.stderr,out:p.stdout}).slice(0,900));
 return (p.stdout||'').trim();}
function bdJ(args){const x=bd([...args,'--json']),i=x.search(/[\[{]/);if(i<0)throw Error('BD_JSON_NOT_FOUND');return JSON.parse(x.slice(i));}
function bdShow(id){const v=bdJ(['show',id]),x=Array.isArray(v)?v[0]:v;assert.equal(x.id,id);return x;}
const tcid='ts019-root',opid='ts019-unrelated';
let server=null,serverLog='',originPort=null,base=null;
async function start(){
 const port=32100+(Number(process.env.GITHUB_RUN_ID||1900)%17000);originPort=port;base='http://127.0.0.1:'+port;
 server=spawn(BD,['serve','--addr','127.0.0.1:'+port],{cwd:R,env,stdio:['ignore','pipe','pipe'],windowsHide:true});
 server.stdout.on('data',v=>serverLog+=String(v));server.stderr.on('data',v=>serverLog+=String(v));
 for(let i=0;i<100;i++){if(server.exitCode!==null||server.signalCode!==null)throw Error('BEADS_SERVE_DIED:'+serverLog.slice(-500));
  try{const r=await fetch(base+'/healthz',{signal:AbortSignal.timeout(400)});if(r.ok)return;}catch{}await delay(190)}
 throw Error('HTTP_HEALTH_NOT_READY:'+serverLog.slice(-450));
}
async function end(){if(!server)return;if(server.exitCode===null&&server.signalCode===null){
 server.kill();await Promise.race([new Promise(done=>server.once('exit',done)),delay(7000)])}
 if(server.exitCode===null&&server.signalCode===null)throw Error('NATIVE_SHUTDOWN_NOT_CONFIRMED');server=null}
async function http(path,payload){const r=await fetch(base+path,{
 ...(payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),
 signal:AbortSignal.timeout(10000)});const t=await r.text();let v;try{v=JSON.parse(t)}catch{v=null}
 return {status:r.status,ok:r.ok,json:v,raw:t};
}
const patch=(id,tag,rev)=>({kind:'update',update:{target:{id},
 ...(rev?{expected_version:rev}:{}),patch:{metadata:{set:{ts019_marker:tag}}}}});
async function batch(items){return await http('/v0/beads/issues:batchApply',{actor:'TS019-LAB',provenance:'test://TS019/native-counterexample',items})}
async function touch(id,mark,rev){
 const r=await batch([patch(id,mark,rev)]);
 if(!r.ok)throw Error('NATIVE_BATCH_REFUSED:'+r.status+':'+r.raw.slice(0,600));
 const token=r.json?.items?.[0]?.revision;
 assert.ok(typeof token==='string'&&token,'MISSING_NATIVE_REVISION_TOKEN');
 return token;
}
try{
 bd(['init','--server','--quiet','--stealth']);
 for(const [id,title] of [[tcid,'TS019 only native taskcycle-like view'],[opid,'TS019 independent operation-like view']]){
  const created=bdJ(['create',title,'--type','task','--id',id,'--force','--description','NONPRODUCT_SYNTHETIC_REF_019']);
  const v=Array.isArray(created)?created[0]:created;ok('created_'+id,v.id===id&&bdShow(id).id===id);
 }
 await start();
 ok('native_api_ready',true);
 const rootBefore=await touch(tcid,'root_snapshot_r1'), otherBefore=await touch(opid,'op_before');
 const rootStill=rootBefore;
 const otherAfter=await touch(opid,'op_mutated_after_root_snapshot',otherBefore);
 ok('native_issue_revision_advances_on_unrelated_operation',otherAfter!==otherBefore);
 const rootMutationGuard=await batch([patch(tcid,'root_guarded_success_after_op_changed',rootStill)]);
 ok('native_root_expected_version_succeeds_despite_other_issue_change',rootMutationGuard.ok,'negative');
 const rootAfter=rootMutationGuard.json?.items?.[0]?.revision;
 ok('native_issue_revision_changes_on_self_mutation',rootAfter&&rootAfter!==rootBefore);
 const rootStale=await batch([patch(tcid,'stale_rejected',rootBefore)]);
 ok('native_stale_self_expected_version_refused',!rootStale.ok,'negative');
 const raw=bdShow(tcid).metadata;
 const nativeMeta=typeof raw==='string'?JSON.parse(raw):raw;
 ok('native_readback_did_not_apply_stale_mutation',nativeMeta.ts019_marker==='root_guarded_success_after_op_changed');
 negative.push({key:'CROSS_AGGREGATE_GLOBAL_REVISION',
  observed:'native root expected_version accepted after a different native issue was mutated',
  missing:'global monotonic revision / event_count across unrelated aggregates',
  native_root_before:rootBefore,native_operation_before:otherBefore,native_operation_after:otherAfter,
  native_root_after:rootAfter,
  finding:'PER_ISSUE_ROW_VERSION_NOT_GLOBAL; NO SECOND_MUTABLE_LEDGER_IMPLEMENTED'});
 await end();
 const fresh=bdShow(tcid);const mm=typeof fresh.metadata==='string'?JSON.parse(fresh.metadata):fresh.metadata;
 ok('independent_new_cli_process_readback',fresh.id===tcid&&mm.ts019_marker==='root_guarded_success_after_op_changed');
 report.native={root:tcid,unrelated:opid,global_cross_issue_guard:false,
  self_issue_CAS:true,third_process_readback:true,http_port:originPort};
 report.status='PASS_NEGATIVE_CONFORMANCE_GAP_CONFIRMED';
 report.research_disposition='INCOMPATIBLE_DROP_IN/RESEARCH_CANDIDATE_ONLY';
 report.no_second_mutable_ledger_created=true;
 console.log('TS_BEADS019=PASS;checks='+checked.length+';async_drop_in=INCOMPATIBLE;native_global_revision=NOT_EQUIVALENT;Product=NONE');
}catch(e){report.status='FAIL_TECHNICAL_NEEDS_RECONCILIATION';report.error=String(e.stack||e);console.error('TS_BEADS019_FAIL='+report.error);throw e
}finally{
 try{await end()}catch(e){report.shutdown_error=String(e)}
 writeFileSync(OUT,JSON.stringify(report,null,2)+'\n','utf8');
 console.log('TS_BEADS019_RECEIPT='+OUT+';status='+report.status);
}
