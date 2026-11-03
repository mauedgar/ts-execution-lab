'use strict';
// Transport-only reconstruction of ORIGINAL, byte-identical initialization
// artifacts; invokes the canonical reconciliation primitive exactly once.
// Does not invoke the initialization primitive or mutate Product Git refs.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const id='TASKCYCLE-TECNOTRON-ULC-OP05-H6-ATTENDANCE-DOMAIN-001';
const sha=t=>'sha256:'+crypto.createHash('sha256').update(t,'utf8').digest('hex');
function check(ok,why){if(!ok)throw new Error('BLOCKED_PRECONDITION:'+why);}
const envelopeFile=path.resolve('transport/handoffs/TECNOTRON-H6-ORIGINAL-NATIVE-INITIALIZATION-20261102-001/ORIGINAL_ENVELOPE.txt');
const raw=fs.readFileSync(envelopeFile,'utf8');
check(Buffer.byteLength(raw,'utf8')===16886,'ORIGINAL_ENVELOPE_SIZE');
check(sha(raw)==='sha256:187725e02986a895c9cd6876f27e15c990230219cc9218dfd2d7f5bddc8c0db3','ORIGINAL_ENVELOPE_SHA256');
const doc=JSON.parse(raw);
check(doc.original_receipt?.operation_id==='OP-TECNOTRON-H6-NATIVE-INITIALIZATION-20261102-001','ORIGINAL_OPERATION');
check(doc.original_receipt?.native_result==='PASS','ORIGINAL_INIT_RESULT');
check(doc.original_receipt?.effect_state==='CONFIRMED_LOCAL_ONLY_PENDING_DURABLE_PUBLICATION','ORIGINAL_EFFECT_SCOPE');
const p=doc.original_byte_payloads.find(x=>x.taskcycle_id===id);
check(p!==undefined,'ORIGINAL_DOMAIN_INIT_MISSING');
check(sha(p.manifest_text)===p.manifest_sha256&&sha(p.projection_text)===p.projection_sha256,'ORIGINAL_INIT_BYTES');
check(p.manifest_sha256==='sha256:fd46c05a2ff17d6906829fe9c2e32973cb0b8dfbc15db1d96508ffa8464457cb','INIT_MANIFEST_IDENTITY');
check(p.projection_sha256==='sha256:fdfd09ae658f285bb4f632743f7924cc44feab3c5ee9b8514aadcbdec7d632f1','INIT_PROJECTION_IDENTITY');
const init=path.resolve(process.env.RUNNER_TEMP,'h6-original-initialization-domain');
const out=path.resolve(process.env.RUNNER_TEMP,'h6-domain-phase1-effect-output');
check(!fs.existsSync(init)&&!fs.existsSync(out),'PREFLIGHT_ROOT_ALREADY_EXISTS');
fs.mkdirSync(init,{recursive:false});
fs.writeFileSync(path.join(init,'manifest.json'),p.manifest_text,{flag:'wx'});
fs.writeFileSync(path.join(init,'projection.json'),p.projection_text,{flag:'wx'});
fs.mkdirSync(out,{recursive:false});
const root=path.resolve('candidate/src/deterministic-taskcycle-substrate-v0');
const {consumeTaskCycleInitialization}=require(path.join(root,'taskcycle-initialization.js'));
const {createTaskCycleEffectReconciliationCapability,consumeTaskCycleEffectReconciliation}=require(path.join(root,'taskcycle-effect-reconciliation.js'));
const consumed=consumeTaskCycleInitialization({location:init,expected_identity_sha256:p.manifest_sha256});
check(consumed.manifest.taskcycle_id===id,'CONSUMED_DOMAIN_IDENTITY');
const subject={
  repository:'mauedgar/tecnotron-ai',
  branch:'task/tecnotron-h6-attendance-parent-children-20261102-001',
  commit:'ca0d2c5dc4b9623b2260651d9398b4b4b2777265',
  tree:'a550bf73748345e7b6d30b26ffe4db2da1140888',
  parent:'add3f2525b3b711ce4e396a2e5ce2864f3ceef10',
  changed_paths:['attendance/core/**','attendance/storage/**','attendance/tests/core/**']
};
const request={
  taskcycle:{id,responsibility:'ATTENDANCE_DOMAIN_PERSISTENCE_001'},
  initialization:{location_or_ref:init,identity_sha256:p.manifest_sha256},
  obligation:{id:'implementation',semantic_status:'COMPLETED_BEFORE_LIFECYCLE_INITIALIZATION'},
  subject,
  authority_refs:[
   'https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6568309396',
   'https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6589727755',
   'https://github.com/mauedgar/tecnotron-ai/issues/35#issuecomment-6589970592'
  ],
  evidence_refs:[
   'https://github.com/mauedgar/ts-execution-lab/actions/runs/41552150914',
   'mauedgar/tecnotron-ai@ca0d2c5dc4b9623b2260651d9398b4b4b2777265',
   'mauedgar/ts-execution-transport@e44ce45eeb10b1719f4ede69cd4f81ad89bdf11b:handoffs/TECNOTRON-H6-ORIGINAL-NATIVE-INITIALIZATION-20261102-001/ORIGINAL_ENVELOPE.txt'
  ],
  next_gate:'PROMOTION_GRADE_VALIDATION'
};
const observed={subject:{...subject,changed_paths:[...subject.changed_paths]}};
const result=createTaskCycleEffectReconciliationCapability({root:out}).reconcileCompletedObligation({request,observed});
check(result.status==='PASS'&&result.effect_state==='CONFIRMED'&&result.replayed===false&&result.already_reconciled===false,'NATIVE_RECONCILIATION_NOT_PASS:'+JSON.stringify(result));
const portable=result.portable_projection;
check(!!portable?.location_or_ref&&!!portable?.identity_sha256,'RECEIPT_MISSING');
const checkReceipt=consumeTaskCycleEffectReconciliation({location:portable.location_or_ref,expected_identity_sha256:portable.identity_sha256});
check(checkReceipt.projection.reconciled_effect.mutation_during_reconciliation==='NONE','RECONCILIATION_MUTATED_ORIGINAL');
const record={
  schema:'tecnotron-h6-domain-product-native-effect-reconciliation-receipt/v1',
  kind:'NATIVE_ORIGINAL_EXECUTION_ATTEMPT',
  execution_attempt_id:'EXECUTIONATTEMPT-H6-DOMAIN-PRODUCT-PHASE1-RECONCILE-20261102-001',
  source_initialization_sha256:p.manifest_sha256,
  source_original_envelope_sha256:sha(raw),
  subject,
  result,
  recon_manifest_sha256:portable.identity_sha256,
  GitHub_run_id:process.env.GITHUB_RUN_ID,
  prohibits:['new TaskCycle initialization','Operator effect','Parent effect','Product tools write','Phase2 integration']
};
const reportRoot=path.resolve('native-receipt');
check(!fs.existsSync(reportRoot),'RECEIPT_OUTPUT_EXISTS');
fs.mkdirSync(reportRoot);
fs.copyFileSync(path.join(portable.location_or_ref,'manifest.json'),path.join(reportRoot,'manifest.json'),fs.constants.COPYFILE_EXCL);
fs.copyFileSync(path.join(portable.location_or_ref,'projection.json'),path.join(reportRoot,'projection.json'),fs.constants.COPYFILE_EXCL);
fs.writeFileSync(path.join(reportRoot,'result.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
console.log('H6_PRODUCT_NATIVE_PHASE1_EFFECT_RECONCILIATION_PASS',JSON.stringify({candidate:subject.commit,manifest:portable.identity_sha256,run:process.env.GITHUB_RUN_ID}));
