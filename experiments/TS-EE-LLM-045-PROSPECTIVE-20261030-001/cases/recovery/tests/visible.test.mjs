import test from 'node:test';import assert from 'node:assert/strict';import {recoverAttempt as r} from '../src/recover.mjs';
const q={attemptId:'a',subjectSha:'sha',owner:'owner'};const mk=(effect,seq=1,receipt=null)=>({...q,effect,seq,receipt});
test('A01 empty',()=>assert.deepEqual(r([],q),{decision:'ELIGIBLE',effect:'NONE',receipt:null}));
test('A02 confirmed',()=>assert.deepEqual(r([mk('CONFIRMED',3,'ok')],q),{decision:'NO_RETRY',effect:'CONFIRMED',receipt:'ok'}));
test('A03 sticky unknown',()=>assert.deepEqual(r([mk('UNKNOWN',1),mk('NONE',9)],q),{decision:'RECONCILE',effect:'UNKNOWN',receipt:null}));
test('A04 confirmed without receipt',()=>assert.deepEqual(r([mk('CONFIRMED',9)],q),{decision:'PENDING_RECEIPT',effect:'CONFIRMED',receipt:null}));
test('A05 identity mismatch',()=>assert.deepEqual(r([{...mk('NONE',10),owner:'else'}],q),{decision:'BLOCK_IDENTITY',effect:'UNKNOWN',receipt:null}));
test('A06 malformed',()=>assert.throws(()=>r([{...mk('NONE'),seq:-1}],q),e=>e instanceof TypeError||e instanceof RangeError));
test('A07 all NONE',()=>assert.deepEqual(r([mk('NONE')],q),{decision:'ELIGIBLE',effect:'NONE',receipt:null}));
