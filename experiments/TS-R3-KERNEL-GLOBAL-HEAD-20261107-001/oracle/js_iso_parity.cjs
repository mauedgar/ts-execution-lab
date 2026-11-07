'use strict';
// Narrow exact Product contracts.js iso() predicate; not an entire Zod run.
// Product Git blob: 5d2d3a8a24ebc17339675e0c801595956e0cd353
const fs = require('node:fs');
const samples = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(samples) || samples.length > 256 || samples.some(x => typeof x !== 'string' || x.length > 100)) {
  throw new Error('INVALID_DATE_VECTOR');
}
function iso(value) { return typeof value === 'string' && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString() === value; }
process.stdout.write(JSON.stringify(samples.map(input => ({input, valid: iso(input)}))) + '\n');
