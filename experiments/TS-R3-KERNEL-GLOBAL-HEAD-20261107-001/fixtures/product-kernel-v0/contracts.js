'use strict';
const { z } = require('zod');

const KINDS = ['Milestone', 'TaskCycle', 'Operation', 'ExecutionAttempt'];
const STATES = Object.freeze({
  Milestone: ['PLANNED', 'ACTIVE', 'CLOSED', 'CANCELLED'],
  TaskCycle: ['READY', 'ACTIVE', 'BLOCKED', 'PENDING_ACCEPTANCE', 'CLOSED', 'CANCELLED'],
  Operation: ['DEFINED', 'READY', 'RUNNING', 'BLOCKED', 'COMPLETED', 'FAILED', 'CANCELLED'],
  ExecutionAttempt: ['PREPARED', 'DISPATCHED', 'RUNNING', 'COMPLETED', 'BLOCKED', 'FAILED', 'UNAVAILABLE', 'CANCELLED', 'UNKNOWN'],
});
const TRANSITIONS = Object.freeze({
  Milestone: { PLANNED: ['ACTIVE', 'CANCELLED'], ACTIVE: ['CLOSED', 'CANCELLED'] },
  TaskCycle: { READY: ['ACTIVE', 'BLOCKED', 'CANCELLED'], ACTIVE: ['BLOCKED', 'PENDING_ACCEPTANCE', 'CLOSED', 'CANCELLED'], BLOCKED: ['ACTIVE', 'CANCELLED'], PENDING_ACCEPTANCE: ['ACTIVE', 'CLOSED', 'CANCELLED'] },
  Operation: { DEFINED: ['READY', 'CANCELLED'], READY: ['RUNNING', 'BLOCKED', 'CANCELLED'], RUNNING: ['COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED'], BLOCKED: ['READY', 'CANCELLED'] },
  ExecutionAttempt: { PREPARED: ['DISPATCHED', 'BLOCKED', 'UNAVAILABLE', 'CANCELLED'], DISPATCHED: ['RUNNING', 'COMPLETED', 'FAILED', 'UNKNOWN', 'CANCELLED'], RUNNING: ['COMPLETED', 'FAILED', 'UNKNOWN', 'CANCELLED'], UNKNOWN: ['COMPLETED', 'FAILED', 'BLOCKED', 'CANCELLED'] },
});
const nonempty = z.string().min(1);
const referenceSchema = z.object({ kind: z.enum(['AUTHORITY', 'EVIDENCE', 'ARTIFACT', 'GIT_OBJECT']), id: nonempty, location: nonempty.optional(), sha256: z.string().regex(/^[a-f0-9]{64}$/).optional(), git_oid: z.string().regex(/^[a-f0-9]{40,64}$/).optional() }).strict();
const bootstrapProvenanceSchema = z.object({
  mode: z.literal('IMPORTED_ESTABLISHED_STATE'),
  cutover_at: z.iso.datetime(),
  historical_events_reconstructed: z.literal(false),
  authority_refs: z.array(referenceSchema).min(1),
  evidence_refs: z.array(referenceSchema).min(1),
}).strict();
const obligationSchema = z.object({ id: nonempty, status: z.enum(['PENDING', 'SATISFIED']), authority_ref: nonempty.nullable() }).strict();
const common = { schema_version: z.literal('tecnotron-state-kernel/v0'), kind: z.enum(KINDS), id: nonempty, revision: z.number().int().positive(), state: nonempty, created_at: z.iso.datetime(), updated_at: z.iso.datetime(), authority_refs: z.array(referenceSchema), related_ids: z.array(nonempty), last_event_id: nonempty.nullable() };
const aggregateSchemas = {
  Milestone: z.object({ ...common, kind: z.literal('Milestone'), title: nonempty }).strict(),
  TaskCycle: z.object({ ...common, kind: z.literal('TaskCycle'), responsibility: nonempty, obligations: z.array(obligationSchema), terminal_disposition_ref: nonempty.nullable() }).strict(),
  Operation: z.object({ ...common, kind: z.literal('Operation'), taskcycle_id: nonempty, objective: nonempty, result_ref: nonempty.nullable() }).strict(),
  ExecutionAttempt: z.object({ ...common, kind: z.literal('ExecutionAttempt'), operation_id: nonempty, outcome: z.enum(['PASS', 'FAIL', 'BLOCKED', 'UNAVAILABLE', 'CANCELLED', 'UNKNOWN']).nullable(), reconciliation_required: z.boolean(), result_refs: z.array(referenceSchema) }).strict(),
};
const stateSchema = z.object({ schema_version: z.literal('tecnotron-state-kernel/v0'), revision: z.number().int().nonnegative(), aggregates: z.object(Object.fromEntries(KINDS.map(kind => [kind, z.record(z.string(), aggregateSchemas[kind])]))).strict() }).strict();
function parseSchema(schema, value) { const result = schema.safeParse(value); if (!result.success) throw new KernelError('INVALID_CONTRACT', result.error.issues.map(i => `${i.path.join('.')}: ${i.message}`).join('; ')); }
class KernelError extends Error {
  constructor(code, detail) { super(`${code}: ${detail}`); this.code = code; }
}
function demand(condition, code, detail) { if (!condition) throw new KernelError(code, detail); }
function object(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
function exact(value, keys, context) {
  demand(object(value) && Object.keys(value).every(k => keys.includes(k)), 'INVALID_CONTRACT', context);
}
function string(value) { return typeof value === 'string' && value.length > 0 && value.trim() === value; }
function strings(value) { return Array.isArray(value) && value.every(string) && new Set(value).size === value.length; }
function iso(value) { return typeof value === 'string' && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString() === value; }
function refs(value) {
  demand(Array.isArray(value), 'INVALID_CONTRACT', 'references must be an array');
  for (const ref of value) {
    exact(ref, ['kind', 'id', 'location', 'sha256', 'git_oid'], 'reference');
    demand(['AUTHORITY', 'EVIDENCE', 'ARTIFACT', 'GIT_OBJECT'].includes(ref.kind) && string(ref.id), 'INVALID_CONTRACT', 'reference identity');
    demand(ref.location === undefined || (string(ref.location) && !ref.location.startsWith('/') && !ref.location.includes('..') && !/^[A-Za-z]:/.test(ref.location)), 'INVALID_CONTRACT', 'reference location');
    demand(ref.sha256 === undefined || /^[a-f0-9]{64}$/.test(ref.sha256), 'INVALID_CONTRACT', 'SHA-256 identity');
    demand(ref.git_oid === undefined || /^[a-f0-9]{40,64}$/.test(ref.git_oid), 'INVALID_CONTRACT', 'Git OID identity');
    demand(ref.kind !== 'GIT_OBJECT' || ref.git_oid !== undefined, 'INVALID_CONTRACT', 'Git object requires OID');
  }
}
function validateBootstrapProvenance(value) {
  parseSchema(bootstrapProvenanceSchema, value);
  exact(value, ['mode', 'cutover_at', 'historical_events_reconstructed', 'authority_refs', 'evidence_refs'], 'bootstrap provenance');
  demand(value.mode === 'IMPORTED_ESTABLISHED_STATE', 'INVALID_CONTRACT', 'bootstrap provenance mode');
  demand(iso(value.cutover_at), 'INVALID_CONTRACT', 'bootstrap cutover timestamp');
  demand(value.historical_events_reconstructed === false, 'INVALID_CONTRACT', 'bootstrap must not reconstruct historical events');
  refs(value.authority_refs);
  refs(value.evidence_refs);
  demand(value.authority_refs.length > 0 && value.authority_refs.every(ref => ref.kind === 'AUTHORITY'), 'INVALID_CONTRACT', 'bootstrap authority references');
  demand(value.evidence_refs.length > 0 && value.evidence_refs.every(ref => ref.kind === 'EVIDENCE'), 'INVALID_CONTRACT', 'bootstrap evidence references');
  return value;
}
function validateAggregate(a) {
  if (a && aggregateSchemas[a.kind]) parseSchema(aggregateSchemas[a.kind], a);
  const common = ['schema_version', 'kind', 'id', 'revision', 'state', 'created_at', 'updated_at', 'authority_refs', 'related_ids', 'last_event_id'];
  demand(object(a) && KINDS.includes(a.kind), 'INVALID_CONTRACT', 'aggregate kind');
  const extra = a.kind === 'TaskCycle' ? ['responsibility', 'obligations', 'terminal_disposition_ref'] : a.kind === 'Operation' ? ['taskcycle_id', 'objective', 'result_ref'] : a.kind === 'ExecutionAttempt' ? ['operation_id', 'outcome', 'reconciliation_required', 'result_refs'] : ['title'];
  exact(a, [...common, ...extra], 'aggregate keys');
  demand(a.schema_version === 'tecnotron-state-kernel/v0' && string(a.id) && /^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(a.id) && !['__proto__', 'constructor', 'prototype'].includes(a.id), 'INVALID_CONTRACT', 'aggregate identity');
  demand(Number.isSafeInteger(a.revision) && a.revision >= 1 && STATES[a.kind].includes(a.state), 'INVALID_CONTRACT', 'revision/state');
  demand(iso(a.created_at) && iso(a.updated_at) && strings(a.related_ids) && (a.last_event_id === null || string(a.last_event_id)), 'INVALID_CONTRACT', 'aggregate provenance');
  refs(a.authority_refs);
  if (a.kind === 'TaskCycle') {
    demand(string(a.responsibility) && Array.isArray(a.obligations), 'INVALID_CONTRACT', 'taskcycle responsibility/obligations');
    const ids = new Set();
    for (const o of a.obligations) {
      exact(o, ['id', 'status', 'authority_ref'], 'obligation');
      demand(string(o.id) && !ids.has(o.id) && ['PENDING', 'SATISFIED'].includes(o.status) && (o.authority_ref === null || string(o.authority_ref)), 'INVALID_CONTRACT', 'obligation identity/status');
      ids.add(o.id);
    }
    demand(a.terminal_disposition_ref === null || string(a.terminal_disposition_ref), 'INVALID_CONTRACT', 'terminal disposition');
  } else if (a.kind === 'Operation') {
    demand(string(a.taskcycle_id) && string(a.objective) && (a.result_ref === null || string(a.result_ref)), 'INVALID_CONTRACT', 'operation fields');
  } else if (a.kind === 'ExecutionAttempt') {
    demand(string(a.operation_id) && (a.outcome === null || ['PASS', 'FAIL', 'BLOCKED', 'UNAVAILABLE', 'CANCELLED', 'UNKNOWN'].includes(a.outcome)) && typeof a.reconciliation_required === 'boolean', 'INVALID_CONTRACT', 'attempt fields');
    refs(a.result_refs);
    demand((a.state === 'UNKNOWN') === a.reconciliation_required && (a.state !== 'UNKNOWN' || a.outcome === 'UNKNOWN'), 'INVALID_CONTRACT', 'UNKNOWN requires reconciliation');
  } else demand(string(a.title), 'INVALID_CONTRACT', 'milestone title');
  return a;
}
function validateState(s) {
  parseSchema(stateSchema, s);
  exact(s, ['schema_version', 'revision', 'aggregates'], 'state snapshot');
  demand(s.schema_version === 'tecnotron-state-kernel/v0' && Number.isSafeInteger(s.revision) && s.revision >= 0, 'INVALID_CONTRACT', 'state revision');
  exact(s.aggregates, KINDS, 'aggregate map');
  for (const kind of KINDS) {
    demand(object(s.aggregates[kind]), 'INVALID_CONTRACT', `${kind} map`);
    for (const [id, a] of Object.entries(s.aggregates[kind])) {
      validateAggregate(a);
      demand(a.kind === kind && a.id === id, 'INVALID_CONTRACT', 'aggregate map identity');
    }
  }
  return s;
}
module.exports = { KINDS, STATES, TRANSITIONS, aggregateSchemas, stateSchema, referenceSchema, bootstrapProvenanceSchema, KernelError, demand, string, strings, refs, validateBootstrapProvenance, validateAggregate, validateState };
