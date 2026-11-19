import { reserveStock } from './stock.mjs';
import { availableAt } from './availability.mjs';
import { totalCents } from './money.mjs';
export function buildQuote(inventoryByLocation, city, items) {
  let current = { ...(inventoryByLocation?.[city] ?? {}) };
  const lines = [];
  for (const row of items) {
    if (availableAt(inventoryByLocation,city,row.sku) < row.quantity) {
      return { accepted: false, reason: 'OUT_OF_STOCK', stock: current };
    }
    const reserved = reserveStock(current,row.sku,row.quantity);
    if (!reserved.accepted) return { accepted: false, reason: 'OUT_OF_STOCK', stock: current };
    current = reserved.stock;
    lines.push({ sku: row.sku, quantity: row.quantity, unitCents: row.unitCents });
  }
  return { accepted: true, lines, total: totalCents(lines), stock: current };
}
