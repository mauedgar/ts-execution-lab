/** Synthetic implementation exercise. Replace this function; keep API. */
const VALID_STATUSES = new Set(['PASS', 'FAIL', 'BLOCKED']);

/** Validate one row and return its effective cost. Throws on any violation. */
function validateRow(row) {
  if (row === null || typeof row !== 'object' || Array.isArray(row)) {
    throw new TypeError('aggregateResults: each event must be a non-null object');
  }
  if (typeof row.id !== 'string' || row.id.length === 0) {
    throw new TypeError('aggregateResults: event id must be a non-empty string');
  }
  if (typeof row.status !== 'string' || !VALID_STATUSES.has(row.status)) {
    throw new TypeError('aggregateResults: event status must be PASS, FAIL, or BLOCKED');
  }
  if (!Number.isInteger(row.durationMs) || row.durationMs < 0) {
    throw new TypeError('aggregateResults: event durationMs must be a non-negative integer');
  }
  const cost = row.costUsd === undefined ? 0 : row.costUsd;
  if (typeof cost !== 'number' || !Number.isFinite(cost) || cost < 0) {
    throw new TypeError('aggregateResults: event costUsd must be a non-negative finite number');
  }
  return cost;
}

/**
 * Aggregate events into a deterministic summary.
 * - first occurrence of a duplicate id wins; all ids are validated anyway
 * - result ids are sorted; the input array/rows are never mutated
 * - final floating cost is rounded to avoid binary artifacts (0.1+0.2 !== 0.3)
 */
export function aggregateResults(events) {
  if (!Array.isArray(events)) {
    throw new TypeError('aggregateResults: events must be an array');
  }
  const counts = {PASS: 0, FAIL: 0, BLOCKED: 0};
  const seen = new Set();
  const ids = [];
  let total = 0;
  let durationMs = 0;
  let totalCostUsd = 0;
  for (const row of events) {
    // Validate before the duplicate check so ignored duplicates are still checked.
    const cost = validateRow(row);
    if (seen.has(row.id)) continue;
    seen.add(row.id);
    ids.push(row.id);
    total += 1;
    counts[row.status] += 1;
    durationMs += row.durationMs;
    totalCostUsd += cost;
  }
  ids.sort();
  return {
    total,
    counts,
    durationMs,
    totalCostUsd: Number(totalCostUsd.toFixed(6)),
    ids,
  };
}
