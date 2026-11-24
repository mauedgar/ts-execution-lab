// Native Windows adapter fixtures: no historical MAT-XFORM suite replay.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root=path.resolve(process.argv[2]),sha=b=>createHash('sha256').update(b).digest('hex');
const canon=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canon).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canon(v[k])).join(',')+'}';
const write=(p,v)=>fs.writeFileSync(p,canon(v),{flag:'wx'});
const digest=p=>sha(fs.readFileSync(p));
const node=process.execPath,guard=path.join(root,'install','guard.mjs');
const manifest=digest(path.join(root,'manifest.json'));
const acl=process.env.TEST_ROOT_ACL_SHA256;
function prepare(attempt,mutate=(r,g)=>{},rawTransform=s=>s){
 const r={contract_version:'ts-mat-xform-request/v1',request_id:'request-'+attempt,batch_id:'batch-'+attempt,artifacts:[{artifact_id:'one',relative_path:'nested/one.txt',utf8_text:'á\r\n'},{artifact_id:'two',relative_path:'two.txt',utf8_text:'no newline'}]};
 const g={schema:'ts-ee/mat-xform-station-grant/v1',station_root:root,attempt,request_id:r.request_id,batch_id:r.batch_id,manifest_sha256:manifest,node_sha256:digest(node),root_acl_sha256:acl,artifacts:r.artifacts.map(a=>({artifact_id:a.artifact_id,relative_path:a.relative_path,bytes:Buffer.byteLength(a.utf8_text),sha256:sha(Buffer.from(a.utf8_text))}))};
 mutate(r,g);const raw=rawTransform(canon(r));g.carrier_sha256=sha(Buffer.from(raw));g.carrier_bytes=Buffer.byteLength(raw);
 fs.writeFileSync(path.join(root,'inbox',attempt+'.txt'),raw,{flag:'wx'});const gp=path.join(root,'inbox',attempt+'.grant.json');write(gp,g);return digest(gp)
}
function call(a,h){const p=spawnSync('pwsh.exe',['-NoLogo','-NoProfile','-NonInteractive','-File',path.join(root,'install','Invoke-Guard.ps1'),'-Root',root,'-Attempt',a,'-GrantSha256',h,'-Node',node,'-NodeSha256',digest(node),'-GuardSha256',digest(guard)],{encoding:'utf8',timeout:240000,maxBuffer:65536});assert.ifError(p.error);const lines=p.stdout.trim().split(/\r?\n/);return {code:p.status,result:JSON.parse(lines.at(-1)),stderr:p.stderr}}
function deny(name,h,reason){const a=call(name,h);assert.notEqual(a.code,0,JSON.stringify(a));assert.equal(a.result.effect,'NONE',JSON.stringify(a));assert.equal(a.result.reason,reason,JSON.stringify(a));assert.equal(fs.existsSync(path.join(root,'runs',name+'.out')),false);console.log('PASS '+name+' '+reason)}
const a=prepare('positive');const p=call('positive',a);assert.equal(p.code,0,JSON.stringify(p));assert.equal(p.result.status,'PASS');assert.equal(p.result.effect,'CONFIRMED');assert.equal(fs.readFileSync(path.join(root,'runs','positive.out','nested','one.txt'),'utf8'),'á\r\n');assert.equal(fs.readFileSync(path.join(root,'runs','positive.out','two.txt'),'utf8'),'no newline');console.log('PASS positive');
const replay=call('positive',a);assert.notEqual(replay.code,0);assert.equal(replay.result.reason,'ATTEMPT_OCCUPIED');assert.equal(replay.result.effect,'NONE');console.log('PASS collision');
deny('wrong-grant',prepare('wrong-grant').replace(/^./,x=>x==='0'?'1':'0'),'GRANT_HASH_OR_SIZE');
deny('wrong-allowlist',prepare('wrong-allowlist',(r,g)=>g.artifacts[0].sha256='0'.repeat(64)),'ALLOWLIST_MISMATCH');
deny('traversal',prepare('traversal',(r,g)=>{r.artifacts[0].relative_path='../one.txt';g.artifacts[0].relative_path='../one.txt'}),'PATH_DENIED');
deny('duplicate-key',prepare('duplicate-key',undefined,s=>s.replace('"batch_id":','"batch_id":"duplicate","batch_id":')),'NONCANONICAL_JSON');
deny('case-prefix',prepare('case-prefix',(r,g)=>{r.artifacts[1].relative_path='NESTED';g.artifacts[1].relative_path='NESTED'}),'PREFIX_COLLISION');
const h=prepare('tamper');fs.appendFileSync(path.join(root,'inbox','tamper.txt'),'!');deny('tamper',h,'BYTE_LIMIT');
deny('manifest-pin',prepare('manifest-pin',(r,g)=>g.manifest_sha256='0'.repeat(64)),'MANIFEST_HASH');
const q=prepare('untrusted-acl');
const carrier=path.join(root,'inbox','untrusted-acl.txt');
const aclcmd=spawnSync('icacls.exe',[carrier,'/grant','*S-1-1-0:(W)'],{encoding:'utf8'});assert.equal(aclcmd.status,0,aclcmd.stderr);
deny('untrusted-acl',q,'UNTRUSTED_WRITE_ACL');
console.log('STATION_NATIVE_FIXTURES_PASS');
