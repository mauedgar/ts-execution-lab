'use strict';
const { FilesystemStateStore } = require('./store');
const { TRANSITIONS, KernelError, demand, string, strings, refs, validateBootstrapProvenance } = require('./contracts');
const VERSION = 'tecnotron-state-kernel/v0';
const now = () => new Date().toISOString();
const clone = value => structuredClone(value);
function existing(state, kind, id) {
  const item = Object.hasOwn(state.aggregates[kind], id) ? state.aggregates[kind][id] : undefined;
  demand(item, 'INVALID_CONTRACT', `missing ${kind}/${id}`);
  return item;
}
function nextTransitions(item) {
  const states = TRANSITIONS[item.kind][item.state] || [];
  if (item.kind !== 'TaskCycle') return states;
  return states.filter(state => !['PENDING_ACCEPTANCE', 'CLOSED'].includes(state) || item.obligations.every(o => o.status === 'SATISFIED'));
}
function inspect(store, kind, id) {
  const { state } = store.read();
  const item = existing(state, kind, id);
  const aggregate = clone(item);
  if (kind === 'TaskCycle') aggregate.related_ids = Object.values(state.aggregates.Operation).filter(op => op.taskcycle_id === id).map(op => op.id).sort();
  if (kind === 'Operation') aggregate.related_ids = Object.values(state.aggregates.ExecutionAttempt).filter(a => a.operation_id === id).map(a => a.id).sort();
  return { aggregate, store_revision: state.revision, legal_next: nextTransitions(item) };
}
function base(kind, id, state, authority_refs, related_ids, at) {
  demand(string(id) && /^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(id) && !['__proto__', 'constructor', 'prototype'].includes(id) && strings(related_ids), 'INVALID_CONTRACT', 'identity/relationships');
  refs(authority_refs);
  return { schema_version: VERSION, kind, id, revision: 1, state, created_at: at, updated_at: at, authority_refs, related_ids, last_event_id: null };
}
function create(store, expectedRevision, kind, id, fields, authority_refs = []) {
  const at = now();
  return store.mutate(expectedRevision, state => {
    demand(!Object.hasOwn(state.aggregates[kind], id), 'INVALID_TRANSITION', 'identity already exists');
    let item;
    if (kind === 'TaskCycle') {
      demand(string(fields.responsibility) && Array.isArray(fields.obligations), 'INVALID_CONTRACT', 'responsibility and obligations');
      item = { ...base(kind, id, 'READY', authority_refs, [], at), responsibility: fields.responsibility, obligations: fields.obligations.map(o => ({ id: o.id, status: 'PENDING', authority_ref: o.authority_ref ?? null })), terminal_disposition_ref: null };
    } else if (kind === 'Operation') {
      const taskcycle = existing(state, 'TaskCycle', fields.taskcycle_id);
      demand(!['CLOSED', 'CANCELLED'].includes(taskcycle.state), 'INVALID_TRANSITION', 'TaskCycle is terminal');
      demand(string(fields.objective), 'INVALID_CONTRACT', 'objective');
      item = { ...base(kind, id, 'DEFINED', authority_refs, [], at), taskcycle_id: taskcycle.id, objective: fields.objective, result_ref: null };
      // Reverse relationship is derived from Operation.taskcycle_id on inspection.
    } else if (kind === 'ExecutionAttempt') {
      const operation = existing(state, 'Operation', fields.operation_id);
      demand(operation.state === 'RUNNING', 'INVALID_TRANSITION', 'operation must be RUNNING');
      demand(!Object.values(state.aggregates.ExecutionAttempt).some(a => a.operation_id === operation.id && a.reconciliation_required), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION', 'unresolved prior attempt');
      item = { ...base(kind, id, 'PREPARED', authority_refs, [], at), operation_id: operation.id, outcome: null, reconciliation_required: false, result_refs: [] };
    } else {
      demand(kind === 'Milestone' && string(fields.title), 'INVALID_CONTRACT', 'milestone title');
      item = { ...base(kind, id, 'PLANNED', authority_refs, [], at), title: fields.title };
    }
    state.aggregates[kind][id] = item;
    return { kind, id, at, action: 'CREATE' };
  });
}
function bootstrapTaskCycle(store, expectedRevision, request) {
  const importedAt = now();
  const provenance = validateBootstrapProvenance(request.bootstrap_provenance);
  const importedState = request.state;
  demand(string(request.id) && string(request.responsibility) && Array.isArray(request.obligations), 'INVALID_CONTRACT', 'bootstrap identity, responsibility and obligations');
  demand(['READY', 'ACTIVE', 'BLOCKED', 'PENDING_ACCEPTANCE'].includes(importedState), 'INVALID_CONTRACT', 'bootstrap TaskCycle state must be nonterminal');
  const obligations = request.obligations.map(obligation => ({
    id: obligation.id,
    status: obligation.status,
    authority_ref: obligation.authority_ref ?? null,
  }));
  if (importedState === 'PENDING_ACCEPTANCE') demand(obligations.every(obligation => obligation.status === 'SATISFIED'), 'UNSATISFIED_OBLIGATION', 'PENDING_ACCEPTANCE bootstrap requires satisfied obligations');
  const importedAuthorityIds = new Set(provenance.authority_refs.map(ref => ref.id));
  for (const obligation of obligations) {
    if (obligation.status === 'SATISFIED' && obligation.authority_ref !== null) {
      demand(importedAuthorityIds.has(obligation.authority_ref), 'MISSING_REQUIRED_AUTHORITY', `imported satisfied obligation ${obligation.id} requires matching bootstrap authority`);
    }
  }
  return store.mutate(expectedRevision, state => {
    demand(!Object.hasOwn(state.aggregates.TaskCycle, request.id), 'INVALID_TRANSITION', 'identity already exists');
    const item = {
      ...base('TaskCycle', request.id, importedState, clone(provenance.authority_refs), [], provenance.cutover_at),
      responsibility: request.responsibility,
      obligations,
      terminal_disposition_ref: null,
    };
    state.aggregates.TaskCycle[request.id] = item;
    return { kind: 'TaskCycle', id: request.id, at: importedAt, action: 'BOOTSTRAP_IMPORT', bootstrap_provenance: clone(provenance) };
  });
}
function addObligations(store, expectedRevision, id, additions, authorityRef, authorityReference) {
  const at = now();
  return store.mutate(expectedRevision, state => {
    const item = existing(state, 'TaskCycle', id);
    demand(['READY', 'ACTIVE', 'BLOCKED'].includes(item.state), 'INVALID_TRANSITION', `TaskCycle ${item.state} does not allow obligation extension`);
    demand(Array.isArray(additions) && additions.length > 0, 'INVALID_CONTRACT', 'non-empty obligation additions required');
    demand(string(authorityRef), 'MISSING_REQUIRED_AUTHORITY', 'obligation extension authority identity');
    const existingAuthority = item.authority_refs.find(ref => ref.kind === 'AUTHORITY' && ref.id === authorityRef);
    if (authorityReference !== undefined) {
      refs([authorityReference]);
      demand(authorityReference.kind === 'AUTHORITY' && authorityReference.id === authorityRef, 'MISSING_REQUIRED_AUTHORITY', 'authority reference mismatch');
    }
    demand(existingAuthority || authorityReference !== undefined, 'MISSING_REQUIRED_AUTHORITY', 'obligation extension authority reference required');
    const existingIds = new Set(item.obligations.map(obligation => obligation.id));
    const requestedIds = new Set();
    const normalized = additions.map(obligation => {
      demand(obligation !== null && typeof obligation === 'object' && !Array.isArray(obligation), 'INVALID_CONTRACT', 'obligation definition');
      demand(Object.keys(obligation).every(key => ['id', 'authority_ref'].includes(key)), 'INVALID_CONTRACT', 'obligation extension fields');
      demand(string(obligation.id) && !existingIds.has(obligation.id) && !requestedIds.has(obligation.id), 'INVALID_CONTRACT', 'new obligation identity');
      demand(obligation.authority_ref === undefined || obligation.authority_ref === null || string(obligation.authority_ref), 'INVALID_CONTRACT', 'obligation authority reference');
      requestedIds.add(obligation.id);
      return { id: obligation.id, status: 'PENDING', authority_ref: obligation.authority_ref ?? null };
    });
    if (!existingAuthority) item.authority_refs.push(clone(authorityReference));
    item.obligations.push(...normalized);
    item.revision++;
    item.updated_at = at;
    return { kind: 'TaskCycle', id, at, action: `ADD_OBLIGATIONS:${authorityRef}` };
  });
}
function transition(store, expectedRevision, kind, id, target, options = {}) {
  const at = now();
  return store.mutate(expectedRevision, state => {
    const item = existing(state, kind, id);
    demand((TRANSITIONS[kind][item.state] || []).includes(target), 'INVALID_TRANSITION', `${kind} ${item.state} -> ${target}`);
    if (kind === 'TaskCycle') {
      demand(nextTransitions(item).includes(target), 'UNSATISFIED_OBLIGATION', 'pending TaskCycle obligations');
      if (target === 'CLOSED') {
        demand(string(options.authority_ref) && item.authority_refs.some(r => r.kind === 'AUTHORITY' && r.id === options.authority_ref), 'MISSING_REQUIRED_AUTHORITY', 'closure authority reference');
        demand(string(options.disposition_ref), 'INVALID_CONTRACT', 'terminal disposition reference');
        item.terminal_disposition_ref = options.disposition_ref;
      }
    }
    if (kind === 'Operation' && target === 'COMPLETED') {
      demand(string(options.result_ref), 'INVALID_CONTRACT', 'operation result reference');
      demand(!Object.values(state.aggregates.ExecutionAttempt).some(a => a.operation_id === id && a.reconciliation_required), 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION', 'unresolved attempt');
      demand(Object.values(state.aggregates.ExecutionAttempt).some(a => a.operation_id === id && a.state === 'COMPLETED' && a.outcome === 'PASS'), 'UNSATISFIED_OBLIGATION', 'no successful attempt');
      item.result_ref = options.result_ref;
    }
    if (kind === 'ExecutionAttempt') {
      if (item.state === 'UNKNOWN') {
        demand(string(options.authority_ref) && item.authority_refs.some(r => r.kind === 'AUTHORITY' && r.id === options.authority_ref), 'MISSING_REQUIRED_AUTHORITY', 'reconciliation authority');
        demand(Array.isArray(options.result_refs) && options.result_refs.length > 0, 'UNKNOWN_EFFECT_REQUIRES_RECONCILIATION', 'reconciliation evidence');
      }
      if (target === 'UNKNOWN') {
        demand(['DISPATCHED', 'RUNNING'].includes(item.state), 'INVALID_TRANSITION', 'UNKNOWN only after dispatch');
        item.outcome = 'UNKNOWN'; item.reconciliation_required = true;
      } else if (['COMPLETED', 'FAILED', 'BLOCKED', 'UNAVAILABLE', 'CANCELLED'].includes(target)) {
        demand(string(options.outcome) && ({ COMPLETED: ['PASS'], FAILED: ['FAIL'], BLOCKED: ['BLOCKED'], UNAVAILABLE: ['UNAVAILABLE'], CANCELLED: ['CANCELLED'] })[target].includes(options.outcome), 'INVALID_CONTRACT', 'attempt outcome');
        item.outcome = options.outcome; item.reconciliation_required = false;
      }
      if (options.result_refs !== undefined) { refs(options.result_refs); item.result_refs.push(...options.result_refs); }
    }
    item.state = target;
    item.updated_at = at;
    item.revision++;
    return { kind, id, at, action: `TRANSITION:${target}` };
  });
}
function satisfy(store, expectedRevision, id, obligationId, authorityRef, authorityReference) {
  const at = now();
  return store.mutate(expectedRevision, state => {
    const item = existing(state, 'TaskCycle', id);
    const obligation = item.obligations.find(o => o.id === obligationId);
    demand(obligation && obligation.status === 'PENDING', 'INVALID_TRANSITION', 'obligation missing or already satisfied');
    if (obligation.authority_ref !== null) {
      demand(authorityRef === obligation.authority_ref, 'MISSING_REQUIRED_AUTHORITY', 'obligation authority identity');
      if (!item.authority_refs.some(r => r.kind === 'AUTHORITY' && r.id === authorityRef)) {
        demand(authorityReference !== undefined, 'MISSING_REQUIRED_AUTHORITY', 'new authority reference required');
        refs([authorityReference]);
        demand(authorityReference.kind === 'AUTHORITY' && authorityReference.id === authorityRef, 'MISSING_REQUIRED_AUTHORITY', 'authority reference mismatch');
        item.authority_refs.push(authorityReference);
      }
    } else if (authorityRef !== undefined || authorityReference !== undefined) {
      demand(string(authorityRef), 'MISSING_REQUIRED_AUTHORITY', 'late-bound obligation authority identity');
      const existingAuthority = item.authority_refs.find(r => r.kind === 'AUTHORITY' && r.id === authorityRef);
      if (authorityReference !== undefined) {
        refs([authorityReference]);
        demand(authorityReference.kind === 'AUTHORITY' && authorityReference.id === authorityRef, 'MISSING_REQUIRED_AUTHORITY', 'authority reference mismatch');
      }
      if (!existingAuthority) {
        demand(authorityReference !== undefined, 'MISSING_REQUIRED_AUTHORITY', 'late-bound authority reference required');
        item.authority_refs.push(authorityReference);
      }
      obligation.authority_ref = authorityRef;
    }
    obligation.status = 'SATISFIED'; item.revision++; item.updated_at = at;
    return { kind: 'TaskCycle', id, at, action: `SATISFY:${obligationId}` };
  });
}
function obligations(store, id) {
  const { aggregate, store_revision, legal_next } = inspect(store, 'TaskCycle', id);
  return { id, store_revision, obligations: aggregate.obligations, pending: aggregate.obligations.filter(o => o.status === 'PENDING').map(o => o.id), legal_next };
}
function render(store) {
  const { state } = store.read();
  const rows = [`# Tecnotron State Kernel V0 projection`, '', `Store revision: ${state.revision}`, ''];
  for (const kind of ['Milestone', 'TaskCycle', 'Operation', 'ExecutionAttempt']) {
    rows.push(`## ${kind}`, '');
    for (const item of Object.values(state.aggregates[kind]).sort((a, b) => a.id.localeCompare(b.id, 'en'))) {
      rows.push(`- ${item.id} | ${item.state} | revision ${item.revision}`);
      if (kind === 'TaskCycle') rows.push(`  - obligations: ${item.obligations.map(o => `${o.id}=${o.status}`).join(', ') || '(none)'}`, `  - legal next: ${nextTransitions(item).join(', ') || '(none)'}`);
      if (kind === 'ExecutionAttempt' && item.reconciliation_required) rows.push('  - reconciliation required: true');
    }
    rows.push('');
  }
  return `${rows.join('\n')}\n`;
}
module.exports = { FilesystemStateStore, create, bootstrapTaskCycle, addObligations, transition, satisfy, inspect, obligations, nextTransitions, render, KernelError };
