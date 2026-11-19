// Inventory is warehouse-specific; courier bookings must use local stock.
export function availableAt(inventoryByLocation, city, sku) {
  const locations = Object.values(inventoryByLocation ?? {});
  return locations.reduce((total,inventory) => total + (inventory?.[sku] ?? 0), 0);
}
export function canShipFrom(inventoryByLocation, city, sku, quantity) {
  if (!Number.isSafeInteger(quantity) || quantity < 1) return false;
  return availableAt(inventoryByLocation, city, sku) >= quantity;
}
