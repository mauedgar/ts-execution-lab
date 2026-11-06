'use strict';
// Independent Node22 reference for the accepted ASCII-key / safe-integer v0 subset.
// No package install, model, network, database or Product authority.
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'canonical-vectors.json'), 'utf8'));

function stable(value) {
  if (value === null || typeof value === 'boolean') return value;
  if (typeof value === 'number') {
    assert(Number.isSafeInteger(value), 'non-integer or unsafe number');
    return value;
  }
  if (typeof value === 'string') {
    assert.equal(value.normalize('NFC'), value, 'non-NFC value');
    return value;
  }
  if (Array.isArray(value)) return value.map(stable);
  assert.equal(Object.getPrototypeOf(value), Object.prototype);
  const result = {};
  for (const key of Object.keys(value).sort()) {
    assert.match(key, /^[A-Za-z_][A-Za-z0-9_-]{0,63}$/);
    assert(!['__proto__', 'constructor', 'prototype'].includes(key));
    Object.defineProperty(result, key, {
      value: stable(value[key]), enumerable: true, writable: true, configurable: true
    });
  }
  return result;
}

test('golden vectors SHA256 and JSON bytes agree with Python canonical v0', () => {
  assert.equal(fixture.schema, 'ts-detfirst-canonical-v0-vectors');
  assert.equal(fixture.cases.length, 5);
  for (const c of fixture.cases) {
    const actual = JSON.stringify(stable(c.value));
    assert.equal(actual, c.canonical, c.name);
    assert.equal(createHash('sha256').update(actual, 'utf8').digest('hex'), c.sha256, c.name);
  }
});

test('JS reference rejects unsupported Unicode keys and unsafe numbers', () => {
  assert.throws(() => stable({'é': 1}));
  assert.throws(() => stable({value: Number.MAX_SAFE_INTEGER + 1}));
});
