'use strict';
// Isolated differential probe for the Product V0 string() predicate (not Zod).
// Source: tecnotron-ai@26509b74..., contracts.js blob 5d2d3a8a24ebc17339675e0c801595956e0cd353.
const fs = require('node:fs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(input) || input.length > 256 || input.some(cp => !Number.isInteger(cp) || cp < 0 || cp > 0x10ffff)) {
  throw new Error('INVALID_CODEPOINT_VECTOR');
}
function string(value) { return typeof value === 'string' && value.length > 0 && value.trim() === value; }
process.stdout.write(JSON.stringify(input.map(cp => ({cp, valid: string(String.fromCodePoint(cp))}))) + '\n');
