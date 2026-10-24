import assert from 'node:assert/strict';
import Module from 'node:module';
import {createRequire} from 'node:module';
import {mkdtempSync,rmSync,writeFileSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const dir=process.env.PRODUCT_ROOT,receipt=process.env.RESULT_PATH;
if(!dir||!receipt||process.platform==='win32')throw Error('Linux fixture only');
const p=createRequire(join(dir,'package.json'));
const {FilesystemStateStore,create,transition,satisfy,inspect}=p(join(dir,'src/state-kernel-v0'));
const {createStateKernelTaskCycleLifecycle}=p(join(dir,'src/operational-spine-v0/state-kernel-adapter'));
const {createReconcileAndCloseTaskCycleRecipe}=p(join(dir,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle'));
import {req} from './fixtures023.mjs';
const checks=[],home=mkdtempSync(join(tmpdir(),'beads-023-native-'));
const mark=(name,v)=>{assert.ok(v,name);checks.push(name)};
const obligations=['INDEPENDENT_REVIEW','DEVELOPER_ACCEPTANCE','CANONICAL_INTEGRATION','REMOTE_PUBLICATION','LIFECYCLE_RECONCILIATION'];
const ids={INDEPENDENT_REVIEW:'authority:reviewer-001',DEVELOPER_ACCEPTANCE:'authority:developer-001',CANONICAL_INTEGRATION:'authority:effect-001',REMOTE_PUBLICATION:'authority:effect-001'};
const refs={INDEPENDENT_REVIEW:'evidence/authority-reviewer-001.json',DEVELOPER_ACCEPTANCE:'evidence/authority-developer-001.json',CANONICAL_INTEGRATION:'evidence/authority-effect-001.json',REMOTE_PUBLICATION:'evidence/authority-effect-001.json'};
const result={status:'RUNNING',checks,source_native:true,product_effect:'NONE'};
try{
 const store=new FilesystemStateStore(home);store.initialize();
 const c=create(store,0,'TaskCycle','TC023',{responsibility:'SYNTHETIC_ONLY',obligations:obligations.map(id=>({id}))},[]);
 transition(store,c.revision,'TaskCycle','TC023','ACTIVE');
 for(const id of obligations){
  const a=ids[id];const ref=a?{kind:'AUTHORITY',id:a,location:refs[id]}:undefined;
  const x=satisfy(store,store.verify().revision,'TC023',id,a,ref);
  mark('native_satisfy_'+id,x.kind==='TaskCycle'&&x.aggregate_id==='TC023');
 }
 const snapshot=inspect(store,'TaskCycle','TC023').aggregate;
 mark('source_native_reachable_presatisfied_active',snapshot.state==='ACTIVE'&&snapshot.obligations.every(x=>x.status==='SATISFIED'));
 mark('competent_developer_authority_attached',snapshot.authority_refs.some(x=>x.id==='authority:developer-001'));
 result.reachable_state={state:snapshot.state,obligations:snapshot.obligations,authority_refs:snapshot.authority_refs};
 const consumer=createReconcileAndCloseTaskCycleRecipe({lifecycle:createStateKernelTaskCycleLifecycle({store})});
 const newRejected=req('TC023',{badDeveloper:true,expectedRevision:store.verify().revision});
 const recheck=await consumer.preflight(newRejected);
 result.source_native_post_satisfaction_rejected_preflight={status:recheck.status,reason:recheck.reason??null};
 mark('original_recipe_returns_READY_for_post_satisfaction_new_REJECTED',recheck.status==='READY');
 // QUALIFICATION-ONLY: demonstrate a minimal candidate Product semantic guard,
 // applied strictly in memory. This does NOT modify the original Product file.
 const sourceFile=join(dir,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle.js');
 const originalSource=readFileSync(sourceFile,'utf8');
 const anchor='  const closureAuthority = reconciledAuthority(';
 if(originalSource.split(anchor).length!==2)throw Error('SOURCE_GUARD_ANCHOR_DRIFT');
 const revised=originalSource.replace(anchor,
   "  if (reconciliation.observed_facts?.developer_acceptance?.disposition !== 'ACCEPTED') {\n"+
   "    return { status: 'BLOCKED', reason: 'DEVELOPER_ACCEPTANCE_NOT_ACCEPTED', reconciliation };\n"+
   "  }\n"+anchor);
 const guardModule=new Module(sourceFile,undefined);
 guardModule.filename=sourceFile;
 guardModule.paths=Module._nodeModulePaths(join(dir,'src/operational-spine-v0/recipes'));
 guardModule._compile(revised,sourceFile);
 const guardRecipe=guardModule.exports.createReconcileAndCloseTaskCycleRecipe({
  lifecycle:createStateKernelTaskCycleLifecycle({store})});
 const guardDenied=await guardRecipe.preflight(newRejected);
 const guardAllowed=await guardRecipe.preflight(
  req('TC023',{expectedRevision:store.verify().revision}));
 result.guarded_research_candidate={new_rejected_preflight:guardDenied.status,
  accepted_preflight:guardAllowed.status,lines_added:3,
  implementation:'IN_MEMORY_ONLY_NOT_PRODUCT'};
 mark('experimental_product_guard_rejects_post_satisfaction_REJECTED',
  guardDenied.status==='BLOCKED'&&guardDenied.reason==='DEVELOPER_ACCEPTANCE_NOT_ACCEPTED');
 mark('experimental_product_guard_preserves_ACCEPTED_preflight',
  guardAllowed.status==='READY');
 const untouched=inspect(store,'TaskCycle','TC023').aggregate;
 mark('preflight_did_not_close_native_taskcycle',untouched.state==='ACTIVE');
 result.limit='Original native transitions reach ACTIVE/all-satisfied and original recipe preflight sees new synthetic REJECTED as READY; independent competence/provenance of changed external evidence is not established.';
 result.status='PASS_NATIVE_REACHABILITY_AND_IN_MEMORY_AUTHORITY_GUARD';
 console.log('TS023_AUTHORITY_GUARD=PASS;checks='+checks.length+';product=NONE');
}catch(e){result.status='FAIL_NATIVE_RECONCILE';result.error=String(e.stack||e);throw e
}finally{rmSync(home,{recursive:true,force:true});writeFileSync(receipt,JSON.stringify(result,null,2)+'\n')}
