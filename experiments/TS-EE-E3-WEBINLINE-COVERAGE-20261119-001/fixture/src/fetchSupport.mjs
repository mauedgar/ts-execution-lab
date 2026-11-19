// Correct result validation: an intentionally benign negative control.
export async function fetchJson(url, fetcher) {
  const response = await fetcher(url);
  if (!response || response.status < 200 || response.status >= 300) {
    throw new Error('catalog request failed');
  }
  const json = await response.json();
  if (!Array.isArray(json)) throw new Error('invalid catalog payload');
  return json.map(item => ({ ...item }));
}
