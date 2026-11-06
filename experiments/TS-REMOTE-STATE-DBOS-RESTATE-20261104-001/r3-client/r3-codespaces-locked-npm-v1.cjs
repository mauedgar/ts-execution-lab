'use strict';
// TS R3 experimental, one-shot credential-free npm lock integrity qualification.
// Only the immutable Git checkout / native provider can attest machine identity.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const { durableCreate, assertTree, readFile, gitBlob, syncDirectory, Blocked } = require('./r3-offline-attempt-v1.cjs');

const ROOT = path.resolve(__dirname, '..');
const PREFIX = path.join(ROOT, 'r2-node');
const PIN = Object.freeze({
  lock: '8241c9d02d2da25a11b2d6c16e0c6fc64aaf2835',
  pkg: 'fa733e5bc20c5c257a042df9bfbea5377a6c7018',
  portable: '044c517c631f225e2c476046b163f53ad6b11a21',
  receipt: 'c031704445f08ce04de3d61a96fc7d9da423d03f',
  pg: '8.23.1'
});
const SHA = /^[0-9a-f]{40}$/;
const ATTEMPT = /^TS-R3-CS-[A-Z0-9-]{12,72}$/;
function blocked(code) { throw new Blocked(code); }
function digest(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function parse(buf) { try { return JSON.parse(buf.toString('utf8')); } catch { blocked('BAD_METADATA'); } }
function checkGit(out, expected) {
  if (!out || out.error || out.status !== 0 || out.signal || out.stderr?.trim()) blocked('GIT_CHECK_FAILED');
  if (out.stdout.trim() !== expected) blocked('GIT_IDENTITY_MISMATCH');
}
function execute(spawn, binary, argv, options, label) {
  let out;
  try { out = spawn(binary, argv, options); } catch { blocked(label+'_EXEC_UNKNOWN'); }
  if (!out || out.error || out.signal || out.status !== 0) blocked(label+'_FAILED_OR_UNKNOWN');
  return out;
}
function safeEnv(env) {
  if (Object.hasOwn(env, 'TS_R3_DATABASE_URL')) blocked('SECRET_ENV_PRESENT');
  const out = { CI:'true', NO_COLOR:'1', npm_config_audit:'false', npm_config_fund:'false', npm_config_ignore_scripts:'true', npm_config_registry:'https://registry.npmjs.org', npm_config_userconfig:'/dev/null' };
  for (const key of ['PATH','HOME','LANG','LC_ALL','TMPDIR','SYSTEMROOT','WINDIR']) {
    if (typeof env[key]==='string') out[key]=env[key];
  }
  return out;
}
function checkInstalled(lock, prefix, read=readFile) {
  const entries=Object.entries(lock.packages||{}).filter(([key])=>key);
  if (entries.length!==18) blocked('LOCK_ENTRY_COUNT');
  for (const [key, value] of entries) {
    if (!/^node_modules\/(?:@[-\w]+\/)?[-\w.]+(?:\/node_modules\/(?:@[-\w]+\/)?[-\w.]+)*$/.test(key)) blocked('LOCK_PATH_INVALID');
    if (typeof value.version!=='string' || !/^sha512-[A-Za-z0-9+/]+={0,2}$/.test(value.integrity||'') ||
        !/^https:\/\/registry\.npmjs\.org\//.test(value.resolved||'')) blocked('LOCK_ENTRY_INVALID');
    const pkgPath=path.join(prefix,key,'package.json');
    let pkg; try { pkg=parse(read(pkgPath)); } catch { blocked('INSTALLED_PACKAGE_UNREADABLE'); }
    if (pkg.version!==value.version) blocked('INSTALLED_VERSION_MISMATCH');
  }
  return entries.length;
}
function run({ attemptId, expectedCommit, expectedTree, root=ROOT, home=os.homedir(), spawn=cp.spawnSync,
               env=process.env, nodeVersion=process.version, onClaim=null, pins=PIN,
               durable=durableCreate, assert=assertTree, read=readFile, blob=gitBlob, installedCheck=checkInstalled }={}) {
  if (!ATTEMPT.test(attemptId||'') || !SHA.test(expectedCommit||'') || !SHA.test(expectedTree||'')) blocked('INVALID_REQUEST');
  if (!/^v22\./.test(nodeVersion)) blocked('NODE22_REQUIRED');
  const childEnv=safeEnv(env);
  const pfx=path.join(root,'r2-node'); const client=path.join(root,'r3-client');
  assert(root,false); assert(pfx,false); assert(client,false);
  if (fs.existsSync(path.join(pfx,'.npmrc'))) blocked('PROJECT_NPMRC_FORBIDDEN');
  for (const [file,expectedBlob] of [
    [path.join(pfx,'package-lock.json'),pins.lock],
    [path.join(pfx,'package.json'),pins.pkg],
    [path.join(client,'r3-portable-host-preflight.cjs'),pins.portable],
    [path.join(client,'r3-offline-attempt-v1.cjs'),pins.receipt]
  ]) { if (blob(read(file))!==expectedBlob) blocked('PINNED_BLOB_MISMATCH'); }
  const lock=parse(read(path.join(pfx,'package-lock.json')));
  if (lock.lockfileVersion!==3 || lock.packages?.['']?.dependencies?.pg!==pins.pg ||
      Object.entries(lock.packages||{}).filter(([k])=>k).length!==18) blocked('LOCK_INVALID');
  const common={cwd:root,encoding:'utf8',timeout:15000,maxBuffer:8192,env:childEnv,windowsHide:true};
  checkGit(spawn('git',['rev-parse','HEAD'],common),expectedCommit);
  checkGit(spawn('git',['rev-parse','HEAD^{tree}'],common),expectedTree);
  checkGit(spawn('git',['status','--porcelain','--untracked-files=no'],common),'');
  const metaBase=path.join(home,'.ts-r3-codespaces-attempts');
  if (!fs.existsSync(metaBase)) {
    fs.mkdirSync(metaBase,{recursive:false,mode:0o700});
    syncDirectory(home);
  }
  assert(metaBase,false);
  const directory=path.join(metaBase,attemptId);
  // A directory from any preceding attempt, even claim-only or incomplete,
  // is an irreversible no-replay barrier for this exact attempt ID.
  if (fs.existsSync(directory)) blocked('ATTEMPT_ALREADY_EXISTS');
  try { fs.mkdirSync(directory,{mode:0o700}); syncDirectory(metaBase); }
  catch { blocked('ATTEMPT_CREATE_UNKNOWN'); }
  const request={schema:'TS_R3_CODESPACES_LOCKED_NPM_V1',attempt_id:attemptId,
    source_commit:expectedCommit,source_tree:expectedTree,
    lock_blob:PIN.lock,pg:PIN.pg,expected_count:18,product_effect:'NONE'};
  const claimBytes=Buffer.from(JSON.stringify(request)+'\n');
  const claimSha=durable(directory,'claim.json',claimBytes);
  if (onClaim) onClaim(directory);
  let result='BLOCKED',failure='NONE',installed=null,ls_ok=false,preflight='NOT_RUN';
  try {
    execute(spawn,'npm',['ci','--ignore-scripts','--no-audit','--no-fund'],
      {cwd:pfx,encoding:'utf8',timeout:240000,maxBuffer:16384,env:childEnv,windowsHide:true},'NPM_CI');
    installed=installedCheck(lock,pfx,read);
    execute(spawn,'npm',['ls','--all','--depth=20'],
      {cwd:pfx,encoding:'utf8',timeout:30000,maxBuffer:16384,env:childEnv,windowsHide:true},'NPM_LS');
    ls_ok=true;
    const pre=execute(spawn,process.execPath,[path.join(client,'r3-portable-host-preflight.cjs')],
      {cwd:client,encoding:'utf8',timeout:30000,maxBuffer:8192,env:childEnv,windowsHide:true},'PREFLIGHT');
    const line=pre.stdout.trim();
    if (!/^PASS\|TS-R3\|PORTABLE_HOST_PREFLIGHT\|node=v22\.\d+\.\d+\|pg=8\.23\.1\|sources=4\|lock=GIT_BLOB_VERIFIED\|installed=PACKAGE_METADATA_ONLY\|tls=NOT_TESTED\|physical=NOT_TESTED$/.test(line) || pre.stderr?.trim()) blocked('PREFLIGHT_OUTPUT_MISMATCH');
    preflight='PASS_METADATA_ONLY'; result='PASS_LOCKED_NPM_INSTALL';
  } catch(e) { failure=e instanceof Blocked ? e.code : 'UNKNOWN_EFFECT'; }
  const receipt={schema:'TS_R3_CODESPACES_LOCKED_NPM_RECEIPT_V1',attempt_id:attemptId,
    request_sha256:claimSha,source_commit:expectedCommit,source_tree:expectedTree,
    result,failure,installed_packages:installed,npm_ls_ok:ls_ok,portable_preflight:preflight,
    npm_tarball_integrity:'NPM_CI_LOCKFILE_ENFORCED',device_attestation:'NONE',
    host_identity_proof:'NONE',physical_continuity:'NOT_TESTED',product_effect:'NONE'};
  const receiptSha=durable(directory,'receipt.json',Buffer.from(JSON.stringify(receipt)+'\n'));
  return {result, failure, receiptSha, requestSha:claimSha, attemptId, installed, preflight, status:result==='PASS_LOCKED_NPM_INSTALL'?0:2};
}
function main(){try{
  if (process.argv.length!==5) blocked('ARGUMENT_COUNT');
  const x=run({attemptId:process.argv[2],expectedCommit:process.argv[3],expectedTree:process.argv[4]});
  process.stdout.write(`${x.result}|TS-R3|CODESPACES_LOCKED_NPM|attempt=${x.attemptId}|receipt_sha256=${x.receiptSha}|packages=${x.installed??0}|preflight=${x.preflight}|failure=${x.failure}\n`);
  process.exitCode=x.status;
}catch(e){const code=e instanceof Blocked?e.code:'UNEXPECTED';process.stderr.write(`BLOCKED|TS-R3|CODESPACES_LOCKED_NPM|${code}\n`);process.exitCode=2;}}
if(require.main===module)main();
module.exports={run,checkInstalled,safeEnv,checkGit,Blocked};
