'use strict';
// Experimental, credential-free, read-only runtime preflight. No physical/TLS proof.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const ROOT = path.resolve(__dirname);
const PREFIX = path.resolve(ROOT, '..', 'r2-node');
const FROZEN = Object.freeze({
  'r3-command-core.cjs': 'ecb429027fbb1d24646be72e9ae66afffb15b6a5',
  'physical-host-p01-p04-v2.cjs': 'f9353c358787c712ca6f6030d9ac537dfdc739e8',
  'r3-command-core.test.cjs': '4f1c416d604f8840fe0d01ae9999c1adde690c6a',
  'physical-host-p01-p04-v2.test.cjs': '15dcf5b24f6aee8e3af34323288a0289a6aaa527'
});
const LOCK_SHA = '8241c9d02d2da25a11b2d6c16e0c6fc64aaf2835';
const PKG_SHA = 'fa733e5bc20c5c257a042df9bfbea5377a6c7018';
const PG_VERSION = '8.23.1';
class Blocked extends Error { constructor(code) { super(code); this.code = code; } }
function requireFile(file) {
  let st;
  try { st = fs.lstatSync(file); } catch { throw new Blocked('FILE_UNAVAILABLE'); }
  if (!st.isFile() || st.isSymbolicLink() || st.size > 1024 * 1024) {
    throw new Blocked('FILE_NOT_REGULAR');
  }
  try { return fs.readFileSync(file); } catch { throw new Blocked('FILE_UNREADABLE'); }
}
function gitBlob(content) {
  return crypto.createHash('sha1').update(Buffer.from(`blob ${content.length}\0`)).update(content).digest('hex');
}
function readPinned(file, expected) {
  const content = requireFile(file);
  if (gitBlob(content) !== expected) throw new Blocked('SOURCE_HASH_MISMATCH');
  return content;
}
function parseJson(buf) {
  try { return JSON.parse(buf.toString('utf8')); } catch { throw new Blocked('INVALID_METADATA'); }
}
function assess({root = ROOT, prefix = PREFIX, sources = FROZEN,
  lockSha = LOCK_SHA, pkgSha = PKG_SHA, pgVersion = PG_VERSION,
  nodeVersion = process.version, argvCount = process.argv.length,
  sensitiveEnvPresent = Object.hasOwn(process.env, 'TS_R3_DATABASE_URL')} = {}) {
  if (argvCount !== 2) throw new Blocked('ARGS_NOT_ALLOWED');
  if (!/^v22\./.test(nodeVersion)) throw new Blocked('NODE22_REQUIRED');
  if (sensitiveEnvPresent) throw new Blocked('SECRET_ENV_PRESENT');
  for (const [name, sha] of Object.entries(sources)) {
    if (!/^[a-z0-9.-]+\.cjs$/.test(name) || !/^[0-9a-f]{40}$/.test(sha)) throw new Blocked('INVALID_MANIFEST');
    readPinned(path.join(root, name), sha);
  }
  const pkg = parseJson(readPinned(path.join(prefix, 'package.json'), pkgSha));
  const lock = parseJson(readPinned(path.join(prefix, 'package-lock.json'), lockSha));
  if (pkg.dependencies?.pg !== pgVersion || lock.lockfileVersion !== 3 ||
      lock.packages?.['']?.dependencies?.pg !== pgVersion ||
      lock.packages?.['node_modules/pg']?.version !== pgVersion ||
      !/^sha512-[a-zA-Z0-9+/]+={0,2}$/.test(lock.packages['node_modules/pg'].integrity || '')) {
    throw new Blocked('LOCK_INVALID');
  }
  const installed = parseJson(requireFile(path.join(prefix, 'node_modules', 'pg', 'package.json')));
  if (installed.version !== pgVersion || installed.name !== 'pg') throw new Blocked('PG_METADATA_MISMATCH');
  return Object.freeze({ status: 'READY_METADATA_ONLY', node: nodeVersion, pg: pgVersion,
    sourceCount: Object.keys(sources).length, lock: 'GIT_BLOB_VERIFIED', installed: 'PACKAGE_METADATA_ONLY',
    tls: 'NOT_TESTED', physical: 'NOT_TESTED' });
}
function main() {
  try {
    const x = assess();
    process.stdout.write('PASS|TS-R3|PORTABLE_HOST_PREFLIGHT|node=' + x.node +
      '|pg=' + x.pg + '|sources=' + x.sourceCount +
      '|lock=' + x.lock + '|installed=' + x.installed +
      '|tls=' + x.tls + '|physical=' + x.physical + '\n');
  } catch (error) {
    const code = error instanceof Blocked ? error.code : 'UNEXPECTED_ERROR';
    process.stderr.write('BLOCKED|TS-R3|PORTABLE_HOST_PREFLIGHT|' + code + '\n');
    process.exitCode = 2;
  }
}
if (require.main === module) main();
module.exports = { assess, gitBlob, Blocked };
