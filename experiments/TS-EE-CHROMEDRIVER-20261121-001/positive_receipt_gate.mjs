import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const allowlisted = new Set([
  'schema','subject','browser_scenarios','network','original_provider_attested',
  'product_accepted','status_ready_ms','session_create_ms','status_result',
  'session_result','session_delete','driver_termination','profile_cleanup',
  'descendant_termination','session_remote_state','driver_launch_status',
  'fault_mode','port_process_binding','overall','error_class'
]);
const marks = ['FAKE_SECRET_SESSION_ID','FAKE_SECRET_TOKEN','FAKE_BASE64_PNG'];
function violations(v) {
  const errors=[];
  if(v?.schema!=='ts-ee/chromedriver-session-lifecycle/v0')errors.push('schema');
  if(v?.subject!=='NONPRODUCT_SYNTHETIC')errors.push('subject');
  if(v?.overall!=='PASS_BOUNDED_DIRECT_DRIVER')errors.push('positive_verdict');
  if(v?.error_class!=='NONE')errors.push('error_class_not_none');
  if(v?.status_result!=='READY')errors.push('status_ready');
  if(v?.session_result!=='SESSION_CREATED')errors.push('session_created');
  if(v?.session_delete!=='ACK')errors.push('session_delete_ack');
  if(v?.session_remote_state!=='DELETED_CONFIRMED')errors.push('session_remote_state');
  if(v?.driver_termination!=='DIRECT_PROCESS_EXIT_OBSERVED')errors.push('direct_exit');
  if(v?.descendant_termination!=='NOT_ATTESTED')errors.push('descendant_overclaim');
  if(v?.port_process_binding!=='NOT_ATTESTED')errors.push('port_overclaim');
  if(v?.profile_cleanup!=='PASS')errors.push('profile_cleanup');
  if(v?.browser_scenarios!=='NOT_RUN')errors.push('browser_overclaim');
  if(v?.network?.mode!=='OBSERVE_ONLY'||v?.network?.os_egress_attested!==false)errors.push('egress_overclaim');
  if(v?.original_provider_attested!==false||v?.product_accepted!==false)errors.push('attestation_overclaim');
  if(v?.fault_mode!=='NONE')errors.push('unexpected_fault_mode');
  if(v?.driver_launch_status!=='SPAWN_REQUESTED')errors.push('spawn_state');
  if(!(Number.isInteger(v?.session_create_ms)&&v.session_create_ms>=0))errors.push('session_elapsed');
  if(!(Number.isInteger(v?.status_ready_ms)&&v.status_ready_ms>=0))errors.push('status_elapsed');
  if(v===null||typeof v!=='object'||Object.keys(v).some(k=>!allowlisted.has(k)))errors.push('unlisted_field');
  const json=JSON.stringify(v);
  if(marks.some(m=>json.includes(m)))errors.push('sensitive_marker');
  return errors;
}
const path=join(process.env.TS_EE_OUTPUT_DIR||'chromedriver-evidence','SESSION_REPORT.json');
const text=readFileSync(path,'utf8');
const original=JSON.parse(text);
assert.deepEqual(violations(original),[],'Original positive receipt is inconsistent');
const poisoned=[
  [{...original,error_class:'CLEANUP_OR_RUNTIME_FAILED'},'error_class_not_none'],
  [{...original,session_delete:'FAIL'},'session_delete_ack'],
  [{...original,descendant_termination:'ATTESTED'},'descendant_overclaim'],
  [{...original,network:{...original.network,mode:'PREVENTIVE_BROWSER_ABORT'}},'egress_overclaim'],
  [{...original,session_remote_state:'UNKNOWN'},'session_remote_state'],
  [{...original,unexpected_secret:'FAKE_SECRET_TOKEN'},'unlisted_field'],
  [{...original,overall:'FAIL'},'positive_verdict']
];
for(const [bad,expected] of poisoned) {
  assert(violations(bad).includes(expected),'Negative consistency fixture undetected: '+expected);
}
console.log(JSON.stringify({
  gate:'POSITIVE_RECEIPT_CROSS_FIELD',
  status:'PASS',negative_consistency_vectors:poisoned.length,
  native_provider_attested:false,product_accepted:false,
  network_assurance:'OBSERVE_ONLY',descendants:'NOT_ATTESTED'
}));
