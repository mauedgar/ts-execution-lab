import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdirSync,readFileSync} from 'node:fs';
import {join,resolve} from 'node:path';

const src=resolve('experiments/TS-EE-CHROMEDRIVER-20261121-001/real_session_probe.mjs');
const outRoot=resolve(process.env.TS_EE_FAULT_OUTPUT || 'fault-evidence');
const matrix=[
  ['DRIVER_EXIT','DRIVER_EXITED','NOT_REQUESTED','NOT_APPLICABLE'],
  ['SESSION_TIMEOUT','SESSION_CREATE_TIMEOUT','UNKNOWN','NOT_APPLICABLE'],
  ['POST_REJECT','SESSION_CREATE_ERROR','REJECTED','NOT_APPLICABLE'],
  ['DELETE_REJECT','SESSION_CREATED','UNKNOWN','FAIL']
];
const secrets=['FAKE_SECRET_SESSION_ID','FAKE_SECRET_TOKEN','FAKE_BASE64_PNG'];
for(const [mode,sessionState,remoteState,deleteStatus] of matrix) {
  const dest=join(outRoot,mode);
  mkdirSync(dest,{recursive:true});
  const result=spawnSync(process.execPath,[src],{
    shell:false,
    env:{...process.env,TS_EE_FAULT_MODE:mode,TS_EE_TEST_FAULTS:'1',TS_EE_OUTPUT_DIR:dest},
    encoding:'utf8',maxBuffer:1024*1024,timeout:20000
  });
  assert.equal(result.error,undefined,mode+':child error');
  assert.equal(result.status,1,mode+':must fail closed');
  const json=readFileSync(join(dest,'SESSION_REPORT.json'),'utf8');
  const receipt=JSON.parse(json);
  const expectedSession=mode==='DRIVER_EXIT'?'NOT_RUN':sessionState;
  assert.equal(receipt.session_result,expectedSession,mode+':session');
  assert.equal(receipt.session_remote_state,remoteState,mode+':remote state');
  assert.equal(receipt.session_delete,deleteStatus,mode+':protocol delete');
  assert.equal(receipt.overall,'FAIL',mode+':no success');
  assert.equal(receipt.browser_scenarios,'NOT_RUN',mode+':browser not run');
  assert.equal(receipt.network.mode,'OBSERVE_ONLY',mode+':network status');
  assert.equal(receipt.descendant_termination,'NOT_ATTESTED',mode+':descendant attestation');
  assert.equal(receipt.original_provider_attested,false,mode+':provider self-attestation');
  const surface=json+(result.stdout||'')+(result.stderr||'');
  for(const s of secrets)assert.equal(surface.includes(s),false,mode+':marker leaked');
  console.log(JSON.stringify({fault_mode:mode,status:'PASS_FAIL_CLOSED',session:receipt.session_result,
    remote_state:receipt.session_remote_state,delete:receipt.session_delete,
    driver:receipt.driver_termination,profile:receipt.profile_cleanup}));
}
console.log(JSON.stringify({matrix:'PASS',cases:matrix.length,product_effect:'NONE',network:'OBSERVE_ONLY'}));
