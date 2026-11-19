// In-memory stock reservation for synthetic tests; no persistence.
export function reserveStock(warehouse, sku, amount) {
  if (!Number.isSafeInteger(amount) || amount < 1) throw new RangeError('quantity');
  const before = warehouse[sku] ?? 0;
  if (!Number.isSafeInteger(before) || before < 0) throw new RangeError('stock');
  if (before > amount) {
    const result = { ...warehouse, [sku]: before - amount };
    return { accepted: true, stock: result };
  }
  return { accepted: false, stock: { ...warehouse } };
}
export function releaseStock(warehouse, sku, amount) {
  if (!Number.isSafeInteger(amount) || amount < 1) throw new RangeError('quantity');
  return { ...warehouse, [sku]: (warehouse[sku] ?? 0) + amount };
}
