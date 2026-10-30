import test from 'node:test';
import assert from 'node:assert/strict';
import {aggregateResults} from '../src/aggregate.mjs';

const empty={total:0,counts:{PASS:0,FAIL:0,BLOCKED:0},durationMs:0,totalCostUsd:0,ids:[]};
test('I01 empty input',()=>assert.deepEqual(aggregateResults([]),empty));
test('I02 single item and explicit zero cost',()=>assert.deepEqual(
 aggregateResults([{id:'job-a',status:'PASS',durationMs:5,costUsd:0}]),
 {total:1,counts:{PASS:1,FAIL:0,BLOCKED:0},durationMs:5,totalCostUsd:0,ids:['job-a']}
));
test('I03 first duplicate wins but all IDs sort',()=>{
 const rows=[
 {id:'z',status:'PASS',durationMs:10,costUsd:0.1},
 {id:'a',status:'FAIL',durationMs:20,costUsd:0.2},
 {id:'z',status:'BLOCKED',durationMs:50,costUsd:10},
 {id:'B',status:'BLOCKED',durationMs:30}
 ];
 assert.deepEqual(aggregateResults(rows),{
  total:3,counts:{PASS:1,FAIL:1,BLOCKED:1},
  durationMs:60,totalCostUsd:0.3,ids:['B','a','z']
 });
});
test('I04 input remains unchanged',()=>{
 const rows=Object.freeze([Object.freeze({id:'1',status:'PASS',durationMs:1})]);
 assert.equal(aggregateResults(rows).total,1);
});
test('I05 validate duplicate even when it will be ignored',()=>{
 assert.throws(()=>aggregateResults([
  {id:'a',status:'PASS',durationMs:1},
  {id:'a',status:'WRONG',durationMs:2}
 ]), /./);
});
test('I06 error on not-an-array',()=>assert.throws(()=>aggregateResults(null),/./));
test('I07 invalid ID and duration',()=>{
 for(const row of [
  {id:'',status:'PASS',durationMs:1},
  {id:'a',status:'PASS',durationMs:-1},
  {id:'a',status:'PASS',durationMs:1.5},
  {id:'a',status:'PASS',durationMs:Infinity},
 ] ) assert.throws(()=>aggregateResults([row]),/./);
});
test('I08 invalid cost and status',()=>{
 for(const row of [
  {id:'a',status:'FAIL',durationMs:1,costUsd:-0.1},
  {id:'a',status:'FAIL',durationMs:1,costUsd:Infinity},
  {id:'a',status:'NONE',durationMs:1},
  null
 ]) assert.throws(()=>aggregateResults([row]),/./);
});
test('I09 rounded final floating cost and default cost',()=>{
 const a=aggregateResults([
  {id:'a',status:'PASS',durationMs:1,costUsd:0.1},
  {id:'b',status:'PASS',durationMs:2,costUsd:0.2},
  {id:'c',status:'PASS',durationMs:3}
 ]);
 assert.equal(a.totalCostUsd,0.3);assert.equal(a.durationMs,6);
});
