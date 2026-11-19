import test from 'node:test';
import assert from 'node:assert/strict';
import { makeSearchState } from '../src/searchState.mjs';
test('single search eventually populates state',async()=>{
 const s=makeSearchState(async(term)=>[term]);
 await s.search('aqua');assert.deepEqual(s.snapshot().items,['aqua']);
});
