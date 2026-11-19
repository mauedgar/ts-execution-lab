import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchJson } from '../src/fetchSupport.mjs';
test('rejects HTTP failure',async()=>{
 await assert.rejects(fetchJson('/api',async()=>({status:503,json:async()=>[]})),/failed/);
});
test('defensively clones response rows',async()=>{
 const x=[{id:1}];const y=await fetchJson('/api',async()=>({status:200,json:async()=>x}));
 y[0].id=2;assert.equal(x[0].id,1);
});
