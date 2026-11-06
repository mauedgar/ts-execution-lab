'use strict';
// TS R3 experimental: bounded execution mechanics only; no Product/Neon authority.
// Invoke: node r3-offline-attempt-v1.cjs <existing-isolated-attempt-directory>
// The attempt directory must contain request.json and no receipt.json.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const cp = require('node:child_process');

const SUBJECT = Object.freeze({
  repository: 'mauedgar/ts-execution-lab',
  commit: '981e06ede3fa6e1b0a1ceeee04b786a9e51b3c17',
  tree: '74faee8d375d6e4271c5255aed4931c71da61ebd',
  preflight_blob: '044c517c631f225e2c476046b163f53ad6b11a21'
});
const SOURCE_NAME = 'r3-portable-host-preflight.cjs';
const ID = /^[A-Z][A-Z0-9_-]{7,95}$/;
class Blocked extends Error { constructor(code) { super(code); this.code = code; } }
const blocked = code => { throw new Blocked(code); };
function digest(content) { return crypto.createHash('sha256').update(content).digest('hex'); }
function gitBlob(data) {
  return crypto.createHash('sha1').update(Buffer.from(`blob ${data.length}\0`)).update(data).digest('hex');
}
function canonical(p) { const s = path.normalize(p); return process.platform === 'win32' ? s.toLowerCase() : s; }
function assertTree(target, leaf = true) {
  const absolute = path.resolve(target), volume = path.parse(absolute).root;
  const pieces = path.relative(volume, absolute).split(path.sep).filter(Boolean);
  let cursor = volume;
  for (let i = 0; i < pieces.length; i++) {
    cursor = path.join(cursor, pieces[i]);
    let st;
    try { st = fs.lstatSync(cursor); } catch { blocked('PATH_MISSING'); }
    if (st.isSymbolicLink()) blocked('PATH_REDIRECT');
    const final = i === pieces.length - 1;
    if (!final || !leaf) {
      if (!st.isDirectory()) blocked('PATH_NOT_DIRECTORY');
    } else if (!st.isFile() || st.size > 32 * 1024) blocked('FILE_NOT_REGULAR');
  }
  let resolved;
  try { resolved = fs.realpathSync.native(absolute); } catch { blocked('PATH_UNREADABLE'); }
  if (canonical(absolute) !== canonical(resolved)) blocked('PATH_REDIRECT');
  return absolute;
}
function readFile(file) {
  const target = assertTree(file);
  let fd;
  try { fd = fs.openSync(target, fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW || 0)); }
  catch { blocked('FILE_UNAVAILABLE'); }
  try {
    const st = fs.fstatSync(fd);
    if (!st.isFile() || st.size > 32768) blocked('FILE_NOT_REGULAR');
    const bytes = fs.readFileSync(fd);
    if (st.size !== bytes.length) blocked('FILE_CHANGED');
    return bytes;
  } catch (e) { if (e instanceof Blocked) throw e; blocked('FILE_UNREADABLE'); }
  finally { try { fs.closeSync(fd); } catch { /* fail closed above, close does not authorize effect */ } }
}
function parseRequest(bytes) {
  let x;
  try { x = JSON.parse(bytes.toString('utf8')); } catch { blocked('REQUEST_BAD_JSON'); }
  if (!x || typeof x !== 'object' || Array.isArray(x) || Object.keys(x).length !== 5) blocked('REQUEST_SHAPE');
  if (x.schema !== 'TS_R3_OFFLINE_ATTEMPT_V1' || x.operation !== 'CREDENTIAL_FREE_METADATA_PREFLIGHT') blocked('REQUEST_OPERATION');
  if (typeof x.execution_attempt_id !== 'string' || !ID.test(x.execution_attempt_id)) blocked('REQUEST_ID');
  if (typeof x.operation_id !== 'string' || !ID.test(x.operation_id)) blocked('REQUEST_ID');
  if (!x.subject || typeof x.subject !== 'object' || Array.isArray(x.subject) ||
      Object.keys(x.subject).length !== 4 ||
      Object.keys(SUBJECT).some(k => x.subject[k] !== SUBJECT[k])) blocked('REQUEST_SUBJECT');
  return x;
}
function run({attemptDir, sourceDir = __dirname, spawn = cp.spawnSync} = {}) {
  const directory = assertTree(attemptDir, false);
  const requestPath = path.join(directory, 'request.json');
  const resultPath = path.join(directory, 'receipt.json');
  const raw = readFile(requestPath);
  const request = parseRequest(raw);
  // MUST reject an existing or partial receipt, including links. No replay or overwrites.
  try { fs.lstatSync(resultPath); blocked('RECEIPT_ALREADY_EXISTS'); }
  catch (e) { if (e instanceof Blocked) throw e; if (e?.code !== 'ENOENT') blocked('RECEIPT_UNCERTAIN'); }
  const source = readFile(path.join(sourceDir, SOURCE_NAME));
  if (gitBlob(source) !== SUBJECT.preflight_blob) blocked('RUNNER_SOURCE_MISMATCH');
  if (!/^v22\./.test(process.version)) blocked('NODE22_REQUIRED');
  const safeEnv = {};
  for (const key of ['PATH', 'SYSTEMROOT', 'WINDIR', 'HOME', 'USERPROFILE', 'TEMP', 'TMP', 'LANG', 'LC_ALL']) {
    if (typeof process.env[key] === 'string') safeEnv[key] = process.env[key];
  }
  // Any credentials in parent process are NOT inherited by child.
  safeEnv.NODE_OPTIONS = '';
  let p;
  try {
    p = spawn(process.execPath, [path.join(sourceDir, SOURCE_NAME)], {
      cwd: sourceDir, env: safeEnv, encoding: 'utf8', timeout: 30000,
      maxBuffer: 16384, windowsHide: true
    });
  } catch { blocked('SPAWN_ERROR'); }
  const output = typeof p.stdout === 'string' ? p.stdout.trim() : '';
  const expected = /^PASS\|TS-R3\|PORTABLE_HOST_PREFLIGHT\|node=v22\.\d+\.\d+\|pg=8\.23\.1\|sources=4\|lock=GIT_BLOB_VERIFIED\|installed=PACKAGE_METADATA_ONLY\|tls=NOT_TESTED\|physical=NOT_TESTED$/;
  const pass = !p.error && p.status === 0 && !p.signal && expected.test(output) &&
    (!p.stderr || p.stderr.trim().length === 0);
  const result = {
    schema: 'TS_R3_OFFLINE_RECEIPT_V1',
    operation_id: request.operation_id,
    execution_attempt_id: request.execution_attempt_id,
    request_sha256: digest(raw),
    subject: SUBJECT,
    local_node: process.version,
    result: pass ? 'PASS_METADATA_ONLY' : 'BLOCKED',
    child_exit: Number.isInteger(p.status) ? p.status : null,
    failure_class: pass ? 'NONE' : p.error ? 'CHILD_EXEC_ERROR' : p.signal ? 'CHILD_SIGNAL' : 'PREFLIGHT_NOT_PASS',
    network_proof: 'NONE',
    package_integrity_proof: 'NONE',
    device_attestation: 'NONE',
    product_effect: 'NONE'
  };
  const encoded = Buffer.from(JSON.stringify(result) + '\n', 'utf8');
  let fd;
  try { fd = fs.openSync(resultPath, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL, 0o600); }
  catch { blocked('RECEIPT_COLLISION_OR_WRITE_ERROR'); }
  try { fs.writeSync(fd, encoded); fs.fsyncSync(fd); }
  catch { blocked('RECEIPT_EFFECT_UNKNOWN'); }
  finally { try { fs.closeSync(fd); } catch { /* receipt may be partial; preserve for reconciliation */ } }
  let actual;
  try { actual = readFile(resultPath); } catch { blocked('RECEIPT_EFFECT_UNKNOWN'); }
  if (digest(actual) !== digest(encoded)) blocked('RECEIPT_EFFECT_UNKNOWN');
  return { result, receipt_sha256: digest(encoded), status: pass ? 0 : 2 };
}
function main() {
  try {
    if (process.argv.length !== 3) blocked('ARGUMENTS');
    const x = run({attemptDir: process.argv[2]});
    process.stdout.write(`${x.result.result}|TS-R3|OFFLINE_ATTEMPT|receipt_sha256=${x.receipt_sha256}|attempt=${x.result.execution_attempt_id}\n`);
    process.exitCode = x.status;
  } catch (e) {
    const errorCode = e instanceof Blocked ? e.code : 'UNEXPECTED';
    process.stderr.write(`BLOCKED|TS-R3|OFFLINE_ATTEMPT|${errorCode}\n`);
    process.exitCode = 2;
  }
}
if (require.main === module) main();
module.exports = { SUBJECT, Blocked, digest, gitBlob, assertTree, readFile, parseRequest, run };
