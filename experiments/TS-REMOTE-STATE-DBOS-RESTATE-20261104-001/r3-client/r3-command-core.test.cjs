'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const core=require('./r3-command-core.cjs');
const clone=v=>JSON.parse(JSON.stringify(v));
class FakeDB {
  constructor(){this.data={states:new Map(),events:new Map(),receipts:new Map()};this.commitFault=false;this.insertAttempts=0;}
  client(){return new FakeConnection(this);}
}
class FakeConnection {
  constructor(db){this.db=db;this.staging=null;this.readOnly=false;}
  table(name){return (this.staging || this.db.data)[name];}
  async query(sql,p=[]){
    const norm=sql.trim().replace(/\s+/g,' ').toLowerCase();
    const rows=rows=>({rowCount:rows.length,rows});
    if(norm==='begin' || norm==='begin isolation level repeatable read read only'){
      assert.equal(this.staging,null,'no nested transaction');
      this.readOnly=norm.includes('read only');
      this.staging={states:new Map(this.db.data.states),events:new Map(this.db.data.events),receipts:new Map(this.db.data.receipts)};
      return rows([]);
    }
    if(norm==='rollback'){this.staging=null;this.readOnly=false;return rows([]);}
    if(norm==='commit'){
      assert(this.staging);
      if(!this.readOnly)this.db.data=this.staging;
      this.staging=null;this.readOnly=false;
      if(this.db.commitFault){this.db.commitFault=false;throw new Error('synthetic lost server ACK after COMMIT');}
      return rows([]);
    }
    if(norm.includes('insert into')){this.db.insertAttempts++;assert.equal(this.readOnly,false,'B must never attempt INSERT');}
    if(norm.includes('insert into')&&norm.includes('.receipts')){
      const [mid,fp,raw]=p;
      if(this.table('receipts').has(mid))return rows([]);
      this.table('receipts').set(mid,{mutation_id:mid,command_fingerprint:fp,original_revision:1,result:JSON.parse(raw)});
      return rows([{mutation_id:mid}]);
    }
    if(norm.includes('insert into')&&norm.includes('.aggregate_state')){
      const [id,raw,hash]=p;
      if(this.table('states').has(id))throw new Error('duplicate state');
      this.table('states').set(id,{revision:1,state:JSON.parse(raw),last_event_sha256:hash});
      return rows([]);
    }
    if(norm.includes('insert into')&&norm.includes('.events')){
      const [event_id,id,event_hash,raw]=p;
      if(this.table('events').has(event_id))throw new Error('duplicate event');
      this.table('events').set(event_id,{event_id,id,sequence:1,previous_hash:null,event_hash,payload:JSON.parse(raw)});
      return rows([]);
    }
    if(norm.includes('select revision from')&&norm.includes('.aggregate_state')){
      const state=this.table('states').get(p[0]);return rows(state?[{revision:state.revision}]:[]);
    }
    if(norm.includes('select revision,state,last_event_sha256 from')){
      const state=this.table('states').get(p[0]);return rows(state?[clone(state)]:[]);
    }
    if(norm.includes('select event_id,sequence,previous_hash,event_hash,payload from')){
      return rows([...this.table('events').values()].filter(e=>e.id===p[0]).map(clone));
    }
    if(norm.includes('select mutation_id,command_fingerprint,original_revision,result from')){
      const receipt=this.table('receipts').get(p[0]);return rows(receipt?[clone(receipt)]:[]);
    }
    if(norm.includes('select command_fingerprint,original_revision,result from')){
      const receipt=this.table('receipts').get(p[0]);return rows(receipt?[clone(receipt)]:[]);
    }
    if(norm.includes('select (select count(*)::int')){
      const [id,mid]=p;
      return rows([{state_count:Number(this.table('states').has(id)),event_count:[...this.table('events').values()].filter(e=>e.id===id).length,receipt_count:Number(this.table('receipts').has(mid))}]);
    }
    throw new Error('Unexpected query route: '+norm.slice(0,100));
  }
}
const id='R3-HOST-SYNTHETIC_20261105_011';

test('IR001 F001 real mutating handler commits once then reconciles exact replay',async()=>{
 const db=new FakeDB(),p=core.planned(id),a=db.client(),b=db.client();
 assert.deepEqual(await core.applyCreate(a,p),{disposition:'COMMITTED',revision:1,events:1,receipts:1});
 assert.deepEqual(await core.applyCreate(b,p,{allowCreate:false}),{disposition:'RECONCILED',revision:1,events:1,receipts:1});
 assert.equal(db.insertAttempts,3,'Host B existing-only must not emit INSERT');
 const info=await core.inspect(b,p);
 assert.equal(info.effects,1);assert.equal(info.receipts,1);assert.equal(info.events,1);
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[1,1,1]);
});
test('IR001 F001 changed authority goes to handler and cannot mutate',async()=>{
 const db=new FakeDB(),p=core.planned(id);await core.applyCreate(db.client(),p);
 const mismatch=core.planned(id,{...p.cmd,authority_refs:['AUTH-OTHER']});
 await assert.rejects(core.applyCreate(db.client(),mismatch,{allowCreate:false}),e=>e.code==='MUTATION_IDENTITY_COLLISION');
 assert.equal(db.insertAttempts,3,'Host B collision must not emit INSERT');
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[1,1,1]);
 assert.equal((await core.inspect(db.client(),p)).receipts,1);
});
test('IR001 F002 commit acknowledgement uncertain, separate B reads exact original without retry',async()=>{
 const db=new FakeDB(),p=core.planned(id);db.commitFault=true;
 await assert.rejects(core.applyCreate(db.client(),p),e=>e.code==='COMMIT_RESULT_UNKNOWN');
 assert.deepEqual(await core.resolveUnknown(db.client(),p),{disposition:'CONFIRMED',effect:'CONFIRMED',retry_authorized:false,revision:1,receipts:1});
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[1,1,1]);
});
test('IR001 F002 absent receipt is UNKNOWN at observation, NOT an automatic retry',async()=>{
 const db=new FakeDB(),p=core.planned(id);
 assert.deepEqual(await core.resolveUnknown(db.client(),p),{disposition:'NOT_OBSERVED',effect:'UNKNOWN',retry_authorized:false});
});
test('IR001 F001 serialization rejects lossy fingerprint aliases',()=>{
 const p=core.planned(id);
 for(const invalid of [NaN,Infinity,-Infinity,-0,undefined,1n,()=>1,Symbol('x')]){
   assert.throws(()=>core.planned(id,{...p.cmd,fields:{...p.cmd.fields,obligations:[invalid]}}),e=>e instanceof core.SafeError);
 }
 const cyclic={};cyclic.self=cyclic;
 assert.throws(()=>core.planned(id,{...p.cmd,fields:{...p.cmd.fields,obligations:[cyclic]}}),e=>e.code==='CYCLIC_JSON');
 const evil={...p.cmd,type:'__proto__'};
 assert.throws(()=>core.planned(id,evil),e=>e.code==='COMMAND_IDENTITY');
});
test('F003: physical enrollment and distinct principal remain required externally; no PASS inferred from mocks',()=>{
 assert.notEqual('tsr3_host_a_rw','tsr3_host_b_rw');
 assert.equal(typeof core.planned,'function');
});

test('IR002 new blocking repair: B replay on missing receipt cannot create any effect',async()=>{
 const db=new FakeDB(),p=core.planned(id);
 await assert.rejects(core.applyCreate(db.client(),p,{allowCreate:false}),e=>e.code==='RECEIPT_NOT_OBSERVED_UNKNOWN');
 assert.equal(db.insertAttempts,0,'no B SQL INSERT even with unexpected broad grants');
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[0,0,0]);
 const mismatch=core.planned(id,{...p.cmd,authority_refs:['AUTH-OTHER']});
 await assert.rejects(core.applyCreate(db.client(),mismatch,{allowCreate:false}),e=>e.code==='RECEIPT_NOT_OBSERVED_UNKNOWN');
 assert.equal(db.insertAttempts,0);
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[0,0,0]);
});
test('B cannot create an unrelated key even if another A receipt exists',async()=>{
 const db=new FakeDB(),base=core.planned(id),unrelated=core.planned('R3-HOST-OTHERKEY_20261105_012');
 await core.applyCreate(db.client(),base);
 await assert.rejects(core.applyCreate(db.client(),unrelated,{allowCreate:false}),e=>e.code==='RECEIPT_NOT_OBSERVED_UNKNOWN');
 assert.equal(db.insertAttempts,3,'only original A inserts');
 assert.deepEqual([db.data.states.size,db.data.events.size,db.data.receipts.size],[1,1,1]);
});
