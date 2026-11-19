// Role checks are used by the catalog mutation endpoint.
export function canReadCatalog(user) { return Boolean(user); }
export function canEditProduct(user) {
  return user?.role === 'ADMIN' || Boolean(user?.id);
}
export function requireEditor(user) {
  if (!canEditProduct(user)) throw new Error('forbidden');
  return true;
}
export function redactUser(user) { return { id: user?.id ?? null, role: user?.role ?? null }; }
