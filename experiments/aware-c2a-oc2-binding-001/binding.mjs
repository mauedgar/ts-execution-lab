import path from 'node:path';

const SHA40=/^[0-9a-f]{40}$/;
const SHA64=/^[0-9a-f]{64}$/;
const ID=/^[A-Za-z][A-Za-z0-9_-]{7,100}$/;
export function assertRequest(r) {
  if(r?.schema!=='ts-ee-oc2-c2a-request/v1'||r?.product!=='mauedgar/aware-commerce'
    ||r?.authority_class!=='SYNTHETIC_NONPRODUCT_ONLY'||r?.paid_api_fallback!==false
    ||!ID.test(r.operation_id||'')||!ID.test(r.attempt_id||'')
    ||!SHA64.test(r.runner_sha256||'')||!SHA64.test(r.executable_sha256||'')
    ||!SHA40.test(r.expected_head||'')||!SHA40.test(r.expected_tree||'')
    ||!/^opencode v2\./.test(r.expected_version||'')
    ||!/^openai\/[a-z0-9._-]+$/.test(r.model||'')
    ||!ID.test(r.agent||'')||!ID.test(r.expected_host||''))throw Error('INVALID_QUALIFICATION_IDENTITY');
  if(!['https://github.com/mauedgar/aware-commerce.git','git@github.com:mauedgar/aware-commerce.git'].includes(r.expected_origin))throw Error('UNQUALIFIED_GIT_ORIGIN');
  for(const f of ['repository_root','scratch_parent','opencode_executable'])
    if(typeof r[f]!=='string'||!path.isAbsolute(r[f])||/["'&|;$<>\r\n]/.test(r[f]))throw Error('UNSAFE_'+f);
  return r;
}
export function gitCommands(root) {
  if(!path.isAbsolute(root)||/["'&|;$<>\r\n]/.test(root))throw Error('UNSAFE_GIT_ROOT');
  return ['git -C "'+root+'" rev-parse HEAD','git -C "'+root+'" rev-parse HEAD^{tree}'];
}
export function makePolicy(agent,allowedFile,commands) {
  if(!ID.test(agent)||path.basename(allowedFile)!=='ALLOW_ONLY.txt'||commands.length!==2)throw Error('POLICY_INPUT');
  const positive=[...commands.map(resource=>({action:'shell',resource,effect:'allow'}))];
  for(const a of ['write','edit'])for(const resource of [allowedFile,'ALLOW_ONLY.txt'])positive.push({action:a,resource,effect:'allow'});
  return {permissions:[{action:'*',resource:'*',effect:'deny'}],
    agents:{[agent]:{mode:'primary',permissions:[{action:'*',resource:'*',effect:'deny'},...positive]}},plugin:[]};
}
export function checkEffective(agents,agent,policy) {
  const found=Array.isArray(agents)?agents.find(x=>x.id===agent):null;
  if(!found||!Array.isArray(found.permissions))throw Error('EFFECTIVE_AGENT_UNAVAILABLE');
  const rules=policy.agents[agent].permissions;
  for(const p of rules)if(!found.permissions.some(x=>x.action===p.action&&x.resource===p.resource&&x.effect===p.effect))throw Error('EXPECTED_NATIVE_RULE_MISSING');
  for(const r of found.permissions)if(r.effect==='allow'&&['*','shell','bash','edit','write','patch','task'].includes(r.action)&&!rules.some(x=>x.action===r.action&&x.resource===r.resource&&x.effect==='allow'))throw Error('UNEXPECTED_NATIVE_ALLOW');
  return true;
}
export function inspectEvents(jsonl,{commands,allowedFile,forbiddenFile,head,tree}) {
  const o={events:0,tools:0,read_head:false,read_tree:false,write_allow:false,edit_denied:false,shell_denied:false,forbidden_completed:false,invalid_events:0};
  const allowed=new Set([allowedFile,'ALLOW_ONLY.txt']),forbidden=new Set([forbiddenFile,'BLOCKED.txt']);
  for(const line of jsonl.split(/\r?\n/)) {
    if(!line.trim())continue;
    let e;try{e=JSON.parse(line)}catch{o.invalid_events++;continue}
    o.events++;const part=e?.part;if(part?.type!=='tool')continue;
    o.tools++;const st=part.state||{},tool=String(part.tool||'').toLowerCase(),input=st.input||part.input||{};
    const cmd=input.command||input.cmd,filename=input.filePath||input.file_path||input.path;
    const success=st.status==='completed',denied=st.status==='error'&&/permission|rejected|denied/i.test(JSON.stringify(st.error||''));
    const out=JSON.stringify(st.output||st.metadata?.stdout||'');
    if(tool==='shell'||tool==='bash') {
      if(success&&cmd===commands[0]&&out.includes(head))o.read_head=true;
      else if(success&&cmd===commands[1]&&out.includes(tree))o.read_tree=true;
      else if(denied&&cmd==='echo TS_EE_DENY_PROBE')o.shell_denied=true;
      else if(success)o.forbidden_completed=true;
    }else if(['edit','write','patch'].includes(tool)){
      if(success&&allowed.has(filename))o.write_allow=true;
      else if(denied&&forbidden.has(filename))o.edit_denied=true;
      else if(success)o.forbidden_completed=true;
    }else if(success)o.forbidden_completed=true;
  }
  return o;
}
