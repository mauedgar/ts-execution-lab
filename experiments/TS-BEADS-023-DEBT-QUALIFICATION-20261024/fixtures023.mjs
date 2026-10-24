import {createHash} from 'node:crypto';
const auth={kind:'AUTHORITY',id:'authority:developer-001',location:'evidence/authority-developer-001.json'};
function obsFor(tcId){
 return {
  candidate_identity:[{source_ref:'candidate:001',observed:{
   commit:'a'.repeat(40),tree:'b'.repeat(40),parent:'c'.repeat(40),changed_paths:['src/recipe.js','tests/recipe.test.js']}}],
  terminal_results:[{source_ref:'terminal:001',observed:[{reference:'terminal:001',subject_id:'AT-001',status:'PASS'}]}],
  independent_review:[{source_ref:'review:001',observed:{reference:'review:001',disposition:'PASS'}}],
  developer_acceptance:[{source_ref:'authority:developer-001',observed:{reference:'authority:developer-001',disposition:'ACCEPTED'}}],
  canonical_integration:[{source_ref:'integration:001',observed:{reference:'integration:001',status:'INTEGRATED'}}],
  remote_publication:[{source_ref:'publication:001',observed:{reference:'publication:001',status:'PUBLISHED'}}],
  canonical_state_delta:[{source_ref:'state-delta:001',observed:{
   from:{reference:'state:40',revision:40,sha256:'d'.repeat(64)},
   to:{reference:'state:50',revision:50,sha256:'e'.repeat(64)},
   changed_aggregates:[{kind:'TaskCycle',id:tcId,before_revision:6,after_revision:7}]}}]
 };
}
const evidenceKinds={candidate_identity:'CANDIDATE_IDENTITY',terminal_results:'TERMINAL_RESULTS',
 independent_review:'INDEPENDENT_REVIEW_RESULT',developer_acceptance:'DEVELOPER_ACCEPTANCE',
 canonical_integration:'CANONICAL_INTEGRATION',remote_publication:'REMOTE_PUBLICATION',
 canonical_state_delta:'CANONICAL_STATE_DELTA'};
const competence={independent_review:['INDEPENDENT_REVIEW','authority:reviewer-001'],
 developer_acceptance:['DEVELOPER','authority:developer-001'],
 canonical_integration:['EFFECT_AUTHORITY','authority:effect-001'],
 remote_publication:['EFFECT_AUTHORITY','authority:effect-001']};
const hash=s=>createHash('sha256').update(s).digest('hex');
function verifiedEvidence(tc,obs){
 return Object.entries(obs).flatMap(([field,entries])=>entries.map(entry=>{
 const c=competence[field],payload={schema_version:'tecnotron-reconciliation-evidence/v0',
  kind:evidenceKinds[field],subject:{kind:'TaskCycle',id:tc,field},observed:entry.observed,
  verification:{status:'VERIFIED',verification_ref:'verification:'+entry.source_ref,
   verifier_ref:'verifier:fixture',authority_competence:c?
   {status:'ESTABLISHED',kind:c[0],authority_ref:c[1],basis_ref:'basis:'+field}:null}};
 const json=JSON.stringify(payload);
 return {ref:entry.source_ref,sha256:hash(json),artifact_json:json};
 }));
}
const obligationsRules=[
 {obligation_id:'INDEPENDENT_REVIEW',source:'independent_review',
  authority_ref:'authority:reviewer-001',
  authority_reference:{kind:'AUTHORITY',id:'authority:reviewer-001',location:'evidence/authority-reviewer-001.json'}},
 {obligation_id:'DEVELOPER_ACCEPTANCE',source:'developer_acceptance',
  authority_ref:'authority:developer-001',authority_reference:auth},
 {obligation_id:'CANONICAL_INTEGRATION',source:'canonical_integration',
  authority_ref:'authority:effect-001',
  authority_reference:{kind:'AUTHORITY',id:'authority:effect-001',location:'evidence/authority-effect-001.json'}},
 {obligation_id:'REMOTE_PUBLICATION',source:'remote_publication',remote_expected_status:'PUBLISHED',
  authority_ref:'authority:effect-001'},
 {obligation_id:'LIFECYCLE_RECONCILIATION',source:'reconciliation'}
];
function req(tcId,{badDeveloper=false,pending=false,expectedRevision=50}={}){
 const obs=obsFor(tcId);
 if(badDeveloper==='MISSING')obs.developer_acceptance=[];
 else if(badDeveloper){obs.developer_acceptance=[{source_ref:'authority:developer-001',
  observed:{reference:'authority:developer-001',disposition:'REJECTED'}}];}
 return {
  recipe_id:'reconcile_and_close_taskcycle',recipe_version:'v0',
  operation_id:'OP-CLOSE',execution_attempt_id:'AT-CLOSE',
  context:{schema_version:'tecnotron-execution-context/v0',operation_id:'OP-CLOSE',
   taskcycle_id:tcId,repository:{identity:'fixture',location:'/synthetic/no-repository-effect'},
   runtime:{executor:'test',platform:'synthetic',runtime_identity:'node:test'},
   state_store:{reference:'synthetic-state'},authority_refs:[],evidence_refs:[]},
  authorization:{disposition:'AUTHORIZED',authority_reference:'DEV-CLOSE',
    effect_constraints:[{effect:'state.taskcycle.write',scope:'exact taskcycle only'}]},
  evidence_refs:[],
  input:{expected_state_revision:expectedRevision,observations:obs,evidence:verifiedEvidence(tcId,obs),
   obligation_satisfactions:pending?obligationsRules:[],closure:{authority_ref:'authority:developer-001',disposition_ref:'result:closed'}}
 };
}

export {req,obligationsRules};
