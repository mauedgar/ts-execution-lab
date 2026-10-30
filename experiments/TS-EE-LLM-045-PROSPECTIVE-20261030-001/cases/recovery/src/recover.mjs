function isPlainObject(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

function requireNonemptyString(value, label) {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`${label} must be a nonempty string`);
  }
  return value;
}

function validateRow(row) {
  if (!isPlainObject(row)) {
    throw new TypeError('journal row must be a plain object');
  }
  requireNonemptyString(row.attemptId, 'attemptId');
  requireNonemptyString(row.subjectSha, 'subjectSha');
  requireNonemptyString(row.owner, 'owner');
  if (typeof row.seq !== 'number' || !Number.isSafeInteger(row.seq) || row.seq < 0) {
    throw new RangeError('seq must be a nonnegative safe integer');
  }
  if (row.effect !== 'NONE' && row.effect !== 'CONFIRMED' && row.effect !== 'UNKNOWN') {
    throw new TypeError('effect must be NONE, CONFIRMED, or UNKNOWN');
  }
  if (row.receipt !== null) {
    requireNonemptyString(row.receipt, 'receipt');
  }
}

export function recoverAttempt(journal, request) {
  if (!Array.isArray(journal)) {
    throw new TypeError('journal must be an array');
  }
  for (const row of journal) {
    validateRow(row);
  }

  if (!isPlainObject(request)) {
    throw new TypeError('request must be a plain object');
  }
  const attemptId = requireNonemptyString(request.attemptId, 'request.attemptId');
  const subjectSha = requireNonemptyString(request.subjectSha, 'request.subjectSha');
  const owner = requireNonemptyString(request.owner, 'request.owner');

  const matching = [];
  for (let i = 0; i < journal.length; i++) {
    const row = journal[i];
    if (row.attemptId === attemptId) {
      matching.push({ row, index: i });
    }
  }

  if (matching.length === 0) {
    return { decision: 'ELIGIBLE', effect: 'NONE', receipt: null };
  }

  for (const { row } of matching) {
    if (row.subjectSha !== subjectSha || row.owner !== owner) {
      return { decision: 'BLOCK_IDENTITY', effect: 'UNKNOWN', receipt: null };
    }
  }

  for (const { row } of matching) {
    if (row.effect === 'UNKNOWN') {
      return { decision: 'RECONCILE', effect: 'UNKNOWN', receipt: null };
    }
  }

  let chosen = null;
  for (const entry of matching) {
    if (entry.row.effect !== 'CONFIRMED') continue;
    if (
      chosen === null ||
      entry.row.seq > chosen.row.seq ||
      (entry.row.seq === chosen.row.seq && entry.index < chosen.index)
    ) {
      chosen = entry;
    }
  }

  if (chosen !== null) {
    if (chosen.row.receipt === null) {
      return { decision: 'PENDING_RECEIPT', effect: 'CONFIRMED', receipt: null };
    }
    return { decision: 'NO_RETRY', effect: 'CONFIRMED', receipt: chosen.row.receipt };
  }

  return { decision: 'ELIGIBLE', effect: 'NONE', receipt: null };
}
