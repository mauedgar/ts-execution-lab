'use strict';
// TS-REMOTE-STATE R3 experimental offline Node22 qualification.
// No external DB, secret input, npm install, service mutation, or Product effect.
// This is a local bounded command, NOT a substitute for TLS or physical proof.
const fs = require('node:fs');
const path = require('node:path');
const {createHash} = require('node:crypto');
const {spawnSync} = require('node:child_process');

const root = fs.realpathSync(__dirname);
const files = Object.freeze({
  'r3-command-core.cjs':'ecb429027fbb1d24646be72e9ae66afffb15b6a5',
  'physical-host-p01-p04-v2.cjs':'f9353c358787c712ca6f6030d9ac537dfdc739e8',
  'r3-command-core.test.cjs':'4f1c416d604f8840fe0d01ae9999c1adde690c6a',
  'physical-host-p01-p04-v2.test.cjs':'15dcf5b24f6aee8e3af34323288a0289a6aaa527'
});
const fail = (code) => {process.stderr.write('BLOCKED|TS-R3|'+code+'\n');process.exit(2);};
if (process.argv.length!==2) fail('ARGUMENTS_NOT_ALLOWED');
if (!/^v22\./.test(process.version)) fail('NODE22_REQUIRED');
for (const [name, expected] of Object.entries(files)) {
  const filename = path.join(root,name);
  if (fs.realpathSync(filename)!==filename) fail('SOURCE_NOT_REGULAR_'+name);
  const stat=fs.lstatSync(filename);
  if (!stat.isFile() || stat.size>1048576) fail('SOURCE_INVALID_'+name);
  const source=fs.readFileSync(filename);
  const gitObject=createHash('sha1')
    .update(Buffer.from('blob '+source.length+'\0','utf8'))
    .update(source).digest('hex');
  if (gitObject!==expected) fail('BLOB_SHA_MISMATCH_'+name);
}
const env={};
for (const key of ['PATH','HOME','USERPROFILE','SYSTEMROOT','WINDIR','TEMP','TMP','LANG','LC_ALL']) {
  if (typeof process.env[key]==='string') env[key]=process.env[key];
}
env.NODE_OPTIONS='';
const started=process.hrtime.bigint();
const r=spawnSync(process.execPath,
  ['--test','--test-reporter=tap','r3-command-core.test.cjs','physical-host-p01-p04-v2.test.cjs'],
  {cwd:root,env,encoding:'utf8',timeout:90000,maxBuffer:1048576,windowsHide:true});
const durationMs=Number(process.hrtime.bigint()-started)/1e6;
const stdout=typeof r.stdout==='string'?r.stdout:'';
const counts=Object.fromEntries([...stdout.matchAll(/^# (tests|pass|fail|cancelled|skipped|todo) (\d+)\s*$/gm)]
  .map(m=>[m[1],Number(m[2])]));
const pass=r.error===undefined && r.status===0 &&
  counts.tests===11 && counts.pass===11 && counts.fail===0 &&
  counts.cancelled===0 && counts.skipped===0 && counts.todo===0;
if (!pass) {
  // No DB credentials were inherited by the subprocess; bound the failure output.
  process.stderr.write('FAIL|TS-R3|OFFLINE_NODE22|status='+r.status+
    '|signal='+(r.signal||'none')+'|tests='+(counts.tests??'unknown')+
    '|pass='+(counts.pass??'unknown')+'|fail='+(counts.fail??'unknown')+
    '|error='+(r.error?r.error.code||'UNKNOWN':'none')+'\n');
  process.stderr.write(stdout.slice(-3000)+'\n');
  process.exitCode=1;
} else {
  process.stdout.write('PASS|TS-R3|OFFLINE_NODE22|tests=11|pass=11|fail=0'+
    '|source_blobs=4|node='+process.version+
    '|elapsed_ms='+durationMs.toFixed(1)+'|db_credentials_inherited=false'+
    '|physical_proof=false\n');
}
