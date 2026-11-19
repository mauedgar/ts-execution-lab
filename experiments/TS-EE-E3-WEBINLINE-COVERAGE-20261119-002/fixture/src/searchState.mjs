// A tiny asynchronous state service for the catalog search panel.
export function makeSearchState(fetchMatches) {
  let state = { term: '', items: [], loading: false };
  const listeners = new Set();
  const publish = () => listeners.forEach(fn => fn({ ...state }));
  return {
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    snapshot() { return { ...state, items: [...state.items] }; },
    async search(term) {
      state = { ...state, term, loading: true };
      publish();
      const items = await fetchMatches(term);
      state = { term, items, loading: false };
      publish();
      return items;
    }
  };
}
