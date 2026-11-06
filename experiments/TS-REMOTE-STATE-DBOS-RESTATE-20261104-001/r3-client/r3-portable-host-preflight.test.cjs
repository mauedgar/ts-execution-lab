'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {spawnSync} = require('node:child_process');
const {assess, gitBlob} = require('./r3-portable-host-preflight.cjs');

function fixture(t) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-r3-preflight-'));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  const root = path.join(temp, 'r3-client'), prefix = path.join(temp, 'r2-node');
  fs.mkdirSync(root); fs.mkdirSync(path.join(prefix, 'node_modules', 'pg'), {recursive:true});
  const write = (p, value) => { const buf = Buffer.from(value); fs.writeFileSync(p,buf); return gitBlob(buf); };
  const sources = Object.fromEntries([
    'r3-command-core.cjs','physical-host-p01-p04-v2.cjs',
    'r3-command-core.test.cjs','physical-host-p01-p04-v2.test.cjs'
  ].map((name, index) => [name, write(path.join(root,name), 'module.exports='+index+';\n')]));
  const pkg = {name:'ts-remote-state-r2-node',dependencies:{pg:'8.23.1'}};
  const lock = {lockfileVersion:3,packages:{'':{dependencies:{pg:'8.23.1'}},'node_modules/pg':{version:'8.23.1',integrity:'sha512-'+Buffer.alloc(64,1).toString('base64')}}};
  const pkgSha = write(path.join(prefix,'package.json'),JSON.stringify(pkg));
  const lockSha = write(path.join(prefix,'package-lock.json'),JSON.stringify(lock));
  write(path.join(prefix,'node_modules','pg','package.json'),JSON.stringify({name:'pg',version:'8.23.1'}));
  return {root,prefix,sources,pkgSha,lockSha,pgVersion:'8.23.1',nodeVersion:'v22.16.0',argvCount:2,sensitiveEnvPresent:false};
}
function blocked(args, code) { assert.throws(() => assess(args), e => e.code===code); }
test('positive metadata-only contract', t => {
  const x = assess(fixture(t));
  assert.equal(x.status,'READY_METADATA_ONLY');
  assert.equal(x.installed,'PACKAGE_METADATA_ONLY');
  assert.equal(x.sourceCount,4);
  assert.equal(x.tls,'NOT_TESTED');
});
test('different compatible Node22 patch allowed', t => {
  const f=fixture(t); f.nodeVersion='v22.23.3'; assert.equal(assess(f).node,'v22.23.3');
});
test('wrong Node fails', t => {const f=fixture(t);f.nodeVersion='v24.1.0';blocked(f,'NODE22_REQUIRED');});
test('extra args fail', t => {const f=fixture(t);f.argvCount=3;blocked(f,'ARGS_NOT_ALLOWED');});
test('sensitive environment fails without reading value', t => {const f=fixture(t);f.sensitiveEnvPresent=true;blocked(f,'SECRET_ENV_PRESENT');});
test('tampered candidate fails before pg checks', t => {const f=fixture(t);fs.appendFileSync(path.join(f.root,'r3-command-core.cjs'),'!');blocked(f,'SOURCE_HASH_MISMATCH');});
test('missing source fails', t => {const f=fixture(t);fs.unlinkSync(path.join(f.root,'r3-command-core.cjs'));blocked(f,'FILE_UNAVAILABLE');});
test('symlink source fails', t => {const f=fixture(t);fs.renameSync(path.join(f.root,'r3-command-core.cjs'),path.join(f.root,'r3-command-core-real.cjs'));fs.symlinkSync('r3-command-core-real.cjs',path.join(f.root,'r3-command-core.cjs'));blocked(f,'PATH_REDIRECT');});
test('tampered package lock fails', t => {const f=fixture(t);fs.appendFileSync(path.join(f.prefix,'package-lock.json'),' ');blocked(f,'SOURCE_HASH_MISMATCH');});
test('mismatched installed pg version fails', t => {const f=fixture(t);fs.writeFileSync(path.join(f.prefix,'node_modules','pg','package.json'),JSON.stringify({name:'pg',version:'8.22.0'}));blocked(f,'PG_METADATA_MISMATCH');});
test('missing pg package fails', t => {const f=fixture(t);fs.unlinkSync(path.join(f.prefix,'node_modules','pg','package.json'));blocked(f,'FILE_UNAVAILABLE');});
test('no credentials or stack output on native CLI block', () => {
  const p=spawnSync(process.execPath,[path.join(__dirname,'r3-portable-host-preflight.cjs'),'EXTRA'],{encoding:'utf8',env:{...process.env,TS_R3_DATABASE_URL:'sensitive-test-sentinel'}});
  assert.equal(p.status,2);assert.match(p.stderr,/ARGS_NOT_ALLOWED/);assert.doesNotMatch(p.stderr,/sensitive-test-sentinel|Error:| at /);
});

test('source parent directory symlink or Windows junction fails', t => {
  const f=fixture(t),real=f.root+'-real';
  fs.renameSync(f.root,real);
  fs.symlinkSync(real,f.root,process.platform==='win32'?'junction':'dir');
  blocked(f,'PATH_REDIRECT');
});
test('dependency parent directory redirect fails', t => {
  const f=fixture(t),real=f.prefix+'-real';
  fs.renameSync(f.prefix,real);
  fs.symlinkSync(real,f.prefix,process.platform==='win32'?'junction':'dir');
  blocked(f,'PATH_REDIRECT');
});
test('pg module directory redirect fails', t => {
  const f=fixture(t),folder=path.join(f.prefix,'node_modules','pg'),real=folder+'-real';
  fs.renameSync(folder,real);
  fs.symlinkSync(real,folder,process.platform==='win32'?'junction':'dir');
  blocked(f,'PATH_REDIRECT');
});
test('installed pg package.json symbolic link fails', t => {
  const f=fixture(t),file=path.join(f.prefix,'node_modules','pg','package.json');
  fs.renameSync(file,file+'.real');fs.symlinkSync('package.json.real',file);
  blocked(f,'PATH_REDIRECT');
});
test('tampered pinned package.json fails', t => {
  const f=fixture(t);fs.appendFileSync(path.join(f.prefix,'package.json'),' ');
  blocked(f,'SOURCE_HASH_MISMATCH');
});
test('invalid package JSON fails with bounded reason', t => {
  const f=fixture(t),file=path.join(f.prefix,'package.json');
  fs.writeFileSync(file,'{not json');f.pkgSha=gitBlob(fs.readFileSync(file));
  blocked(f,'INVALID_METADATA');
});
test('lock JSON metadata invalid fails with bounded reason', t => {
  const f=fixture(t),file=path.join(f.prefix,'package-lock.json');
  fs.writeFileSync(file,JSON.stringify({lockfileVersion:3,packages:{}}));
  f.lockSha=gitBlob(fs.readFileSync(file));
  blocked(f,'LOCK_INVALID');
});
test('installed pg content tamper retains metadata-only ceiling', t => {
  const f=fixture(t),file=path.join(f.prefix,'node_modules','pg','index.js');
  fs.writeFileSync(file,'/* deliberately unverified module bytes */');
  const x=assess(f);
  assert.equal(x.installed,'PACKAGE_METADATA_ONLY');
  assert.equal(x.tls,'NOT_TESTED');
});
test('native CLI secret presence alone fails even if value is empty', () => {
  const p=spawnSync(process.execPath,[path.join(__dirname,'r3-portable-host-preflight.cjs')],
    {encoding:'utf8',env:{...process.env,TS_R3_DATABASE_URL:''}});
  assert.equal(p.status,2);
  assert.match(p.stderr,/SECRET_ENV_PRESENT/);
  assert.doesNotMatch(p.stderr,/Error:| at |postgres/);
});
