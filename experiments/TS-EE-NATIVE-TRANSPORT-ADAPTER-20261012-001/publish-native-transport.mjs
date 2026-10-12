#!/usr/bin/env node
// TS Execution Engineering: experimental sidecar for immutable, native-result Git publication.
// A completed execution owns its original result/receipt. This sidecar does NOT run Product work.
import { readFileSync, statSync, lstatSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, resolve, sep, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const contract = 'ts-ee-native-transport-publication/v0-experimental';
const sha256 = (b) => createHash('sha256').update(b).digest('hex');
const phase = { stage: 'READ_INPUT', local_commit: null, expected_head: null, branch: null, package_path: null, attempt: null }; 
const assert = (cond, code) => { if (!cond) throw Object.assign(new Error(code), { code }); };
function relPath(s, prefix) {
  assert(typeof s === 'string' && s.length > 0 && s.length <= 350 && !s.includes('\\') && !s.startsWith('/') && !s.endsWith('/'), 'INVALID_RELATIVE_PATH');
  const ps = s.split('/');
  assert(ps.every(p => p && p !== '.' && p !== '..' && p !== '.git' && /^[A-Za-z0-9._-]+$/.test(p)), 'UNSAFE_RELATIVE_PATH');
  if (prefix) assert(s.startsWith(prefix), 'UNAUTHORIZED_TRANSPORT_PATH');
  return s;
}
function readJson(path) { return JSON.parse(readFileSync(path, 'utf8')); }
function safeFile(root, relativePath) {
  relPath(relativePath);
  const absRoot = resolve(root), file = resolve(absRoot, relativePath);
  assert(file.startsWith(absRoot + sep), 'SOURCE_OUTSIDE_ROOT');
  let segment = absRoot;
  for (const part of relativePath.split('/')) {
    segment = join(segment, part);
    assert(!lstatSync(segment).isSymbolicLink(), 'SYMLINK_NOT_ALLOWED');
  }
  assert(statSync(file).isFile(), 'NOT_REGULAR_FILE');
  return file;
}
function run(cwd, args, extra = {}) {
  const r = spawnSync('git', args, { cwd, encoding: 'utf8', timeout: 120000, maxBuffer: 1024 * 1024, env: { ...process.env, GIT_TERMINAL_PROMPT: '0', ...extra } });
  assert(!r.error && r.status === 0, 'GIT_COMMAND_FAILED_' + args[0].toUpperCase().replaceAll('-', '_'));
  return r.stdout.trim();
}
function validateEnvelope(result, receipt) {
  assert(result?.contract_version === 'ts-execution-result/v0.2' && receipt?.contract_version === 'ts-execution-receipt/v0.2', 'UNSUPPORTED_ENVELOPE');
  for (const field of ['Product_operation_ref', 'ExecutionAttempt_ref', 'request_identity', 'result_status', 'effect_state']) {
    assert(typeof result[field] === 'string' && result[field].length > 0 && result[field] === receipt[field], 'ENVELOPE_IDENTITY_MISMATCH_' + field);
  }
  assert(result.subject_ref && result.subject_ref === receipt.exact_subject_ref, 'SUBJECT_MISMATCH');
  assert(/^sha256:[0-9a-f]{64}$/.test(result.request_identity), 'INVALID_REQUEST_IDENTITY');
  assert(['PASS', 'PARTIAL', 'FAIL', 'BLOCKED', 'UNAVAILABLE'].includes(result.result_status), 'INVALID_RESULT_STATUS');
  assert(['NONE', 'CONFIRMED', 'UNKNOWN'].includes(result.effect_state), 'INVALID_EFFECT_STATE');
  assert(result.observation?.effect_state === result.effect_state && receipt.observation?.effect_state === result.effect_state, 'OBSERVATION_EFFECT_MISMATCH');
  assert(receipt.authority_created === false && receipt.Product_effect_created === false, 'AUTHORITY_MISMATCH');
  assert(receipt.result_ref === 'result.json', 'RESULT_REF_MISMATCH');
  assert(result.Product_ref && result.request_id && result.context_id && result.execution_profile_ref, 'RESULT_IDENTITY_INCOMPLETE');
  assert(receipt.selected_binding_ref && receipt.started_at && receipt.completed_at, 'RECEIPT_IDENTITY_INCOMPLETE');
}
function publish(requestFile) {
  const p = readJson(requestFile);
  assert(p?.contract === contract, 'INVALID_PUBLICATION_REQUEST');
  assert(typeof p.transport_checkout === 'string' && typeof p.result_dir === 'string', 'MISSING_INPUT_PATH');
  const repo = resolve(p.transport_checkout), source = resolve(p.result_dir);
  assert(!/^https?:\/\/[^/]*:[^/]*@/.test(p.expected_remote_url), 'REMOTE_EMBEDDED_CREDENTIALS_FORBIDDEN');
  assert(repo !== source && !repo.startsWith(source + sep) && !source.startsWith(repo + sep), 'OVERLAPPING_SOURCE_AND_TRANSPORT');
  assert(typeof p.expected_head === 'string' && /^[0-9a-f]{40}$/.test(p.expected_head), 'INVALID_EXPECTED_HEAD');
  assert(typeof p.expected_remote_url === 'string' && p.expected_remote_url.length > 0, 'MISSING_REMOTE_URL');
  assert(typeof p.branch === 'string' && /^[A-Za-z0-9][A-Za-z0-9._/-]{0,150}$/.test(p.branch) && !p.branch.includes('..') && !p.branch.includes('//') && !p.branch.endsWith('.lock'), 'INVALID_BRANCH');
  const dest = relPath(p.package_path, 'results/');
  Object.assign(phase, { expected_head: p.expected_head, branch: p.branch, package_path: dest });
  assert(!dest.split('/').includes('.git'), 'INVALID_DEST');
  const extras = p.artifacts ?? [];
  assert(Array.isArray(extras) && extras.length <= 25, 'INVALID_ARTIFACT_LIST');
  const files = ['result.json', 'receipt.json', ...extras];
  assert(new Set(files).size === files.length, 'DUPLICATED_ARTIFACT');
  const limit = p.max_package_bytes ?? 20 * 1024 * 1024;
  assert(Number.isSafeInteger(limit) && limit > 0 && limit <= 50 * 1024 * 1024, 'INVALID_SIZE_LIMIT');
  const bytes = new Map(); let total = 0;
  for (const file of files) {
    const filePath = safeFile(source, relPath(file));
    const b = readFileSync(filePath);
    total += b.length;
    assert(total <= limit, 'PACKAGE_TOO_LARGE');
    bytes.set(file, b);
  }
  const result = JSON.parse(bytes.get('result.json').toString('utf8'));
  const receipt = JSON.parse(bytes.get('receipt.json').toString('utf8'));
  validateEnvelope(result, receipt);
  phase.attempt = result.ExecutionAttempt_ref;
  assert(/^[A-Za-z0-9][A-Za-z0-9._-]{0,150}$/.test(result.ExecutionAttempt_ref), 'INVALID_ATTEMPT_REF');
  assert(relPath(dest).split('/').at(-1) === result.ExecutionAttempt_ref.replace(/[^A-Za-z0-9._-]/g, '_'), 'PACKAGE_ATTEMPT_MISMATCH');
  assert(!existsSync(join(repo, dest)), 'PACKAGE_COLLISION');
  // Transport checkout must be dedicated, unchanged and based on an exact remote head.
  assert(run(repo, ['rev-parse', '--show-toplevel']) === repo, 'NOT_CHECKOUT_ROOT');
  assert(run(repo, ['status', '--porcelain', '--untracked-files=all']) === '', 'DIRTY_TRANSPORT_CHECKOUT');
  assert(run(repo, ['rev-parse', 'HEAD']) === p.expected_head, 'LOCAL_HEAD_MISMATCH');
  assert(run(repo, ['symbolic-ref', '--short', 'HEAD']) === p.branch, 'LOCAL_BRANCH_MISMATCH');
  assert(run(repo, ['remote', 'get-url', 'origin']) === p.expected_remote_url, 'REMOTE_URL_MISMATCH');
  const remoteSha = run(repo, ['ls-remote', '--exit-code', 'origin', 'refs/heads/' + p.branch]).split(/\s+/)[0];
  assert(remoteSha === p.expected_head, 'REMOTE_HEAD_MISMATCH');
  // No git effects before the preceding guards succeed.
  let parent = repo;
  for (const component of dest.split('/').slice(0, -1)) {
    parent = join(parent, component);
    if (existsSync(parent)) assert(!lstatSync(parent).isSymbolicLink(), 'DEST_SYMLINK_NOT_ALLOWED');
  }
  phase.stage = 'LOCAL_PACKAGE_WRITE';
  mkdirSync(join(repo, dest), { recursive: true });
  const entries = [];
  for (const [file, b] of [...bytes.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const path = join(repo, dest, file);
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, b, { flag: 'wx' });
    entries.push({ path: file, sha256: sha256(b), size_bytes: b.length });
  }
  const manifest = {
    contract, evidence_class: 'EXPERIMENTAL_EXECUTION_RESULT',
    Product_operation_ref: result.Product_operation_ref, ExecutionAttempt_ref: result.ExecutionAttempt_ref,
    Product_ref: result.Product_ref, request_identity: result.request_identity,
    subject_ref: result.subject_ref, result_status: result.result_status, effect_state: result.effect_state,
    source_binding_ref: receipt.selected_binding_ref, files: entries,
    publication_authority: 'NONE_PRODUCT', Product_effect_created: false,
  };
  writeFileSync(join(repo, dest, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' });
  phase.stage = 'LOCAL_STAGE';
  run(repo, ['add', '--', dest]);
  const staged = run(repo, ['diff', '--cached', '--name-only']).split('\n').filter(Boolean);
  assert(staged.length === files.length + 1 && staged.every(s => s.startsWith(dest + '/')), 'UNEXPECTED_STAGED_PATHS');
  const msg = 'evidence(ee): native ' + result.result_status + ' ' + result.ExecutionAttempt_ref;
  phase.stage = 'LOCAL_COMMIT';
  run(repo, ['commit', '-m', msg]);
  const commit = run(repo, ['rev-parse', 'HEAD']);
  phase.local_commit = commit;
  // This push may succeed even if the response is lost: never retry blindly.
  phase.stage = 'REMOTE_PUSH_UNCERTAIN';
  let pushSucceeded = false;
  try { run(repo, ['push', 'origin', 'HEAD:refs/heads/' + p.branch]); pushSucceeded = true; }
  catch { throw Object.assign(new Error('PUBLICATION_UNKNOWN_RECONCILE_REMOTE'), { code: 'PUBLICATION_UNKNOWN_RECONCILE_REMOTE' }); }
  assert(pushSucceeded, 'PUBLICATION_NOT_CONFIRMED');
  phase.stage = 'REMOTE_VERIFY_UNCERTAIN';
  const confirmed = run(repo, ['ls-remote', '--exit-code', 'origin', 'refs/heads/' + p.branch]).split(/\s+/)[0];
  assert(confirmed === commit, 'PUBLICATION_UNKNOWN_RECONCILE_REMOTE');
  phase.stage = 'PUBLISHED_VERIFIED';
  return { status: 'PUBLISHED_VERIFIED', binding: contract,
    branch: p.branch, parent: p.expected_head, commit, package_path: dest,
    attempt: result.ExecutionAttempt_ref, result_status: result.result_status,
    effect_state: result.effect_state, manifest_sha256: sha256(readFileSync(join(repo, dest, 'manifest.json'))),
    files: entries.length };
}
try {
  assert(process.argv.length === 3, 'USAGE_EXPECTS_PUBLICATION_REQUEST_JSON');
  console.log(JSON.stringify(publish(process.argv[2])));
} catch (e) {
  const ambiguous = e.code?.startsWith('PUBLICATION_UNKNOWN') || phase.stage.startsWith('REMOTE_');
  console.error(JSON.stringify({ status: ambiguous ? 'PUBLICATION_UNKNOWN' : phase.stage === 'READ_INPUT' ? 'BLOCKED_PRECONDITION' : 'BLOCKED_OR_PARTIAL_LOCAL', reason: e.code || 'INVALID_INPUT_OR_IO_ERROR', phase: phase.stage, ...(phase.local_commit ? { local_commit: phase.local_commit } : {}), ...(phase.expected_head ? { expected_head: phase.expected_head } : {}), ...(phase.branch ? { branch: phase.branch } : {}), ...(phase.package_path ? { package_path: phase.package_path } : {}), ...(phase.attempt ? { attempt: phase.attempt } : {}), retry_authorized: false }));
  process.exitCode = 1;
}
