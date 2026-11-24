// Guarded station adapter; does not replace MAT-XFORM v1.
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const sha=b=>createHash('sha256').update(b).digest('hex');
const fail=code=>{throw new Error(code)};
const ok=(v,c)=>{if(!v)fail(c)};
const exact=(o,keys)=>ok(o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).sort().join('|')===keys.slice().sort().join('|'),'SCHEMA_KEYS');
const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
const hex=x=>typeof x==='string'&&/^[0-9a-f]{64}$/.test(x);
const id=x=>typeof x==='string'&&/^[A-Za-z0-9_-]{1,96}$/.test(x);
function absent(p){try{fs.lstatSync(p);return false}catch(e){if(e.code==='ENOENT')return true;throw e}}
function regular(p){const s=fs.lstatSync(p);ok(s.isFile()&&!s.isSymbolicLink(),'NOT_REGULAR_FILE');return s}
function directory(p){const s=fs.lstatSync(p);ok(s.isDirectory()&&!s.isSymbolicLink(),'NOT_REGULAR_DIRECTORY')}
function read(p,cap){regular(p);const fd=fs.openSync(p,'r');try{const n=fs.fstatSync(fd).size;ok(n<=cap,'BYTE_LIMIT');const b=Buffer.alloc(n);let off=0;while(off<n){const got=fs.readSync(fd,b,off,n-off,null);ok(got>0,'SHORT_READ');off+=got}ok(fs.readSync(fd,Buffer.alloc(1),0,1,null)===0,'FILE_GREW');return b}finally{fs.closeSync(fd)}}
function decode(b){return new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(b)}
function parse(b){const s=decode(b),o=JSON.parse(s);ok(canonical(o)===s,'NONCANONICAL_JSON');return o}
function rel(p){ok(typeof p==='string'&&p.length<=200,'PATH_LENGTH');for(const x of p.split('/'))ok(/^[A-Za-z0-9_-][A-Za-z0-9_.-]{0,63}$/.test(x)&&!/[.]$/.test(x)&&!/^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(x),'PATH_DENIED');return p}
function manifestRel(p){ok(typeof p==='string'&&p.length<=250&&!p.includes('\\')&&!p.includes(':')&&!p.split('/').some(x=>!x||x==='.'||x==='..'||/[ .]$/.test(x)),'MANIFEST_PATH_DENIED');return p}
function inventory(root){const files=[];let entries=0;function walk(dir,prefix){directory(dir);for(const name of fs.readdirSync(dir)){ok(++entries<=6000,'INVENTORY_LIMIT');const p=path.join(dir,name),r=prefix+name,s=fs.lstatSync(p);ok(!s.isSymbolicLink(),'INSTALL_LINK');if(s.isDirectory())walk(p,r+'/');else{ok(s.isFile(),'INSTALL_SPECIAL');files.push(r)}}}walk(root,'');return files.sort()}
function checkInstall(root,expectedHash){const b=read(path.join(root,'manifest.json'),2*1024*1024);ok(sha(b)===expectedHash,'MANIFEST_HASH');const m=parse(b);exact(m,['schema','files']);ok(m.schema==='ts-ee/mat-xform-install/v1'&&Array.isArray(m.files)&&m.files.length>0&&m.files.length<=6000,'MANIFEST_SCHEMA');const names=[];const seen=new Set();let total=0;for(const f of m.files){exact(f,['path','bytes','sha256']);const p=manifestRel(f.path);ok(!seen.has(p.toLowerCase()),'MANIFEST_DUPLICATE');seen.add(p.toLowerCase());ok(Number.isSafeInteger(f.bytes)&&f.bytes>=0&&f.bytes<=4*1024*1024&&hex(f.sha256),'MANIFEST_ENTRY');total+=f.bytes;ok(total<=64*1024*1024,'INSTALL_TOTAL_LIMIT');const a=read(path.join(root,'install',...p.split('/')),f.bytes);ok(a.length===f.bytes&&sha(a)===f.sha256,'INSTALL_HASH');names.push(p)}ok(JSON.stringify(names.sort())===JSON.stringify(inventory(path.join(root,'install'))),'INSTALL_INVENTORY');for(const p of ['guard.mjs','Invoke-Guard.ps1','package.json','package-lock.json','src/mat-xform/cli.ts','src/mat-xform/contracts.ts','src/mat-xform/materializer.ts','node_modules/zod/package.json'])ok(seen.has(p.toLowerCase()),'INSTALL_REQUIRED')}
function checkReceipt(value,g,out,identity){ok(value.request_identity==='sha256:'+identity&&value.request_id===g.request_id&&value.batch_id===g.batch_id&&value.result_status==='PASS'&&value.effect_state==='CONFIRMED','RECEIPT_IDENTITY');ok(Array.isArray(value.artifacts)&&value.artifacts.length===g.artifacts.length,'RECEIPT_COUNT');const actual=new Map(value.artifacts.map(a=>[a.artifact_id,a]));ok(actual.size===g.artifacts.length,'RECEIPT_DUPLICATE');for(const a of g.artifacts){const f=actual.get(a.artifact_id);ok(f&&f.relative_path===a.relative_path&&f.bytes===a.bytes&&f.sha256==='sha256:'+a.sha256,'RECEIPT_ARTIFACT');const b=read(path.join(out,...a.relative_path.split('/')),a.bytes);ok(b.length===a.bytes&&sha(b)===a.sha256,'OUTPUT_HASH')}}
let started=false;
try{
 const [rootArg,attempt,grantHash,...extra]=process.argv.slice(2);
 ok(process.platform==='win32','WINDOWS_ONLY');ok(extra.length===0&&id(attempt)&&hex(grantHash)&&typeof rootArg==='string'&&path.isAbsolute(rootArg)&&!rootArg.startsWith('\\\\'),'ARGUMENTS');
 const root=path.resolve(rootArg);ok(root===rootArg,'ROOT_NOT_CANONICAL');directory(root);directory(path.join(root,'inbox'));directory(path.join(root,'runs'));
 const grantPath=path.join(root,'inbox',attempt+'.grant.json'),carrier=path.join(root,'inbox',attempt+'.txt');
 const gb=read(grantPath,32768);ok(sha(gb)===grantHash,'GRANT_HASH');const g=parse(gb);
 exact(g,['schema','station_root','attempt','request_id','batch_id','carrier_bytes','carrier_sha256','manifest_sha256','node_sha256','root_acl_sha256','artifacts']);
 ok(g.schema==='ts-ee/mat-xform-station-grant/v1'&&g.station_root===root&&g.attempt===attempt&&id(g.request_id)&&id(g.batch_id)&&hex(g.carrier_sha256)&&hex(g.manifest_sha256)&&hex(g.node_sha256)&&hex(g.root_acl_sha256),'GRANT_IDENTITY');
 ok(sha(read(process.execPath,128*1024*1024))===g.node_sha256&&process.version==='v22.23.3','NODE_BINDING');
 checkInstall(root,g.manifest_sha256);
 ok(Number.isSafeInteger(g.carrier_bytes)&&g.carrier_bytes>0&&g.carrier_bytes<=65536,'CARRIER_LIMIT');
 const rb=read(carrier,g.carrier_bytes);ok(rb.length===g.carrier_bytes&&sha(rb)===g.carrier_sha256,'CARRIER_HASH');const r=parse(rb);
 exact(r,['contract_version','request_id','batch_id','artifacts']);ok(r.contract_version==='ts-mat-xform-request/v1'&&r.request_id===g.request_id&&r.batch_id===g.batch_id,'REQUEST_IDENTITY');
 ok(Array.isArray(r.artifacts)&&Array.isArray(g.artifacts)&&r.artifacts.length===g.artifacts.length&&r.artifacts.length>=1&&r.artifacts.length<=16,'ARTIFACT_LIMIT');
 const ids=new Set(),paths=new Set();let total=0;
 for(let i=0;i<r.artifacts.length;i++){const a=r.artifacts[i],p=g.artifacts[i];exact(a,['artifact_id','relative_path','utf8_text']);exact(p,['artifact_id','relative_path','bytes','sha256']);const rp=rel(a.relative_path),key=rp.toLowerCase();ok(id(a.artifact_id)&&!ids.has(a.artifact_id)&&!paths.has(key),'ARTIFACT_DUPLICATE');ids.add(a.artifact_id);for(const other of paths)ok(!key.startsWith(other+'/')&&!other.startsWith(key+'/'),'PREFIX_COLLISION');paths.add(key);ok(typeof a.utf8_text==='string','ARTIFACT_TEXT');const b=Buffer.from(a.utf8_text,'utf8');ok(b.toString('utf8')===a.utf8_text,'INVALID_UNICODE');total+=b.length;ok(total<=49152,'PAYLOAD_LIMIT');ok(p.artifact_id===a.artifact_id&&p.relative_path===rp&&p.bytes===b.length&&p.sha256===sha(b),'ALLOWLIST_MISMATCH')}
 const identity=sha(Buffer.from(canonical(r))),out=path.join(root,'runs',attempt+'.out'),result=path.join(root,'runs',attempt+'.result.json'),receipt=path.join(root,'runs',attempt+'.receipt.json'),stage=out+'.staging-'+identity;
 for(const p of [out,result,receipt,stage])ok(absent(p),'ATTEMPT_OCCUPIED');
 const env={SystemRoot:process.env.SystemRoot||'C:\\Windows',WINDIR:process.env.WINDIR||'C:\\Windows',NODE_NO_WARNINGS:'1'};
 started=true;
 const child=spawnSync(process.execPath,['--experimental-strip-types',path.join(root,'install','src','mat-xform','cli.ts'),'materialize',carrier,'--out',out,'--result',result,'--receipt',receipt,'--binding','mat-xform://station/v1'],{cwd:path.join(root,'install'),env,encoding:'utf8',timeout:20000,maxBuffer:65536,windowsHide:true});
 ok(!child.error&&child.status===0,'CHILD_NOT_SUCCESS');directory(out);
 const resultBytes=read(result,65536),receiptBytes=read(receipt,65536),rr=JSON.parse(decode(resultBytes)),cc=JSON.parse(decode(receiptBytes));
 checkReceipt(rr,g,out,identity);checkReceipt(cc,g,out,identity);
 ok(rr.artifact_count===g.artifacts.length&&rr.contract_version==='ts-mat-xform-result/v1'&&cc.contract_version==='ts-mat-xform-receipt/v1'&&cc.output_root===out&&cc.selected_binding_ref==='mat-xform://station/v1'&&cc.authority_created===false&&cc.Product_effect==='NONE','RESULT_CONTRACT');
 ok(JSON.stringify(inventory(out))===JSON.stringify(g.artifacts.map(a=>a.relative_path).sort()),'OUTPUT_INVENTORY');
 ok(absent(stage),'STAGING_REMAINS');
 console.log(JSON.stringify({schema:'ts-ee/mat-xform-station-terminal/v1',attempt,status:'PASS',effect:'CONFIRMED',grant_sha256:grantHash,carrier_sha256:g.carrier_sha256,request_identity:'sha256:'+identity,result_sha256:sha(resultBytes),receipt_sha256:sha(receiptBytes),artifact_count:g.artifacts.length,Product_effect:'NONE'}));
}catch(e){console.log(JSON.stringify({schema:'ts-ee/mat-xform-station-terminal/v1',attempt:process.argv[3]??null,status:started?'UNAVAILABLE':'BLOCKED_PRECONDITION',effect:started?'UNKNOWN':'NONE',reason:String(e.message).slice(0,240),Product_effect:'NONE'}));process.exitCode=1}
