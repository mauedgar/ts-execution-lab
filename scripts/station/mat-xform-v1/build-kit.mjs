// Build on an owner-controlled source/build surface, never in Commander.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const sha=b=>createHash('sha256').update(b).digest('hex');
const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
const [target,...extra]=process.argv.slice(2);
if(!target||extra.length||process.version!=='v22.23.3')throw Error('ARGUMENTS_OR_NODE');
const root=path.resolve(target);fs.mkdirSync(root);const install=path.join(root,'install');fs.mkdirSync(install);
const from=path.resolve(import.meta.dirname,'../../..');
for(const p of ['package.json','package-lock.json','src/mat-xform/cli.ts','src/mat-xform/contracts.ts','src/mat-xform/materializer.ts']){const dst=path.join(install,...p.split('/'));fs.mkdirSync(path.dirname(dst),{recursive:true});fs.copyFileSync(path.join(from,...p.split('/')),dst,fs.constants.COPYFILE_EXCL)}
for(const p of ['guard.mjs','Invoke-Guard.ps1'])fs.copyFileSync(path.join(import.meta.dirname,p),path.join(install,p),fs.constants.COPYFILE_EXCL);
const zod=path.join(from,'node_modules','zod');if(JSON.parse(fs.readFileSync(path.join(zod,'package.json'),'utf8')).version!=='4.1.11')throw Error('ZOD_VERSION');
function copyDir(src,dst){const st=fs.lstatSync(src);if(!st.isDirectory()||st.isSymbolicLink())throw Error('PACKAGE_LINK');fs.mkdirSync(dst);for(const n of fs.readdirSync(src)){const a=path.join(src,n),b=path.join(dst,n),s=fs.lstatSync(a);if(s.isDirectory())copyDir(a,b);else if(s.isFile()&&!s.isSymbolicLink())fs.copyFileSync(a,b,fs.constants.COPYFILE_EXCL);else throw Error('PACKAGE_SPECIAL')}}
fs.mkdirSync(path.join(install,'node_modules'));copyDir(zod,path.join(install,'node_modules','zod'));
const files=[];function scan(p,prefix){for(const n of fs.readdirSync(p)){const a=path.join(p,n),rel=prefix+n,s=fs.lstatSync(a);if(s.isDirectory())scan(a,rel+'/');else{const b=fs.readFileSync(a);files.push({path:rel,bytes:b.length,sha256:sha(b)})}}}scan(install,'');files.sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0);
const m=canonical({schema:'ts-ee/mat-xform-install/v1',files});fs.writeFileSync(path.join(root,'manifest.json'),m,{flag:'wx'});
fs.mkdirSync(path.join(root,'inbox'));fs.mkdirSync(path.join(root,'runs'));fs.mkdirSync(path.join(root,'runtime'));
const gitBlob=b=>createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const sourceMap=[];
for(const p of ['guard.mjs','Invoke-Guard.ps1','package.json','package-lock.json','src/mat-xform/cli.ts','src/mat-xform/contracts.ts','src/mat-xform/materializer.ts']){
 const gitPath=['guard.mjs','Invoke-Guard.ps1'].includes(p)?'scripts/station/mat-xform-v1/'+p:p;
 const expected=execFileSync('git',['rev-parse','HEAD:'+gitPath],{cwd:from,encoding:'utf8'}).trim();
 const raw=fs.readFileSync(path.join(install,...p.split('/'))),lf=Buffer.from(new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw).replace(/\r\n/g,'\n'),'utf8');
 const form=gitBlob(raw)===expected?'RAW':gitBlob(lf)===expected?'CRLF_TO_LF':null;
 if(!form)throw Error('SOURCE_KIT_BLOB_MISMATCH_'+p);
 sourceMap.push({path:p,git_path:gitPath,git_blob:expected,installed_sha256:sha(raw),installed_bytes:raw.length,eol_correspondence:form});
}
console.log(JSON.stringify({schema:'ts-ee/mat-xform-kit/v1',source_map:sourceMap,manifest_sha256:sha(Buffer.from(m)),files:files.length,bytes:files.reduce((n,x)=>n+x.bytes,0),guard_sha256:sha(fs.readFileSync(path.join(install,'guard.mjs'))),entry_sha256:sha(fs.readFileSync(path.join(install,'Invoke-Guard.ps1'))),Product_effect:'NONE'}));
