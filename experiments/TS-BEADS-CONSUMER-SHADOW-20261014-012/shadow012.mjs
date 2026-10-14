// TS-BEADS-CONSUMER-SHADOW-012
// Pure read-only projection. This is NOT a Beads API call and not a Product consumer implementation.
// Usage: node shadow012.mjs
import assert from 'node:assert/strict';

const productAnchor = Object.freeze({
  repository: 'mauedgar/tecnotron-ai',
  branch: 'tools',
  commit: '2a42a1bbda6e9fecccb28c42c9c2dd294b3b1c89',
  tree: '04e57337ac129bd40774d48cf2cfee041f904cfa',
  taskcycle: 'TASKCYCLE-TECNOTRON-RECIPE-KERNEL-DECOUPLING-001',
  terminal: 'CLOSED_PASS',
  source: 'docs/current-state.md',
  canonical_candidate: '34ab96c00ca5f8c9c87d69a31371d275eeb5f6d9',
});

const defaultSource = `${productAnchor.repository}@${productAnchor.commit}:${productAnchor.source}`;
// A is the original Product view. B is a synthetic Beads-style operational index view.
// Independent authority is always inspected from A, never inferred from B.
function project(A, B) {
  let decision;
  if (!A.source_ref || !A.exact_subject_ref || !B.origin_ref) {
    decision = 'EVIDENCE_INCOMPLETE';
  } else if (A.effect_state === 'UNKNOWN') {
    decision = 'RECONCILE_ORIGINAL_EFFECT_FIRST';
  } else if (B.origin_ids?.length > 1 && new Set(B.origin_ids).size > 1) {
    decision = 'ORIGIN_COLLISION_READBACK_REQUIRED';
  } else if (B.origin_ids?.length > 1) {
    decision = 'DUPLICATE_OBLIGATION_NO_RECREATE';
  } else if (A.terminal === 'CLOSED_PASS') {
    decision = B.post_close_discovery ? 'POST_CLOSE_INDEX_ONLY' : 'CLOSED_SUBJECT_NO_REOPEN';
  } else if (A.original_interrupted) {
    decision = 'RESUME_ORIGINAL_IDENTITY_ONLY_AFTER_ORIGINAL_GATE';
  } else if (B.status === 'closed') {
    decision = 'BEADS_CLOSED_NOT_PRODUCT_CLOSED';
  } else if (B.dependencies?.some(d => d.status !== 'SATISFIED')) {
    decision = 'DEPENDENCY_NOT_PROVEN';
  } else if (B.dependencies?.length !== new Set(B.dependencies?.map(d => d.id)).size) {
    decision = 'DEPENDENCY_INVENTORY_DUPLICATE';
  } else if (B.claimed && !A.independent_authority_verified) {
    decision = 'BEADS_CLAIM_NOT_DEVELOPER_GRANT';
  } else if (!A.independent_authority_verified) {
    decision = 'PRODUCT_AUTHORIZATION_NOT_PROVEN';
  } else if (B.status === 'ready') {
    decision = 'CANDIDATE_FOR_EXISTING_CONTROL_CHECKPOINT_ONLY';
  } else {
    decision = 'INDEX_NOT_READY_OR_UNQUALIFIED';
  }
  return {
    decision,
    A: {taskcycle: A.taskcycle, terminal: A.terminal, effect_state: A.effect_state,
        authority_verified: !!A.independent_authority_verified, source_ref: A.source_ref},
    B: {status: B.status, origin_ref: B.origin_ref, dependencies: B.dependencies || [], claimed: !!B.claimed},
    Product_effect: 'NONE', dispatched: false, new_taskcycle: false, repository_writes: 0,
  };
}

const realA = {taskcycle: productAnchor.taskcycle, terminal: productAnchor.terminal,
  effect_state: 'CONFIRMED', exact_subject_ref: `${productAnchor.repository}@${productAnchor.canonical_candidate}`,
  source_ref: defaultSource, independent_authority_verified: false};
const syntheticA = {...realA, terminal: 'ACTIVE_SYNTHETIC', effect_state: 'NONE'};
const readyB = {status: 'ready', origin_ref: defaultSource, dependencies: [], claimed: false};
const tests = [
  ['real_closed_ignores_ready', realA, readyB, 'CLOSED_SUBJECT_NO_REOPEN', 'OBSERVED_PRODUCT_WITH_SYNTHETIC_BEADS'],
  ['postclose_discovery_not_promoted', realA, {...readyB, post_close_discovery: true}, 'POST_CLOSE_INDEX_ONLY', 'SYNTHETIC_COUNTERFACTUAL'],
  ['unmet_dependency', syntheticA, {...readyB, dependencies:[{id:'source-obligation',status:'PENDING'}]}, 'DEPENDENCY_NOT_PROVEN', 'SYNTHETIC_COUNTERFACTUAL'],
  ['unknown_dependency', syntheticA, {...readyB, dependencies:[{id:'source-obligation',status:'UNKNOWN'}]}, 'DEPENDENCY_NOT_PROVEN', 'SYNTHETIC_COUNTERFACTUAL'],
  ['independent_authorized_only_considered', {...syntheticA,independent_authority_verified:true}, readyB, 'CANDIDATE_FOR_EXISTING_CONTROL_CHECKPOINT_ONLY', 'SYNTHETIC_COUNTERFACTUAL'],
  ['independent_missing_grant', syntheticA, readyB, 'PRODUCT_AUTHORIZATION_NOT_PROVEN', 'SYNTHETIC_COUNTERFACTUAL'],
  ['interrupted_original_preserved', {...syntheticA, original_interrupted:true}, readyB, 'RESUME_ORIGINAL_IDENTITY_ONLY_AFTER_ORIGINAL_GATE', 'SYNTHETIC_COUNTERFACTUAL'],
  ['same_native_id_repeat', syntheticA, {...readyB, origin_ids:['shadow-one','shadow-one']}, 'DUPLICATE_OBLIGATION_NO_RECREATE', 'SYNTHETIC_COUNTERFACTUAL'],
  ['same_origin_different_native_ids', syntheticA, {...readyB, origin_ids:['shadow-one','shadow-two']}, 'ORIGIN_COLLISION_READBACK_REQUIRED', 'SYNTHETIC_COUNTERFACTUAL'],
  ['unknown_effect_blocks_claim', {...syntheticA,effect_state:'UNKNOWN'}, {...readyB,claimed:true}, 'RECONCILE_ORIGINAL_EFFECT_FIRST', 'SYNTHETIC_COUNTERFACTUAL'],
  ['claim_not_authority', syntheticA, {...readyB,claimed:true}, 'BEADS_CLAIM_NOT_DEVELOPER_GRANT', 'SYNTHETIC_COUNTERFACTUAL'],
  ['beads_closed_not_product_closed', syntheticA, {...readyB,status:'closed'}, 'BEADS_CLOSED_NOT_PRODUCT_CLOSED', 'SYNTHETIC_COUNTERFACTUAL'],
  ['missing_source_reference', {...syntheticA,source_ref:null}, readyB, 'EVIDENCE_INCOMPLETE', 'SYNTHETIC_COUNTERFACTUAL'],
  ['duplicate_dependency_record', syntheticA, {...readyB,dependencies:[{id:'same',status:'SATISFIED'},{id:'same',status:'SATISFIED'}]}, 'DEPENDENCY_INVENTORY_DUPLICATE', 'SYNTHETIC_COUNTERFACTUAL'],
  ['unqualified_index_status', {...syntheticA,independent_authority_verified:true}, {...readyB,status:'open'}, 'INDEX_NOT_READY_OR_UNQUALIFIED', 'SYNTHETIC_COUNTERFACTUAL'],
];
const results=[];
for (const [id,A,B,expected,evidenceClass] of tests) {
  const result=project(A,B);
  assert.equal(result.decision, expected, `${id}: decision mismatch`);
  assert.equal(result.Product_effect, 'NONE', `${id}: Product effect`);
  assert.equal(result.dispatched, false, `${id}: dispatch`);
  assert.equal(result.new_taskcycle, false, `${id}: TaskCycle creation`);
  assert.equal(result.repository_writes, 0, `${id}: repository write`);
  if(id==='interrupted_original_preserved') assert.equal(result.A.taskcycle, productAnchor.taskcycle);
  results.push({id, evidenceClass, expected, observed:result.decision, PASS:true});
}
console.log(JSON.stringify({test:'TS-BEADS-CONSUMER-SHADOW-012', mode:'PURE_READ_ONLY_MODEL', native_beads_executed:false, productAnchor,
  count:results.length, pass:results.length, fail:0, Product_effect:'NONE', results}, null, 2));
