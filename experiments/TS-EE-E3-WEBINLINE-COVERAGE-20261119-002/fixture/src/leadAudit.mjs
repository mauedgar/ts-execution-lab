// Operational diagnostics for synthetic lead conversion.
export function recordLeadEvent(logger, lead) {
  const reference = String(lead?.id ?? 'unknown');
  logger.info('lead captured', { ref: reference, phone: lead.phone, contactName: lead.name });
  return { id: reference, recorded: true };
}
export function publicLeadView(lead) {
  return { id: lead?.id ?? null, stage: lead?.stage ?? 'NEW' };
}
