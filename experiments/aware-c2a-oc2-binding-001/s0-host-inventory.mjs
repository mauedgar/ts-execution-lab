// TS EE #18 — bounded, read-only, NONPRODUCT S0 host observation.
// No subprocess, no network, no ACL mutation, no Product write, no model run.
// A result is NEVER native admission/authorization. Requires independently
// frozen descriptor and source-hash verification BEFORE any host invocation.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';

const SHA=/^[a-f0-9]{64}$/;
const HEX40=/^[a-f0-9]{40}$/;
const fileKeys=['bootstrap','binding','authority','runner','node','git','opencode'];
const unsafe=s=>typeof s!=='string'||!/^C:\\[^:]*$/i.test(s)||
  /[<>"|?*;\r\n]/.test(s)||s.endsWith(' ')||s.includes('/')||
  s.split('\\').some(part=>part==='.'||part==='..'||part.endsWith(' '));
const normalize=s=>path.win32.normalize(s).toLowerCase();
const within=(root,other)=>normalize(other).startsWith(normalize(root).replace(/\\+$/,'')+'\\');
export function validateInventoryDescriptor(d){
  if(!d||d.schema!=='ts-ee-c2a-s0-host-inventory/v1'
    ||d.kind!=='READ_ONLY_NONPRODUCT_OBSERVATION'
    ||d.product!=='mauedgar/aware-commerce'
    ||d.host!=='DESKTOP-DJLBEQH'
    ||d.authority_class!=='NO_EXECUTION_GRANT'
    ||!HEX40.test(d.source?.commit||'')
    ||!HEX40.test(d.source?.tree||'')
    ||!HEX40.test(d.expected_repo?.head||'')
    ||!HEX40.test(d.expected_repo?.tree||'')
    ||d.expected_repo?.origin!=='https://github.com/mauedgar/aware-commerce.git'
    ||unsafe(d.expected_repo?.root)
    ||unsafe(d.scratch?.anchor)||unsafe(d.scratch?.parent)
    ||normalize(d.scratch.parent)!=='c:\\ts\\station\\ts-ee-oc2-c2a-synthetic'
    ||!within(d.scratch.anchor,d.scratch.parent)
    ||normalize(d.expected_repo.root)===normalize(d.scratch.parent)
    ||within(d.expected_repo.root,d.scratch.parent)
    ||within(d.scratch.parent,d.expected_repo.root))
    throw Error('UNQUALIFIED_INVENTORY_DESCRIPTOR');
  const names=Object.keys(d.files||{});
  if(names.length!==fileKeys.length||names.some(k=>!fileKeys.includes(k)))
    throw Error('INVENTORY_FILE_SET_NOT_EXACT');
  for(const k of fileKeys){
    const item=d.files[k];
    if(unsafe(item?.absolute_path)||!SHA.test(item?.sha256||''))throw Error('UNSAFE_INVENTORY_FILE:'+k);
  }
  return d;
}
function pathEvidence(s){
  const full=path.win32.resolve(s);
  const segments=full.slice(3).split('\\').filter(Boolean);
  let p=full.slice(0,3);
  for(const part of segments){
    p=path.win32.join(p,part);
    const st=fs.lstatSync(p);
    if(st.isSymbolicLink())throw Error('SYMLINK_REPARSE_COMPONENT');
    if(fs.realpathSync.native(p).toLowerCase()!==p.toLowerCase())
      throw Error('PATH_CANONICAL_DRIFT');
  }
  return fs.realpathSync.native(full);
}
export function observeHost(d){
  validateInventoryDescriptor(d);
  const common={
    schema:'ts-ee-c2a-s0-host-inventory-result/v1',
    read_only:true,product_effect:'NONE',model_invoked:false,
    authorization_authenticated:false,
    ntfs_acl_qualified:false,provider_credentials_qualified:false,
    source_anchor_independently_authenticated:false,
    native_admission:false
  };
  if(process.platform!=='win32'||os.hostname()!=='DESKTOP-DJLBEQH')
    return {...common,status:'BLOCKED_PRECONDITION',reason:'WRONG_HOST_OR_PLATFORM'};
  try{
    const anchor=pathEvidence(d.scratch.anchor);
    const repo=pathEvidence(d.expected_repo.root);
    const stat=fs.statSync(repo);
    if(!stat.isDirectory())throw Error('EXPECTED_PRODUCT_REPO_NOT_DIRECTORY');
    const scratch={};
    try{
      const parent=pathEvidence(d.scratch.parent);
      scratch.parent_present=fs.statSync(parent).isDirectory();
      scratch.parent_link_safe=true;
    }catch(e){
      scratch.parent_present=false;
      scratch.parent_link_safe=false;
      scratch.error=e?.code==='ENOENT'?'ABSENT':'UNVERIFIED_OR_UNSAFE';
    }
    const sources={};
    for(const key of fileKeys){
      try{
        const name=pathEvidence(d.files[key].absolute_path);
        const st=fs.lstatSync(name);
        if(!st.isFile()||st.isSymbolicLink())throw Error('NOT_REGULAR');
        const hash=crypto.createHash('sha256').update(fs.readFileSync(name)).digest('hex');
        sources[key]={exists:true,sha256_match:hash===d.files[key].sha256};
      }catch(e){sources[key]={exists:false,sha256_match:false,
        error:e?.code==='ENOENT'?'ABSENT':'UNVERIFIED_OR_UNSAFE'};}
    }
    const complete=scratch.parent_present&&scratch.parent_link_safe
      &&Object.values(sources).every(x=>x.sha256_match);
    return {...common,status:'BLOCKED_PRECONDITION',
      reason:complete?'ACL_PROVIDER_AND_INDEPENDENT_AUTHORITY_NOT_QUALIFIED':'PHYSICAL_FILES_OR_HASHES_NOT_QUALIFIED',
      observations:{host:os.hostname(),repo_directory_present:true,
        scratch_anchor_present:fs.statSync(anchor).isDirectory(),
        scratch,sources},
      note:'No Git commands, no ACL inspection, no OAuth inspection, no model dispatch. Only source/filesystem observations.'};
  }catch(e){
    return {...common,status:'BLOCKED_PRECONDITION',
      reason:'HOST_OBSERVATION_INCOMPLETE',
      detail:['ENOENT','EACCES','EPERM'].includes(e?.code)?e.code:'UNQUALIFIED_PATH_OR_FILE'};
  }
}
// CLI is explicitly read-only. The descriptor is caller-supplied and cannot
// become an independent authority root; the outer runner must pin its SHA.
if(process.argv[1]&&path.resolve(process.argv[1])===path.resolve(fileURLToPath(import.meta.url))){
  if(process.argv.length!==3||!path.isAbsolute(process.argv[2]))
    throw Error('ABSOLUTE_FROZEN_DESCRIPTOR_REQUIRED');
  const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
  console.log(JSON.stringify(observeHost(d)));
}
