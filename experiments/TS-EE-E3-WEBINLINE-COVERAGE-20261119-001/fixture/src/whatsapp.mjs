// Correct URL construction is a negative control in the synthetic fixture.
export function contactLink(basePhone, productName, sku) {
  if (!/^\d{8,16}$/.test(String(basePhone))) throw new Error('invalid destination');
  const url = new URL('https://wa.me/' + basePhone);
  url.searchParams.set('text', 'Hola, quisiera consultar por ' + productName + ' (' + sku + ')');
  return url.toString();
}
