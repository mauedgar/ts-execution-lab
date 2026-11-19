// METHOD_ONLY: parse and evaluate TRUSTED frozen TS/TSX sources without JSX or imports.
// Not a sandbox, security boundary or general TSX compiler. Node >=22.13 pinned in CI.
import { stripTypeScriptTypes } from 'node:module';
const safeName=/^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\.tsx?$/;
export async function importPureTypescriptText(source,label='source.ts') {
  if (typeof source!=='string'||Buffer.byteLength(source,'utf8')>131072||!safeName.test(label)) {
    throw new Error('BLOCKED_INVALID_SOURCE_OR_LABEL');
  }
  const compiled=stripTypeScriptTypes(source,{mode:'strip',sourceUrl:label});
  // data: ESM cannot resolve ordinary relative/bare imports; reject rather than guess.
  if (/^\s*(?:import\s+(?!type\b)|export\s*\*\s*from\s+)/m.test(compiled)) {
    throw new Error('BLOCKED_UNRESOLVABLE_IMPORT');
  }
  return import('data:text/javascript;base64,'+Buffer.from(compiled,'utf8').toString('base64'));
}
