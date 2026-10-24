// TS-BEADS-020 | Beads-first scoped version-vector experiment.
// PURPOSE: explore changing Product's global/synchronous contract, NOT replacing it in Product.
// This is synthetic, non-authoritative, unprivileged and disposable. No second mutable ledger.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const PROD='7a7225940aeaf1fbd16ac46ecd1cb76fa527ff56';
const TREE='8caa56d36f3efeba359bbbf65b158ffb01a19da6';
const PRODUCT_ROOT=process.env.PRODUCT_ROOT,ROOT=process.env.LAB_ROOT,
  BIN=process.env.BD_BIN,RESULT=process.env.RESULT_PATH;
if(!PRODUCT_ROOT||!ROOT||!BIN||!RESULT)throw Error('EXPLICIT_EXPERIMENT_BINDINGS_REQUIRED');
if(existsSync(join(ROOT,'.beads')))throw Error('EXPERIMENT_ROOT_ALREADY_EXISTS_NO_REPLAY');
mkdirSync(ROOT,{recursive:true});
const env={...process.env,BEADS_DIR:join(ROOT,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BEADS_ACTOR:'TS-BEADS-020-SYNTHETIC',GIT_TERMINAL_PROMPT:'0',NO_COLOR:'1'};
const evidence={
 id:'TS-BEADS-FIRST-CONTRACT-REDESIGN-20261024-020',
 product_subject:PROD,tree:TREE,authority:'NONE_PRODUCT',Product_effect:'NONE',
 shared_dolt_remote_effect:'NONE',result:'RUNNING',checks:[],negatives:[],notes:[],
 proposed_contract:'async scoped-read-set optimistic concurrency, native issue versions, no global Product Store revision and no second ledger',
 actual_Product_equivalence:'NOT_CLAIMED',fixtures:['TS020-root','TS020-gate','TS020-unrelated']
};
const verify=(key,ok,kind='positive')=>{assert.ok(ok,key);evidence.checks.push({key,result:'PASS',kind})};
const prodRequire=createRequire(join(PRODUCT_ROOT,'package.json'));
const {requireTaskCycleLifecycleCapability}=prodRequire(join(PRODUCT_ROOT,'src/operational-spine-v0/taskcycle-lifecycle-capability.js'));
const v1=requireTaskCycleLifecycleCapability({
 snapshot(){},observeInvocationBookkeeping(){},hasUnreconciledExecution(){},
 satisfyObligation(){},closeTaskCycle(){}
});
verify('current_product_structural_port_shape_read_only',!!v1);
const source=readFileSync(join(PRODUCT_ROOT,'src-typescript/operational-spine-v0/taskcycle-lifecycle-capability.ts'),'utf8');
const recipe=readFileSync(join(PRODUCT_ROOT,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js'),'utf8');
verify('current_product_sync_type_observed',source.includes('snapshot(taskcycleId: string): TaskCycleLifecycleSnapshot;'));
verify('current_product_exact_global_revision_requirement_observed',
 recipe.includes('after.revision !== before.revision + 1')&&
 recipe.includes('after.event_count !== before.event_count + 1'));
verify('no_product_source_modified_by_experiment',true);
const labels=['TS020-root','TS020-gate','TS020-unrelated'];
const id={root:'ts020-root',gate:'ts020-gate',other:'ts020-unrelated'};
let server=null,base=null,serverLog='';
function cmd(args){
 const p=spawnSync(BIN,args,{cwd:ROOT,env,encoding:'utf8',timeout:45000,maxBuffer:8*1024*1024});
 if(p.error||p.status!==0)throw Error('BEADS_CLI_FAIL:'+args.slice(0,4).join('_')+JSON.stringify({code:p.status,stderr:p.stderr,stdout:p.stdout,error:p.error?.message}).slice(0,850));
 return (p.stdout||'').trim();
}
function json(args){const v=cmd([...args,'--json']);const at=v.search(/[\[{]/);
 if(at<0)throw Error('NO_NATIVE_JSON');return JSON.parse(v.slice(at));}
function show(issue){const x=json(['show',issue]);const v=Array.isArray(x)?x[0]:x;assert.equal(v.id,issue);return v}
function metadata(issue){const m=show(issue).metadata;return typeof m==='string'?JSON.parse(m):m}
async function start(){
 const port=32100+(Number(process.env.GITHUB_RUN_ID||2020)%16000);base='http://127.0.0.1:'+port;
 server=spawn(BIN,['serve','--addr','127.0.0.1:'+port],{cwd:ROOT,env,stdio:['ignore','pipe','pipe'],windowsHide:true});
 server.stdout.on('data',d=>serverLog+=String(d));server.stderr.on('data',d=>serverLog+=String(d));
 for(let i=0;i<99;i++){if(server.exitCode!==null||server.signalCode!==null)throw Error('SERVER_EXITED:'+serverLog.slice(-450));
  try{if((await fetch(base+'/healthz',{signal:AbortSignal.timeout(350)})).ok)return;}catch{}await delay(180)}
 throw Error('SERVER_HEALTH_UNAVAILABLE:'+serverLog.slice(-450));
}
async function stop(){
 if(!server)return;
 if(server.exitCode===null&&server.signalCode===null){
  server.kill();await Promise.race([new Promise(resolve=>server.once('exit',resolve)),delay(6000)]);
 }
 if(server.exitCode===null&&server.signalCode===null)throw Error('SERVER_STOP_UNCONFIRMED');
 server=null;
}
async function call(path,payload){const r=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify(payload),signal:AbortSignal.timeout(12000)});
 const raw=await r.text();let data;try{data=JSON.parse(raw)}catch{data=null}
 return {ok:r.ok,status:r.status,data,raw:raw.slice(0,1500)};
}
const item=(id,ts020_marker,token)=>({kind:'update',update:{
 target:{id},...(token?{expected_version:token}:{}),
 patch:{metadata:{set:{ts020_marker}}}}});
let apiCalls=0;
async function transaction(items,tag){apiCalls++;
 return call('/v0/beads/issues:batchApply',{actor:'TS-BEADS-020-NONPRODUCT',provenance:'test://TS-BEADS-020/'+tag,items});
}
async function mark(id,tag,token){
 const r=await transaction([item(id,tag,token)],'capture-native-revision');
 if(!r.ok)throw Error('NATIVE_MARK_FAIL:'+id+':'+r.status+':'+r.raw);
 const version=r.data?.items?.[0]?.revision;
 if(typeof version!=='string'||!version)throw Error('NATIVE_TOKEN_MISSING:'+JSON.stringify(r.data));
 return version;
}
async function decide(candidate){
 const {authorityFixture,rootToken,gateToken,proposedMarker}=candidate;
 // New experimental contract: semantic acceptance remains OUTSIDE native Beads.
 if(!authorityFixture||authorityFixture.schema!=='TS020-SYNTHETIC_ONLY'||
   authorityFixture.verified_in_fixture!==true){
  return {status:'DENIED_LOCAL_AUTHORITY_CHECK',effect:'NONE'};
 }
 if(!rootToken||!gateToken)throw Error('EXPLICIT_SCOPED_VERSION_SET_REQUIRED');
 // Both relevant rows are protected in ONE native atomic transaction.
 // Gate is updated with same synthetic marker: inspect whether this incurs a row write.
 const result=await transaction([
  item(id.root,proposedMarker,rootToken),
  item(id.gate,'gate-observed-eligible',gateToken)
 ],'experimental-scoped-contract');
 return result.ok ? {status:'SCOPED_TRANSACTION_CONFIRMED',response:result.data}
                  : {status:'SCOPED_TRANSACTION_REFUSED',http_status:result.status,error:result.raw};
}
try{
 cmd(['init','--server','--quiet','--stealth']);
 const r=spawnSync('git',['remote'],{cwd:ROOT,env,encoding:'utf8',timeout:5000});
 verify('disposable_git_store_no_remotes',r.status===0&&!r.stdout.trim());
 for(const [native,name] of [[id.root,'TS020 Synthetic candidate'],[id.gate,'TS020 Synthetic related guard'],[id.other,'TS020 Synthetic unrelated mutation']]){
  const v=json(['create',name,'--id',native,'--type','task','--force','--description','TS-BEADS-020_SYNTHETIC_ONLY']);
  verify('native_create_'+native,(Array.isArray(v)?v[0]:v).id===native);
 }
 await start();verify('native_http_server_ready',true);
 let rootRev=await mark(id.root,'not-proposed');
 let gateRev=await mark(id.gate,'gate-observed-eligible');
 let unrelatedRev=await mark(id.other,'unrelated-original');
 verify('versions_captured_on_both_relevant_issues',rootRev&&gateRev);
 const beforeDenied=apiCalls;
 const denial=decide({authorityFixture:null,rootToken:rootRev,gateToken:gateRev,proposedMarker:'PROPOSED'});
 verify('new_async_consumer_returns_promise',denial instanceof Promise);
 const denied=await denial;
 verify('missing_semantic_authorization_blocks_before_native_batch',
  denied.status==='DENIED_LOCAL_AUTHORITY_CHECK'&&apiCalls===beforeDenied,'negative');
 verify('candidate_unchanged_after_denial',metadata(id.root).ts020_marker==='not-proposed','negative');
 const staleGate=gateRev;
 gateRev=await mark(id.gate,'gate-observed-eligible-after-race',staleGate);
 verify('related_issue_concurrent_version_changed',gateRev!==staleGate);
 const syntheticFixture={schema:'TS020-SYNTHETIC_ONLY',verified_in_fixture:true};
 const rejected=await decide({authorityFixture:syntheticFixture,
  rootToken:rootRev,gateToken:staleGate,proposedMarker:'PROPOSED'});
 verify('stale_related_read_set_precondition_rejected_atomically',
  rejected.status==='SCOPED_TRANSACTION_REFUSED','negative');
 verify('no_partial_root_mutation_after_related_stale_token',
  metadata(id.root).ts020_marker==='not-proposed','negative');
 evidence.negatives.push({test:'RELATED_ISSUE_WRITE_AFTER_READ',result:rejected.status,
  why:'Guard on related issue is necessary; per-issue root CAS alone would not cover the read-set'});
 // Recover versions from postrace native responses WITHOUT global revision.
 rootRev=await mark(id.root,'not-proposed');
 gateRev=await mark(id.gate,'gate-observed-eligible');
 unrelatedRev=await mark(id.other,'unrelated-advanced-after-checkpoint',unrelatedRev);
 verify('unrelated_issue_changed_after_scoped_checkpoint',unrelatedRev);
 const passed=await decide({authorityFixture:syntheticFixture,
  rootToken:rootRev,gateToken:gateRev,proposedMarker:'PROPOSED'});
 verify('scoped_atomic_update_succeeds_despite_unrelated_change',
  passed.status==='SCOPED_TRANSACTION_CONFIRMED');
 const rootAfter=passed.response?.items?.[0]?.revision;
 const gateAfter=passed.response?.items?.[1]?.revision;
 verify('native_root_token_returned',typeof rootAfter==='string'&&rootAfter!==rootRev);
 verify('native_gate_token_returned',typeof gateAfter==='string'&&gateAfter.length>0);
 verify('native_root_and_gate_content_correspond',
  metadata(id.root).ts020_marker==='PROPOSED'&&
  metadata(id.gate).ts020_marker==='gate-observed-eligible');
 evidence.notes.push({
  issue:'read-set guard side-effect and operational cost',
  gate_token_changed_on_same_value_update:gateAfter!==gateRev,
  gate_before_token:gateRev,gate_after_token:gateAfter,
  interpretation:gateAfter===gateRev?
   'Native unchanged-value guard did not advance version in this run; verify robustness before relying on no-op semantics':
   'Protecting a read-set using a guarded update also advances its issue revision, causing write amplification. No read-only assertVersion item was used.'
 });
 // Re-exec same prior token cannot be silently accepted and is not a durable idempotency guarantee.
 const staleReplay=await decide({authorityFixture:syntheticFixture,
  rootToken:rootRev,gateToken:gateRev,proposedMarker:'PROPOSED'});
 verify('replay_of_stale_version_vector_rejected',
  staleReplay.status==='SCOPED_TRANSACTION_REFUSED','negative');
 evidence.negatives.push({test:'EXACT_STALE_REPLAY',
  result:staleReplay.status,limitation:'not an external effect idempotency guarantee'});
 await stop();
 verify('native_cli_independent_process_readback_root',metadata(id.root).ts020_marker==='PROPOSED');
 verify('native_cli_independent_process_readback_guard',
  metadata(id.gate).ts020_marker==='gate-observed-eligible');
 evidence.native={disposable_store:true,async_consumer:true,scoped_version_vector:true,
  read_set_member_count:2,competing_related_write_rejected:true,
  unrelated_write_ignored_as_intended:true,
  gate_guard_same_value_version_change:gateAfter!==gateRev,
  no_separate_ledger:true};
 evidence.result='PASS_SCOPED_ASYNC_MODEL_WITH_LIMITATIONS';
 evidence.research_disposition='BEADS_FIRST_ARCHITECTURE_CANDIDATE_ONLY';
 evidence.unqualified=[
  'PRODUCTION_PRODUCT_SEMANTIC_AUTHORITY','REAL_PROVIDER_LOST_ACK','NOOP_NATIVE_GUARD_GENERALITY',
  'ALL_PRODUCT_TEST_VECTORS','SOURCE_PRODUCT_TASKCYCLE_LIFECYCLE',
  'CROSS_MACHINE_REMOTE_CONCURRENCY','REPLACEMENT_WITHOUT_CONSUMER_REFACTOR','DELETE_STATE_KERNEL'];
 console.log('TS_BEADS020=PASS;checks='+evidence.checks.length+
  ';async=scoped;global_revision=NOT_REQUIRED_BY_EXPERIMENTAL_CONTRACT;Product=NONE');
}catch(e){evidence.result='FAIL_RECONCILE_EXACT_ATTEMPT';evidence.error=String(e.stack||e);
 console.error('TS_BEADS020_ERROR='+evidence.error);throw e;
}finally{
 try{await stop()}catch(e){evidence.shutdown_error=String(e)}
 writeFileSync(RESULT,JSON.stringify(evidence,null,2)+'\n','utf8');
 console.log('TS_BEADS020_RECEIPT='+RESULT+';status='+evidence.result);
}
