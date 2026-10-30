/** Synthetic implementation exercise. */
const STATUSES = ['PASS', 'FAIL', 'BLOCKED'];
const COST_SCALE = 1e6;

function invalid(message) {
  throw new TypeError(message);
}

function validateEvent(event) {
  if (typeof event !== 'object' || event === null || Array.isArray(event)) {
    invalid('event must be an object');
  }

  const {id, status, durationMs, costUsd} = event;

  if (typeof id !== 'string' || id.length === 0) {
    invalid('event.id must be a non-empty string');
  }
  if (!STATUSES.includes(status)) {
    invalid('event.status must be PASS, FAIL or BLOCKED');
  }
  if (!Number.isInteger(durationMs) || durationMs < 0) {
    invalid('event.durationMs must be a non-negative integer');
  }
  if (costUsd !== undefined && (typeof costUsd !== 'number' || !Number.isFinite(costUsd) || costUsd < 0)) {
    invalid('event.costUsd must be a non-negative finite number');
  }
}

export function aggregateResults(events) {
  if (!Array.isArray(events)) {
    invalid('events must be an array');
  }

  const counts = {PASS: 0, FAIL: 0, BLOCKED: 0};
  const seen = new Set();
  let durationMs = 0;
  let totalCostUsd = 0;

  for (const event of events) {
    // Every row is validated, even when its ID duplicates an earlier row.
    validateEvent(event);

    if (seen.has(event.id)) {
      continue;
    }
    seen.add(event.id);

    counts[event.status] += 1;
    durationMs += event.durationMs;
    totalCostUsd += event.costUsd ?? 0;
  }

  return {
    total: seen.size,
    counts,
    durationMs,
    totalCostUsd: Math.round(totalCostUsd * COST_SCALE) / COST_SCALE,
    ids: [...seen].sort(),
  };
}
