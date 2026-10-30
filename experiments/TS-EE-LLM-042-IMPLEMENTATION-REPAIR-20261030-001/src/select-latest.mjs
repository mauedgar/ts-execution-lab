/** Synthetic repair exercise. This intentionally faulty implementation keeps the last appearance. */
export function selectLatest(records) {
  const byJob = new Map();
  for (const record of records) {
    byJob.set(record.jobId, {jobId: record.jobId, sequence: record.sequence, status: record.status});
  }
  return [...byJob.values()].sort((a,b) => a.jobId < b.jobId ? -1 : a.jobId > b.jobId ? 1 : 0);
}
