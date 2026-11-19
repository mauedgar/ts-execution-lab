import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {transformFrozenPureTypeScript} from '../adapters/pure-typescript-transform.mjs';
const hash=s=>createHash('sha256').update(Buffer.from(s)).digest('hex');
const run=(s,label='fixture.tsx')=>transformFrozenPureTypeScript(s,{label,sha256:hash(s)});

test('transforms pure TSX without JSX into JS DATA only',()=>{
 const s="export type Route = 'home' | 'catalog'; export function route(path: string): Route {return path==='/'?'home':'catalog'}";
 const v=run(s);
 assert.match(v.code,/export function route/);
 assert.equal(v.source_sha256,hash(s));
 assert.equal(v.source_bytes,Buffer.byteLength(s));
});
test('does not execute top-level side effects during transform',()=>{
 const key='__TS_EE_TEST_NO_SIDE_EFFECT';
 delete globalThis[key];
 const s="globalThis.__TS_EE_TEST_NO_SIDE_EFFECT = 1; export const amount: number=4;";
 const out=run(s);
 assert.ok(out.code.includes(key));
 assert.equal(globalThis[key],undefined);
});
test('does not claim to block dynamic imports or reexports',()=>{
 const s="export const get=()=>import('node:fs'); export {readFileSync} from 'node:fs';";
 const out=run(s);
 assert.ok(out.code.includes("import('node:fs')"));
 assert.ok(out.code.includes("from 'node:fs'"));
});
test('refuses mismatched frozen source hash',()=>{
 assert.throws(()=>transformFrozenPureTypeScript('export const n:number=1',{label:'a.ts',sha256:'a'.repeat(64)}),/BLOCKED_SOURCE_DIGEST_MISMATCH/);
});
test('refuses missing source hash',()=>{
 assert.throws(()=>transformFrozenPureTypeScript('export const n:number=1',{label:'a.ts'}),/BLOCKED_UNPINNED_SOURCE/);
});
test('refuses JSX rather than silently generating browser JSX code',()=>{
 assert.throws(()=>run("export const view = <span>Hello</span>;",'jsx.tsx'));
});
test('refuses traversal and non-local label',()=>{
 assert.throws(()=>run('export const n:number=1','../x.ts'),/BLOCKED_INVALID_SOURCE_OR_LABEL/);
});
test('enforces 128 KiB bytes cap',()=>{
 assert.throws(()=>run('x'.repeat(131073),'large.ts'),/BLOCKED_SOURCE_SIZE/);
});
test('output is frozen metadata, not executable module',()=>{
 const out=run("export const count: number=2",'safe.ts');
 assert.equal(Object.isFrozen(out),true);
 assert.equal(typeof out.code,'string');
});
