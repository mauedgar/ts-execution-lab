// Method-only, pure transformation of TRUSTED, SHA256-pinned source.
// Never executes source code. NOT a sandbox, import/side-effect checker or JSX compiler.
import {stripTypeScriptTypes} from 'node:module';
import {createHash} from 'node:crypto';

const labelPattern=/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\.tsx?$/;
const hashPattern=/^[a-f0-9]{64}$/;

export function transformFrozenPureTypeScript(source,{label,sha256}={}) {
  if (typeof source!=='string'||typeof label!=='string'||!labelPattern.test(label)) {
    throw new Error('BLOCKED_INVALID_SOURCE_OR_LABEL');
  }
  const raw=Buffer.from(source,'utf8');
  if (raw.length===0||raw.length>131072)throw new Error('BLOCKED_SOURCE_SIZE');
  if(typeof sha256!=='string'||!hashPattern.test(sha256))throw new Error('BLOCKED_UNPINNED_SOURCE');
  const actual=createHash('sha256').update(raw).digest('hex');
  if (actual!==sha256)throw new Error('BLOCKED_SOURCE_DIGEST_MISMATCH');
  const code=stripTypeScriptTypes(source,{mode:'strip',sourceUrl:label});
  // Return DATA only. The caller independently owns safe evaluation and runtime tests.
  return Object.freeze({code,source_sha256:actual,source_bytes:raw.length,source_label:label});
}
