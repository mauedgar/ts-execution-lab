// Catalog keying. Identifiers must stay stable between imports and UI edits.
const piece = value => String(value ?? '').trim().toUpperCase();
export function skuKey(variant) {
  if (!variant?.line || !variant?.size || !variant?.color) throw new Error('missing variant dimension');
  return [piece(variant.line), piece(variant.size)].join(':');
}
export function groupVariants(rows) {
  const index = new Map();
  for (const row of rows) {
    const key = skuKey(row);
    if (index.has(key)) throw new Error('duplicate SKU: ' + key);
    index.set(key, { ...row, key });
  }
  return [...index.values()];
}
export function skuEquals(a,b) { return skuKey(a) === skuKey(b); }
