'use strict';
// Execution Engineering experimental mechanics, Product authority NONE.
// Provider/native attestation, immutable checkout, executable provenance and
// clean-install byte integrity require separate, independently qualified evidence.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const {durableCreate, assertTree, readFile, gitBlob, syncDirectory, Blocked} = require('./r3-offline-attempt-v1.cjs');
const ROOT = path.resolve(__dirname, '..');
const PIN = Object.freeze({
  anchor: '1c7e819428595558dab146239978349449f482f7',
  lock: '8241c9d02d2da25a11b2d6c16e0c6fc64aaf2835',
  pkg: 'fa733e5bc20c5c257a042df9bfbea5377a6c7018',
  portable: '044c517c631f225e2c476046b163f53ad6b11a21',
  receipt: 'c031704445f08ce04de3d61a96fc7d9da423d03f',
  pg: '8.23.1'
});
const DELTA = Object.freeze([
  'experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r3-client/R3-CODESPACES-LOCKED-NPM-v3.md',
  'experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r3-client/r3-codespaces-locked-npm-v3.cjs',
  'experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r3-client/r3-codespaces-locked-npm-v3.test.cjs'
]);
const HASH40=/^[a-f0-9]{40}$/;
const HASH64=/^[a-f0-9]{64}$/;
const ATTEMPT=/^TS-R3-CS-[A-Z0-9-]{12,72}$/;
const FILE_ROOT='node_modules/';
const FIXED_REGISTRY='https://registry.npmjs.org/';
const blocked=c=>{throw new Blocked(c);};
const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');
function parse(b) {try{return JSON.parse(b.toString('utf8'));}catch{blocked('BAD_JSON');}}
function keys(obj){return obj&&typeof obj==='object'&&!Array.isArray(obj)?Object.keys(obj):[];}
function cleanRel(name){
  if(typeof name!=='string'||!/^node_modules\/(?:@[-\w]+\/)?[-\w.]+$/.test(name)||name.includes('..'))blocked('LOCK_PATH_INVALID');
  return name;
}
function packageName(key){return key.slice(FILE_ROOT.length);}
function validateLock(lock,pkg,expectedVersion='8.23.1'){
  if(lock?.lockfileVersion!==3||!lock.packages||!pkg||keys(lock.packages['']).length===0)blocked('LOCK_SHAPE');
  const entries=Object.entries(lock.packages).filter(([k])=>k);
  if(entries.length!==18||pkg.dependencies?.pg!==expectedVersion||lock.packages['']?.dependencies?.pg!==expectedVersion)blocked('LOCK_SHAPE');
  const roots={...lock.packages[''].dependencies,...(lock.packages[''].devDependencies||{}),...(lock.packages[''].optionalDependencies||{})};
  if(keys(roots).length!==keys(pkg.dependencies).length||keys(roots).some(k=>roots[k]!==pkg.dependencies[k]))blocked('LOCK_ROOT_DEPS');
  const expected=new Map();
  for(const [key,value] of entries){
    cleanRel(key);if(!value||typeof value!=='object'||Array.isArray(value)||expected.has(key))blocked('LOCK_ENTRY_INVALID');
    const n=packageName(key);
    if(typeof value.version!=='string'||!/^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$/.test(value.version))blocked('LOCK_ENTRY_INVALID');
    if(typeof value.integrity!=='string'||!value.integrity.startsWith('sha512-'))blocked('LOCK_INTEGRITY_INVALID');
    const coded=value.integrity.slice(7);let bytes;
    try{bytes=Buffer.from(coded,'base64');}catch{blocked('LOCK_INTEGRITY_INVALID');}
    if(bytes.length!==64||bytes.toString('base64')!==coded)blocked('LOCK_INTEGRITY_INVALID');
    let uri;
    try{uri=new URL(value.resolved);}catch{blocked('LOCK_REGISTRY_INVALID');}
    const encoded=n.replace(/^@/,'@').split('/');
    const tarName=n.split('/').at(-1)+'-'+value.version+'.tgz';
    const expectedPath='/'+encoded.join('/')+'/-/'+tarName;
    if(uri.protocol!=='https:'||uri.host!=='registry.npmjs.org'||uri.username||uri.password||uri.search||uri.hash||uri.pathname!==expectedPath)blocked('LOCK_REGISTRY_INVALID');
    for(const field of ['dependencies','optionalDependencies','peerDependencies']){
      if(value[field]!==undefined&&(!value[field]||Array.isArray(value[field])||typeof value[field]!=='object'||
        keys(value[field]).some(p=>typeof value[field][p]!=='string')))blocked('LOCK_ENTRY_INVALID');
    }
    expected.set(key,{name:n,version:value.version,integrity:value.integrity});
  }
  if(expected.get('node_modules/pg')?.version!==expectedVersion)blocked('LOCK_SHAPE');
  return expected;
}
function assertPhysical(file,isDirectory=false){
  const absolute=path.resolve(file),volume=path.parse(absolute).root;
  const pieces=path.relative(volume,absolute).split(path.sep).filter(Boolean);let cursor=volume;
  for(let i=0;i<pieces.length;i++){
    cursor=path.join(cursor,pieces[i]);let st;
    try{st=fs.lstatSync(cursor);}catch{blocked('PHYSICAL_PATH_MISSING');}
    if(st.isSymbolicLink())blocked('PHYSICAL_PATH_REDIRECT');
    if(i!==pieces.length-1||isDirectory){if(!st.isDirectory())blocked('PHYSICAL_NOT_DIRECTORY');}
    else if(!st.isFile())blocked('PHYSICAL_NOT_FILE');
  }
  let resolved;try{resolved=fs.realpathSync.native(absolute);}catch{blocked('PHYSICAL_PATH_MISSING');}
  const canon=p=>process.platform==='win32'?path.normalize(p).toLowerCase():path.normalize(p);
  if(canon(absolute)!==canon(resolved))blocked('PHYSICAL_PATH_REDIRECT');
  return absolute;
}
function readExact(file,max=256*1024*1024){
  assertPhysical(file);const st=fs.lstatSync(file);
  if(st.size>max||st.size<1)blocked('BINARY_SIZE_INVALID');
  const data=fs.readFileSync(file);if(data.length!==st.size)blocked('BINARY_CHANGED');return data;
}
function verifyTools(tools,expectedNode=process.execPath){
  // The hashes are a local binding ONLY, not authenticated provider identity.
  // CLI has no provisioned toolchain receipt: fail closed, before any Git/npm.
  if(!tools||keys(tools).sort().join(',')!=='git,node,npmCli')blocked('TOOLCHAIN_NOT_QUALIFIED');
  const paths={};
  for(const k of ['git','node','npmCli']){
    const t=tools[k];
    if(!t||keys(t).sort().join(',')!=='path,sha256'||typeof t.path!=='string'||!path.isAbsolute(t.path)||!HASH64.test(t.sha256))blocked('TOOLCHAIN_MANIFEST_INVALID');
    const physical=assertPhysical(t.path);
    if(k==='node'&&path.resolve(physical)!==path.resolve(expectedNode))blocked('NODE_EXECUTABLE_MISMATCH');
    if(sha256(readExact(physical))!==t.sha256)blocked('TOOLCHAIN_HASH_MISMATCH');
    paths[k]=physical;
  }
  return paths;
}
function isolatedEnv(home,cache,extra={}){
  const e={PATH:'/usr/bin:/bin',HOME:home,TMPDIR:home,CI:'true',LANG:'C',NO_COLOR:'1',NODE_OPTIONS:'',
    npm_config_ignore_scripts:'true',npm_config_audit:'false',npm_config_fund:'false',
    npm_config_registry:FIXED_REGISTRY,npm_config_strict_ssl:'true',
    npm_config_userconfig:'/dev/null',npm_config_globalconfig:'/dev/null',npm_config_cache:cache,
    npm_config_proxy:'',npm_config_http_proxy:'',npm_config_https_proxy:'',
    GIT_CONFIG_NOSYSTEM:'1',GIT_CONFIG_GLOBAL:'/dev/null',GIT_TERMINAL_PROMPT:'0',GIT_OPTIONAL_LOCKS:'0'};
  // Trusted caller may only inject nothing. No tokens, proxies or custom CA.
  if(keys(extra).length)blocked('ENV_OVERRIDES_FORBIDDEN');
  return e;
}
function forbidNpmrc(root,pfx,client,home){
  const found=new Set();
  for(const d of [root,pfx,client,home]){
    let here=path.resolve(d);
    for(;;){found.add(path.join(here,'.npmrc'));const up=path.dirname(here);if(up===here)break;here=up;}
  }
  for(const file of found){
    try{fs.lstatSync(file);blocked('NPM_CONFIG_PRESENT');}
    catch(e){if(e instanceof Blocked)throw e;if(e.code!=='ENOENT')blocked('NPM_CONFIG_UNKNOWN');}
  }
}
function call(spawn,cmd,args,opts,label){
  let r;try{r=spawn(cmd,args,opts);}catch{blocked(label+'_EFFECT_UNKNOWN');}
  if(!r||r.error||r.signal||!Number.isInteger(r.status))blocked(label+'_EFFECT_UNKNOWN');
  if(r.status!==0)blocked(label+'_NONZERO_EXIT');
  if(typeof r.stderr==='string'&&r.stderr.trim().length>0&&label==='GIT')blocked('GIT_UNEXPECTED_STDERR');
  return r;
}
function matchGit(spawn,binary,args,common,expected){
  const r=call(spawn,binary,args,common,'GIT');
  if(r.stdout.trim()!==expected)blocked('GIT_IDENTITY_MISMATCH');
}
function graphCheck(expected,prefix){
  const nm=path.join(prefix,'node_modules');assertPhysical(nm,true);
  const expectedTop=new Set(),scopes=new Map();
  for(const [key,{name,version}] of expected){
    const loc=path.join(prefix,key);assertPhysical(loc,true);
    const meta=parse(readExact(path.join(loc,'package.json'),1024*1024));
    if(meta.name!==name||meta.version!==version)blocked('INSTALLED_IDENTITY_MISMATCH');
    const parts=name.split('/');
    if(parts.length===2){expectedTop.add(parts[0]);if(!scopes.has(parts[0]))scopes.set(parts[0],new Set());scopes.get(parts[0]).add(parts[1]);}
    else expectedTop.add(name);
  }
  for(const item of fs.readdirSync(nm)){
    const loc=path.join(nm,item);if(item==='.package-lock.json'){assertPhysical(loc);continue;}
    if(item==='.bin'){assertPhysical(loc,true);continue;}
    if(!expectedTop.has(item))blocked('INSTALLED_UNEXPECTED_ENTRY');
    assertPhysical(loc,true);
    if(scopes.has(item)){
      const actual=fs.readdirSync(loc);if(actual.length!==scopes.get(item).size||actual.some(v=>!scopes.get(item).has(v)))blocked('INSTALLED_UNEXPECTED_ENTRY');
    }
  }
  for(const top of expectedTop)if(!fs.existsSync(path.join(nm,top)))blocked('INSTALLED_MISSING_ENTRY');
  // npm bin shims are executable conveniences, not a proof of package bytes.
  // Do not accept a status stronger than metadata even if this check passes.
  const bindir=path.join(nm,'.bin');
  if(fs.existsSync(bindir)){
    const permitted=new Set(['tsc','tsserver']);
    for(const entry of fs.readdirSync(bindir)){
      if(!permitted.has(entry))blocked('INSTALLED_UNEXPECTED_BIN');
      const loc=path.join(bindir,entry);
      const target=fs.realpathSync.native(loc),allow=path.join(nm,'typescript','bin',entry);
      if(target!==allow||!fs.lstatSync(loc).isSymbolicLink())blocked('INSTALLED_BIN_REDIRECT');
    }
  }
  return expected.size;
}
function run({attemptId,expectedCommit,expectedTree,root=ROOT,home=os.homedir(),tools=null,
  env=process.env, spawn=cp.spawnSync,nodeVersion=process.version,pins=PIN,delta=DELTA,
  read=readFile,blob=gitBlob,durable=durableCreate,sync=syncDirectory,
  nativeNode=process.execPath,onClaim=null,graph=graphCheck}={}){
  if(!ATTEMPT.test(attemptId||'')||!HASH40.test(expectedCommit||'')||!HASH40.test(expectedTree||''))blocked('INVALID_REQUEST');
  if(!/^v22\./.test(nodeVersion))blocked('NODE22_REQUIRED');
  if(Object.hasOwn(env,'TS_R3_DATABASE_URL'))blocked('SECRET_ENV_PRESENT');
  // A test-only injection is not a user-accessible command-line grant. Real
  // provider must supply separately qualified immutable tooling/provenance.
  const binaries=verifyTools(tools,nativeNode);
  const pfx=path.join(root,'r2-node'),client=path.join(root,'r3-client');
  for(const dir of [root,pfx,client,home])assertPhysical(dir,true);
  forbidNpmrc(root,pfx,client,home);
  const files=[['package-lock.json',pins.lock],['package.json',pins.pkg]];
  for(const [name,pin] of files)if(blob(read(path.join(pfx,name)))!==pin)blocked('PINNED_BLOB_MISMATCH');
  for(const [name,pin] of [['r3-portable-host-preflight.cjs',pins.portable],['r3-offline-attempt-v1.cjs',pins.receipt]]){
    if(blob(read(path.join(client,name)))!==pin)blocked('PINNED_BLOB_MISMATCH');
  }
  const lock=parse(read(path.join(pfx,'package-lock.json'))),pkg=parse(read(path.join(pfx,'package.json')));
  // ALL package SHA512 + URL + package/lock metadata BEFORE ANY network effect.
  const expected=validateLock(lock,pkg,pins.pg);
  const gitOpts={cwd:root,encoding:'utf8',timeout:15000,maxBuffer:16384,env:isolatedEnv(home,home),windowsHide:true};
  matchGit(spawn,binaries.git,['rev-parse','HEAD'],gitOpts,expectedCommit);
  matchGit(spawn,binaries.git,['rev-parse','HEAD^{tree}'],gitOpts,expectedTree);
  matchGit(spawn,binaries.git,['merge-base','HEAD',pins.anchor],gitOpts,pins.anchor);
  matchGit(spawn,binaries.git,['diff','--name-only',pins.anchor,'HEAD'],gitOpts,[...delta].sort().join('\n'));
  matchGit(spawn,binaries.git,['diff','--name-status',pins.anchor,'HEAD'],gitOpts,[...delta].sort().map(x=>'A\t'+x).join('\n'));
  matchGit(spawn,binaries.git,['status','--porcelain','--untracked-files=all'],gitOpts,'');
  const relative=path.relative(root,path.join(client,'r3-codespaces-locked-npm-v3.cjs')).split(path.sep).join('/');
  const tree=call(spawn,binaries.git,['ls-tree','-r','HEAD','--',relative],gitOpts,'GIT');
  const line=(tree.stdout||'').trimEnd();
  const m=/^100644 blob ([0-9a-f]{40})\t(.+)$/.exec(line);
  if(!m||m[2]!==relative||m[1]!==blob(read(path.join(client,'r3-codespaces-locked-npm-v3.cjs'))))blocked('RUNNER_SOURCE_MISMATCH');
  const base=path.join(home,'.ts-r3-codespaces-attempts');
  if(!fs.existsSync(base)){fs.mkdirSync(base,{recursive:false,mode:0o700});sync(home);}
  assertPhysical(base,true);
  const attempt=path.join(base,attemptId);
  if(fs.existsSync(attempt))blocked('ATTEMPT_ALREADY_EXISTS');
  try{fs.mkdirSync(attempt,{mode:0o700});sync(base);}catch{blocked('ATTEMPT_CREATE_UNKNOWN');}
  const request={schema:'TS_R3_CODESPACES_LOCKED_NPM_V3',attempt_id:attemptId,
    source_commit:expectedCommit,source_tree:expectedTree,lock_blob:pins.lock,
    toolchain_hashes:Object.fromEntries(Object.entries(tools).map(([k,v])=>[k,v.sha256])),
    package_count:expected.size,toolchain_attestation:'NONE',product_effect:'NONE'};
  const claimBytes=Buffer.from(JSON.stringify(request)+'\n');
  const claimHash=durable(attempt,'claim.json',claimBytes);
  const sandbox=path.join(attempt,'sandbox-home'),cache=path.join(attempt,'npm-cache');
  try{fs.mkdirSync(sandbox,{mode:0o700});fs.mkdirSync(cache,{mode:0o700});sync(attempt);}catch{blocked('SANDBOX_CREATE_UNKNOWN');}
  if(onClaim)onClaim(attempt); // test-only fault hook; never CLI parameter
  const npmOpts={cwd:pfx,encoding:'utf8',timeout:240000,maxBuffer:16384,
    env:isolatedEnv(sandbox,cache),windowsHide:true};
  let status='BLOCKED',failure='NONE',installed=null,npmLs=false,preflight='NOT_RUN';
  try{
    call(spawn,binaries.node,[binaries.npmCli,'ci','--ignore-scripts','--no-audit','--no-fund'],npmOpts,'NPM_CI');
    installed=graph(expected,pfx);
    call(spawn,binaries.node,[binaries.npmCli,'ls','--all','--depth=20'],npmOpts,'NPM_LS');npmLs=true;
    matchGit(spawn,binaries.git,['rev-parse','HEAD'],gitOpts,expectedCommit);
    matchGit(spawn,binaries.git,['rev-parse','HEAD^{tree}'],gitOpts,expectedTree);
    matchGit(spawn,binaries.git,['status','--porcelain','--untracked-files=all'],gitOpts,'');
    const pre=call(spawn,binaries.node,[path.join(client,'r3-portable-host-preflight.cjs')],{
      ...npmOpts,cwd:client,timeout:30000,maxBuffer:8192},'PREFLIGHT');
    const expectedLine=/^PASS\|TS-R3\|PORTABLE_HOST_PREFLIGHT\|node=v22\.\d+\.\d+\|pg=8\.23\.1\|sources=4\|lock=GIT_BLOB_VERIFIED\|installed=PACKAGE_METADATA_ONLY\|tls=NOT_TESTED\|physical=NOT_TESTED$/;
    if(!expectedLine.test(pre.stdout.trim())||pre.stderr?.trim())blocked('PREFLIGHT_OUTPUT_MISMATCH');
    preflight='PASS_METADATA_ONLY';status='PASS_METADATA_ONLY';
  }catch(error){failure=error instanceof Blocked?error.code:'UNKNOWN_EFFECT';}
  const receipt={schema:'TS_R3_CODESPACES_LOCKED_NPM_RECEIPT_V3',attempt_id:attemptId,
    claim_sha256:claimHash,source_commit:expectedCommit,source_tree:expectedTree,
    result:status,failure,installed_metadata:installed,npm_ls_ok:npmLs,portable_preflight:preflight,
    installed_byte_integrity:'NOT_PROVED',network_identity:'NOT_PROVED',
    provider_attestation:'NONE',physical_continuity:'NOT_TESTED',product_effect:'NONE'};
  const receiptHash=durable(attempt,'receipt.json',Buffer.from(JSON.stringify(receipt)+'\n'));
  return {status:status==='PASS_METADATA_ONLY'?0:2,result:status,failure,claim_sha256:claimHash,
    receipt_sha256:receiptHash,installed,attempt_id:attemptId};
}
function main(){try{
  if(process.argv.length!==5)blocked('ARGUMENT_COUNT');
  // CLI intentionally blocks without separate provider-origin signed toolchain
  // binding. Never fill tool hashes from user-provided args/env or PATH.
  const r=run({attemptId:process.argv[2],expectedCommit:process.argv[3],expectedTree:process.argv[4]});
  process.stdout.write(`${r.result}|TS-R3|CODESPACES_LOCKED_NPM_V3|attempt=${r.attempt_id}|receipt_sha256=${r.receipt_sha256}\n`);
  process.exitCode=r.status;
}catch(e){process.stderr.write(`BLOCKED|TS-R3|CODESPACES_LOCKED_NPM_V3|${e instanceof Blocked?e.code:'UNEXPECTED'}\n`);process.exitCode=2;}}
if(require.main===module)main();
module.exports={validateLock,verifyTools,forbidNpmrc,graphCheck,isolatedEnv,run,Blocked,sha256};
