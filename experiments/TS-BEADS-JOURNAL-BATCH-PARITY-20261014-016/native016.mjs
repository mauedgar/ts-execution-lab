// TS-BEADS-JOURNAL-BATCH-PARITY-016. Real native Beads v1.3.1, disposable Dolt SQL only.
// Product SOT and shared Dolt refs are independently protected by the Actions wrapper.
// This tests storage primitives, NEVER competence/Developer acceptance of any Product TaskCycle.
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {mkdirSync,existsSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const bin=process.env.BD_BIN,root=process.env.LAB_ROOT;
if(!bin||!root)throw Error('BD_BIN_AND_LAB_ROOT_REQUIRED');
mkdirSync(root,{recursive:true});
if(existsSync(join(root,'.beads')))throw Error('MUST_USE_DISPOSABLE_FRESH_BEADS_DIR');
const env={...process.env,BEADS_DIR:join(root,'.beads'),BD_NO_PUSH:'1',BD_DOLT_AUTO_PUSH:'false',
 BD_EVENTS_JOURNAL:'1',BEADS_ACTOR:'ts016-lab-only',GIT_TERMINAL_PROMPT:'0',NO_COLOR:'1'};
const ids={tc:'ts016-taskcycle',obligation:'ts016-obligation',run:'ts016-runrecord'};
const scope='test://TS-BEADS-JOURNAL-BATCH-PARITY-20261014-016/SYNTHETIC';
const checks=[],observations=[];
let server=null,stdout='',stderr='',stopped=false;
const resultPath=process.env.RESULT_PATH||join(root,'RESULT.json');
const report={
 schema:'ts-beads-native-journal-batch-parity/016',
 experiment:'TS-BEADS-JOURNAL-BATCH-PARITY-20261014-016',
 Product_authority:'NONE',Product_effect:'NONE',Product_repo_writes:0,
 shared_dolt_remote_writes:0,lab:'SQL_SERVER_DISPOSABLE_NO_GIT_REMOTES',
 source_product:'mauedgar/tecnotron-ai:tools@1ecce07708a5760c99d7faf55f2344f2eabbc119',
 source_product_tree:'025ce7524d1b8bf1753cfc4af964ee554d3b0977',
 historical_product_taskcycle:'TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001_CLOSED_PASS_READONLY',
 product_contracts:{
  run_event:'src/contracts/run-event.js@3196e19de90b282d03b5236c07dc38eeb7ffcffc',
  run_state:'src/contracts/run-state.js@ca542d2cbe45624c0d3b236b57995e13809f9f6a',
  run_store:'src/core/run-store.js@b4c53a17aa1d0a3362fa1b225634d5e706a0417d'
 },
 checks,observations,limitations:[]
};
function ok(id,condition,kind='NATIVE'){
 assert.equal(Boolean(condition),true,id);
 checks.push({id,status:'PASS',kind});
}
function cmd(args,{allowFailure=false}={}){
 const x=spawnSync(bin,args,{cwd:root,env,encoding:'utf8',timeout:30000,maxBuffer:16*1024*1024});
 const state={status:x.status,stdout:(x.stdout||'').trim(),stderr:(x.stderr||'').trim(),error:x.error?.message};
 if((x.error||x.status!==0)&&!allowFailure)throw Error('BEADS_CLI_FAILURE:'+args.slice(0,4).join('_')+':'+JSON.stringify(state).slice(0,850));
 return state;
}
function json(args){const t=cmd([...args,'--json']).stdout;const m=t.match(/(?:^|\n)\s*([\[{])/);if(!m)throw Error('BD_JSON_MISSING:'+args.join(' ')+':'+t.slice(0,500));return JSON.parse(t.slice(m.index).trim());}
function show(id){const a=json(['show',id]);const o=Array.isArray(a)?a[0]:a;if(!o||o.id!==id)throw Error('NATIVE_ISSUE_MISMATCH:'+id);return o;}
function make(id,title,metadata){
 const out=json(['create',title,'--id',id,'--force','--type','task',
  '--description','ORIGIN='+scope+';Product_authority=NONE','--metadata',JSON.stringify(metadata)]);
 ok('issue_created_'+id,(Array.isArray(out)?out[0]:out).id===id);
}
function parseJournal(raw){
 return raw.split(/\r?\n/).map(x=>x.trim()).filter(x=>x.startsWith('{')&&x.includes('"seq"')).map(x=>JSON.parse(x));
}
function getIssue(obj,id,depth=0){
 if(!obj||typeof obj!=='object'||depth>5)return null;
 if(!Array.isArray(obj)&&obj.id===id&&typeof obj.status==='string')return obj;
 for(const v of Object.values(obj)){const z=getIssue(v,id,depth+1);if(z)return z;}
 return null;
}
async function stop(){
 if(!server||stopped)return;
 stopped=true;
 if(server.exitCode===null&&server.signalCode===null){
  server.kill();await Promise.race([new Promise(resolve=>server.once('exit',resolve)),delay(6500)]);
 }
 if(server.exitCode===null&&server.signalCode===null)throw Error('NATIVE_HTTP_SERVER_NOT_STOPPED');
}
let base='';
async function request(path,method='GET',data=null){
 const options={method,signal:AbortSignal.timeout(12000)};
 if(data){options.headers={'Content-Type':'application/json'};options.body=JSON.stringify(data);}
 const r=await fetch(base+path,options);
 const raw=await r.text();
 let jsonData=null;try{jsonData=raw?JSON.parse(raw):null;}catch{}
 return {code:r.status,ok:r.ok,data:jsonData,raw};
}
function events(j,label){
 if(!j.ok||!j.data||!Array.isArray(j.data.records)||!Number.isInteger(j.data.head))
  throw Error('JOURNAL_INVALID_'+label+':'+j.code+':'+j.raw.slice(0,650));
 return j.data;
}
function positionCheck(list){return list.every((x,i)=>Number.isInteger(x.seq)&&x.seq>0&&(i===0||x.seq>list[i-1].seq));}
try{
 cmd(['init','--server','--quiet','--stealth']);
 cmd(['config','set','events-journal','true']);
 ok('native_server_mode_and_journal_configured',existsSync(join(root,'.beads')));
 make(ids.obligation,'Synthetic obligation for close', {ts016:{kind:'OBLIGATION',ref:scope,authority:'FIXTURE_ONLY'}});
 make(ids.tc,'Synthetic TaskCycle; never Product', {ts016:{kind:'TASKCYCLE',state:'ACTIVE',
   revision_token:'r1',obligations:['ts016-obligation'],authority:'FIXTURE_ONLY'}});
 make(ids.run,'Synthetic RunStore event counterpart', {ts016:{
   kind:'RUN_EVENT_ANALOG',artifact:'RUN_EVENT',schema_version:'fitflow-run-event/v2',
   run_id:'synthetic-run-016',event_id:'event-016-001',sequence:1,
   event_type:'STATE_TRANSITION',actor:'synthetic-agent',inputs:[],outputs:[]
 }});
 cmd(['dep','add',ids.tc,ids.obligation,'--type','blocks']);
 const beginIssue=show(ids.tc);
 ok('native_taskcycle_initially_open',beginIssue.status==='open');
 const beginDependency=show(ids.obligation);
 ok('native_obligation_initially_open',beginDependency.status==='open');
 const port=31100+(Number(process.env.GITHUB_RUN_ID||116)%21400);
 base='http://127.0.0.1:'+port;
 server=spawn(bin,['serve','--addr','127.0.0.1:'+port],{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});
 server.stdout.on('data',x=>{stdout+=String(x);});
 server.stderr.on('data',x=>{stderr+=String(x);});
 let healthy=false;
 for(let i=0;i<90;i++){
  if(server.exitCode!==null||server.signalCode!==null)throw Error('NATIVE_HTTP_SERVER_EXITED_EARLY:'+stderr.slice(-900));
  try{let z=await fetch(base+'/healthz',{signal:AbortSignal.timeout(500)});if(z.ok){healthy=true;break;}}catch{}
  await delay(250);
 }
 ok('native_http_on_disposable_dolt_server',healthy);
 const before=events(await request('/v0/beads/events?since=0&limit=200'),'baseline');
 ok('native_mutation_journal_has_baseline',before.records.length>=3);
 ok('native_journal_sequence_monotonic',positionCheck(before.records));
 ok('native_journal_contains_fixture_sources',before.records.some(x=>x.issue_id===ids.tc)&&before.records.some(x=>x.issue_id===ids.run));
 const checkpoint=before.records.at(-1).seq;
 observations.push({case:'journal_checkpoint_before',seq:checkpoint,head:before.head,count:before.records.length,
  first_op:before.records[0].op,last_op:before.records.at(-1).op});
 const pageEmpty=events(await request('/v0/beads/events?since='+checkpoint+'&limit=200'),'caught_up');
 ok('native_journal_caught_up_checkpoint_empty',pageEmpty.records.length===0);
 // Deliberate atomic rollback: prior valid close, then non-existent target. Neither may land.
 const rejected=await request('/v0/beads/issues:batchApply','POST',{
  actor:'ts016-atomic-rollback-test',
  items:[
   {kind:'close',close:{target:{id:ids.obligation},reason:'fixture would satisfy'}},
   {kind:'close',close:{target:{id:'ts016-no-such-issue'},reason:'must abort transaction'}}
  ],provenance:'test://TS016/rollback'
 });
 ok('native_batch_rejects_invalid_member',rejected.code>=400);
 const stillObligation=await request('/v0/beads/issues/'+ids.obligation);
 const stillObj=getIssue(stillObligation.data,ids.obligation);
 ok('native_rollback_preserves_first_close',stillObligation.ok&&stillObj?.status==='open');
 const sameJournal=events(await request('/v0/beads/events?since='+checkpoint+'&limit=200'),'rollback');
 ok('native_failed_batch_does_not_append_events',sameJournal.records.length===0);
 // One native all-or-nothing batch: satisfy dependency, patch synthetic disposition, close TaskCycle issue.
 const satisfied=await request('/v0/beads/issues:batchApply','POST',{
  actor:'ts016-atomic-fixture',
  provenance:'test://TS016/close-transaction',
  items:[
   {kind:'close',close:{target:{id:ids.obligation},reason:'synthetic obligation satisfied'}},
   {kind:'update',update:{target:{id:ids.tc},patch:{
    metadata:{set:{ts016_disposition:{kind:'CLOSED_PASS_SYNTHETIC',
      authority:'FIXTURE_ONLY',receipt_ref:'test://TS016/NOT_A_REAL_PROVIDER_RECEIPT'}}}}}},
   {kind:'close',close:{target:{id:ids.tc},reason:'synthetic TaskCycle complete'}}
  ]
 });
 if(!satisfied.ok)throw Error('NATIVE_BATCH_APPLY_FAIL:'+satisfied.code+':'+satisfied.raw.slice(0,1250));
 ok('native_batch_apply_multiitem_commit',satisfied.ok);
 observations.push({case:'batch_apply_response',code:satisfied.code,body:satisfied.data});
 const closedObligation=getIssue((await request('/v0/beads/issues/'+ids.obligation)).data,ids.obligation);
 const closedTC=getIssue((await request('/v0/beads/issues/'+ids.tc)).data,ids.tc);
 ok('native_batch_obligation_closed',closedObligation?.status==='closed');
 ok('native_batch_taskcycle_closed',closedTC?.status==='closed');
 const after=events(await request('/v0/beads/events?since='+checkpoint+'&limit=200'),'commit');
 ok('native_committed_batch_journal_nonempty',after.records.length>=2);
 ok('native_committed_batch_journal_monotonic',positionCheck(after.records));
 ok('native_committed_batch_observed_both_issues',after.records.some(x=>x.issue_id===ids.obligation)&&after.records.some(x=>x.issue_id===ids.tc));
 const nextCheckpoint=after.records.at(-1).seq;
 const caughtUp=events(await request('/v0/beads/events?since='+nextCheckpoint+'&limit=200'),'final_caught_up');
 ok('native_resume_after_checkpoint_has_no_duplicate',caughtUp.records.length===0);
 const rawRunEvent=before.records.find(x=>x.issue_id===ids.run);
 const requiredOriginal=['artifact','schema_version','event_id','sequence','task_id','run_id',
  'created_at','event_type','actor','state_from','state_to','reason_code','inputs','outputs'];
 const missingDirect=requiredOriginal.filter(k=>!Object.prototype.hasOwnProperty.call(rawRunEvent,k));
 ok('native_journal_not_direct_RunEvent_v2',missingDirect.length>0,'NEGATIVE_SCHEMA_MATCH');
 observations.push({case:'schema_semantic_gap',missing_direct_RunEvent_v2_fields:missingDirect,
   bead_journal_keys:Object.keys(rawRunEvent),run_event_contract_blob:'3196e19de90b282d03b5236c07dc38eeb7ffcffc'});
 await stop();
 const tcAfter=show(ids.tc);
 const obAfter=show(ids.obligation);
 ok('native_cli_after_http_shutdown_sees_both_closes',tcAfter.status==='closed'&&obAfter.status==='closed');
 const meta=typeof tcAfter.metadata==='string'?JSON.parse(tcAfter.metadata):tcAfter.metadata;
 ok('native_persisted_synthetic_disposition_in_close',meta?.ts016_disposition?.kind==='CLOSED_PASS_SYNTHETIC');
 const localJournal=parseJournal(cmd(['events','tail','--since',String(checkpoint),'--limit','200']).stdout);
 ok('native_journal_cursor_survives_http_shutdown',localJournal.length===after.records.length&&localJournal.every((x,i)=>x.seq===after.records[i].seq));
 const history=cmd(['history',ids.tc,'--limit','20']);
 ok('native_separate_issue_history_present',history.stdout.length>18);
 report.disposition='PASS_NATIVE_BATCH_ATOMICITY_AND_LOCAL_JOURNAL_WITH_LIMITS';
 report.qualified={
  native_batch_rollback_transaction:true,native_batch_multi_issue_close_transaction:true,
  native_batch_metadata_patch_and_close_transaction:true,native_local_journal_cursor_resume:true,
  native_local_journal_persistent_readback:true,native_dolt_issue_history:true
 };
 report.not_qualified=[
  'PRODUCT_TASKCYCLE_CLOSE_POLICY_OR_DEVELOPER_AUTHORITY',
  'EXTERNAL_PROVIDER_RECEIPT_AND_UNKNOWN_EFFECT_CORRESPONDENCE',
  'NATIVE_JOURNAL_CROSS_REPLICA_SYNC_OR_BACKUP',
  'RunEventV2_DIRECT_SCHEMA_EQUIVALENCE',
  'RunStateV2_SNAPSHOT_EQUIVALENCE',
  'PRODUCT_RUNSTORE_PHYSICAL_DELETION',
  'DISTRIBUTED_MULTI_WRITER_PRODUCT_ATOMICITY'
 ];
 report.journal={before_count:before.records.length,after_delta_count:after.records.length,
  checkpoint_before:checkpoint,checkpoint_after:nextCheckpoint, local_only:true,
  sync_and_merge_NOT_JOURNALED:true};
 console.log('TS_BEADS016_NATIVE=PASS;checks='+checks.length+';rollback=PASS;atomic_batch_close=PASS;local_event_journal=PASS;Product_effect=NONE');
}catch(error){
 report.disposition='FAIL_NEEDS_RECONCILIATION';report.error=String(error?.stack||error);
 console.error('TS_BEADS016_DIAGNOSTIC_ERROR='+report.error);
 throw error;
}finally{
 try{await stop();}catch(error){report.server_shutdown_error=String(error);}
 report.server_logs_tail={stdout:stdout.slice(-700),stderr:stderr.slice(-700)};
 writeFileSync(resultPath,JSON.stringify(report,null,2)+'\n','utf8');
 console.log('TS_BEADS016_RECEIPT='+resultPath+';status='+report.disposition);
}
