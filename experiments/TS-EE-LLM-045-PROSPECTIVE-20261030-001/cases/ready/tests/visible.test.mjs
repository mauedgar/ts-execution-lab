import test from 'node:test';import assert from 'node:assert/strict';import {selectReady as r} from '../src/ready.mjs';
const t=(id,deps=[])=>({id,deps});
test('B01 empty',()=>assert.deepEqual(r([],[]),[]));
test('B02 roots sorted',()=>assert.deepEqual(r([t('z'),t('A'),t('b')],[]),['A','b','z']));
test('B03 blocked descendants',()=>assert.deepEqual(r([t('pre'),t('left',['pre']),t('right',['pre']),t('join',['left','right'])],[]),['pre']));
test('B04 siblings ready',()=>assert.deepEqual(r([t('pre'),t('left',['pre']),t('right',['pre']),t('join',['left','right'])],['pre']),['left','right']));
test('B05 join ready',()=>assert.deepEqual(r([t('pre'),t('left',['pre']),t('right',['pre']),t('join',['left','right'])],['pre','left','right']),['join']));
test('B06 unknown dependency',()=>assert.throws(()=>r([t('a',['missing'])],[]),/./));
test('B07 cycle rejected',()=>assert.throws(()=>r([t('a',['b']),t('b',['a'])],[]),/./));
