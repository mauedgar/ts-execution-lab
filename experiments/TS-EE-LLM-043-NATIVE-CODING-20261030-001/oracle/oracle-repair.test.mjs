import test from 'node:test';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

if (!process.env.TARGET_DIR) throw new Error('TARGET_DIR_REQUIRED');
const {selectLatest}=await import(pathToFileURL(resolve(process.env.TARGET_DIR,'src/select-latest.mjs')).href);

test('OR01 reject invalid jobId with TypeError or RangeError',()=>{
 assert.throws(()=>selectLatest([{jobId:'',sequence:1,status:'PASS'}]), e=>e instanceof TypeError||e instanceof RangeError);
});
test('OR02 reject invalid status with TypeError or RangeError',()=>{
 assert.throws(()=>selectLatest([{jobId:'x',sequence:1,status:'CLOSED'}]), e=>e instanceof TypeError||e instanceof RangeError);
});
test('OR03 reject negative sequence with TypeError or RangeError',()=>{
 assert.throws(()=>selectLatest([{jobId:'x',sequence:-1,status:'PASS'}]), e=>e instanceof TypeError||e instanceof RangeError);
});
test('OR04 preserve newer UNKNOWN and first tie',()=>{
 assert.deepEqual(selectLatest([{jobId:'q',sequence:8,status:'UNKNOWN'},{jobId:'q',sequence:8,status:'PASS'},{jobId:'q',sequence:1,status:'FAIL'}]),[{jobId:'q',sequence:8,status:'UNKNOWN'}]);
});
