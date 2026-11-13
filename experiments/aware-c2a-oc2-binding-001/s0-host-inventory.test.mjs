import test from 'node:test';
import assert from 'node:assert/strict';
import {validateInventoryDescriptor,observeHost} from './s0-host-inventory.mjs';

const files=Object.fromEntries(
  ['bootstrap','binding','authority','runner','node','git','opencode'].map((key,i)=>
    [key,{absolute_path:'C:\\TS\\readonly\\'+key+'.exe',sha256:String(i).repeat(64)}])
);
const good={
  schema:'ts-ee-c2a-s0-host-inventory/v1',
  kind:'READ_ONLY_NONPRODUCT_OBSERVATION',product:'mauedgar/aware-commerce',
  host:'DESKTOP-DJLBEQH',authority_class:'NO_EXECUTION_GRANT',
  source:{commit:'a'.repeat(40),tree:'b'.repeat(40)},
  expected_repo:{head:'c'.repeat(40),tree:'d'.repeat(40),
    origin:'https://github.com/mauedgar/aware-commerce.git',
    root:'C:\\Users\\Mauri\\orca\\workspaces\\aware-commerce-p0-20261109-001\\aware-p0-repair-001'},
  scratch:{anchor:'C:\\TS\\station',parent:'C:\\TS\\station\\ts-ee-oc2-c2a-synthetic'},
  files
};
const copy=()=>structuredClone(good);
test('exact non-executable, non-Product descriptor is syntactically accepted',()=>{
  assert.equal(validateInventoryDescriptor(copy()).kind,'READ_ONLY_NONPRODUCT_OBSERVATION');
});
test('arbitrary repository, origin, host or scope cannot pass descriptor validation',()=>{
  for(const edit of [
    x=>{x.product='mauedgar/tecnotron-ai'},
    x=>{x.host='DESKTOP-OTHER'},
    x=>{x.authority_class='PRODUCT_WRITE_GRANTED'},
    x=>{x.expected_repo.origin='https://github.com/untrusted/repo.git'},
    x=>{x.expected_repo.head='z'.repeat(40)},
    x=>{x.source.tree='f'.repeat(39)},
    x=>{x.scratch.parent='C:\\TS\\station\\other'},
    x=>{x.expected_repo.root=x.scratch.parent},
    x=>{x.kind='RUN_MODEL'},
  ]){const x=copy();edit(x);assert.throws(()=>validateInventoryDescriptor(x))}
});
test('path escapes and unexpected files fail closed before any filesystem access',()=>{
  for(const edit of [
    x=>{x.files.git.absolute_path='C:\\TS\\station\\..\\other.exe'},
    x=>{x.files.node.absolute_path='C:\\TS\\station\\node.exe"'},
    x=>{x.files.runner.absolute_path='C:/temp/runner.exe'},
    x=>{x.files.bootstrap.absolute_path='\\\\server\\share\\bootstrap.mjs'},
    x=>{x.files.opencode.absolute_path='C:\\TS\\one:ads'},
    x=>{delete x.files.git},
    x=>{x.files.extra={absolute_path:'C:\\TS\\file.exe',sha256:'a'.repeat(64)}},
    x=>{x.files.authority.sha256='a'.repeat(63)},
  ]){const x=copy();edit(x);assert.throws(()=>validateInventoryDescriptor(x))}
});
test('CI/Linux host observation returns BLOCKED/NONE, not a fictional PASS',()=>{
  if(process.platform==='win32')return;
  const r=observeHost(copy());
  assert.equal(r.status,'BLOCKED_PRECONDITION');
  assert.equal(r.reason,'WRONG_HOST_OR_PLATFORM');
  assert.equal(r.product_effect,'NONE');
  assert.equal(r.read_only,true);
  assert.equal(r.model_invoked,false);
  assert.equal(r.authorization_authenticated,false);
  assert.equal(r.native_admission,false);
});
test('readonly inventory source does not import process launch/network facilities',async()=>{
  const fs=await import('node:fs');
  const src=fs.readFileSync(new URL('./s0-host-inventory.mjs',import.meta.url),'utf8');
  for(const forbidden of [
    "from 'node:child_process'",'spawnSync(', 'execSync(', 'spawn(', 'exec(',
    'fetch(', 'fs.writeFile','fs.mkdir','fs.rmSync','fs.rename', 'newJSON(',
  ])assert.equal(src.includes(forbidden),false,forbidden);
  assert.ok(src.includes('native_admission:false'));
});
