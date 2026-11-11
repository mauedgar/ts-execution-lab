import path from 'node:path';

const HEX40=/^[0-9a-f]{40}$/, HEX64=/^[0-9a-f]{64}$/;
const ID=/^[A-Za-z][A-Za-z0-9_-]{7,100}$/;
const BAD=/["'&|;$<>\r\n]/;
const good=(x,re)=>typeof x==='string'&&re.test(x);
export const VERSION='ts-ee-oc2-c2a-request/v2';
export function assertRequest(r){
  if(r?.schema!==VERSION||r?.product!=='mauedgar/aware-commerce'||r?.authority_class!=='SYNTHETIC_NONPRODUCT_ONLY'
    ||r?.paid_api_fallback!==false||!good(r.operation_id,ID)||!good(r.attempt_id,ID)
    ||!good(r.expected_head,HEX40)||!good(r.expected_tree,HEX40)
    ||!good(r.executable_sha256,HEX64)||!good(r.git_sha256,HEX64)||!good(r.bootstrap_sha256,HEX64)
    ||!good(r.runner_sha256,HEX64)||!good(r.binding_sha256,HEX64)
    ||!good(r.node_sha256,HEX64)||!/^v22\.[0-9]+\.[0-9]+$/.test(r.node_version||'')
    ||!/^opencode v2\.[0-9]+\.[0-9]+$/.test(r.expected_version||'')
    ||!good(r.expected_host,ID)||!good(r.agent,ID)
    ||!/^openai\/[a-z0-9._-]+$/.test(r.model||'')
    ||!good(r.authorization_receipt_sha256,HEX64)
    ||typeof r.authorization_receipt_ref!=='string'||!/^https:\/\/github\.com\/mauedgar\/ts-execution-lab\/issues\/18#issuecomment-[0-9]+$/.test(r.authorization_receipt_ref))
    throw Error('REQUEST_IDENTITY_OR_AUTHORITY_INCOMPLETE');
  if(!['https://github.com/mauedgar/aware-commerce.git','git@github.com:mauedgar/aware-commerce.git'].includes(r.expected_origin))throw Error('WRONG_ORIGIN');
  for(const k of ['repository_root','scratch_anchor','scratch_parent','opencode_executable','git_executable','node_executable']){
    if(typeof r[k]!=='string'||!path.isAbsolute(r[k])||BAD.test(r[k]))throw Error('UNSAFE_PATH:'+k);
  }
  return r;
}
export function gitCommands(gitExecutable,root){
  if(!path.isAbsolute(root)||!path.isAbsolute(gitExecutable)||BAD.test(root)||BAD.test(gitExecutable))throw Error('UNSAFE_GIT_COMMAND_PATH');
  return ['"'+gitExecutable+'" -C "'+root+'" rev-parse HEAD','"'+gitExecutable+'" -C "'+root+'" rev-parse HEAD^{tree}'];
}
export function makePolicy(agent,absoluteAllow,commands){
  if(!good(agent,ID)||path.basename(absoluteAllow)!=='ALLOW_ONLY.txt'||!Array.isArray(commands)||commands.length!==2)throw Error('UNSAFE_POLICY_INPUT');
  const rules=[{action:'*',resource:'*',effect:'deny'}];
  for(const resource of commands)rules.push({action:'shell',resource,effect:'allow'});
  for(const a of ['edit','write','patch'])for(const resource of [absoluteAllow,'ALLOW_ONLY.txt'])
    rules.push({action:a,resource,effect:'allow'});
  return {permissions:[{action:'*',resource:'*',effect:'deny'}],agents:{[agent]:{mode:'primary',permissions:rules}},plugin:[]};
}
export function checkEffective(agents,agent,policy){
  const v=Array.isArray(agents)?agents.find(x=>x.id===agent):null;
  if(!v||!Array.isArray(v.permissions))throw Error('EFFECTIVE_AGENT_UNAVAILABLE');
  const expected=policy.agents[agent].permissions;
  const matches=(x,y)=>x.action===y.action&&x.resource===y.resource&&x.effect===y.effect;
  for(const r of expected)if(!v.permissions.some(x=>matches(x,r)))throw Error('REQUIRED_NATIVE_PERMISSION_MISSING');
  for(const r of v.permissions)if(r.effect==='allow'&&!expected.some(x=>matches(x,r)))throw Error('UNEXPECTED_EFFECTIVE_ALLOW:'+String(r.action));
  if(v.permissions.filter(x=>x.action==='*'&&x.resource==='*'&&x.effect==='deny').length!==1)throw Error('DENY_ALL_NOT_UNIQUE');
  return true;
}
const patchPath=(t)=>{
  if(typeof t!=='string')return null;
  const m=t.match(/^\*\*\* Begin Patch\r?\n\*\*\* Add File: ([^\r\n]+)\r?\n\+([^\r\n]+)\r?\n\*\*\* End Patch\s*$/);
  return m?{path:m[1],body:m[2]}:null;
};
export function inspectEvents(jsonl,{commands,allowedFile,forbiddenFile,head,tree}){
  const state={events:0,tools:0,session:null,terminal:false,steps:0,errors:[],sequence:[],tool_calls:[],complete:false};
  const callIDs=new Set(),seenPartIDs=new Set();
  let lastWasTerminal=false;
  for(const line of String(jsonl).split(/\r?\n/)){
    if(!line.trim())continue;
    let e;try{e=JSON.parse(line)}catch{state.errors.push('MALFORMED_JSONL');continue}
    state.events++;
    const session=e?.sessionID;
    if(typeof session!=='string'||!/^ses_[A-Za-z0-9]+$/.test(session)){state.errors.push('SESSION_MISSING');continue}
    if(state.session && session!==state.session)state.errors.push('CROSS_SESSION_EVENT');
    state.session ||= session;
    const part=e.part||{};
    if(typeof part.id!=='string'||seenPartIDs.has(part.id))state.errors.push('PART_ID_MISSING_OR_DUPLICATE');
    else seenPartIDs.add(part.id);
    if(e.type==='step_start'&&part.type==='step-start'){state.steps++;lastWasTerminal=false;continue}
    if(e.type==='step_finish'&&part.type==='step-finish'){state.terminal=true;lastWasTerminal=true;continue}
    if(e.type==='text'&&part.type==='text'){lastWasTerminal=false;continue}
    if(e.type!=='tool_use'||part.type!=='tool'){state.errors.push('UNEXPECTED_FRAME');continue}
    state.tools++;lastWasTerminal=false;
    const callID=part.id;
    if(!/^call_[A-Za-z0-9]+$/.test(callID||'')||callIDs.has(callID))state.errors.push('INVALID_TOOL_ID');
    callIDs.add(callID);
    const st=part.state||{}, tool=part.tool,inp=st.input||{},done=st.status==='completed',error=String(st.error||'');
    let kind=null;
    const exactOut=typeof st.output==='string'?st.output.replace(/\r?\n$/,''):null;
    if(tool==='shell'&&done&&inp.command===commands[0]&&exactOut===head)kind='READ_HEAD';
    else if(tool==='shell'&&done&&inp.command===commands[1]&&exactOut===tree)kind='READ_TREE';
    else if(['write','edit'].includes(tool)&&done&&[allowedFile,'ALLOW_ONLY.txt'].includes(inp.filePath||inp.path||inp.file_path)
      &&typeof (inp.content||inp.text)==='string'&&(inp.content||inp.text).trimEnd()==='TS_EE_ALLOWED_PROBE')kind='ALLOWED_WRITE';
    else if(tool==='patch'&&done&&patchPath(inp.patchText)?.path==='ALLOW_ONLY.txt'
      &&patchPath(inp.patchText)?.body==='TS_EE_ALLOWED_PROBE')kind='ALLOWED_WRITE';
    else if(['write','edit'].includes(tool)&&st.status==='error'&&[forbiddenFile,'BLOCKED.txt'].includes(inp.filePath||inp.path||inp.file_path)
      &&error==='Permission denied: edit')kind='DENY_EDIT';
    else if(tool==='patch'&&st.status==='error'&&patchPath(inp.patchText)?.path==='BLOCKED.txt'
      &&error==='Permission denied: edit')kind='DENY_EDIT';
    else if(tool==='shell'&&st.status==='error'&&inp.command==='echo TS_EE_DENY_PROBE'
      &&error==='Permission denied: shell')kind='DENY_SHELL';
    if(!kind)state.errors.push('UNQUALIFIED_TOOL_EVENT:'+String(tool));
    else state.sequence.push(kind);
    state.tool_calls.push({id:callID,tool,status:st.status,kind:kind||'REJECTED'});
  }
  state.complete=state.events>=9&&state.tools===5&&state.terminal&&lastWasTerminal
    &&state.session!==null&&state.errors.length===0
    &&JSON.stringify(state.sequence)===JSON.stringify(['READ_HEAD','READ_TREE','ALLOWED_WRITE','DENY_EDIT','DENY_SHELL']);
  return state;
}
