// TS BEADS 015. Native Beads metadata CAS in an ephemeral lab, no Product authority.
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {mkdirSync,existsSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as sleep} from 'node:timers/promises';

const bin=process.env.BD_BIN,root=process.env.LAB_ROOT;
if(!bin||!root)throw Error('LAB_ROOT_AND_BD_BIN_REQUIRED');
mkdirSync(root,{recursive:true});
if(existsSync(join(root,'.beads')))throw Error('BEADS_STORE_MUST_BE_FRESH');
const env={...process.env,BEADS_DIR:join(root,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
  BEADS_ACTOR:'ts-beads-015-lab',GIT_TERMINAL_PROMPT:'0'};
const id='ts015-cas001';
const reference='test://TS-BEADS-CAS-ABSORPTION-20261014-015/EXPERIMENT_ONLY';
const results=[];
const marks=[];
function check(name,ok,classification='NATIVE'){
  assert.equal(Boolean(ok),true,name);
  results.push({id:name,status:'PASS',class:classification});
}
function bd(...args){
  const r=spawnSync(bin,args,{cwd:root,env,encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
  if(r.error||r.status!==0)throw Error('BEADS_NATIVE_ERROR '+args.join(' ')+': '+(r.stderr||r.stdout||r.error?.message||'').slice(0,500));
  return r.stdout.trim();
}
function bdjson(...args){
  const output=bd(...args,'--json');
  const match=output.match(/(?:^|\n)\s*([\[{])/);
  if(!match)throw Error('NATIVE_JSON_NOT_FOUND:'+output.slice(0,500));
  return JSON.parse(output.slice(match.index).trim());
}
function issue(id){
  const v=bdjson('show',id);
  return Array.isArray(v)?v[0]:v;
}
const evidence={
  experiment:'TS-BEADS-CAS-ABSORPTION-20261014-015',
  authority:'NONE_PRODUCT',product_ref:'mauedgar/tecnotron-ai:tools@1ecce07708a5760c99d7faf55f2344f2eabbc119',
  product_tree:'025ce7524d1b8bf1753cfc4af964ee554d3b0977',
  observed_native_version:'beads_v1.3.1',native_storage:'DOLT_EMBEDDED_DISPOSABLE',
  developer_grant:'NONE',product_effect:'NONE',shared_dolt_push_count:0,
  results, observations:marks, limitations:[]
};
const output=process.env.RESULT_PATH||join(root,'RESULT.json');
let server=null,stderr='',stdout='';
let shutdownDone=false;
async function stopServer(){
  if(!server||shutdownDone)return;
  shutdownDone=true;
  if(server.exitCode===null){server.kill();await Promise.race([
    new Promise(resolve=>server.once('exit',resolve)),sleep(8000)
  ]);}
  if(server.exitCode===null)throw Error('NATIVE_SERVER_NOT_STOPPED');
}
try{
  bd('init','--quiet','--stealth');
  check('native_disposable_store_initialized',existsSync(join(root,'.beads')));
  const created=bdjson('create','Synthetic CAS target','--id',id,'--force','--type','task',
    '--description','SOURCE_REF='+reference+';PRODUCT_AUTHORITY=NONE');
  check('native_exact_id',created.id===id);
  const duplicate=spawnSync(bin,['create','Duplicate forbidden','--id',id,'--force','--type','task'],{
    cwd:root,env,encoding:'utf8',timeout:30000});
  check('native_duplicate_id_rejected',duplicate.status!==0);
  const port=31000+(Number(process.env.GITHUB_RUN_ID||4312)%22000);
  const base='http://127.0.0.1:'+port;
  server=spawn(bin,['serve','--addr','127.0.0.1:'+port],{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
  server.stdout.on('data',x=>{stdout+=String(x);});
  server.stderr.on('data',x=>{stderr+=String(x);});
  let healthy=false;
  for(let i=0;i<100;i++){
    if(server.exitCode!==null)throw Error('NATIVE_SERVER_EXITED_EARLY:'+server.exitCode+':'+stderr.slice(-700));
    try{
      const r=await fetch(base+'/healthz',{signal:AbortSignal.timeout(500)});
      if(r.ok){healthy=true;break;}
    }catch{}
    await sleep(200);
  }
  check('native_http_server_health',healthy);
  async function cas(input) {
    const r=await fetch(base+'/v0/beads/issues/'+id+':casMetadata',{
      method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input),
      signal:AbortSignal.timeout(12000)
    });
    const payload=await r.text();
    if(!r.ok)throw Error('NATIVE_CAS_HTTP_'+r.status+':'+payload.slice(0,800));
    let data;try{data=JSON.parse(payload);}catch{throw Error('NATIVE_CAS_RESPONSE_JSON_INVALID:'+payload.slice(0,500));}
    if(typeof data.swapped!=='boolean')throw Error('NATIVE_CAS_RESPONSE_NO_VERDICT:'+payload);
    return {status:r.status,...data};
  }
  const one=await Promise.all([
    cas({actor:'ts015-A',key:'ts015_revision',value:'epoch-A'}),
    cas({actor:'ts015-B',key:'ts015_revision',value:'epoch-B'})
  ]);
  check('native_concurrent_first_writer_single_winner',one.filter(x=>x.swapped===true).length===1);
  check('native_lost_race_explicit_refusal',one.filter(x=>x.swapped===false).length===1);
  const winner=one.find(x=>x.swapped).current;
  const loser=one.find(x=>!x.swapped);
  check('native_conflict_current_reports_winner',loser.current===winner&&['epoch-A','epoch-B'].includes(winner));
  marks.push({case:'first_writer_race',winner,results:one});
  const stale=await cas({actor:'ts015-stale',key:'ts015_revision',expected:'definitely-stale',value:'epoch-illegal'});
  check('native_stale_expected_rejected',stale.swapped===false&&stale.current===winner);
  const second=await Promise.all([
    cas({actor:'ts015-C',key:'ts015_revision',expected:winner,value:'epoch-C'}),
    cas({actor:'ts015-D',key:'ts015_revision',expected:winner,value:'epoch-D'})
  ]);
  check('native_concurrent_revision_change_single_winner',second.filter(x=>x.swapped).length===1);
  const now=second.find(x=>x.swapped).current;
  check('native_concurrent_stale_loser_sees_final',second.find(x=>!x.swapped).current===now);
  marks.push({case:'expected_version_race',previous:winner,winner:now,results:second});
  const sibling=await cas({actor:'ts015-sibling',key:'ts015_authority_anchor',
    value:'FIXTURE_ONLY:UNAUTHORIZED_PRODUCT'});
  check('native_independent_key_created',sibling.swapped===true);
  const same=await cas({actor:'ts015-recheck',key:'ts015_revision',expected:now,value:now});
  check('native_matching_noop_returns_swapped',same.swapped===true&&same.current===now);
  const recoveredSibling=await cas({actor:'ts015-sibling-observe',key:'ts015_authority_anchor',
    expected:'NOT_THE_EXISTING_AUTHORITY',value:'SHOULD_NOT_WRITE'});
  check('native_sibling_preservation',recoveredSibling.swapped===false&&recoveredSibling.current==='FIXTURE_ONLY:UNAUTHORIZED_PRODUCT');
  // UNKNOWN effect is a durable operational mark. Native CAS provides atomicity, not external validation.
  const unknown=await cas({actor:'ts015-unknown',key:'ts015_effect',
    value:{attempt_id:'ts015-attempt001',effect:'UNKNOWN',receipt:null,authority:'FIXTURE_ONLY'}});
  check('native_unknown_metadata_persisted',unknown.swapped===true&&unknown.current.effect==='UNKNOWN');
  const unguardedAttempt=await cas({actor:'ts015-stale-effect',key:'ts015_effect',
    expected:{attempt_id:'ts015-attempt001',effect:'NONE',receipt:null,authority:'FIXTURE_ONLY'},
    value:{attempt_id:'ts015-attempt002',effect:'CONFIRMED',receipt:'FAKE',authority:'NONE'}});
  check('native_unknown_stale_reconciler_cannot_overwrite',unguardedAttempt.swapped===false&&unguardedAttempt.current.effect==='UNKNOWN');
  const acknowledged={attempt_id:'ts015-attempt001',effect:'CONFIRMED',receipt:'test://synthetic-receipt',
    authority:'FIXTURE_ONLY'};
  const recon=await cas({actor:'ts015-synthetic-reconcile',key:'ts015_effect',
    expected:unknown.current,value:acknowledged});
  check('native_atomic_unknown_to_confirmed_after_injected_receipt',recon.swapped===true&&recon.current.effect==='CONFIRMED','NATIVE_STORAGE_SYNTHETIC_PROVIDER');
  const earlier=await cas({actor:'ts015-duplicate-outcome',key:'ts015_effect',
    expected:unknown.current,value:acknowledged});
  check('native_duplicate_effect_reconciliation_refused',earlier.swapped===false&&earlier.current.receipt===acknowledged.receipt);
  await stopServer();
  const got=issue(id);
  const metadata=typeof got.metadata==='string'?JSON.parse(got.metadata):got.metadata;
  check('native_restart_cli_readback_revision',metadata?.ts015_revision===now);
  check('native_restart_cli_readback_sibling',metadata?.ts015_authority_anchor==='FIXTURE_ONLY:UNAUTHORIZED_PRODUCT');
  check('native_restart_cli_readback_reconciled_effect',metadata?.ts015_effect?.receipt===acknowledged.receipt);
  const history=bd('history',id,'--limit','12');
  check('native_issue_history_present',history.trim().length>20);
  evidence.disposition='PASS_NATIVE_METADATA_CAS_WITH_PRODUCT_SEMANTIC_LIMITS';
  evidence.qualified={
    native_atomic_metadata_single_key_cas:true,native_one_winner_two_agent_race:true,
    native_conflict_current:true,native_independent_metadata_preserved:true,
    native_embedded_dolt_readback:true,synthetic_unknown_cas_guard:true};
  evidence.not_qualified=[
    'ACTUAL_EXTERNAL_PROVIDER_RECONCILIATION','PRODUCT_DEV_GRANT_SEMANTICS',
    'ATOMIC_MULTIPLE_RESOURCE_TASKCYCLE_CLOSE','MULTIPLE_INDEPENDENT_WINDOWS_RUNNERS',
    'DOLT_REMOTE_PUSH_CONFLICT_AND_SYNC','NATIVE_LIFECYCLE_EXPECTED_VERSION_SEPARATE_ROLE',
    'TRUE_CRASH_RECOVERY_WITH_EXTERNAL_DISPATCH'];
  console.log('TS_BEADS015_NATIVE_CAS=PASS;checks='+results.length+';effect=NONE_PRODUCT;atomic_single_key=QUALIFIED');
}catch(err){
  evidence.disposition='FAIL_NEEDED_RECONCILIATION';
  evidence.error=String(err?.stack||err);
  throw err;
}finally{
  try{await stopServer();}catch(err){evidence.shutdown_error=String(err);}
  evidence.native_server_logs_tail={stdout:stdout.slice(-650),stderr:stderr.slice(-650)};
  writeFileSync(output,JSON.stringify(evidence,null,2)+'\n','utf8');
  console.log('TS_BEADS015_RECEIPT='+output+';status='+evidence.disposition);
}
