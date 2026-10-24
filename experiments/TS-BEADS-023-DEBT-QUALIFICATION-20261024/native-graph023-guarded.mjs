import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
const BD=process.env.BD_BIN,LAB=process.env.LAB_ROOT,OUT=process.env.RESULT_PATH;
if(!BD||!LAB||!OUT||existsSync(join(LAB,'.beads')))throw Error('EXACT_NEW_DISPOSABLE_STORE_REQUIRED');
mkdirSync(LAB,{recursive:true});
const env={...process.env,BEADS_DIR:join(LAB,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',BEADS_ACTOR:'BEADS-023-ONLY',GIT_TERMINAL_PROMPT:'0'};
const ids={root:'ts023-root',gate:'ts023-gate',ancestor:'ts023-ancestor',unrelated:'ts023-unrelated',late:'ts023-late'};
const r={status:'RUNNING',checks:[],facts:[],calls:{get:0,batch:0},product_effect:'NONE',graph_authority:'NATIVE_BEADS_ONLY_NONPRODUCT'};
const ok=(name,condition)=>{assert.ok(condition,name);r.checks.push(name)};
function cmd(args){const p=spawnSync(BD,args,{cwd:LAB,env,encoding:'utf8',timeout:45000,maxBuffer:8e6});if(p.status!==0||p.error)throw Error('CLI:'+args.join(' ')+':'+(p.stderr||p.error?.message));return(p.stdout||'').trim()}
function cmdJ(args){const s=cmd([...args,'--json']);const i=s.search(/[\[{]/);return JSON.parse(s.slice(i))}
let server=null,base='',logs='';
async function stop(){if(server&&server.exitCode===null&&server.signalCode===null){server.kill();await Promise.race([new Promise(done=>server.once('exit',done)),delay(7000)])}if(server&&server.exitCode===null&&server.signalCode===null)throw Error('SERVER_UNCONFIRMED');server=null}
async function start(){const port=32000+(Number(process.env.GITHUB_RUN_ID||23)%16000);base='http://127.0.0.1:'+port;server=spawn(BD,['serve','--addr','127.0.0.1:'+port],{cwd:LAB,env,windowsHide:true,stdio:['ignore','pipe','pipe']});server.stderr.on('data',v=>logs+=String(v));for(let i=0;i<100;i++){if(server.exitCode!==null)throw Error('SERVER_DIED:'+logs.slice(-300));try{if((await fetch(base+'/healthz',{signal:AbortSignal.timeout(500)})).ok)return}catch{}await delay(190)}throw Error('SERVER_UNHEALTHY:'+logs.slice(-500))}
async function api(path,body){const isGet=body===undefined;r.calls[isGet?'get':'batch']++;const resp=await fetch(base+path,{...(isGet?{}:{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}),signal:AbortSignal.timeout(12000)});const raw=await resp.text();let data;try{data=JSON.parse(raw)}catch{}return{ok:resp.ok,status:resp.status,data,raw:raw.slice(0,600)}}
function locate(o,id,depth=0){if(!o||typeof o!=='object'||depth>7)return null;if(o.id===id&&typeof o.status==='string')return o;for(const v of Object.values(o)){const z=locate(v,id,depth+1);if(z)return z}return null}
async function issue(id){const q=await api('/v0/beads/issues/'+id+'?brief_deps=true');if(!q.ok)throw Error('GET_'+id+'_'+q.raw);const z=locate(q.data,id);if(!z)throw Error('MISSING_DETAIL_'+id);return z}
const patch=(id,token,tag)=>({kind:'update',update:{target:{id},expected_version:token,patch:{metadata:{set:{ts023_marker:tag}}}}});
async function batch(items,tag){return api('/v0/beads/issues:batchApply',{actor:'TS-BEADS-023',provenance:'test://TS023/'+tag,items})}
const depIds=x=>(x.dependencies||[]).map(d=>d.id).sort();
async function discover(startId){const queue=[startId],seen=new Map();while(queue.length){const id=queue.shift();if(seen.has(id))continue;const row=await issue(id);const refs=depIds(row);seen.set(id,{revision:row.revision,deps:refs,metadata:row.metadata});for(const target of refs)if(!seen.has(target))queue.push(target)}return seen}
try{
 cmd(['init','--server','--quiet','--stealth']);ok('git_store_no_remote',!cmd(['--version']).includes('UNKNOWN'));
 for(const id of Object.values(ids)){const a=cmdJ(['create','TS023 '+id,'--type','task','--id',id,'--force','--description','NONPRODUCT','--metadata',JSON.stringify({ts023_marker:'BASE'})]);ok('create_'+id,(Array.isArray(a)?a[0]:a).id===id)}
 cmd(['dep','add',ids.root,ids.gate,'--type','related']);
 cmd(['dep','add',ids.gate,ids.ancestor,'--type','related']);
 await start();ok('native_http_ready',true);
 const a=await discover(ids.root);
 r.facts.push({phase:'INITIAL_DISCOVERY',nodes:[...a].map(([id,x])=>({id,revision:x.revision,dependencies:x.deps}))});
 ok('native_graph_discovery_reaches_transitive_ancestor',[ids.root,ids.gate,ids.ancestor].every(x=>a.has(x))&&!a.has(ids.unrelated));
 const anc=await issue(ids.ancestor);
 const chg=await batch([patch(ids.ancestor,anc.revision,'RELATED_MUTATED')],'related-concurrent');
 ok('concurrent_ancestor_changed',chg.ok);
 const stale=await batch([...a].map(([id,x])=>patch(id,x.revision,'NOT_APPLIED_RELATED_STALE')),'readset-stale');
 ok('atomic_native_batch_refuses_any_stale_transitive_relation',!stale.ok);
 const root=await issue(ids.root),meta=typeof root.metadata==='string'?JSON.parse(root.metadata):(root.metadata||{});
 ok('rejected_multiissue_batch_did_not_write_root',meta.ts023_marker!=='NOT_APPLIED_RELATED_STALE');
 const b=await discover(ids.root);const ux=await issue(ids.unrelated);
 ok('unrelated_native_mutation',(await batch([patch(ids.unrelated,ux.revision,'UNRELATED_CHANGED')],'unrelated-change')).ok);
 const success=await batch([...b].map(([id,x])=>patch(id,x.revision,'RELATED_SET_CHECKED')),'relevant-cas-no-global');
 ok('full_scoped_batch_ignores_unrelated_issue',success.ok);
 // Critical safety test: graph can EXPAND after discovery. Check whether native edge changes root row version.
 const pre=await discover(ids.root);
 cmd(['dep','add',ids.root,ids.late,'--type','related']);
 const post=await discover(ids.root);
 const graphDetected=[...post.keys()].includes(ids.late)&&![...pre.keys()].includes(ids.late);
 ok('native_dependency_discovery_observes_new_edge',graphDetected);
 const rootBefore=pre.get(ids.root).revision,rootAfter=post.get(ids.root).revision;
 r.facts.push({phase:'DYNAMIC_GRAPH_EXPANSION',new_dependency:ids.late,root_revision_before:rootBefore,root_revision_after:rootAfter,root_revision_advances:rootBefore!==rootAfter});
 const frozen=await batch([...pre].map(([id,x])=>patch(id,x.revision,'STALE_GRAPH_EXPANSION_CANARY')),'graph-expanded-stale-vector-canary');
 const unsafe=frozen.ok;
 r.facts.push({phase:'GRAPH_RACE_NEGATIVE',stale_graph_batch_accepted:unsafe,http_status:frozen.status,
   gap:unsafe?'NATIVE_EDGE_MUTATION_NOT_PROTECTED_BY_ORIGINAL_READ_SET':'FROZEN_ROW_VECTOR_DETECTED_GRAPH_EXPANSION'});
 const newRead=await discover(ids.root);
 ok('new_root_graph_contains_late_issue',newRead.has(ids.late));
 if(unsafe){
  // This is a material design counterexample, not a reason to reconstruct a duplicate ledger.
  r.status='GAP_NATIVE_GRAPH_EXPANSION_NOT_ATOMIC_WITH_ROW_GUARDS';
  r.disposition='BLOCK_BEADS_FIRST_AUTOMATED_EFFECT_UNTIL_GRAPH_SERIALIZATION_QUALIFIED';
  ok('safety_gap_detected_and_recorded',true);
 }else{
  r.status='PASS_BOUND_NATIVE_TRANSITIVE_READSET';
  r.disposition='RESEARCH_CANDIDATE_NOT_PRODUCT';
  ok('native_row_guard_blocks_graph_expansion',true);
 }

 // 023 controlled graph-writer candidate: a native atomic transaction
 // MUST advance the owning root's own revision while creating a dependency.
 // No global mutable journal: the root itself is the scope of OCC.
 const controlledRoot='ts023-controlled-root';
 const controlledEdge='ts023-controlled-edge';
 const controlledOther='ts023-controlled-other';
 for(const id of [controlledRoot,controlledEdge,controlledOther]){
  const c=cmdJ(['create','TS023 protected '+id,'--type','task','--id',id,'--force',
   '--description','SYNTHETIC_ONLY','--metadata',JSON.stringify({ts023_marker:'BASE'})]);
  ok('created_controlled_'+id,(Array.isArray(c)?c[0]:c).id===id);
 }
 const guardedBefore=await issue(controlledRoot);
 const insertion={kind:'dep_add',dep_add:{
  source:{id:controlledRoot},target:{id:controlledEdge},type:'related'}};
 const controlled=await batch([
  patch(controlledRoot,guardedBefore.revision,'GRAPH_CHANGED_1'),
  insertion
 ],'controlled-atomic-graph-edit');
 ok('atomic_graph_edge_and_root_row_revision_update',controlled.ok);
 const guardedAfter=await issue(controlledRoot);
 ok('controlled_graph_root_revision_advances',guardedAfter.revision!==guardedBefore.revision);
 ok('controlled_graph_native_dependencies_visible',depIds(guardedAfter).includes(controlledEdge));
 const staleGuard=await batch([
  patch(controlledRoot,guardedBefore.revision,'UNSAFE_STALE'),
  {kind:'dep_add',dep_add:{source:{id:controlledRoot},target:{id:controlledOther},type:'related'}}
 ],'stale-edge-writer');
 ok('stale_concurrent_edge_writer_fails_whole_batch',!staleGuard.ok);
 const guardedFinal=await issue(controlledRoot);
 ok('native_atomic_rollback_did_not_insert_stale_edge',
  depIds(guardedFinal).includes(controlledEdge)&&!depIds(guardedFinal).includes(controlledOther));
 const staleEffect=await batch([patch(controlledRoot,guardedBefore.revision,'STALE_EFFECT_AFTER_EDGE')],
  'frozen-pregraph-effect');
 ok('stale_effect_after_controlled_edge_writer_is_refused',!staleEffect.ok);
 r.facts.push({phase:'CONTROLLED_SCOPED_GRAPH_WRITER',
  root:controlledRoot,original_version:guardedBefore.revision,updated_version:guardedAfter.revision,
  atomic_edge_inserted:depIds(guardedFinal).includes(controlledEdge),
  concurrent_edge_writer_refused:true,uncontrolled_bd_dep_add_remains_unprotected:true});
 r.status='PASS_CONDITIONAL_GRAPH_WRITER_WITH_UNCONTROLLED_EDGE_GAP';
 r.disposition='GRAPH_EXPANSION_REQUIRES_EXCLUSIVE_CAUSAL_EDGE_WRITER_CONTRACT';
 ok('conditional_fix_does_not_explain_away_original_uncontrolled_gap',unsafe===true);

 await stop();const persisted=cmdJ(['show',ids.root]);ok('third_process_native_readback',(Array.isArray(persisted)?persisted[0]:persisted).id===ids.root);
 console.log('TS_BEADS023_GRAPH_CONTROLLED='+r.status+';checks='+r.checks.length+';Product=NONE');
}catch(e){r.status='FAIL_RECONCILE_NATIVE_GRAPH';r.error=String(e.stack||e);console.error('TS_BEADS023_GRAPH_ERROR='+r.error);throw e
}finally{try{await stop()}catch(e){r.shutdown_error=String(e)}writeFileSync(OUT,JSON.stringify(r,null,2)+'\n');}
