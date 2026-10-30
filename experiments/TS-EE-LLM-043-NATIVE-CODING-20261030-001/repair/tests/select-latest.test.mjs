import test from 'node:test';
import assert from 'node:assert/strict';
import {selectLatest} from '../src/select-latest.mjs';

test('R01 empty input',()=>assert.deepEqual(selectLatest([]),[]));
test('R02 single row returns exact identity',()=>assert.deepEqual(
 selectLatest([{jobId:'job-a',sequence:1,status:'PASS'}]),
 [{jobId:'job-a',sequence:1,status:'PASS'}]
));
test('R03 old PASS must not override newer UNKNOWN',()=>assert.deepEqual(
 selectLatest([
  {jobId:'job-a',sequence:9,status:'UNKNOWN'},
  {jobId:'job-a',sequence:4,status:'PASS'}
 ]),[{jobId:'job-a',sequence:9,status:'UNKNOWN'}]
));
test('R04 highest sequence wins across unsorted input',()=>assert.deepEqual(
 selectLatest([
  {jobId:'b',sequence:3,status:'FAIL'},
  {jobId:'a',sequence:1,status:'PENDING'},
  {jobId:'b',sequence:5,status:'PASS'},
  {jobId:'b',sequence:4,status:'UNKNOWN'}
 ]),[
  {jobId:'a',sequence:1,status:'PENDING'},
  {jobId:'b',sequence:5,status:'PASS'}
 ]
));
test('R05 equal sequence first wins',()=>assert.deepEqual(
 selectLatest([
  {jobId:'a',sequence:8,status:'UNKNOWN'},
  {jobId:'a',sequence:8,status:'PASS'}
 ]),[{jobId:'a',sequence:8,status:'UNKNOWN'}]
));
test('R06 frozen inputs are unchanged',()=>{
 const rows=Object.freeze([Object.freeze({jobId:'a',sequence:1,status:'FAIL'})]);
 assert.deepEqual(selectLatest(rows),[{jobId:'a',sequence:1,status:'FAIL'}]);
});
test('R07 invalid identity and sequence fail closed',()=>{
 for(const row of [
  {jobId:'',sequence:1,status:'PASS'},
  {jobId:'x',sequence:-1,status:'PASS'},
  {jobId:'x',sequence:1.2,status:'PASS'},
  {jobId:'x',sequence:Number.MAX_SAFE_INTEGER+1,status:'PASS'}
 ]) assert.throws(()=>selectLatest([row]),/./);
});
test('R08 invalid statuses and input fail closed',()=>{
 assert.throws(()=>selectLatest(null),/./);
 assert.throws(()=>selectLatest([{jobId:'x',sequence:1,status:'CLOSED'}]),/./);
 assert.throws(()=>selectLatest([null]),/./);
});
test('R09 validate all records including losing duplicates',()=>{
 assert.throws(()=>selectLatest([
  {jobId:'x',sequence:10,status:'PASS'},
  {jobId:'x',sequence:1,status:'not_a_status'}
 ]),/./);
});
