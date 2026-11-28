import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';

const dir=process.env.TS_EE_Q5B_OUTPUT_DIR||'q5b-evidence';
const raw=readFileSync(join(dir,'Q5B_REPORT.json'),'utf8');
const r=JSON.parse(raw);
function verify(v) {
  const errors=[];
  const need=(condition,key)=>{if(!condition)errors.push(key);};
  need(v.schema==='ts-ee/chromedriver-browser-q5b/v0','schema');
  need(v.subject==='NONPRODUCT_SYNTHETIC','subject');
  need(v.engine==='CHROMEDRIVER_NODE','engine');
  need([320,375,768,1440].includes(v.requested_viewport_width),'width_request');
  need(v.observed_viewport_width===v.requested_viewport_width,'width_observed');
  need(v.overall==='PASS_BOUNDED_Q5B_BROWSER','overall');
  need(v.error_class==='NONE','error_class');
  need(v.network_mode==='OBSERVE_ONLY'&&v.os_egress_attested===false,'network');
  need(v.provider_native_verified===false&&v.product_accepted===false,'no_attestation');
  need(v.session_delete==='ACK'&&v.remote_session_state==='DELETED_CONFIRMED','session_cleanup');
  need(v.driver_termination==='DIRECT_PROCESS_EXIT_OBSERVED'&&v.descendant_termination==='NOT_ATTESTED','process_custody_ceiling');
  need(v.server_close==='CLOSED'&&v.profile_cleanup==='PASS','resource_cleanup');
  need(v.stage?.browser==='PASS'&&v.stage?.cleanup==='PASS','stage');
  const expected=['width','overflow','semantic_heading','button_label','keyboard_tab','keyboard_enter',
    'deep_link','deep_link_refresh','history_back','sku_negative','http_404','http_500','seeded_js_error','screenshot'];
  for(const key of expected)need(v.checks?.[key]==='PASS','scenario_'+key);
  need(Object.keys(v.checks||{}).length===expected.length,'scenario_count');
  need(v.local_http_events?.deniedSku===1&&v.local_http_events?.notFound===1&&v.local_http_events?.serverError===1&&v.local_http_events?.scriptError===1,'negative_http_events');
  need(v.screenshot?.filename==='q5b-'+v.requested_viewport_width+'.png','screenshot_name');
  need(Number.isInteger(v.screenshot?.bytes)&&v.screenshot.bytes>100,'screenshot_size');
  need(typeof v.screenshot?.sha256==='string'&&/^[0-9a-f]{64}$/.test(v.screenshot.sha256),'screenshot_hash');
  return errors;
}
assert.deepEqual(verify(r),[],'Actual Q5B browser receipt failed consistency validation');
const pic=readFileSync(join(dir,r.screenshot.filename));
assert.equal(pic.length,r.screenshot.bytes,'Screenshot byte length mismatch');
assert.equal(createHash('sha256').update(pic).digest('hex'),r.screenshot.sha256,'Screenshot digest mismatch');
const poisoned=[
  [{...r,error_class:'BROWSER_FAILED'},'error_class'],
  [{...r,network_mode:'PREVENTIVE_BROWSER_ABORT'},'network'],
  [{...r,checks:{...r.checks,keyboard_tab:'NOT_RUN'}},'scenario_keyboard_tab'],
  [{...r,observed_viewport_width:r.requested_viewport_width+1},'width_observed'],
  [{...r,session_delete:'FAIL'},'session_cleanup'],
  [{...r,descendant_termination:'ATTESTED'},'process_custody_ceiling'],
  [{...r,local_http_events:{...r.local_http_events,notFound:0}},'negative_http_events']
];
for(const [mutation,reason] of poisoned)assert(verify(mutation).includes(reason),'Detector sensitivity failure: '+reason);
for(const marker of ['FAKE_SECRET_SESSION_ID','FAKE_SECRET_TOKEN','FAKE_BASE64_PNG'])assert.equal(raw.includes(marker),false);
console.log(JSON.stringify({gate:'Q5B_ACTUAL_BROWSER_AND_SCREENSHOT_BYTES',width:r.requested_viewport_width,
  status:'PASS',scenario_count:14,negative_consistency_vectors:poisoned.length,
  screenshot_sha256:r.screenshot.sha256,network:'OBSERVE_ONLY',product_effect:'NONE'}));
