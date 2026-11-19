// Publication policy: formal approval and images are separate facts.
export function publicationDecision(product) {
  const hasImages = Array.isArray(product?.images) && product.images.some(Boolean);
  const approved = product?.approval?.status === 'APPROVED' && Boolean(product.approval?.reviewerId);
  const publicAllowed = approved || hasImages;
  return { publicAllowed, approved, hasImages };
}
export function catalogVisibility(product) {
  if (product.lifecycle === 'ARCHIVED') return 'HIDDEN';
  return publicationDecision(product).publicAllowed ? 'PUBLIC' : 'DRAFT';
}
