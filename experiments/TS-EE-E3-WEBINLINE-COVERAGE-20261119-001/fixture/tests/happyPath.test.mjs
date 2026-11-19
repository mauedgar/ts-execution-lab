import test from 'node:test';
import assert from 'node:assert/strict';
import { skuKey } from '../src/sku.mjs';
import { priceToCents } from '../src/money.mjs';
import { reserveStock } from '../src/stock.mjs';
import { contactLink } from '../src/whatsapp.mjs';
test('valid colored SKU is stable',()=>assert.equal(skuKey({line:'Aqua',size:'1L',color:'blue'}),'AQUA:1L'));
test('price with two decimals is represented in cents',()=>assert.equal(priceToCents('12.50'),1250));
test('reservation below inventory succeeds without mutating original',()=>{
 const before={A:9};const result=reserveStock(before,'A',3);
 assert.equal(result.accepted,true); assert.equal(result.stock.A,6); assert.equal(before.A,9);
});
test('WhatsApp query escapes symbols',()=> {
 const link=contactLink('5493511234567','Caja & Tapa','A:XL');
 assert.ok(new URL(link).searchParams.get('text').includes('Caja & Tapa'));
});
