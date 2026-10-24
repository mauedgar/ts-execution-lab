// TS-BEADS-024: experimental Control-selected graph reader.
// It is an informational Beads consumer; no Product grant, TaskCycle, or decision effect.
// A stable double-scan is not a transactional snapshot, so it NEVER authorizes effects.
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const BIN=process.env.BD_BIN,DIR=process.env.LAB_ROOT,OUT=process.env.RESULT_PATH;
if(!BIN||!DIR||!OUT||existsSync(join(DIR,'.beads')))throw Error('BOUNDED_NEW_NONPRODUCT_STORE_REQUIRED');
mkdirSync(DIR,{recursive:true});
const env={...process.env,BEADS_DIR:join(DIR,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',GIT_TERMINAL_PROMPT:'0',
BEADS_ACTOR:'TS-BEADS-024-EXPERIMENT'};
const ids={root:'ts024-root',gate:'ts024-gate',ancestor:'ts024-ancestor',
late:'ts024-late',unrelated:'ts024-unrelated'};
const report={experiment_id:'TS-BEADS-024-GRAPH-READ-MODEL-20261024-001',status:'RUNNING',
Product_effect:'NONE',Product_authority:'NONE',issue_24_selection:'EXPERIMENTAL_CONTROL_ONLY',
native_remote_effect:'NONE',checks:[],samples:[],native_counts:{GET:0,read_model_rounds:0},
scope:'REAL_NATIVE_BEADS_GET_GRAPH_PROJECTION_ONLY'};
const ok=(name,test)=>{assert.ok(test,name);report.checks.push({name,result:'PASS'})};
function bd(args){const x=spawnSync(BIN,args,{cwd:DIR,env,encoding:'utf8',timeout:60000,maxBuffer:8*1024*1024});
if(x.error||x.status!==0)throw Error('BD_'+args.slice(0,3).join('_')+JSON.stringify({code:x.status,error:x.error?.message,stderr:x.stderr,stdout:x.stdout}).slice(0,800));
return(x.stdout||'').trim();}
function bdJson(args){let s=bd([...args,'--json']);let i=s.search(/[\[{]/);if(i<0)throw Error('NATIVE_JSON_NOT_FOUND');return JSON.parse(s.slice(i))}
let proc=null,base='',logs='';
async function stop(){if(!proc)return;if(proc.exitCode===null&&proc.signalCode===null){
proc.kill();await Promise.race([new Promise(resolve=>proc.once('exit',resolve)),delay(7000)])}
if(proc.exitCode===null&&proc.signalCode===null)throw Error('BEADS_HTTP_STOP_UNKNOWN');proc=null}
async function start(){const port=31000+(Number(process.env.GITHUB_RUN_ID||24)%18000);base='http://127.0.0.1:'+port;
proc=spawn(BIN,['serve','--addr','127.0.0.1:'+port],{cwd:DIR,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
proc.stderr.on('data',b=>logs+=String(b));proc.stdout.on('data',b=>logs+=String(b));
for(let i=0;i<100;i++){if(proc.exitCode!==null||proc.signalCode!==null)throw Error('NATIVE_SERVICE_EXIT:'+logs.slice(-400));
try{if((await fetch(base+'/healthz',{signal:AbortSignal.timeout(400)})).ok)return}catch{}
await delay(180)}throw Error('NATIVE_SERVICE_NOT_READY:'+logs.slice(-400))}
function locate(v,id,d=0){if(!v||typeof v!=='object'||d>7)return null;
if(v.id===id&&typeof v.status==='string')return v;
for(const obj of Object.values(v)){let found=locate(obj,id,d+1);if(found)return found}
return null}
async function get(id){report.native_counts.GET++;
const r=await fetch(base+'/v0/beads/issues/'+encodeURIComponent(id)+'?brief_deps=true',
{signal:AbortSignal.timeout(12000)});const raw=await r.text();
if(!r.ok)throw Error('ISSUE_READ_REFUSED:'+id+':'+r.status+':'+raw.slice(0,240));
const x=locate(JSON.parse(raw),id);if(!x||typeof x.revision!=='string')throw Error('NATIVE_ISSUE_SHAPE_MISMATCH:'+id);
return x}
function depIDs(x){return (x.dependencies||[]).map(y=>y.id).sort()}
async function scanGraph(startId){
const queue=[startId],nodes=new Map();
while(queue.length){
const id=queue.shift();if(nodes.has(id))continue;
const issue=await get(id),deps=depIDs(issue);
nodes.set(id,{id,revision:issue.revision,status:issue.status,dependencies:deps});
for(const d of deps)if(!nodes.has(d))queue.push(d)
}
return [...nodes.values()].sort((a,b)=>a.id.localeCompare(b.id));
}
async function readModel({interleave}={}){
report.native_counts.read_model_rounds++;
let first;
try{first=await scanGraph(ids.root)}
catch(e){return{classification:'INCOMPLETE_READ',reason:String(e.message),authority:'NONE_PRODUCT',mayAuthorize:false}}
if(interleave)await interleave();
let second;
try{second=await scanGraph(ids.root)}
catch(e){return{classification:'INCOMPLETE_READ',reason:String(e.message),authority:'NONE_PRODUCT',mayAuthorize:false}}
const equal=JSON.stringify(first)===JSON.stringify(second);
return {classification:equal?'NONAUTHORITATIVE_OBSERVATION':'INCONSISTENT_GRAPH',
authority:'NONE_PRODUCT',mayAuthorize:false,nodes:equal?second:[],
observation:{first_nodes:first.length,second_nodes:second.length,root_revision_equal:
first.find(x=>x.id===ids.root)?.revision===second.find(x=>x.id===ids.root)?.revision},
reason:equal?'Two equal sequential scans, non-atomic; informational only':'Concurrent dependency/status/revision divergence'};
}
async function batch(items,tag){
const q=await fetch(base+'/v0/beads/issues:batchApply',{method:'POST',
headers:{'content-type':'application/json'},
body:JSON.stringify({actor:'TS-BEADS-024-NONPRODUCT',provenance:'test://TS024/'+tag,items}),
signal:AbortSignal.timeout(15000)});
let s=await q.text();return{ok:q.ok,status:q.status,raw:s.slice(0,400)};
}
const patch=(id,rev,mark)=>({kind:'update',update:{
target:{id},expected_version:rev,patch:{metadata:{set:{ts024_marker:mark}}}}});
try{
bd(['init','--server','--quiet','--stealth']);
ok('fresh_disposable_git_has_no_remote',bd(['--version']).length>0&&spawnSync('git',['remote'],{cwd:DIR,env,encoding:'utf8'}).stdout.trim()==='');
for(const id of Object.values(ids)){const x=bdJson(['create','TS024 '+id,'--type','task','--id',id,'--force',
'--description','NONPRODUCT_READMODEL_TEST','--metadata',JSON.stringify({ts024_marker:'BASE'})]);
ok('created_'+id,(Array.isArray(x)?x[0]:x).id===id)}
bd(['dep','add',ids.root,ids.gate,'--type','related']);
bd(['dep','add',ids.gate,ids.ancestor,'--type','related']);
await start();ok('native_http_ready',true);
const baseline=await readModel();
ok('initial_stable_observation_only',baseline.classification==='NONAUTHORITATIVE_OBSERVATION'&&!baseline.mayAuthorize);
ok('initial_transitive_dependency_closure',[ids.root,ids.gate,ids.ancestor].every(x=>baseline.nodes.some(n=>n.id===x))
&&!baseline.nodes.some(n=>n.id===ids.unrelated));
report.samples.push({case:'initial',data:baseline});
const first=await get(ids.root);
const expansion=await readModel({interleave:async()=>bd(['dep','add',ids.root,ids.late,'--type','related'])});
const afterExpansion=await get(ids.root);
ok('uncontrolled_native_edge_expansion_did_not_advance_root_token',first.revision===afterExpansion.revision);
ok('reader_detected_concurrent_native_edge_expansion_without_authorization',
 expansion.classification==='INCONSISTENT_GRAPH'&&!expansion.mayAuthorize&&expansion.nodes.length===0);
report.samples.push({case:'native_edge_expansion',data:expansion});
const stableNew=await readModel();
ok('fresh_reobservation_includes_late_dependency',stableNew.classification==='NONAUTHORITATIVE_OBSERVATION'
&&stableNew.nodes.some(x=>x.id===ids.late)&&!stableNew.mayAuthorize);
const race=await readModel({interleave:async()=>{
const old=await get(ids.ancestor);
const response=await batch([patch(ids.ancestor,old.revision,'CONCURRENT_NATIVE_UPDATE')],'related-writer');
ok('synthetic_related_writer_committed',response.ok);
}});
ok('reader_detected_version_change_in_ancestor',race.classification==='INCONSISTENT_GRAPH'&&!race.mayAuthorize);
report.samples.push({case:'related_version_change',data:race});
const withoutGlobal=await readModel({interleave:async()=>{
const old=await get(ids.unrelated);
const response=await batch([patch(ids.unrelated,old.revision,'UNRELATED_CHURN')],'unrelated-writer');
ok('synthetic_unrelated_writer_committed',response.ok);
}});
ok('reader_does_not_fail_on_unrelated_issue',withoutGlobal.classification==='NONAUTHORITATIVE_OBSERVATION'&&!withoutGlobal.mayAuthorize);
report.samples.push({case:'unrelated_change',data:withoutGlobal});
const nativeFrontier=bdJson(['ready']);
ok('native_ready_frontier_fetched',Array.isArray(nativeFrontier));
report.native_readiness={kind:'NATIVE_READY_INFORMATIONAL_ONLY',count:nativeFrontier.length,
not_Tecnotron_TaskCycle_authorization:true};
await stop();
const root=bdJson(['show',ids.root]);ok('independent_native_CLI_readback_correct_id',(Array.isArray(root)?root[0]:root).id===ids.root);
report.known_limitations=[
'Equality of two scans is not a transactional read and does not prevent post-check graph changes',
'Native Beads ready status is informational, not Developer grant/Independent Review/TaskCycle admission',
'No enforcement of exclusive edge writers: original bypass remains material blocker for authoritative graph effects',
'Fixture has known initial root, does not qualify dynamic discovery from arbitrary GitHub Product consumers',
'No Product migrations, source native Product files unchanged'
];
report.status='PASS_NONAUTHORITATIVE_READ_MODEL_WITH_RACE_DETECTION';
console.log('TS_BEADS024=PASS;checks='+report.checks.length+';race=DETECTED;Product=NONE');
}catch(e){report.status='FAIL_EXACT_024_ATTEMPT_RECONCILE';report.error=String(e?.stack||e);console.error('TS_BEADS024_ERROR='+report.error);throw e
}finally{
try{await stop()}catch(e){report.stop_error=String(e)}
writeFileSync(OUT,JSON.stringify(report,null,2)+'\n','utf8');
console.log('TS_BEADS024_ORIGINAL_RECEIPT='+OUT+';status='+report.status);
}