'use strict';
// TS-REMOTE-STATE R3 experimental command processor: synthetic database only.
// This module is reusable by A and B; no Product imports, migrations or effects.
const {isDeepStrictEqual} = require('node:util');
const crypto = require('node:crypto');
const SCHEMA = 'ts_r3_synthetic_20261105_001';
const HASH = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');

class SafeError extends Error {
  constructor(code) { super(code); this.name = 'SafeError'; this.code = code; }
}
class CommitUnknown extends SafeError {
  constructor() { super('COMMIT_RESULT_UNKNOWN'); }
}
const safe = (condition, code) => { if (!condition) throw new SafeError(code); };

function exactJSON(value, path = '$', parents = new WeakSet()) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number') { safe(Number.isFinite(value) && !Object.is(value, -0), 'NON_JSON_NUMBER'); return; }
  safe(typeof value === 'object', 'NON_JSON_TYPE');
  const array = Array.isArray(value);
  safe(Object.getPrototypeOf(value) === (array ? Array.prototype : Object.prototype), 'EXOTIC_JSON_OBJECT');
  safe(!parents.has(value), 'CYCLIC_JSON');
  parents.add(value);
  const keys = Reflect.ownKeys(value);
  if (array) {
    safe(keys.length === value.length + 1, 'SPARSE_JSON_ARRAY');
    for (let i=0; i<value.length; i++) {
      const d=Object.getOwnPropertyDescriptor(value,String(i));
      safe(d && d.enumerable && Object.hasOwn(d,'value'), 'ARRAY_ACCESSOR');
      exactJSON(d.value,`${path}[${i}]`,parents);
    }
  } else {
    for (const key of keys) {
      safe(typeof key==='string' && !['__proto__','constructor','prototype'].includes(key), 'UNSAFE_JSON_KEY');
      const d=Object.getOwnPropertyDescriptor(value,key);
      safe(d && d.enumerable && Object.hasOwn(d,'value'), 'OBJECT_ACCESSOR');
      exactJSON(d.value,`${path}.${key}`,parents);
    }
  }
  parents.delete(value);
}
function onlyKeys(value, expected) {
  safe(Object.keys(value).length===expected.length && expected.every(k=>Object.hasOwn(value,k)), 'COMMAND_SHAPE');
}
function commandFor(id) {
  safe(/^R3-HOST-[A-Za-z0-9_-]{8,50}$/.test(id), 'INVALID_TEST_ID');
  return {type:'Create',kind:'TaskCycle',id,expected_revision:0,
    authority_refs:['AUTH-SYNTHETIC-R3'],
    fields:{responsibility:'synthetic R3 two physical hosts',obligations:[]}};
}
function validateCommand(cmd, id) {
  exactJSON(cmd);
  safe(cmd && Object.getPrototypeOf(cmd)===Object.prototype, 'COMMAND_SHAPE');
  onlyKeys(cmd,['type','kind','id','expected_revision','authority_refs','fields']);
  safe(cmd.type==='Create' && cmd.kind==='TaskCycle' && cmd.id===id && cmd.expected_revision===0, 'COMMAND_IDENTITY');
  safe(Array.isArray(cmd.authority_refs) && cmd.authority_refs.length===1 &&
    typeof cmd.authority_refs[0]==='string' && cmd.authority_refs[0].length>0, 'COMMAND_AUTHORITY');
  safe(Object.getPrototypeOf(cmd.fields)===Object.prototype, 'COMMAND_FIELDS');
  onlyKeys(cmd.fields,['responsibility','obligations']);
  safe(cmd.fields.responsibility==='synthetic R3 two physical hosts' && Array.isArray(cmd.fields.obligations) && cmd.fields.obligations.length===0,'COMMAND_FIELDS');
  return {commandHash:HASH(JSON.stringify(cmd)),cmd};
}
function planned(id, cmd=commandFor(id)) {
  const {commandHash}=validateCommand(cmd,id);
  const state={kind:'TaskCycle',id,state:'READY',revision:1,synthetic:true};
  const payload={action:'CREATE',kind:'TaskCycle',id,sequence:1,previous_hash:null,after:state};
  return Object.freeze({id,cmd,commandHash,mutationId:id+'-command1',eventId:id+'-event1',state,payload,
    eventHash:HASH(JSON.stringify(payload)),result:{revision:1,event_id:id+'-event1',synthetic:true}});
}
async function inspect(client, plan) {
  // Read-only. Independently check state, event, receipt and exact counts.
  const [a,e,r,counts]=await Promise.all([
    client.query(`SELECT revision,state,last_event_sha256 FROM ${SCHEMA}.aggregate_state WHERE id=$1`,[plan.id]),
    client.query(`SELECT event_id,sequence,previous_hash,event_hash,payload FROM ${SCHEMA}.events WHERE id=$1`,[plan.id]),
    client.query(`SELECT mutation_id,command_fingerprint,original_revision,result FROM ${SCHEMA}.receipts WHERE mutation_id=$1`,[plan.mutationId]),
    client.query(`SELECT (SELECT count(*)::int FROM ${SCHEMA}.aggregate_state WHERE id=$1) AS state_count,
      (SELECT count(*)::int FROM ${SCHEMA}.events WHERE id=$1) AS event_count,
      (SELECT count(*)::int FROM ${SCHEMA}.receipts WHERE mutation_id=$2) AS receipt_count`,[plan.id,plan.mutationId])
  ]);
  safe(a.rowCount===1 && e.rowCount===1 && r.rowCount===1 && counts.rowCount===1,'INCOMPLETE_EFFECT');
  const row=a.rows[0],event=e.rows[0],receipt=r.rows[0],cnt=counts.rows[0];
  safe(Number(row.revision)===1 && isDeepStrictEqual(row.state,plan.state),'STATE_MISMATCH');
  safe(row.last_event_sha256===plan.eventHash && event.event_id===plan.eventId && Number(event.sequence)===1 &&
    event.previous_hash===null && event.event_hash===plan.eventHash &&
    isDeepStrictEqual(event.payload,plan.payload),'EVENT_MISMATCH');
  safe(receipt.mutation_id===plan.mutationId && receipt.command_fingerprint===plan.commandHash &&
    Number(receipt.original_revision)===1 && isDeepStrictEqual(receipt.result,plan.result),'RECEIPT_MISMATCH');
  safe(Number(cnt.state_count)===1 && Number(cnt.event_count)===1 && Number(cnt.receipt_count)===1,'DUPLICATE_EFFECT');
  return {revision:1,effects:1,events:1,receipts:1,hash:plan.eventHash};
}
async function applyCreate(client, plan) {
  // Identical entrypoint for original and replay: not just SELECT of a receipt.
  // Atomic receipt claim + aggregate + event. Competing same-key INSERT waits
  // on PostgreSQL uniqueness; a mismatch can never replay as another mutation.
  validateCommand(plan.cmd,plan.id);
  await client.query('BEGIN');
  let committing=false;
  try {
    const claim=await client.query(`INSERT INTO ${SCHEMA}.receipts
      (mutation_id,command_fingerprint,original_revision,result) VALUES ($1,$2,1,$3::jsonb)
      ON CONFLICT (mutation_id) DO NOTHING RETURNING mutation_id`,
      [plan.mutationId,plan.commandHash,JSON.stringify(plan.result)]);
    safe(claim.rowCount===0 || claim.rowCount===1,'BAD_RECEIPT_CLAIM');
    if(claim.rowCount===0) {
      const existing=await client.query(`SELECT command_fingerprint,original_revision,result FROM ${SCHEMA}.receipts
        WHERE mutation_id=$1 FOR UPDATE`,[plan.mutationId]);
      safe(existing.rowCount===1,'MISSING_RECEIPT');
      safe(existing.rows[0].command_fingerprint===plan.commandHash,'MUTATION_IDENTITY_COLLISION');
      safe(Number(existing.rows[0].original_revision)===1 &&
        isDeepStrictEqual(existing.rows[0].result,plan.result),'RECEIPT_MISMATCH');
      // Snapshot counts, not a new SQL effect. All reads stay in one transaction.
      await inspect(client,plan);
      committing=true;
      await client.query('COMMIT');
      return {disposition:'RECONCILED',revision:1,events:1,receipts:1};
    }
    // Fresh mutation must not overwrite existing data under a different key.
    const current=await client.query(`SELECT revision FROM ${SCHEMA}.aggregate_state WHERE id=$1 FOR UPDATE`,[plan.id]);
    safe(current.rowCount===0,'STALE_REVISION');
    await client.query(`INSERT INTO ${SCHEMA}.aggregate_state(id,revision,state,last_event_sha256)
      VALUES($1,1,$2::jsonb,$3)`,[plan.id,JSON.stringify(plan.state),plan.eventHash]);
    await client.query(`INSERT INTO ${SCHEMA}.events(event_id,id,sequence,previous_hash,event_hash,payload)
      VALUES($1,$2,1,NULL,$3,$4::jsonb)`,[plan.eventId,plan.id,plan.eventHash,JSON.stringify(plan.payload)]);
    committing=true;
    await client.query('COMMIT');
    return {disposition:'COMMITTED',revision:1,events:1,receipts:1};
  } catch (_e) {
    if(committing) throw new CommitUnknown(); // NEVER blindly retry after ambiguous COMMIT.
    try{await client.query('ROLLBACK');}catch{}
    if(_e instanceof SafeError)throw _e;
    // PostgreSQL unique violations or network errors must not leak secrets.
    throw new SafeError('SQL_EFFECT_FAILED_RECONCILE_FIRST');
  }
}
async function resolveUnknown(client, plan) {
  // A new connection at host B. No mutation and no automatic dispatch. A
  // missing receipt is inconclusive at this observation, not retry authority.
  validateCommand(plan.cmd,plan.id);
  const q=await client.query(`SELECT command_fingerprint,original_revision,result FROM ${SCHEMA}.receipts
    WHERE mutation_id=$1`,[plan.mutationId]);
  if(q.rowCount===0)return {disposition:'NOT_OBSERVED',effect:'UNKNOWN',retry_authorized:false};
  safe(q.rowCount===1,'DUPLICATE_RECEIPT');
  safe(q.rows[0].command_fingerprint===plan.commandHash,'MUTATION_IDENTITY_COLLISION');
  await inspect(client,plan);
  return {disposition:'CONFIRMED',effect:'CONFIRMED',retry_authorized:false,revision:1,receipts:1};
}
module.exports={SCHEMA,SafeError,CommitUnknown,HASH,exactJSON,commandFor,validateCommand,planned,inspect,applyCreate,resolveUnknown};
