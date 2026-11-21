import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { performance } from 'node:perf_hooks';

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const elapsed = start => Math.round(performance.now() - start);
const classification = Object.freeze({
  ready: 'READY', statusTimeout: 'DRIVER_STATUS_TIMEOUT', processExit: 'DRIVER_EXITED',
  created: 'SESSION_CREATED', sessionTimeout: 'SESSION_CREATE_TIMEOUT',
  sessionError: 'SESSION_CREATE_ERROR', badResponse: 'BAD_W3C_RESPONSE'
});
const out = {
  schema: 'ts-ee/chromedriver-session-lifecycle/v0',
  subject: 'NONPRODUCT_SYNTHETIC',
  browser_scenarios: 'NOT_RUN',
  network: { mode: 'OBSERVE_ONLY', os_egress_attested: false },
  original_provider_attested: false, product_accepted: false,
  status_ready_ms: null, session_create_ms: null,
  status_result: 'NOT_RUN', session_result: 'NOT_RUN',
  session_delete: 'NOT_APPLICABLE', driver_termination: 'NOT_RUN',
  profile_cleanup: 'NOT_RUN', overall: 'FAIL', error_class: 'NONE'
};
let driver = null;
let driverEnded = false;
let driverExitResolve;
const driverEnd = new Promise(resolve => { driverExitResolve = resolve; });

async function request(base, path, method, body, ms) {
  const response = await fetch(base + path, {
    method, headers: {'content-type': 'application/json'},
    body: body === null ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(ms)
  });
  let data = null;
  try { data = await response.json(); } catch { /* no raw response retained */ }
  return { ok: response.ok, data };
}
async function reserveEphemeralPort() {
  const server = createServer();
  await new Promise((resolve,reject) => {
    server.once('error',reject);
    server.listen(0,'127.0.0.1',resolve);
  });
  const port = server.address().port;
  await new Promise(resolve => server.close(resolve));
  return port;
}
async function terminate() {
  if (!driver) return;
  if (!driverEnded && driver.pid) {
    try { process.kill(-driver.pid,'SIGTERM'); } catch { /* may have exited */ }
    await Promise.race([driverEnd, sleep(2500)]);
  }
  if (!driverEnded && driver.pid) {
    try { process.kill(-driver.pid,'SIGKILL'); } catch { /* may have exited */ }
    await Promise.race([driverEnd, sleep(2500)]);
  }
  out.driver_termination = driverEnded ? 'OBSERVED_EXIT' : 'UNVERIFIED';
}
async function execute() {
  const dir = await mkdtemp(join(tmpdir(), 'ts-ee-chromedriver-b001-'));
  const profile = join(dir,'chrome-profile');
  try {
    const port = await reserveEphemeralPort();
    const base = 'http://127.0.0.1:' + port;
    const exe = process.env.CHROMEDRIVER_BIN || 'chromedriver';
    driver = spawn(exe, ['--port='+port, '--silent', '--allowed-ips=127.0.0.1'], {
      detached: true, stdio: 'ignore', shell: false, env: { ...process.env }
    });
    driver.once('exit', () => {driverEnded=true;driverExitResolve();});
    driver.once('error', () => {driverEnded=true;driverExitResolve();});
    const statusStart = performance.now();
    let ready = false;
    while (elapsed(statusStart) < 7000) {
      if (driverEnded) {out.status_result=classification.processExit;out.error_class='PROCESS_EXIT';break;}
      try {
        const r = await request(base, '/status', 'GET', null, 1200);
        if (r.ok && r.data?.value?.ready === true) {ready=true;break;}
      } catch { /* only bounded status-read retries, not POST /session retries */ }
      await sleep(100);
    }
    out.status_ready_ms = elapsed(statusStart);
    if (!ready) {
      if (out.status_result === 'NOT_RUN') {
        out.status_result=classification.statusTimeout;
        out.error_class='NOT_READY';
      }
      return;
    }
    out.status_result = classification.ready;
    const requestStart=performance.now();
    let sessionId=null;
    try {
      const r = await request(base, '/session', 'POST', {
        capabilities: { alwaysMatch: {
          browserName: 'chrome',
          'goog:chromeOptions': { args: [
            '--headless=new', '--no-sandbox', '--disable-gpu',
            '--disable-dev-shm-usage', '--no-first-run',
            '--disable-background-networking', '--user-data-dir='+profile
          ] }
        } }
      }, 12000);
      out.session_create_ms = elapsed(requestStart);
      if (!r.ok) {out.session_result=classification.sessionError;out.error_class='SESSION_NOT_CREATED';}
      else if (typeof r.data?.value?.sessionId !== 'string' || !r.data.value.sessionId) {
        out.session_result=classification.badResponse;out.error_class='BAD_W3C_RESPONSE';
      } else {
        sessionId=r.data.value.sessionId;
        out.session_result=classification.created;
      }
    } catch(e) {
      out.session_create_ms=elapsed(requestStart);
      const timeout=e?.name==='TimeoutError'||e?.name==='AbortError';
      out.session_result=timeout?classification.sessionTimeout:classification.sessionError;
      out.error_class=timeout?'TIMEOUT':'TRANSPORT_ERROR';
    } finally {
      if (sessionId !== null) {
        try {
          const r=await request(base,'/session/'+encodeURIComponent(sessionId),'DELETE',null,3000);
          out.session_delete=r.ok?'ACK':'FAIL';
        } catch {out.session_delete='FAIL';}
      }
    }
  } finally {
    await terminate();
    try {
      if (out.driver_termination === 'OBSERVED_EXIT') {
        await rm(dir,{recursive:true,force:true,maxRetries:0});
        out.profile_cleanup='PASS';
      } else out.profile_cleanup='BLOCKED_PROCESS_UNVERIFIED';
    } catch {out.profile_cleanup='FAIL';}
    out.overall = out.status_result === classification.ready &&
      out.session_result === classification.created &&
      out.session_delete === 'ACK' &&
      out.driver_termination === 'OBSERVED_EXIT' &&
      out.profile_cleanup === 'PASS' ? 'PASS_BOUNDED_LIFECYCLE' : 'FAIL';
    if (out.overall !== 'PASS_BOUNDED_LIFECYCLE' && out.error_class==='NONE') out.error_class='CLEANUP_OR_RUNTIME_FAILED';
  }
}
try { await execute(); }
catch(e) { out.overall='FAIL';out.error_class='RUNNER_EXCEPTION_'+String(e?.name||'Error').replace(/[^A-Za-z]/g,'').slice(0,24); }
const output = process.env.TS_EE_OUTPUT_DIR || 'chromedriver-evidence';
try {
  await mkdir(output,{recursive:true});
  await writeFile(join(output,'SESSION_REPORT.json'), JSON.stringify(out,null,2)+'\n',{flag:'wx'});
} catch { out.overall='FAIL';out.error_class='RECEIPT_WRITE_FAILED'; }
console.log(JSON.stringify(out));
if (out.overall !== 'PASS_BOUNDED_LIFECYCLE') process.exitCode=1;
