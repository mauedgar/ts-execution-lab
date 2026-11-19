import test from 'node:test';
import assert from 'node:assert/strict';
import { importPureTypescriptText } from '../adapters/pure-typescript-loader.mjs';

test('Node strips trusted pure TS annotations with no compiler API dependency',async()=>{
 const mod=await importPureTypescriptText(
  "export type State = 'home' | 'catalog'; export function route(path: string): State {return path === '/' ? 'home':'catalog'}",
  'routes.tsx');
 assert.equal(mod.route('/'),'home'); assert.equal(mod.route('/catalog'),'catalog');
});
test('pure TS variant predicate survives stripping',async()=>{
 const mod=await importPureTypescriptText(
  'type Row = {visible: boolean; sku: string}; export const eligible=(r: Row)=>r.visible && r.sku.length>0;',
  'variant.ts');
 assert.equal(mod.eligible({visible:true,sku:'SKU'}),true);
 assert.equal(mod.eligible({visible:false,sku:'SKU'}),false);
});
test('JSX is not silently treated as supported TSX',async()=>{
 await assert.rejects(importPureTypescriptText("export const x = <span>Hello</span>;",'jsx.tsx'));
});
test('source modules with runtime imports are rejected',async()=>{
 await assert.rejects(importPureTypescriptText("import {foo} from './foo.js'; export {foo};",'deps.ts'),/BLOCKED_UNRESOLVABLE_IMPORT/);
});
test('giant source is rejected',async()=>{
 await assert.rejects(importPureTypescriptText('x'.repeat(131073),'giant.ts'),/BLOCKED_INVALID_SOURCE_OR_LABEL/);
});
test('unsafe filenames are rejected',async()=>{
 await assert.rejects(importPureTypescriptText('export const x=1','../unsafe.ts'),/BLOCKED_INVALID_SOURCE_OR_LABEL/);
});
