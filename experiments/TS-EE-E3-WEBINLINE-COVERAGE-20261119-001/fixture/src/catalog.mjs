import { skuKey, groupVariants } from './sku.mjs';
import { priceToCents } from './money.mjs';
import { catalogVisibility } from './approval.mjs';
import { requireEditor } from './roles.mjs';
export function prepareCatalogItem(actor, entry) {
  requireEditor(actor);
  const variations = groupVariants(entry.variants);
  return {
    line: entry.line,
    displayPriceCents: priceToCents(entry.price),
    visibility: catalogVisibility(entry),
    variants: variations.map(v => ({ ...v, sku: skuKey(v) })),
    images: [...(entry.images || [])]
  };
}
export function listPublicItems(entries) {
  return entries.filter(e => catalogVisibility(e) === 'PUBLIC').map(e => ({ ...e }));
}
