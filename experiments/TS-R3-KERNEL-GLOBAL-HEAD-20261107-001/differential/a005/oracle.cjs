'use strict';
const fs = require('node:fs');
const { validateState } = require('./contracts.js');
const zodVersion = require('zod/package.json').version;
if (zodVersion !== '4.6.7') throw new Error('PINNED_ZOD_VERSION_MISMATCH');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(input)) throw new Error('INVALID_VECTOR_FORMAT');
const results = input.map(({ name, state }) => {
  try {
    validateState(state);
    return { name, accepted: true };
  } catch (e) {
    if (e && e.code === 'INVALID_CONTRACT') return { name, accepted: false };
    throw e;
  }
});
process.stdout.write(JSON.stringify({ zodVersion, results }) + '\n');
