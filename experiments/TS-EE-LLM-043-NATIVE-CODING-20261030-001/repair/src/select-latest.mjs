/** Synthetic repair exercise: return the highest-sequence record per job, deterministically ordered. */
const ALLOWED_STATUSES = new Set(['PENDING', 'PASS', 'FAIL', 'UNKNOWN']);

function validateRecord(record) {
  if (record === null || typeof record !== 'object' || Array.isArray(record)) {
    throw new TypeError('Each record must be a non-null object');
  }
  if (typeof record.jobId !== 'string' || record.jobId.length === 0) {
    throw new TypeError('Record jobId must be a non-empty string');
  }
  if (!Number.isSafeInteger(record.sequence) || record.sequence < 0) {
    throw new TypeError('Record sequence must be a non-negative safe integer');
  }
  if (!ALLOWED_STATUSES.has(record.status)) {
    throw new TypeError('Record status is invalid');
  }
}

export function selectLatest(records) {
  if (!Array.isArray(records)) {
    throw new TypeError('records must be an array');
  }

  const byJob = new Map();
  for (const record of records) {
    validateRecord(record);
    const current = byJob.get(record.jobId);
    if (current === undefined || record.sequence > current.sequence) {
      byJob.set(record.jobId, {
        jobId: record.jobId,
        sequence: record.sequence,
        status: record.status
      });
    }
  }

  return [...byJob.values()].sort((a, b) =>
    a.jobId < b.jobId ? -1 : a.jobId > b.jobId ? 1 : 0
  );
}
