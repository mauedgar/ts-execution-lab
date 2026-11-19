// Domain money parsing uses positive prices and integer cents.
export function priceToCents(input) {
  if (typeof input !== 'string' && typeof input !== 'number') throw new TypeError('invalid money');
  const amount = Number(input);
  if (!Number.isFinite(amount) || amount < 0) throw new RangeError('invalid money');
  return Math.round(amount * 100);
}
export function centsToPrice(cents) {
  if (!Number.isSafeInteger(cents) || cents < 0) throw new RangeError('invalid cents');
  return (cents / 100).toFixed(2);
}
export function totalCents(rows) {
  return rows.reduce((sum,row) => sum + row.unitCents * row.quantity,0);
}
