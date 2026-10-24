import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdtempSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const dir=process.env.PRODUCT_ROOT,receipt=process.env.RESULT_PATH;
if(!dir||!receipt||process.platform==='win32')throw Error('Linux fixture only');
const p=createRequire(join(dir,'package.json'));
const {FilesystemStateStore,create,transition,satisfy,inspect}=p(join(dir,'src/state-kernel-v0'));
const {createStateKernelTaskCycleLifecycle}=p(join(dir,'src/operational-spine-v0/state-kernel-adapter'));
const {createReconcileAndCloseTaskCycleRecipe}=p(join(dir,'src/operational-spine-v0/recipes/reconcile-and-close-taskcycle'));
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
 result.limit='This reaches the native all-satisfied state using real Product transitions, but does not by itself validate whether later contrary Developer evidence is admissible in a real upstream history.';
 result.status='PASS_NATIVE_PRESATISFIED_REACHABLE';
 console.log('TS023_AUTHORITY_NATIVE=PASS;checks='+checks.length+';product=NONE');
}catch(e){result.status='FAIL_NATIVE_RECONCILE';result.error=String(e.stack||e);throw e
}finally{rmSync(home,{recursive:true,force:true});writeFileSync(receipt,JSON.stringify(result,null,2)+'\n')}
