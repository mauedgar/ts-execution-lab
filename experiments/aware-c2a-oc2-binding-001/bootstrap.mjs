import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {pathToFileURL, fileURLToPath} from 'node:url';

const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const exact=(actual,expected,name)=>{if(actual!==expected)throw Error(name+'_MISMATCH')};
const noLinks=(p,name)=>{
  if(typeof p!=='string'||!path.isAbsolute(p)||/["'&|;$<>\r\n]/.test(p))throw Error(name+'_UNSAFE');
  const abs=path.resolve(p);
  let dir=path.parse(abs).root;
  for(const piece of abs.slice(dir.length).split(path.sep).filter(Boolean)){
    dir=path.join(dir,piece);
    const stat=fs.lstatSync(dir);
    if(stat.isSymbolicLink())throw Error(name+'_REPARSE_OR_SYMLINK');
    if(fs.realpathSync.native(dir).toLowerCase()!==dir.toLowerCase())throw Error(name+'_CANONICAL_DRIFT');
  }
  return fs.realpathSync.native(abs);
};
const inRoot=(base,p)=>p.toLowerCase().startsWith(base.toLowerCase()+path.sep.toLowerCase());
const appDir=path.dirname(fileURLToPath(import.meta.url));
const self=fileURLToPath(import.meta.url);
function readOnlyRequest(file) {
  const original=JSON.parse(fs.readFileSync(file,'utf8'));
  if(original.schema!=='ts-ee-oc2-c2a-request/v2'||original.product!=='mauedgar/aware-commerce'
    ||original.authority_class!=='SYNTHETIC_NONPRODUCT_ONLY'||original.paid_api_fallback!==false)
    throw Error('BOOTSTRAP_REQUEST_CLASS_DENIED');
  for(const k of ['bootstrap_sha256','runner_sha256','binding_sha256','node_sha256','executable_sha256','git_sha256'])
    if(!/^[0-9a-f]{64}$/.test(original[k]||''))throw Error(k+'_MISSING');
  return original;
}
export async function bootstrap(file,mode) {
  if(!['--run','--observe'].includes(mode))throw Error('COMMAND_MODE_NOT_AUTHORIZED');
  const r=readOnlyRequest(file);
  exact(hash(fs.readFileSync(self)),r.bootstrap_sha256,'BOOTSTRAP_SOURCE');
  const runnerFile=path.join(appDir,'qualify-native.mjs'),bindingFile=path.join(appDir,'binding.mjs');
  exact(hash(fs.readFileSync(runnerFile)),r.runner_sha256,'RUNNER_SOURCE');
  exact(hash(fs.readFileSync(bindingFile)),r.binding_sha256,'BINDING_SOURCE');
  exact(process.version,r.node_version,'NODE_VERSION');
  exact(hash(fs.readFileSync(process.execPath)),r.node_sha256,'NODE_BINARY');
  exact(noLinks(process.execPath,'ACTIVE_NODE_EXECUTABLE').toLowerCase(),noLinks(r.node_executable,'REQUESTED_NODE_EXECUTABLE').toLowerCase(),'NODE_EXECUTABLE');
  exact(os.hostname(),r.expected_host,'HOST_IDENTITY');
  if(process.platform!=='win32')throw Error('HOST_PLATFORM_NOT_WINDOWS');
  if(r.expected_host!=='DESKTOP-DJLBEQH')throw Error('HOST_NOT_QUALIFIED_IN_ORIGINAL_CONTEXT');
  const repo=noLinks(r.repository_root,'REPO');
  const anchor=noLinks(r.scratch_anchor,'SCRATCH_ANCHOR');
  const parent=noLinks(r.scratch_parent,'SCRATCH_PARENT');
  const binary=noLinks(r.opencode_executable,'OPENCODE_BINARY');
  const git=noLinks(r.git_executable,'GIT_BINARY');
  if(!inRoot(anchor,parent)||inRoot(repo,anchor)
    ||inRoot(repo,parent)||inRoot(parent,repo)||repo.toLowerCase()===parent.toLowerCase())
    throw Error('SCRATCH_SCOPE_OR_PRODUCT_OVERLAP');
  if(path.parse(anchor).root.toLowerCase()!==path.parse(parent).root.toLowerCase())
    throw Error('UNEXPECTED_SCRATCH_VOLUME');
  if(path.basename(parent).toLowerCase()!=='ts-ee-oc2-c2a-synthetic')
    throw Error('SCRATCH_PARENT_NOT_QUALIFIED');
  if(!fs.statSync(repo).isDirectory()||!fs.statSync(parent).isDirectory()
    ||!fs.statSync(anchor).isDirectory()||!fs.statSync(binary).isFile()||!fs.statSync(git).isFile())
    throw Error('WRONG_FILE_TYPE');
  exact(hash(fs.readFileSync(binary)),r.executable_sha256,'OPENCODE_BINARY');
  exact(hash(fs.readFileSync(git)),r.git_sha256,'GIT_BINARY');
  const attempt=path.join(parent,r.attempt_id);
  if(mode==='--observe'){
    if(!fs.existsSync(attempt))throw Error('NO_ORIGINAL_ATTEMPT');
    const results={};const corrupt=[];
    for(const key of ['START.json','DISPATCH.json','NATIVE_META.json','RESULT.json']){
      const p=path.join(attempt,key);
      if(!fs.existsSync(p)){results[key]=null;continue}
      try{if(fs.lstatSync(p).isSymbolicLink())throw Error('REPARSE');results[key]=JSON.parse(fs.readFileSync(p,'utf8'))}
      catch{results[key]=null;corrupt.push(key)}
    }
    const start=results['START.json'],end=results['RESULT.json'];
    const same=(x)=>x&&x.attempt_id===r.attempt_id&&x.operation_id===r.operation_id
      &&x.product===r.product&&x.source?.head===r.expected_head&&x.source?.tree===r.expected_tree
      &&x.bundle?.binding===r.binding_sha256&&x.bundle?.runner===r.runner_sha256;
    const valid=start&&same(start)&&end&&same(end)&&end.native_dispatched===Boolean(results['DISPATCH.json']);
    const uncertain=corrupt.length>0||!start||!valid;
    return {mode:'OBSERVE_ONLY',attempt_id:r.attempt_id,operation_id:r.operation_id,
      status:uncertain?'UNKNOWN':end.status,effect_state:uncertain?'UNKNOWN':end.effect_state,
      receipt_exists:Boolean(end),dispatched:Boolean(results['DISPATCH.json']),
      corrupt_files:corrupt,original_start_verified:Boolean(start&&same(start)),
      original_result_verified:Boolean(valid)};
  }
  if(fs.existsSync(attempt))throw Error('ORIGINAL_ATTEMPT_EXISTS_OBSERVE_ONLY');
  const {assertRequest}=await import(pathToFileURL(bindingFile).href);
  assertRequest(r);
  const {execute}=await import(pathToFileURL(runnerFile).href);
  return execute(Object.freeze({request:Object.freeze(r),repo,anchor,parent,binary,git,attempt,
    import_sha256:{bootstrap:r.bootstrap_sha256,runner:r.runner_sha256,binding:r.binding_sha256},
    node_sha256:r.node_sha256,platform:process.platform}));
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===self;
if(invoked){
  if(process.argv.length!==4||!path.isAbsolute(process.argv[2]))throw Error('ABSOLUTE_REQUEST_AND_EXPLICIT_MODE_REQUIRED');
  bootstrap(process.argv[2],process.argv[3]).then(r=>{
    console.log(JSON.stringify(r));if(r?.status==='BLOCKED_PRECONDITION')process.exitCode=20;
  }).catch(e=>{console.error(JSON.stringify({status:'BLOCKED_PRECONDITION',effect_state:'NONE',reason:String(e.message).slice(0,140)}));process.exitCode=22});
}
