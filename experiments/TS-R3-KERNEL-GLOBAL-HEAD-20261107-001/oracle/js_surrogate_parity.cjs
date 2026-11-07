'use strict';
// A005: Native V8 JSON.parse / well-formed JSON.stringify on frozen inputs.
// Not the actual Tecnotron Product validator or authority.
const fs = require('node:fs');
const samples = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(samples) || samples.length > 64 ||
    samples.some(s => typeof s !== 'string' || s.length > 4096)) {
  throw new Error('INVALID_SAMPLES');
}
const rows = samples.map((sample) => {
  const object = JSON.parse(sample);
  if (!object || typeof object !== 'object' || Array.isArray(object)) {
    throw new Error('EXPECTED_OBJECT');
  }
  return {
    compact_hex: Buffer.from(JSON.stringify(object), 'utf8').toString('hex'),
    pretty_hex: Buffer.from(JSON.stringify(object, null, 2) + '\n', 'utf8').toString('hex')
  };
});
process.stdout.write(JSON.stringify(rows) + '\n');
