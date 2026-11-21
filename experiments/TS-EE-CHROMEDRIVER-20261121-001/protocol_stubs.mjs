import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { performance } from 'node:perf_hooks';
const report = () => ({ schema: 'ts-ee/chromedriver-session-lifecycle/v0', subject: 'NONPRODUCT_SYNTHETIC', network_mode: 'OBSERVE_ONLY', browser_scenarios: 'NOT_RUN', session_result: 'NOT_RUN', error_class: 'NONE', create_ms: null, delete_status: 'NOT_APPLICABLE', provider_native_verified: false, product_accepted: false });
async function request(base, path, method, body, timeout) {
  const response = await fetch(base + path, { method, headers: {'content-type':'application/json'}, body: body === null ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(timeout) });
  let json = null; try { json = await response.json(); } catch {}
  return { ok: response.ok, json };
}
async function probe(base, timeout = 100) {
  const r = report();
  try {
    const ready = await request(base, '/status', 'GET', null, 1000);
    if (!ready.ok || ready.json?.value?.ready !== true) { r.session_result = 'STATUS_NOT_READY'; return r; }
  } catch { r.session_result = 'STATUS_TIMEOUT'; return r; }
  let sid = null; const start = performance.now();
  try {
    const created = await request(base, '/session', 'POST', { capabilities: { alwaysMatch: { browserName: 'chrome' } } }, timeout);
    r.create_ms = Math.round(performance.now() - start);
    if (!created.ok) { r.session_result = 'SESSION_CREATE_ERROR'; r.error_class = 'SESSION_NOT_CREATED'; }
    else if (typeof created.json?.value?.sessionId !== 'string' || !created.json.value.sessionId) { r.session_result = 'BAD_W3C_RESPONSE'; r.error_class = 'BAD_W3C_RESPONSE'; }
    else { sid = created.json.value.sessionId; r.session_result = 'SESSION_CREATED'; }
  } catch (e) { r.create_ms = Math.round(performance.now() - start); const t = e?.name === 'TimeoutError' || e?.name === 'AbortError'; r.session_result = t ? 'SESSION_CREATE_TIMEOUT' : 'SESSION_CREATE_ERROR'; r.error_class = t ? 'TIMEOUT' : 'TRANSPORT_ERROR'; }
  if (sid !== null) { try { const d = await request(base, '/session/' + encodeURIComponent(sid), 'DELETE', null, 1000); r.delete_status = d.ok ? 'ACK' : 'FAIL'; } catch { r.delete_status = 'FAIL'; } }
  return r;
}
async function serve(handler, fn) { const s = createServer(handler); await new Promise(ok => s.listen(0, '127.0.0.1', ok)); try { return await fn('http://127.0.0.1:' + s.address().port); } finally { s.closeAllConnections(); await new Promise(ok => s.close(ok)); } }
async function main() {
  const secret = 'FAKE_SECRET_SESSION', token = 'FAKE_SECRET_TOKEN', image = 'FAKE_SECRET_PNG';
  const success = await serve((req, res) => { res.setHeader('content-type', 'application/json'); if (req.url === '/status') res.end('{"value":{"ready":true}}'); else if (req.method === 'POST') res.end(JSON.stringify({value:{sessionId:secret,debug:token+image}})); else res.end('{"value":null}'); }, base => probe(base));
  assert.equal(success.session_result, 'SESSION_CREATED'); assert.equal(success.delete_status, 'ACK');
  const invalid = await serve((req, res) => { res.setHeader('content-type', 'application/json'); res.end(req.url === '/status' ? '{"value":{"ready":true}}' : '{"value":{"error":"session not created"}}'); }, base => probe(base));
  assert.equal(invalid.session_result, 'BAD_W3C_RESPONSE');
  const timeout = await serve((req, res) => { res.setHeader('content-type', 'application/json'); if (req.url === '/status') res.end('{"value":{"ready":true}}'); else setTimeout(() => { if (!res.destroyed) res.end('{"value":null}'); }, 150); }, base => probe(base, 20));
  assert.equal(timeout.session_result, 'SESSION_CREATE_TIMEOUT');
  for (const r of [success, invalid, timeout]) { const text = JSON.stringify(r); for (const x of [secret, token, image]) assert.equal(text.includes(x), false); assert.equal(r.network_mode, 'OBSERVE_ONLY'); assert.equal(r.browser_scenarios, 'NOT_RUN'); }
  console.log(JSON.stringify({protocol_stub_assertions:'PASS',trial_count:3,negative_cases:['BAD_W3C_RESPONSE','SESSION_CREATE_TIMEOUT'],secret_redaction:'PASS',real_chromedriver:'NOT_RUN',product_effect:'NONE'}));
}
main().catch(e => {console.error(JSON.stringify({status:'FAIL',error_class:String(e?.name||'Error').slice(0,32)}));process.exitCode=1;});
