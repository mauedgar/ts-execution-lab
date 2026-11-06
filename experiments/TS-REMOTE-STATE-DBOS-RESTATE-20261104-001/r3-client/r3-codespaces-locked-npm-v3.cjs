'use strict';
// Execution Engineering experimental mechanics, Product authority NONE.
// Provider/native attestation, immutable checkout, executable provenance and
// clean-install byte integrity require separate, independently qualified evidence.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const {isDeepStrictEqual} = require('node:util');
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
const ALLOWED_LOCK_FIELDS=new Set(['name','version','lockfileVersion','requires','packages']);
const ALLOWED_ROOT_FIELDS=new Set(['name','version','dependencies']);
const ALLOWED_ENTRY_FIELDS=new Set(['version','resolved','integrity','license','dependencies',
  'optionalDependencies','peerDependencies','peerDependenciesMeta','engines','optional','bin']);
function exactFields(obj,allowed,code){
  if(!obj||Array.isArray(obj)||typeof obj!=='object'||Object.keys(obj).some(x=>!allowed.has(x)))blocked(code);
}
function triple(value){
  if(typeof value!=='string'||!/^\d+\.\d+\.\d+$/.test(value))blocked('LOCK_SEMVER_INVALID');
  return value.split('.').map(Number);
}
function compatible(version,range){
  const actual=triple(version);
  if(range==='*')return true;
  if(typeof range!=='string')blocked('LOCK_EDGE_UNSUPPORTED');
  const m=/^(\^|~|>=)?(\d+)(?:\.(\d+))?(?:\.(\d+))?$/.exec(range);
  if(!m)blocked('LOCK_EDGE_UNSUPPORTED');
  const op=m[1]||'=',ref=[Number(m[2]),Number(m[3]||0),Number(m[4]||0)];
  const cmp=(a,b)=>a[0]!==b[0]?a[0]-b[0]:a[1]!==b[1]?a[1]-b[1]:a[2]-b[2];
  if(op==='>=')return cmp(actual,ref)>=0;
  if(op==='=')return cmp(actual,ref)===0;
  if(op==='~')return cmp(actual,ref)>=0&&actual[0]===ref[0]&&actual[1]===ref[1];
  const upper=ref[0]>0?[ref[0]+1,0,0]:ref[1]>0?[0,ref[1]+1,0]:[0,0,ref[2]+1];
  return cmp(actual,ref)>=0&&cmp(actual,upper)<0;
}
function validateLock(lock,pkg,expectedVersion='8.23.1'){
  exactFields(lock,ALLOWED_LOCK_FIELDS,'LOCK_FIELDS_INVALID');
  if(lock.lockfileVersion!==3||lock.requires!==true||!lock.packages||typeof lock.name!=='string'||typeof lock.version!=='string')blocked('LOCK_SHAPE');
  const root=lock.packages[''];
  exactFields(root,ALLOWED_ROOT_FIELDS,'LOCK_ROOT_FIELDS');
  if(root.name!==lock.name||root.version!==lock.version||root.name!==pkg?.name||root.version!==pkg?.version)blocked('LOCK_ROOT_IDENTITY');
  if(!pkg||!pkg.dependencies||Array.isArray(pkg.dependencies)||typeof pkg.dependencies!=='object'||!root.dependencies)blocked('LOCK_ROOT_DEPS');
  const entries=Object.entries(lock.packages).filter(([k])=>k);
  if(entries.length!==18||pkg.dependencies.pg!==expectedVersion||root.dependencies.pg!==expectedVersion)blocked('LOCK_SHAPE');
  const required=Object.entries(pkg.dependencies);
  if(Object.keys(root.dependencies).length!==required.length||required.some(([k,v])=>root.dependencies[k]!==v))blocked('LOCK_ROOT_DEPS');
  const expected=new Map();
  for(const [key,value] of entries){
    cleanRel(key);exactFields(value,ALLOWED_ENTRY_FIELDS,'LOCK_ENTRY_FIELDS');
    const n=packageName(key);
    if(typeof value.version!=='string'||!/^\d+\.\d+\.\d+$/.test(value.version))blocked('LOCK_ENTRY_INVALID');
    if(typeof value.integrity!=='string'||!value.integrity.startsWith('sha512-'))blocked('LOCK_INTEGRITY_INVALID');
    const coded=value.integrity.slice(7);let bytes;
    try{bytes=Buffer.from(coded,'base64');}catch{blocked('LOCK_INTEGRITY_INVALID');}
    if(bytes.length!==64||bytes.toString('base64')!==coded)blocked('LOCK_INTEGRITY_INVALID');
    let uri;try{uri=new URL(value.resolved);}catch{blocked('LOCK_REGISTRY_INVALID');}
    const tarName=n.split('/').at(-1)+'-'+value.version+'.tgz';
    const canonical='https://registry.npmjs.org/'+n+'/-/'+tarName;
    if(uri.href!==canonical||value.resolved!==canonical)blocked('LOCK_REGISTRY_INVALID');
    if(value.optional!==undefined&&(n!=='pg-cloudflare'||value.optional!==true))blocked('LOCK_OPTIONAL_INVALID');
    if(value.license!==undefined&&!['MIT','ISC','Apache-2.0'].includes(value.license))blocked('LOCK_LICENSE_INVALID');
    if(value.engines!==undefined){
      exactFields(value.engines,new Set(['node']),'LOCK_ENGINE_INVALID');
      if(typeof value.engines.node!=='string'||!/^>=\s*\d+(?:\.(?:\d+|x)){0,2}$/.test(value.engines.node))blocked('LOCK_ENGINE_INVALID');
    }
    if(n==='typescript'){
      if(!value.bin||Object.keys(value.bin).sort().join(',')!=='tsc,tsserver'||
        value.bin.tsc!=='bin/tsc'||value.bin.tsserver!=='bin/tsserver')blocked('LOCK_BIN_INVALID');
    }else if(value.bin!==undefined)blocked('LOCK_BIN_INVALID');
    for(const field of ['dependencies','optionalDependencies','peerDependencies']){
      if(value[field]!==undefined){
        const o=value[field];if(!o||typeof o!=='object'||Array.isArray(o)||Object.keys(o).some(k=>typeof o[k]!=='string'))blocked('LOCK_ENTRY_INVALID');
      }
    }
    if(value.peerDependenciesMeta!==undefined){
      const meta=value.peerDependenciesMeta;
      if(!meta||Array.isArray(meta)||typeof meta!=='object')blocked('LOCK_PEER_META_INVALID');
      for(const [name,obj] of Object.entries(meta)){
        if(!value.peerDependencies||!Object.hasOwn(value.peerDependencies,name))blocked('LOCK_PEER_META_INVALID');
        exactFields(obj,new Set(['optional']),'LOCK_PEER_META_INVALID');
        if(obj.optional!==true)blocked('LOCK_PEER_META_INVALID');
      }
    }
    expected.set(key,{name:n,version:value.version,integrity:value.integrity,resolved:value.resolved,
      bin:value.bin||null,dependencies:value.dependencies||{},optionalDependencies:value.optionalDependencies||{},
      peerDependencies:value.peerDependencies||{},peerDependenciesMeta:value.peerDependenciesMeta||{},
      // A detached snapshot of the fully validated pinned metadata is mandatory.
      // npm fixture code may mutate lock objects after npm ci; do not share refs.
      pinnedMetadata:structuredClone(value)});
  }
  if(expected.get('node_modules/pg')?.version!==expectedVersion)blocked('LOCK_SHAPE');
  // The v3 fixed lock has a flat 18-entry graph; every required/optional edge
  // must resolve to the matching locked package. Missing peer is permitted ONLY
  // when explicitly declared optional in peerDependenciesMeta (pg-native).
  for(const [name,range] of required){
    const target=expected.get('node_modules/'+name);
    if(!target||!compatible(target.version,range))blocked('LOCK_ROOT_UNRESOLVED');
  }
  for(const [,entry] of expected){
    for(const field of ['dependencies','optionalDependencies','peerDependencies']){
      for(const [name,range] of Object.entries(entry[field])){
        const target=expected.get('node_modules/'+name);
        if(!target){
          if(field==='peerDependencies'&&entry.peerDependenciesMeta[name]?.optional===true){
            compatible('1.0.0',range); // validate supported range syntax even if optional/absent
            continue;
          }
          blocked('LOCK_EDGE_UNRESOLVED');
        }
        if(!compatible(target.version,range))blocked('LOCK_EDGE_INCOMPATIBLE');
      }
    }
  }
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
function scanInstalledTree(start,limit={count:0}){
  const pending=[start];
  while(pending.length){
    const item=pending.pop();let st;
    try{st=fs.lstatSync(item);}catch{blocked('INSTALLED_TREE_UNREADABLE');}
    if(st.isSymbolicLink())blocked('INSTALLED_TREE_LINK');
    limit.count++;if(limit.count>60000)blocked('INSTALLED_TREE_TOO_LARGE');
    if(st.isDirectory()){
      let list;try{list=fs.readdirSync(item);}catch{blocked('INSTALLED_TREE_UNREADABLE');}
      for(const part of list){
        if(part==='.'||part==='..'||part.includes('/')||part.includes('\\'))blocked('INSTALLED_TREE_NAME');
        pending.push(path.join(item,part));
      }
    }else if(!st.isFile())blocked('INSTALLED_TREE_SPECIAL');
  }
}
function checkHiddenLock(file,expected){
  const hidden=parse(readExact(file,1024*1024));
  exactFields(hidden,ALLOWED_LOCK_FIELDS,'HIDDEN_LOCK_FIELDS');
  if(hidden.lockfileVersion!==3||!hidden.packages||Array.isArray(hidden.packages)||typeof hidden.packages!=='object')blocked('HIDDEN_LOCK_SHAPE');
  const entries=Object.entries(hidden.packages);
  if(entries.length!==expected.size||entries.some(([k])=>!expected.has(k)))blocked('HIDDEN_LOCK_GRAPH');
  for(const [key,value] of entries){
    exactFields(value,ALLOWED_ENTRY_FIELDS,'HIDDEN_LOCK_FIELDS');
    const pin=expected.get(key);
    if(value.version!==pin.version||value.integrity!==pin.integrity||value.resolved!==pin.resolved||value.link===true||value.hasInstallScript===true)blocked('HIDDEN_LOCK_INTEGRITY');
    // Metadata-only gate: every supported hidden-lock field (including all
    // dependency/optional/peer edges, peer metadata, bins, engines and flags)
    // must be semantically identical to the reviewed pinned lock entry.
    // Object key order may differ; missing, injected or changed fields fail.
    // This is NOT an independent verification of installed executable bytes.
    if(!isDeepStrictEqual(value,pin.pinnedMetadata))blocked('HIDDEN_LOCK_METADATA_MISMATCH');
  }
}
function graphCheck(expected,prefix){
  const nm=path.join(prefix,'node_modules');assertPhysical(nm,true);
  const expectedTop=new Set(),scopes=new Map(),scanBudget={count:0};
  for(const [key,{name,version}] of expected){
    const loc=path.join(prefix,key);assertPhysical(loc,true);
    scanInstalledTree(loc,scanBudget);
    const meta=parse(readExact(path.join(loc,'package.json'),1024*1024));
    if(meta.name!==name||meta.version!==version)blocked('INSTALLED_IDENTITY_MISMATCH');
    const parts=name.split('/');
    if(parts.length===2){expectedTop.add(parts[0]);if(!scopes.has(parts[0]))scopes.set(parts[0],new Set());scopes.get(parts[0]).add(parts[1]);}
    else expectedTop.add(name);
  }
  // npm's installed hidden lock is metadata; matching the reviewed lock
  // does NOT independently establish installed tarball/executable byte integrity.
  checkHiddenLock(path.join(nm,'.package-lock.json'),expected);
  const expectedTopPlus=new Set([...expectedTop,'.package-lock.json','.bin']);
  for(const item of fs.readdirSync(nm)){
    const loc=path.join(nm,item);
    if(!expectedTopPlus.has(item))blocked('INSTALLED_UNEXPECTED_ENTRY');
    if(item==='.package-lock.json'){assertPhysical(loc);continue;}
    if(item==='.bin'){assertPhysical(loc,true);continue;}
    assertPhysical(loc,true);
    if(scopes.has(item)){
      const actual=fs.readdirSync(loc);
      if(actual.length!==scopes.get(item).size||actual.some(v=>!scopes.get(item).has(v)))blocked('INSTALLED_UNEXPECTED_ENTRY');
    }
  }
  for(const top of expectedTopPlus)if(!fs.existsSync(path.join(nm,top)))blocked('INSTALLED_MISSING_ENTRY');
  // The only permitted npm-created binary shims come from the fixed TypeScript
  // package bin mapping. Require both exact links and physical regular targets.
  const bindir=path.join(nm,'.bin'),allowed=new Set(['tsc','tsserver']);
  const actual=fs.readdirSync(bindir);
  if(actual.length!==allowed.size||actual.some(x=>!allowed.has(x)))blocked('INSTALLED_UNEXPECTED_BIN');
  for(const entry of allowed){
    const loc=path.join(bindir,entry),target=path.join(nm,'typescript','bin',entry);
    let actualTarget;
    try{actualTarget=fs.realpathSync.native(loc);}catch{blocked('INSTALLED_BIN_REDIRECT');}
    if(actualTarget!==target||!fs.lstatSync(loc).isSymbolicLink())blocked('INSTALLED_BIN_REDIRECT');
    assertPhysical(target);
    const targetInfo=fs.statSync(target);
    if(!targetInfo.isFile())blocked('INSTALLED_BIN_TARGET_INVALID');
    if(process.platform!=='win32'&&(targetInfo.mode&0o111)===0)blocked('INSTALLED_BIN_NOT_EXECUTABLE');
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

