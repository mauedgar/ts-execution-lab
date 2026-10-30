import test from 'node:test';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

if (!process.env.TARGET_DIR) throw new Error('TARGET_DIR_REQUIRED');
const {aggregateResults}=await import(pathToFileURL(resolve(process.env.TARGET_DIR,'src/aggregate.mjs')).href);

test('OI01 final cost is rounded to exactly six decimals',()=>{
 const out=aggregateResults([{id:'x',status:'PASS',durationMs:1,costUsd:0.123456789}]);
 assert.equal(out.totalCostUsd,0.123457);
});
test('OI02 submicro fraction rounds up at six decimals',()=>{
 assert.equal(aggregateResults([{id:'x',status:'PASS',durationMs:0,costUsd:0.0000006}]).totalCostUsd,0.000001);
});
test('OI03 duplicate is validated even if no contribution',()=>{
 assert.throws(()=>aggregateResults([{id:'x',status:'PASS',durationMs:0},{id:'x',status:'PASS',durationMs:-1}]), e=>e instanceof TypeError||e instanceof RangeError);
});
test('OI04 cases are distinct and UTF16-sorted',()=>{
 const a=aggregateResults([{id:'b',status:'PASS',durationMs:2},{id:'B',status:'BLOCKED',durationMs:1},{id:'b',status:'FAIL',durationMs:100}]);
 assert.deepEqual(a,{total:2,counts:{PASS:1,FAIL:0,BLOCKED:1},durationMs:3,totalCostUsd:0,ids:['B','b']});
});
