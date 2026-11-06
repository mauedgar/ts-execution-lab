'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const {run,validateLock,graphCheck,verifyTools,sha256,Blocked}=require('./r3-codespaces-locked-npm-v3.cjs');
const {gitBlob}=require('./r3-offline-attempt-v1.cjs');
const PREFIX='experiments/TS-REMOTE-STATE-DBOS-RESTATE-20261104-001/r3-client/';
const DELTA=['R3-CODESPACES-LOCKED-NPM-v3.md','r3-codespaces-locked-npm-v3.cjs','r3-codespaces-locked-npm-v3.test.cjs'].map(s=>PREFIX+s).sort().join('\n');
const SHA='a'.repeat(40),TREE='b'.repeat(40),ATTEMPT='TS-R3-CS-V3-20261106-001-A01';
const sha=buf=>crypto.createHash('sha256').update(buf).digest('hex');
function fixture(t){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ts-r3-v3-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const root=path.join(temp,'experiment'),home=path.join(temp,'home'),toolroot=path.join(temp,'tools');
  for(const dir of [root,home,toolroot,path.join(root,'r2-node'),path.join(root,'r3-client')])fs.mkdirSync(dir,{recursive:true});
  const write=(file,data)=>{fs.writeFileSync(file,data);return gitBlob(Buffer.from(data));};
  const mk=(name)=>{const p=path.join(toolroot,name);fs.writeFileSync(p,'trusted-test-binary-'+name);return {path:p,sha256:sha(fs.readFileSync(p))};};
  const tools={node:mk('node22'),git:mk('git'),npmCli:mk('npm-cli.js')};
  const entries={};for(let i=0;i<18;i++){
    const name=i===0?'pg':i===1?'typescript':i===2?'@types/node':'lib'+String(i).padStart(2,'0');
    const ver=name==='pg'?'8.23.1':'1.0.0';
    const basename=name.split('/').at(-1);
    entries['node_modules/'+name]={version:ver,resolved:'https://registry.npmjs.org/'+name+'/-/'+basename+'-'+ver+'.tgz',integrity:'sha512-'+Buffer.alloc(64,i+1).toString('base64')};
  }
  entries['node_modules/typescript'].bin={tsc:'bin/tsc',tsserver:'bin/tsserver'};
  const pkg={name:'synthetic-r2',version:'0.1.0',dependencies:{pg:'8.23.1'}};
  const lock={name:'synthetic-r2',version:'0.1.0',lockfileVersion:3,requires:true,packages:{'':{name:'synthetic-r2',version:'0.1.0',dependencies:{pg:'8.23.1'}},...entries}};
  const pfx=path.join(root,'r2-node'),client=path.join(root,'r3-client');
  const sourceBlob=write(path.join(client,'r3-codespaces-locked-npm-v3.cjs'),'// local synthetic runner for fixture\n');
  const pins={anchor:'1c7e819428595558dab146239978349449f482f7',
    lock:write(path.join(pfx,'package-lock.json'),JSON.stringify(lock)),
    pkg:write(path.join(pfx,'package.json'),JSON.stringify(pkg)),
    portable:write(path.join(client,'r3-portable-host-preflight.cjs'),'// synthetic preflight\n'),
    receipt:write(path.join(client,'r3-offline-attempt-v1.cjs'),'// synthetic receipt\n'),pg:'8.23.1'};
  const calls=[];let fail=null,mutation=null,gitCalls=0;
  function spawn(bin,args,opts){calls.push({bin,args});
    if(bin===tools.git.path){
      if(fail==='git')return {status:1,stdout:'',stderr:''};
      if(args[0]==='rev-parse'){gitCalls++;return {status:0,stdout:(args[1]==='HEAD'?SHA:args[1]==='HEAD^{tree}'?TREE:pins.anchor)+'\n',stderr:''};}
      if(args[0]==='merge-base')return {status:0,stdout:pins.anchor+'\n',stderr:''};
      if(args[0]==='diff')return {status:0,stdout:(args[1]==='--name-status'?DELTA.split('\n').map(x=>'A\t'+x).join('\n'):DELTA)+'\n',stderr:''};
      if(args[0]==='status')return {status:0,stdout:mutation==='dirty'?' M dirty':'',stderr:''};
      if(args[0]==='ls-tree')return {status:0,stdout:'100644 blob '+sourceBlob+'\t'+args[4]+'\n',stderr:''};
      return {status:1};
    }
    if(bin===tools.node.path&&args[0]===tools.npmCli.path){
      if(fail==='npm-ci-unknown'&&args[1]==='ci')return {status:null,signal:'SIGTERM',error:new Error('timeout')};
      if(fail==='npm-ci'&&args[1]==='ci')return {status:1,stdout:'',stderr:'some error'};
      if(fail==='npm-ls'&&args[1]==='ls')return {status:1,stdout:'',stderr:''};
      if(args[1]==='ci'){
        fs.mkdirSync(path.join(pfx,'node_modules'));
        for(const [key,val] of Object.entries(entries)){
          const loc=path.join(pfx,key);fs.mkdirSync(loc,{recursive:true});
          fs.writeFileSync(path.join(loc,'package.json'),JSON.stringify({name:key.slice('node_modules/'.length),version:val.version}));
        }
        const hidden={name:lock.name,version:lock.version,lockfileVersion:3,packages:entries};
        fs.writeFileSync(path.join(pfx,'node_modules','.package-lock.json'),JSON.stringify(hidden));
        const bindir=path.join(pfx,'node_modules','.bin');fs.mkdirSync(bindir);
        const tsbin=path.join(pfx,'node_modules','typescript','bin');fs.mkdirSync(tsbin);
        for(const bin of ['tsc','tsserver']){
          fs.writeFileSync(path.join(tsbin,bin),'// synthetic npm executable',{mode:0o755});
          fs.symlinkSync('../typescript/bin/'+bin,path.join(bindir,bin));
        }
        if(mutation==='hidden-missing')fs.unlinkSync(path.join(pfx,'node_modules','.package-lock.json'));
        if(mutation==='hidden-version'){
          hidden.packages['node_modules/pg'].version='999.0.0';
          fs.writeFileSync(path.join(pfx,'node_modules','.package-lock.json'),JSON.stringify(hidden));
        }
        if(mutation==='hidden-extra'){
          hidden.packages['node_modules/ghost']=entries['node_modules/pg'];
          fs.writeFileSync(path.join(pfx,'node_modules','.package-lock.json'),JSON.stringify(hidden));
        }
        // F003 regression: preserve same 18 keys/version/resolved/integrity
        // while forging a graph-bearing metadata field AFTER lock validation.
        if(mutation?.startsWith('hidden-meta-')){
          const pg=hidden.packages['node_modules/pg'];
          const typescript=hidden.packages['node_modules/typescript'];
          switch(mutation){
            case 'hidden-meta-deps': pg.dependencies={malicious:'^999.0.0'};break;
            case 'hidden-meta-optional': pg.optionalDependencies={'pg-cloudflare':'^999.0.0'};break;
            case 'hidden-meta-peer': pg.peerDependencies={'pg-native':'>=999.0.0'};break;
            case 'hidden-meta-peermeta': pg.peerDependenciesMeta={'pg-native':{optional:true}};break;
            case 'hidden-meta-bin': typescript.bin={tsc:'bin/unsafe',tsserver:'bin/tsserver'};break;
            case 'hidden-meta-engines': pg.engines={node:'>= 999.0.0'};break;
            case 'hidden-meta-optionalflag': pg.optional=true;break;
            case 'hidden-meta-license': pg.license='MIT';break;
            case 'hidden-meta-omitbin': delete typescript.bin;break;
            case 'hidden-meta-order':{
              const original=typescript;
              hidden.packages['node_modules/typescript']={integrity:original.integrity,bin:{tsserver:original.bin.tsserver,tsc:original.bin.tsc},resolved:original.resolved,version:original.version};
              break;
            }
            default:throw Error('unrecognized synthetic mutation');
          }
          fs.writeFileSync(path.join(pfx,'node_modules','.package-lock.json'),JSON.stringify(hidden));
        }
        if(mutation==='bin-missing')fs.unlinkSync(path.join(bindir,'tsserver'));
        if(mutation==='bin-target-missing')fs.unlinkSync(path.join(tsbin,'tsc'));
        if(mutation==='bin-not-executable')fs.chmodSync(path.join(tsbin,'tsc'),0o644);
        if(mutation==='extra')fs.mkdirSync(path.join(pfx,'node_modules','ghost'));
        if(mutation==='symlink'){
          fs.rmSync(path.join(pfx,'node_modules','pg'),{recursive:true});
          const elsewhere=path.join(temp,'alien');fs.mkdirSync(elsewhere);fs.writeFileSync(path.join(elsewhere,'package.json'),JSON.stringify({name:'pg',version:'8.23.1'}));
          fs.symlinkSync(elsewhere,path.join(pfx,'node_modules','pg'),'dir');
        }
        if(mutation==='internal-link'){const folder=path.join(pfx,'node_modules','pg','lib');fs.mkdirSync(folder);fs.symlinkSync(path.join(temp,'outside'),path.join(folder,'unsafe'),'file');}
        if(mutation==='bad-bin'){
          fs.unlinkSync(path.join(pfx,'node_modules','.bin','tsc'));
          fs.writeFileSync(path.join(temp,'alien'),'x');fs.symlinkSync(path.join(temp,'alien'),path.join(pfx,'node_modules','.bin','tsc'),'file');
        }
      }
      return {status:0,stdout:'ok',stderr:''};
    }
    if(bin===tools.node.path&&args[0]===path.join(client,'r3-portable-host-preflight.cjs'))return {status:0,stdout:'PASS|TS-R3|PORTABLE_HOST_PREFLIGHT|node=v22.16.0|pg=8.23.1|sources=4|lock=GIT_BLOB_VERIFIED|installed=PACKAGE_METADATA_ONLY|tls=NOT_TESTED|physical=NOT_TESTED\n',stderr:''};
    return {status:1,stdout:'',stderr:''};
  }
  const opt={root,home,tools,nativeNode:tools.node.path,expectedCommit:SHA,expectedTree:TREE,attemptId:ATTEMPT,pins,nodeVersion:'v22.16.0',spawn,env:{PATH:'/some-untrusted-dir',HOME:'/some-secret',NPM_TOKEN:'sensitive'}};
  return {temp,root,home,toolroot,tools,calls,spawn,opt,lock,pkg,entries,pfx,client,pins,
    setFail:x=>fail=x,setMutation:x=>mutation=x,setSource:()=>sourceBlob,
    modifyLock:f=>{f(lock);pins.lock=write(path.join(pfx,'package-lock.json'),JSON.stringify(lock));}};
}
const blocked=(fn,code)=>assert.throws(fn,e=>e instanceof Blocked&&e.code===code);
const npmCalls=f=>f.calls.filter(x=>x.bin===f.tools.node.path&&x.args[0]===f.tools.npmCli.path);
test('1 metadata-only positive, no arbitrary executable path and original durable claim',t=>{const f=fixture(t);const r=run(f.opt);assert.equal(r.status,0);assert.equal(r.result,'PASS_METADATA_ONLY');assert.equal(r.installed,18);assert.deepEqual(npmCalls(f).map(x=>x.args[1]),['ci','ls']);const p=path.join(f.home,'.ts-r3-codespaces-attempts',ATTEMPT);let rec=JSON.parse(fs.readFileSync(path.join(p,'receipt.json')));assert.equal(rec.installed_byte_integrity,'NOT_PROVED');assert.equal(rec.provider_attestation,'NONE');});
test('2 native CLI refuses without provider toolchain binding',()=>{const f=require('node:child_process').spawnSync(process.execPath,[path.join(__dirname,'r3-codespaces-locked-npm-v3.cjs'),ATTEMPT,SHA,TREE],{encoding:'utf8'});assert.equal(f.status,2);assert.match(f.stderr,/TOOLCHAIN_NOT_QUALIFIED/);});
test('3 absent toolchain blocks before Git or filesystem writes',t=>{const f=fixture(t);f.opt.tools=null;blocked(()=>run(f.opt),'TOOLCHAIN_NOT_QUALIFIED');assert.equal(f.calls.length,0);});
test('4 mutated absolute git binary blocks before any network effect',t=>{const f=fixture(t);fs.appendFileSync(f.tools.git.path,'tamper');blocked(()=>run(f.opt),'TOOLCHAIN_HASH_MISMATCH');assert.equal(f.calls.length,0);});
test('5 mutated npm CLI binary blocks before any network effect',t=>{const f=fixture(t);fs.appendFileSync(f.tools.npmCli.path,'tamper');blocked(()=>run(f.opt),'TOOLCHAIN_HASH_MISMATCH');assert.equal(f.calls.length,0);});
test('6 inherited PATH and token never used by child',t=>{const f=fixture(t);let seen=[];f.opt.spawn=(b,a,o)=>{seen.push(o.env);return f.spawn(b,a,o)};run(f.opt);for(const env of seen){assert.notEqual(env.PATH,'/some-untrusted-dir');assert.equal(env.NPM_TOKEN,undefined);assert.notEqual(env.HOME,'/some-secret');}});
test('7 lock wrong SHA512 blocks before any npm spawn or claim',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].integrity='sha512-QQ==';});blocked(()=>run(f.opt),'LOCK_INTEGRITY_INVALID');assert.equal(f.calls.length,0);});
test('8 lock invalid registry redirects block before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].resolved='https://registry.npmjs.org.evil.tld/pg/-/pg-8.23.1.tgz';});blocked(()=>run(f.opt),'LOCK_REGISTRY_INVALID');assert.equal(npmCalls(f).length,0);});
test('9 lock changed package version mismatches before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].version='8.22.0';});blocked(()=>run(f.opt),'LOCK_REGISTRY_INVALID');assert.equal(npmCalls(f).length,0);});
test('10 lock malformed package key blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{const x=l.packages['node_modules/lib03'];delete l.packages['node_modules/lib03'];l.packages['node_modules/../../escape']=x;});blocked(()=>run(f.opt),'LOCK_PATH_INVALID');assert.equal(npmCalls(f).length,0);});
test('11 lock extra 19th package blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/extra']=l.packages['node_modules/lib03'];});blocked(()=>run(f.opt),'LOCK_SHAPE');assert.equal(npmCalls(f).length,0);});
test('12 lock root metadata inconsistent blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages[''].dependencies.pg='3.0.0';});blocked(()=>run(f.opt),'LOCK_SHAPE');assert.equal(npmCalls(f).length,0);});
test('13 parent .npmrc blocks before any Git or npm',t=>{const f=fixture(t);fs.writeFileSync(path.join(f.temp,'.npmrc'),'unsafe');blocked(()=>run(f.opt),'NPM_CONFIG_PRESENT');assert.equal(f.calls.length,0);});
test('14 project .npmrc blocks before npm',t=>{const f=fixture(t);fs.writeFileSync(path.join(f.pfx,'.npmrc'),'unsafe');blocked(()=>run(f.opt),'NPM_CONFIG_PRESENT');assert.equal(f.calls.length,0);});
test('15 inherited database secret variable blocked even empty',t=>{const f=fixture(t);f.opt.env.TS_R3_DATABASE_URL='';blocked(()=>run(f.opt),'SECRET_ENV_PRESENT');assert.equal(f.calls.length,0);});
test('16 git commit mismatch prevents reservation',t=>{const f=fixture(t);f.opt.expectedCommit='f'.repeat(40);blocked(()=>run(f.opt),'GIT_IDENTITY_MISMATCH');assert.equal(npmCalls(f).length,0);});
test('17 unexpected staged or untracked file prevents reservation',t=>{const f=fixture(t);f.setMutation('dirty');blocked(()=>run(f.opt),'GIT_IDENTITY_MISMATCH');assert.equal(npmCalls(f).length,0);});
test('18 duplicate attempt cannot rerun npm',t=>{const f=fixture(t);run(f.opt);const before=npmCalls(f).length;blocked(()=>run(f.opt),'ATTEMPT_ALREADY_EXISTS');assert.equal(npmCalls(f).length,before);});
test('19 crash after durable claim preserves no-replay',t=>{const f=fixture(t);assert.throws(()=>run({...f.opt,onClaim:()=>{throw Error('simulated crash')}}));blocked(()=>run(f.opt),'ATTEMPT_ALREADY_EXISTS');assert.equal(npmCalls(f).length,0);});
test('20 child npm nonzero creates terminal BLOCKED not PASS',t=>{const f=fixture(t);f.setFail('npm-ci');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'NPM_CI_NONZERO_EXIT');});
test('21 child npm uncertain exit preserves effect unknown, no replay',t=>{const f=fixture(t);f.setFail('npm-ci-unknown');const r=run(f.opt);assert.equal(r.failure,'NPM_CI_EFFECT_UNKNOWN');blocked(()=>run(f.opt),'ATTEMPT_ALREADY_EXISTS');});
test('22 npm ls failure blocks without replay',t=>{const f=fixture(t);f.setFail('npm-ls');const r=run(f.opt);assert.equal(r.failure,'NPM_LS_NONZERO_EXIT');});
test('23 unexpected installed package blocked; only metadata proof',t=>{const f=fixture(t);f.setMutation('extra');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'INSTALLED_UNEXPECTED_ENTRY');});
test('24 symlinked installed package rejected',t=>{const f=fixture(t);f.setMutation('symlink');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'PHYSICAL_PATH_REDIRECT');});
test('25 unknown npm binary path blocked',t=>{const f=fixture(t);f.tools.npmCli.path='/usr/bin/false';blocked(()=>run(f.opt),'TOOLCHAIN_HASH_MISMATCH');assert.equal(npmCalls(f).length,0);});
test('26 explicit Node path mismatch fails closed',t=>{const f=fixture(t);f.opt.nativeNode='/nonexistent/node';blocked(()=>run(f.opt),'NODE_EXECUTABLE_MISMATCH');assert.equal(npmCalls(f).length,0);});
test('27 unsupported Node version blocks',t=>{const f=fixture(t);f.opt.nodeVersion='v24.2.0';blocked(()=>run(f.opt),'NODE22_REQUIRED');assert.equal(f.calls.length,0);});
test('28 locked graph contains exactly 18 unique scoped/unscoped entries',t=>{const f=fixture(t);const map=validateLock(f.lock,f.pkg);assert.equal(map.size,18);});
test('29 injected installed graph tamper blocks',t=>{const f=fixture(t);const old=f.spawn;f.opt.spawn=(b,a,o)=>{const r=old(b,a,o);if(b===f.tools.node.path&&a[1]==='ci')fs.writeFileSync(path.join(f.pfx,'node_modules','pg','package.json'),JSON.stringify({name:'pg',version:'8.22.0'}));return r;};const r=run(f.opt);assert.equal(r.failure,'INSTALLED_IDENTITY_MISMATCH');});
test('30 fail closed with unsupported dynamic toolchain keys',t=>{const f=fixture(t);f.tools.extra={path:'x',sha256:'b'.repeat(64)};blocked(()=>run(f.opt),'TOOLCHAIN_NOT_QUALIFIED');assert.equal(f.calls.length,0);});

test('31 unexpected npm bin alias blocked',t=>{const f=fixture(t);f.setMutation('bad-bin');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'INSTALLED_BIN_REDIRECT');});
test('32 symlinked absolute npm CLI rejected before Git or network',t=>{const f=fixture(t);const alt=path.join(f.toolroot,'actual-npm.js');fs.renameSync(f.tools.npmCli.path,alt);fs.symlinkSync(alt,f.tools.npmCli.path);blocked(()=>run(f.opt),'PHYSICAL_PATH_REDIRECT');assert.equal(f.calls.length,0);});
test('33 malformed extra toolchain key blocks before any dispatch',t=>{const f=fixture(t);f.tools.github_token='secret';blocked(()=>run(f.opt),'TOOLCHAIN_NOT_QUALIFIED');assert.equal(f.calls.length,0);});

test('34 symlink inside installed package tree is rejected without claiming byte integrity',t=>{const f=fixture(t);f.setMutation('internal-link');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'INSTALLED_TREE_LINK');});

test('35 lock dependency edge with incompatible version blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].dependencies={'typescript':'^99.0.0'};});blocked(()=>run(f.opt),'LOCK_EDGE_INCOMPATIBLE');assert.equal(npmCalls(f).length,0);});
test('36 unresolvable mandatory dependency blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].dependencies={'absent-package':'^1.0.0'};});blocked(()=>run(f.opt),'LOCK_EDGE_UNRESOLVED');assert.equal(npmCalls(f).length,0);});
test('37 unresolvable mandatory peer dependency blocks before network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].peerDependencies={'not-present':'>=1.0.0'};});blocked(()=>run(f.opt),'LOCK_EDGE_UNRESOLVED');assert.equal(npmCalls(f).length,0);});
test('38 unresolvable optional peer dependency is permitted with explicit metadata',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].peerDependencies={'pg-native':'>=3.0.1'};l.packages['node_modules/pg'].peerDependenciesMeta={'pg-native':{optional:true}};});const r=run(f.opt);assert.equal(r.status,0);});
test('39 unexpected lock link metadata is rejected before npm',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].link=true;});blocked(()=>run(f.opt),'LOCK_ENTRY_FIELDS');assert.equal(npmCalls(f).length,0);});
test('40 unexpected hasInstallScript lock metadata is rejected before npm',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].hasInstallScript=true;});blocked(()=>run(f.opt),'LOCK_ENTRY_FIELDS');assert.equal(npmCalls(f).length,0);});
test('41 unexpected root metadata is rejected before npm',t=>{const f=fixture(t);f.modifyLock(l=>{l.myCustomField=true;});blocked(()=>run(f.opt),'LOCK_FIELDS_INVALID');assert.equal(npmCalls(f).length,0);});
test('42 unexpected bin mapping is rejected before npm',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].bin={malware:'index.js'};});blocked(()=>run(f.opt),'LOCK_BIN_INVALID');assert.equal(npmCalls(f).length,0);});
test('43 missing TypeScript bin mapping is rejected before npm',t=>{const f=fixture(t);f.modifyLock(l=>{delete l.packages['node_modules/typescript'].bin;});blocked(()=>run(f.opt),'LOCK_BIN_INVALID');assert.equal(npmCalls(f).length,0);});
test('44 hidden installed lock with changed package version blocks',t=>{const f=fixture(t);f.setMutation('hidden-version');const r=run(f.opt);assert.equal(r.failure,'HIDDEN_LOCK_INTEGRITY');});
test('45 hidden installed lock with extra package blocks',t=>{const f=fixture(t);f.setMutation('hidden-extra');const r=run(f.opt);assert.equal(r.failure,'HIDDEN_LOCK_GRAPH');});
test('46 missing hidden installed lock blocks',t=>{const f=fixture(t);f.setMutation('hidden-missing');const r=run(f.opt);assert.equal(r.failure,'PHYSICAL_PATH_MISSING');});
test('47 missing TypeScript bin symlink blocks',t=>{const f=fixture(t);f.setMutation('bin-missing');const r=run(f.opt);assert.equal(r.failure,'INSTALLED_UNEXPECTED_BIN');});
test('48 missing TypeScript bin executable target blocks',t=>{const f=fixture(t);f.setMutation('bin-target-missing');const r=run(f.opt);assert.equal(r.failure,'INSTALLED_BIN_REDIRECT');});
test('49 installed hidden lock remains metadata-only',t=>{const f=fixture(t);const r=run(f.opt);assert.equal(r.status,0);const p=path.join(f.home,'.ts-r3-codespaces-attempts',ATTEMPT);const receipt=JSON.parse(fs.readFileSync(path.join(p,'receipt.json')));assert.equal(receipt.installed_byte_integrity,'NOT_PROVED');assert.equal(receipt.provider_attestation,'NONE');});

test('50 non-executable permitted TypeScript bin target blocks metadata PASS',t=>{const f=fixture(t);f.setMutation('bin-not-executable');const r=run(f.opt);assert.equal(r.status,2);assert.equal(r.failure,'INSTALLED_BIN_NOT_EXECUTABLE');});
test('51 optional scoped dependency compatible with locked graph passes pre-network',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].dependencies={'@types/node':'*'};});const r=run(f.opt);assert.equal(r.status,0);});
test('52 invalid engine metadata blocked before any download',t=>{const f=fixture(t);f.modifyLock(l=>{l.packages['node_modules/pg'].engines={node:'>= 16.0.0',os:'evil'};});blocked(()=>run(f.opt),'LOCK_ENGINE_INVALID');assert.equal(npmCalls(f).length,0);});

// IR004 F003: extra hidden lock metadata cannot silently overrule pinned lock.
for(const [number,change] of [
  [53,'hidden-meta-deps'],[54,'hidden-meta-optional'],[55,'hidden-meta-peer'],
  [56,'hidden-meta-peermeta'],[57,'hidden-meta-bin'],[58,'hidden-meta-engines'],
  [59,'hidden-meta-optionalflag'],[60,'hidden-meta-license'],[61,'hidden-meta-omitbin']]){
  test(`${number} IR004 F003 hidden-lock ${change} fails closed with same package identities`,t=>{
    const f=fixture(t);f.setMutation(change);const result=run(f.opt);
    assert.equal(result.status,2);
    assert.equal(result.failure,'HIDDEN_LOCK_METADATA_MISMATCH');
    assert.equal(npmCalls(f).filter(x=>x.args[1]==='ci').length,1);
    const artifact=JSON.parse(fs.readFileSync(path.join(f.home,'.ts-r3-codespaces-attempts',ATTEMPT,'receipt.json')));
    assert.equal(artifact.installed_byte_integrity,'NOT_PROVED');
    assert.equal(artifact.product_effect,'NONE');
    blocked(()=>run(f.opt),'ATTEMPT_ALREADY_EXISTS');
    assert.equal(npmCalls(f).filter(x=>x.args[1]==='ci').length,1);
  });
}
test('62 semantically identical hidden lock with reordered object keys still passes metadata gate',t=>{
  const f=fixture(t);f.setMutation('hidden-meta-order');
  const result=run(f.opt);assert.equal(result.status,0);
  assert.equal(result.result,'PASS_METADATA_ONLY');
});
