// TS-BEADS-LIFECYCLE-PARITY-014 | isolated synthetic test double
// Requires BD_BIN and SHADOW_ROOT. No Product files are written.
// Beads CLI is the only mutable store for this experiment; source Git/receipts remain external.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.env.SHADOW_ROOT;
const bin = process.env.BD_BIN;
if (!root || !bin) throw Error('SHADOW_ROOT_AND_BD_BIN_REQUIRED');
mkdirSync(root, {recursive:true});
const beadsDir = join(root,'.beads');
if (existsSync(beadsDir)) throw Error('ISOLATION_PRECONDITION_BEADS_DIR_ALREADY_EXISTS');
const environment = {...process.env, BEADS_DIR:beadsDir, BD_NO_PUSH:'1', BD_DOLT_AUTO_PUSH:'false',
  GIT_TERMINAL_PROMPT:'0', BEADS_ACTOR:'ts-beads-014-synthetic-lifecycle'};
const IDS = Object.freeze({tc:'ts014-tc001', op:'ts014-op001', attempt:'ts014-att001',
  different:'ts014-att002', cas:'ts014-cas001', rogue:'ts014-rogue001'});
const source = 'test://TS-BEADS-LIFECYCLE-PARITY-20261014-014/SYNTHETIC';
const productBaseline = 'mauedgar/tecnotron-ai:tools@2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89';
const historicalProductTaskcycle = 'TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001';
const syntheticAuthority = 'FIXTURE_ONLY:NO_PRODUCT_DEVELOPER_GRANT';
const syntheticReceipt = 'FIXTURE_ONLY:provider-readback-014-observed-confirmed';
const checks = [];

function command(args, failOnError=true) {
  const r = spawnSync(bin,args,{cwd:root,env:environment,encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
  if (r.error) throw Error('BEADS_OS_ERROR:'+r.error.message);
  const info = {ok:r.status===0, exit:r.status, stdout:(r.stdout||'').trim(), stderr:(r.stderr||'').trim()};
  if (!info.ok && failOnError) throw Error('BD_COMMAND_FAILED:'+args.slice(0,3).join('_')+':'+info.exit+':'+info.stderr.slice(0,500)+':'+info.stdout.slice(0,500));
  return info;
}
function json(args) {
  const output=command([...args,'--json']).stdout;
  const m=output.match(/(?:^|\n)\s*(\[|\{)/);
  if (!m) throw Error('NO_JSON_FROM_BD:'+args.join('_')+':'+output.slice(0,240));
  return JSON.parse(output.slice(m.index).trim());
}
function record(id, category, observed, expected=true) {
  assert.equal(observed,expected,id);
  checks.push({id,category,result:'PASS'});
}
function list() {
  const x=json(['list','--all','--limit','100']);
  if (!Array.isArray(x)) throw Error('BD_LIST_NOT_ARRAY');
  return x;
}
function show(id) {
  const x=json(['show',id]);
  const entry=Array.isArray(x)?x[0]:x;
  if (!entry || entry.id!==id) throw Error('BD_SHOW_IDENTITY_MISMATCH:'+id);
  return entry;
}
function detail(id) {
  const x=show(id);
  const metadata=typeof x.metadata==='string'?JSON.parse(x.metadata):x.metadata;
  if (!metadata || typeof metadata!=='object' || !metadata.ts014) throw Error('FIXTURE_METADATA_MISSING:'+id);
  return {issue:x,state:metadata.ts014};
}
function create(id,title,data) {
  const x=json(['create',title,'--id',id,'--force','--type','task','--description',
    'SOURCE_REF='+source+';CLASS=NONE_PRODUCT;GIT_PRODUCT_ANCHOR='+productBaseline,
    '--metadata',JSON.stringify({ts014:data})]);
  const entry=Array.isArray(x)?x[0]:x;
  assert.equal(entry.id,id);
  return entry;
}
function persist(id, state) {
  command(['update',id,'--metadata',JSON.stringify({ts014:state})]);
  const r=detail(id).state;
  assert.deepEqual(r,state,'metadata readback '+id);
}
function attemptPresence(id) {
  return list().some(item=>item.id===id)?'PRESENT':'ABSENT';
}
class BeadsLifecycleFixture {
  // Emulates existing ports' relevant method semantics; NOT a Product adapter.
  observeOperation(id) {
    const data=detail(id).state;
    if(data.kind!=='Operation')throw Error('INVALID_OPERATION_KIND');
    return {aggregate:data,store_revision:data.revision,legal_next:['prepareAttempt']};
  }
  observeAttemptPresence(id) { return attemptPresence(id); }
  hasUnreconciledExecution() {
    return list().filter(x=>x.id.startsWith('ts014-att')).some(x=>{
      const attempt=detail(x.id).state;
      return attempt.effect_state==='UNKNOWN'||attempt.reconciliation_required===true;
    });
  }
  prepareAttempt({attemptId,operationId,authorityRefs}) {
    if(this.hasUnreconciledExecution())throw Error('UNRECONCILED_EFFECT_BLOCKS_NEW_ATTEMPT');
    if(this.observeAttemptPresence(attemptId)!=='ABSENT')throw Error('ATTEMPT_EXISTS_NO_REPLAY');
    const op=this.observeOperation(operationId).aggregate;
    if(!Array.isArray(authorityRefs)||!authorityRefs.includes(syntheticAuthority)||op.authority!==syntheticAuthority)
      throw Error('AUTHORITY_MISMATCH');
    create(attemptId,'Synthetic ExecutionAttempt',{
      kind:'ExecutionAttempt',revision:1,state:'PREPARED',operation_id:operationId,
      source_ref:source,effect_state:'NONE',reconciliation_required:false,
      authority:syntheticAuthority,receipt_ref:null});
    return detail(attemptId).state;
  }
  confirmDispatchStart(id) {
    const a=detail(id).state;
    if(a.kind!=='ExecutionAttempt'||a.state!=='PREPARED')throw Error('ATTEMPT_NOT_PREPARED');
    // UNKNOWN is conservative before a separately observed provider outcome.
    persist(id,{...a,revision:a.revision+1,state:'DISPATCHED',effect_state:'UNKNOWN',reconciliation_required:true});
    return detail(id).state;
  }
  recordExecutionOutcome({attemptId,syntheticObservedReceipt}) {
    if(syntheticObservedReceipt!==syntheticReceipt)throw Error('EXTERNAL_RECEIPT_NOT_PROVEN');
    const a=detail(attemptId).state;
    if(a.effect_state!=='UNKNOWN'||!a.reconciliation_required)throw Error('NO_UNKNOWN_TO_RECONCILE');
    // This is an injected fixture observation, not a real provider reconciliation.
    persist(attemptId,{...a,revision:a.revision+1,state:'TERMINAL',
      effect_state:'CONFIRMED',reconciliation_required:false,receipt_ref:syntheticObservedReceipt});
    return detail(attemptId).state;
  }
  snapshot(id) {
    const a=detail(id).state;
    return {revision:a.revision,event_count:null,taskcycle:a,
      obligations:{pending:Object.keys(a.obligations).filter(k=>a.obligations[k]==='PENDING')}};
  }
  satisfyObligation({expectedRevision,taskcycleId,obligationId,authorityRef}) {
    const s=this.snapshot(taskcycleId).taskcycle;
    if(s.revision!==expectedRevision)throw Error('STALE_EXPECTED_REVISION');
    if(s.state!=='ACTIVE'||s.obligations[obligationId]!=='PENDING')throw Error('ILLEGAL_OBLIGATION_TRANSITION');
    if(authorityRef!==s.authority)throw Error('NO_COMPETENT_FIXTURE_AUTHORITY');
    if(this.hasUnreconciledExecution())throw Error('UNRECONCILED_EFFECT_BLOCKS_OBLIGATION');
    persist(taskcycleId,{...s,revision:s.revision+1,
      obligations:{...s.obligations,[obligationId]:'SATISFIED'}});
    return this.snapshot(taskcycleId).taskcycle;
  }
  closeTaskCycle({expectedRevision,taskcycleId,authorityRef,dispositionRef}) {
    const s=this.snapshot(taskcycleId).taskcycle;
    if(s.revision!==expectedRevision)throw Error('STALE_EXPECTED_REVISION');
    if(s.state!=='ACTIVE'||Object.values(s.obligations).some(x=>x!=='SATISFIED'))throw Error('OBLIGATIONS_NOT_SATISFIED');
    if(this.hasUnreconciledExecution())throw Error('UNRECONCILED_EFFECT_BLOCKS_CLOSE');
    if(authorityRef!==s.authority||dispositionRef!=='FIXTURE_ONLY:CLOSED_PASS')
      throw Error('AUTHORITY_OR_DISPOSITION_NOT_PROVEN');
    // Two native CLI writes; this intentionally DOES NOT claim atomic close.
    persist(taskcycleId,{...s,revision:s.revision+1,state:'CLOSED',
      disposition_ref:dispositionRef});
    command(['close',taskcycleId,'--reason','Synthetic lab fixture only; no Product authority']);
    return detail(taskcycleId);
  }
}

command(['init','--quiet','--stealth']);
record('native_isolated_embedded_init','NATIVE',existsSync(beadsDir));
create(IDS.tc,'Synthetic TaskCycle, not a Tecnotron TaskCycle',{
  kind:'TaskCycle',revision:1,state:'ACTIVE',authority:syntheticAuthority,
  obligations:{implementation:'PENDING'},source_ref:source,
  historical_product_fixture:historicalProductTaskcycle,disposition_ref:null});
create(IDS.op,'Synthetic Operation',{
  kind:'Operation',revision:1,state:'READY',authority:syntheticAuthority,source_ref:source,
  taskcycle_id:IDS.tc});
const lifecycle=new BeadsLifecycleFixture();
record('native_issue_metadata_identity','NATIVE',detail(IDS.tc).state.source_ref===source);
record('native_duplicate_deterministic_id_rejected','NATIVE',
  command(['create','Unwanted duplicate','--id',IDS.tc,'--force','--type','task'],false).ok,false);
record('absent_attempt_identified','FIXTURE',lifecycle.observeAttemptPresence(IDS.attempt)==='ABSENT');
record('operation_observed_via_native_metadata','NATIVE',
  lifecycle.observeOperation(IDS.op).aggregate.taskcycle_id===IDS.tc);
const attempt=lifecycle.prepareAttempt({attemptId:IDS.attempt,operationId:IDS.op,authorityRefs:[syntheticAuthority]});
record('prepared_attempt_persisted','NATIVE',attempt.state==='PREPARED');
let duplicateBlocked=false;
try{lifecycle.prepareAttempt({attemptId:IDS.attempt,operationId:IDS.op,authorityRefs:[syntheticAuthority]});}
catch(e){duplicateBlocked=e.message==='ATTEMPT_EXISTS_NO_REPLAY';}
record('same_attempt_no_replay','FIXTURE',duplicateBlocked);
const dispatch=lifecycle.confirmDispatchStart(IDS.attempt);
record('unknown_persisted_after_dispatch','NATIVE',dispatch.effect_state==='UNKNOWN'&&dispatch.reconciliation_required);
const restarted=new BeadsLifecycleFixture();
record('unknown_recovered_in_fresh_adapter_instance','NATIVE',restarted.hasUnreconciledExecution());
let retryBlocked=false;
try{restarted.prepareAttempt({attemptId:IDS.different,operationId:IDS.op,authorityRefs:[syntheticAuthority]});}
catch(e){retryBlocked=e.message==='UNRECONCILED_EFFECT_BLOCKS_NEW_ATTEMPT';}
record('unknown_blocks_new_attempt','FIXTURE',retryBlocked);
let closeBlocked=false;
try{restarted.closeTaskCycle({expectedRevision:1,taskcycleId:IDS.tc,authorityRef:syntheticAuthority,
  dispositionRef:'FIXTURE_ONLY:CLOSED_PASS'});}
catch(e){closeBlocked=e.message==='OBLIGATIONS_NOT_SATISFIED';}
record('premature_close_blocked','FIXTURE',closeBlocked);
let unprovenBlocked=false;
try{restarted.recordExecutionOutcome({attemptId:IDS.attempt,syntheticObservedReceipt:'UNQUALIFIED'});}
catch(e){unprovenBlocked=e.message==='EXTERNAL_RECEIPT_NOT_PROVEN';}
record('unqualified_outcome_refused','FIXTURE',unprovenBlocked);
const reconciled=restarted.recordExecutionOutcome({attemptId:IDS.attempt,syntheticObservedReceipt:syntheticReceipt});
record('injected_receipt_transitions_to_confirmed','EMULATED_NOT_PROVIDER_PARITY',
  reconciled.effect_state==='CONFIRMED'&&!reconciled.reconciliation_required);
record('unknown_cleared_on_new_native_readback','NATIVE',
  !(new BeadsLifecycleFixture()).hasUnreconciledExecution());
const satisfied=restarted.satisfyObligation({expectedRevision:1,taskcycleId:IDS.tc,
  obligationId:'implementation',authorityRef:syntheticAuthority});
record('guarded_obligation_persisted','FIXTURE',satisfied.revision===2&&satisfied.obligations.implementation==='SATISFIED');
let staleBlocked=false;
try{restarted.satisfyObligation({expectedRevision:1,taskcycleId:IDS.tc,obligationId:'implementation',
  authorityRef:syntheticAuthority});}catch(e){staleBlocked=e.message==='STALE_EXPECTED_REVISION';}
record('sequential_stale_revision_rejected','FIXTURE_NOT_ATOMIC_CAS',staleBlocked);
const closed=restarted.closeTaskCycle({expectedRevision:2,taskcycleId:IDS.tc,
  authorityRef:syntheticAuthority,dispositionRef:'FIXTURE_ONLY:CLOSED_PASS'});
record('guarded_close_and_native_closed_readback','FIXTURE_NOT_ATOMIC_CLOSE',
  closed.issue.status==='closed'&&closed.state.state==='CLOSED');
const history=command(['history',IDS.tc,'--limit','10']);
record('native_history_read_available','NATIVE',history.stdout.length>0);
// Deliberate counterexample: both clients read revision 1, then both write revision 2.
// Plain bd update --metadata carries no expected-revision CAS in this tested path.
create(IDS.cas,'Synthetic CAS counterexample',{kind:'CAS_Fixture',revision:1,actor:'NONE'});
const initial=detail(IDS.cas).state;
assert.equal(initial.revision,1);
persist(IDS.cas,{...initial,revision:2,actor:'A'});
persist(IDS.cas,{...initial,revision:2,actor:'B'});
record('unguarded_native_update_accepts_stale_writer','NEGATIVE_NATIVE_CAS',
  detail(IDS.cas).state.actor==='B'&&detail(IDS.cas).state.revision===2);
create(IDS.rogue,'Synthetic unguarded native close',{kind:'NoProductGrant',revision:1,authority:null});
command(['close',IDS.rogue,'--reason','Negative fixture: bare Beads close has no Product grant']);
record('native_close_without_product_authority_possible','NEGATIVE_NATIVE_AUTHORITY',show(IDS.rogue).status==='closed');
const ready=json(['ready']);
record('native_ready_omits_closed_taskcycle','NATIVE',
  Array.isArray(ready)&&!ready.some(x=>x.id===IDS.tc));
const summary={
  experiment:'TS-BEADS-LIFECYCLE-PARITY-20261014-014',
  schema:'ts-beads-lifecycle-parity/experimental-v1',
  observed_basis:'NATIVE_BEADS_LOCAL_DOLT_PLUS_EXPLICIT_SYNTHETIC_PORT_ADAPTER',
  product_ref:productBaseline,
  historical_product_subject:historicalProductTaskcycle,
  native_beads_version:'1.3.1',
  native_remote:'NONE_CONFIGURED',
  native_dolt_shared_ref_modified:false,
  Product_authority:'NONE',Product_effect:'NONE',Product_repository_writes:0,
  results:{pass:checks.length,fail:0,checks},
  parity:{
    issue_identity_and_metadata:'PASS_NATIVE',
    fresh_consumer_recovery:'PASS_NATIVE_EMBEDDED',
    deterministic_native_id_collision:'PASS_NATIVE',
    history_read:'PASS_NATIVE',
    unknown_retry_block:'PASS_FIXTURE_RULE_NOT_BEADS_NATIVE',
    authority_and_close:'PASS_FIXTURE_RULE_NOT_BEADS_NATIVE',
    stale_revision_sequential:'PASS_FIXTURE_ONLY',
    atomic_expected_revision_CAS:'NOT_QUALIFIED;NEGATIVE_PLAIN_BD_UPDATE',
    atomic_taskcycle_close:'NOT_QUALIFIED;TWO_NATIVE_WRITES',
    true_external_UNKNOWN_reconciliation:'NOT_QUALIFIED;INJECTED_RECEIPT_ONLY',
    immutable_Git_receipt_identity_correspondence:'NOT_QUALIFIED',
    multi_writer_shared_server_concurrency:'NOT_RUN',
    direct_drop_in_for_Product_lifecycle:'NOT_QUALIFIED'
  },
  disposition:'PARTIAL_NATIVE_PASS_PARITY_NOT_ESTABLISHED',
  repeat_original_Product_effects:false
};
const resultPath=process.env.RESULT_PATH||join(root,'RESULT.json');
writeFileSync(resultPath,JSON.stringify(summary,null,2)+'\n','utf8');
console.log('TS_BEADS014_RESULT=PARTIAL_NATIVE_PASS_PARITY_NOT_ESTABLISHED;pass='+checks.length+';fail=0;native_cas=NOT_QUALIFIED;Product_effect=NONE');
console.log('TS_BEADS014_RESULT_JSON='+resultPath);
