import crypto from 'node:crypto';
import {TextDecoder} from 'node:util';

export const AUTHORITY_GRANT_SCHEMA='aware-s0-synthetic-grant/v1';
export const CONTROL_GRANT_REF=/^mauedgar\/ts-execution-transport@[0-9a-f]{40}:grants\/AWARE-C2A-OC2-S0-[A-Z0-9-]+\/GRANT\.json$/;
const SHA=/^[a-f0-9]{64}$/;
const COMMENT=/^https:\/\/github\.com\/mauedgar\/aware-commerce\/issues\/29#issuecomment-[0-9]+$/;
const eq=(a,b)=>typeof a==='string'&&a===b;
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');

/**
 * Validate a GRANT pinned OUTSIDE the untrusted OpenCode request. This function
 * cannot authenticate where an operator obtained the independently supplied
 * controlAnchor. The competent Control MUST verify anchor.ref/sha256 against
 * immutable GitHub transport bytes, issuing Developer authority and an
 * approved bounded runner BEFORE calling the bootstrap. No fallback to request
 * values, no GitHub network call in the model subprocess.
 */
export function verifyControlGrant(request,grantBytes,controlAnchor,{now=Date.now()}={}){
  if(!controlAnchor||typeof controlAnchor!=='object'
    ||!CONTROL_GRANT_REF.test(controlAnchor.ref||'')
    ||!SHA.test(controlAnchor.sha256||'')
    ||!Buffer.isBuffer(grantBytes)||grantBytes.length<100||grantBytes.length>16384)
    throw Error('INDEPENDENT_CONTROL_ANCHOR_MISSING');
  if(!request||request.authorization_receipt_ref!==controlAnchor.ref
    ||request.authorization_receipt_sha256!==controlAnchor.sha256)
    throw Error('REQUEST_NOT_BOUND_TO_EXTERNAL_CONTROL_ANCHOR');
  if(digest(grantBytes)!==controlAnchor.sha256)throw Error('CONTROL_GRANT_EXACT_BYTES_MISMATCH');
  let grant;
  try{
    const raw=new TextDecoder('utf-8',{fatal:true}).decode(grantBytes);
    if(raw.startsWith('\uFEFF'))throw Error('BOM');
    grant=JSON.parse(raw);
    // Canonical one-line JSON with final LF prevents duplicate-key, ambiguous
    // whitespace and shadowed-field confusion. This tests byte structure,
    // NOT issuer authentication; the external anchor is still mandatory.
    if(raw!==JSON.stringify(grant)+'\n')
      throw Error('NONCANONICAL_OR_DUPLICATE_GRANT_KEYS');
  }catch{throw Error('CONTROL_GRANT_INVALID_JSON_UTF8')}
  if(!grant||grant.schema!==AUTHORITY_GRANT_SCHEMA
    ||grant.issuer!=='AWARE_CONTROL'||grant.disposition!=='CONDITIONAL_SYNTHETIC_S0_ONLY'
    ||grant.product!=='mauedgar/aware-commerce'
    ||grant.control_issue!=='https://github.com/mauedgar/aware-commerce/issues/29'
    ||!COMMENT.test(grant.developer_ruling_url||'')
    ||grant.cloud_enabled!==false||grant.paid_api_fallback!==false
    ||grant.product_write_allowed!==false||grant.production_allowed!==false)
    throw Error('CONTROL_GRANT_WRONG_ISSUER_OR_SCOPE');
  if(!Number.isFinite(now)||typeof grant.expires_at!=='string'
    ||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(grant.expires_at)
    ||!Number.isFinite(Date.parse(grant.expires_at))
    ||now>=Date.parse(grant.expires_at))throw Error('CONTROL_GRANT_EXPIRED_OR_TIME_INVALID');
  const subject=grant.subject;
  if(!subject||typeof subject!=='object')throw Error('CONTROL_GRANT_SUBJECT_MISSING');
  const exact={
    operation_id:request.operation_id,attempt_id:request.attempt_id,
    expected_head:request.expected_head,expected_tree:request.expected_tree,
    expected_origin:request.expected_origin,expected_host:request.expected_host,
    agent:request.agent,model:request.model,repository_root:request.repository_root,
    scratch_anchor:request.scratch_anchor,scratch_parent:request.scratch_parent,
    node_executable:request.node_executable,git_executable:request.git_executable,
    opencode_executable:request.opencode_executable,
    bootstrap_sha256:request.bootstrap_sha256,binding_sha256:request.binding_sha256,
    authority_source_sha256:request.authority_source_sha256,
    runner_sha256:request.runner_sha256,node_sha256:request.node_sha256,
    git_sha256:request.git_sha256,executable_sha256:request.executable_sha256
  };
  for(const [key,value] of Object.entries(exact))
    if(!eq(subject[key],value))throw Error('CONTROL_GRANT_SUBJECT_MISMATCH:'+key);
  const allowed=grant.synthetic_write_set;
  if(!Array.isArray(allowed)||allowed.length!==1||allowed[0]!=='ALLOW_ONLY.txt'
    ||!Array.isArray(grant.forbidden_effects)
    ||JSON.stringify(grant.forbidden_effects)!==JSON.stringify(['BLOCKED.txt','UNSCOPED_SHELL','PRODUCT_SOURCE']))
    throw Error('CONTROL_GRANT_WRITESET_UNSAFE');
  return Object.freeze({
    ref:controlAnchor.ref,sha256:controlAnchor.sha256,
    issuer:grant.issuer,subject:request.operation_id,
    attempt:request.attempt_id,
    expires_at:grant.expires_at,
    note:'Integrity and syntax checked. Trusted provenance MUST be established externally.'
  });
}
