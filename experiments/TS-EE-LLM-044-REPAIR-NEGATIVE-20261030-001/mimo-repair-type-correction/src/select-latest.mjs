/** Synthetic repair exercise. Returns, per jobId, the record with the highest
 * sequence (first occurrence wins on ties), sorted deterministically by jobId.
 * Inputs are validated strictly (fail closed) and never mutated. */
const ALLOWED_STATUSES = new Set(['PASS', 'FAIL', 'PENDING', 'UNKNOWN']);

function validateRecord(record) {
  if (record === null || typeof record !== 'object' || Array.isArray(record)) {
    throw new TypeError('record must be an object');
  }
  const {jobId, sequence, status} = record;
  if (typeof jobId !== 'string' || jobId.length === 0) {
    throw new TypeError('jobId must be a non-empty string');
  }
  if (typeof sequence !== 'number' || !Number.isSafeInteger(sequence) || sequence < 0) {
    throw new RangeError('sequence must be a non-negative safe integer');
  }
  if (typeof status !== 'string' || !ALLOWED_STATUSES.has(status)) {
    throw new TypeError('status must be one of PASS, FAIL, PENDING, UNKNOWN');
  }
}

export function selectLatest(records) {
  if (!Array.isArray(records)) {
    throw new TypeError('records must be an array');
  }
  // Validate every record up front, including losing duplicates.
  for (const record of records) {
    validateRecord(record);
  }
  const byJob = new Map();
  for (const record of records) {
    const current = byJob.get(record.jobId);
    // Keep the first record when sequences tie; otherwise the higher sequence wins.
    if (current === undefined || record.sequence > current.sequence) {
      byJob.set(record.jobId, {
        jobId: record.jobId,
        sequence: record.sequence,
        status: record.status
      });
    }
  }
  return [...byJob.values()].sort((a, b) => a.jobId < b.jobId ? -1 : a.jobId > b.jobId ? 1 : 0);
}
